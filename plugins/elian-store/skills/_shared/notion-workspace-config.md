# Notion workspace config — schema and first-run setup

`/issue-open` and `/issue-close` write to *your* Notion workspace. Nothing about that
workspace is baked into these skills: every database id, property name, and status value
is read from a local config file. That is what makes the plugin distributable — the
workspace is a local concern, the skill is shared.

## Location

Resolve in this order and use the first that exists:

1. `$CLAUDE_PROJECT_DIR/.claude/notion-workspace.json` — per-repository override
2. `~/.claude/notion-workspace.json` — user default

A per-repository file is useful when one machine works against two Notion workspaces
(for example a company workspace and a personal one). Most people only need the
user-level file.

## Schema

```json
{
  "mcpServer": "<your notion mcp server name, e.g. notion>",
  "dataSources": {
    "taskList": "<data source id of the database holding one page per issue>",
    "auditLog": "<data source id of the per-commit log database, optional>"
  },
  "properties": {
    "title": "<title property name>",
    "issueKey": "<text property holding the issue key, optional>",
    "status": "<status or select property name>",
    "startDate": "<date property name, optional>",
    "domain": "<multi-select property name, optional>"
  },
  "statusValues": {
    "inProgress": "<the value meaning work started>",
    "done": "<the value meaning work finished>"
  },
  "issueKeyPattern": "([A-Z]+-\\d+)",
  "baseBranches": ["develop", "main"]
}
```

| Field | Required | Notes |
|---|---|---|
| `mcpServer` | yes | The Notion MCP server name. Tools are called as `mcp__<mcpServer>__notion-*`. |
| `dataSources.taskList` | yes | The database whose **page body** holds the issue narrative. |
| `dataSources.auditLog` | no | Per-commit one-line rows. Omit it and `/issue-close` skips commit backfill. |
| `properties.*` | title/status required | Names are workspace-specific and may contain non-ASCII characters or control-character prefixes — always read them from the live database rather than guessing. |
| `statusValues.*` | yes | Must match existing options exactly; the API does not create new select options implicitly. |
| `issueKeyPattern` | no | Regex with one capture group, matched against the branch name. Defaults to `([A-Z]+-\d+)`. |
| `baseBranches` | no | Tried in order for `git merge-base`. Defaults to `["develop", "main"]`. |

## First-run setup

When no config file resolves, run setup instead of failing. Do not guess ids — discover them.

1. Tell the user what is about to happen and that the result is written to
   `~/.claude/notion-workspace.json` (or the project path, if they prefer).
2. Ask which Notion MCP server to use. Detect the candidates from the available
   `mcp__*__notion-search` tools rather than assuming a name.
3. Find the task database: run `notion-search` for a term the user supplies
   ("what do you call your task list?"), show the matches with their urls, and let
   them pick. Extract the data source id from the result.
4. Read the real schema: `notion-fetch` the database, then list its properties with
   their types. Map them to the schema keys above by asking the user to confirm the
   proposed mapping — propose by type (the single `title` property, the one `status`
   property, and so on) and let them correct it.
5. Read the actual status options from that property and ask which two mean
   "in progress" and "done". Never invent option values.
6. Optionally repeat steps 3–4 for the per-commit audit database. Skipping it is fine.
7. Show the assembled JSON, get confirmation, then write the file.

Setup is idempotent — rerunning it overwrites the file after showing a diff of what
changes. `/issue-open --setup` and `/issue-close --setup` force it explicitly.

## Reading the config in a skill

Read the file with the `Read` tool and use the values directly. Two rules matter:

- **Never fall back to a hard-coded id.** If a required key is missing, run setup for
  that key. A wrong database id writes real content into the wrong place.
- **Pass property names through verbatim.** Some Notion property names carry invisible
  prefix characters, and a name that looks equivalent will fail with a 400. Copy the
  string from the config; do not normalize, trim, or re-type it.

Dates use Notion's flat extended form, where `<name>` is the configured property name:

```
"date:<name>:start": "YYYY-MM-DD"
"date:<name>:is_datetime": 0
```

`multi_select` and `relation` values are passed as JSON array strings, not
comma-separated text.
