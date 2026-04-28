#!/usr/bin/env python3
"""SKILL.md 품질 평가 (LLM, 100점 만점, 90 미만 → exit 1).

사용법:
    python scripts/evaluate_skill.py <SKILL.md path> [<SKILL.md path>...]

환경변수:
    ANTHROPIC_API_KEY (필수) — Anthropic API 키
    SKILL_EVAL_MODEL          — 모델 ID (기본: claude-sonnet-4-6)
    SKILL_EVAL_PASS_SCORE     — 통과 점수 (기본: 90)
    SKILL_EVAL_OUTPUT         — 결과 JSON 파일 경로 (기본: evaluation-results.json)

산출물:
    evaluation-results.json — 모든 평가된 스킬의 점수와 상세
    표준출력에 사람이 읽을 요약 표
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic 패키지 필요. `pip install anthropic` 실행.", file=sys.stderr)
    sys.exit(2)


MODEL = os.environ.get("SKILL_EVAL_MODEL", "claude-sonnet-4-6")
PASS_SCORE = int(os.environ.get("SKILL_EVAL_PASS_SCORE", "90"))
OUTPUT_PATH = os.environ.get("SKILL_EVAL_OUTPUT", "evaluation-results.json")
RUBRIC_PATH = Path(__file__).parent / "rubric.md"


SUBMIT_TOOL = {
    "name": "submit_evaluation",
    "description": "SKILL.md 평가 결과를 구조화된 JSON 으로 제출한다. 10개 축 각각 0~10 정수 점수, 한 줄 사유, 개선 제안을 포함.",
    "input_schema": {
        "type": "object",
        "properties": {
            "axes": {
                "type": "array",
                "minItems": 10,
                "maxItems": 10,
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "minimum": 1, "maximum": 10},
                        "name": {"type": "string"},
                        "score": {"type": "integer", "minimum": 0, "maximum": 10},
                        "max": {"type": "integer", "const": 10},
                        "reason": {"type": "string", "description": "한 문장. 점수 사유."},
                        "improvements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "구체적 개선 제안 (옵션, 빈 배열 가능).",
                        },
                    },
                    "required": ["id", "name", "score", "max", "reason", "improvements"],
                },
            },
            "total": {"type": "integer", "minimum": 0, "maximum": 100},
            "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
            "blocking_issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "정적 검증을 통과했지만 LLM 관점에서 명백한 차단 이슈 (보통 빈 배열).",
            },
            "top_improvements": {
                "type": "array",
                "items": {"type": "string"},
                "description": "점수 상승에 가장 효과적인 개선 3~5개.",
            },
            "summary": {"type": "string", "description": "한 문장 총평."},
        },
        "required": [
            "axes",
            "total",
            "verdict",
            "blocking_issues",
            "top_improvements",
            "summary",
        ],
    },
}


def build_system_prompt(rubric: str) -> list[dict]:
    return [
        {
            "type": "text",
            "text": (
                "당신은 Claude Code 플러그인 마켓플레이스의 SKILL.md 품질 평가자입니다.\n"
                "공식 가이드(https://code.claude.com/docs/en/skills)와 아래 루브릭에 따라 채점합니다.\n\n"
                "원칙:\n"
                "- 각 축은 0~10 정수 점수.\n"
                "- 사유는 한 문장. 추측 대신 본문에서 확인 가능한 사실 인용.\n"
                "- 90점 통과 게이트가 있으므로 의심스러우면 보수적으로 채점.\n"
                "- 개선 제안은 실행 가능한 수준으로 구체화 (모호한 '더 좋게' 금지).\n"
                "- 일반화 / 공유 적합성 축에서는 마켓플레이스에 배포되어 다른 팀이 쓴다는 전제로 평가.\n\n"
                "루브릭:\n\n"
                + rubric
            ),
            "cache_control": {"type": "ephemeral"},
        }
    ]


def evaluate_one(client: Anthropic, system: list[dict], skill_path: Path) -> dict:
    content = skill_path.read_text(encoding="utf-8")
    user_msg = (
        f"평가 대상: `{skill_path}`\n"
        f"줄 수: {len(content.splitlines())}\n"
        f"바이트: {len(content.encode('utf-8'))}\n\n"
        f"--- SKILL.md 시작 ---\n{content}\n--- SKILL.md 끝 ---\n\n"
        "위 SKILL.md 를 루브릭의 10개 축으로 평가하고 submit_evaluation 도구로 제출하세요."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system,
        tools=[SUBMIT_TOOL],
        tool_choice={"type": "tool", "name": "submit_evaluation"},
        messages=[{"role": "user", "content": user_msg}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "submit_evaluation":
            result = dict(block.input)
            # 자가 검산: total 이 axes 합과 일치하는지 확인
            axes_sum = sum(a["score"] for a in result["axes"])
            if axes_sum != result["total"]:
                # LLM 이 잘못 합산한 경우 강제 보정
                result["total"] = axes_sum
                result["_total_corrected"] = True
            # verdict 자동 보정
            result["verdict"] = "PASS" if result["total"] >= PASS_SCORE else "FAIL"
            # 사용량 기록
            result["_usage"] = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_read_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
                "cache_creation_tokens": getattr(
                    response.usage, "cache_creation_input_tokens", 0
                ),
            }
            return result

    raise RuntimeError(f"submit_evaluation tool_use 블록 없음: {response.content}")


def format_summary(path: Path, result: dict) -> str:
    lines = []
    verdict_icon = "✅" if result["verdict"] == "PASS" else "❌"
    lines.append(
        f"\n{verdict_icon} {path}  →  {result['total']}/100  ({result['verdict']}, 통과 기준 {PASS_SCORE})"
    )
    lines.append("")
    lines.append("| # | 축 | 점수 | 사유 |")
    lines.append("|---|---|---|---|")
    for ax in result["axes"]:
        reason = ax["reason"].replace("|", "\\|")
        lines.append(f"| {ax['id']} | {ax['name']} | {ax['score']}/{ax['max']} | {reason} |")
    if result.get("blocking_issues"):
        lines.append("")
        lines.append("**Blocking issues**:")
        for b in result["blocking_issues"]:
            lines.append(f"- {b}")
    if result.get("top_improvements"):
        lines.append("")
        lines.append("**Top improvements**:")
        for imp in result["top_improvements"]:
            lines.append(f"- {imp}")
    lines.append("")
    lines.append(f"_Summary_: {result['summary']}")
    usage = result.get("_usage", {})
    if usage:
        lines.append(
            f"_Token usage_: in={usage['input_tokens']} out={usage['output_tokens']} "
            f"cache_read={usage['cache_read_tokens']} cache_create={usage['cache_creation_tokens']}"
        )
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: evaluate_skill.py <SKILL.md path> [...]", file=sys.stderr)
        return 2

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY 환경변수 미설정", file=sys.stderr)
        return 2

    if not RUBRIC_PATH.exists():
        print(f"ERROR: rubric.md 없음: {RUBRIC_PATH}", file=sys.stderr)
        return 2

    rubric = RUBRIC_PATH.read_text(encoding="utf-8")
    client = Anthropic(api_key=api_key)
    system = build_system_prompt(rubric)

    skill_paths = [Path(p) for p in argv[1:]]
    results: list[dict] = []
    all_pass = True
    for path in skill_paths:
        if not path.exists():
            print(f"::error file={path}::파일 없음", file=sys.stderr)
            all_pass = False
            results.append({"path": str(path), "error": "file not found"})
            continue
        try:
            result = evaluate_one(client, system, path)
            result["path"] = str(path)
            results.append(result)
            print(format_summary(path, result))
            if result["verdict"] != "PASS":
                all_pass = False
        except Exception as exc:  # noqa: BLE001
            print(f"::error file={path}::평가 실패: {exc}", file=sys.stderr)
            all_pass = False
            results.append({"path": str(path), "error": str(exc)})

    Path(OUTPUT_PATH).write_text(
        json.dumps(
            {"results": results, "pass_score": PASS_SCORE, "all_pass": all_pass},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\n결과 저장: {OUTPUT_PATH}")

    if not all_pass:
        print(
            f"\n❌ 일부 스킬이 {PASS_SCORE}점 미만. 머지 차단.",
            file=sys.stderr,
        )
        return 1
    print(f"\n✅ 모든 스킬 {PASS_SCORE}점 이상.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
