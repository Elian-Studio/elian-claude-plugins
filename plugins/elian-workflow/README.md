# Elian Workflow

Issue-cycle bookends that record engineering work history to Notion.

Development work has three nested cycles, and each one wants a different record:

| Cycle | What it records |
|---|---|
| Commit | one audit row per commit |
| **Issue** | **the narrative — decisions, architecture, verification, remaining checks** |
| Day | context restore in the morning, a summary at night |

The commit and day levels are well served by existing tooling. The issue level is the one
that carries *why* a thing was built the way it was, and it is the one a diff can never
reconstruct. That is what this plugin writes down.

## Skills

| Skill | When | What it does |
|---|---|---|
| `issue-open` | picking up a piece of work | Verifies the branch upstream, moves the task to in-progress with a start date, reports whether design documents and open decisions exist, and seeds the issue page with the background that is only clear at kickoff. |
| `issue-close` | the work is finished | Interviews against the commit list for the decisions and dropped alternatives, upserts a readable narrative into the issue page body, backfills commits missing from the audit log, transitions status, and renders a before/after HTML viewer. |

```shell
/elian-workflow:issue-open KEY-123
# ... build the thing ...
/elian-workflow:issue-close KEY-123
```

Both are `disable-model-invocation: true` — they write to a live workspace, so they run only
when you ask for them by name.

## Setup

Nothing about any particular Notion workspace is baked into these skills. That is deliberate:
the workspace is a local concern, the skill is shared. Every database id, property name, and
status value comes from a config file.

Resolved in this order, first match wins:

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

## The narrative format

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

## What these skills will not do

- No git mutation. No branch create, switch, merge, push, or delete — not even the upstream
  fix `issue-open` recommends, which it prints for you to run.
- No Notion write without showing you the draft first.
- No rewrite after an issue is closed. The narrative freezes to append-only; `--no-freeze`
  overrides when you really mean it.
- `issue-close` is recording only. Whatever you use to merge or clean up the branch should run
  **after** it, because the commit range is its source and a cleaned-up branch takes that away.

## Codex

Not ported. Both skills depend on a Notion MCP server, which is a Claude-side integration.
Recorded as a deliberate exception in
[`docs/claude-codex-skill-parity.md`](../../docs/claude-codex-skill-parity.md).

## Release boundary

This directory is the plugin source of truth. The installed plugin should always match
`plugins/elian-workflow/.claude-plugin/plugin.json` and the matching root marketplace entry —
`plugin.json.version` is the update cache key, so the two move together or installed users
receive nothing. `scripts/validate_repository.py` enforces that parity.
