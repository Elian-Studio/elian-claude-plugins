# Definition of Done

Use this checklist before implementation handoff and again before merge.

## Planning DoD

1. Feature intent is one sentence and testable.
2. Primary users and use contexts are named.
3. Success criteria are explicit.
4. Non-failure conditions are explicit.
5. Edge cases are listed.
6. Risk level is assigned and justified.
7. BDD scenarios cover normal, failure, and exception flows.
8. Product-policy unknowns are questions, not guesses.
9. Specification defines scope and out of scope.
10. Acceptance criteria are observable.
11. DDD was considered and either applied or rejected with a reason.
12. Test plan exists before implementation.

## Context DoD

1. Required files are listed.
2. Optional files are separated from required files.
3. Existing architecture constraints are listed.
4. No-touch files or behavior are listed.
5. Verification commands are explicit.
6. Protected tests are named.

## Implementation Handoff DoD

1. Agent task has goal, scope, out of scope, and acceptance criteria.
2. Task references the bounded context package.
3. Task forbids weakening or deleting protected tests.
4. Task names the expected verification commands.
5. Task is small enough to review as one PR.

## Review DoD

1. Implementation matches the spec.
2. BDD scenarios are satisfied or explicitly deferred.
3. Failure-path tests exist for risky behavior.
4. Security, permission, and privacy behavior are verified.
5. Performance and accessibility risks are addressed when in scope.
6. No unrelated refactor is bundled.
7. New assumptions are documented.
8. SPDD archive captures useful prompts and decisions.

## Merge Blockers

Block merge when any of these are true:

- Behavior differs from the approved spec.
- Core BDD scenario fails or is untested.
- Failure-path tests are missing for high-risk behavior.
- AI weakened or deleted protected tests.
- Security, permission, privacy, or account boundary policy is unclear.
- Context package omitted required files.
- The implementation introduced a new architecture pattern without approval.
- The PR bundles unrelated large refactors.
