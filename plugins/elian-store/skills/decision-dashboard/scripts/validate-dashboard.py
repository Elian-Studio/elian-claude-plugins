#!/usr/bin/env python3
"""decision-dashboard 가 생성한 HTML 의 4가지 게이트를 검증.

stdlib 만 사용 (zero pip installs).

검사 항목:
  1. 미해결 placeholder ({{...}}) 0개
  2. 중첩 HTML 주석 0개 (<!-- ... <!-- ... --> ... -->)
  3. 모든 nav-link 의 data-id 가 실제 카드 id 와 매칭
  4. LANGUAGE GATE — 카드 본문(info-box, card-title, .opt 내부)에
     클래스명/테이블명/내부 약어 등 내부 식별자 노출 금지
     (단, .detail-panel 내부는 개발자 근거 영역으로 허용)

사용법:
  python3 validate-dashboard.py <html-file>
  python3 validate-dashboard.py <html-file> --json
  python3 validate-dashboard.py --help

종료 코드:
  0 — 모든 게이트 통과
  1 — 1개 이상 게이트 실패
  2 — 사용법 오류 / 파일 없음

JSON 출력 스키마 (--json):
  {
    "file": "...",
    "verdict": "PASS" | "FAIL",
    "gates": {
      "placeholders": {"pass": bool, "hits": [...]},
      "nested_comments": {"pass": bool, "hits": [...]},
      "navlink_card_match": {"pass": bool, "diff": "..."},
      "language_gate": {"pass": bool, "hits": [...]}
    }
  }
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


LANGUAGE_GATE_PATTERNS: dict[str, str] = {
    "ClassName (Camel 3+)": r"\b[A-Z][a-z]+(?:[A-Z][a-z]+){2,}\b",
    "snake_case_table": r"\b[a-z]+_[a-z]+(?:_[a-z]+)+\b",
    "internal_decision_no": r"(?:결정\s*)?#[A-Z]?[0-9]{2,}",
    "requirement_no": r"\bR[0-9]{1,2}\b",
    "tech_stack": r"\b(?:ShedLock|cron|@\w+|polling|@Scheduled)\b",
    "env_name": r"\b(?:stag|prod)\b",
}


def gate_placeholders(html: str) -> tuple[bool, list[str]]:
    hits = re.findall(r"\{\{[^}]+\}\}", html)
    return (not hits, hits)


def gate_nested_comments(html: str) -> tuple[bool, list[str]]:
    hits = re.findall(r"<!--[^-]*<!--", html)
    return (not hits, hits)


def gate_navlink_card_match(html: str) -> tuple[bool, str]:
    nav_ids = sorted(set(re.findall(r'data-id="(c[0-9]+)"', html)))
    card_ids = sorted(set(re.findall(r' id="(c[0-9]+)"', html)))
    if nav_ids == card_ids:
        return (True, "")
    only_nav = [i for i in nav_ids if i not in card_ids]
    only_card = [i for i in card_ids if i not in nav_ids]
    diff = []
    if only_nav:
        diff.append(f"nav-link 에 있지만 카드 없음: {only_nav}")
    if only_card:
        diff.append(f"카드 있지만 nav-link 없음: {only_card}")
    return (False, " / ".join(diff))


def gate_language(html: str) -> tuple[bool, list[str]]:
    # detail-panel 영역 제거 (개발자 근거 영역으로 허용)
    stripped = re.sub(
        r'<div class="detail-panel[^"]*"[^>]*>.*?</div>\s*</div>',
        "",
        html,
        flags=re.DOTALL,
    )
    # 카드 본문 추출
    scopes = re.findall(
        r'<div class="info-box[^"]*"[^>]*>(.*?)</div>', stripped, re.DOTALL
    )
    scopes += re.findall(
        r'<div class="card-title"[^>]*>(.*?)</div>', stripped, re.DOTALL
    )
    scopes += re.findall(
        r'<button class="opt"[^>]*>(.*?)</button>', stripped, re.DOTALL
    )
    body = "\n".join(scopes)

    hits: list[str] = []
    for name, pat in LANGUAGE_GATE_PATTERNS.items():
        for m in re.finditer(pat, body):
            hits.append(f"[{name}] {m.group()}")
    hits = sorted(set(hits))
    return (not hits, hits)


def validate(path: Path) -> dict:
    html = path.read_text(encoding="utf-8")
    p_pass, p_hits = gate_placeholders(html)
    n_pass, n_hits = gate_nested_comments(html)
    m_pass, m_diff = gate_navlink_card_match(html)
    l_pass, l_hits = gate_language(html)
    all_pass = p_pass and n_pass and m_pass and l_pass
    return {
        "file": str(path),
        "verdict": "PASS" if all_pass else "FAIL",
        "gates": {
            "placeholders": {"pass": p_pass, "hits": p_hits},
            "nested_comments": {"pass": n_pass, "hits": n_hits},
            "navlink_card_match": {"pass": m_pass, "diff": m_diff},
            "language_gate": {"pass": l_pass, "hits": l_hits},
        },
    }


def render_text(report: dict) -> str:
    lines = [f"=== {report['file']} ==="]
    icon_pass = "✓"
    icon_fail = "✗"
    g = report["gates"]

    def line(name: str, ok: bool, detail: str) -> str:
        return f"  {icon_pass if ok else icon_fail} {name}: {detail}"

    lines.append(
        line(
            "1. placeholders",
            g["placeholders"]["pass"],
            "0 hits"
            if g["placeholders"]["pass"]
            else f"{len(g['placeholders']['hits'])} hits — {g['placeholders']['hits'][:3]}",
        )
    )
    lines.append(
        line(
            "2. nested HTML comments",
            g["nested_comments"]["pass"],
            "0 hits"
            if g["nested_comments"]["pass"]
            else f"{len(g['nested_comments']['hits'])} hits",
        )
    )
    lines.append(
        line(
            "3. nav-link/card match",
            g["navlink_card_match"]["pass"],
            "matched"
            if g["navlink_card_match"]["pass"]
            else g["navlink_card_match"]["diff"],
        )
    )
    lines.append(
        line(
            "4. LANGUAGE GATE",
            g["language_gate"]["pass"],
            "no internal identifiers in card body"
            if g["language_gate"]["pass"]
            else f"{len(g['language_gate']['hits'])} leaks: " + ", ".join(g["language_gate"]["hits"][:5]),
        )
    )
    lines.append("")
    lines.append(
        f"Verdict: {report['verdict']}"
        + (" — 모든 게이트 통과" if report["verdict"] == "PASS" else " — 위 항목 수정 필요")
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate-dashboard.py",
        description="decision-dashboard HTML 4-gate 검증 (placeholders / nested-comments / navlink-match / LANGUAGE GATE)",
    )
    parser.add_argument("html_file", help="검증할 HTML 파일 경로")
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="결과를 JSON 으로 출력 (다른 스킬이 chaining 가능)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="첫 게이트 실패 시 즉시 종료 (CI 용)",
    )
    args = parser.parse_args(argv)

    path = Path(args.html_file)
    if not path.exists():
        print(f"::error file={path}::파일 없음", file=sys.stderr)
        return 2

    report = validate(path)

    if args.json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))

    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
