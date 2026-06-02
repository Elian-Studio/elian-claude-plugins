# Quick Start

Pick the smallest mode that protects the risk.

## 1. First Use Or High-Risk Feature

Command:

```text
/ai-assisted-feature-development "<feature>" --risk high --depth full
```

Use when:

- Authentication, payment, privacy, permission, data loss, or external provider behavior is involved.
- Product policy is still unclear.
- Tests must protect important regressions.

Expected artifacts:

- Feature framing.
- BDD scenarios.
- Specification.
- DDD decision.
- Test plan.
- Context package.
- Agent task.
- Review checklist.
- SPDD archive.

## 2. Design Only

Command:

```text
/ai-assisted-feature-development "<feature>" --risk medium --depth design-only
```

Use when:

- The team needs intent, scenarios, spec, and test plan before deciding who implements.
- Implementation will happen in a later PR.

Expected artifacts:

- Feature framing.
- BDD scenarios.
- Specification.
- DDD decision if needed.
- Test plan.

## 3. Task Only

Command:

```text
/ai-assisted-feature-development "<feature>" --depth task-only
```

Use when:

- A good spec already exists.
- The next step is handing work to an implementation agent.

Required inputs:

- Existing specification.
- Existing test plan.
- Existing scope and out-of-scope boundaries.

Expected artifacts:

- Context package.
- Agentic coding ticket.

## 4. Review Only

Command:

```text
/ai-assisted-feature-development "<feature>" --depth review-only
```

Use when:

- Implementation exists.
- You need to compare the result against spec, BDD, tests, and risk criteria.

Expected artifact:

- Review checklist and merge judgment.

## Risk Selection

| Risk | Use when | Minimum depth |
|---|---|---|
| low | prototype, demo, simple UI copy | Phase 1, 2, 5 |
| medium | ordinary CRUD, moderate UX, normal API | Phase 1, 3, 5, 6 |
| high | auth, payment, permission, privacy, irreversible state | full |

## Handoff Rule

Before downstream implementation, make sure these exist:

- `spec.md`
- `test-plan.md`
- `context-package.md`
- `agent-task.md`

If any are missing, do not hand off yet.
