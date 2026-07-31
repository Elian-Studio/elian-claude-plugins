#!/usr/bin/env python3
"""Structural self-validation for a workflow skill directory.

Stdlib only (no external dependencies). Chainable: supports --json output for
programmatic consumption.

This is the single source for what used to be four byte-identical copies under
brainstorm/, fix/, implement/, and improve/ scripts/. The copies self-identified
by their own location; this version takes the skill directory as an argument
instead, so changing a rule is one edit rather than four.

It lives in `_shared/` rather than the repository's `tools/` because the skills that
document it ship to installed users, and `tools/` is not part of the plugin package —
the documented command has to resolve inside a Claude or Codex install, not only in a
repository checkout.

Usage:
    python3 <plugin>/skills/_shared/validate_skill.py <skill-dir> [<skill-dir> ...]
    python3 <plugin>/skills/_shared/validate_skill.py <skill-dir> --json    # JSON output
    python3 <plugin>/skills/_shared/validate_skill.py <skill-dir> --quiet   # exit code only

Exits 0 when every skill passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


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

# The retired `scripts/ directory exists` check is deliberately absent: it only ever
# passed because the checker itself lived in that directory, so it asserted nothing.


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


def check_frontmatter(skill_dir: Path) -> CheckResult:
    name = skill_dir.name
    fm = _frontmatter(_read(skill_dir / "SKILL.md"))
    missing = [k for k in REQUIRED_FRONTMATTER if k not in fm]
    name_ok = fm.get("name") == name
    return CheckResult(
        name=f"frontmatter: required fields + name=={name}",
        passed=not missing and name_ok,
        detail=f"missing={missing}, name_match={name_ok}",
    )


def check_disable_model_invocation(skill_dir: Path) -> CheckResult:
    fm = _frontmatter(_read(skill_dir / "SKILL.md"))
    has = fm.get("disable-model-invocation") == "true"
    return CheckResult(
        name="frontmatter: disable-model-invocation: true",
        passed=has,
        detail="found" if has else "missing",
    )


def check_required_sections(skill_dir: Path) -> CheckResult:
    text = _read(skill_dir / "SKILL.md")
    missing = [pat for pat in REQUIRED_SECTIONS if not re.search(pat, text, re.MULTILINE)]
    return CheckResult(
        name=f"required sections present ({len(REQUIRED_SECTIONS)} total)",
        passed=not missing,
        detail=f"missing={missing}",
    )


def check_references_dir(skill_dir: Path) -> CheckResult:
    refs = skill_dir / "references"
    if not refs.is_dir():
        return CheckResult(name="references/ directory exists with ≥1 file", passed=False, detail="missing")
    files = [p for p in refs.iterdir() if p.suffix in {".md", ".html", ".txt"}]
    return CheckResult(
        name="references/ directory exists with ≥1 file",
        passed=len(files) >= 1,
        detail=f"{len(files)} file(s)",
    )


def check_references_linked(skill_dir: Path) -> CheckResult:
    text = _read(skill_dir / "SKILL.md")
    has = re.search(r"\[[^\]]+\]\(\s*references/", text) is not None
    return CheckResult(
        name="SKILL.md links into references/",
        passed=has,
        detail="linked" if has else "missing",
    )


CHECKS = [
    check_frontmatter,
    check_disable_model_invocation,
    check_required_sections,
    check_references_dir,
    check_references_linked,
]


def run_all(skill_dir: Path) -> tuple[list[CheckResult], bool]:
    results = [fn(skill_dir) for fn in CHECKS]
    return results, all(r.passed for r in results)


def format_human(skill_name: str, results: list[CheckResult], overall: bool) -> str:
    lines = ["=" * 70, f"  /{skill_name} self-validation", "=" * 70]
    for r in results:
        lines.append(f"  [{'PASS' if r.passed else 'FAIL'}] {r.name}")
        if r.detail:
            lines.append(f"         {r.detail}")
    lines.append("-" * 70)
    lines.append(f"  Overall: {'PASS' if overall else 'FAIL'}")
    lines.append("=" * 70)
    return "\n".join(lines)


def format_json(skill_name: str, results: list[CheckResult], overall: bool) -> dict:
    return {
        "skill": skill_name,
        "overall": "pass" if overall else "fail",
        "checks": [r.to_dict() for r in results],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
        },
    }


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
        skill_dir = raw.resolve()
        if not (skill_dir / "SKILL.md").is_file():
            print(f"error: {raw}/SKILL.md not found", file=sys.stderr)
            all_ok = False
            continue
        results, overall = run_all(skill_dir)
        all_ok = all_ok and overall
        if args.quiet:
            continue
        if args.json:
            reports.append(format_json(skill_dir.name, results, overall))
        else:
            print(format_human(skill_dir.name, results, overall))

    if args.json and not args.quiet:
        # Always a list, even for one skill. Returning a bare object for N==1 and a list
        # otherwise means `jq '.[].overall'` breaks on one input and `jq '.overall'` breaks
        # on several — and the shape flips silently when a directory is skipped.
        print(json.dumps(reports, ensure_ascii=False, indent=2))

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
