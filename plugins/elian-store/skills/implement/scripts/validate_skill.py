#!/usr/bin/env python3
"""Self-verification for the /implement skill.

Stdlib only (no external dependencies). Designed to be chainable: supports
--json output for programmatic consumption.

Usage:
    python3 validate_skill.py             # human-readable report
    python3 validate_skill.py --json      # JSON output
    python3 validate_skill.py --quiet     # exit code only
    python3 validate_skill.py --help

Exits 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_NAME = SKILL_DIR.name
SKILL_FILE = SKILL_DIR / "SKILL.md"


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


REQUIRED_FRONTMATTER = ["name", "description", "when_to_use", "argument-hint", "allowed-tools"]
REQUIRED_SECTIONS = [
    r"^##\s+(Workflow|Procedure)",
    r"^##\s+Standing Rules",
    r"^##\s+Forbidden",
    r"^##\s+Pitfall",
    r"^##\s+Where this fits",
    r"^##\s+Manual decision gating",
    r"^##\s+Reflection",
    r"^##\s+Persistent artifacts",
    r"^##\s+BEFORE\s*/\s*AFTER",
    r"^##\s+Pre-flight checklist",
]


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def check_frontmatter() -> CheckResult:
    text = _read(SKILL_FILE)
    fm = _frontmatter(text)
    missing = [k for k in REQUIRED_FRONTMATTER if k not in fm]
    name_ok = fm.get("name") == SKILL_NAME
    return CheckResult(
        name=f"frontmatter: required fields + name=={SKILL_NAME}",
        passed=not missing and name_ok,
        detail=f"missing={missing}, name_match={name_ok}",
    )


def check_disable_model_invocation() -> CheckResult:
    text = _read(SKILL_FILE)
    fm = _frontmatter(text)
    has = fm.get("disable-model-invocation") == "true"
    return CheckResult(
        name="frontmatter: disable-model-invocation: true",
        passed=has,
        detail="found" if has else "missing",
    )


def check_required_sections() -> CheckResult:
    text = _read(SKILL_FILE)
    missing: list[str] = []
    for pat in REQUIRED_SECTIONS:
        if not re.search(pat, text, re.MULTILINE):
            missing.append(pat)
    return CheckResult(
        name=f"required sections present ({len(REQUIRED_SECTIONS)} total)",
        passed=not missing,
        detail=f"missing={[p for p in missing]}",
    )


def check_references_dir() -> CheckResult:
    refs = SKILL_DIR / "references"
    if not refs.is_dir():
        return CheckResult(name="references/ directory exists with ≥1 file", passed=False, detail="missing")
    files = [p for p in refs.iterdir() if p.suffix in {".md", ".html", ".txt"}]
    return CheckResult(
        name="references/ directory exists with ≥1 file",
        passed=len(files) >= 1,
        detail=f"{len(files)} file(s)",
    )


def check_references_linked() -> CheckResult:
    text = _read(SKILL_FILE)
    has = re.search(r"\[[^\]]+\]\(\s*references/", text) is not None
    return CheckResult(
        name="SKILL.md links into references/",
        passed=has,
        detail="linked" if has else "missing",
    )


def check_scripts_dir() -> CheckResult:
    scripts = SKILL_DIR / "scripts"
    if not scripts.is_dir():
        return CheckResult(name="scripts/ directory exists", passed=False, detail="missing")
    return CheckResult(name="scripts/ directory exists", passed=True, detail="present")


CHECKS = [
    check_frontmatter,
    check_disable_model_invocation,
    check_required_sections,
    check_references_dir,
    check_references_linked,
    check_scripts_dir,
]


def run_all() -> tuple[list[CheckResult], bool]:
    results = [fn() for fn in CHECKS]
    overall = all(r.passed for r in results)
    return results, overall


def format_human(results: list[CheckResult], overall: bool) -> str:
    lines = ["=" * 70, f"  /{SKILL_NAME} self-validation", "=" * 70]
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        lines.append(f"  [{mark}] {r.name}")
        if r.detail:
            lines.append(f"         {r.detail}")
    lines.append("-" * 70)
    lines.append(f"  Overall: {'PASS' if overall else 'FAIL'}")
    lines.append("=" * 70)
    return "\n".join(lines)


def format_json(results: list[CheckResult], overall: bool) -> str:
    return json.dumps(
        {
            "skill": SKILL_NAME,
            "overall": "pass" if overall else "fail",
            "checks": [r.to_dict() for r in results],
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed),
            },
        },
        ensure_ascii=False,
        indent=2,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Validate the /{SKILL_NAME} skill structure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of human report")
    parser.add_argument("--quiet", action="store_true", help="suppress output; exit code only")
    args = parser.parse_args()

    results, overall = run_all()

    if args.quiet:
        pass
    elif args.json:
        print(format_json(results, overall))
    else:
        print(format_human(results, overall))

    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
