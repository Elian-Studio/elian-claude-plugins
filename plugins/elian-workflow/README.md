# Elian Workflow

The development lifecycle as one plugin: which stage comes next, and which skill runs there.

Nineteen skills covering idea through recorded history, plus the 30 agents those skills
dispatch. The plugin knows *when* — the order of the stages. It does not define house style,
and the only thing it renders is delegated to the document skill it carries.

## Stages

| Stage | Skills |
|---|---|
| Idea | `brainstorm` |
| Spec / PRD | `intake-spec` |
| Issue | `issue-open` |
| Architecture | `design-feature`, `update-design` |
| Implementation | `implement`, `fix`, `improve` |
| Review | `review`, `persona-review`, `pr-review`, `respond-to-review` |
| Test / Verify | `spec-coverage`, `verify-implementation`, `verify-before-claiming` |
| Release | `pr-writer` |
| Record | `issue-close` |
| Cross-stage | `generate-teammate` (execution routing), `create-document` (render target) |

Agents: 14 domain specialists and 16 review personas, auto-discovered from `agents/`.

## Install one, not both

> **`elian-workflow` and `elian-store` overlap by 17 skills.** Install one of them.
>
> With both installed, every shared skill appears twice — `/elian-store:implement` and
> `/elian-workflow:implement` are the same skill from two plugins, and the 30 agents are
> likewise duplicated in the picker. Nothing breaks, but every choice is asked twice.

Pick by what you want:

- **`elian-workflow`** — the lifecycle, stage-ordered, including the issue-history bookends.
- **`elian-store`** — the original bundle. Same workflow skills plus the document and
  convention utilities (`document-writer`, `erd-preview`, `decision-dashboard`,
  `manage-skills`, `harness-manager`), without the Notion issue cycle.

```shell
/plugin install elian-workflow@elian
```

## Notion setup — for `issue-open` and `issue-close` only

Seventeen of the nineteen skills need no configuration. The two issue-cycle skills write to a
Notion workspace and do nothing until one is configured.

Nothing about any particular workspace is baked in. Every database id, property name, and
status value comes from a config file, resolved in this order, first match wins:

1. `$CLAUDE_PROJECT_DIR/.claude/notion-workspace.json` — per-repository override
2. `~/.claude/notion-workspace.json` — user default

You do not have to write it by hand. On first run, either skill enters setup: it asks which
Notion MCP server to use, searches for your task database, reads its **live** property names
and status options, proposes a mapping for you to correct, and writes the file after you
confirm. Re-run it any time with `--setup`.

Requirements: a Notion MCP server connected to Claude Code, and a database with one page per
issue. A second database for per-commit rows is optional — omit it and `issue-close` skips
the commit backfill.

Full schema and the setup procedure: [`skills/_shared/notion-workspace-config.md`](skills/_shared/notion-workspace-config.md).

## The issue cycle

Development work has three nested cycles, and each one wants a different record:

| Cycle | What it records |
|---|---|
| Commit | one audit row per commit |
| **Issue** | **the narrative — decisions, architecture, verification, remaining checks** |
| Day | context restore in the morning, a summary at night |

The commit and day levels are well served by existing tooling. The issue level is the one
that carries *why* a thing was built the way it was, and it is the one a diff can never
reconstruct.

```shell
/elian-workflow:issue-open KEY-123
# ... run the stages above ...
/elian-workflow:issue-close KEY-123
```

Both are `disable-model-invocation: true` — they write to a live workspace, so they run only
when you ask for them by name.

`issue-close` writes into the **body** of the issue page — the page a person opens when they
search the issue key. Someone reading it for the first time should be able to answer four
questions in about two minutes: what changed, why, how it was verified, and what is left.

The canonical template lives in
[`skills/_shared/narrative-template.md`](skills/_shared/narrative-template.md), along with the
supersede safety rules. One rule matters more than the rest:

> Never select the page root or the whole body when updating. Replacement is scoped to a
> `## heading` and stops before the next one.

That is the single failure here that cannot be undone. A hand-written section replaced in full
is gone, and nothing in Notion's history makes it cheap to recover.

`issue-close` also refuses to invent a Why. When the commits and PR carry no evidence for a
decision, it leaves `> [TODO: confirm intent with a human]` rather than filling the gap with
something plausible. A fabricated rationale is worse than an admitted one, because nobody
later knows to question it.

## What the issue skills will not do

- No git mutation. No branch create, switch, merge, push, or delete — not even the upstream
  fix `issue-open` recommends, which it prints for you to run.
- No Notion write without showing you the draft first.
- No rewrite after an issue is closed. The narrative freezes to append-only; `--no-freeze`
  overrides when you really mean it.
- `issue-close` is recording only. Whatever you use to merge or clean up the branch should run
  **after** it, because the commit range is its source and a cleaned-up branch takes that away.

## How this plugin is assembled

Two of the nineteen skills are hand-authored here; the rest are generated copies.

| Kind | Contents | Edit where |
|---|---|---|
| Native | `issue-open`, `issue-close`, `_shared/narrative-template.md`, `_shared/notion-workspace-config.md` | here |
| Generated | the other 17 skills, all 30 agents, `_shared/execution-strategy.md`, `_shared/review-severity.md` | `plugins/elian-store/`, then re-sync |

```shell
python3 tools/generate.py --sync      # refresh the generated copies
python3 scripts/validate_repository.py  # fails if a copy drifted from its source
```

The copies are committed rather than built at install time, so nothing stops someone editing
one directly — and that edit would be silently reverted by the next sync. The validator's
`composed-parity` check exists to fail first. `tools/clusters.json` declares which skills are
generated and which are native.

`create-document` is carried here rather than invoked across plugins because three skills
(`design-feature`, `update-design`, `generate-teammate`) execute its renderer scripts by path.
A plugin is copied as a unit at install time, so a path that leaves the plugin resolves in
this repository and breaks for installed users. The `plugin-self-containment` check enforces
that boundary.

## Codex

Not ported. `issue-open` and `issue-close` depend on a Notion MCP server, which is a
Claude-side integration. Recorded as a deliberate exception in the repository's
`docs/claude-codex-skill-parity.md`.

## Release boundary

`plugin.json.version` is the update cache key and wins over the marketplace entry, so
`plugins/elian-workflow/.claude-plugin/plugin.json` and the matching root marketplace entry
move together or installed users receive nothing. `scripts/validate_repository.py` enforces
that parity.
