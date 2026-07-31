#!/usr/bin/env python3
"""Self-verification for the /persona-review skill.

Stdlib only. Supports --json for programmatic consumption.

Usage:
    python3 validate_skill.py
    python3 validate_skill.py --json
    python3 validate_skill.py --quiet

Exits 0 on PASS, 1 on FAIL.

Generic structure checks (frontmatter, sections, markers, report shape) come from
`tools/skill_check.py`. What stays here is the persona-specific contract:

  - persona-first/free-form review contract is documented
  - Agent-based dispatch contract is documented
  - required persona reviewer agent files exist and are read-only
  - the old locked scorecard/5-block contract is not reintroduced
  - references/ has personas/*.md + example-review.md and SKILL.md links them
  - persona override and interview mode are documented
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Walk up to the repository checkout this skill lives in; a fixed `parents[N]` would
# break the moment a skill moves between plugins.
sys.path.insert(0, str(next(
    p / "tools" for p in Path(__file__).resolve().parents if (p / "tools" / "skill_check.py").is_file()
)))

from skill_check import (  # noqa: E402
    CheckResult,
    SkillValidator,
    parse_frontmatter,
    read_text,
    run_cli,
)

VALIDATOR = SkillValidator(Path(__file__).resolve().parents[1])
SKILL_DIR = VALIDATOR.skill_dir
AGENTS_DIR = SKILL_DIR.parents[1] / "agents"

REQUIRED_FRONTMATTER = ["name", "description", "when_to_use", "argument-hint", "allowed-tools"]

REQUIRED_SECTIONS = [
    r"^##\s+Modes",
    r"^##\s+Persona library",
    r"^##\s+Common Review Contract",
    r"^##\s+Subagent Execution Contract",
    r"^##\s+Workflow",
    r"^##\s+Pitfalls",
    r"^##\s+Forbidden",
    r"^##\s+Validation",
]

FREE_FORM_MARKERS = [
    "Persona-native free-form review",
    "No scorecard",
    "Do not expand all `Pressure Questions` into rows, grades, or scores",
    "Forcing a common five-block output",
]

FORBIDDEN_LOCKED_CONTRACT_PATTERNS = [
    r"^##\s+OUTPUT FORMAT",
    r"locked 5-block",
    r"LOCKED OUTPUT FORMAT",
    r"^##\s+Persona Pressure Questions",
    r"\|\s*#\s*\|\s*Question\s*\|\s*Score\s*\|",
]

PERSONA_FORBIDDEN_PATTERNS = [
    r"score notation",
    r"evaluate every question",
    r"\|\s*#\s*\|\s*Question\s*\|\s*Score\s*\|",
    r"✓",
    r"△",
    r"✗",
]

PERSONAS_DIR_NAME = "personas"
REQUIRED_REFERENCE_FILES = ["example-review.md"]
REQUIRED_AGENT_FILES = [
    "persona-daniel-reviewer.md",
    "persona-evans-reviewer.md",
    "persona-dean-reviewer.md",
    "persona-martin-reviewer.md",
    "persona-beck-reviewer.md",
    "persona-fowler-reviewer.md",
    "persona-abramov-reviewer.md",
    "persona-evanyou-reviewer.md",
    "persona-norman-reviewer.md",
    "persona-rams-reviewer.md",
    "persona-dunford-reviewer.md",
    "persona-christensen-reviewer.md",
    "persona-watson-reviewer.md",
    "persona-fielding-reviewer.md",
    "persona-custom-reviewer.md",
]
REQUIRED_AGENT_NAMES = [name[:-3] for name in REQUIRED_AGENT_FILES]

DISPATCH_PHRASES = [
    "Subagent Execution Contract",
    "Agent prompt payload",
    "single persona",
    "multiple personas",
    "persona-custom-reviewer",
]


def _persona_files() -> list[Path]:
    personas = SKILL_DIR / "references" / PERSONAS_DIR_NAME
    if not personas.is_dir():
        return []
    return sorted(p for p in personas.iterdir() if p.suffix == ".md")


def _agent_files() -> list[Path]:
    if not AGENTS_DIR.is_dir():
        return []
    return sorted(AGENTS_DIR / name for name in REQUIRED_AGENT_FILES)


def check_agent_tool_allowed() -> CheckResult:
    allowed = VALIDATOR.frontmatter.get("allowed-tools", "")
    has_agent = "Agent" in allowed
    return CheckResult(
        name="frontmatter: Agent tool allowed for subagent dispatch",
        passed=has_agent,
        detail="Agent found" if has_agent else f"allowed-tools={allowed}",
    )


def check_subagent_dispatch_contract() -> CheckResult:
    return VALIDATOR.check_markers(
        [*REQUIRED_AGENT_NAMES, *DISPATCH_PHRASES],
        name="subagent dispatch contract documented",
    )


def check_references_dir() -> CheckResult:
    refs = SKILL_DIR / "references"
    if not refs.is_dir():
        return CheckResult(name="references/ has personas/ + example files", passed=False, detail="missing dir")
    present = {p.name for p in refs.iterdir() if p.is_file()}
    personas = _persona_files()
    missing_fixed = [f for f in REQUIRED_REFERENCE_FILES if f not in present]
    passed = bool(personas) and not missing_fixed
    detail = (
        f"persona(s): {[p.name for p in personas]}; fixed: {sorted(present)}"
        if passed
        else f"personas={len(personas)}, missing_fixed={missing_fixed}"
    )
    return CheckResult(
        name="references/ has personas/ + example files",
        passed=passed,
        detail=detail,
    )


def check_references_linked() -> CheckResult:
    text = VALIDATOR.text
    fixed_missing = [f for f in REQUIRED_REFERENCE_FILES if f"references/{f}" not in text]
    linked_personas = [
        p.name for p in _persona_files()
        if f"references/{PERSONAS_DIR_NAME}/{p.name}" in text
    ]
    passed = not fixed_missing and bool(linked_personas)
    detail = (
        f"linked_personas={linked_personas}"
        if passed
        else f"missing_fixed_links={fixed_missing}, linked_personas={linked_personas}"
    )
    return CheckResult(
        name="SKILL.md links example + persona files",
        passed=passed,
        detail=detail,
    )


def check_agent_files_exist() -> CheckResult:
    missing = [path.name for path in _agent_files() if not path.is_file()]
    return CheckResult(
        name="persona reviewer agent files exist",
        passed=not missing and AGENTS_DIR.is_dir(),
        detail=(
            f"agents={REQUIRED_AGENT_FILES}"
            if not missing and AGENTS_DIR.is_dir()
            else f"agents_dir={AGENTS_DIR.is_dir()}, missing={missing}"
        ),
    )


def check_agent_files_read_only() -> CheckResult:
    hits: list[str] = []
    for path in _agent_files():
        text = read_text(path)
        tools = parse_frontmatter(text).get("tools", "")
        if "Write" in tools or "Edit" in tools:
            hits.append(f"{path.name}:tools={tools}")
        if "Do not implement, edit, create files" not in text:
            hits.append(f"{path.name}:missing read-only instruction")
        if "Do not output a scorecard" not in text:
            hits.append(f"{path.name}:missing no-scorecard instruction")
    return CheckResult(
        name="persona reviewer agents are read-only and no-scorecard",
        passed=not hits,
        detail="all read-only" if not hits else f"hits={hits}",
    )


def check_persona_files_not_scorecards() -> CheckResult:
    hits: list[str] = []
    for path in _persona_files():
        text = read_text(path)
        for pattern in PERSONA_FORBIDDEN_PATTERNS:
            if re.search(pattern, text):
                hits.append(f"{path.name}:{pattern}")
    return CheckResult(
        name="persona files describe lenses, not scorecards",
        passed=not hits,
        detail="no scorecard patterns" if not hits else f"hits={hits}",
    )


def check_scripts_dir() -> CheckResult:
    scripts = SKILL_DIR / "scripts"
    return CheckResult(
        name="scripts/ directory exists",
        passed=scripts.is_dir(),
        detail="present" if scripts.is_dir() else "missing",
    )


CHECKS = [
    lambda: VALIDATOR.check_frontmatter(REQUIRED_FRONTMATTER),
    VALIDATOR.check_model_invocation_disabled,
    check_agent_tool_allowed,
    lambda: VALIDATOR.check_required_sections(REQUIRED_SECTIONS),
    lambda: VALIDATOR.check_markers(
        FREE_FORM_MARKERS, name="persona-first free-form contract documented"
    ),
    check_subagent_dispatch_contract,
    lambda: VALIDATOR.check_forbidden_patterns(
        FORBIDDEN_LOCKED_CONTRACT_PATTERNS,
        name="old locked scorecard/5-block contract not reintroduced",
        flags=re.MULTILINE | re.IGNORECASE,
    ),
    check_references_dir,
    check_references_linked,
    check_agent_files_exist,
    check_agent_files_read_only,
    check_persona_files_not_scorecards,
    check_scripts_dir,
    lambda: VALIDATOR.check_markers(
        ["--persona", "--depth", "interview"],
        name="persona override and interview mode documented",
    ),
]


if __name__ == "__main__":
    sys.exit(
        run_cli(
            VALIDATOR.name,
            CHECKS,
            description=f"Validate the /{VALIDATOR.name} skill structure.",
            epilog=__doc__,
        )
    )
