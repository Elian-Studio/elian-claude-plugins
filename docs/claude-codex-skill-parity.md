# Claude / Codex Skill Parity Review

Date: 2026-06-02

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
| Catalog entries | 13 skills | 10 prompts | Not equal |
| Command naming | `/elian-store:<skill>` | `/<prompt-file>` | Mostly alignable |
| Current matched commands | `ai-assisted-feature-development`, `brainstorm`, `create-document`, `decision-dashboard`, `design-ui`, `fix`, `improve`, `implement`, `review`, `persona-review` | `ai-assisted-feature-development`, `brainstorm`, `create-document`, `decision-dashboard`, `design-ui`, `fix`, `improve`, `implement`, `review`, `persona-review` | Aligned |
| Legacy `on-call-elian` | Removed from current Claude skill catalog | Removed from current Codex prompt catalog | Aligned |
| Validation | YAML + skill-owned validators where present | Prompt/config review | Asymmetric, manual |

Current conclusion: **the two trees are not identical yet**. The name drift around `on-call-elian` is fixed, `ai-assisted-feature-development`, `brainstorm`, `create-document`, `decision-dashboard`, `design-ui`, `fix`, `improve`, `implement`, `review`, and `persona-review` now match on command name and output contract, but 3 Claude skills still have no Codex prompt counterpart.

## gstack Portfolio Lens

[`docs/gstack-skill-review.md`](gstack-skill-review.md) adds a portfolio-level check based on `garrytan/gstack`. That review is separate from one-to-one Claude/Codex parity:

| Lifecycle lane | Current Claude coverage | Current Codex coverage | Status |
|---|---|---|---|
| Product/spec planning | `brainstorm`, `ai-assisted-feature-development`, `decision-dashboard` | Missing | Partial |
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
| `ai-assisted-feature-development` | Produce intent/spec/test/context/task/review artifacts before AI coding | Mostly good | Codex now shares the same planning-first artifact flow, though it emits artifacts in response rather than writing them to repo files. Keep the phase gates and review discipline intact. | Present |
| `implement` | Build new features through TDD with approval gates | Good | Codex now preserves the approval-gated TDD flow and explicit file ownership before execution. | Present |
| `fix` | Repair confirmed bugs with root-cause analysis and regression test first | Good | Codex now preserves root-cause-first repair, regression-test-first repair, and sibling-site search. | Present |
| `improve` | Make behavior-changing improvements to working features | Good | Codex now preserves BEFORE/AFTER measurement and existing-test protection. | Present |
| `design-ui` | Produce UI/UX design artifacts through interview, reference, wireframe, gate, visual | Mostly good | Codex now shares the same brief -> reference -> wireframe -> gate -> visual flow. Keep the gate explicit and preserve the artifact set. | Present |
| `decision-dashboard` | Turn 3+ blocking decisions into a printable decision artifact and JSON | Good | Codex now preserves the JSON-first / HTML-second contract and the `generate` / `finalize` flow. Keep the memo requirement for `Other` explicit. | Present |
| `generate-teammate` | Decide direct/subagent/team execution and generate teammate/task prompts | Platform-specific | Claude can use Agent/Team tools; Codex prompt can only produce a plan unless a Codex-side delegation system exists. Same command can be mirrored, but runtime behavior cannot be identical today. | Missing |
| `create-document` | Deterministically render schema-validated JSON into HTML/MD templates | Good utility | Codex now preserves the validate-first rendering contract and the supported template set. Keep the legacy fixed five-block renderer out of the active path. | Present |
| `manage-skills` | Detect and repair verify-skill drift | Good, but Claude-specific | Assumes Claude-style `.claude/skills/verify-*` maintenance. Codex mirror should define whether it maintains Codex prompts, Claude skills, or both. | Missing |
| `verify-implementation` | Discover and run project verify-* skills before shipping | Good, but Claude-specific | Purpose is correct for projects that have verify-* skills. Codex parity needs a separate discovery rule for Codex prompt validators or explicitly keeps this as Claude-only. | Missing |
| `persona-review` | Review plans/docs/ideas through selected persona lenses with persona-native output | Aligned | Claude and Codex now share the same command name, default persona choices (`daniel`, `evans`, `dean`, `martin`, custom path), interview mode, and free-form review contract. Claude still uses persona-specific subagents; Codex keeps the same judgment shape in-process without Claude Agent tools. | Present |
| `review` | Read-only engineering review of code, diffs, PRs, or changed files with findings-first output | Good | Codex now shares the same findings-first contract and read-only boundary. Keep the target/diff/line evidence discipline aligned with the Claude skill. | Present |

## Required Work To Make Them Identical

Minimum parity work:

1. Add Codex prompt counterparts for the 3 remaining Claude skills.
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

- `ai-assisted-feature-development` now closes the biggest gap in the pre-implementation planning lane.
- `brainstorm` now closes the biggest gap in the planning/discovery lane.
- `create-document` now closes the JSON-to-artifact rendering lane.
- `decision-dashboard` now closes the decision-dashboard generation lane.
- `design-ui` now closes the biggest gap in the UX design artifact lane.
- `fix` now closes the bug-repair lane.
- `improve` now closes the behavior-improvement lane.
- `implement` now closes the new-feature implementation lane.
- `review` now closes the biggest gap between read-only persona critique and production-oriented engineering review.
- `persona-review` now matches the Claude command name and the native free-form review contract.

## Operating Rule Going Forward

Every new Claude skill requires one of these in the same PR:

- A matching `codex/prompts/<skill>.md`, or
- A documented exception in this file explaining why no Codex equivalent exists.

Every rename must update both trees in the same change. `on-call-elian` should appear only in historical changelog entries or external migration notes.
