from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_repository.py"
SPEC = importlib.util.spec_from_file_location("validate_repository", SCRIPT)
assert SPEC and SPEC.loader
validator_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator_module
SPEC.loader.exec_module(validator_module)

RepositoryValidator = validator_module.RepositoryValidator
parse_frontmatter = validator_module.parse_frontmatter
strip_fenced_code = validator_module.strip_fenced_code


class FrontmatterTests(unittest.TestCase):
    def test_parses_folded_values_and_tool_lists(self) -> None:
        metadata = parse_frontmatter(
            """---
name: sample
description: >
  First line
  second line
allowed-tools:
  - Read
  - Bash(git status*)
---
body
"""
        )
        self.assertEqual(metadata["name"], "sample")
        self.assertEqual(metadata["description"], "First line second line")
        self.assertEqual(metadata["allowed-tools"], "Read Bash(git status*)")

    def test_rejects_unclosed_frontmatter(self) -> None:
        self.assertEqual(parse_frontmatter("---\nname: broken\n"), {})


class RepositoryFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.skills = self.root / "plugins" / "elian-store" / "skills"
        self.skills.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_skill(
        self,
        directory: str,
        *,
        name: str | None = None,
        tools: str = "Read",
        disable: str | None = None,
        description: str = "A focused test skill.",
    ) -> Path:
        skill_dir = self.skills / directory
        skill_dir.mkdir()
        gate = f"\ndisable-model-invocation: {disable}" if disable is not None else ""
        path = skill_dir / "SKILL.md"
        path.write_text(
            f"""---
name: {name or directory}
description: {description}
allowed-tools: {tools}{gate}
---
# {directory}
""",
            encoding="utf-8",
        )
        return path

    def test_reports_directory_name_mismatch(self) -> None:
        self.write_skill("alpha", name="beta")
        validator = RepositoryValidator(self.root)
        validator.validate_skill_contracts()
        self.assertTrue(any("does not match directory" in item.message for item in validator.findings))

    def test_reports_duplicate_skill_name(self) -> None:
        self.write_skill("alpha", name="shared")
        self.write_skill("beta", name="shared")
        validator = RepositoryValidator(self.root)
        validator.validate_skill_contracts()
        self.assertTrue(any("duplicate skill name" in item.message for item in validator.findings))

    def test_requires_invocation_gate_for_write_tools(self) -> None:
        self.write_skill("writer", tools="Read Write")
        validator = RepositoryValidator(self.root)
        validator.validate_skill_contracts()
        self.assertTrue(any(item.check == "side-effect-gate" for item in validator.findings))

    def test_requires_invocation_gate_for_known_high_impact_skill(self) -> None:
        self.write_skill("finish-branch", tools="Read")
        validator = RepositoryValidator(self.root)
        validator.validate_skill_contracts()
        self.assertTrue(any(item.check == "side-effect-gate" for item in validator.findings))

    def test_read_only_command_prefixes_are_not_misclassified(self) -> None:
        self.write_skill("reader", tools="Read Bash(git merge-base*) Bash(mvn test*)")
        validator = RepositoryValidator(self.root)
        validator.validate_skill_contracts()
        self.assertFalse(any(item.check == "side-effect-gate" for item in validator.findings))

    def test_rejects_unbounded_tool_permissions(self) -> None:
        self.write_skill("shell", tools="Read Bash(git *)", disable="true")
        validator = RepositoryValidator(self.root)
        validator.validate_skill_contracts()
        self.assertTrue(any(item.check == "tool-policy" for item in validator.findings))

    def test_flags_pre_allowlisted_pr_posting_commands(self) -> None:
        self.write_skill(
            "poster",
            tools="Read Bash(gh pr view*) Bash(gh pr comment*)",
            disable="true",
        )
        validator = RepositoryValidator(self.root)
        validator.validate_skill_contracts()
        self.assertTrue(
            any(
                item.check == "tool-policy" and "posting commands" in item.message
                for item in validator.findings
            )
        )

    def test_read_only_pr_query_commands_are_allowed(self) -> None:
        self.write_skill("querier", tools="Read Bash(gh pr view*) Bash(gh pr diff*) Bash(glab mr view*)")
        validator = RepositoryValidator(self.root)
        validator.validate_skill_contracts()
        self.assertFalse(
            any("posting commands" in item.message for item in validator.findings)
        )

    def test_reports_live_missing_link_but_ignores_fenced_example(self) -> None:
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "guide.md").write_text(
            "[Missing](./missing.md)\n\n```markdown\n[Example](./example.md)\n```\n",
            encoding="utf-8",
        )
        validator = RepositoryValidator(self.root)
        validator.validate_links()
        messages = [item.message for item in validator.findings]
        self.assertEqual(messages, ["relative link target does not exist: ./missing.md"])
        self.assertNotIn("./example.md", strip_fenced_code((docs / "guide.md").read_text()))

    def test_deferred_skill_must_not_ship_a_codex_symlink(self) -> None:
        self.write_skill("spec-coverage")
        (self.root / "tools").mkdir()
        (self.root / "plugins" / "elian-store" / "agents").mkdir()
        codex_skills = self.root / "codex" / "skills"
        codex_skills.mkdir(parents=True)
        # A deferred skill is not shipped; a stray symlink contradicts that.
        (codex_skills / "spec-coverage").symlink_to("../../plugins/elian-store/skills/spec-coverage")
        (self.root / "tools" / "clusters.json").write_text(
            json.dumps(
                {
                    "source": {
                        "skills_dir": "plugins/elian-store/skills",
                        "agents_dir": "plugins/elian-store/agents",
                    },
                    "agent_groups": {},
                    "plugins": {"only": {"skills": ["spec-coverage"]}},
                    "codex": {
                        "claude_only": [],
                        "prompt_only": [],
                        "deferred": ["spec-coverage"],
                    },
                }
            ),
            encoding="utf-8",
        )
        validator = RepositoryValidator(self.root)
        validator.validate_cluster_manifest()
        self.assertTrue(
            any("must not ship a codex/skills symlink" in item.message for item in validator.findings)
        )

    def test_reports_cluster_orphan_and_disposition_overlap(self) -> None:
        self.write_skill("alpha")
        (self.root / "tools").mkdir()
        (self.root / "plugins" / "elian-store" / "agents").mkdir()
        (self.root / "tools" / "clusters.json").write_text(
            json.dumps(
                {
                    "source": {
                        "skills_dir": "plugins/elian-store/skills",
                        "agents_dir": "plugins/elian-store/agents",
                    },
                    "agent_groups": {},
                    "plugins": {},
                    "codex": {
                        "claude_only": ["alpha"],
                        "prompt_only": ["alpha"],
                        "deferred": [],
                    },
                }
            ),
            encoding="utf-8",
        )
        validator = RepositoryValidator(self.root)
        validator.validate_cluster_manifest()
        messages = [item.message for item in validator.findings]
        self.assertTrue(any("unassigned" in message for message in messages))
        self.assertTrue(any("appears in both" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
