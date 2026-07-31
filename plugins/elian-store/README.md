# elian-store

`elian-store` is the distributable Claude Code plugin bundle in this repository. Install it once to get the full set of bundled skills, agents, hooks, and validators.

## Start Here

- Install the plugin from the marketplace entry in the repo root.
- Enable Claude Code marketplace/plugin auto-update in your Claude Code settings if you want native marketplace updates instead of only manual `/plugin update` refreshes.
- The SessionStart update hook shows a short CHANGELOG excerpt for available updates when release notes are reachable, and runs versioned `migrations/vX.Y.Z.sh` scripts after future upgrades.
- Use `/elian-store:<skill-name>` to invoke a skill.
- Read the skill's `SKILL.md` before changing or extending it.
- Use the root `README.md` for repository-level structure and parity context.

## Common Entry Points

| Skill | Use when | Invocation |
|---|---|---|
| `intake-spec` | Front door — you are starting a feature and need requirements captured as a `spec.json`. | `/elian-store:intake-spec` |
| `design-feature` | The spec is settled and you need the design document set (design, architecture, PRD, tech spec, API spec, QA checklist, roadmap hub). | `/elian-store:design-feature` |
| `update-design` | Design docs already exist and a decision, review, or requirement changed — propagate it to only the affected documents. | `/elian-store:update-design` |
| `brainstorm` | The request is still fuzzy and needs scope, criteria, or options. | `/elian-store:brainstorm` |
| `decision-dashboard` | You need a printable decision artifact for 3+ blocking choices. | `/elian-store:decision-dashboard` |
| `implement` | You are building a new feature through approval-gated TDD. | `/elian-store:implement` |
| `fix` | You are repairing a confirmed bug with regression tests first. | `/elian-store:fix` |
| `improve` | You are changing working behavior with explicit before/after evidence. | `/elian-store:improve` |
| `review` | You need a read-only engineering review of code, diffs, or PRs. | `/elian-store:review` |
| `verify-implementation` | You need to discover and run verify skills before shipping. | `/elian-store:verify-implementation` |
| `spec-coverage` | Implementation is underway and you need to know which PRD acceptance criteria are actually backed by a passing test. | `/elian-store:spec-coverage` |
| `manage-skills` | You need to detect or repair verify-skill drift after changes. | `/elian-store:manage-skills` |
| `generate-teammate` | You need to decide direct, subagent, or team execution. | `/elian-store:generate-teammate` |
| `create-document` | You need schema-validated HTML or Markdown artifacts. | `/elian-store:create-document` |
| `document-writer` | You need to turn arbitrary content into a polished, house-styled HTML (or Markdown) document. | `/elian-store:document-writer` |
| `persona-review` | You want a persona-specific critique instead of a generic review. | `/elian-store:persona-review` |
| `harness-manager` | The Codex and Claude Code global harnesses have drifted and you want them reconciled. | `/elian-store:harness-manager` |
| `pr-writer` | You need a review-friendly PR/MR title and body drafted from the diff, commits, and stated intent. | `/elian-store:pr-writer` |
| `pr-review` | You want an existing PR/MR reviewed from many perspectives (specialists + personas) with one synthesized verdict, posted only on confirmation. | `/elian-store:pr-review` |
| `verify-before-claiming` | You are about to claim work passes/builds/is fixed/done and want to force fresh evidence first. | `/elian-store:verify-before-claiming` |
| `respond-to-review` | You received review feedback on your change and need to respond with rigor before implementing. | `/elian-store:respond-to-review` |

## Package Layout

```text
plugins/elian-store/
  .claude-plugin/plugin.json
  agents/
  hooks/
  migrations/
  skills/
    <skill>/
      SKILL.md
      scripts/
      references/
      templates/   # when needed
```

## What To Edit

- Change a skill: edit `skills/<skill>/SKILL.md` and its `references/` or `scripts/`.
- Add a skill: create a new skill directory, then update plugin metadata, marketplace metadata, the root README, this README, the changelog, and parity docs.
- Change plugin metadata: edit `plugins/elian-store/.claude-plugin/plugin.json`.
- Change marketplace metadata: edit `.claude-plugin/marketplace.json`.
- Change repository-level parity guidance: edit `docs/claude-codex-skill-parity.md`.

## Validation

Use the skill-owned validator when the skill provides one, and keep the plugin metadata in sync when the bundle changes.

Typical checks from the repository root (the repository validator is contributor tooling and is
not part of the installed plugin):

```shell
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
python3 tools/generate.py
ruby -EUTF-8 -ryaml -e 'Dir.glob("plugins/*/skills/*/SKILL.md").sort.each { |p| s=File.read(p, encoding: "UTF-8"); YAML.safe_load(s.split(/^---\s*$/,3)[1] || "", permitted_classes: [], aliases: false); puts "OK #{p}" }'
python3 plugins/elian-store/skills/review/scripts/validate_skill.py
python3 plugins/elian-store/skills/_shared/validate_skill.py plugins/elian-store/skills/implement
```

`brainstorm`, `fix`, `implement`, and `improve` share `skills/_shared/validate_skill.py` rather
than each carrying a copy of it. It lives inside the plugin, not in the repository's `tools/`,
so the command the skills document also resolves in an installed plugin.

## Release Boundary

This directory is the plugin bundle source of truth. The installed Claude plugin should always match the metadata in `plugins/elian-store/.claude-plugin/plugin.json` and the root marketplace entry.
