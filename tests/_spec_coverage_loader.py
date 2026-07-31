"""Shared helper for loading the spec-coverage scripts by path.

The spec-coverage scripts live under a skill package (not an importable
package), so — exactly like ``test_repository_validation.py`` does for the
repository validator — the tests load them from their file path with
``importlib``. ``sys.modules`` is populated so a script that imports a sibling
by module name (``apply.py`` does ``from build_status import ...``) resolves it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_COVERAGE = REPO_ROOT / "plugins" / "elian-store" / "skills" / "spec-coverage" / "scripts"


def load(module_name: str, path: Path):
    """Load ``path`` as ``module_name`` and register it in ``sys.modules``."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    # apply.py resolves its sibling build_status by name, so its directory must
    # be importable while the module body executes.
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        try:
            sys.path.remove(str(path.parent))
        except ValueError:
            pass
    return module
