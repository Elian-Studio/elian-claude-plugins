#!/usr/bin/env python3
"""Self-verification for the /respond-to-review skill.

Stdlib only. Supports --json for programmatic consumption.
This skill is always-on (disable-model-invocation: false) and read-ish: it triages
review feedback and hands the edits to /fix or /improve, so it must not edit code itself.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_FILE = SKILL_DIR / "SKILL.md"

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

# Consumer-side triage only — execution is delegated to /fix or /improve.
FORBIDDEN_TOOL_PATTERNS = [
    r"\ballowed-tools:.*\bEdit\b",
    r"\ballowed-tools:.*\bWrite\b",
    r"\ballowed-tools:.*Bash\(git commit",
    r"\ballowed-tools:.*Bash\(git push",
]

# Must hand execution off, not do it here.
HANDOFF_MARKERS = ["/fix", "/improve"]


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def check_frontmatter() -> CheckResult:
    text = read_text(SKILL_FILE)
    fm = frontmatter(text)
    missing = [key for key in REQUIRED_FRONTMATTER if key not in fm]
    name_ok = fm.get("name") == SKILL_DIR.name
    always_on = fm.get("disable-model-invocation") == "false"
    return CheckResult(
        "frontmatter required fields + always-on",
        not missing and name_ok and always_on,
        f"missing={missing}, name_ok={name_ok}, disable_model_invocation={fm.get('disable-model-invocation')}",
    )


def check_allowed_tools_read_only() -> CheckResult:
    text = read_text(SKILL_FILE)
    hits = [pattern for pattern in FORBIDDEN_TOOL_PATTERNS if re.search(pattern, text)]
    allowed = frontmatter(text).get("allowed-tools", "")
    has_read_tools = all(token in allowed for token in ["Read", "Glob", "Grep"])
    return CheckResult(
        "allowed tools are read-only (triage only, execution delegated)",
        not hits and has_read_tools,
        "ok" if not hits and has_read_tools else f"hits={hits}, allowed={allowed}",
    )


def check_required_sections() -> CheckResult:
    text = read_text(SKILL_FILE)
    missing = [pattern for pattern in REQUIRED_SECTIONS if not re.search(pattern, text, re.MULTILINE)]
    return CheckResult(
        f"required sections present ({len(REQUIRED_SECTIONS)})",
        not missing,
        "ok" if not missing else f"missing={missing}",
    )


def check_content_markers() -> CheckResult:
    text = read_text(SKILL_FILE)
    missing = [marker for marker in CONTENT_MARKERS if marker not in text]
    return CheckResult(
        "core doctrine markers present (no-performative, verify, YAGNI)",
        not missing,
        "ok" if not missing else f"missing={missing}",
    )


def check_handoff() -> CheckResult:
    text = read_text(SKILL_FILE)
    missing = [marker for marker in HANDOFF_MARKERS if marker not in text]
    return CheckResult(
        "delegates execution to /fix and /improve",
        not missing,
        "ok" if not missing else f"missing={missing}",
    )


def check_line_cap() -> CheckResult:
    text = read_text(SKILL_FILE)
    lines = text.count("\n") + 1
    return CheckResult(
        "SKILL.md under 500 lines",
        lines < 500,
        f"lines={lines}",
    )


def run_checks() -> list[CheckResult]:
    return [
        check_frontmatter(),
        check_allowed_tools_read_only(),
        check_required_sections(),
        check_content_markers(),
        check_handoff(),
        check_line_cap(),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate /respond-to-review skill structure")
    parser.add_argument("--json", action="store_true", help="emit JSON result")
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    args = parser.parse_args()

    checks = run_checks()
    passed = all(check.passed for check in checks)
    payload = {
        "skill": SKILL_DIR.name,
        "passed": passed,
        "checks": [check.to_dict() for check in checks],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.quiet:
        for check in checks:
            if not check.passed:
                print(f"FAIL {check.name}: {check.detail}")
    else:
        print(f"{'PASS' if passed else 'FAIL'} /respond-to-review skill validation")
        for check in checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"- {status} {check.name}: {check.detail}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
