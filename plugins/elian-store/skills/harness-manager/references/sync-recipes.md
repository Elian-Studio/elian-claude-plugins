# Sync recipes — how to compare and how to reconcile each surface

Per shared surface: how to detect drift (Phase 2) and, once the user approves, how to apply the
fix without breaking the file or recreating the drift (Phase 4). Read before editing.

## General principles

- **Compare by intent, not by bytes.** Two rules worded differently can still be "in sync".
- **Back up first, validate after.** Every target lives outside git. Snapshot to
  `~/.claude/backups/harness-sync-<DATE>/`, edit, then re-parse the whole file to prove it's valid.
- **Prefer a pointer over a copy.** Duplicated full text drifts again. One canonical statement +
  a short "see X" on the other side stays consistent.

## Rules: `CLAUDE.md` ↔ `AGENTS.md` (+ `rules/default.rules`)

**Detect:** build a topic list from both files (e.g. communication-language, scope-discipline,
destructive-ops, supply-chain, testing, frontend, git). For each topic ask: does the other side
state it? does it *contradict*? Contradiction → ⚠️. One states it, other silent, and it's
universal intent → ➕. Codex-idiomatic (apply_patch/rg) → 🔒.

**Reconcile (➕, propagate a rule the user wants everywhere):**
- AGENTS.md is intentionally lean. Don't paste a whole CLAUDE.md section into it. Add a short,
  AGENTS-voiced line capturing the *behavior*, e.g.:

  ```
  ## Supply Chain
  - Do not install packages published within the last 7 days; report and pin an older version
    instead. Never disable lockfile/ignore-scripts policy to work around it.
  ```

- If the rule is long or already canonical in CLAUDE.md, prefer a pointer:

  ```
  > Package, commit, and destructive-op policy follows ~/.claude/CLAUDE.md as the source of truth.
  ```

  Establishing this pointer once is often the better fix than copying N rules — it makes CLAUDE.md
  canonical for both tools and kills future drift at the source.

**Reconcile (⚠️, diverged):** do not pick the winner. Present both statements + which one you'd
keep and why; the user chooses canonical, then you write that one into both (or pointer).

## MCP servers: `~/.claude.json` ↔ `~/.codex/config.toml`

**Detect:** list servers on each side, match by *service/URL* not name. Buckets: present both
(compare transport/args → ✅ or ⚠️), present one + clearly portable → ➕, single-tool runtime
(node_repl, magic, morphllm) → 🔒.

**Format translation (the fiddly part):**

Remote (URL) server — Claude JSON:
```json
"notion-work": { "type": "http", "url": "https://mcp.notion.com/mcp" }
```
…as Codex TOML:
```toml
[mcp_servers.notion]
url = "https://mcp.notion.com/mcp"
```

Local (command) server — Claude JSON:
```json
"playwright": { "command": "npx", "args": ["-y","@playwright/mcp"], "env": { "FOO": "bar" } }
```
…as Codex TOML:
```toml
[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp"]
startup_timeout_sec = 120

[mcp_servers.playwright.env]
FOO = "bar"
```

Reverse (TOML→JSON) is the mirror. After editing `~/.claude.json`, `json.load` the whole file;
after editing `config.toml`, load it with a TOML parser. A corrupt central config breaks the
tool's startup, so validation is non-optional.

**Auth does not travel with the definition — this is the gotcha that bites.** Copying a server
entry moves only the transport/command/args, never the credentials. An OAuth/HTTP server (notion,
figma) needs a fresh login on the other tool before it works; a keyed stdio server needs its API
key in `env`. And if the source side's `env` is *empty* (as Claude's `magic`/`morphllm` are), the
key lives outside the config and the entry is **not portable as-is** — copying it yields a dead
server. So for any auth-bearing server, "synced" = definition copied **plus** an explicit
"re-authenticate / add the API key on side X" note in the report; never report it as simply done.
This is frequently *why* a server present on one side was deliberately left off the other —
treat a one-sided auth-bearing server as "confirm intent" rather than an automatic ➕.

## Commands ↔ Prompts: `~/.claude/commands/` ↔ `~/.codex/prompts/`

**Detect:** list `.md` filenames on each side; a name on one and not the other → ➕ candidate.
**Reconcile:** copy the `.md` body across. Strip/adjust tool-specific frontmatter — a Codex
prompt is plain markdown; a Claude command may carry frontmatter (`description`, `argument-hint`).
Keep the instruction body identical; adapt only the wrapper.

## Skills: `~/.claude/skills/` ↔ `~/.codex/skills/`

**Detect (presence):** compare directory name sets, but resolve presence honestly first — Claude
also gets skills from *plugins*, so a name may be "present" without a folder in `~/.claude/skills/`
(check `~/.claude/plugins/**` and the loaded skill list). A raw `comm` of the two folders
over-reports Codex-only skills; verify each candidate against the plugin set before listing it as a
gap, or you'll emit false ➕.
**Detect (broken-port — cheap, do it):** for a skill that exists on both sides, grep the *ported*
copy for the other tool's idioms. A Codex skill that still contains `${CLAUDE_PLUGIN_ROOT}`, a
`/plugin:` namespace, or `Edit`/`Read`/`Write` tool names is a Claude skill copied without
adaptation and will break under Codex → flag 🛠️ "broken port" (a token-adaptation fix, counted
separately from ⚠️ diverged). This is a grep, not a body diff —
keep it that light; don't escalate to full content comparison unless the user asks.
**Reconcile:** presence drift is informational — list it, don't auto-copy skill folders. A
🛠️ broken port is a real fix the user may want; describe what tokens need adapting, but apply only
on request. Full content sync only when the user names a specific skill; then copy the folder and
adjust the other tool's idioms (tokens, namespaces, tool names, frontmatter), same as commands.
