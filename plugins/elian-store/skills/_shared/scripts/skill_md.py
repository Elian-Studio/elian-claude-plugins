#!/usr/bin/env python3
"""`SKILL.md` parsing shared by the runtime scripts that skills ship to users.

`manage-skills/scripts/check-skill-frontmatter.py` and
`verify-implementation/scripts/check-skill-discovery.py` both inspect third-party
`SKILL.md` files on the user's machine, and each carried its own copy of the same
frontmatter reader and section detector.

This module lives under `skills/_shared/` because that directory is copied into every
emitted plugin (`tools/generate.py`), so the import keeps resolving after the bundle is
split — unlike `tools/`, which is repository tooling and is never shipped.

Consumers import it with:

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared" / "scripts"))

Stdlib only, matching the zero-install contract of the scripts that use it.
"""
from __future__ import annotations

import re

FRONTMATTER_KEY_RE = re.compile(r"^([a-zA-Z_-][a-zA-Z0-9_-]*)\s*:\s*(.*)$")


def split_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """Split `SKILL.md` into (frontmatter, body).

    Returns `(None, text)` when the file has no opening `---` or never closes it —
    callers treat a missing block and an unterminated one as the same failure.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), -1)
    if end == -1:
        return None, text

    frontmatter: dict[str, str] = {}
    for line in lines[1:end]:
        match = FRONTMATTER_KEY_RE.match(line)
        if match:
            key, value = match.group(1), match.group(2).strip()
            frontmatter[key] = value.strip('"').strip("'")
    return frontmatter, "\n".join(lines[end + 1 :])


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Frontmatter only, or `None` when the block is absent or unterminated."""
    return split_frontmatter(text)[0]


def has_section(text: str, name: str) -> bool:
    """True when a heading of any level names `name`, case-insensitively."""
    return bool(re.search(rf"^#{{1,4}}\s+.*\b{re.escape(name)}\b", text, re.MULTILINE | re.IGNORECASE))
