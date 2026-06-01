# elian-claude-plugins

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/Elian-Studio/elian-claude-plugins?label=release)](https://github.com/Elian-Studio/elian-claude-plugins/releases)
[![Plugin: elian-store](https://img.shields.io/badge/plugin-elian--store-blue)](plugins/elian-store/)
[![Skill Quality Gate](https://img.shields.io/badge/quality_gate-90%2F100-brightgreen)](scripts/rubric.md)

> **A Claude Code skill bundle that reduces decision fatigue and smooths workflow.**
> One plugin install (`elian-store`) gives you the full workflow skill set, and new skills land automatically on update.
> Every plugin-distributed SKILL.md change must pass a 90-point heuristic quality gate before it can merge to `main`.

**Latest: v3.0.0 — Persona Code Review**

`/persona-review` is now a development review skill for code, PRs, design, architecture, refactoring plans, domain models, and test strategy. The active built-in lenses are `evans`, `dean`, `martin`, `fowler`, and `beck`; Daniel persona routing was removed. See [`CHANGELOG.md`](CHANGELOG.md#300--2026-06-01) and the [`v3.0.0` release notes](https://github.com/Elian-Studio/elian-claude-plugins/releases/tag/v3.0.0).

---

## 🚀 Quick Start

```shell
/plugin marketplace add Elian-Studio/elian-claude-plugins
/plugin install elian-store@elian
```

Then in Claude Code:

> "I have 4 decisions piling up. Make me a decision dashboard."

→ The `decision-dashboard` skill inside `elian-store` is invoked automatically and produces a printable HTML dashboard. Explicit invocation: `/elian-store:decision-dashboard`.

---

## 📦 Skills inside elian-store

| Skill | Status | Description | Invocation |
|-------|--------|-------------|------------|
| [decision-dashboard](plugins/elian-store/skills/decision-dashboard/) | ✅ bundled | Capture 3+ blocking decisions in a printable HTML artifact with downloadable JSON for downstream skills. | `/elian-store:decision-dashboard` |
| [generate-teammate](plugins/elian-store/skills/generate-teammate/) | ✅ bundled | Decompose work into phases, decide Agent Team / Subagent / direct execution per phase, and render JSON-first teammate prompts. | `/elian-store:generate-teammate` |
| [create-document](plugins/elian-store/skills/create-document/) | ✅ bundled | Render structured HTML/MD from JSON through schema validation and templates. Used directly or by other skills. | `/elian-store:create-document` |
| [design-ui](plugins/elian-store/skills/design-ui/) | ✅ bundled | Design UI/UX through Interview → Reference → Wireframe → Gate → Visual → Deliver. | `/elian-store:design-ui` |
| [ai-assisted-feature-development](plugins/elian-store/skills/ai-assisted-feature-development/) | ✅ bundled | Turn feature work into intent, BDD/SDD/DDD, tests, context, agentic tasks, review, and SPDD archive. | `/elian-store:ai-assisted-feature-development` |
| [implement](plugins/elian-store/skills/implement/) | ✅ bundled | TDD-driven feature build: context → plan → approval gate → Red→Green→Refactor → verify → review → report. | `/elian-store:implement` |
| [fix](plugins/elian-store/skills/fix/) | ✅ bundled | Root-cause-first bug repair: regression test first, then fix, with side-effect audit. | `/elian-store:fix` |
| [improve](plugins/elian-store/skills/improve/) | ✅ bundled | Behavior-changing improvement to working features with quantified BEFORE/AFTER and Characterization Tests. | `/elian-store:improve` |
| [brainstorm](plugins/elian-store/skills/brainstorm/) | ✅ bundled | Conversational discovery for fuzzy requests: Socratic probing → 3+ options → tradeoff matrix → decision → handoff. | `/elian-store:brainstorm` |
| [manage-skills](plugins/elian-store/skills/manage-skills/) | ✅ bundled | Detect verify-skill drift after code changes and create/update verify-* skills so project verification stays current. | `/elian-store:manage-skills` |
| [verify-implementation](plugins/elian-store/skills/verify-implementation/) | ✅ bundled | Discover and run project verify-* skills before shipping; report failures and apply fixes only with approval. | `/elian-store:verify-implementation` |
| [persona-review](plugins/elian-store/skills/persona-review/) | ✅ bundled | Review code, PRs, design, architecture, refactoring, domain models, and tests through `evans`, `dean`, `martin`, `fowler`, and `beck` lenses. | `/elian-store:persona-review` |

New skills land via `/plugin update elian-store@elian` — no separate install per skill.

Portfolio-level review: [`docs/gstack-skill-review.md`](docs/gstack-skill-review.md) compares this bundle against `garrytan/gstack` lifecycle patterns. Current status: structurally healthy, but not yet lifecycle-complete; browser QA, release, benchmark, security, learning, and stricter release-readiness review workflows are tracked as roadmap gaps.

---

## 🤖 Codex CLI config (independent tree)

This repo also ships an **independent** OpenAI Codex CLI config tree under [`codex/`](codex/) — separate from the Claude `plugins/` tree, with its own quality gate (`scripts/score_codex_prompt.py`) and CI (`codex-config-gate.yml`).

| Skill | Status | Codex command |
|-------|--------|---------------|
| [persona-review](codex/prompts/persona-review.md) | ✅ reference port | `/persona-review <target> [--persona evans\|dean\|martin\|fowler\|beck\|all\|comma-list\|<path>] [--depth quick\|deep\|interview] [--apply]` |

Install or update the Codex prompt:

```shell
mkdir -p ~/.codex/prompts
rm -f ~/.codex/prompts/on-call-elian.md  # remove legacy command from old installs
cp codex/prompts/*.md ~/.codex/prompts/
```

Setup: see [`codex/README.md`](codex/README.md). ⚠️ The two trees have **no shared source** — editing skill logic on one side requires manually syncing the other (intentional trade-off; see `CONTRIBUTING.md` → "Claude vs Codex"). Current Claude/Codex parity status: [`docs/claude-codex-skill-parity.md`](docs/claude-codex-skill-parity.md).

---

## 🧩 Local Agent Skills

This repository can also carry local Agent Skill drafts outside the `elian-store` marketplace plugin and outside the `codex/prompts` tree. These files are copied into the tool-specific skill locations directly and are not pulled by `/plugin update elian-store@elian`. They are currently ungated drafts; the 90-point Skill Quality Gate covers plugin-distributed skills under `plugins/**/skills/**/SKILL.md`.

| Skill | Purpose | Codex path | Claude path |
|-------|---------|------------|-------------|
| [pr-writer](.agents/skills/pr-writer/SKILL.md) | Draft PR/MR titles and Markdown bodies from diffs, commits, branches, issue context, tests, and PR templates. Output-only: it does not create, push, submit, or merge PRs unless explicitly asked. | `.agents/skills/pr-writer/SKILL.md` | `.claude/skills/pr-writer/SKILL.md` |
| [vue-nuxt-best-practices](.agents/skills/vue-nuxt-best-practices/SKILL.md) | Vercel-style rules pack for Vue 3 + Nuxt 3/4 work. `SKILL.md` routes to focused `rules/` for SSR/hydration, data fetching, components, performance, Nitro/server, state, accessibility, and testing. | `.agents/skills/vue-nuxt-best-practices/` | `.claude/skills/vue-nuxt-best-practices/` |

---

## 🎯 decision-dashboard — what does it look like?

![decision-dashboard preview](docs/screenshots/decision-dashboard-overview.png)

Left sidebar groups decisions by priority (P0/P1/P2). Right pane shows the expanded card: background → guiding question → options (A/B/C/D + "Other — custom input") → notes. Footer carries progress + JSON/MD download buttons.

### Use case

**Before** — 4 decisions are scattered across chat threads; the PO doesn't read to the bottom; downstream work stalls.

**After** — invoke `decision-dashboard` → 4 cards generated automatically → share the HTML with the PO → receive JSON in 5 minutes → downstream skills consume that JSON as context.

Core principles:
- **Card-body LANGUAGE GATE** — class names, table names, internal acronyms are filtered out automatically. The decision-maker doesn't need to read code.
- **"Other — custom input" is mandatory** — escape hatch when none of the offered options fit.
- **Two modes** — `generate` (first creation) vs `finalize` (persist JSON + clean up HTML).
- **Persistent artifact** — `decisions-final.json` is consumed as context by downstream skills.

Full usage: [`plugins/elian-store/skills/decision-dashboard/SKILL.md`](plugins/elian-store/skills/decision-dashboard/SKILL.md)

---

## 🔄 Update

```shell
/plugin marketplace update elian
/plugin update elian-store@elian
```

New skills are pulled along with the plugin update.

---

## ⚠️ v1.x → v2.x migration

In v1.x, `decision-dashboard` was a standalone plugin. From v2.0.0, it lives **as a skill inside the `elian-store` bundle**. The reason: bundling lets multiple skills land via a single install.

If you installed v1.x:
```shell
/plugin uninstall decision-dashboard@elian
/plugin install elian-store@elian
```

Invocation format change:
```
/decision-dashboard:decision-dashboard   →   /elian-store:decision-dashboard
```

Natural-language invocation ("make a decision dashboard") is unchanged.

---

## 📜 License

MIT — see `plugins/elian-store/.claude-plugin/plugin.json`.

---

## 🤝 Contributing / forks / maintainer guide

To open a PR or run your own fork, see [`CONTRIBUTING.md`](CONTRIBUTING.md) — workflow, local validation, evaluation rubric, new-skill workflow, and branch-protection / release procedure are all there.

Full change history: [`CHANGELOG.md`](CHANGELOG.md). Release notes: [Releases](https://github.com/Elian-Studio/elian-claude-plugins/releases).
