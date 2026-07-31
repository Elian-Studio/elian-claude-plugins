from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from _spec_coverage_loader import REPO_ROOT, load

csf = load(
    "check_skill_frontmatter",
    REPO_ROOT / "plugins" / "elian-store" / "skills" / "manage-skills" / "scripts" / "check-skill-frontmatter.py",
)

REQUIRED_SECTION_BODY = "\n".join(f"## {s}" for s in csf.REQUIRED_SECTIONS) + "\n"


class ParseFrontmatterTests(unittest.TestCase):
    def test_parses_and_strips_quotes(self) -> None:
        fm, body = csf.parse_frontmatter('---\nname: verify-build\ndescription: "does x"\n---\nbody here\n')
        self.assertEqual(fm, {"name": "verify-build", "description": "does x"})
        self.assertEqual(body.strip(), "body here")

    def test_no_leading_marker_returns_none(self) -> None:
        fm, body = csf.parse_frontmatter("# not frontmatter\n")
        self.assertIsNone(fm)
        self.assertEqual(body, "# not frontmatter\n")

    def test_unterminated_frontmatter_returns_none(self) -> None:
        fm, _ = csf.parse_frontmatter("---\nname: x\n")
        self.assertIsNone(fm)


class HasRequiredSectionTests(unittest.TestCase):
    def test_matches_heading_case_insensitively(self) -> None:
        self.assertTrue(csf.has_required_section("### when to run\n", "When to Run"))

    def test_missing_section(self) -> None:
        self.assertFalse(csf.has_required_section("## Something Else\n", "Purpose"))


class CheckOneTests(unittest.TestCase):
    def _write(self, tmp: Path, text: str) -> Path:
        p = tmp / "SKILL.md"
        p.write_text(text, encoding="utf-8")
        return p

    def _valid_text(self, name: str = "verify-build", tools: str = "Read") -> str:
        return (
            f"---\nname: {name}\ndescription: does x\nallowed-tools: {tools}\n---\n"
            + REQUIRED_SECTION_BODY
        )

    def test_valid_skill_passes(self) -> None:
        with TemporaryDirectory() as tmpname:
            report = csf.check_one(self._write(Path(tmpname), self._valid_text()))
        self.assertEqual(report["verdict"], "PASS")
        self.assertTrue(all(c["pass"] for c in report["checks"].values()))

    def test_missing_frontmatter_fails_multiple_checks(self) -> None:
        with TemporaryDirectory() as tmpname:
            report = csf.check_one(self._write(Path(tmpname), REQUIRED_SECTION_BODY))
        self.assertEqual(report["verdict"], "FAIL")
        self.assertFalse(report["checks"]["frontmatter_block"]["pass"])
        self.assertFalse(report["checks"]["required_fields"]["pass"])

    def test_missing_required_field(self) -> None:
        with TemporaryDirectory() as tmpname:
            text = "---\nname: verify-build\n---\n" + REQUIRED_SECTION_BODY
            report = csf.check_one(self._write(Path(tmpname), text))
        self.assertIn("description", report["checks"]["required_fields"]["missing"])

    def test_non_kebab_name_fails_name_format(self) -> None:
        with TemporaryDirectory() as tmpname:
            report = csf.check_one(self._write(Path(tmpname), self._valid_text(name="Verify_Build")))
        self.assertFalse(report["checks"]["name_format"]["pass"])

    def test_missing_section_reported(self) -> None:
        with TemporaryDirectory() as tmpname:
            text = "---\nname: verify-build\ndescription: d\nallowed-tools: Read\n---\n## Purpose\n"
            report = csf.check_one(self._write(Path(tmpname), text))
        missing = report["checks"]["required_sections"]["missing"]
        self.assertIn("Workflow", missing)
        self.assertNotIn("Purpose", missing)

    def test_dangerous_tools_flagged(self) -> None:
        with TemporaryDirectory() as tmpname:
            report = csf.check_one(self._write(Path(tmpname), self._valid_text(tools="Bash(*)")))
        self.assertFalse(report["checks"]["allowed_tools"]["pass"])
        self.assertTrue(report["checks"]["allowed_tools"]["violations"])

    def test_sudo_and_rm_flagged(self) -> None:
        with TemporaryDirectory() as tmpname:
            report = csf.check_one(self._write(Path(tmpname), self._valid_text(tools="Bash(sudo rm -rf /)")))
        self.assertGreaterEqual(len(report["checks"]["allowed_tools"]["violations"]), 1)


class MainTests(unittest.TestCase):
    def _valid(self, tmp: Path) -> Path:
        p = tmp / "SKILL.md"
        p.write_text(
            "---\nname: verify-build\ndescription: d\nallowed-tools: Read\n---\n" + REQUIRED_SECTION_BODY,
            encoding="utf-8",
        )
        return p

    def test_json_output_all_pass(self) -> None:
        with TemporaryDirectory() as tmpname:
            p = self._valid(Path(tmpname))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = csf.main([str(p), "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["all_pass"])

    def test_missing_file_exits_one(self) -> None:
        with TemporaryDirectory() as tmpname:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = csf.main([str(Path(tmpname) / "nope.md"), "--json"])
        self.assertEqual(code, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["all_pass"])


if __name__ == "__main__":
    unittest.main()
