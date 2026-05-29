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

FIVE_BLOCKS = ["결론", "트레이드오프", "운영 리스크", "압박 질문", "다음 질문"]


def axis_identity(text: str, path: Path) -> tuple[int, str, list[str]]:
    """15점: command identity + purpose가 분명한가."""
    imps: list[str] = []
    command = path.stem
    score = 0
    if re.search(rf"^#\s+/{re.escape(command)}\b", text, re.MULTILINE):
        score += 5
    else:
        imps.append(f"첫 H1이 /{command} 명령을 명시하지 않음")
    if re.search(r"무엇을 하는가|Purpose|Goal|목적", text, re.IGNORECASE):
        score += 5
    else:
        imps.append("목적/Purpose 섹션 부재")
    if "$ARGUMENTS" in text or re.search(r"`\$ARGUMENTS`\s*=", text):
        score += 5
    else:
        imps.append("$ARGUMENTS 계약 부재")
    return score, f"command=/{command}", imps


def axis_scope(text: str) -> tuple[int, str, list[str]]:
    """15점: 사용/비사용 경계와 trigger가 분명한가."""
    imps: list[str] = []
    score = 0
    if re.search(r"when|trigger|사용|호출|Use for|사용할 때", text, re.IGNORECASE):
        score += 5
    else:
        imps.append("사용 조건/trigger 설명 부재")
    if re.search(r"Forbidden|Do not|사용하지|금지|Skip|제외", text, re.IGNORECASE):
        score += 5
    else:
        imps.append("비사용/금지 경계 부재")
    if re.search(r"얇음|모호|충분|scope|범위|경계|폴백|fallback", text, re.IGNORECASE):
        score += 5
    else:
        imps.append("입력 범위/판정/폴백 기준 부재")
    return score, "scope contract", imps


def axis_phases(text: str) -> tuple[int, str, list[str]]:
    """15점: workflow/procedure가 명시되고 번호 drift가 없는가."""
    imps: list[str] = []
    phases = set(re.findall(r"Phase\s+(\d+(?:\.\d+)?)", text))
    steps = set(re.findall(r"Step\s+(\d+)|^\s*(\d+)\.\s+", text, re.MULTILINE))
    has_workflow = re.search(r"절차|Workflow|Procedure|Phase|Step", text, re.IGNORECASE)
    score = 10 if has_workflow else 0
    if not has_workflow:
        imps.append("Workflow/Procedure/절차 설명 부재")
    phase_numbers = sorted(float(p) for p in phases)
    integer_phases = sorted(int(p) for p in phases if re.fullmatch(r"\d+", p))
    if integer_phases:
        expected = list(range(integer_phases[0], integer_phases[-1] + 1))
        if integer_phases == expected:
            score += 5
        else:
            imps.append(f"Phase 번호가 비연속: 발견={sorted(phases)}")
    elif steps:
        score += 5
    else:
        score += 3
    return score, f"phases={sorted(phases)}", imps


def axis_safety(text: str) -> tuple[int, str, list[str]]:
    """15점: approval/safety posture가 명시됐는가."""
    imps: list[str] = []
    score = 0
    if re.search(r"read-only|읽기 전용|승인|approval|ask|멈춤|wait|사용자 답", text, re.IGNORECASE):
        score += 6
    else:
        imps.append("승인/멈춤/read-only 등 safety posture 부재")
    if re.search(r"sandbox|config\.toml|approval_policy|allowed-tools|권한", text, re.IGNORECASE):
        score += 4
    else:
        imps.append("Codex 권한 모델/config 언급 부재")
    if re.search(r"rm\s+-rf|git push --force|git reset --hard|DROP TABLE", text):
        imps.append("파괴적 명령 문자열 포함")
    else:
        score += 5
    return score, "safety posture", imps


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
    """12점: output/handoff/artifact contract가 있는가."""
    score = 0
    imps: list[str] = []
    if re.search(r"```(?:markdown|json|text)?", text):
        score += 4
    else:
        imps.append("fenced output/template 예시 부재")
    if re.search(r"OUTPUT FORMAT|출력|산출물|artifact|handoff|핸드오프", text, re.IGNORECASE):
        score += 4
    else:
        imps.append("출력/산출물 계약 부재")
    positions = [text.find(b) for b in FIVE_BLOCKS]
    found = [b for b, p in zip(FIVE_BLOCKS, positions) if p != -1]
    if not found or (len(found) == len(FIVE_BLOCKS) and positions == sorted(positions)):
        score += 4
    else:
        imps.append("5블록을 일부만 쓰거나 순서가 어긋남")
    return score, "output contract", imps


def axis_budget(text: str) -> tuple[int, str, list[str]]:
    """5점: 라인 예산 (자기완결 프롬프트 ≤320줄)."""
    n = len(text.splitlines())
    if n <= 320:
        return 5, f"{n} lines", []
    return 2, f"{n} lines (>320)", [f"본문 {n}줄 — 320 초과, 압축 권장"]


AXES = [
    ("명령·목적 계약", axis_identity, 15),
    ("사용 범위·경계", axis_scope, 15),
    ("Workflow 절차 정합", axis_phases, 15),
    ("Safety / approval posture", axis_safety, 15),
    ("독립 트리 drift 가드", axis_drift_guard, 15),
    ("인자 규약", axis_args, 8),
    ("출력·산출물 계약", axis_template, 12),
    ("라인 예산", axis_budget, 5),
]


def score_prompt(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    axis_results = []
    total = 0
    all_imps: list[str] = []
    for idx, (name, fn, mx) in enumerate(AXES, start=1):
        if fn is axis_identity:
            s, reason, imps = fn(text, path)
        else:
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
