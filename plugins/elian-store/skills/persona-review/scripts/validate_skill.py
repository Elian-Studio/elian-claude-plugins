#!/usr/bin/env python3
"""Self-verification for the /persona-review skill.

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
  - references/ has personas/daniel.md + example-review.md and SKILL.md links them
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
# sequence inside the OUTPUT FORMAT fenced block. Each "block" is a list of
# accepted headers (default persona uses Korean; English custom personas use
# the English fallbacks). The check passes if ANY header from each list is
# found, and the chosen headers appear in document order.
OUTPUT_BLOCK_VARIANTS: list[list[str]] = [
    ["## 결론", "## Conclusion"],
    ["## 트레이드오프", "## Trade-offs", "## Tradeoffs"],
    ["## 운영 리스크", "## Operational risks", "## Operational Risk"],
    ["## 페르소나 압박 질문", "## Pressure questions", "## Pressure Questions"],
    ["## 다음 질문", "## Next question", "## Next Question"],
]

# Persona library lives under references/personas/. Each *.md file there is
# a persona definition (e.g., daniel.md, evans.md). The skill requires at
# least one persona file to exist. Legacy layout (references/persona-*.md)
# is still recognized for backwards compatibility.
PERSONAS_DIR_NAME = "personas"
LEGACY_PERSONA_GLOB = "persona-*.md"
REQUIRED_REFERENCE_FILES = ["example-review.md"]  # additional fixed references


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
    """The 5 blocks must appear, in order, in the SKILL.md body.

    Each block accepts multiple header variants (e.g., Korean default +
    English fallback). At least one variant from each block must be found,
    and the chosen variants must appear in document order.
    """
    text = _read(SKILL_FILE)
    chosen: list[tuple[str, int]] = []
    missing_blocks: list[int] = []
    for i, variants in enumerate(OUTPUT_BLOCK_VARIANTS):
        first_hit: tuple[str, int] | None = None
        for v in variants:
            idx = text.find(v)
            if idx != -1 and (first_hit is None or idx < first_hit[1]):
                first_hit = (v, idx)
        if first_hit is None:
            missing_blocks.append(i)
        else:
            chosen.append(first_hit)
    found_all = not missing_blocks
    positions = [p for _, p in chosen]
    in_order = found_all and positions == sorted(positions)
    return CheckResult(
        name="5-block LOCKED OUTPUT FORMAT documented in order",
        passed=found_all and in_order,
        detail=(
            f"ok ({', '.join(h for h, _ in chosen)})" if (found_all and in_order)
            else f"found_all={found_all}, in_order={in_order}, missing={missing_blocks}, chosen={chosen}"
        ),
    )


def _list_personas() -> list[str]:
    """Return persona file names from both the new and legacy layouts."""
    refs = SKILL_DIR / "references"
    found: list[str] = []
    personas_dir = refs / PERSONAS_DIR_NAME
    if personas_dir.is_dir():
        found.extend(sorted(p.name for p in personas_dir.iterdir() if p.suffix == ".md"))
    if refs.is_dir():
        found.extend(
            sorted(p.name for p in refs.iterdir()
                   if p.is_file() and p.name.startswith("persona-") and p.suffix == ".md")
        )
    return found


def check_references_dir() -> CheckResult:
    refs = SKILL_DIR / "references"
    if not refs.is_dir():
        return CheckResult(name="references/ has personas/ + example files", passed=False, detail="missing dir")
    present = {p.name for p in refs.iterdir() if p.is_file()}
    personas = _list_personas()
    missing_fixed = [f for f in REQUIRED_REFERENCE_FILES if f not in present]
    missing_persona = not personas
    passed = not missing_fixed and not missing_persona
    if passed:
        detail = f"{len(present)} top-level file(s); persona(s): {personas}"
    else:
        parts = []
        if missing_persona:
            parts.append(f"no persona file found in references/{PERSONAS_DIR_NAME}/ nor as references/{LEGACY_PERSONA_GLOB}")
        if missing_fixed:
            parts.append(f"missing fixed: {missing_fixed}")
        detail = "; ".join(parts)
    return CheckResult(
        name="references/ has personas/ + example files",
        passed=passed,
        detail=detail,
    )


def check_references_linked() -> CheckResult:
    """SKILL.md must link example-review.md AND at least one persona file
    (either references/personas/<name>.md or references/persona-*.md)."""
    text = _read(SKILL_FILE)
    fixed_linked = [f for f in REQUIRED_REFERENCE_FILES if re.search(rf"references/{re.escape(f)}", text)]
    fixed_missing = [f for f in REQUIRED_REFERENCE_FILES if f not in fixed_linked]
    persona_link = (
        re.search(rf"references/{PERSONAS_DIR_NAME}/[\w-]+\.md", text)
        or re.search(r"references/persona-[\w-]+\.md", text)
    )
    parts = []
    if fixed_missing:
        parts.append(f"missing_fixed_links={fixed_missing}")
    if not persona_link:
        parts.append("no persona file link found")
    passed = not fixed_missing and persona_link is not None
    return CheckResult(
        name="SKILL.md explicitly links example + at least one persona file",
        passed=passed,
        detail="all linked" if passed else "; ".join(parts),
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
