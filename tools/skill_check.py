#!/usr/bin/env python3
"""Shared scaffolding for skill self-validators.

Stdlib only. Every skill validator in this repository — the generic
`tools/validate_skill.py` and the bespoke `scripts/validate_skill.py` files owned by
`review`, `persona-review`, `respond-to-review`, and `verify-before-claiming` — used to
carry its own copy of the same four pieces: a `CheckResult` dataclass, a `read_text`
wrapper, a regex frontmatter parser, and an argparse `main` printing either a human
report or JSON. The copies had already drifted into two report shapes and two frontmatter
parsers of differing strictness.

This module owns those pieces once. A validator now declares only the checks that are
actually specific to its skill and hands the list to `run_cli`.

`parse_frontmatter` is the parser from `scripts/validate_repository.py` (multi-line and
list values included), so validators and the repository-wide checker agree on what a
frontmatter field contains.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

FRONTMATTER_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(?:\s*(.*))?$")

#: Tool grants that let a read-only skill mutate the working tree.
WRITE_TOOL_PATTERNS = [
    r"\ballowed-tools:.*\bEdit\b",
    r"\ballowed-tools:.*\bWrite\b",
    r"\ballowed-tools:.*Bash\(git commit",
    r"\ballowed-tools:.*Bash\(git push",
]

READ_TOOLS = ("Read", "Glob", "Grep")

#: `SKILL.md` length ceiling from CLAUDE.md.
LINE_CAP = 500

Check = Callable[[], "CheckResult"]


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


def read_text(path: Path) -> str:
    """File contents, or an empty string when the file is absent."""
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        return ""


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the top-level scalar/list subset used by repository frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}

    result: dict[str, str] = {}
    i = 1
    while i < end:
        match = FRONTMATTER_KEY_RE.match(lines[i])
        if not match:
            i += 1
            continue
        key, raw = match.group(1), (match.group(2) or "").strip()
        i += 1
        continuation: list[str] = []
        while i < end and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
            stripped = lines[i].strip()
            if stripped.startswith("- "):
                stripped = stripped[2:].strip()
            continuation.append(stripped)
            i += 1
        if raw in {">", ">-", "|", "|-"}:
            value = " ".join(part for part in continuation if part)
        elif continuation:
            value = " ".join([raw, *continuation]).strip()
        else:
            value = raw
        result[key] = _strip_quotes(value)
    return result


class SkillValidator:
    """Reusable checks over one skill directory.

    Each method returns a `CheckResult` rather than printing, so a validator composes
    shared checks and its own closures in one list.
    """

    def __init__(self, skill_dir: Path) -> None:
        self.skill_dir = skill_dir.resolve()
        self.name = self.skill_dir.name
        self.skill_file = self.skill_dir / "SKILL.md"

    @property
    def text(self) -> str:
        return read_text(self.skill_file)

    @property
    def frontmatter(self) -> dict[str, str]:
        return parse_frontmatter(self.text)

    def check_frontmatter(
        self,
        required: Sequence[str],
        *,
        model_invocation_disabled: bool | None = None,
    ) -> CheckResult:
        """Required fields present, `name` matches the directory, invocation gate as declared.

        `model_invocation_disabled` is tri-state: `None` skips the gate check, `True`
        demands `disable-model-invocation: true` (side-effecting or user-agency skills),
        `False` demands the literal `false` (always-on skills, where the field must still
        be spelled out rather than left to the default).
        """
        fm = self.frontmatter
        missing = [key for key in required if key not in fm]
        name_ok = fm.get("name") == self.name
        declared = fm.get("disable-model-invocation")
        gate_ok = model_invocation_disabled is None or declared == str(model_invocation_disabled).lower()
        return CheckResult(
            name=f"frontmatter: required fields + name=={self.name}",
            passed=not missing and name_ok and gate_ok,
            detail=f"missing={missing}, name_match={name_ok}, disable_model_invocation={declared}",
        )

    def check_model_invocation_disabled(self) -> CheckResult:
        declared = self.frontmatter.get("disable-model-invocation")
        return CheckResult(
            name="frontmatter: disable-model-invocation: true",
            passed=declared == "true",
            detail="found" if declared == "true" else f"disable_model_invocation={declared}",
        )

    def check_required_sections(self, patterns: Sequence[str]) -> CheckResult:
        text = self.text
        missing = [pattern for pattern in patterns if not re.search(pattern, text, re.MULTILINE)]
        return CheckResult(
            name=f"required sections present ({len(patterns)} total)",
            passed=not missing,
            detail=f"missing={missing}",
        )

    def check_markers(self, markers: Sequence[str], *, name: str) -> CheckResult:
        """Literal strings that must appear in `SKILL.md` (a documented contract, a doctrine line)."""
        text = self.text
        missing = [marker for marker in markers if marker not in text]
        return CheckResult(
            name=name,
            passed=not missing,
            detail="all markers found" if not missing else f"missing={missing}",
        )

    def check_forbidden_patterns(
        self,
        patterns: Sequence[str],
        *,
        name: str,
        flags: int = re.MULTILINE,
    ) -> CheckResult:
        """Regexes that must *not* match — a retired contract that keeps coming back."""
        text = self.text
        hits = [pattern for pattern in patterns if re.search(pattern, text, flags)]
        return CheckResult(
            name=name,
            passed=not hits,
            detail="no forbidden patterns" if not hits else f"hits={hits}",
        )

    def check_read_only_tools(
        self,
        *,
        name: str = "allowed tools are read-only",
        required_tools: Sequence[str] = READ_TOOLS,
    ) -> CheckResult:
        text = self.text
        hits = [pattern for pattern in WRITE_TOOL_PATTERNS if re.search(pattern, text)]
        allowed = self.frontmatter.get("allowed-tools", "")
        has_read_tools = all(token in allowed for token in required_tools)
        passed = not hits and has_read_tools
        return CheckResult(
            name=name,
            passed=passed,
            detail="ok" if passed else f"hits={hits}, allowed={allowed}",
        )

    def check_line_cap(self, limit: int = LINE_CAP) -> CheckResult:
        lines = self.text.count("\n") + 1
        return CheckResult(
            name=f"SKILL.md under {limit} lines",
            passed=lines < limit,
            detail=f"lines={lines}",
        )

    def check_references_dir(self, suffixes: Sequence[str] = (".md", ".html", ".txt")) -> CheckResult:
        refs = self.skill_dir / "references"
        if not refs.is_dir():
            return CheckResult(
                name="references/ directory exists with ≥1 file", passed=False, detail="missing"
            )
        files = [path for path in refs.iterdir() if path.suffix in set(suffixes)]
        return CheckResult(
            name="references/ directory exists with ≥1 file",
            passed=bool(files),
            detail=f"{len(files)} file(s)",
        )

    def check_references_linked(self) -> CheckResult:
        linked = re.search(r"\[[^\]]+\]\(\s*references/", self.text) is not None
        return CheckResult(
            name="SKILL.md links into references/",
            passed=linked,
            detail="linked" if linked else "missing",
        )


def run_checks(checks: Sequence[Check]) -> tuple[list[CheckResult], bool]:
    results = [check() for check in checks]
    return results, all(result.passed for result in results)


def format_human(skill_name: str, results: Sequence[CheckResult], overall: bool) -> str:
    lines = ["=" * 70, f"  /{skill_name} self-validation", "=" * 70]
    for result in results:
        lines.append(f"  [{'PASS' if result.passed else 'FAIL'}] {result.name}")
        if result.detail:
            lines.append(f"         {result.detail}")
    lines.append("-" * 70)
    lines.append(f"  Overall: {'PASS' if overall else 'FAIL'}")
    lines.append("=" * 70)
    return "\n".join(lines)


def json_payload(skill_name: str, results: Sequence[CheckResult], overall: bool) -> dict[str, object]:
    """Superset of the two shapes the copies used to emit.

    `overall` came from the `tools/validate_skill.py` lineage and `passed` from the
    skill-owned lineage; both are kept so neither consumer breaks on the merge.
    """
    return {
        "skill": skill_name,
        "overall": "pass" if overall else "fail",
        "passed": overall,
        "checks": [result.to_dict() for result in results],
        "summary": {
            "total": len(results),
            "passed": sum(1 for result in results if result.passed),
            "failed": sum(1 for result in results if not result.passed),
        },
    }


def build_parser(description: str, epilog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of human report")
    parser.add_argument("--quiet", action="store_true", help="suppress output; exit code only")
    return parser


def run_cli(skill_name: str, checks: Sequence[Check], *, description: str, epilog: str | None = None) -> int:
    """Standard entry point for a single-skill validator. Returns the process exit code."""
    args = build_parser(description, epilog).parse_args()
    results, overall = run_checks(checks)

    if args.quiet:
        pass
    elif args.json:
        print(json.dumps(json_payload(skill_name, results, overall), ensure_ascii=False, indent=2))
    else:
        print(format_human(skill_name, results, overall))

    return 0 if overall else 1
