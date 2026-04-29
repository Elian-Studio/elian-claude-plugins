#!/usr/bin/env python3
"""Self-verification for the /generate-teammate skill.

Runs the .spec.md verification rules using stdlib only (no external
dependencies). Designed to be chainable: supports --json output for
programmatic consumption by other skills or CI pipelines.

Usage:
    python3 validate_skill.py             # human-readable report
    python3 validate_skill.py --json      # JSON output
    python3 validate_skill.py --quiet     # exit code only
    python3 validate_skill.py --help

Exits 0 on PASS, 1 on FAIL. The verify checks mirror .spec.md so the
spec is the canonical source — this script is the executable form.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = SKILL_DIR.parent.parent  # plugins/elian-store
AGENTS_DIR = PLUGIN_ROOT / "agents"


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""
    severity: str = "critical"  # critical | important | minor

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "detail": self.detail,
            "severity": self.severity,
        }


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _strip_inline_code(line: str) -> str:
    """Remove backtick-wrapped spans so prose references like `Task({...})` are
    not flagged as code occurrences."""
    return re.sub(r"`[^`]*`", "", line)


def _grep_files(
    pattern: str, paths: list[Path], code_blocks_only: bool = False
) -> list[tuple[Path, int, str]]:
    """Return [(path, line_no, line)] for matches across the given files.

    When `code_blocks_only=True`, only lines inside fenced code blocks
    (``` ... ```) are checked, and inline-code spans are stripped from prose
    lines too. This avoids flagging documentation that quotes the forbidden
    pattern in `inline code`.
    """
    rx = re.compile(pattern)
    hits: list[tuple[Path, int, str]] = []
    for p in paths:
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        in_fence = False
        for i, raw in enumerate(text.splitlines(), 1):
            if raw.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if code_blocks_only and not in_fence:
                continue
            line = raw if in_fence else _strip_inline_code(raw)
            if rx.search(line):
                hits.append((p, i, raw))
    return hits


def _all_skill_files() -> list[Path]:
    return [p for p in SKILL_DIR.rglob("*.md") if p.name != ".spec.md"]


# ---------- Critical checks (C-1..C-7) ----------


def check_c1_no_model_param() -> CheckResult:
    hits = _grep_files(r"Agent\(\s*\{[^}]*model:", _all_skill_files())
    return CheckResult(
        name="C-1: no `model` parameter on Agent({...}) calls",
        passed=not hits,
        detail=f"{len(hits)} hit(s)" + (f" (e.g., {hits[0][0].name}:{hits[0][1]})" if hits else ""),
        severity="critical",
    )


def check_c2_no_legacy_task_tool() -> CheckResult:
    files = [p for p in _all_skill_files() if p.name != ".spec.md"]
    hits = _grep_files(r"Task\(\s*\{", files)
    return CheckResult(
        name="C-2: no legacy `Task({` (renamed to Agent in v2.1.63)",
        passed=not hits,
        detail=f"{len(hits)} hit(s)" + (f" (e.g., {hits[0][0].name}:{hits[0][1]})" if hits else ""),
        severity="critical",
    )


def check_c3_no_addblockedby_in_taskcreate() -> CheckResult:
    hits = _grep_files(r"TaskCreate\(\s*\{[^}]*addBlockedBy", _all_skill_files())
    return CheckResult(
        name="C-3: TaskCreate has no addBlockedBy (use TaskUpdate instead)",
        passed=not hits,
        detail=f"{len(hits)} hit(s)" + (f" (e.g., {hits[0][0].name}:{hits[0][1]})" if hits else ""),
        severity="critical",
    )


def check_c4_disable_model_invocation() -> CheckResult:
    body = _read(SKILL_DIR / "SKILL.md")
    has = "disable-model-invocation: true" in body
    return CheckResult(
        name="C-4: SKILL.md frontmatter has `disable-model-invocation: true`",
        passed=has,
        detail="found" if has else "missing",
        severity="critical",
    )


def check_c5_custom_agent_prereq_documented() -> CheckResult:
    body = _read(SKILL_DIR / "SKILL.md")
    has_path_note = "agents/" in body and "definition" in body.lower()
    has_count = "14" in body
    return CheckResult(
        name="C-5: custom agent prerequisites documented",
        passed=has_path_note and has_count,
        detail=f"path note={has_path_note}, 14-count mention={has_count}",
        severity="critical",
    )


def check_c6_experimental_flag() -> CheckResult:
    body = _read(SKILL_DIR / "SKILL.md")
    has = "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" in body
    return CheckResult(
        name="C-6: SKILL.md mentions CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS",
        passed=has,
        detail="found" if has else "missing",
        severity="critical",
    )


def check_c7_agents_self_contained() -> CheckResult:
    """No agent definition uses `skills:` frontmatter (external dep)."""
    if not AGENTS_DIR.is_dir():
        return CheckResult(
            name="C-7: plugin agents are self-contained (no `skills:` frontmatter)",
            passed=False,
            detail="agents/ directory missing",
            severity="critical",
        )
    bad: list[str] = []
    for p in sorted(AGENTS_DIR.glob("*.md")):
        # Inspect frontmatter only (between first two `---`)
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            continue
        fm = m.group(1)
        if re.search(r"^skills:", fm, re.MULTILINE):
            bad.append(p.name)
    return CheckResult(
        name="C-7: plugin agents are self-contained (no `skills:` frontmatter)",
        passed=not bad,
        detail=("clean" if not bad else f"agents with skills: {bad}"),
        severity="critical",
    )


# ---------- Important checks (I-6..I-9) ----------


EXPECTED_AGENTS = [
    "frontend-architect",
    "backend-architect",
    "system-architect",
    "security-engineer",
    "performance-engineer",
    "quality-engineer",
    "devops-architect",
    "requirements-analyst",
    "ui-ux-designer",
    "technical-writer",
    "ux-researcher",
    "marketing-strategist",
    "business-analyst",
    "devil-advocate",
]


def check_i6_fourteen_agents() -> CheckResult:
    if not AGENTS_DIR.is_dir():
        return CheckResult(
            name="I-6: 14 plugin-bundled agents present",
            passed=False,
            detail="agents/ directory missing",
            severity="important",
        )
    found = sorted(p.stem for p in AGENTS_DIR.glob("*.md"))
    missing = [a for a in EXPECTED_AGENTS if a not in found]
    extras = [a for a in found if a not in EXPECTED_AGENTS]
    passed = not missing and len(found) == 14
    return CheckResult(
        name="I-6: 14 plugin-bundled agents present",
        passed=passed,
        detail=f"found={len(found)}, missing={missing}, extras={extras}",
        severity="important",
    )


def check_i7_framework_agnostic() -> CheckResult:
    """frontend-architect / backend-architect cover multiple frameworks."""
    fe = _read(AGENTS_DIR / "frontend-architect.md").lower()
    be = _read(AGENTS_DIR / "backend-architect.md").lower()
    fe_terms = ["react", "vue", "angular", "svelte"]
    be_terms = ["spring", "express", "django", "fastapi", "rails", "go"]
    fe_missing = [t for t in fe_terms if t not in fe]
    be_missing = [t for t in be_terms if t not in be]
    fe_has_detect = "stack detection" in fe or "manifest" in fe
    be_has_detect = "stack detection" in be or "manifest" in be
    passed = not fe_missing and not be_missing and fe_has_detect and be_has_detect
    return CheckResult(
        name="I-7: frontend / backend agents are framework-agnostic",
        passed=passed,
        detail=f"FE missing={fe_missing}, BE missing={be_missing}, detection FE={fe_has_detect} BE={be_has_detect}",
        severity="important",
    )


def check_i8_examples_present() -> CheckResult:
    refs = SKILL_DIR / "references"
    if not refs.is_dir():
        return CheckResult(
            name="I-8: references/ contains end-to-end traces",
            passed=False,
            detail="references/ directory missing",
            severity="important",
        )
    n = len([p for p in refs.glob("*.md") if p.name != "README.md"])
    return CheckResult(
        name="I-8: references/ contains ≥ 4 example traces",
        passed=n >= 4,
        detail=f"found {n} examples (excluding README)",
        severity="important",
    )


def check_i9_team_patterns_complete() -> CheckResult:
    body = _read(SKILL_DIR / "team-patterns.md")
    has_doc = re.search(r"\bDocumentation Team\b", body) is not None
    has_strat = re.search(r"\bStrategy Team\b", body) is not None
    has_design_variants = "Variant A" in body and "Variant B" in body
    passed = has_doc and has_strat and has_design_variants
    return CheckResult(
        name="I-9: team-patterns.md has Documentation + Strategy Teams + Design variants",
        passed=passed,
        detail=f"Documentation Team={has_doc}, Strategy Team={has_strat}, Design variants={has_design_variants}",
        severity="important",
    )


CHECKS = [
    check_c1_no_model_param,
    check_c2_no_legacy_task_tool,
    check_c3_no_addblockedby_in_taskcreate,
    check_c4_disable_model_invocation,
    check_c5_custom_agent_prereq_documented,
    check_c6_experimental_flag,
    check_c7_agents_self_contained,
    check_i6_fourteen_agents,
    check_i7_framework_agnostic,
    check_i8_examples_present,
    check_i9_team_patterns_complete,
]


def run_all() -> tuple[list[CheckResult], bool]:
    results = [fn() for fn in CHECKS]
    # Critical checks must all pass; important checks are warnings only at critical level.
    critical_failed = any(not r.passed for r in results if r.severity == "critical")
    important_failed = any(not r.passed for r in results if r.severity == "important")
    overall = not critical_failed and not important_failed
    return results, overall


def format_human(results: list[CheckResult], overall: bool) -> str:
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("  /generate-teammate self-validation")
    lines.append("=" * 70)
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        sev = r.severity[:4].upper()
        lines.append(f"  [{mark}] [{sev}] {r.name}")
        if r.detail:
            lines.append(f"         {r.detail}")
    lines.append("-" * 70)
    lines.append(f"  Overall: {'PASS' if overall else 'FAIL'}")
    lines.append("=" * 70)
    return "\n".join(lines)


def format_json(results: list[CheckResult], overall: bool) -> str:
    payload = {
        "skill": "generate-teammate",
        "overall": "pass" if overall else "fail",
        "checks": [r.to_dict() for r in results],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "critical_failures": sum(
                1 for r in results if not r.passed and r.severity == "critical"
            ),
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the /generate-teammate skill against .spec.md rules.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of human report")
    parser.add_argument(
        "--quiet", action="store_true", help="suppress output; exit code only"
    )
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
