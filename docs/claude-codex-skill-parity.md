# Claude / Codex Skill Parity Review

Date: 2026-06-02
Last updated: 2026-06-12 (migrated 13 commands from Codex prompts to shared Codex *skills* via `tools/generate.py`; only `generate-teammate` and `persona-review` stay prompts — their core is Claude subagent dispatch, which Codex cannot reproduce; `document-writer` and `harness-manager` remain Claude-only. Codex catalog: 2 prompts + 13 shared skills. 2026-06-12: added `pr-review` as a third Claude-only skill — parallel multi-subagent review panel the Codex runtime cannot reproduce. 2026-06-23: added three superpowers-derived skills — `verify-before-claiming` and `respond-to-review` as shared Codex skills, and `finish-branch` as a fourth Claude-only skill (native worktree tooling). Codex catalog: 2 prompts + 15 shared skills. 2026-07-03: added `functional-spec` as a shared Codex skill (wireframe→code-grounded spec bridge; doc-generation + codebase-reading, fully Codex-reproducible — symlinked, no Claude-only blocker). Codex catalog: 2 prompts + 16 shared skills. 2026-07-22 (v3.0.0): retired `ai-assisted-feature-development` and `skill-dispatcher` from **both** trees (the first duplicated `intake-spec` + `design-feature` + `implement` + `review`; the second duplicated the host's built-in skill discovery). Codex catalog: 2 prompts + 14 shared skills. 2026-07-22 (v3.1.0): added `spec-coverage` (requirement-to-test coverage) as a fifth Claude-only skill — it detects and runs the project's test runner and depends on a bundled renderer/validator asset pair. Codex catalog unchanged: 2 prompts + 14 shared skills.)

## Goal

Make the Claude plugin catalog and Codex prompt catalog use the same command names, intent boundaries, approval posture, and validation expectations where the platforms allow it.

This does **not** mean byte-for-byte identical files:

- Claude Code uses plugin skills under `plugins/elian-store/skills/*/SKILL.md` with YAML frontmatter, `allowed-tools`, `disable-model-invocation`, bundled agents, hooks, and plugin marketplace metadata.
- Codex in this repository uses `codex/prompts/*.md`, `codex/AGENTS.md`, and `codex/config.toml.example`. There is no Codex plugin marketplace shape here, so the equivalent of a Claude skill is a Codex prompt file plus repo-level config.

Terminology: this repository has a Claude plugin tree and an independent Codex CLI prompt/config tree. It does not currently ship a Codex plugin marketplace bundle.

## Equivalence Rule

A Claude skill and Codex prompt are considered aligned only when all of these match:

- Same public command name: `/persona-review`, `/implement`, etc.
- Same primary purpose and exclusion boundary.
- Same approval posture: read-only, write-artifact, or code-changing.
- Same output contract or same handoff artifact.
- Platform-specific tool differences are explicit, not hidden.
- Both have a relevant verification path:
  - Claude: YAML/frontmatter smoke test plus the skill-owned validator when present.
  - Codex: prompt/config review plus parity review against the Claude counterpart.

## Current Parity Status

| Area | Claude | Codex | Status |
|---|---:|---:|---|
| Catalog entries | 26 skills | 2 prompts + 14 shared skills | 15 matched + 5 documented Claude-only + 6 not yet ported |
| Command naming | `/elian-store:<skill>` | `/<prompt-file>` | Mostly alignable |
| Current matched commands | `brainstorm`, `create-document`, `decision-dashboard`, `design-ui`, `fix`, `functional-spec`, `generate-teammate`, `improve`, `implement`, `manage-skills`, `review`, `verify-implementation`, `persona-review`, `pr-writer`, `verify-before-claiming`, `respond-to-review` | `brainstorm`, `create-document`, `decision-dashboard`, `design-ui`, `fix`, `functional-spec`, `generate-teammate`, `improve`, `implement`, `manage-skills`, `review`, `verify-implementation`, `persona-review`, `pr-writer`, `verify-before-claiming`, `respond-to-review` | Aligned |
| Legacy `on-call-elian` | Removed from current Claude skill catalog | Removed from current Codex prompt catalog | Aligned |
| Validation | YAML + skill-owned validators where present | Prompt/config review | Asymmetric, manual |

Current conclusion: **the two trees now cover the same ported command catalog, but they are not byte-for-byte or runtime-identical yet**. The name drift around `on-call-elian` is fixed, the 16 ported commands all have Codex counterparts (2 prompts + 14 shared skills), the 5 Claude-only skills (`harness-manager`, `document-writer`, `pr-review`, `finish-branch`, `spec-coverage`) plus the 5 design-pipeline skills not yet ported (`intake-spec`, `design-feature`, `update-design`, `erd-preview`, `kanban-board`) are documented exceptions below, and the remaining divergence is platform/runtime behavior rather than missing prompt coverage.

**Skills-based Codex distribution.** Instead of hand-mirrored prompts, `codex/skills/<name>` is a relative symlink into `plugins/elian-store/skills/<name>/`, and `codex/setup.sh` symlinks it into `~/.codex/skills/`. Both tools read one `SKILL.md`, so migrated commands cannot drift. `tools/generate.py` (manifest `tools/clusters.json`) maintains the symlinks and lints every `SKILL.md` for host-agnostic script paths. **14 commands are now shared skills** — everything except the exceptions below.

**Third-host decision.** The current Claude + Codex shape should stay simple: shared `SKILL.md` symlinks for portable skills plus hand-authored Codex prompts for the two subagent-core flows. Template/adapter generation is deferred until a third host such as Gemini or Cursor becomes a real target; adding that machinery now would increase release and validation surface without solving an active parity gap.

**The exceptions.** Five skills are **Claude-only** (`harness-manager` operates on the global harnesses; `pr-review` is a parallel multi-subagent review panel; `finish-branch` depends on the native `EnterWorktree`/`ExitWorktree` tools and `.claude/worktrees/` semantics; `spec-coverage` detects and runs the project's test runner behind a bundled validator/renderer pair; `document-writer` is a deferred port, not a platform limitation — its `~/.claude/skills/...` hardcoding was removed in v3.0.0, so a symlink port is now feasible) and do not currently ship to Codex. Two stay **hand-authored Codex prompts** because their core is Claude subagent dispatch, which Codex cannot reproduce: `generate-teammate` (teammate-spawn / subagent team flow) and `persona-review` (per-persona subagent dispatch + aggregation). Their `SKILL.md` is host-agnostic, but symlinking it would advertise a flow that does not run on Codex.

**Host-agnostic `SKILL.md` portability** (resolve `SKILL_DIR` / sibling `CD` with a `${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+...}}` → `${CODEX_HOME:-$HOME/.codex}/skills/...` fallback, never a bare `CLAUDE_PLUGIN_ROOT`/`CLAUDE_SKILL_DIR`) is applied to all six skills that used those vars: `create-document`, `decision-dashboard`, `design-ui`, `generate-teammate`, `manage-skills`, and `verify-implementation`. The last two were caught by the `tools/generate.py` lint; the lint now gates every skill.

## gstack Portfolio Lens

[`docs/gstack-skill-review.md`](gstack-skill-review.md) adds a portfolio-level check based on `garrytan/gstack`. That review is separate from one-to-one Claude/Codex parity:

| Lifecycle lane | Current Claude coverage | Current Codex coverage | Status |
|---|---|---|---|
| Product/spec planning | `brainstorm`, `intake-spec`, `design-feature`, `update-design`, `decision-dashboard` | `brainstorm`, `decision-dashboard` | Partial |
| Design planning | `design-ui` | Missing | Partial |
| Implementation/fix/improve | `implement`, `fix`, `improve` | Missing | Claude-only |
| Engineering review | `review`; `persona-review` remains persona-lens critique | `persona-review` only | Claude-only |
| Browser QA | None | None | Gap |
| Ship/release | Referenced by downstream handoffs, no skill | None | Gap |
| Deploy/canary/benchmark/security | None | None | Gap |
| Learning/retro/context restore | Partial through docs/artifacts, no skill | None | Gap |

Do not treat these gaps as immediate parity bugs. They are roadmap gaps and should become skills only when the workflow, artifacts, and verification path are concrete.

## Purpose Fit Matrix

| Skill | Purpose | Fit | Notes | Codex parity |
|---|---|---|---|---|
| `brainstorm` | Clarify fuzzy requests through context, Socratic probing, options, tradeoff, decision, handoff | Good | Codex now shares the same discovery flow, option drafting requirement, and handoff outputs. Keep the "ask, do not assume" boundary intact. | Present |
| `implement` | Build new features through TDD with approval gates | Good | Codex now preserves the approval-gated TDD flow and explicit file ownership before execution. | Present |
| `fix` | Repair confirmed bugs with root-cause analysis and regression test first | Good | Codex now preserves root-cause-first repair, regression-test-first repair, and sibling-site search. | Present |
| `improve` | Make behavior-changing improvements to working features | Good | Codex now preserves BEFORE/AFTER measurement and existing-test protection. | Present |
| `design-ui` | Produce UI/UX design artifacts through interview, reference, wireframe, gate, visual | Mostly good | Codex now shares the same brief -> reference -> wireframe -> gate -> visual flow. Keep the gate explicit and preserve the artifact set. | Present |
| `decision-dashboard` | Turn 3+ blocking decisions into a printable decision artifact and JSON | Good | Codex now preserves the JSON-first / HTML-second contract and the `generate` / `finalize` flow. Keep the memo requirement for `Other` explicit. | Present |
| `generate-teammate` | Decide direct/subagent/team execution and generate teammate/task prompts | Platform-specific | Claude can use Agent/Team tools; Codex keeps the same phase analysis and handoff plan, but not actual teammate spawning. | Present (platform-limited) |
| `create-document` | Deterministically render schema-validated JSON into HTML/MD templates | Good utility | Codex now preserves the validate-first rendering contract and the supported template set. Keep the legacy fixed five-block renderer out of the active path. | Present |
| `manage-skills` | Detect and repair verify-skill drift | Good, but Claude-specific | Codex now treats this as verification prompt maintenance and drift repair within the prompt tree; actual `.claude/skills` repair is still Claude-side. | Present (platform-limited) |
| `verify-implementation` | Discover and run project verify-* skills before shipping | Good, but Claude-specific | Codex now provides a prompt-level verification orchestrator, but project-local verification semantics still depend on the prompt tree rather than Claude Agent tooling. | Present (platform-limited) |
| `persona-review` | Auto-select matching persona lenses from the target and review with persona-native output | Aligned | Claude and Codex now share the same command name, signal-map **auto-selection** as the default when no `--persona` is given (cap 3, `daniel` fallback), the full 14-persona roster (+ custom path), interview mode, and free-form review contract. Claude dispatches persona-specific subagents; Codex keeps the same judgment shape in-process without Claude Agent tools. | Present |
| `review` | Read-only engineering review of code, diffs, PRs, or changed files with findings-first output | Good | Codex now shares the same findings-first contract and read-only boundary. Keep the target/diff/line evidence discipline aligned with the Claude skill. | Present |
| `pr-writer` | Draft a review-friendly PR/MR title and body from the diff, commits, and stated intent, contrasting intent vs implementation | Good | Both trees share the draft-only posture, PLAN -> DRAFT -> CONTRAST flow, platform (`gh`/`glab`) detection, and the same title/body output contract. Claude scopes read-only git tools via `allowed-tools`; Codex enforces the same draft-only boundary in prompt prose. | Present |
| `verify-before-claiming` | Claim-time honesty gate — require fresh verification evidence before any pass/fixed/done claim | Good | Portable doctrine + bash verification idioms; ships as a shared symlink. Always-on (`disable-model-invocation: false`), read-only. Distinct from `verify-implementation` (suite runner) — this proves the specific claim being made. | Present |
| `respond-to-review` | Consumer side of review — verify feedback before implementing, no performative agreement, push back with reasoning | Good | Behavioral, read-only triage that hands edits to `/fix` or `/improve`; ships as a shared symlink. Always-on (`disable-model-invocation: false`). | Present |
| `finish-branch` | Disposition of a finished branch (merge / push+PR / keep / discard) with worktree-safe cleanup | Claude-only | Depends on native `EnterWorktree`/`ExitWorktree` and `.claude/worktrees/`; delegates push+PR to `/ship`. Documented exception below. | Claude-only |

## Required Work To Make Them Identical

Minimum parity work:

1. Keep prompt bodies and runtime assumptions in sync as the remaining platform-specific gaps are refined.
2. Keep command names exactly equal to Claude skill directory names.
3. For side-effect skills (`implement`, `fix`, `improve`, `manage-skills`, `verify-implementation`), convert Claude `AskUserQuestion` and tool-gate behavior into Codex "ask and stop" instructions.
4. For utility skills (`create-document`, `decision-dashboard`), call shared scripts/templates instead of duplicating generated output logic in prompt prose.
5. For Claude-only runtime skills (`generate-teammate`, parts of `verify-implementation`), document the Codex limitation in the prompt and make the Codex version produce a handoff plan rather than pretending to spawn agents.
6. Keep Codex validation prompt-specific. Skill-specific contracts should be validated without forcing unrelated prompts into the same output shape.

## Recommended Port Order

| Order | Prompt | Reason |
|---:|---|---|
| 1 | `manage-skills`, `verify-implementation` | Needs a cross-tool definition of what gets verified. |
| 2 | `generate-teammate` | Most platform-specific because Claude Agent/Team tools do not have a direct Codex equivalent here. |

## Recommended New-Skill Order From gstack Review

These are new Claude skill candidates, not Codex parity ports:

| Order | Skill candidate | Reason |
|---:|---|---|
| 1 | `qa` or `browser-qa` | Adds browser-visible verification with screenshots/reports before release. |
| 2 | `ship` | Separates branch/test/PR release readiness from implementation. |
| 3 | `learn` or `retro` | Captures repeated preferences and workflow lessons after real usage. |

Completed:

- `brainstorm` now closes the biggest gap in the planning/discovery lane.
- `create-document` now closes the JSON-to-artifact rendering lane.
- `decision-dashboard` now closes the decision-dashboard generation lane.
- `design-ui` now closes the biggest gap in the UX design artifact lane.
- `fix` now closes the bug-repair lane.
- `generate-teammate` now closes the execution-planning lane with a Codex handoff-only equivalent.
- `improve` now closes the behavior-improvement lane.
- `implement` now closes the new-feature implementation lane.
- `manage-skills` now closes the verification-drift maintenance lane at the prompt level.
- `review` now closes the biggest gap between read-only persona critique and production-oriented engineering review.
- `verify-implementation` now closes the verification orchestration lane at the prompt level.
- `persona-review` now matches the Claude command name and the native free-form review contract.
- `pr-writer` ships in both trees with a shared draft-only PR/MR description contract and platform-aware (`gh`/`glab`) context gathering.

## Documented Exceptions (Claude-only, no Codex prompt)

These skills ship in the Claude plugin without a `codex/prompts/<skill>.md` counterpart. The operating rule below requires the exception to be recorded here.

| Skill | Why no Codex prompt (yet) |
|---|---|
| `harness-manager` | Meta-tool that operates on **both** harnesses' global files at once (`~/.claude/CLAUDE.md` ↔ `~/.codex/AGENTS.md`, `~/.claude.json` ↔ `~/.codex/config.toml`, commands ↔ prompts, skills). It is not a per-tool workflow to mirror; a Codex prompt that drives the same scan/report/reconcile flow from the Codex side is a reasonable future addition, not a behavioral mirror. Until authored, the Claude skill is the single entry point. |
| `document-writer` | House-style self-contained HTML/MD document generator shipped to the Claude plugin (PR #19). v3.0.0 rewrote it in English and replaced its `~/.claude/skills/...` hardcoding with the standard `SKILL_DIR` resolver, so nothing platform-specific blocks it any more — it is now a straightforward symlink port, just not yet done. Tracked as a port candidate. |
| `pr-review` | Multi-perspective PR/MR reviewer whose core is **parallel multi-subagent panel dispatch** — up to ~17 specialist + persona reviewers run concurrently via the Agent tool, then synthesized into one verdict. The Codex runtime cannot reproduce the concurrent panel (same limitation as `generate-teammate` / `persona-review`). A Codex prompt that drives a sequential, handoff-style review is a reasonable future addition, not a behavioral mirror. |
| `finish-branch` | Branch-disposition workflow whose cleanup depends on the native `EnterWorktree`/`ExitWorktree` harness tools and `.claude/worktrees/` semantics, which do not exist in Codex. Its push+PR option also delegates to the Claude-side `/ship`. A Codex prompt using plain `git worktree` is a reasonable future addition, not a behavioral mirror. |
| `erd-preview` | Self-contained "Lineage Explorer" HTML generator: fills a bundled `assets/template.html` from real data and self-checks with a Node-backed `scripts/validate.py` (referential integrity, cardinality, LAYERS ordering). The value is the shipped template + validator asset pair, not a portable prompt; a Codex prompt could describe the flow but cannot carry the template/validator the same way. Claude-only by deferral, a reasonable future port candidate, not a behavioral mirror. |
| `intake-spec`, `design-feature`, `update-design` | The requirements → design → propagation pipeline. Their `SKILL.md` bodies are host-agnostic (they already resolve `create-document` through a `${CODEX_HOME}` fallback), so a symlink port is feasible. Deferred, not blocked: the pipeline is still changing shape (v3.0.0 moved `spec.json` into `claudedocs/<label>/` and added `tech-spec.md`), and porting a moving contract to a second tree doubles the churn. Port once the artifact set settles. |
| `kanban-board` | Self-contained interactive HTML board generator whose value is the bundled `scripts/build_board.py` + template pair, same shape as `erd-preview`. Claude-only by deferral, a reasonable future port candidate. |
| `spec-coverage` | Requirement-to-test coverage tracker. Its contract is "run this project's test suite now, parse the JUnit XML, and decide each acceptance criterion from the result" — that means detecting and executing a build tool, then rendering through a bundled validator/renderer pair. A Codex prompt could describe the judgement but could not carry the scripts that make it deterministic, and a prompt that guessed at status would defeat the skill's only purpose. Claude-only by design, not deferral. |

## Retired Commands

| Command | Retired | Reason | Migration |
|---|---|---|---|
| `ai-assisted-feature-development` | v3.0.0 (2026-07-22) | Its 9 phases duplicated existing skills: phases 1–5 = `intake-spec` + `design-feature`, phases 6–7 = `implement`, phase 8 = `review`. It wrote artifacts to its own layout, so nothing downstream could consume them, and `disable-model-invocation: false` let it auto-trigger against `intake-spec`. | `/intake-spec` → `/design-feature` → `/implement` → `/review` |
| `skill-dispatcher` | v3.0.0 (2026-07-22) | Duplicated the host's built-in skill discovery plus each skill's own `when_to_use`. | None — the host routes on `description` / `when_to_use`. |

Removed from both trees in the same change (plugin skill + `codex/skills/` symlink).

## Operating Rule Going Forward

Every new Claude skill requires one of these in the same PR:

- A matching `codex/prompts/<skill>.md`, or
- A documented exception in this file explaining why no Codex equivalent exists.

Every rename must update both trees in the same change. `on-call-elian` should appear only in historical changelog entries or external migration notes.
