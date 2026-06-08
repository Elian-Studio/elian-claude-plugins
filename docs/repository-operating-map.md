# Repository Operating Map

Date: 2026-06-02

## Why This Exists

This repository has more than one tool surface:

- Claude Code marketplace and plugin files.
- Claude Code skill packages, agents, and hooks.
- Codex CLI prompt/config files.
- Portfolio docs and contributor workflow files.

Without an explicit map, the repo looks scattered even when the physical layout is technically valid. This document defines what each tree owns and where contributors should start.

## Reference Pattern

The useful pattern from small plugin repos such as [`explorium-ai/vibeprospecting-plugin`](https://github.com/explorium-ai/vibeprospecting-plugin/tree/main) is not the exact folder names. It is the clarity:

- the repo root is the product entrypoint;
- the root README explains what the plugin does, how to run it, auth/runtime notes, and where the skill lives;
- the plugin has a small visible surface: `.claude-plugin/`, `.mcp.json`, `skills/`, and `README.md`;
- the skill owns domain instructions and references.

`elian-claude-plugins` is broader because it contains a marketplace, one bundled Claude plugin, and an independent Codex tree. The same clarity rule still applies: root README must explain the surfaces first, then point to deeper docs.

## Source Of Truth By Surface

| Surface | Source of truth | What belongs there |
|---|---|---|
| Claude marketplace | `.claude-plugin/marketplace.json` | Marketplace identity, plugin listing, install-visible metadata. |
| Claude plugin | `plugins/elian-store/.claude-plugin/plugin.json` | Plugin identity, version, hooks, bundled plugin metadata. |
| Claude skills | `plugins/elian-store/skills/<skill>/` | `SKILL.md`, skill-specific `scripts/`, `references/`, templates, fixtures. |
| Claude agents | `plugins/elian-store/agents/` | Plugin-bundled subagent definitions. |
| Claude hooks | `plugins/elian-store/hooks/` | Plugin-bundled hook commands. |
| Codex companion | `codex/` | Codex prompts, AGENTS template, config sample, Codex-specific setup docs. |
| Claude workflows | `.claude/workflows/` | Workflow-tool `.js` scripts distributed by copying into `~/.claude/workflows/` (sibling tree, not part of the plugin). See "Workflow Distribution Tree" below. |
| Contributor workflow | `CONTRIBUTING.md` and `.github/pull_request_template.md` | Review checklist, validation expectations, PR metadata. |
| Portfolio docs | `docs/` | Architecture decisions, parity status, roadmap, audits. |

## Non-Source Trees

| Path | Meaning | Rule |
|---|---|---|
| `.claude/settings.local.json` | Per-developer Claude state for this checkout | Git-ignored. Do not treat as plugin source. Keep local state out of release notes unless intentionally versioned. |
| `.claude/skills/` | Maintainer-only dev skills for working *in this repo* | Git-tracked but **not the product**. See "Maintainer Dev Skills" below. |
| `~/.codex/` | User-global Codex install/config destination | Not stored in this repo; `codex/` only provides source files to copy from. |
| `.codex/` | If present locally, Codex state/config | Do not confuse with this repo's `codex/` distribution tree. |

### Maintainer Dev Skills (`.claude/skills/`)

`.claude/skills/` holds Claude Code skills the *maintainer* uses while working on this
repository. They are deliberately **not** part of the shipped `elian-store` plugin and exist
on a different axis from it: `plugins/elian-store/skills/` is the **product** (what users
install); `.claude/skills/` is the **toolbox** (what builds the product).

| Skill | Purpose | Shipped to plugin users? |
|---|---|---|
| `pr-writer` | Draft PR descriptions for this repo's changes | No |
| `vue-nuxt-best-practices` | Vue/Nuxt reference rules for the maintainer's day work | No |

Rules:

- These skills are **dev tooling, not product.** They are never installed by
  `/plugin install elian-store@elian`; only `plugins/elian-store/skills/` ships.
- Do not list them in the root README skill table, `marketplace.json`, `plugin.json`,
  or `CHANGELOG.md` — those describe the distributed plugin only.
- Keep a skill here only while it is specific to working in *this* repo. A skill that is
  useful across all of the maintainer's projects (e.g. general Vue/Nuxt guidance) belongs
  in the global `~/.claude/skills/`, not committed here.
- Maintain **exactly one copy** under `.claude/skills/`. Do not mirror these into a second
  tree (a former `.agents/skills/` byte-for-byte copy was removed for this reason — two
  hand-maintained copies guarantee drift).

### Workflow Distribution Tree (`.claude/workflows/`)

`.claude/workflows/` is a **distribution surface**, not local state — distinct in role from the
two other `.claude/` entries above:

| `.claude/` entry | Role | Git | Distributed? |
|---|---|---|---|
| `.claude/settings.local.json` | Per-developer local state | Ignored | No |
| `.claude/skills/` | Maintainer dev tooling (toolbox) | Tracked | No |
| `.claude/workflows/` | Workflow-tool `.js` source (product) | Tracked | Yes — copy into `~/.claude/workflows/` |

Claude Code plugins cannot register Workflow-tool workflows (a plugin ships skills / agents /
hooks / MCP / LSP / monitors / themes / bin / settings only), so — like `codex/` — these `.js`
files are distributed by **copying them into the user config**, not through the marketplace. The
directory name mirrors the install destination (`~/.claude/workflows/`) so the copy command is
obvious, and the `.claude/` prefix keeps it from being confused with `.github/workflows/` (GitHub
Actions CI, run by GitHub — a different thing entirely). See `.claude/workflows/README.md`.

## Current Physical Shape

```text
elian-claude-plugins/
  .claude-plugin/
    marketplace.json
  plugins/
    elian-store/
      .claude-plugin/
        plugin.json
      agents/
      hooks/
      skills/
        <skill>/
          SKILL.md
          scripts/
          references/
  codex/
    README.md
    AGENTS.md
    config.toml.example
    prompts/
  .claude/
    workflows/                     # Workflow-tool .js, copied into ~/.claude/workflows/
    skills/                        # maintainer-only dev skills (not distributed)
  docs/
  .github/
```

This shape is acceptable because it separates marketplace, plugin, and Codex companion concerns. The problem to avoid is not nested folders; it is undocumented ownership.

## Contributor Entry Points

| Goal | Start here |
|---|---|
| Install the Claude plugin | Root `README.md` -> `Install / Claude Code`. |
| Install Codex prompt/config files | Root `README.md` -> `Install / Codex CLI`, then `codex/README.md`. |
| Add or update a Claude skill | `CONTRIBUTING.md` -> `Add A New Skill`, then the target `plugins/elian-store/skills/<skill>/`. |
| Add or update a Codex prompt | `codex/README.md`, then `docs/claude-codex-skill-parity.md`. |
| Decide whether a new skill should exist | `docs/plugin-portfolio-hybrid-model.md`. |
| Check lifecycle gaps | `docs/gstack-skill-review.md`. |
| Check Claude/Codex drift | `docs/claude-codex-skill-parity.md`. |

## README Contract

The root README should answer these in order:

1. What does this repo ship?
2. How do I install the Claude plugin?
3. How do I install the Codex companion files?
4. What skills are available?
5. Where do I edit each kind of thing?
6. How do I validate changes?
7. Where are roadmap and parity docs?

It should not be the full maintainer manual. Detailed branch protection, release commands, and validation expectations belong in `CONTRIBUTING.md`.

## Future Cleanup Options

Do not move files until a tool constraint is confirmed. If physical cleanup becomes necessary, evaluate these options separately:

1. Add `plugins/elian-store/README.md` as the plugin-local usage guide.
2. Add `docs/skill-catalog.md` if the root README skill table becomes too large.
3. Keep `codex/` independent, but add a parity checklist near every new Claude skill PR.
4. Only split into multiple plugins if different audience, permissions, or release cadence makes the single bundle harmful.
