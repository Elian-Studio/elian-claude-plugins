# Claude / Codex Skill Parity Review

Date: 2026-05-28

## Goal

Make the Claude plugin catalog and Codex prompt catalog use the same command names, intent boundaries, and quality gates where the platforms allow it.

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
- Both pass their local gates:
  - Claude: `python3 scripts/score_skill.py plugins/elian-store/skills/*/SKILL.md`
  - Codex: `python3 scripts/score_codex_prompt.py codex/prompts/*.md`

## Current Parity Status

| Area | Claude | Codex | Status |
|---|---:|---:|---|
| Catalog entries | 13 skills | 1 prompt | Not equal |
| Command naming | `/elian-store:<skill>` | `/<prompt-file>` | Mostly alignable |
| Current matched command | `persona-review` | `persona-review` | Aligned |
| Legacy `on-call-elian` | Removed from current Claude skill catalog | Removed from current Codex prompt catalog | Aligned |
| Quality gate | 13/13 pass | 1/1 pass | Passing, but asymmetric |

Current conclusion: **the two trees are not identical yet**. The name drift around `on-call-elian` is fixed, but 12 Claude skills have no Codex prompt counterpart.

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
| `brainstorm` | Clarify fuzzy requests through context, Socratic probing, options, tradeoff, decision, handoff | Good | Scope boundary is clear: ambiguous requests only; excludes clear implementation and confirmed bugs. | Missing |
| `ai-assisted-feature-development` | Produce intent/spec/test/context/task/review artifacts before AI coding | Mostly good | Purpose is planning, not implementation. Because it can write artifacts and has broad triggers, Codex/Claude parity should keep explicit review gates. Consider whether auto invocation should remain enabled. | Missing |
| `implement` | Build new features through TDD with approval gates | Good | Clear separation from `fix` and `improve`; side-effect posture is correctly non-auto. | Missing |
| `fix` | Repair confirmed bugs with root-cause analysis and regression test first | Good | Clear exclusion of new features and improvements; matches bug-repair purpose. | Missing |
| `improve` | Make behavior-changing improvements to working features | Good | Correctly excludes new features, bugs, and behavior-preserving refactors. | Missing |
| `design-ui` | Produce UI/UX design artifacts through interview, reference, wireframe, gate, visual | Mostly good | Purpose is clear. Since it can write design artifacts and fetch references, Codex parity should preserve explicit gates before visual generation. | Missing |
| `decision-dashboard` | Turn 3+ blocking decisions into a printable decision artifact and JSON | Good | Purpose is narrow and artifact-driven. Watch the cleanup permission pattern in Claude (`rm claudedocs/*`) if expanded. | Missing |
| `generate-teammate` | Decide direct/subagent/team execution and generate teammate/task prompts | Platform-specific | Claude can use Agent/Team tools; Codex prompt can only produce a plan unless a Codex-side delegation system exists. Same command can be mirrored, but runtime behavior cannot be identical today. | Missing |
| `create-document` | Deterministically render schema-validated JSON into HTML/MD templates | Good utility | This is closer to a shared script wrapper than a conversational skill. Codex parity should call the same scripts rather than duplicate rendering logic in prose. | Missing |
| `manage-skills` | Detect and repair verify-skill drift | Good, but Claude-specific | Assumes Claude-style `.claude/skills/verify-*` maintenance. Codex mirror should define whether it maintains Codex prompts, Claude skills, or both. | Missing |
| `verify-implementation` | Discover and run project verify-* skills before shipping | Good, but Claude-specific | Purpose is correct for projects that have verify-* skills. Codex parity needs a separate discovery rule for Codex prompt validators or explicitly keeps this as Claude-only. | Missing |
| `persona-review` | Review plans/docs/ideas through selected persona lenses with persona-native output | Mostly aligned | Claude and Codex names now match and include the same default persona choices (`daniel`, `evans`, `dean`, `martin`, custom path). Claude now uses persona-specific subagents and free-form persona output; Codex remains a prompt-only port and should be refreshed to remove any legacy fixed-template assumptions. | Present, drift risk |
| `review` | Read-only engineering review of code, diffs, PRs, or changed files with findings-first output | Good | New Claude skill fills the engineering review lane. Codex parity should be read-only and can preserve the same findings-first contract without Agent-based lenses unless Codex delegation exists. | Missing |

## Required Work To Make Them Identical

Minimum parity work:

1. Add Codex prompt counterparts for the 12 missing Claude skills.
2. Keep command names exactly equal to Claude skill directory names.
3. For side-effect skills (`implement`, `fix`, `improve`, `manage-skills`, `verify-implementation`), convert Claude `AskUserQuestion` and tool-gate behavior into Codex "ask and stop" instructions.
4. For utility skills (`create-document`, `decision-dashboard`), call shared scripts/templates instead of duplicating generated output logic in prompt prose.
5. For Claude-only runtime skills (`generate-teammate`, parts of `verify-implementation`), document the Codex limitation in the prompt and make the Codex version produce a handoff plan rather than pretending to spawn agents.
6. Keep `scripts/score_codex_prompt.py` generic. Skill-specific contracts should be validated without forcing unrelated prompts into the same output shape.

## Recommended Port Order

| Order | Prompt | Reason |
|---:|---|---|
| 1 | `review` | Read-only, findings-first, low mutation risk; strongest immediate Codex parity candidate. |
| 2 | `brainstorm` | Read-heavy, conversational, low risk; good template for Codex ask-and-wait behavior. |
| 3 | `ai-assisted-feature-development` | Planning artifact skill; useful without direct code mutation. |
| 4 | `design-ui` | Artifact-generating but can be gated clearly. |
| 5 | `implement`, `fix`, `improve` | Core code-changing trio; needs careful approval wording. |
| 6 | `decision-dashboard`, `create-document` | Should share deterministic scripts/templates; avoid prompt-only reimplementation. |
| 7 | `manage-skills`, `verify-implementation` | Needs a cross-tool definition of what gets verified. |
| 8 | `generate-teammate` | Most platform-specific because Claude Agent/Team tools do not have a direct Codex equivalent here. |

## Recommended New-Skill Order From gstack Review

These are new Claude skill candidates, not Codex parity ports:

| Order | Skill candidate | Reason |
|---:|---|---|
| 1 | `qa` or `browser-qa` | Adds browser-visible verification with screenshots/reports before release. |
| 2 | `ship` | Separates branch/test/PR release readiness from implementation. |
| 3 | `learn` or `retro` | Captures repeated preferences and workflow lessons after real usage. |

Completed:

- `review` now closes the biggest gap between read-only persona critique and production-oriented engineering review.

## Operating Rule Going Forward

Every new Claude skill requires one of these in the same PR:

- A matching `codex/prompts/<skill>.md`, or
- A documented exception in this file explaining why no Codex equivalent exists.

Every rename must update both trees in the same change. `on-call-elian` should appear only in historical changelog entries or external migration notes.
