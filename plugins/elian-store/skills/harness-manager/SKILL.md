---
name: harness-manager
description: >-
  Detect and reconcile drift between the Codex and Claude Code GLOBAL harnesses — the
  behavioral rules (~/.claude/CLAUDE.md ↔ ~/.codex/AGENTS.md), MCP servers, custom
  commands/prompts, and skills that should behave consistently across both assistants.
  Runs scan → drift report (HTML) → user approval → backed-up edits. Reach for this whenever
  the user says "harness sync", "reconcile Codex and Claude Code rules", "check AGENTS.md vs
  CLAUDE.md drift", "align MCP servers across both assistants", "make both assistants' settings
  and rules match", or just
  edited one tool's global config and wants the other to match — even when they don't say the
  word "harness", if the concern is "the two tools disagree", this is the skill. It is NOT
  harness-legacy-scan (cruft audit) or harness-diet (cruft removal); those trim a single
  harness, this one keeps two harnesses consistent. Global scope only (~/.claude, ~/.codex);
  project-level AGENTS.md / .claude are out of scope.
---

# harness-manager

Keep the **Codex** and **Claude Code** global harnesses consistent. The pain this solves: a
rule, an MCP server, or a command lives in one tool's config but not the other — or the two
have quietly diverged — so the two assistants behave differently for the same task, and you
don't find out until one of them does the wrong thing. This skill finds those gaps, shows
them to you, and (after you approve) reconciles them.

## Scope

**In:** the *global* harness of both tools and only the surfaces that are genuinely shared.

| Shared surface | Claude Code | Codex |
|---|---|---|
| Behavioral rules | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` (+ `~/.codex/rules/default.rules`) |
| MCP servers | `~/.claude.json` → `mcpServers` | `~/.codex/config.toml` → `[mcp_servers.*]` |
| Commands ↔ Prompts | `~/.claude/commands/*.md` | `~/.codex/prompts/*.md` |
| Skills | `~/.claude/skills/` | `~/.codex/skills/` |

**Out:** project-level `AGENTS.md` / `.claude/` (the user scoped this to global). Tool-specific
machinery that has no meaningful counterpart in the other tool — classify it, never sync it
(see *Drift classification* below). Cruft removal within one tool — that's `harness-diet`.

Exact paths, gotchas, and the per-machine inventory live in `references/harness-map.md`. Read it
first — it records non-obvious facts (e.g. Claude MCP is in `~/.claude.json`, **not**
`settings.json`; Codex has *two* rule surfaces). Verify each path still exists before reading;
don't assume.

## Workflow: scan → report → approve → edit

Four phases. Phases 1–3 are read-only and safe to run anytime. Phase 4 mutates real files and
only happens after the user approves specific items.

### Phase 1 — Locate & read (read-only)

Resolve every file pair from `references/harness-map.md` and read both sides for each shared
surface. If a path has moved, find the real one rather than reporting a false "missing".

### Phase 2 — Classify drift

For each item (a rule/topic, an MCP server, a command/prompt, a skill) decide which bucket it
falls in. This classification *is* the skill — the rest is plumbing.

| Mark | Bucket | Meaning |
|---|---|---|
| ✅ | In sync | Equivalent on both sides. Nothing to do. |
| 🔗 | Delegated | One side intentionally points to the other as the source of truth (pointer pattern). **Not drift** — preserve it. |
| ⚠️ | Diverged | Both sides define it but they contradict or materially differ. This is where the two assistants actively disagree — the fix is a *which-side-is-canonical* decision. |
| ➕ | Missing | Present on one side, absent on the other, **and** the kind of thing the user plainly wants everywhere. Candidate to propagate. Carries a grade — see below. |
| 🛠️ | Broken port | Exists on both sides but the *ported* copy still carries the other tool's idioms, so it fails at runtime (e.g. a Codex skill with `${CLAUDE_PLUGIN_ROOT}`). The fix is token-adaptation, not a canonical decision — so it is **not** ⚠️. |
| 🔒 | Tool-specific | Only meaningful in one tool. **Not drift** — never sync. |

**Two distinctions the report must keep visible** (they were collapsed in early runs and made the counts unreadable):

- **⚠️ vs 🛠️ are different actions.** ⚠️ asks "which tool wins?"; 🛠️ asks "adapt these tokens." Never fold a broken port into ⚠️ — they go in different rows and count separately.
- **➕ is graded required vs optional.** Mark a ➕ **required** when it's machine-enforced or plainly universal (supply-chain 7-day, no-TODO, destructive-op confirmation); **optional** when it's a preference one could reasonably leave per-tool (a soft TDD nudge, frontend-aesthetic defaults). The summary must show required ➕ separately so the must-do gaps don't hide behind the nice-to-haves.

The only hard judgment is **Missing vs Tool-specific**, and getting it right is the whole point.
A rule absent on one side is *not* automatically a gap:

- `apply_patch`, `rg`-first, `git status` separation → Codex-idiomatic. Leave them.
- Hooks, `permissions.allow`, sandbox `trust_level`, plugin enablement → tool-specific machinery
  with no cross-mapping. Leave them.
- 7-day package-age / supply-chain policy, "confirm before destructive ops", no-TODO, Korean
  default, "read before changing", TDD-first → universal *intent*. If one tool states it and the
  other is silent, that's a real gap worth propagating.

A fast tie-breaker for ➕ vs 🔒: **is the rule backed by machine-level enforcement that hits both
tools the same way?** If the trigger is a shared mechanism — `~/.npmrc` `min-release-age`, a git
hook, the OS sandbox, a lockfile — then the other tool runs into the exact same wall, so the rule
is almost certainly universal intent → ➕. Check for that enforcement and cite it as the evidence
(e.g. "`~/.npmrc` enforces `min-release-age=7`, so Codex hits it too"); it's a stronger argument
than the prose alone.

Lead with the reasoning ("this is universal intent / this is tool-idiomatic"), not a keyword
match. When you're unsure, mark it ⚠️/➕ and let the user decide — under-reporting a real
divergence is worse than asking.

### Phase 3 — Drift report (HTML, no edits yet)

Write `claudedocs/harness-sync/REPORT-<YYYY-MM-DD>.html` (plus a `.md` mirror for grep/diff).
One section per shared surface; one row per item with: classification mark, current state on
*each* side, and a recommended reconciliation (a direction, or "leave"). Open it in the browser.

**Format rules (so the summary stays actionable):**
- Put ⚠️ (diverged) and 🛠️ (broken port) in **separate rows and separate summary counts** — they
  are different actions. A line like "⚠️ 5" that secretly mixes one diverged rule with four broken
  ports is unreadable; show "⚠️ diverged: 1 · 🛠️ broken port: 4" instead.
- Tag each ➕ as **required** or **optional** and surface the required count on its own in the
  summary (e.g. "➕ 8 — required 4 / optional 4"), so the must-do gaps don't hide behind the
  nice-to-haves. Order the priority list by the required ➕ and 🛠️ first.

This is decision content, so follow the house rules: it's an HTML artifact the user clicks
through — not a wall of chat markdown — and the `.content`/`main` carries no `max-width` cap
(the comparison tables need the width). If there are 3+ items that need a real which-side-wins
call, offer to escalate to `/decision-dashboard` rather than reinventing decision cards here.

Recommend a direction per ⚠️/➕ item but **do not pick the winner for the user** on diverged
rules — surface both and your reasoning; the user owns "which tool is canonical."

### Phase 4 — Approve & edit (only after the user picks items + directions)

Before touching anything, **back up every target file**. These files are not under git — a bad
edit is unrecoverable. Snapshot to `~/.claude/backups/harness-sync-<YYYY-MM-DD>/` and tell the
user the one-line restore command. (This is the lesson the prior harness-diet run paid for.)

Then apply only the approved items, surgically:

- Respect each file's format. Translate MCP entries JSON↔TOML; write rules in AGENTS.md's lean
  prose rather than pasting CLAUDE.md's full section.
- Edit `~/.claude.json` (large, central) and `config.toml` with extra care — change only the
  target block, then re-parse the whole file (`json.load` / a TOML load) to prove it's still
  valid. These are system-boundary config files; validate after writing.
- Don't recreate the drift you just fixed. If you propagate a rule, prefer the pointer pattern
  (one canonical statement + a short "see X" on the other side) over duplicating full text that
  will diverge again later. See `references/sync-recipes.md`.

Report what changed, per file, with the restore command.

## What not to do

- **Don't sync tool-specific config.** Forcing Claude hooks into Codex, or Codex `trust_level`
  into Claude permissions, produces broken config and a worse harness, not a synced one.
- **Don't auto-resolve diverged rules.** The user decides which tool is canonical.
- **Skills surface: presence drift by default, plus one cheap content check — never a full diff.**
  Report which skill names exist on which side, but first verify presence honestly: Claude also
  loads skills from *plugins*, so a name can be "present" without a folder in `~/.claude/skills/` —
  check the plugin paths before calling something a Codex-only gap, or you'll raise false ➕ (the
  real Codex-only set is much smaller than a raw folder diff suggests). On top of presence, do one
  grep-level **broken-port** check: a skill copied to one tool that still carries the *other* tool's
  idioms — a Codex skill containing `${CLAUDE_PLUGIN_ROOT}`, a `/plugin:` namespace, or `Edit`/
  `Read`/`Write` tool names — is a Claude skill pasted without adaptation and will fail at runtime;
  mark it 🛠️ (broken port — a token-adaptation fix, counted separately from ⚠️ diverged). Full
  body sync only when the user names a specific skill.
- **Don't touch project scope.** Global only.
- **Don't edit without a backup.** No exceptions for "small" edits to these files.

## References

- `references/harness-map.md` — exact paths, per-tool gotchas, and the current per-machine
  inventory of what's shared vs tool-specific. Read before Phase 1.
- `references/sync-recipes.md` — per-surface comparison method and concrete format-translation
  recipes (JSON↔TOML MCP, rule propagation via pointer, command↔prompt). Read before Phase 4.
