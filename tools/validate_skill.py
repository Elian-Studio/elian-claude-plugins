#!/usr/bin/env python3
"""Structural self-validation for a workflow skill directory.

Stdlib only (no external dependencies). Chainable: supports --json output for
programmatic consumption.

This is the single source for what used to be four byte-identical copies under
brainstorm/, fix/, implement/, and improve/ scripts/. The copies self-identified
by their own location; this version takes the skill directory as an argument
instead, so changing a rule is one edit rather than four.

The checks themselves live in `tools/skill_check.py`, shared with the skill-owned
validators that add their own skill-specific checks on top.

Usage:
    python3 tools/validate_skill.py <skill-dir> [<skill-dir> ...]
    python3 tools/validate_skill.py <skill-dir> --json    # JSON output
    python3 tools/validate_skill.py <skill-dir> --quiet   # exit code only

Exits 0 when every skill passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from skill_check import (
    Check,
    SkillValidator,
    format_human,
    json_payload,
    run_checks,
)

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

# The retired `scripts/ directory exists` check is deliberately absent: it only ever
# passed because the checker itself lived in that directory, so it asserted nothing.


def structural_checks(validator: SkillValidator) -> list[Check]:
    return [
        lambda: validator.check_frontmatter(REQUIRED_FRONTMATTER),
        validator.check_model_invocation_disabled,
        lambda: validator.check_required_sections(REQUIRED_SECTIONS),
        validator.check_references_dir,
        validator.check_references_linked,
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the structure of one or more skill directories.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("skill_dir", nargs="+", type=Path, help="path to a skill directory")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of human report")
    parser.add_argument("--quiet", action="store_true", help="suppress output; exit code only")
    args = parser.parse_args()

    reports = []
    all_ok = True
    for raw in args.skill_dir:
        validator = SkillValidator(raw)
        if not validator.skill_file.is_file():
            print(f"error: {raw}/SKILL.md not found", file=sys.stderr)
            all_ok = False
            continue
        results, overall = run_checks(structural_checks(validator))
        all_ok = all_ok and overall
        if args.quiet:
            continue
        if args.json:
            reports.append(json_payload(validator.name, results, overall))
        else:
            print(format_human(validator.name, results, overall))

    if args.json and not args.quiet:
        # Always a list, even for one skill. Returning a bare object for N==1 and a list
        # otherwise means `jq '.[].overall'` breaks on one input and `jq '.overall'` breaks
        # on several — and the shape flips silently when a directory is skipped.
        print(json.dumps(reports, ensure_ascii=False, indent=2))

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
