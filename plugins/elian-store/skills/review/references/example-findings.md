# /review Example Findings

Use this reference when the output risks becoming vague or plan-like. The review should be concrete enough that another skill can fix or verify it.

## Checklist

- [ ] Is the target explicit: worktree, staged, branch diff, PR/MR, or path?
- [ ] Are findings ordered by severity?
- [ ] Does every finding have a file/line or a clear evidence gap?
- [ ] Does each finding explain impact, not just style preference?
- [ ] Is the suggested fix concise rather than a full implementation plan?
- [ ] Is the test or verification gap named?
- [ ] Are browser QA, verification, and ship tasks handed off instead of performed?
- [ ] If there are no findings, is residual risk still stated?

## BEFORE / AFTER

### Vague review

BEFORE:

```text
This needs more validation and maybe better tests.
```

Problem: no location, no impact, no handoff.

AFTER:

```text
Findings
- [HIGH] src/orders/createOrder.ts:117 - user-supplied `hospitalId` is trusted after the new fast path.
  Evidence: the branch added in this diff skips `assertUserCanAccessHospital`.
  Impact: a user may create orders for another hospital if they know the ID.
  Suggested fix: run the authorization check before both fast and slow paths.
  Test/verification gap: add a regression test for cross-hospital order creation.
```

### Review that turns into implementation

BEFORE:

```text
I will fix this by changing createOrder, updating the repository, and adding tests.
```

Problem: `/review` is read-only and should hand off execution.

AFTER:

```text
Handoff
- Target: current worktree diff
- Blocking findings: 1 HIGH
- Recommended next skill: /fix
- Required verification: regression test for cross-hospital order creation + existing order-service tests
- Residual risk: related update/delete paths were not reviewed in this quick pass
```

## Severity Examples

| Severity | Example |
|---|---|
| `CRITICAL` | new migration can delete tenant data or auth check is bypassed on a production path |
| `HIGH` | changed API contract breaks existing clients or regression is likely from code evidence |
| `MEDIUM` | risky branch lacks tests, behavior is plausible but needs confirmation |
| `LOW` | naming, readability, or local maintainability issue with limited impact |
| `INFO` | useful note that does not require action |

## No-Findings Example

```text
Findings
- No blocking findings in the reviewed scope.

Reviewed Scope
- `git diff --cached`
- `src/orders/createOrder.ts`
- `src/orders/createOrder.test.ts`

Residual Risk
- Did not run browser QA; no user-visible UI files changed.
- Did not run full project verification; hand off to /verify-implementation before /ship.
```
