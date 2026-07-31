#!/usr/bin/env python3
"""Self-verification for the /verify-before-claiming skill.

Stdlib only. Supports --json for programmatic consumption.
This skill is intentionally always-on (disable-model-invocation: false) and read-only:
its value is firing right before a completion claim, and it never edits code.

Generic structure checks come from `tools/skill_check.py`; only the doctrine markers
specific to this gate live here.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Walk up to the repository checkout this skill lives in; a fixed `parents[N]` would
# break the moment a skill moves between plugins.
sys.path.insert(0, str(next(
    p / "tools" for p in Path(__file__).resolve().parents if (p / "tools" / "skill_check.py").is_file()
)))

from skill_check import SkillValidator, run_cli  # noqa: E402

VALIDATOR = SkillValidator(Path(__file__).resolve().parents[1])

REQUIRED_FRONTMATTER = [
    "name",
    "description",
    "when_to_use",
    "argument-hint",
    "allowed-tools",
    "disable-model-invocation",
]

REQUIRED_SECTIONS = [
    r"^##\s+The Iron Law",
    r"^##\s+The Gate Function",
    r"^##\s+Standing Rules",
    r"^##\s+Forbidden",
    r"^##\s+Pitfalls",
    r"^##\s+Validation",
    r"^##\s+Pre-flight checklist",
]

CONTENT_MARKERS = [
    "NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION EVIDENCE",
    "Claim → Requires → Not sufficient",
    "Rationalization table",
    "Evidence before claims",
]

CHECKS = [
    # Always-on by design: the gate must be model-invocable to fire before a claim.
    lambda: VALIDATOR.check_frontmatter(REQUIRED_FRONTMATTER, model_invocation_disabled=False),
    # It governs claims; it must not be able to change code.
    lambda: VALIDATOR.check_read_only_tools(
        name="allowed tools are read-only (governs claims, never edits)"
    ),
    lambda: VALIDATOR.check_required_sections(REQUIRED_SECTIONS),
    lambda: VALIDATOR.check_markers(
        CONTENT_MARKERS, name="core doctrine markers present (iron law, claim table)"
    ),
    VALIDATOR.check_line_cap,
]


if __name__ == "__main__":
    sys.exit(
        run_cli(
            VALIDATOR.name,
            CHECKS,
            description="Validate /verify-before-claiming skill structure",
        )
    )
