# elian-claude-plugins

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/Elian-Studio/elian-claude-plugins?label=release)](https://github.com/Elian-Studio/elian-claude-plugins/releases)
[![Plugin: elian-store](https://img.shields.io/badge/plugin-elian--store-blue)](plugins/elian-store/)
[![Skill Quality Gate](https://img.shields.io/badge/quality_gate-90%2F100-brightgreen)](scripts/rubric.md)

> **A Claude Code skill bundle that reduces decision fatigue and smooths workflow.**
> One plugin install (`elian-store`) gives you multiple skills, and new skills land automatically on update.
> Every SKILL.md change must pass a 90-point heuristic quality gate before it can merge to `main`.

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
| [decision-dashboard](plugins/elian-store/skills/decision-dashboard/) | ✅ v1.0.0 | When 3+ decisions block the team, capture them in a printable HTML artifact so the team can decide in 5 minutes. | `/elian-store:decision-dashboard` |
| [generate-teammate](plugins/elian-store/skills/generate-teammate/) | ✅ v2.1.0 | Decompose work into phases, judge each phase independently (Agent Team / Subagent / direct), produce a hybrid execution plan. Ships with 14 plugin-bundled domain agents. | `/elian-store:generate-teammate` |
| [implement](plugins/elian-store/skills/implement/) | ✅ v2.2.0 | TDD-driven feature build: context → plan → approval gate → Red→Green→Refactor → verify → review → report. | `/elian-store:implement` |
| [fix](plugins/elian-store/skills/fix/) | ✅ v2.2.0 | Root-cause-first bug repair: regression test first, then fix, with sibling-site audit. | `/elian-store:fix` |
| [improve](plugins/elian-store/skills/improve/) | ✅ v2.2.0 | Behavior-changing improvement to working features with quantified BEFORE/AFTER and Characterization Tests. | `/elian-store:improve` |
| [brainstorm](plugins/elian-store/skills/brainstorm/) | ✅ v2.2.0 | Conversational discovery for fuzzy requests: Socratic probing → 3+ options → tradeoff matrix → decision → handoff. | `/elian-store:brainstorm` |
| [manage-skills](plugins/elian-store/skills/manage-skills/) | ✅ v2.3.0 | Auto-detect verify-skill drift after code changes and create/update verify-* skills so the project's verification stays current. Pairs with verify-implementation. | `/elian-store:manage-skills` |
| [verify-implementation](plugins/elian-store/skills/verify-implementation/) | ✅ v2.3.0 | Discover and run all verify-* skills in the project before shipping; surface failures with concrete fix suggestions; auto-apply fixes and re-verify with approval. | `/elian-store:verify-implementation` |
| [persona-review](plugins/elian-store/skills/persona-review/) | ✅ v2.5.0 | Review a plan/design/doc through a fixed persona lens (default `daniel`) with a locked 5-block OUTPUT FORMAT (결론 → 트레이드오프 → 운영 리스크 → 8 압박 질문 → 다음 질문). Thin one-liners get ONE intent question first; optional `--depth interview` re-emits the 5-block up to 3 rounds re-interviewing the weakest points, then emits a read-only `/improve` handoff. Read-only. Pairs with /brainstorm as 수렴 압박. | `/elian-store:persona-review` |

New skills land via `/plugin update elian-store@elian` — no separate install per skill.

---

## 🤖 Codex CLI config (independent tree)

This repo also ships an **independent** OpenAI Codex CLI config tree under [`codex/`](codex/) — separate from the Claude `plugins/` tree, with its own quality gate (`scripts/score_codex_prompt.py`) and CI (`codex-config-gate.yml`).

| Skill | Status | Codex install |
|-------|--------|---------------|
| [persona-review](codex/prompts/persona-review.md) | ✅ reference port | `cp codex/prompts/*.md ~/.codex/prompts/` → `/persona-review <target> [--depth interview]` |

Setup: see [`codex/README.md`](codex/README.md). ⚠️ The two trees have **no shared source** — editing skill logic on one side requires manually syncing the other (intentional trade-off; see `CONTRIBUTING.md` → "Claude vs Codex").

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
