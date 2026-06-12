# elian-store

`elian-store` is the distributable Claude Code plugin bundle in this repository. Install it once to get the full set of bundled skills, agents, hooks, and validators.

## Start Here

- Install the plugin from the marketplace entry in the repo root.
- Enable Claude Code marketplace/plugin auto-update in your Claude Code settings if you want native marketplace updates instead of only manual `/plugin update` refreshes.
- Use `/elian-store:<skill-name>` to invoke a skill.
- Read the skill's `SKILL.md` before changing or extending it.
- Use the root `README.md` for repository-level structure and parity context.

## Common Entry Points

| Skill | Use when | Invocation |
|---|---|---|
| `brainstorm` | The request is still fuzzy and needs scope, criteria, or options. | `/elian-store:brainstorm` |
| `decision-dashboard` | You need a printable decision artifact for 3+ blocking choices. | `/elian-store:decision-dashboard` |
| `ai-assisted-feature-development` | You want planning artifacts before AI-assisted coding begins. | `/elian-store:ai-assisted-feature-development` |
| `design-ui` | You need interview-driven UI/UX design artifacts. | `/elian-store:design-ui` |
| `implement` | You are building a new feature through approval-gated TDD. | `/elian-store:implement` |
| `fix` | You are repairing a confirmed bug with regression tests first. | `/elian-store:fix` |
| `improve` | You are changing working behavior with explicit before/after evidence. | `/elian-store:improve` |
| `review` | You need a read-only engineering review of code, diffs, or PRs. | `/elian-store:review` |
| `verify-implementation` | You need to discover and run verify skills before shipping. | `/elian-store:verify-implementation` |
| `manage-skills` | You need to detect or repair verify-skill drift after changes. | `/elian-store:manage-skills` |
| `generate-teammate` | You need to decide direct, subagent, or team execution. | `/elian-store:generate-teammate` |
| `create-document` | You need schema-validated HTML or Markdown artifacts. | `/elian-store:create-document` |
| `document-writer` | You need to turn arbitrary content into a polished, house-styled HTML (or Markdown) document. | `/elian-store:document-writer` |
| `persona-review` | You want a persona-specific critique instead of a generic review. | `/elian-store:persona-review` |
| `harness-manager` | The Codex and Claude Code global harnesses have drifted and you want them reconciled. | `/elian-store:harness-manager` |
| `pr-writer` | You need a review-friendly PR/MR title and body drafted from the diff, commits, and stated intent. | `/elian-store:pr-writer` |
| `skill-dispatcher` | You want an opt-in recommendation for the smallest relevant `elian-store` skill before starting work. | `/elian-store:skill-dispatcher` |

## Package Layout

```text
plugins/elian-store/
  .claude-plugin/plugin.json
  agents/
  hooks/
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

Typical checks:

```shell
ruby -EUTF-8 -ryaml -e 'Dir["plugins/elian-store/skills/*/SKILL.md"].sort.each { |p| s=File.read(p, encoding: "UTF-8"); YAML.safe_load(s.split(/^---\s*$/,3)[1] || "", permitted_classes: [], aliases: false); puts "OK #{p}" }'
python3 plugins/elian-store/skills/review/scripts/validate_skill.py
```

## Release Boundary

This directory is the plugin bundle source of truth. The installed Claude plugin should always match the metadata in `plugins/elian-store/.claude-plugin/plugin.json` and the root marketplace entry.
