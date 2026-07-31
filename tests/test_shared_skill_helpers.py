"""Regression tests for the two shared helper modules the validators were folded onto.

`tools/skill_check.py` backs the repository-side validators; `skills/_shared/scripts/skill_md.py`
backs the runtime scripts that ship inside the plugin. Both replaced copies that only ever ran
against passing fixtures, so the negative cases below are the part worth pinning.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


skill_check = _load("skill_check", ROOT / "tools" / "skill_check.py")
skill_md = _load(
    "skill_md", ROOT / "plugins" / "elian-store" / "skills" / "_shared" / "scripts" / "skill_md.py"
)

PASSING_SKILL = """---
name: sample
description: a sample
when_to_use: always
argument-hint: none
allowed-tools: Read, Glob, Grep
disable-model-invocation: true
---

## Workflow

See [notes](references/notes.md).
"""


class SkillValidatorTests(unittest.TestCase):
    def _validator(self, body: str, *, skill_name: str = "sample") -> "skill_check.SkillValidator":
        skill_dir = Path(self.tmp.name) / skill_name
        (skill_dir / "references").mkdir(parents=True, exist_ok=True)
        (skill_dir / "references" / "notes.md").write_text("notes\n", encoding="utf-8")
        (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
        return skill_check.SkillValidator(skill_dir)

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_passing_skill_passes_every_shared_check(self) -> None:
        validator = self._validator(PASSING_SKILL)
        results, overall = skill_check.run_checks(
            [
                lambda: validator.check_frontmatter(["name", "description"], model_invocation_disabled=True),
                validator.check_model_invocation_disabled,
                lambda: validator.check_required_sections([r"^##\s+Workflow"]),
                validator.check_read_only_tools,
                validator.check_line_cap,
                validator.check_references_dir,
                validator.check_references_linked,
            ]
        )
        self.assertTrue(overall, [r for r in results if not r.passed])

    def test_missing_field_and_name_mismatch_fail(self) -> None:
        validator = self._validator(PASSING_SKILL, skill_name="other")
        result = validator.check_frontmatter(["name", "missing-field"])
        self.assertFalse(result.passed)
        self.assertIn("missing-field", result.detail)
        self.assertIn("name_match=False", result.detail)

    def test_invocation_gate_is_tri_state(self) -> None:
        always_on = PASSING_SKILL.replace("disable-model-invocation: true", "disable-model-invocation: false")
        validator = self._validator(always_on)
        self.assertTrue(validator.check_frontmatter(["name"], model_invocation_disabled=False).passed)
        self.assertFalse(validator.check_frontmatter(["name"], model_invocation_disabled=True).passed)
        self.assertTrue(validator.check_frontmatter(["name"]).passed)

    def test_write_tool_grant_fails_read_only_check(self) -> None:
        validator = self._validator(PASSING_SKILL.replace("Read, Glob, Grep", "Read, Glob, Grep, Edit"))
        self.assertFalse(validator.check_read_only_tools().passed)

    def test_missing_section_marker_and_reference_are_reported(self) -> None:
        validator = self._validator(PASSING_SKILL.replace("See [notes](references/notes.md).", ""))
        self.assertFalse(validator.check_references_linked().passed)
        self.assertFalse(validator.check_required_sections([r"^##\s+Pitfalls"]).passed)
        self.assertFalse(validator.check_markers(["absent"], name="markers").passed)
        self.assertFalse(
            validator.check_forbidden_patterns([r"^##\s+Workflow"], name="forbidden").passed
        )

    def test_line_cap_counts_against_the_limit(self) -> None:
        validator = self._validator("\n".join(["line"] * 20))
        self.assertFalse(validator.check_line_cap(limit=10).passed)
        self.assertTrue(validator.check_line_cap(limit=100).passed)

    def test_json_payload_keeps_both_legacy_shapes(self) -> None:
        results = [skill_check.CheckResult("a", True), skill_check.CheckResult("b", False, "why")]
        payload = skill_check.json_payload("sample", results, False)
        self.assertEqual(payload["overall"], "fail")
        self.assertFalse(payload["passed"])
        self.assertEqual(payload["summary"], {"total": 2, "passed": 1, "failed": 1})


class SharedFrontmatterTests(unittest.TestCase):
    def test_splits_frontmatter_from_body(self) -> None:
        frontmatter, body = skill_md.split_frontmatter('---\nname: "verify-x"\n---\n\n## Purpose\n')
        self.assertEqual(frontmatter, {"name": "verify-x"})
        self.assertIn("## Purpose", body)

    def test_unterminated_block_is_treated_as_absent(self) -> None:
        self.assertIsNone(skill_md.parse_frontmatter("---\nname: broken\n"))
        self.assertIsNone(skill_md.parse_frontmatter("no frontmatter here"))

    def test_section_lookup_ignores_heading_level_and_case(self) -> None:
        self.assertTrue(skill_md.has_section("#### when to run\n", "When to Run"))
        self.assertFalse(skill_md.has_section("plain text mentioning Workflow\n", "Workflow"))


if __name__ == "__main__":
    unittest.main()
