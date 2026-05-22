#!/usr/bin/env python3
"""/design-ui self-validation.

design-ui SKILL.md + references + templates 의 구조 일관성 검증.
stdlib 만 사용.

검증 항목:
  - frontmatter 필수 필드 (name, description, when_to_use, argument-hint, allowed-tools)
  - name 이 'design-ui' 와 일치
  - 5 Phase 표현 (Interview / Reference / Wireframe / Visual / Deliver) 본문 명시
  - templates/{wireframe,visual}.html + templates/{brief,references,DESIGN}.md 존재
  - references/ux-checklist.md 존재
  - $ARGUMENTS 또는 argument-hint 본문 언급 (override mechanism)
  - Standing rules 섹션 존재
  - Pitfall / Failure modes 섹션 존재

사용법:
  python3 validate_skill.py
  python3 validate_skill.py --json
  python3 validate_skill.py --quiet

종료 코드:
  0 — PASS
  1 — FAIL
  2 — 사용법 오류
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
TEMPLATES_DIR = SKILL_DIR / "templates"
REFERENCES_DIR = SKILL_DIR / "references"

REQUIRED_FRONTMATTER = ["name", "description", "when_to_use", "argument-hint", "allowed-tools"]
REQUIRED_PHASES = ["Interview", "Reference", "Wireframe", "Visual", "Deliver"]
REQUIRED_TEMPLATES = ["brief.md", "references.md", "wireframe.html", "visual.html", "DESIGN.md"]
REQUIRED_REFERENCES = ["ux-checklist.md"]


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm: dict[str, str] = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            break
        m = re.match(r"^([a-zA-Z_-][a-zA-Z0-9_-]*)\s*:\s*(.*)$", lines[i])
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def check_frontmatter(text: str) -> tuple[bool, str]:
    fm = parse_frontmatter(text)
    missing = [f for f in REQUIRED_FRONTMATTER if not fm.get(f)]
    if missing:
        return (False, f"missing fields: {missing}")
    if fm.get("name") != "design-ui":
        return (False, f"name='{fm.get('name')}' != 'design-ui'")
    return (True, "all required fields present, name matches")


def check_phases(body: str) -> tuple[bool, str]:
    missing = [p for p in REQUIRED_PHASES if p not in body]
    if missing:
        return (False, f"missing phases in body: {missing}")
    return (True, f"all 5 phases ({', '.join(REQUIRED_PHASES)}) present")


def check_templates() -> tuple[bool, str]:
    missing = [t for t in REQUIRED_TEMPLATES if not (TEMPLATES_DIR / t).exists()]
    if missing:
        return (False, f"missing templates: {missing}")
    return (True, f"all {len(REQUIRED_TEMPLATES)} templates present")


def check_references() -> tuple[bool, str]:
    missing = [r for r in REQUIRED_REFERENCES if not (REFERENCES_DIR / r).exists()]
    if missing:
        return (False, f"missing references: {missing}")
    return (True, f"all {len(REQUIRED_REFERENCES)} references present")


def check_override_mechanism(body: str) -> tuple[bool, str]:
    has_args = bool(re.search(r"\$ARGUMENTS|argument-hint", body))
    has_env = bool(re.search(r"\$\{?[A-Z_]+\}?|환경변수", body))
    if has_args and has_env:
        return (True, "$ARGUMENTS + env var both documented")
    if has_args:
        return (True, "$ARGUMENTS documented (env override optional)")
    return (False, "neither $ARGUMENTS nor env var documented in body")


def check_standing_rules(body: str) -> tuple[bool, str]:
    if re.search(r"^##\s+Standing rules", body, re.MULTILINE):
        return (True, "Standing rules section present")
    return (False, "Standing rules section missing")


def check_pitfall(body: str) -> tuple[bool, str]:
    if re.search(r"^##\s+(Pitfall|Failure modes|Known issues)", body, re.MULTILINE):
        return (True, "Pitfall/Failure modes section present")
    return (False, "Pitfall / Failure modes / Known issues section missing")


CHECKS = [
    ("frontmatter required fields + name match", lambda t, b: check_frontmatter(t)),
    ("5 Phases documented in body", lambda t, b: check_phases(b)),
    ("templates/ has required files", lambda t, b: check_templates()),
    ("references/ has required files", lambda t, b: check_references()),
    ("override mechanism ($ARGUMENTS / env)", lambda t, b: check_override_mechanism(b)),
    ("Standing rules section", lambda t, b: check_standing_rules(b)),
    ("Pitfall / Failure modes section", lambda t, b: check_pitfall(b)),
]


def run() -> dict:
    if not SKILL_MD.exists():
        return {"verdict": "FAIL", "error": f"SKILL.md not found at {SKILL_MD}"}
    text = SKILL_MD.read_text(encoding="utf-8")
    parts = re.split(r"^---$", text, maxsplit=2, flags=re.MULTILINE)
    body = parts[2] if len(parts) >= 3 else text

    results = []
    all_pass = True
    for name, fn in CHECKS:
        ok, detail = fn(text, body)
        results.append({"name": name, "pass": ok, "detail": detail})
        if not ok:
            all_pass = False
    return {
        "verdict": "PASS" if all_pass else "FAIL",
        "checks": results,
    }


def render_text(report: dict, quiet: bool = False) -> str:
    if "error" in report:
        return f"::error::{report['error']}"
    lines = ["=" * 70, "  /design-ui self-validation", "=" * 70]
    for c in report["checks"]:
        icon = "[PASS]" if c["pass"] else "[FAIL]"
        if quiet and c["pass"]:
            continue
        lines.append(f"  {icon} {c['name']}")
        lines.append(f"         {c['detail']}")
    lines.append("-" * 70)
    lines.append(f"  Overall: {report['verdict']}")
    lines.append("=" * 70)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_skill.py",
        description="/design-ui self-validation (structure + reference integrity). stdlib only.",
    )
    parser.add_argument("--json", dest="as_json", action="store_true", help="JSON output")
    parser.add_argument("--quiet", action="store_true", help="suppress PASS lines")
    args = parser.parse_args(argv)

    report = run()
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report, quiet=args.quiet))
    return 0 if report.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
