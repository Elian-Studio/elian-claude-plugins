# Decision Matrix

Use this matrix after drift detection.

## CREATE

Choose CREATE when:

- A new rule family has no existing `verify-*` skill.
- The changed files form a coherent verification domain.
- Existing skills would become too broad if updated.
- The verifier can be expressed with explicit Related Files, Workflow, Output Format, and Exceptions.

Example:

```text
New files:
- src/i18n/en.json
- src/i18n/ko.json
- src/features/profile/useProfileCopy.ts

No verifier covers i18n keys.

Decision: CREATE verify-i18n
```

Approval: required per new skill.

## UPDATE

Choose UPDATE when:

- An existing skill already owns the domain.
- Only paths, command patterns, thresholds, or exceptions need to change.
- The required check belongs naturally to the skill's current purpose.

Examples:

```text
Existing verify-api-contract already checks OpenAPI files.
New path docs/api/v2/openapi.yaml was added.

Decision: UPDATE Related Files.
```

```text
Existing verify-message-cost checks SMS and LMS.
New ALIMTALK message type was added.

Decision: UPDATE Workflow and tests.
```

Approval:

- Batch approval is acceptable for straightforward path additions.
- Per-item approval is required for command or rule changes.

## EXEMPT

Choose EXEMPT when:

- A changed file is a generated artifact.
- A fixture intentionally violates the production rule.
- The rule does not apply to the file's environment.
- The user confirms a one-off exception.

Example:

```text
Changed file: tests/fixtures/bad-contract.json
Verifier: verify-api-contract
Reason: fixture intentionally contains invalid contract examples.

Decision: EXEMPT and document in Exceptions.
```

## DEFER

Choose DEFER when:

- The mapping is unclear and the user cannot decide now.
- A verifier would need product policy that is not settled.
- Creating the skill would exceed the current task scope.

Deferred items must stay visible in the report.

## Matrix

| Condition | Decision |
|---|---|
| No skill covers a new verification domain | CREATE |
| Existing skill covers the domain but misses paths | UPDATE Related Files |
| Existing skill covers paths but misses rule | UPDATE Workflow |
| Existing skill references deleted path | UPDATE stale references |
| File is generated or fixture | EXEMPT |
| Ownership is ambiguous | Ask user, then CREATE/UPDATE/EXEMPT |
| Policy is unsettled | DEFER |

## Quality Gate

Before applying CREATE or UPDATE, verify:

- The skill has a clear domain.
- It will not overlap confusingly with another skill.
- PASS/FAIL criteria are explicit.
- Exceptions are narrow.
- Commands are safe and runnable.
