#!/usr/bin/env python3
"""Self-verification for the /review skill.

Stdlib only. Supports --json for programmatic consumption.
Generic structure checks (frontmatter, sections, read-only tools, report shape) come from
`tools/skill_check.py`; only the /review-specific contract checks live here.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Walk up to the repository checkout this skill lives in; a fixed `parents[N]` would
# break the moment a skill moves between plugins.
sys.path.insert(0, str(next(
    p / "tools" for p in Path(__file__).resolve().parents if (p / "tools" / "skill_check.py").is_file()
)))

from skill_check import CheckResult, SkillValidator, read_text, run_cli  # noqa: E402

VALIDATOR = SkillValidator(Path(__file__).resolve().parents[1])
REFERENCE_FILE = VALIDATOR.skill_dir / "references" / "example-findings.md"

REQUIRED_FRONTMATTER = [
    "name",
    "description",
    "when_to_use",
    "argument-hint",
    "allowed-tools",
    "disable-model-invocation",
]

REQUIRED_SECTIONS = [
    r"^##\s+Modes",
    r"^##\s+Standing Rules",
    r"^##\s+Procedure",
    r"^##\s+Output Contract",
    r"^##\s+What's Automated vs What Needs User Taste",
    r"^##\s+Forbidden",
    r"^##\s+Pitfalls",
    r"^##\s+Validation",
]

FINDINGS_MARKERS = [
    "Findings",
    "Evidence:",
    "Impact:",
    "Suggested fix:",
    "Test/verification gap:",
    "Residual Risk",
    "Handoff",
]

BOUNDARY_MARKERS = [
    "Read-only",
    "Do not create files",
    "Edit, write, stage, commit, push",
    "browser QA",
    "ship",
    "persona-review",
    "verify-implementation",
]


def check_reference() -> CheckResult:
    reference_text = read_text(REFERENCE_FILE)
    linked = "references/example-findings.md" in VALIDATOR.text
    checklist = reference_text.count("- [ ]") >= 5
    examples = "BEFORE" in reference_text and "AFTER" in reference_text
    return CheckResult(
        "reference file linked with checklist and examples",
        linked and checklist and examples,
        f"linked={linked}, checklist={checklist}, examples={examples}",
    )


CHECKS = [
    lambda: VALIDATOR.check_frontmatter(REQUIRED_FRONTMATTER, model_invocation_disabled=True),
    lambda: VALIDATOR.check_read_only_tools(name="allowed tools are read-only review oriented"),
    lambda: VALIDATOR.check_required_sections(REQUIRED_SECTIONS),
    lambda: VALIDATOR.check_markers(FINDINGS_MARKERS, name="findings-first output contract documented"),
    lambda: VALIDATOR.check_markers(BOUNDARY_MARKERS, name="neighbor-skill boundaries documented"),
    check_reference,
]


if __name__ == "__main__":
    sys.exit(run_cli(VALIDATOR.name, CHECKS, description="Validate /review skill structure"))
