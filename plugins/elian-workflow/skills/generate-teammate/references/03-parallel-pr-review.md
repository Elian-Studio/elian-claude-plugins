# Example 3: Parallel Multi-Lens PR Review

A pure **Subagent** scenario — multi-perspective review where reviewers don't need to talk to each other. Demonstrates that not every multi-perspective task needs an Agent Team.

This contrasts with Example 2: there, hypotheses must rebut each other. Here, reviewers operate independently and the lead aggregates.

---

## Input

```
/generate-teammate Review PR #142 from multiple lenses: security, performance, tests, design, and adversarial.
```

---

## Phase 1: Request Analysis

```typescript
{
  domain: 'review',
  techStack: ['<inferred from the PR diff>'],
  deliverables: ['security findings', 'performance findings', 'test gap report', 'design QA', 'adversarial findings'],
  constraints: ['must finish before merge'],
  parallelizableUnits: ['security review', 'performance review', 'test review', 'design QA', 'adversarial']
}
```

---

## Phase 2: Decomposition

```
┌────────────┬────────────────────────────────┬──────────────────────────────────────┐
│   Phase    │            Content              │           Characteristics            │
├────────────┼────────────────────────────────┼──────────────────────────────────────┤
│ A: Review  │ Independent multi-lens passes   │ Independent, no debate needed,       │
│            │                                 │ aggregating findings is enough       │
└────────────┴────────────────────────────────┴──────────────────────────────────────┘
```

---

## Phase 3: Approach Decision

```
┌────────────┬───────────────┬───────────────────┬───────────────┬──────────────────────────────────┐
│   Phase    │  Agent Team   │    Subagent       │   Direct      │              Reason              │
├────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ A: Review  │ Possible      │ ★ Fit             │ Possible      │ Reviewers don't need to talk.    │
│            │               │                   │               │ Each writes a finding file. Lead │
│            │               │                   │               │ aggregates. Team adds overhead   │
│            │               │                   │               │ without benefit.                 │
└────────────┴───────────────┴───────────────────┴───────────────┴──────────────────────────────────┘

Strategy: single — Subagent (parallel)
```

> **When would this become Agent Team instead?**
> If reviewers must reconcile contradictory recommendations (e.g., "add validation" vs "that validation is in a hot path; performance regression"), they need real-time tradeoff debate → Agent Team. The decision is about coordination need, not the number of reviewers.

---

## Phase 4-5: Subagent Plan

| Subagent | subagent_type | Output file |
|----------|---------------|-------------|
| sec-reviewer | security-engineer | `claudedocs/pr-142/security.md` |
| perf-reviewer | performance-engineer | `claudedocs/pr-142/performance.md` |
| test-reviewer | quality-engineer | `claudedocs/pr-142/test-gaps.md` |
| design-reviewer | ui-ux-designer | `claudedocs/pr-142/design-qa.md` |
| adversarial | devil-advocate | `claudedocs/pr-142/adversarial.md` |

No file conflicts; each owns its own output file.

---

## Phase 6: Confirmation Output

```
Subagent execution plan:

[parallel] 5 reviewers
├── security-engineer    → claudedocs/pr-142/security.md
├── performance-engineer → claudedocs/pr-142/performance.md
├── quality-engineer     → claudedocs/pr-142/test-gaps.md
├── ui-ux-designer       → claudedocs/pr-142/design-qa.md
└── devil-advocate       → claudedocs/pr-142/adversarial.md

[sequential] Lead aggregates → claudedocs/pr-142/review-summary.md
```

---

## Phase 7: Execution (sketch)

```typescript
const reviews = await Promise.all([
  Agent({ subagent_type: 'security-engineer', prompt: prompt('security', diff) }),
  Agent({ subagent_type: 'performance-engineer', prompt: prompt('performance', diff) }),
  Agent({ subagent_type: 'quality-engineer', prompt: prompt('tests', diff) }),
  Agent({ subagent_type: 'ui-ux-designer', prompt: prompt('design', diff) }),
  Agent({ subagent_type: 'devil-advocate', prompt: prompt('adversarial', diff) }),
]);

// Lead synthesizes
synthesize(reviews); // → claudedocs/pr-142/review-summary.md
```

---

## Spawn prompt example (sec-reviewer)

```
You are a security reviewer.

[ROLE]
Review PR #142 from a security lens only. Output structured findings.

[INPUT]
- PR diff: produced by `gh pr diff 142` (run it yourself)
- Changed files: <list>

[FOCUS]
- OWASP Top 10
- Auth / authz changes
- Input validation at system boundaries
- Secret leakage
- Cryptographic correctness
- AI / LLM-specific risks if applicable

[OUTPUT]
Write findings to claudedocs/pr-142/security.md in this format:

# Security review — PR #142

## Summary
{1-3 sentences: overall risk posture}

## Findings

### [SEVERITY] file:line — summary
**Reproduction**: ...
**Impact**: ...
**Fix**: ...
**Evidence**: ...

(Repeat per finding. Severity: CRITICAL / HIGH / MEDIUM / LOW / INFO.)

## Out-of-scope observations
{Things the diff didn't introduce but you noticed}

[DEFINITION OF DONE]
- File saved at claudedocs/pr-142/security.md
- Every CRITICAL / HIGH finding has reproduction + fix
- Severity rubric followed (don't escalate or downplay)

[CONSTRAINT]
- Read-only on the source. Do not edit.
- Output the file location only when done.
```

---

## Lead aggregation

```typescript
const summary = `
# PR #142 Review Summary

## Critical issues (must fix before merge)
${extract(reviews, 'CRITICAL')}

## High issues (should fix)
${extract(reviews, 'HIGH')}

## Medium / low issues
${extract(reviews, 'MEDIUM', 'LOW')}

## Conflicts between reviewers
${detectConflicts(reviews)}
`;
```

If `detectConflicts` finds an issue (e.g., security wants strict validation, performance flags the same code as a hot path), the lead can decide to:
- Resolve directly (read both findings, pick a tradeoff)
- Spawn a **2-person Agent Team** (security-engineer + performance-engineer) to negotiate

This is when a hybrid kicks in: Subagent review → Agent Team conflict resolution → final decision.

---

## Why Subagent (not Agent Team) here

- Reviewers don't need each other's findings during their own review.
- Aggregating the final docs is a synthesis problem, not a debate problem.
- Lower token cost (each reviewer summarizes back; main context isn't flooded).
- Simpler spawn / shutdown lifecycle.

This is the same shape as `/generate-mr` and similar review pipelines.
