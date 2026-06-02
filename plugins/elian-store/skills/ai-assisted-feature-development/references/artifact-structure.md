# Artifact Structure

Use a small, predictable artifact tree so downstream agents can load the right files without scanning the whole repository.

## Recommended Tree

```text
docs/features/<feature-name>/
  feature-framing.md
  bdd-scenarios.feature
  spec.md
  domain-model.md
  test-plan.md
  context-package.md
  agent-task.md
  review-checklist.md
  prompt-record.md
```

## File Purposes

| File | Purpose |
|---|---|
| `feature-framing.md` | Intent, users, success criteria, risks, questions |
| `bdd-scenarios.feature` | Given/When/Then scenarios |
| `spec.md` | Product, API, UI, state, error, and acceptance specification |
| `domain-model.md` | DDD decision and model notes when warranted |
| `test-plan.md` | AI-TDD matrix and protected tests |
| `context-package.md` | Files, docs, constraints, no-touch areas, verification commands |
| `agent-task.md` | Implementation-ready ticket |
| `review-checklist.md` | Phase 8 review criteria |
| `prompt-record.md` | SPDD archive of prompts, decisions, assumptions, and results |

## Naming

- Use lowercase kebab-case feature directory names.
- Prefer product terms over ticket-only names when possible.
- If an issue ID is required, include it as a prefix: `PROJ-123-login`.

## Minimal Artifact Set By Mode

| Mode | Required artifacts |
|---|---|
| `full` | all files |
| `design-only` | framing, BDD, spec, domain-model when needed, test-plan |
| `task-only` | context-package, agent-task |
| `review-only` | review-checklist plus links to existing spec/tests |

## Context Handoff Rule

Downstream implementation should receive:

1. `spec.md`
2. `test-plan.md`
3. `context-package.md`
4. `agent-task.md`

Do not hand off the entire artifact directory if only those four files are needed.
