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
| Contributor workflow | `CONTRIBUTING.md` and `.github/pull_request_template.md` | Review checklist, validation expectations, PR metadata. |
| Portfolio docs | `docs/` | Architecture decisions, parity status, roadmap, audits. |

## Non-Source Trees

| Path | Meaning | Rule |
|---|---|---|
| `.claude/` | Local Claude settings/state for this checkout | Do not treat as plugin source. Keep user/local state out of release notes unless intentionally versioned. |
| `~/.codex/` | User-global Codex install/config destination | Not stored in this repo; `codex/` only provides source files to copy from. |
| `.codex/` | If present locally, Codex state/config | Do not confuse with this repo's `codex/` distribution tree. |

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
