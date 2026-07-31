# Claude / Codex Skill Parity Review

Date: 2026-06-02
Last updated: 2026-07-29. The `elian-store` catalog has 22 skills. Codex ships 12 shared
skill symlinks and two hand-authored prompts; two skills are blocked by runtime
constraints and six portable skills are explicitly deferred. `tools/clusters.json`
is the machine-readable disposition source and `scripts/validate_repository.py`
checks that every skill has exactly one non-overlapping disposition.

> **4.0.0 (2026-07-29) — four skills retired, so parts of the tables below are historical.**
> `finish-branch`, `functional-spec`, `design-ui`, and `kanban-board` were removed on usage
> evidence. Their rows are kept as a record of the disposition reasoning, but they no longer
> exist in either tree, and the `codex/skills/design-ui` and `codex/skills/functional-spec`
> symlinks are gone. Treat `tools/clusters.json` as authoritative wherever this doc disagrees.
>
> A second plugin, `elian-workflow` (`issue-open`, `issue-close`), now ships alongside
> `elian-store`. It has no Codex counterpart yet — both skills depend on a Notion MCP server,
> which is a Claude-side integration. Recorded here as a deliberate parity exception rather
> than an oversight.

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
| Catalog entries | 22 skills (`elian-store`) + 2 (`elian-workflow`) | 2 prompts + 12 shared skills | 14 matched + 2 Claude-only + 6 deferred + 2 MCP-bound |
| Command naming | `/elian-store:<skill>`, `/elian-workflow:<skill>` | `/<prompt-file>` | Mostly alignable |
| Current matched commands | `brainstorm`, `create-document`, `decision-dashboard`, `fix`, `generate-teammate`, `improve`, `implement`, `manage-skills`, `review`, `verify-implementation`, `persona-review`, `pr-writer`, `verify-before-claiming`, `respond-to-review` | `brainstorm`, `create-document`, `decision-dashboard`, `fix`, `generate-teammate`, `improve`, `implement`, `manage-skills`, `review`, `verify-implementation`, `persona-review`, `pr-writer`, `verify-before-claiming`, `respond-to-review` | Aligned |
| Legacy `on-call-elian` | Removed from current Claude skill catalog | Removed from current Codex prompt catalog | Aligned |
| Validation | Repository validator + YAML + skill-owned validators | Repository validator + prompt/config parity review | Automated structure, manual semantics |

Current conclusion: **the two trees cover the same 14-command ported catalog, but they are
not runtime-identical**. Two skills are Claude-only because of real runtime behavior:
`harness-manager` and `pr-review`. Six are portable but
deliberately deferred: `document-writer`, `intake-spec`, `design-feature`, `update-design`,
`erd-preview`, and `spec-coverage`.

**Skills-based Codex distribution.** Instead of hand-mirrored prompts, `codex/skills/<name>` is a relative symlink into `plugins/elian-store/skills/<name>/`, and `codex/setup.sh` symlinks it into `~/.codex/skills/`. Both tools read one `SKILL.md`, so migrated commands cannot drift. `tools/generate.py` (manifest `tools/clusters.json`) maintains the symlinks and lints every `SKILL.md` for host-agnostic script paths **across every plugin, not only the cluster source** — a bare `${CLAUDE_*}` is host-dependent wherever it lives, and scoping the lint to one plugin let a second plugin ship unlinted. **12 commands are now shared skills** — everything except the exceptions below.

**Third-host decision.** The current Claude + Codex shape should stay simple: shared `SKILL.md` symlinks for portable skills plus hand-authored Codex prompts for the two subagent-core flows. Template/adapter generation is deferred until a third host such as Gemini or Cursor becomes a real target; adding that machinery now would increase release and validation surface without solving an active parity gap.

**The exceptions.** Two skills are **Claude-only** for runtime reasons. Six portable skills are
**deferred**, which means omission is an explicit product choice rather than a runtime claim. Two
stay **hand-authored Codex prompts** because their core is Claude subagent dispatch:
`generate-teammate` and `persona-review`. Their `SKILL.md` bodies are host-agnostic, but
symlinking them would advertise a dispatch flow Codex cannot reproduce.

**Host-agnostic `SKILL.md` portability** (resolve `SKILL_DIR` / sibling `CD` with a `${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+...}}` → `${CODEX_HOME:-$HOME/.codex}/skills/...` fallback, never a bare `CLAUDE_PLUGIN_ROOT`/`CLAUDE_SKILL_DIR`) is applied to every skill that uses those vars: `create-document`, `decision-dashboard`, `generate-teammate`, `manage-skills`, `verify-implementation`, and `issue-close`. The last two were caught by the `tools/generate.py` lint; the lint now gates every skill.

## gstack Portfolio Lens

[`docs/gstack-skill-review.md`](gstack-skill-review.md) adds a portfolio-level check based on `garrytan/gstack`. That review is separate from one-to-one Claude/Codex parity:

| Lifecycle lane | Current Claude coverage | Current Codex coverage | Status |
|---|---|---|---|
| Product/spec planning | `brainstorm`, `intake-spec`, `design-feature`, `update-design`, `decision-dashboard` | `brainstorm`, `decision-dashboard` | Partial; pipeline deferred |
| Design planning | None (`design-ui` retired in 4.0.0) | None | Gap — slot reopened |
| Implementation/fix/improve | `implement`, `fix`, `improve` | `implement`, `fix`, `improve` | Aligned |
| Engineering review | `review`; `persona-review` remains persona-lens critique | `review`, `persona-review` | Aligned with runtime-specific dispatch |
| Browser QA | None | None | Gap |
| Ship/release | Referenced by downstream handoffs, no skill | None | Gap |
| Deploy/canary/benchmark/security | None | None | Gap |
| Learning/retro/context restore | Partial through docs/artifacts, no skill | None | Gap |

Do not treat these gaps as immediate parity bugs. They are roadmap gaps and should become skills only when the workflow, artifacts, and verification path are concrete.

## Ported Purpose Fit Matrix

| Skill | Purpose | Fit | Notes | Codex parity |
|---|---|---|---|---|
| `brainstorm` | Clarify fuzzy requests through context, Socratic probing, options, tradeoff, decision, handoff | Good | Codex now shares the same discovery flow, option drafting requirement, and handoff outputs. Keep the "ask, do not assume" boundary intact. | Present |
| `implement` | Build new features through TDD with approval gates | Good | Codex now preserves the approval-gated TDD flow and explicit file ownership before execution. | Present |
| `fix` | Repair confirmed bugs with root-cause analysis and regression test first | Good | Codex now preserves root-cause-first repair, regression-test-first repair, and sibling-site search. | Present |
| `improve` | Make behavior-changing improvements to working features | Good | Codex now preserves BEFORE/AFTER measurement and existing-test protection. | Present |
| ~~`design-ui`~~ | Produce UI/UX design artifacts through interview, reference, wireframe, gate, visual | Mostly good | Codex shared the same brief -> reference -> wireframe -> gate -> visual flow. | Retired in 4.0.0 |
| `decision-dashboard` | Turn 3+ blocking decisions into a printable decision artifact and JSON | Good | Codex now preserves the JSON-first / HTML-second contract and the `generate` / `finalize` flow. Keep the memo requirement for `Other` explicit. | Present |
| `generate-teammate` | Decide direct/subagent/team execution and generate teammate/task prompts | Platform-specific | Claude can use Agent/Team tools; Codex keeps the same phase analysis and handoff plan, but not actual teammate spawning. | Present (platform-limited) |
| `create-document` | Deterministically render schema-validated JSON into HTML/MD templates | Good utility | Codex now preserves the validate-first rendering contract and the supported template set. Keep the legacy fixed five-block renderer out of the active path. | Present |
| `manage-skills` | Detect and repair verify-skill drift | Good | Both hosts read the same `SKILL.md`; project harness paths are resolved at runtime. | Present |
| `verify-implementation` | Discover and run project verify-* skills before shipping | Good | Both hosts read the same discovery and approval contract. | Present |
| `persona-review` | Auto-select matching persona lenses from the target and review with persona-native output | Aligned | Claude and Codex now share the same command name, signal-map **auto-selection** as the default when no `--persona` is given (cap 3, `daniel` fallback), the full 14-persona roster (+ custom path), interview mode, and free-form review contract. Claude dispatches persona-specific subagents; Codex keeps the same judgment shape in-process without Claude Agent tools. | Present |
| `review` | Read-only engineering review of code, diffs, PRs, or changed files with findings-first output | Good | Codex now shares the same findings-first contract and read-only boundary. Keep the target/diff/line evidence discipline aligned with the Claude skill. | Present |
| `pr-writer` | Draft a review-friendly PR/MR title and body from the diff, commits, and stated intent, contrasting intent vs implementation | Good | Both trees share the draft-only posture, PLAN -> DRAFT -> CONTRAST flow, platform (`gh`/`glab`) detection, and the same title/body output contract. Claude scopes read-only git tools via `allowed-tools`; Codex enforces the same draft-only boundary in prompt prose. | Present |
| `verify-before-claiming` | Claim-time honesty gate — require fresh verification evidence before any pass/fixed/done claim | Good | Portable doctrine + bash verification idioms; ships as a shared symlink. Always-on (`disable-model-invocation: false`), read-only. Distinct from `verify-implementation` (suite runner) — this proves the specific claim being made. | Present |
| `respond-to-review` | Consumer side of review — verify feedback before implementing, no performative agreement, push back with reasoning | Good | Behavioral, read-only triage that hands edits to `/fix` or `/improve`; ships as a shared symlink. Always-on (`disable-model-invocation: false`). | Present |
| ~~`finish-branch`~~ | Disposition of a finished branch (merge / push+PR / keep / discard) with worktree-safe cleanup | Claude-only | Depended on native `EnterWorktree`/`ExitWorktree` and `.claude/worktrees/`. | Retired in 4.0.0 |

## Required Work To Maintain Parity

Minimum ongoing parity work:

1. Keep the two prompt-only adapters aligned with their Claude `SKILL.md` intent and output.
2. Keep command names exactly equal to Claude skill directory names.
3. Keep side-effect approval semantics explicit in shared skills and prompt adapters.
4. Call shared scripts/templates from shared skills instead of duplicating output logic.
5. Record every non-shared skill as `claude_only`, `prompt_only`, or `deferred` in
   `tools/clusters.json`; do not infer a runtime blocker from a missing symlink.
6. Run `scripts/validate_repository.py` and `tools/generate.py` for every parity change.

## Recommended Port Order

| Order | Skill | Reason |
|---:|---|---|
| 1 | `document-writer` | Portable and self-contained; only artifact-contract stability blocks it. |
| 2 | `intake-spec`, `design-feature`, `update-design` | Port together after the design artifact manifest stabilizes. |
| 3 | `erd-preview` | Port after Codex asset-backed artifact packaging is standardized. |

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
- `fix` now closes the bug-repair lane.
- `generate-teammate` now closes the execution-planning lane with a Codex handoff-only equivalent.
- `improve` now closes the behavior-improvement lane.
- `implement` now closes the new-feature implementation lane.
- `manage-skills` now closes the verification-drift maintenance lane at the prompt level.
- `review` now closes the biggest gap between read-only persona critique and production-oriented engineering review.
- `verify-implementation` now closes the verification orchestration lane at the prompt level.
- `persona-review` now matches the Claude command name and the native free-form review contract.
- `pr-writer` ships in both trees with a shared draft-only PR/MR description contract and platform-aware (`gh`/`glab`) context gathering.

## Documented Non-Shared Dispositions

These skills ship in the Claude plugin without a shared `codex/skills/<skill>` symlink.

| Skill | Disposition | Reason |
|---|---|---|
| `harness-manager` | Claude-only | Operates on both hosts' global harnesses and depends on Claude-side workflow semantics. |
| `pr-review` | Claude-only | Its core is parallel multi-agent panel dispatch plus optional confirmed PR posting. |
| `document-writer` | Deferred | Portable renderer; port after the artifact contract settles. |
| `intake-spec`, `design-feature`, `update-design` | Deferred | Portable requirements/design pipeline that is still changing as a unit. |
| `erd-preview` | Deferred | Portable asset-backed generator; defer until the Codex artifact packaging path is standardized. |
| `spec-coverage` | Deferred | Coverage core (test-runner discovery, status/render scripts) is portable via Read/Write/Bash, but the optional PostToolUse auto-render hook is Claude-only; defer Codex shipping until that hook guidance is host-conditioned and smoke-tested. |

## Retired Commands

| Command | Retired | Reason | Migration |
|---|---|---|---|
| `ai-assisted-feature-development` | v3.0.0 (2026-07-22) | Its 9 phases duplicated existing skills: phases 1–5 = `intake-spec` + `design-feature`, phases 6–7 = `implement`, phase 8 = `review`. It wrote artifacts to its own layout, so nothing downstream could consume them, and `disable-model-invocation: false` let it auto-trigger against `intake-spec`. | `/intake-spec` → `/design-feature` → `/implement` → `/review` |
| `skill-dispatcher` | v3.0.0 (2026-07-22) | Duplicated the host's built-in skill discovery plus each skill's own `when_to_use`. | None — the host routes on `description` / `when_to_use`. |
| `design-ui` | v4.0.0 (2026-07-29) | 3 invocations in 67 days. | None — the slot is open; see `docs/plugin-portfolio-hybrid-model.md`. |
| `functional-spec` | v4.0.0 (2026-07-29) | 0 invocations in 22 days. | None — reopen only with a repeatable workflow. |
| `kanban-board` | v4.0.0 (2026-07-29) | Unused; superseded by host task tooling. | None. |
| `finish-branch` | v4.0.0 (2026-07-29) | Unused; `/ship` and plain git covered the same dispositions. | `/pr-writer` for the PR body; plain git for merge/cleanup. |

Removed from both trees in the same change (plugin skill + `codex/skills/` symlink).

## Operating Rule Going Forward

Every new Claude skill requires one of these in the same PR:

- A matching `codex/prompts/<skill>.md`, or
- A documented exception in this file explaining why no Codex equivalent exists.

Every rename must update both trees in the same change. `on-call-elian` should appear only in historical changelog entries or external migration notes.
