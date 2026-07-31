#!/usr/bin/env python3
"""Self-verification for the /respond-to-review skill.

Stdlib only. Supports --json for programmatic consumption.
This skill is always-on (disable-model-invocation: false) and read-ish: it triages
review feedback and hands the edits to /fix or /improve, so it must not edit code itself.

Generic structure checks come from `tools/skill_check.py`; only the triage and handoff
markers specific to this skill live here.
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
    r"^##\s+The response pattern",
    r"^##\s+Forbidden responses",
    r"^##\s+Standing Rules",
    r"^##\s+Forbidden",
    r"^##\s+Pitfalls",
    r"^##\s+Validation",
    r"^##\s+Pre-flight checklist",
]

CONTENT_MARKERS = [
    "You're absolutely right!",  # the forbidden-phrase example must be present
    "Verify before implementing",
    "YAGNI",
    "push back",
]

# Must hand execution off, not do it here.
HANDOFF_MARKERS = ["/fix", "/improve"]

CHECKS = [
    lambda: VALIDATOR.check_frontmatter(REQUIRED_FRONTMATTER, model_invocation_disabled=False),
    # Consumer-side triage only — execution is delegated to /fix or /improve.
    lambda: VALIDATOR.check_read_only_tools(
        name="allowed tools are read-only (triage only, execution delegated)"
    ),
    lambda: VALIDATOR.check_required_sections(REQUIRED_SECTIONS),
    lambda: VALIDATOR.check_markers(
        CONTENT_MARKERS, name="core doctrine markers present (no-performative, verify, YAGNI)"
    ),
    lambda: VALIDATOR.check_markers(
        HANDOFF_MARKERS, name="delegates execution to /fix and /improve"
    ),
    VALIDATOR.check_line_cap,
]


if __name__ == "__main__":
    sys.exit(
        run_cli(VALIDATOR.name, CHECKS, description="Validate /respond-to-review skill structure")
    )
