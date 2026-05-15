#!/usr/bin/env python3
"""Self-verification for the /on-call-elian skill.

Stdlib only (no external dependencies). Designed to be chainable: supports
--json output for programmatic consumption.

Usage:
    python3 validate_skill.py             # human-readable report
    python3 validate_skill.py --json      # JSON output
    python3 validate_skill.py --quiet     # exit code only
    python3 validate_skill.py --help

Exits 0 on PASS, 1 on FAIL.

What it checks:
  - frontmatter required fields + name == dir name
  - disable-model-invocation: true (user-agency guard)
  - required sections present (workflow, output format, forbidden, pitfalls)
  - the 5-block LOCKED OUTPUT FORMAT contract is documented in order
  - references/ has persona-daniel.md + example-review.md and SKILL.md links them
  - scripts/ dir exists
  - persona override mechanism (--persona arg) documented
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

REQUIRED_FRONTMATTER = ["name", "description", "when_to_use", "argument-hint", "allowed-tools"]

REQUIRED_SECTIONS = [
    r"^##\s+Where this fits",
    r"^##\s+What's automated vs what needs your taste",
    r"^##\s+OUTPUT FORMAT",
    r"^##\s+Workflow",
    r"^##\s+Pitfall",
    r"^##\s+Forbidden",
]

# The 5-block locked contract. Order matters — these must appear in this
# sequence inside the OUTPUT FORMAT fenced block.
OUTPUT_BLOCKS = ["## 결론", "## 트레이드오프", "## 운영 리스크", "## 페르소나 압박 질문", "## 다음 질문"]

REQUIRED_REFERENCES = ["persona-daniel.md", "example-review.md"]


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


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
    fm = _frontmatter(_read(SKILL_FILE))
    missing = [k for k in REQUIRED_FRONTMATTER if k not in fm]
    name_ok = fm.get("name") == SKILL_NAME
    return CheckResult(
        name=f"frontmatter: required fields + name=={SKILL_NAME}",
        passed=not missing and name_ok,
        detail=f"missing={missing}, name_match={name_ok}",
    )


def check_disable_model_invocation() -> CheckResult:
    fm = _frontmatter(_read(SKILL_FILE))
    has = fm.get("disable-model-invocation") == "true"
    return CheckResult(
        name="frontmatter: disable-model-invocation: true",
        passed=has,
        detail="found" if has else "missing (user-agency guard required)",
    )


def check_required_sections() -> CheckResult:
    text = _read(SKILL_FILE)
    missing = [p for p in REQUIRED_SECTIONS if not re.search(p, text, re.MULTILINE)]
    return CheckResult(
        name=f"required sections present ({len(REQUIRED_SECTIONS)} total)",
        passed=not missing,
        detail=f"missing={missing}",
    )


def check_output_format_contract() -> CheckResult:
    """The 5 blocks must appear, in order, in the SKILL.md body."""
    text = _read(SKILL_FILE)
    positions = []
    for block in OUTPUT_BLOCKS:
        idx = text.find(block)
        positions.append(idx)
    found_all = all(p != -1 for p in positions)
    in_order = found_all and positions == sorted(positions)
    return CheckResult(
        name="5-block LOCKED OUTPUT FORMAT documented in order",
        passed=found_all and in_order,
        detail=(
            "ok" if (found_all and in_order)
            else f"found_all={found_all}, in_order={in_order}, positions={positions}"
        ),
    )


def check_references_dir() -> CheckResult:
    refs = SKILL_DIR / "references"
    if not refs.is_dir():
        return CheckResult(name="references/ has persona + example files", passed=False, detail="missing dir")
    present = {p.name for p in refs.iterdir()}
    missing = [f for f in REQUIRED_REFERENCES if f not in present]
    return CheckResult(
        name="references/ has persona + example files",
        passed=not missing,
        detail=f"missing={missing}" if missing else f"{len(present)} file(s)",
    )


def check_references_linked() -> CheckResult:
    text = _read(SKILL_FILE)
    linked = [f for f in REQUIRED_REFERENCES if re.search(rf"references/{re.escape(f)}", text)]
    missing = [f for f in REQUIRED_REFERENCES if f not in linked]
    return CheckResult(
        name="SKILL.md explicitly links each reference file",
        passed=not missing,
        detail=f"missing_links={missing}" if missing else "all linked",
    )


def check_scripts_dir() -> CheckResult:
    scripts = SKILL_DIR / "scripts"
    return CheckResult(
        name="scripts/ directory exists",
        passed=scripts.is_dir(),
        detail="present" if scripts.is_dir() else "missing",
    )


def check_persona_override() -> CheckResult:
    """Portability: the skill must document a persona override mechanism."""
    text = _read(SKILL_FILE)
    has_arg = "--persona" in text
    return CheckResult(
        name="persona override (--persona arg) documented",
        passed=has_arg,
        detail="--persona found" if has_arg else "no override mechanism",
    )


CHECKS = [
    check_frontmatter,
    check_disable_model_invocation,
    check_required_sections,
    check_output_format_contract,
    check_references_dir,
    check_references_linked,
    check_scripts_dir,
    check_persona_override,
]


def run_all() -> tuple[list[CheckResult], bool]:
    results = [fn() for fn in CHECKS]
    return results, all(r.passed for r in results)


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
