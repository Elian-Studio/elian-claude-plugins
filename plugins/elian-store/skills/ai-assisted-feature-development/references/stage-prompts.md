# Stage Prompts

Use these prompts when running one phase at a time.

## Phase 1: Feature Framing

```text
Frame this feature before implementation.

Input:
- Feature:
- Users:
- Constraints:
- Tech stack:
- Known risks:

Output:
1. One-sentence intent.
2. Primary users and use contexts.
3. Success criteria.
4. Conditions that must not fail.
5. Edge cases.
6. Security, permission, privacy, performance, and accessibility risk.
7. Recommended phase depth.
8. Questions to answer before implementation.
```

## Phase 2: BDD

```text
Convert the framed feature into BDD scenarios.

Rules:
- Use Given/When/Then.
- Include normal, failure, and exception flows.
- Separate policy questions from assumptions.
- Do not invent business policy.

Output:
- Feature statement.
- Scenario list.
- Policy questions.
```

## Phase 3: SDD

```text
Write the feature specification.

Include:
- Purpose.
- Scope and out of scope.
- Roles and permissions.
- Inputs and outputs.
- UI/API behavior.
- State changes.
- Error policy.
- Edge cases.
- Security, performance, accessibility.
- Logging and monitoring.
- Test items.
- Acceptance criteria.
```

## Phase 4: DDD

```text
Decide whether DDD is useful for this feature.

If yes:
- Core/supporting/generic subdomains.
- Entities.
- Value objects.
- Domain services.
- Repositories.
- Aggregates and invariants.
- Bounded contexts.
- Domain events.
- Anti-overengineering notes.

If no:
- Explain why a simpler model is enough.
```

## Phase 5: AI-TDD

```text
Create the test plan before implementation.

Include:
- Unit tests.
- Integration tests.
- E2E or workflow tests.
- Security and permission tests.
- Regression tests.
- Tests the implementation agent may not delete or weaken.

Mark each test as required, optional, or deferred.
```

## Phase 6: Context Engineering

```text
Create a bounded context package for an implementation agent.

Include:
- Required docs.
- Required source files.
- Optional background files.
- Architecture constraints.
- No-touch files or patterns.
- Verification commands.
- Final context summary.
```

## Phase 7: Agentic Coding

```text
Write an implementation ticket.

Use:
# Task: <feature>
## Goal
## Scope
## Out of Scope
## Acceptance Criteria
## Required Context
## Constraints
## Test Requirements
## Review Notes

Do not implement the code in this phase.
```

## Phase 8: Review

```text
Review the implementation against the artifacts.

Check:
- Spec fit.
- BDD scenario coverage.
- Test adequacy.
- Domain model fit.
- Security, permission, privacy.
- Performance and reliability.
- Accessibility.
- Maintainability.
- Unrelated changes.
- Merge blockers.

Return: merge-ready, merge-after-fixes, or block-merge.
```

## Phase 9: SPDD Archive

```text
Archive reusable development knowledge.

Include:
- Feature overview.
- Strategy combination.
- Prompts used.
- Assumptions.
- Decisions.
- Artifacts.
- Test results.
- Review findings.
- Reusable patterns.
- Anti-patterns.
```
