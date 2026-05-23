#!/usr/bin/env python3
"""/ai-assisted-feature-development self-validation.

스킬 구조와 reference 파일 무결성을 결정적으로 검증한다. stdlib만 사용.

검증 항목:
  - frontmatter 필수 필드 (name, description, when_to_use, argument-hint, allowed-tools)
  - name 이 'ai-assisted-feature-development' 와 일치
  - 9 Phase 표현 (Feature Framing / BDD / SDD / DDD / AI-TDD / Context / Agentic / Review / SPDD)
  - references/ 안 필수 8 파일 존재 + SKILL.md 에서 link
  - Standing rules / Forbidden / Pitfall / Where this fits 섹션 존재
  - $ARGUMENTS 또는 환경변수 본문 언급
  - Definition of Done / 병합 차단 / 안티패턴 섹션 본문 명시

사용법:
  python3 validate_skill.py
  python3 validate_skill.py --json
  python3 validate_skill.py --quiet
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

EXPECTED_NAME = "ai-assisted-feature-development"
REQUIRED_FRONTMATTER = ["name", "description", "when_to_use", "argument-hint", "allowed-tools"]
REQUIRED_PHASES = [
    "Feature Framing",
    "BDD",
    "SDD",
    "DDD",
    "AI-TDD",
    "Context Engineering",
    "Agentic Coding",
    "Review",
    "SPDD",
]
REQUIRED_REFERENCES = [
    "master-prompt.md",
    "stage-prompts.md",
    "login-example.md",
    "other-feature-examples.md",
    "artifact-structure.md",
    "definition-of-done.md",
    "anti-patterns.md",
    "quick-start.md",
]


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
    if fm.get("name") != EXPECTED_NAME:
        return (False, f"name='{fm.get('name')}' != '{EXPECTED_NAME}'")
    return (True, "all required fields present, name matches")


def check_phases(body: str) -> tuple[bool, str]:
    missing = [p for p in REQUIRED_PHASES if p not in body]
    if missing:
        return (False, f"missing phases: {missing}")
    return (True, f"all {len(REQUIRED_PHASES)} phases present")


def check_references_files() -> tuple[bool, str]:
    missing = [r for r in REQUIRED_REFERENCES if not (REFERENCES_DIR / r).exists()]
    if missing:
        return (False, f"missing files: {missing}")
    return (True, f"all {len(REQUIRED_REFERENCES)} references present")


def check_references_linked(body: str) -> tuple[bool, str]:
    missing = []
    for r in REQUIRED_REFERENCES:
        if not re.search(rf"references/{re.escape(r)}", body):
            missing.append(r)
    if missing:
        return (False, f"missing links in SKILL.md: {missing}")
    return (True, "all references linked in SKILL.md")


def check_override(body: str) -> tuple[bool, str]:
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


def check_forbidden(body: str) -> tuple[bool, str]:
    if re.search(r"^##\s+Forbidden", body, re.MULTILINE):
        return (True, "Forbidden section present")
    return (False, "Forbidden section missing")


def check_pitfall(body: str) -> tuple[bool, str]:
    if re.search(r"^##\s+(Pitfall|Failure modes|Known issues|안티패턴)", body, re.MULTILINE):
        return (True, "Pitfall / 안티패턴 section present")
    return (False, "Pitfall section missing")


def check_where_this_fits(body: str) -> tuple[bool, str]:
    if re.search(r"^##\s+Where this fits", body, re.MULTILINE):
        return (True, "Where this fits section present")
    return (False, "Where this fits section missing")


def check_dod(body: str) -> tuple[bool, str]:
    if re.search(r"Definition of Done|완료 기준|DoD", body, re.IGNORECASE):
        return (True, "Definition of Done present")
    return (False, "Definition of Done missing")


CHECKS = [
    ("frontmatter required + name match", lambda t, b: check_frontmatter(t)),
    ("9 Phases documented", lambda t, b: check_phases(b)),
    ("references/ files exist", lambda t, b: check_references_files()),
    ("SKILL.md links all references", lambda t, b: check_references_linked(b)),
    ("override mechanism ($ARGUMENTS / env)", lambda t, b: check_override(b)),
    ("Standing rules section", lambda t, b: check_standing_rules(b)),
    ("Forbidden section", lambda t, b: check_forbidden(b)),
    ("Pitfall / 안티패턴 section", lambda t, b: check_pitfall(b)),
    ("Where this fits section", lambda t, b: check_where_this_fits(b)),
    ("Definition of Done documented", lambda t, b: check_dod(b)),
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
    return {"verdict": "PASS" if all_pass else "FAIL", "checks": results}


def render_text(report: dict, quiet: bool = False) -> str:
    if "error" in report:
        return f"::error::{report['error']}"
    lines = ["=" * 70, "  /ai-assisted-feature-development self-validation", "=" * 70]
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
        description="/ai-assisted-feature-development self-validation. stdlib only.",
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
