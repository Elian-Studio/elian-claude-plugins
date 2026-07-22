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
   There is no repository-wide numeric score gate. Keep YAML frontmatter smoke checks mandatory, and make complex skills own focused validators, fixtures, or examples that prove their workflow still works.

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

## Split decision (2026-06-12)

The dual-tool distribution work built a generator (`tools/generate.py`, manifest `tools/clusters.json`) that can render `elian-store`'s 16 skills into **five composition-respecting thematic plugins** (`elian-artifacts`, `elian-tdd`, `elian-review`, `elian-design`, `elian-harness`) plus a marketplace catalog. The split is **validated and staged in the gitignored `dist/`, but deliberately not published.**

**Decision: keep `elian-store` as the single published plugin.** The split does not meet the bar in Operating Principle 1 — the five clusters share one audience, one permission profile, and one release cadence, so the bundle is not "harmful." Two further reasons:

- **History:** v2.0.0 (2026-04-28) consolidated the per-skill `decision-dashboard` plugin *into* `elian-store`. Publishing the split would reverse that deliberate move.
- **No graceful migration:** the Claude Code marketplace has no `deprecated`/`replaces`/`alias` field. Removing `elian-store` would orphan existing installs (the SessionStart update hook looks for an `elian-store` entry that would be gone → silent; no user notification) and force a manual `uninstall`+`install` (the v2.0.0 precedent).

**Revisit when** a real divergence appears — then split only the cluster that diverges:

- a cluster needs a **different permission profile** (e.g. `elian-harness` mutates global config while `elian-review` is read-only);
- a cluster needs a **different release cadence**;
- real **à-la-carte demand** appears (users want one cluster, not the whole bundle);
- the bundle's install size becomes a concrete user complaint.

**Mechanism when triggered:** run `tools/generate.py --emit`, then publish the *specific* diverging cluster(s) as **new marketplace entries alongside** `elian-store` (coexistence), never a hard cut — there is no graceful removal path. The generator keeps the staged output drift-free against the bundle SSOT.

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
| Feature planning | `intake-spec` + `design-feature` + `update-design` | Covered. `ai-assisted-feature-development` was retired in v3.0.0 — it ran a parallel 9-phase pipeline over the same lanes without sharing the `claudedocs/<label>/` artifact set. |
| UI design | `design-ui` | Covered. Needs stronger browser-visible follow-up lane later. |
| Implementation | `implement` | Covered. Should hand off to review/QA instead of absorbing release behavior. |
| Bug fixing | `fix` | Covered. Keep root-cause-first and regression-test-first posture. |
| Improvement | `improve` | Covered. Keep BEFORE/AFTER evidence and characterization tests. |
| Document rendering | `create-document` | Covered as utility. Keep deterministic and schema/template oriented. |
| Agent/team routing | `generate-teammate` | Covered for Claude. Codex parity should remain limited unless delegation tools exist. |
| Verification orchestration | `verify-implementation` | Covered. Should not pretend to replace QA, review, or release readiness. |
| Skill maintenance | `manage-skills` | Covered. Good place to add drift checks over time. |
| Persona review | `persona-review` | Covered. Keep persona-specific review style, not a forced universal scorecard. |
| Engineering review | `review` | Covered. Keep it read-only, findings-first, and separate from persona review, verification, browser QA, and ship. |
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

1. Add `browser-qa` or `qa`.
   Browser-visible verification for UI and deployed/local web flows. It should produce reproduction steps, screenshots or evidence paths, and regression-test handoff.

2. Add `ship`.
   Release-readiness workflow for branch sanity, local verification, changelog/version checks, push/PR preparation, and final user approval. It should not deploy.

Done:

- `review` exists as the read-only engineering review lane.

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
ruby -EUTF-8 -ryaml -e 'Dir["plugins/elian-store/skills/*/SKILL.md"].sort.each { |p| s=File.read(p, encoding: "UTF-8"); YAML.safe_load(s.split(/^---\s*$/,3)[1] || "", permitted_classes: [], aliases: false); puts "OK #{p}" }'
```

Use broader checks only when the changed skill owns additional scripts, generated assets, or cross-tree behavior.
