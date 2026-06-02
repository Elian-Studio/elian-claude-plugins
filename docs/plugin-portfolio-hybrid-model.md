# Plugin Portfolio Hybrid Model

Date: 2026-06-02

## Decision

This repository manages `elian-store` as a hybrid plugin portfolio:

- Anthropic-style distribution: keep a clear marketplace/plugin boundary and a stable install/update path.
- Vercel-style skill packages: keep each skill self-contained, progressively disclosed, script-backed where useful, and locally verifiable.
- gstack-style lifecycle portfolio: manage the skill set as a workflow map from intent to implementation, review, QA, release, and learning.

Do not copy every pattern from the reference repositories. Adopt a pattern only when this repository has a concrete workflow, validation path, and artifact contract for it.

## Reference Roles

| Reference | What to borrow | What not to copy blindly |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) and [Agent Skills spec](https://agentskills.io/specification) | `SKILL.md` as the core unit, marketplace metadata, simple install/update story, progressive disclosure. | Splitting the current single bundle into many plugins before there is a user-facing need. |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | Skill package discipline: `scripts/`, `references/`, focused descriptions, JSON-friendly scripts, targeted CI. | Large generated rule catalogs unless the target skill truly needs that much rule volume. |
| [garrytan/gstack](https://github.com/garrytan/gstack) | Lifecycle coverage, specialist role clarity, workflow sequencing, QA/release/learning gaps as portfolio-level roadmap input. | A broad slash-command OS with many commands before this repo has matching local workflows. |

## Repository Shape

Keep the current shape unless a concrete workflow proves it insufficient:

```text
.claude-plugin/
  marketplace.json
plugins/
  elian-store/
    .claude-plugin/
      plugin.json
    agents/
    hooks/
    skills/
      <skill-name>/
        SKILL.md
        scripts/
        references/
        assets/ or templates/
codex/
  AGENTS.md
  prompts/
```

`plugins/elian-store` remains the primary Claude Code plugin. `codex/` remains an independent sibling tree, not a generated mirror, until a separate source-of-truth decision is made.

## Operating Principles

1. Keep one bundle by default.
   `elian-store` is the install unit. Add a second plugin only when a different audience, permission profile, or release cadence makes the bundle harmful.

2. Treat every skill as a package.
   A skill should have one clear job, a compact `SKILL.md`, and supporting files loaded only when needed. Use `references/` for deeper guidance and `scripts/` for deterministic checks or transformations.

3. Validate before expanding.
   Existing gates stay mandatory: `scripts/score_skill.py`, `scripts/score_codex_prompt.py`, and YAML frontmatter smoke checks. New complex skills should add their own focused validator or example fixture.

4. Manage the portfolio by lifecycle position.
   Every skill must declare where it fits: intent shaping, decision, planning, design, implementation, fix, improvement, review, QA, release, learning, or maintenance.

5. Preserve artifact continuity.
   A skill output should be useful downstream when possible: JSON, Markdown, HTML report, review findings, QA evidence, verification manifest, or a documented handoff.

6. Gate side effects.
   Destructive changes, release actions, external service changes, and taste-heavy decisions require explicit user approval. Side-effect skills should not auto-trigger.

7. Keep Claude/Codex drift visible.
   If a skill exists in both trees, PRs should review both versions together. If only one tree is updated, the PR should state whether parity is intentionally deferred.

8. Avoid shallow command growth.
   A lifecycle gap is not enough reason to add a skill. Add one only when it has a repeatable workflow, clear boundary, expected output, and verification method.

## Skill Intake Checklist

Before adding or materially changing a skill, answer:

- What user situation triggers this skill?
- Which lifecycle slot does it occupy?
- Which existing skill does it overlap with, and why is a separate skill still justified?
- What artifact does it produce or update?
- What does it refuse to do?
- What verification command or fixture proves it still works?
- Does it require `disable-model-invocation: true`?
- Does it require plugin version, marketplace, README, CHANGELOG, or Codex parity updates?

## Lifecycle Map

| Lifecycle slot | Current coverage | Status |
|---|---|---|
| Intent shaping | `brainstorm` | Exists, but keep its core as thought clarification, not forced handoff. |
| Decision artifact | `decision-dashboard` | Strong. Preserve narrow scope and downstream JSON. |
| Feature planning | `ai-assisted-feature-development` | Strong structure. Keep as AI-assisted development orchestration, with execution boundary explicit. |
| UI design | `design-ui` | Covered. Needs stronger browser-visible follow-up lane later. |
| Implementation | `implement` | Covered. Should hand off to review/QA instead of absorbing release behavior. |
| Bug fixing | `fix` | Covered. Keep root-cause-first and regression-test-first posture. |
| Improvement | `improve` | Covered. Keep BEFORE/AFTER evidence and characterization tests. |
| Document rendering | `create-document` | Covered as utility. Keep deterministic and schema/template oriented. |
| Agent/team routing | `generate-teammate` | Covered for Claude. Codex parity should remain limited unless delegation tools exist. |
| Verification orchestration | `verify-implementation` | Covered. Should not pretend to replace QA, review, or release readiness. |
| Skill maintenance | `manage-skills` | Covered. Good place to add drift checks over time. |
| Persona review | `persona-review` | Covered. Keep persona-specific review style, not a forced universal scorecard. |
| Engineering review | Missing | High-priority gap. |
| Browser QA | Missing | High-priority gap for UI/user-visible flows. |
| Ship/PR readiness | Missing | High-priority gap, separate from implementation. |
| Learning/retro | Missing | Medium-priority gap after workflows stabilize. |
| Security review | Missing | Medium-priority gap after review and QA foundations. |
| Benchmark/performance | Missing | Later gap unless a concrete regression workflow exists. |
| Deploy/canary | Missing | Later gap unless deployment targets are known. |

## Roadmap

### P0: Stabilize Portfolio Management

- Add this hybrid model as the portfolio-level decision record.
- Keep `docs/gstack-skill-review.md` as lifecycle gap input, but do not treat gstack as a command checklist.
- Revisit stale purpose wording before routing wording when changing existing skills.
- Keep generated evaluation outputs ignored and out of commits.

### P1: Close Core Workflow Gaps

1. Add `review`.
   Read-first engineering review for bugs, regressions, missing tests, and production risks. It should produce findings and optionally propose fixes only after approval.

2. Add `browser-qa` or `qa`.
   Browser-visible verification for UI and deployed/local web flows. It should produce reproduction steps, screenshots or evidence paths, and regression-test handoff.

3. Add `ship`.
   Release-readiness workflow for branch sanity, local verification, changelog/version checks, push/PR preparation, and final user approval. It should not deploy.

### P2: Add Learning and Risk Controls

- Add `learn` or `retro` only after repeated workflow outcomes produce reusable patterns worth capturing.
- Add `security-review` after `review` exists, so security findings have a compatible reporting contract.
- Extend `manage-skills` with portfolio drift checks: lifecycle slot, duplicate purpose, missing validator, missing downstream artifact.

### P3: Add Operational Follow-through

- Add benchmark/performance only when there are repeatable metrics and before/after fixtures.
- Add deploy/canary only when real deployment targets, credentials boundaries, and rollback expectations are documented.

## Maintenance Rules

- For plugin-distributed changes, update `plugin.json`, root marketplace metadata, README, and CHANGELOG together when versioned behavior changes.
- For docs-only portfolio decisions, prefer a docs PR without version bump unless installed plugin behavior changes.
- Run the smallest meaningful verification first:

```bash
python3 scripts/score_skill.py plugins/elian-store/skills/*/SKILL.md
python3 scripts/score_codex_prompt.py codex/prompts/*.md
ruby -EUTF-8 -ryaml -e 'Dir["plugins/elian-store/skills/*/SKILL.md"].sort.each { |p| s=File.read(p, encoding: "UTF-8"); YAML.safe_load(s.split(/^---\s*$/,3)[1] || "", permitted_classes: [], aliases: false); puts "OK #{p}" }'
```

Use broader checks only when the changed skill owns additional scripts, generated assets, or cross-tree behavior.
