# Harness map — where each shared surface lives (global scope)

Resolve these before scanning. Paths are real as of 2026-06-07 on this machine; **verify each
still exists** before reading — report a moved path, not a false "missing".

## Table of contents
- [Behavioral rules](#behavioral-rules)
- [MCP servers](#mcp-servers)
- [Commands ↔ Prompts](#commands--prompts)
- [Skills](#skills)
- [Tool-specific — classify, never sync](#tool-specific--classify-never-sync)

## Behavioral rules

| | Claude Code | Codex |
|---|---|---|
| Primary | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` |
| Secondary | — | `~/.codex/rules/default.rules` |

**Gotchas:**
- Codex has **two** rule surfaces (`AGENTS.md` + `rules/default.rules`). Read both; a rule may
  live in either.
- The global `~/.codex/AGENTS.md` is currently **standalone** — it does *not* point at
  `~/.claude/CLAUDE.md`. So at global scope there is no pointer convention yet; the two have
  drifted independently.
- `CLAUDE.md` is large and topic-sectioned (Principles, Constraint Registry, Supply Chain, TDD,
  Pre-Commit, Destructive Actions, …). `AGENTS.md` is lean prose (Communication, Work Style,
  File/Command Rules, Verification, Frontend Defaults, Harness Preferences, …). They cover
  overlapping *topics* with different structure — compare by topic/intent, not line-by-line.

**Known real drift to expect (confirm live, don't trust this list blindly):**
- In CLAUDE.md, absent in AGENTS.md → 7-day package-age / supply-chain policy, explicit TDD
  "failing test first", no-TODO/no-stub, Constraint Registry. These read as universal intent → ➕.
  The supply-chain rule is machine-enforced — `~/.npmrc` carries `min-release-age` / `ignore-scripts`
  — so Codex hits the same wall; cite that enforcement as evidence when proposing the ➕.
- In AGENTS.md, absent in CLAUDE.md → `apply_patch`, `rg`-first, lucide/frontend defaults. The
  first two are Codex-idiomatic (🔒); frontend defaults may be shareable (judge).

## MCP servers

| | Location | Format |
|---|---|---|
| Claude Code | `~/.claude.json` → top-level `mcpServers` | JSON |
| Codex | `~/.codex/config.toml` → `[mcp_servers.<name>]` | TOML |

**Gotchas:**
- Claude MCP is in **`~/.claude.json`**, NOT `~/.claude/settings.json` (its `mcpServers` is `{}`).
  Don't report "Claude has no MCP" off settings.json.
- `~/.claude.json` also holds per-project `mcpServers` (14 projects). Global sync compares only
  the top-level block; ignore project blocks (out of scope).
- Server *names* differ across tools for the same service (Claude `notion-work`/`notion-private`
  vs Codex `notion`). Match by target service/URL, not by name.
- Some servers are inherently single-tool (Codex `node_repl` points at `Codex.app` resources;
  Claude `morphllm`/`magic` are Claude-plugin MCPs). Those are 🔒, not ➕.

## Commands ↔ Prompts

| | Location | Format |
|---|---|---|
| Claude Code | `~/.claude/commands/*.md` | Markdown (+ optional frontmatter) |
| Codex | `~/.codex/prompts/*.md` | Markdown |

**Gotchas:**
- A Claude global slash-command ≈ a Codex prompt — both are reusable `.md` instructions invoked
  by name. They map cleanly enough to sync content, but invocation differs.
- Many "commands" the user relies on are actually *plugin/skill* slash-commands, not files in
  `~/.claude/commands/`. Only the loose `.md` files here are in scope for this surface.

## Skills

| | Location |
|---|---|
| Claude Code | `~/.claude/skills/` (+ installed plugins) |
| Codex | `~/.codex/skills/` (legacy, still loaded) **and** `.agents/skills/` (repo) / `$HOME/.agents/skills` (user) / `/etc/codex/skills` (admin) — the Agent Skills open standard |

**Gotchas:**
- **Format has converged — both tools implement the same `SKILL.md` Agent Skills standard**
  (originally authored by Anthropic, now an open standard at agentskills.io). Required frontmatter
  is `name` + `description` on both sides. Each tool only *extends* it: Claude via extra top-level
  frontmatter keys (`disable-model-invocation`, `user-invocable`, `allowed-tools`), Codex via a
  separate `agents/openai.yaml`. Empirically verified (Codex CLI 0.139): Codex **loads a SKILL.md
  carrying Claude-only frontmatter keys without error** — it ignores their semantics but does not
  choke. So one canonical `SKILL.md` can feed both tools; the only blocker is that neither tool
  reads the other's directory, so bridge it with a copy/symlink. This makes the
  `Commands ↔ Prompts` surface above partly legacy: the modern Codex counterpart of a Claude skill
  is a Codex *skill* (`.agents/skills/<name>/SKILL.md` or `~/.codex/skills/<name>/SKILL.md`), not a
  `prompts/*.md` file.
- Codex reads `~/.codex/skills/` **and** `.agents/skills/`; do not assume only one. Verify which a
  given machine actually populates before reporting a Codex-only gap.
- Counts are lopsided (Claude ≫ Codex) and many names overlap (`commit`, `fix`, `implement`,
  `review`, `brainstorm`, `decision-dashboard`, `design-ui`, `deep-interview`,
  `para-memory-files`, …). Plus Claude loads skills from installed *plugins*, so a skill can be
  "present" via a plugin without a folder in `~/.claude/skills/`.
- Report **presence** drift (which skill names exist on which side) — but verify each Codex-only
  candidate against the plugin set first; a raw folder `comm` over-reports gaps. Add one grep-level
  **broken-port** check: a Codex skill still carrying Claude-only tokens (`${CLAUDE_PLUGIN_ROOT}`,
  `/plugin:` namespaces, `Edit`/`Read`/`Write` tool names) is a bad paste → 🛠️ (broken port,
  counted separately from ⚠️ diverged). Full body diff only
  on explicit request.

## Tool-specific — classify, never sync

These have no clean counterpart in the other tool. Mark 🔒 and leave them. Listing them here so
you recognize them fast and don't mistake them for ➕ gaps.

| Claude Code only | Codex only |
|---|---|
| `settings.json` → `hooks` (SessionStart/PostToolUse/Notification) | `config.toml` sandbox / `trust_level` per project |
| `settings.json` → `permissions.allow` (~123 entries) | `[features]`, `[memories]`, `notify`, `personality` |
| `enabledPlugins` (~19) / `extraKnownMarketplaces` | `[plugins.*]` (openai runtime), `[marketplaces.*]` |
| `statusLine`, model/effort, `skipDangerousModePermissionPrompt` | `model_reasoning_effort`, `[otel]`, `[desktop]`, `[tui]` |
| `apply_patch`/`rg` are Codex idioms — Claude has its own Edit/Grep tools | `apply_patch`, `rg`-first (file/command idioms) |
