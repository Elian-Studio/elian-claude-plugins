# Anti-Patterns

Use this reference when a feature request feels like it is moving too quickly into implementation.

## Vague Build Request

Bad:

```text
Build login.
```

Why it fails:

- Product policy is guessed.
- Failure cases are guessed.
- Tests become generic.
- Security behavior may drift.

Better:

```text
Run Phase 1-5 first: intent, BDD, spec, policy questions, and AI-TDD.
```

## Test Decoration

Bad:

```text
Implement it, then add tests if needed.
```

Why it fails:

- Tests are shaped around the implementation.
- Regression intent is unclear.
- AI may weaken assertions to pass.

Better:

```text
Write the test matrix before implementation and mark protected tests.
```

## Whole-Repository Context

Bad:

```text
Read the whole repository and figure it out.
```

Why it fails:

- Context becomes noisy.
- The agent may copy unrelated patterns.
- Review scope expands.

Better:

```text
Build a bounded context package with required docs, files, constraints, and no-touch areas.
```

## Best-Practice Without Criteria

Bad:

```text
Use the best approach.
```

Why it fails:

- "Best" changes by model and run.
- Trade-offs are invisible.
- The team cannot review intent.

Better:

```text
Write acceptance criteria and review axes before generating the implementation ticket.
```

## Phase 7 Without Phase 1-5

Bad:

```text
Write an agent task immediately.
```

Why it fails:

- The agent task hides missing product and test decisions.
- Downstream implementation fills gaps with guesses.

Better:

```text
Use design-only mode first, then emit the task ticket.
```

## High-Risk Feature Without DDD Decision

Bad:

```text
Put payment or cancellation policy directly into a controller because it is faster.
```

Why it fails:

- Invariants scatter.
- Business language disappears.
- Tests target implementation details instead of rules.

Better:

```text
Run Phase 4 and decide whether entities, value objects, policies, or domain services are warranted.
```

## AI Weakens Tests

Bad:

```text
The agent deletes or loosens failing assertions to make CI pass.
```

Why it fails:

- Regression protection collapses.
- The spec no longer controls behavior.

Better:

```text
Mark protected tests in Phase 5 and block merge if they are weakened.
```

## No Archive

Bad:

```text
After the PR, discard prompts and decisions.
```

Why it fails:

- The same policy debate repeats.
- Future agents lack precedent.

Better:

```text
Write the SPDD archive with prompts, assumptions, decisions, tests, and anti-patterns.
```
