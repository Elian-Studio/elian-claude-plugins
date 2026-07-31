---
name: issue-close
description: "Record a finished issue's development history to Notion: interview for the design decisions and dropped alternatives that code cannot show, upsert a readable narrative into the issue page body, backfill commits missing from the audit log, and transition the task to done. Use when a piece of work is finished and the history should be captured — 'this issue is done', 'wrap up this task', 'close out KEY-123', 'finish this', 'record what we decided', 'log this to Notion', or right after a PR is opened or merged. Recording only: it never merges, pushes, or deletes a branch. Run it while the branch still exists, because the commit range is its source. Not a daily wrap-up and not a per-commit logger."
when_to_use: "A single issue or task is finished and its decisions, architecture, verification, and remaining checks should be written down as durable history. Also use when an issue page body is stale and needs to be superseded with what actually happened. Do NOT use for per-commit logging, for end-of-day summaries across many issues, or for deciding what to do with the git branch."
argument-hint: "[ISSUE-KEY] [--dry-run] [--no-freeze] [--setup]"
allowed-tools: Read, Write, Grep, Glob, AskUserQuestion, Bash(git log*), Bash(git diff*), Bash(git branch --show-current), Bash(git merge-base*), Bash(gh pr list*), Bash(glab mr list*), Bash(python3 *scripts/render_before_after.py*), Bash(mkdir -p*)
disable-model-invocation: true
---

# /issue-close — record a finished issue

Development work has three nested cycles, and each one owns a different record:

| Cycle | Records |
|---|---|
| Commit | one audit row per commit |
| **Issue** | **`/issue-open` → `/issue-close` — the narrative: decisions, architecture, checks** |
| Day | context restore / daily summary |

This skill owns the issue cycle's closing record. It is the **only** writer of the issue
narrative — see [narrative-template.md](../_shared/narrative-template.md) for the template and
the supersede safety rules, and [notion-workspace-config.md](../_shared/notion-workspace-config.md)
for where database ids and property names come from.

**Recording only.** This skill never merges, pushes, rebases, or deletes anything. Deciding
what happens to the branch is a separate concern, and whichever tool you use for it should
run *after* this one — once a branch is merged and cleaned up, the commit range that feeds
§Changes and the audit backfill is gone.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `ISSUE-KEY` | Target issue | parsed from the branch name |
| `--dry-run` | Print the draft, write nothing | false |
| `--no-freeze` | Allow section rewrite even when status is already done | false |
| `--setup` | Re-run workspace config setup | false |

## Step 0: Load workspace config

Resolve the config per [notion-workspace-config.md](../_shared/notion-workspace-config.md).
If it is missing, run first-run setup — discover the databases and read their real property
names. Never substitute a hard-coded id; writing to the wrong database is not recoverable
by the user.

Everything below writes `config.<key>` where a workspace-specific value belongs.

## Step 1: Identify the issue and its commits

Parse the issue key from `--` arguments, else from the branch name using
`config.issueKeyPattern`.

```bash
BRANCH=$(git branch --show-current)
for b in <config.baseBranches>; do
  BASE=$(git merge-base HEAD "origin/$b" 2>/dev/null) && break
done
git log --format="%h|%s|%ad" --date=short "$BASE"..HEAD
git diff --stat "$BASE"..HEAD
```

Pull the PR if one exists, and continue without it if not — the branch may be local only:

```bash
glab mr list --source-branch "$BRANCH" 2>/dev/null || gh pr list --head "$BRANCH" 2>/dev/null || true
```

**An empty commit range means the branch was already merged and cleaned up.** Recover the
range from the merge commit before giving up:

```bash
git log --format="%h|%s|%ad" --date=short --grep="<ISSUE-KEY>" --all
```

If recovery also fails, say so and collect §Changes from the user by hand. **Never write an
empty narrative silently** — a blank history looks identical to work that was never done.

Then find the issue page:

```
Tool: mcp__<config.mcpServer>__notion-search
  query: "<ISSUE-KEY>"
  data_source_url: "collection://<config.dataSources.taskList>"
```

`notion-fetch` the resulting page and note two things: whether the body contains the
`## Summary (TL;DR)` marker (seed vs update), and whether the status property already holds
`config.statusValues.done` (freeze vs normal supersede).

> Notion MCP tools may be deferred — load them with `ToolSearch` before calling.
> Fetch on the main thread; sub-agents cannot reach the Notion MCP session.

## Step 2: Draft what can be derived

Fill the template sections that have a mechanical source:

| Section | Source |
|---|---|
| §1 Metadata | issue key, status, domain, first/last commit dates, PR numbers |
| §2 Summary | commit subjects plus PR description |
| §3 Background | problem statement found in commit bodies or the PR description |
| §6 Changes | curated prose grouped by area — **not** a commit list |
| §7 Verification | test commits, CI results, measurements present in commit messages |
| §10 Commit log | audit database link filtered by branch |

**Leave §4 Why, §5 Alternatives, and §9 remaining checks empty for now.** A diff shows what
changed but never why that option beat the others, and inferring intent from a diff produces
confident fiction. Step 3 asks instead.

Add a Mermaid diagram to §4 or §6 when the flow, structure, or state change is non-obvious.

## Step 3: Interview — one `AskUserQuestion`, three questions

Anchor the questions on the commit list from Step 1. Asking "were there any important
decisions?" against a blank page produces nothing; asking "in these commits, which one
carried a decision?" produces real answers, because recognition beats recall.

1. **Key design decision** — which commit, what was chosen, why it beat the alternatives,
   and what the known downside is.
2. **Dropped alternatives** — what was considered and rejected, and why. If there were none,
   §5 is omitted entirely rather than padded.
3. **Remaining checks** — follow-up work, accepted debt, what to watch in production.

Anything left unanswered becomes a `> [TODO: confirm intent with a human]` callout. Do not
fabricate, and do not leave the section blank — a marked gap invites a fix, a blank one hides it.

## Step 4: Show the draft

Print the assembled narrative in full plus a summary of the writes, then ask for
confirmation. Stop here on `--dry-run`.

```
=== /issue-close draft — KEY-123 ===

Issue      KEY-123 <title>
Branch     <branch>
Commits    12 (2026-07-14 ~ 2026-07-28)
Page       <url>
Status     <current> → <config.statusValues.done>
Narrative  seed | supersede §4, §5, §9

<full narrative markdown>

Writes:
  1. Issue page body — <seed | supersede §4·§5·§9>
  2. Audit backfill — N commits missing
  3. Status → <config.statusValues.done>
  4. Before/after HTML

Proceed? (Y / N: pick items to revise)
```

## Step 5: Write to Notion

### 5-1. Narrative upsert

Follow the supersede safety rules in
[narrative-template.md](../_shared/narrative-template.md) exactly. The rule that matters most:
**never select the page root or the whole body.** Section-scoped replacement anchored on
`## headings`, with `insert_content_after` as the fallback when an anchor is missing.

If status is already done, freeze: append one `> Final note — YYYY-MM-DD` line under §2
instead of rewriting. `--no-freeze` overrides.

### 5-2. Audit backfill

Skip entirely when `config.dataSources.auditLog` is unset.

For each commit in the range, search the audit database for its hash and add a row only if
it is absent. Keep the row body empty — the readable version lives in the narrative, and
duplicating it in every row is what made these logs unreadable in the first place.

> Append to the configured audit database. **Do not create a per-issue copy of it on the
> issue page** — that fragments the log into as many databases as there are issues, and the
> cross-issue filters that make it useful stop working.

### 5-3. Status transition

```
Tool: mcp__<config.mcpServer>__notion-update-page
  page_id: "<page_id>"
  properties:
    "<config.properties.status>": "<config.statusValues.done>"
```

Copy the property name from the config verbatim — some workspaces carry invisible prefix
characters in property names, and a retyped equivalent fails with a 400.

### 5-4. Before/after viewer

```bash
# Claude Code sets CLAUDE_SKILL_DIR (direct call) or CLAUDE_PLUGIN_ROOT (internal call).
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/issue-close}}"
mkdir -p claudedocs/<issue>-before-after
python3 "${SKILL_DIR}/scripts/render_before_after.py" \
  --before <pre-write body snapshot .md|.html> \
  --after  <the body just written .md> \
  --title  "<KEY-123 — title>" \
  --out    claudedocs/<issue>-before-after/index.html
```

Use the Step 1 `notion-fetch` result (the body before writing) as `--before`, saved to a temp
file. On a first seed there is no before — confirm with the user and skip.

## Step 6: Report

```
=== /issue-close done — KEY-123 ===

Narrative   <seeded | superseded §4·§5·§9> → <url>
Audit       N rows added (M duplicates skipped)
Status      <old> → <config.statusValues.done> (append-only from here)
HTML        claudedocs/KEY-123-before-after/index.html
```

## Error handling

| Situation | Handling |
|---|---|
| Issue key not parseable | Show the expected branch pattern from `config.issueKeyPattern`, ask for the key |
| No `merge-base` against any base branch | Ask which branch this split from, retry with it |
| Empty commit range | Recover via `--grep=<key> --all`; if that fails, collect §Changes by hand. Never write a blank narrative |
| No page in the task database | Offer to create it; if declined, skip 5-1/5-3 and do the backfill only |
| `notion-fetch` fails | Retry once, then **save the draft to `claudedocs/<issue>-close-draft.md` and stop** — interview answers must not be lost |
| Status already done | Freeze rules apply; `--no-freeze` overrides |
| Backfill partially fails | Keep the successful rows, print the failed hashes for individual retry |
| Config missing or incomplete | Run setup for the missing keys. Never guess an id |

## Notes

- Every Notion write passes the Step 4 confirmation. Nothing is automatic.
- No git mutation: no branch create, switch, merge, push, or delete.
- Per-commit logging and end-of-day summaries are different cycles and different tools.
