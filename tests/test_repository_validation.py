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
        self.write_skill("harness-manager", tools="Read")
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


class DesignArtifactContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.skills = self.root / "plugins" / "elian-store" / "skills"
        (self.skills / "design-feature").mkdir(parents=True)
        (self.skills / "update-design").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, design_feature: str, update_design: str) -> None:
        (self.skills / "design-feature" / "SKILL.md").write_text(design_feature, encoding="utf-8")
        (self.skills / "update-design" / "SKILL.md").write_text(update_design, encoding="utf-8")

    GOOD = "Everything lives under claudedocs/<label>/\n"

    def test_passes_on_aligned_contract(self) -> None:
        self.write(self.GOOD, self.GOOD)
        validator = RepositoryValidator(self.root)
        validator.validate_design_artifact_contract()
        self.assertEqual([item for item in validator.findings if item.check == "design-contract"], [])

    def test_flags_retired_design_path(self) -> None:
        self.write(self.GOOD + "legacy claudedocs/design/<feature>/\n", self.GOOD)
        validator = RepositoryValidator(self.root)
        validator.validate_design_artifact_contract()
        self.assertTrue(any("retired" in item.message for item in validator.findings))

    def test_flags_retired_path_in_update_design(self) -> None:
        self.write(self.GOOD, self.GOOD + "legacy claudedocs/design/<feature>/\n")
        validator = RepositoryValidator(self.root)
        validator.validate_design_artifact_contract()
        self.assertTrue(any("update-design still references" in item.message for item in validator.findings))


class CodexDanglingSymlinkTests(unittest.TestCase):
    """Retiring a skill used to leave its codex/skills symlink behind, and nothing caught it:
    both disposition loops iterate skills discovered under the plugin, so a link pointing at
    a skill that no longer exists is invisible to them."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.skills = self.root / "plugins" / "elian-store" / "skills"
        self.skills.mkdir(parents=True)
        (self.root / "plugins" / "elian-store" / "agents").mkdir()
        (self.root / "tools").mkdir()
        self.codex = self.root / "codex" / "skills"
        self.codex.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_manifest(self, skills: list[str]) -> None:
        (self.root / "tools" / "clusters.json").write_text(
            json.dumps(
                {
                    "source": {
                        "skills_dir": "plugins/elian-store/skills",
                        "agents_dir": "plugins/elian-store/agents",
                    },
                    "agent_groups": {},
                    "plugins": {"only": {"skills": skills}},
                    "codex": {"claude_only": [], "prompt_only": [], "deferred": []},
                }
            ),
            encoding="utf-8",
        )

    def make_skill(self, name: str) -> None:
        skill_dir = self.skills / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: t\nallowed-tools: Read\n---\n# {name}\n",
            encoding="utf-8",
        )

    def test_flags_a_symlink_whose_target_was_removed(self) -> None:
        self.make_skill("kept")
        self.write_manifest(["kept"])
        (self.codex / "kept").symlink_to("../../plugins/elian-store/skills/kept")
        # The skill directory this one points at was never created — the retired case.
        (self.codex / "retired").symlink_to("../../plugins/elian-store/skills/retired")
        validator = RepositoryValidator(self.root)
        validator.validate_cluster_manifest()
        self.assertTrue(any("dangling symlink" in item.message for item in validator.findings))

    def test_passes_when_every_link_resolves(self) -> None:
        self.make_skill("kept")
        self.write_manifest(["kept"])
        (self.codex / "kept").symlink_to("../../plugins/elian-store/skills/kept")
        validator = RepositoryValidator(self.root)
        validator.validate_cluster_manifest()
        self.assertEqual(
            [i for i in validator.findings if i.check == "codex-disposition"], []
        )


class MultiPluginCoverageTests(unittest.TestCase):
    """Both checks below used to hard-code plugins/elian-store, so a second plugin
    was validated by nothing. These lock the plugin-agnostic behavior in place."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / ".claude-plugin").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_plugin(self, name: str, version: str) -> Path:
        plugin_dir = self.root / "plugins" / name
        (plugin_dir / ".claude-plugin").mkdir(parents=True)
        (plugin_dir / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": name, "version": version}), encoding="utf-8"
        )
        skills = plugin_dir / "skills"
        skills.mkdir()
        return skills

    def write_marketplace(self, entries: dict[str, str]) -> None:
        (self.root / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps(
                {"plugins": [{"name": n, "version": v} for n, v in entries.items()]}
            ),
            encoding="utf-8",
        )

    def test_version_parity_covers_every_plugin_not_just_the_bundle(self) -> None:
        self.write_plugin("elian-store", "4.1.0")
        self.write_plugin("elian-workflow", "9.9.9")
        self.write_marketplace({"elian-store": "4.1.0", "elian-workflow": "1.0.0"})
        validator = RepositoryValidator(self.root)
        validator.validate_versions()
        messages = [item.message for item in validator.findings]
        self.assertTrue(any("elian-workflow" in message for message in messages))
        self.assertFalse(any("elian-store" in message for message in messages))

    def test_version_parity_reports_a_missing_marketplace_entry(self) -> None:
        self.write_plugin("elian-workflow", "1.0.0")
        self.write_marketplace({})
        validator = RepositoryValidator(self.root)
        validator.validate_versions()
        self.assertTrue(
            any("marketplace entry is missing" in item.message for item in validator.findings)
        )

    def test_english_policy_covers_a_second_plugin(self) -> None:
        skills = self.write_plugin("elian-workflow", "1.0.0")
        self.write_marketplace({"elian-workflow": "1.0.0"})
        (skills / "issue-open").mkdir()
        (skills / "issue-open" / "SKILL.md").write_text(
            "---\nname: issue-open\n---\n한글 본문\n", encoding="utf-8"
        )
        validator = RepositoryValidator(self.root)
        validator.validate_english_policy()
        self.assertTrue(any(item.check == "english-policy" for item in validator.findings))


class ComposedPluginTests(unittest.TestCase):
    """A published composed plugin carries generated copies of another plugin's skills.
    The copies are committed, so a hand edit would survive until the next sync silently
    reverted it. These lock in that the copies are held byte-identical."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source_skills = self.root / "plugins" / "elian-store" / "skills"
        (self.source_skills / "implement").mkdir(parents=True)
        (self.source_skills / "implement" / "SKILL.md").write_text(
            "---\nname: implement\n---\nbody\n", encoding="utf-8"
        )
        (self.root / "plugins" / "elian-store" / "agents").mkdir(parents=True)
        (self.root / "plugins" / "elian-store" / "agents" / "quality-engineer.md").write_text(
            "agent\n", encoding="utf-8"
        )
        self.target_skills = self.root / "plugins" / "elian-workflow" / "skills"
        (self.target_skills / "implement").mkdir(parents=True)
        (self.target_skills / "implement" / "SKILL.md").write_text(
            "---\nname: implement\n---\nbody\n", encoding="utf-8"
        )
        (self.target_skills / "issue-open").mkdir()
        (self.target_skills / "issue-open" / "SKILL.md").write_text(
            "---\nname: issue-open\n---\nnative\n", encoding="utf-8"
        )
        (self.root / "plugins" / "elian-workflow" / "agents").mkdir(parents=True)
        (self.root / "plugins" / "elian-workflow" / "agents" / "quality-engineer.md").write_text(
            "agent\n", encoding="utf-8"
        )
        self.manifest = self.root / "tools" / "clusters.json"
        self.manifest.parent.mkdir(parents=True)
        self.write_manifest()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_manifest(self) -> None:
        self.manifest.write_text(
            json.dumps(
                {
                    "source": {
                        "skills_dir": "plugins/elian-store/skills",
                        "agents_dir": "plugins/elian-store/agents",
                        "shared_dir": "plugins/elian-store/skills/_shared",
                    },
                    "agent_groups": {"domain": ["quality-engineer"]},
                    "plugins": {},
                    "published": {
                        "elian-workflow": {
                            "target": "plugins/elian-workflow",
                            "skills": ["implement"],
                            "native_skills": ["issue-open"],
                            "agents": ["domain"],
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

    def test_passes_when_the_generated_copy_matches_its_source(self) -> None:
        validator = RepositoryValidator(self.root)
        validator.validate_composed_plugins()
        self.assertEqual([i.message for i in validator.findings], [])

    def test_flags_a_generated_copy_edited_by_hand(self) -> None:
        (self.target_skills / "implement" / "SKILL.md").write_text(
            "---\nname: implement\n---\nedited by hand\n", encoding="utf-8"
        )
        validator = RepositoryValidator(self.root)
        validator.validate_composed_plugins()
        self.assertTrue(
            any("differs from" in i.message for i in validator.findings),
            [i.message for i in validator.findings],
        )

    def test_flags_a_generated_agent_edited_by_hand(self) -> None:
        (self.root / "plugins" / "elian-workflow" / "agents" / "quality-engineer.md").write_text(
            "tampered\n", encoding="utf-8"
        )
        validator = RepositoryValidator(self.root)
        validator.validate_composed_plugins()
        self.assertTrue(any("quality-engineer" in i.message for i in validator.findings))

    def test_native_skill_is_not_reported_as_undeclared(self) -> None:
        validator = RepositoryValidator(self.root)
        validator.validate_composed_plugins()
        self.assertFalse(any("issue-open" in i.message for i in validator.findings))

    def test_flags_a_skill_that_is_neither_generated_nor_native(self) -> None:
        (self.target_skills / "stowaway").mkdir()
        (self.target_skills / "stowaway" / "SKILL.md").write_text(
            "---\nname: stowaway\n---\n", encoding="utf-8"
        )
        validator = RepositoryValidator(self.root)
        validator.validate_composed_plugins()
        self.assertTrue(any("stowaway" in i.path for i in validator.findings))

    def write_shared(self, *names: str) -> None:
        """Put `names` in the source _shared dir and copy them into the target."""
        source = self.source_skills / "_shared"
        target = self.target_skills / "_shared"
        source.mkdir(exist_ok=True)
        target.mkdir(exist_ok=True)
        for name in names:
            (source / name).write_text(f"{name} body\n", encoding="utf-8")
            (target / name).write_text(f"{name} body\n", encoding="utf-8")

    def set_shared_config(self, value) -> None:
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        manifest["published"]["elian-workflow"]["shared"] = value
        self.manifest.write_text(json.dumps(manifest), encoding="utf-8")

    def test_shared_list_copies_only_the_declared_files(self) -> None:
        """A target that reads two of the shared documents should not carry the rest —
        that is duplication with no reader, which is what 2.0.0 shipped 122 of."""
        self.write_shared("narrative-template.md", "notion-workspace-config.md")
        (self.source_skills / "_shared" / "review-severity.md").write_text("rubric\n", encoding="utf-8")
        self.set_shared_config(["narrative-template.md", "notion-workspace-config.md"])
        validator = RepositoryValidator(self.root)
        validator.validate_composed_plugins()
        self.assertEqual([i.message for i in validator.findings], [])

    def test_shared_true_still_requires_every_shared_file(self) -> None:
        self.write_shared("narrative-template.md")
        (self.source_skills / "_shared" / "review-severity.md").write_text("rubric\n", encoding="utf-8")
        self.set_shared_config(True)
        validator = RepositoryValidator(self.root)
        validator.validate_composed_plugins()
        self.assertTrue(
            any("review-severity.md is missing" in i.message for i in validator.findings),
            [i.message for i in validator.findings],
        )

    def test_flags_a_shared_file_the_manifest_does_not_declare(self) -> None:
        self.write_shared("narrative-template.md", "review-severity.md")
        self.set_shared_config(["narrative-template.md"])
        validator = RepositoryValidator(self.root)
        validator.validate_composed_plugins()
        self.assertTrue(
            any("not declared in the manifest" in i.message for i in validator.findings),
            [i.message for i in validator.findings],
        )

    def test_flags_a_declared_shared_file_missing_from_the_source(self) -> None:
        self.set_shared_config(["narrative-template.md"])
        validator = RepositoryValidator(self.root)
        validator.validate_composed_plugins()
        self.assertTrue(
            any("missing from the source" in i.message for i in validator.findings),
            [i.message for i in validator.findings],
        )


class PluginSelfContainmentTests(unittest.TestCase):
    """A plugin is copied as a unit at install time. Anything it resolves outside its
    own root works in this repository and breaks for installed users — the failure the
    layering document predicted but its step list under-counted."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.skills = self.root / "plugins" / "elian-workflow" / "skills"
        (self.skills / "design-feature").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_skill(self, name: str, body: str) -> None:
        (self.skills / name).mkdir(exist_ok=True)
        (self.skills / name / "SKILL.md").write_text(
            f"---\nname: {name}\n---\n{body}", encoding="utf-8"
        )

    def test_flags_a_runtime_reference_to_a_skill_in_another_plugin(self) -> None:
        self.write_skill(
            "design-feature",
            '```bash\nCD="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/create-document}"\n'
            'python3 "${CD}/scripts/build_roadmap.py"\n```\n',
        )
        validator = RepositoryValidator(self.root)
        validator.validate_plugin_self_containment()
        self.assertTrue(
            any("create-document" in i.message for i in validator.findings),
            [i.message for i in validator.findings],
        )

    def test_passes_once_the_referenced_skill_is_vendored_alongside(self) -> None:
        self.write_skill(
            "design-feature",
            '```bash\nCD="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/create-document}"\n```\n',
        )
        self.write_skill("create-document", "renderer\n")
        validator = RepositoryValidator(self.root)
        validator.validate_plugin_self_containment()
        self.assertEqual([i.message for i in validator.findings], [])

    def test_flags_a_relative_link_that_escapes_the_plugin(self) -> None:
        self.write_skill("design-feature", "See [parity](../../../docs/parity.md).\n")
        validator = RepositoryValidator(self.root)
        validator.validate_plugin_self_containment()
        self.assertTrue(any("escapes the plugin" in i.message for i in validator.findings))

    def test_allows_a_relative_link_that_stays_inside_the_plugin(self) -> None:
        self.write_skill("design-feature", "See [shared](../_shared/notes.md).\n")
        validator = RepositoryValidator(self.root)
        validator.validate_plugin_self_containment()
        self.assertEqual([i.message for i in validator.findings], [])


if __name__ == "__main__":
    unittest.main()
