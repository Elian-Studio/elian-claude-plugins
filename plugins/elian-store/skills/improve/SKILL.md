---
name: improve
description: "When the user asks to improve an existing feature, optimize behavior, harden edge cases, or runs /improve, drive a BEFORE/AFTER analysis → plan → user approval → TDD improvement protecting existing tests → quantified before/after verification → review → report."
when_to_use: "Use ONLY for behavior-changing improvements to working features (UX polish, perf optimization, edge-case hardening, API extension) invoked via /improve. Do NOT use for new features (use /implement), bugs (use /fix), or behavior-preserving renames / restructures."
argument-hint: "<issue-id> [--side back|front|both] [--step N] [--skip-docs]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git status*), Bash(git branch*), Bash(git diff*), Bash(git log*), Bash(npm test*), Bash(npm run*), Bash(./gradlew test*), Bash(mvn test*), Bash(pytest*), Bash(go test*), Bash(rspec*), AskUserQuestion, Agent
disable-model-invocation: true
---

# /improve — Behavior-changing improvement to working features

This skill is for making something working better. It explicitly distinguishes from `/implement` (new feature) and `/fix` (broken behavior). The signature workflow is BEFORE → plan → approval → TDD with existing-test protection → quantified AFTER comparison.

**Applies to**: UX polish, performance optimization, API extension, edge-case hardening, logic refinement.
**Does not apply to**: new features → `/implement` | bugs → `/fix` | pure refactor with no behavior change.

## Parameters

| Option | Meaning | Default |
|--------|---------|---------|
| `<issue-id>` | Issue identifier (required) | — |
| `--side back\|front\|both` | Limit to one layer | `both` |
| `--step N` | Resume from a specific step | `1` |
| `--skip-docs` | Skip design-doc generation | `false` |

## Workflow

```
Step 0: Project recognition
Step 1: BEFORE snapshot (current behavior + existing tests)
Step 2: Improvement plan (AFTER target + impact + conflict matrix)
Step 3: ★ Approval gate ★
Step 4: TDD improvement (protect existing tests; add new expectations)
Step 5: BEFORE/AFTER comparison verification
Step 6: Code review
Step 7: Completion report
```

### Step 0: Project recognition

Read `CLAUDE.md` plus any `*/CLAUDE.md` for tech stack, build / test commands, conventions.

### Step 1: BEFORE snapshot

1. `git status && git branch --show-current` — main → prompt for feature branch.
2. Look for design docs at `**/docs/**/$ARGUMENTS[0]/**/*.md`.
3. **Capture current behavior**: per item, the current state, the problem, the existing test coverage, and dependencies.

> If existing tests are missing, **Characterization Tests** are a Step 4 prerequisite — they pin current behavior so the improvement doesn't silently regress it.

### Step 2: Improvement plan

1. **Decompose** the request into improvement units (each with BEFORE / AFTER target / changed files / dependencies).
2. **Conflict matrix** (multi-improvement): identify file overlap.
3. **Impact analysis**: direct changes / indirect (callers) / risk (low / medium / high).
4. **Execution strategy** (use [../_shared/execution-strategy.md](../_shared/execution-strategy.md)).
5. **Rollback criteria**: define explicitly — when do we revert?

Templates: [references/templates.md](references/templates.md).

### Step 3: ★ Approval gate ★

`AskUserQuestion` with options approve / modify / cancel. **No Step 4 without approval.**

### Step 4: TDD improvement

**Protect existing tests first** — don't break green tests while adding new expectations:

1. Run existing tests (Green confirmation) — if Red, switch to `/fix`.
2. Write Characterization Tests if existing test coverage is insufficient.
3. **New-expectation test (Red)** for the target AFTER state.
4. **Code change (Green)**.
5. Run **existing + new** tests — both must pass.
6. Refactor with green tests as safety net.
7. Incremental commit per improvement unit via `/commit`.

For parallel multi-improvement, use the spawn prompt template in [references/templates.md](references/templates.md).

### Step 5: BEFORE/AFTER comparison verification

1. Run project verify skills (`/verify-backend`, `/verify-frontend`, etc.).
2. **BEFORE/AFTER table**: per item, did the AFTER target hold?
3. Rollback decision:
   - All achieved → Step 6
   - Partial → ask user
   - Existing behavior broken → immediate rollback

### Step 6: Code review

`/simplify` for quality. `/code-reviewer` for deep analysis when scope warrants. Stage review fixes via `/commit`.

### Step 7: Completion report

See [references/templates.md](references/templates.md). Required:
- Summary (file counts, test counts, commit counts)
- **BEFORE/AFTER comparison** quantified where possible
- Per-improvement outcome
- Verification results
- Next steps

## Standing Rules

- **Existing tests are the contract.** Improvements must keep them green. Breaking them = hidden regression.
- **Characterization Tests when coverage is thin.** Pin behavior before changing it; otherwise the improvement may silently change semantics.
- **BEFORE / AFTER must be measurable.** "Better UX" without a metric is unverifiable. State the metric (latency, error rate, conversion, click count) before Step 4.
- **Approval-gated**: Step 3 must complete.
- **Rollback criterion explicit**: defined in Step 2, monitored through Step 5.
- **Improvement vs feature vs fix**: if scope leaks into new functionality, switch to `/implement`; if it's actually broken, switch to `/fix`. Don't smuggle.

## Procedure (one-time)

`/improve <issue-id>` runs Step 0 → 7. Resume with `--step N`.

## Forbidden

- ❌ Editing existing tests to accommodate a behavior change without explicit acknowledgement. The test is the contract.
- ❌ Skipping Characterization Tests when coverage is thin. You'll regress and not notice.
- ❌ Skipping Step 5 quantified comparison. "Looks better" isn't verifiable.
- ❌ Skipping Step 3 approval. Improvement scope is taste-laden; user owns it.
- ❌ Adding new features under the guise of improvement. Re-route to `/implement`.
- ❌ Bundling multiple improvements without isolation. One improvement = one commit.
- ❌ Applying a perf optimization to a cold path. Measure first; optimize the 10%.
- ❌ Premature abstraction "while I'm in there." Three duplicates first; abstract later.

## Pitfall / Known Issues

| Pitfall | Why it happens | Fix |
|---------|----------------|-----|
| Existing tests start failing after improvement | Behavior changed beyond the stated AFTER target | Re-read the existing test; if assertion is still right, your change is wrong; if assertion is now wrong, update it explicitly with reason |
| BEFORE/AFTER metric drifts | Measured under different conditions | Capture environment (data size, hardware, traffic shape) on both sides |
| Perf "improved" but feature slow on real data | Bench used synthetic data | Bench with production-shaped data |
| Refactor smuggled into improvement | Hard to resist when reading old code | Separate commit; if it grows, separate PR |
| AFTER state needs design changes | Improvement edges into new feature | Stop, switch to /implement, get design alignment |
| User wants "everything better" | Vague brief | Force item-level decomposition in Step 2; refuse to proceed without metrics |

For failure recovery: every Step has a fail action — Step 1 fail (no test coverage) → Characterization Tests; Step 4 fail (existing tests break) → revert and re-plan; Step 5 fail (target not met) → roll back unit; ask the user before keeping a partial improvement.

## Where this fits in the workflow

```
working feature → /improve → /review → /ship
                     │
                     └── Pre: feature works; metric or pain point identified.
                         Post: PR-ready improvement + before/after evidence.
```

Sequencing principles:
- **Before** /improve: have a baseline measurement or a clear UX pain.
- **During** /improve: quantified comparison is non-optional.
- **After** /improve: hand off to /review, /ship; capture metric in dashboard for ongoing tracking.

## Manual decision gating (automated vs taste)

| Concern | Automated | Needs user taste |
|---------|-----------|------------------|
| Project recognition | ✅ | — |
| Improvement decomposition | ✅ | — |
| Existing-test inventory | ✅ | — |
| Characterization Test drafting | ✅ | — |
| Conflict matrix | ✅ | — |
| Strategy selection per shared rules | ✅ | — |
| Approval to proceed past Step 3 | — | ✅ |
| AFTER target metric definition | drafted automatically | ✅ user reviews |
| Whether a partial improvement is shippable | — | ✅ |
| Scope leakage decision (improve vs implement vs fix) | flagged | ✅ user decides |

## Reflection (end of skill)

Write 3 short observations into `claudedocs/{issueId}-improve-reflection.md`:

1. **Coverage gap revealed** — did Characterization Tests expose poor coverage? If so, propose a coverage initiative.
2. **Metric movement** — quantified delta between BEFORE and AFTER. Is the magnitude worth the change cost?
3. **Sibling improvement candidates** — same pattern likely improvable elsewhere? Capture as follow-up.

## Persistent artifacts for downstream

| Artifact | Producer step | Downstream consumer |
|----------|---------------|---------------------|
| BEFORE snapshot | Step 1 | Post-improvement comparison; future regressions |
| Improvement plan + conflict matrix | Step 2 | /review (knows scope of each unit) |
| Characterization Tests + new tests | Step 4 | CI; future improvement attempts |
| BEFORE/AFTER quantified table | Step 5 | /ship (decision); dashboards (ongoing) |
| Completion report | Step 7 | Retro; cost / benefit analysis |

## BEFORE / AFTER patterns

### Vague vs measurable improvement

❌ **BEFORE**:

> "Make the dashboard faster."

No baseline. No target. No way to verify success.

✅ **AFTER**:

```
Improvement: Dashboard initial render
- BEFORE: p95 first-contentful-paint = 2.4s (Lighthouse, 4G throttling, 100 rows)
- AFTER target: p95 FCP ≤ 1.0s, same conditions
- Strategy: virtualize the row list, defer non-critical CSS, lazy-load charts
```

Measurable, falsifiable, scoped.

### Untested improvement vs Characterization-protected

❌ **BEFORE**:

```
Existing tests: 0 (legacy code)
Improvement: rewrite the formatter
Result: tests still 0, no regression detection, scary
```

✅ **AFTER**:

```
Step 1: Existing tests 0
Step 4 prerequisite: Characterization Tests written first
  → 8 tests pinning current behavior on representative inputs
Step 4: Improvement implemented; all 8 + new tests green
```

The improvement now sits on a safety net.

### Symptom-treating "improvement" vs root-pattern improvement

❌ **BEFORE**:

```
"Slow because of N+1 query in OrderService."
Fix: add eager loading just there.
```

Five other services have the same N+1 pattern; they'll surface in the next sprint.

✅ **AFTER**:

```
Step 2: search for similar patterns → 6 sites identified
Step 4: improve each, with Characterization Tests
Step 5: aggregate latency improvement reported across all sites
```

Same effort, much wider payoff.

## Skill verification

```bash
python3 [scripts/validate_skill.py](scripts/validate_skill.py)
python3 [scripts/validate_skill.py](scripts/validate_skill.py) --json
```

## Pre-flight checklist

Before Step 4 (TDD improvement):
- [ ] Project recognized
- [ ] BEFORE snapshot captured (per improvement unit)
- [ ] AFTER target stated as a measurable metric
- [ ] Existing test coverage assessed; Characterization Tests if needed
- [ ] Conflict matrix built (multi-improvement)
- [ ] Strategy chosen with cited rationale
- [ ] Rollback criteria explicit
- [ ] User approved via AskUserQuestion (Step 3)

## Skill integrations

| Skill | Step |
|-------|------|
| `/commit` | Step 4 — incremental commits (mandatory) |
| `/verify-*` | Step 5 — integration verification |
| `/simplify` | Step 6 — self-review |
| `/generate-teammate` | Step 4 — 4+ improvements warrant a team |
| `/defer` | Out-of-scope discoveries |

## Exceptions

1. **1-2 file improvement**: parallel not needed; still TDD.
2. **Performance improvement with strong existing tests**: Characterization Tests can be skipped.
3. **Zero existing tests**: Characterization Tests are non-negotiable.
4. **Improvement effect not measurable**: fall back to qualitative comparison; state explicitly in report.
