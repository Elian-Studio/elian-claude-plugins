from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from _spec_coverage_loader import REPO_ROOT, load

vs = load("tools_validate_skill", REPO_ROOT / "tools" / "validate_skill.py")


REQUIRED_SECTION_HEADINGS = [
    "## Workflow",
    "## Standing Rules",
    "## Forbidden",
    "## Pitfalls",
    "## Where this fits",
    "## Manual decision gating",
    "## Reflection",
    "## Persistent artifacts",
    "## BEFORE / AFTER",
    "## Pre-flight checklist",
]


def _make_skill(
    root: Path,
    name: str = "implement",
    *,
    frontmatter: dict | None = None,
    sections: bool = True,
    with_references: bool = True,
    link_references: bool = True,
) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    fm = frontmatter if frontmatter is not None else {
        "name": name,
        "description": "does a thing",
        "when_to_use": "when needed",
        "argument-hint": "[target]",
        "allowed-tools": "Read",
        "disable-model-invocation": "true",
    }
    fm_lines = "\n".join(f"{k}: {v}" for k, v in fm.items())
    body = [f"---\n{fm_lines}\n---", f"# {name}"]
    if sections:
        body.extend(REQUIRED_SECTION_HEADINGS)
    if link_references:
        body.append("See [the guide](references/guide.md).")
    (skill_dir / "SKILL.md").write_text("\n\n".join(body) + "\n", encoding="utf-8")
    if with_references:
        refs = skill_dir / "references"
        refs.mkdir()
        (refs / "guide.md").write_text("# guide\n", encoding="utf-8")
    return skill_dir


class FrontmatterParsingTests(unittest.TestCase):
    def test_parses_simple_key_values(self) -> None:
        fm = vs._frontmatter("---\nname: x\ndescription: y\n---\nbody\n")
        self.assertEqual(fm, {"name": "x", "description": "y"})

    def test_missing_frontmatter_is_empty(self) -> None:
        self.assertEqual(vs._frontmatter("# no frontmatter\n"), {})

    def test_read_missing_file_returns_empty_string(self) -> None:
        with TemporaryDirectory() as tmp:
            self.assertEqual(vs._read(Path(tmp) / "nope.md"), "")


class CheckTests(unittest.TestCase):
    def test_all_checks_pass_on_a_well_formed_skill(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname))
            results, overall = vs.run_all(skill)
        self.assertTrue(overall, msg=[r.to_dict() for r in results if not r.passed])

    def test_name_mismatch_fails_frontmatter_check(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname), "implement", frontmatter={
                "name": "wrong", "description": "d", "when_to_use": "w",
                "argument-hint": "h", "allowed-tools": "Read",
            })
            result = vs.check_frontmatter(skill)
        self.assertFalse(result.passed)
        self.assertIn("name_match=False", result.detail)

    def test_missing_required_field_fails(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname), "implement", frontmatter={
                "name": "implement", "description": "d",
            })
            result = vs.check_frontmatter(skill)
        self.assertFalse(result.passed)
        self.assertIn("when_to_use", result.detail)

    def test_disable_model_invocation_detected(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname), "implement", frontmatter={
                "name": "implement", "description": "d", "when_to_use": "w",
                "argument-hint": "h", "allowed-tools": "Read",
                "disable-model-invocation": "true",
            })
            self.assertTrue(vs.check_disable_model_invocation(skill).passed)

    def test_disable_model_invocation_missing_fails(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname), "implement", frontmatter={
                "name": "implement", "description": "d", "when_to_use": "w",
                "argument-hint": "h", "allowed-tools": "Read",
            })
            self.assertFalse(vs.check_disable_model_invocation(skill).passed)

    def test_missing_sections_fail(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname), sections=False)
            result = vs.check_required_sections(skill)
        self.assertFalse(result.passed)

    def test_references_dir_missing_fails(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname), with_references=False)
            self.assertFalse(vs.check_references_dir(skill).passed)

    def test_references_not_linked_fails(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname), link_references=False)
            self.assertFalse(vs.check_references_linked(skill).passed)


class FormatTests(unittest.TestCase):
    def test_format_json_summary_counts(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname))
            results, overall = vs.run_all(skill)
            payload = vs.format_json("implement", results, overall)
        self.assertEqual(payload["overall"], "pass")
        self.assertEqual(payload["summary"]["total"], len(results))
        self.assertEqual(payload["summary"]["failed"], 0)

    def test_format_human_marks_failures(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname), with_references=False)
            results, overall = vs.run_all(skill)
            text = vs.format_human("implement", results, overall)
        self.assertIn("[FAIL]", text)
        self.assertIn("Overall: FAIL", text)


class MainTests(unittest.TestCase):
    def _run(self, args: list[str]) -> tuple[int, str]:
        old = sys.argv
        sys.argv = ["validate_skill.py"] + args
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = vs.main()
        finally:
            sys.argv = old
        return code, buf.getvalue()

    def test_returns_zero_for_valid_skill_json(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname))
            code, out = self._run([str(skill), "--json"])
        self.assertEqual(code, 0)
        parsed = json.loads(out)
        self.assertIsInstance(parsed, list)
        self.assertEqual(parsed[0]["overall"], "pass")

    def test_returns_one_for_invalid_skill(self) -> None:
        with TemporaryDirectory() as tmpname:
            skill = _make_skill(Path(tmpname), with_references=False)
            code, _ = self._run([str(skill), "--quiet"])
        self.assertEqual(code, 1)

    def test_missing_skill_md_returns_one(self) -> None:
        with TemporaryDirectory() as tmpname:
            empty = Path(tmpname) / "empty"
            empty.mkdir()
            code, _ = self._run([str(empty), "--quiet"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
