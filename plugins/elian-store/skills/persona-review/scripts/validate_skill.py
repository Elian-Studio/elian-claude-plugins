#!/usr/bin/env python3
"""Self-verification for the /persona-review skill.

Stdlib only. Supports --json for programmatic consumption.

Usage:
    python3 validate_skill.py
    python3 validate_skill.py --json
    python3 validate_skill.py --quiet

Exits 0 on PASS, 1 on FAIL.

What it checks:
  - frontmatter required fields + name == dir name
  - disable-model-invocation: true (read-only/user-agency guard)
  - required sections present
  - persona-first/free-form review contract is documented
  - Agent-based dispatch contract is documented
  - required persona reviewer agent files exist and are read-only
  - the old locked scorecard/5-block contract is not reintroduced
  - references/ has personas/*.md + example-review.md and SKILL.md links them
  - persona override and interview mode are documented
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
PLUGIN_DIR = SKILL_DIR.parents[1]
AGENTS_DIR = PLUGIN_DIR / "agents"

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
    "페르소나별 자유 형식",
    "No scorecard",
    "전부 행으로 펼치거나 점수화하지 않는다",
    "점수표·등급표·전수 체크리스트 출력",
]

FORBIDDEN_LOCKED_CONTRACT_PATTERNS = [
    r"^##\s+OUTPUT FORMAT",
    r"잠긴 OUTPUT FORMAT",
    r"locked 5-block",
    r"LOCKED OUTPUT FORMAT",
    r"^##\s+페르소나 압박 질문",
    r"\|\s*#\s*\|\s*질문\s*\|\s*점수\s*\|",
]

PERSONA_FORBIDDEN_PATTERNS = [
    r"점수 표기",
    r"리뷰 시 모두 평가",
    r"\|\s*#\s*\|\s*질문\s*\|\s*점수\s*\|",
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
    "persona-custom-reviewer.md",
]
REQUIRED_AGENT_NAMES = [p[:-3] for p in REQUIRED_AGENT_FILES]


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
            fm[k.strip()] = v.strip().strip('"')
    return fm


def _persona_files() -> list[Path]:
    personas = SKILL_DIR / "references" / PERSONAS_DIR_NAME
    if not personas.is_dir():
        return []
    return sorted(p for p in personas.iterdir() if p.suffix == ".md")


def _agent_files() -> list[Path]:
    if not AGENTS_DIR.is_dir():
        return []
    return sorted(AGENTS_DIR / name for name in REQUIRED_AGENT_FILES)


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
        detail="found" if has else "missing read-only/user-agency guard",
    )


def check_agent_tool_allowed() -> CheckResult:
    fm = _frontmatter(_read(SKILL_FILE))
    allowed = fm.get("allowed-tools", "")
    has_agent = "Agent" in allowed
    return CheckResult(
        name="frontmatter: Agent tool allowed for subagent dispatch",
        passed=has_agent,
        detail="Agent found" if has_agent else f"allowed-tools={allowed}",
    )


def check_required_sections() -> CheckResult:
    text = _read(SKILL_FILE)
    missing = [p for p in REQUIRED_SECTIONS if not re.search(p, text, re.MULTILINE)]
    return CheckResult(
        name=f"required sections present ({len(REQUIRED_SECTIONS)} total)",
        passed=not missing,
        detail=f"missing={missing}",
    )


def check_free_form_contract() -> CheckResult:
    text = _read(SKILL_FILE)
    missing = [marker for marker in FREE_FORM_MARKERS if marker not in text]
    return CheckResult(
        name="persona-first free-form contract documented",
        passed=not missing,
        detail="all markers found" if not missing else f"missing={missing}",
    )


def check_subagent_dispatch_contract() -> CheckResult:
    text = _read(SKILL_FILE)
    missing = [name for name in REQUIRED_AGENT_NAMES if name not in text]
    required_phrases = [
        "Subagent Execution Contract",
        "Agent prompt payload",
        "single persona",
        "multiple personas",
        "persona-custom-reviewer",
    ]
    missing.extend([phrase for phrase in required_phrases if phrase not in text])
    return CheckResult(
        name="subagent dispatch contract documented",
        passed=not missing,
        detail="all dispatch markers found" if not missing else f"missing={missing}",
    )


def check_no_locked_contract() -> CheckResult:
    text = _read(SKILL_FILE)
    hits = [p for p in FORBIDDEN_LOCKED_CONTRACT_PATTERNS if re.search(p, text, re.MULTILINE | re.IGNORECASE)]
    return CheckResult(
        name="old locked scorecard/5-block contract not reintroduced",
        passed=not hits,
        detail="no locked contract patterns" if not hits else f"hits={hits}",
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
    text = _read(SKILL_FILE)
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
        text = _read(path)
        fm = _frontmatter(text)
        tools = fm.get("tools", "")
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
        text = _read(path)
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


def check_persona_override_and_interview() -> CheckResult:
    text = _read(SKILL_FILE)
    missing = [s for s in ["--persona", "--depth", "interview"] if s not in text]
    return CheckResult(
        name="persona override and interview mode documented",
        passed=not missing,
        detail="all documented" if not missing else f"missing={missing}",
    )


CHECKS = [
    check_frontmatter,
    check_disable_model_invocation,
    check_agent_tool_allowed,
    check_required_sections,
    check_free_form_contract,
    check_subagent_dispatch_contract,
    check_no_locked_contract,
    check_references_dir,
    check_references_linked,
    check_agent_files_exist,
    check_agent_files_read_only,
    check_persona_files_not_scorecards,
    check_scripts_dir,
    check_persona_override_and_interview,
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
