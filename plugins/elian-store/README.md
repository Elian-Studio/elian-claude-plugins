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
| `issue-open` | You are starting work on an issue and want the branch upstream checked, the task moved to in-progress, and the history skeleton seeded. | `/elian-store:issue-open` |
| `issue-close` | An issue is finished and its decisions, architecture, verification, and remaining checks should be recorded as durable history. | `/elian-store:issue-close` |

## The issue cycle — `issue-open` and `issue-close`

These two are the only skills in the bundle that need configuration, and the only ones that
write to an external service. Everything else runs as installed.

Development work has three nested cycles, each wanting a different record: one audit row per
**commit**, a narrative per **issue**, and context restore/summary per **day**. The issue level
carries *why* a thing was built the way it was — the one thing a diff can never reconstruct.

```shell
/elian-store:issue-open KEY-123
# ... run the stages: intake-spec → design-feature → implement → review → pr-writer ...
/elian-store:issue-close KEY-123
```

Both are `disable-model-invocation: true` — they write to a live workspace, so they run only
when you ask for them by name.

### Notion setup

Nothing about any particular workspace is baked in. Every database id, property name, and status
value comes from a config file, resolved in this order, first match wins:

1. `$CLAUDE_PROJECT_DIR/.claude/notion-workspace.json` — per-repository override
2. `~/.claude/notion-workspace.json` — user default

You do not have to write it by hand. On first run either skill enters setup: it asks which Notion
MCP server to use, searches for your task database, reads its **live** property names and status
options, proposes a mapping for you to correct, and writes the file after you confirm. Re-run any
time with `--setup`. Requirements: a Notion MCP server connected to Claude Code, and a database
with one page per issue. A second database for per-commit rows is optional — omit it and
`issue-close` skips the commit backfill.

Full schema: [`skills/_shared/notion-workspace-config.md`](skills/_shared/notion-workspace-config.md).

### What they will not do

- No git mutation. No branch create, switch, merge, push, or delete — not even the upstream fix
  `issue-open` recommends, which it prints for you to run.
- No Notion write without showing you the draft first.
- No rewrite after an issue is closed. The narrative freezes to append-only; `--no-freeze`
  overrides when you really mean it.
- `issue-close` is recording only. Whatever you use to merge or clean up the branch should run
  **after** it — the commit range is its source, and a cleaned-up branch takes that away.
- `issue-close` refuses to invent a Why. With no evidence for a decision it leaves
  `> [TODO: confirm intent with a human]` rather than something plausible.

The narrative template and its supersede safety rules live in
[`skills/_shared/narrative-template.md`](skills/_shared/narrative-template.md). One rule matters
more than the rest: never select the page root or the whole body when updating — replacement is
scoped to a `## heading` and stops before the next one. That is the single failure here that
cannot be undone.

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
python3 tools/validate_skill.py plugins/elian-store/skills/implement
```

`brainstorm`, `fix`, `implement`, and `improve` share `tools/validate_skill.py` rather than
each carrying a copy of it.

## Release Boundary

This directory is the plugin bundle source of truth. The installed Claude plugin should always match the metadata in `plugins/elian-store/.claude-plugin/plugin.json` and the root marketplace entry.
