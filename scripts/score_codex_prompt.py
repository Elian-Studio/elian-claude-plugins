#!/usr/bin/env python3
"""Codex prompt (codex/prompts/*.md) 휴리스틱 채점 (100점, 90 미만 → exit 1).

Claude SKILL.md 와 독립된 게이트. Codex 프롬프트는 frontmatter/allowed-tools 가
없으므로 (권한은 ~/.codex/config.toml 책임) 축 구성이 다르다. LLM 호출 없이
결정적 신호로 8축 채점. stdlib only.

사용법:
    python3 scripts/score_codex_prompt.py <prompt.md> [<prompt.md>...] [--json]

환경변수:
    CODEX_EVAL_PASS_SCORE  통과 점수 (기본: 90)
    CODEX_EVAL_OUTPUT      JSON 결과 저장 경로 (기본: codex-evaluation-results.json)

종료 코드: 0 모두 통과 / 1 하나 이상 미달 / 2 사용법 오류·파일 없음
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

PASS_SCORE = int(os.environ.get("CODEX_EVAL_PASS_SCORE", "90"))
OUTPUT_PATH = os.environ.get("CODEX_EVAL_OUTPUT", "codex-evaluation-results.json")

# 잠긴 5블록 (순서 고정 — drift 검출의 핵심)
FIVE_BLOCKS = ["결론", "트레이드오프", "운영 리스크", "압박 질문", "다음 질문"]


def axis_five_block(text: str) -> tuple[int, str, list[str]]:
    """20점: 5블록이 모두, 순서대로 문서화됐는가."""
    imps: list[str] = []
    positions = [text.find(b) for b in FIVE_BLOCKS]
    found = [b for b, p in zip(FIVE_BLOCKS, positions) if p != -1]
    score = int(20 * len(found) / len(FIVE_BLOCKS))
    if len(found) == len(FIVE_BLOCKS):
        if positions != sorted(positions):
            score = 10
            imps.append("5블록이 모두 있으나 순서가 잠금 계약과 다름")
    else:
        missing = [b for b in FIVE_BLOCKS if b not in found]
        imps.append(f"5블록 누락: {missing}")
    return score, f"blocks={len(found)}/5, ordered={positions == sorted(positions)}", imps


def axis_phases(text: str) -> tuple[int, str, list[str]]:
    """15점: Phase 절차가 명시되고 고아 번호가 없는가."""
    imps: list[str] = []
    phases = set(re.findall(r"Phase\s+(\d+(?:\.\d+)?)", text))
    score = 0
    if {"1", "2", "3", "4", "5"}.issubset(phases):
        score += 10
    else:
        imps.append(f"Phase 1~5 중 일부 누락: 발견={sorted(phases)}")
    # 고아 번호: 본문에 Phase 6 을 언급하면 SKILL drift 패턴 (PR 리뷰에서 잡은 버그)
    if "Phase 6" in text:
        imps.append("Phase 6 언급 — 절차 본문과 불일치 가능 (drift 패턴)")
    else:
        score += 5
    return score, f"phases={sorted(phases)}", imps


def axis_standing(text: str) -> tuple[int, str, list[str]]:
    """15점: Forbidden + Pre-flight 같은 standing 규칙 섹션."""
    imps: list[str] = []
    score = 0
    if re.search(r"^#+\s*.*Forbidden", text, re.MULTILINE | re.IGNORECASE):
        score += 8
    else:
        imps.append("Forbidden 섹션 부재")
    if re.search(r"Pre-flight|self-check|체크", text, re.IGNORECASE):
        score += 7
    else:
        imps.append("Pre-flight / self-check 섹션 부재")
    return score, "standing rules", imps


def axis_readonly(text: str) -> tuple[int, str, list[str]]:
    """15점: read-only 계약 명시 + 파괴적 지시 없음."""
    imps: list[str] = []
    score = 0
    if re.search(r"read-only|읽기 전용|코드 수정.*안 함|파일 생성.*안 함", text, re.IGNORECASE):
        score += 10
    else:
        imps.append("read-only 계약 명시 부재")
    if re.search(r"rm\s+-rf|git push --force|git reset --hard|DROP TABLE", text):
        imps.append("파괴적 명령 문자열 포함 — read-only 프롬프트에 부적절")
    else:
        score += 5
    return score, "read-only contract", imps


def axis_drift_guard(text: str) -> tuple[int, str, list[str]]:
    """15점: 독립 트리 drift 경고 + Claude 카운터파트 상호참조."""
    imps: list[str] = []
    score = 0
    if re.search(r"독립.*트리|독립.*동기화|수동 동기화|drift", text, re.IGNORECASE):
        score += 8
    else:
        imps.append("독립 트리 / 수동 동기화 drift 경고 부재 (A안 핵심 리스크)")
    if "SKILL.md" in text or "plugins/elian-store" in text:
        score += 7
    else:
        imps.append("Claude SKILL.md 카운터파트 상호참조 부재")
    return score, "drift guard", imps


def axis_args(text: str) -> tuple[int, str, list[str]]:
    """8점: Codex 인자 규약($ARGUMENTS) 사용."""
    if "$ARGUMENTS" in text or re.search(r"\$\d", text):
        return 8, "args contract present", []
    return 0, "args contract absent", ["$ARGUMENTS 인자 규약 부재"]


def axis_template(text: str) -> tuple[int, str, list[str]]:
    """7점: 출력 템플릿 펜스 블록 존재."""
    if re.search(r"```markdown", text) and "## 결론" in text:
        return 7, "fenced output template present", []
    return 0, "output template absent", ["펜스된 5블록 출력 템플릿 부재"]


def axis_budget(text: str) -> tuple[int, str, list[str]]:
    """5점: 라인 예산 (자기완결 프롬프트 ≤320줄)."""
    n = len(text.splitlines())
    if n <= 320:
        return 5, f"{n} lines", []
    return 2, f"{n} lines (>320)", [f"본문 {n}줄 — 320 초과, 압축 권장"]


AXES = [
    ("5블록 잠금 계약", axis_five_block, 20),
    ("Phase 절차 정합", axis_phases, 15),
    ("Standing 규칙", axis_standing, 15),
    ("Read-only 계약", axis_readonly, 15),
    ("독립 트리 drift 가드", axis_drift_guard, 15),
    ("인자 규약", axis_args, 8),
    ("출력 템플릿", axis_template, 7),
    ("라인 예산", axis_budget, 5),
]


def score_prompt(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    axis_results = []
    total = 0
    all_imps: list[str] = []
    for idx, (name, fn, mx) in enumerate(AXES, start=1):
        s, reason, imps = fn(text)
        s = min(s, mx)
        axis_results.append(
            {"id": idx, "name": name, "score": s, "max": mx, "reason": reason, "improvements": imps}
        )
        total += s
        all_imps.extend(imps)
    verdict = "PASS" if total >= PASS_SCORE else "FAIL"
    return {
        "path": str(path),
        "axes": axis_results,
        "total": total,
        "verdict": verdict,
        "pass_score": PASS_SCORE,
        "top_improvements": all_imps[:5],
        "summary": f"{total}/100 ({verdict}).",
    }


def render_text(r: dict[str, Any]) -> str:
    icon = "✅" if r["verdict"] == "PASS" else "❌"
    lines = [f"\n{icon} {r['path']}  →  {r['total']}/100  ({r['verdict']}, 통과 {r['pass_score']})", ""]
    lines.append("| # | 축 | 점수 | 사유 |")
    lines.append("|---|---|---|---|")
    for ax in r["axes"]:
        reason = ax["reason"].replace("|", "\\|")
        lines.append(f"| {ax['id']} | {ax['name']} | {ax['score']}/{ax['max']} | {reason} |")
    if r["top_improvements"]:
        lines.append("")
        lines.append("**점수 상승 포인트**:")
        for imp in r["top_improvements"]:
            lines.append(f"- {imp}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="score_codex_prompt.py",
        description="Codex prompt 휴리스틱 채점 (100점, 90 게이트). LLM 없음. stdlib only.",
    )
    p.add_argument("paths", nargs="+", help="codex/prompts/*.md 경로 (다중 허용)")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON 출력")
    p.add_argument("--output", default=OUTPUT_PATH, help=f"JSON 저장 경로 (기본: {OUTPUT_PATH})")
    args = p.parse_args(argv)

    reports: list[dict[str, Any]] = []
    all_pass = True
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            print(f"::error file={path}::파일 없음", file=sys.stderr)
            reports.append({"path": str(path), "error": "file not found"})
            all_pass = False
            continue
        rep = score_prompt(path)
        reports.append(rep)
        if rep["verdict"] != "PASS":
            all_pass = False
        if not args.as_json:
            print(render_text(rep))

    aggregate = {"pass_score": PASS_SCORE, "all_pass": all_pass, "results": reports}
    Path(args.output).write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if args.as_json:
        print(json.dumps(aggregate, ensure_ascii=False, indent=2))
    else:
        print(f"\n결과 저장: {args.output}")
        print(
            f"✅ 모든 Codex 프롬프트 {PASS_SCORE}점 이상"
            if all_pass
            else f"❌ 일부 {PASS_SCORE}점 미만 — 머지 차단"
        )
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
