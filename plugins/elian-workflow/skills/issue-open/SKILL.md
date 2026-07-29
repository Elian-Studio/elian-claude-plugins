---
name: issue-open
description: "Start an issue cleanly and set it up to be recorded later: verify the branch upstream points at itself, move the task to in-progress with a start date, check whether design documents and open decisions exist, and seed the issue page body with the metadata and background that are only clear at kickoff. Use when picking up a piece of work — 'starting KEY-123', 'begin this issue', 'kicking off this task', 'I'm picking this up'. Never creates, switches, or deletes a branch. Closing is /issue-close."
when_to_use: "Work on a single issue is about to begin on an existing branch, and the task should be marked in-progress with its background captured while it is still fresh. Do NOT use for starting a workday across many issues, for creating branches, or for requirements gathering."
argument-hint: "[ISSUE-KEY] [--dry-run] [--setup]"
allowed-tools: Read, Write, Grep, Glob, AskUserQuestion, Bash(git branch --show-current), Bash(git config --get*)
disable-model-invocation: true
---

# /issue-open — start an issue

The opening bookend to [`/issue-close`](../issue-close/SKILL.md). Its job is to leave the
issue in a state where the closing record can actually be written.

Some things are only clear at kickoff — why this work is needed, and what was agreed to
build. By the time the work is done, that context has faded into the diff. So §Background
gets seeded here, not at the end.

Template and supersede rules: [narrative-template.md](../_shared/narrative-template.md).
Database ids and property names: [notion-workspace-config.md](../_shared/notion-workspace-config.md).

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `ISSUE-KEY` | Target issue | parsed from the branch name |
| `--dry-run` | Print what would be written, write nothing | false |
| `--setup` | Re-run workspace config setup | false |

## Step 0: Load workspace config

Resolve the config per [notion-workspace-config.md](../_shared/notion-workspace-config.md),
running first-run setup when it is absent. Never substitute a hard-coded id.

## Step 1: Issue key and branch upstream

Parse the issue key from the arguments, else from the branch name using
`config.issueKeyPattern`.

Then check the branch upstream, because getting this wrong is quietly destructive:

```bash
B=$(git branch --show-current)
git config --get "branch.$B.merge"
```

It must be `refs/heads/$B`. When it points at a base branch instead (`refs/heads/develop`,
`refs/heads/main`), `git pull` drags the base into the feature branch and `git push` risks
overwriting the base. Worktrees and branch-creation tooling inherit the base's upstream
silently, so this is worth checking every time rather than assuming.

If it is wrong, **warn and show the fix — do not run it without approval**:

```bash
git config branch.$B.merge refs/heads/$B
```

Stop with an explanation if the current branch is a base branch. This skill does not create
or switch branches; changing repository state the user did not ask for is out of scope even
when the intent seems obvious.

## Step 2: Move the task to in-progress

```
Tool: mcp__<config.mcpServer>__notion-search
  query: "<ISSUE-KEY>"
  data_source_url: "collection://<config.dataSources.taskList>"
```

**Row found** — set status and start date:

```
Tool: mcp__<config.mcpServer>__notion-update-page
  page_id: "<page_id>"
  properties:
    "<config.properties.status>": "<config.statusValues.inProgress>"
    "date:<config.properties.startDate>:start": "<YYYY-MM-DD>"
    "date:<config.properties.startDate>:is_datetime": 0
```

Omit the date pair when `config.properties.startDate` is unset.

**No row** — offer to create one, filling title, issue key, status, and start date from the
config's property names. If the user declines, continue with Steps 3–4.

Copy property names from the config verbatim; do not normalize them.

## Step 3: Check design assets

Look for existing design rationale. This is not a gate — it tells the user what
`/issue-close` will have to work with, and gives `/issue-close` a source for §4.

```
Glob: **/docs/**/<ISSUE-KEY>/**/*.md
Glob: **/claudedocs/**/<ISSUE-KEY>/**/*.md
Grep: "#\d{1,4}"   (open decision numbers, in any PENDING/decisions file found)
```

- Documents found → print the paths and use them to seed §Background.
- Nothing found → say so once and move on. Do not require design docs; plenty of valid work
  does not have them.
- Open decision numbers found → print them. They are what commit messages reference later,
  which is how §References gets populated at close.

## Step 4: Seed the issue page body

Only when the body has no `## Summary (TL;DR)` marker. If the marker is present, something
already seeded it — leave it alone rather than overwriting.

Write §1 Metadata and §3 Background with what is known now, and leave the rest as explicit
placeholders so `/issue-close` has anchors to supersede:

```markdown
## Metadata
| Issue | Status | Domain | Period | PR |
|-------|--------|--------|--------|-----|
| [KEY-123](tracker-link) | In progress | <domain> | <start date> ~ | — |

## Summary (TL;DR)
> [TODO: written by /issue-close]

## Background / Why
<Why this work is needed, as understood now. Link the design doc or tracker item rather
than restating it.>

## Decisions and approach
> [TODO: filled from the /issue-close interview]

## Changes
> [TODO: written by /issue-close from commits and PRs]

## Verification
> [TODO: written by /issue-close]

## Outcome / trade-offs
> [TODO: filled from the /issue-close interview]

## References
- Tracker: [KEY-123](...)
```

If there is no basis for §Background, ask one question: "why is this work needed?" If the
user does not answer, leave `> [TODO: confirm intent with a human]`. Do not invent a
motivation — a plausible fabricated Why is worse than an admitted gap, because nobody
later knows to question it.

`--dry-run` prints the seed and stops.

## Step 5: Report

```
=== /issue-open done — KEY-123 ===

Branch     <branch> (upstream OK | MISMATCH — fix shown above)
Status     <old> → <config.statusValues.inProgress>, start <YYYY-MM-DD>
Design     <paths> | none found
Decisions  #110, #111 | none
Body       seeded | already present — skipped

When the work is done: /issue-close KEY-123
```

## Error handling

| Situation | Handling |
|---|---|
| Issue key not parseable | Show the expected pattern from `config.issueKeyPattern`, ask for the key |
| Upstream points at a base branch | Warn, print the fix, **do not run it without approval** |
| On a base branch | Explain and stop. Do not create a branch |
| No row in the task database | Offer to create one; if declined, do Steps 3–4 only |
| Body already has the marker | Skip seeding, do not overwrite |
| Config missing or incomplete | Run setup for the missing keys. Never guess an id |

## Notes

- Notion writes are confirmed before they happen.
- No branch create, switch, or delete under any circumstance.
- Starting a workday across many issues is a different cycle and a different tool.
