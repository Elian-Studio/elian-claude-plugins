---
name: ai-assisted-feature-development
description: When feature work needs discipline before AI writes code, produce framing, BDD/SDD/DDD, AI-TDD, context, agentic tasking, review, and SPDD archive artifacts.
when_to_use: "Use for new features, behavior-changing improvements, legacy refactors, API/UI behavior design, domain-policy work, and defining work before handing it to an AI agent. Trigger phrases: 'start feature planning', 'design this feature before coding', 'prepare for AI coding', 'write the spec first', 'start from BDD', 'apply AI-assisted feature development', '/ai-assisted-feature-development'. Do not use for typos, one-line config changes, or already-scoped small fixes."
argument-hint: "<feature-name> [--risk low|medium|high] [--depth full|design-only|task-only|review-only] [--example login|payment|upload|search]"
disable-model-invocation: false
allowed-tools: Read, Glob, Grep, Write, Bash(git diff*), Bash(git log*), Bash(git status*), AskUserQuestion
---

# /ai-assisted-feature-development

Use this skill to turn a feature request into implementation-ready artifacts before an AI agent writes code. The core flow is:

```text
intent -> behavior -> specification -> model -> tests -> context -> implementation task -> review -> archive
```

The skill produces planning artifacts, task tickets, and review checklists. It does not implement code. Phase 7 emits work that downstream skills such as `/implement`, `/fix`, or `/improve` can execute.

## Where this fits in the workflow

```text
/brainstorm (optional for fuzzy ideas)
  -> /ai-assisted-feature-development
     Phase 1 Feature Framing
     Phase 2 BDD
     Phase 3 SDD
     Phase 4 DDD when needed
     Phase 5 AI-TDD
     Phase 6 Context Engineering
     Phase 7 Agentic Coding
     Phase 8 Review
     Phase 9 SPDD Archive
  -> /implement, /fix, or /improve
  -> /persona-review and /decision-dashboard when decisions or critique remain
```

- **Upstream**: use `/brainstorm` first when intent, users, scope, or constraints are unclear.
- **This skill**: produces reusable documents, tickets, and checklists for the 9-phase flow.
- **Downstream**: pass the artifacts to implementation skills, then use persona review or decision locking when needed.

## Standing rules

- Do not hand vague requests directly to an implementation agent. Phase 1-5 artifacts come first.
- Intent, specification, and tests come before generated code.
- Scale depth by risk. A prototype does not need the same depth as auth, payment, privacy, or permission logic.
- Keep context bounded. Select the files and documents an AI agent must read instead of dumping the whole repository.
- AI drafts; the human owns product policy, security, and architecture decisions.
- Treat tests as contracts. Do not let an implementation agent weaken or delete tests to pass.
- Do not introduce new auth, ORM, queue, or architectural patterns without an explicit specification.
- Keep PR-sized work reviewable. Do not bundle unrelated refactors into feature planning.
- Every phase should leave an artifact that can be reused later.

Detailed master prompt: [references/master-prompt.md](references/master-prompt.md).

## Modes

Control depth with `$ARGUMENTS`.

| Mode | Scope | Use when |
|---|---|---|
| `full` (default) | Phase 1-9 | New feature, high risk, complex product policy |
| `design-only` | Phase 1-5 | Design and tests are needed, implementation is separate |
| `task-only` | Phase 6-7 | Spec already exists and the next step is AI delegation |
| `review-only` | Phase 8 | Implementation exists and needs spec/test/risk review |

Risk guides how much of the workflow to run.

| Risk | Recommended phase set |
|---|---|
| `low` | Phase 1, Phase 2, and a lightweight Phase 5 |
| `medium` | Phase 1, Phase 3, Phase 5, and Phase 6 |
| `high` | Phase 1-9 plus security and privacy review |

`--example login|payment|upload|search` loads the closest example from the reference set.

## Automated vs needs your taste

| Automated | User or team decides |
|---|---|
| Phase order and artifact skeletons | Feature risk level |
| Security, permission, privacy, and payment risk detection | Product policy and business thresholds |
| BDD, SDD, DDD, and test matrix drafts from input | Scenario priority and acceptance criteria |
| Context package recommendations | Files that must be read versus optional background |
| Agentic task ticket structure | Out-of-scope boundaries and ownership |
| Review checklist application | Final merge/block judgment |
| SPDD artifact formatting | Which prompt patterns should be reused |

If an automated decision is wrong, correct it at the phase review gate before moving on.

## Procedure

Use [references/stage-prompts.md](references/stage-prompts.md) for detailed per-phase prompts. Use [references/master-prompt.md](references/master-prompt.md) when the whole workflow should be run as one consolidated planning pass.

### Phase 1: Feature Framing

Capture `FEATURE_NAME`, `FEATURE_DESCRIPTION`, `USER_TYPES`, `TECH_STACK`, `CONSTRAINTS`, and `RISK_LEVEL`.

Output:

1. One-sentence feature intent.
2. Main users and use contexts.
3. Success criteria.
4. Conditions that must not fail.
5. Expected edge cases.
6. Security, permission, privacy, performance, and accessibility risks.
7. Recommended phase set based on risk.
8. Questions that must be answered before implementation.

### Phase 2: BDD

Write normal, failure, and exception flows in Given-When-Then form. Separate unknown product policy into questions or assumptions.

### Phase 3: SDD

Create the feature specification: purpose, scope, roles, inputs, outputs, API/UI behavior, state changes, error policy, edge cases, security, performance, accessibility, logging, monitoring, tests, and acceptance criteria.

Store the specification using the structure in [references/artifact-structure.md](references/artifact-structure.md).

### Phase 4: DDD

Decide whether DDD is warranted. For complex policy, produce entity, value object, domain service, repository, bounded context, domain event, and anti-overengineering notes. Skip heavy modeling for simple CRUD.

### Phase 5: AI-TDD

Before implementation, create the test matrix and failing tests or precise test specifications. Cover unit, integration, E2E, security, permission, and regression cases. Explicitly state that implementation agents may not delete or weaken assertions.

### Phase 6: Context Engineering

Build the minimum useful AI context package:

1. Required documents.
2. Required source files.
3. Optional background files.
4. Existing architecture rules.
5. Files or patterns that must not change.
6. Test and verification commands.
7. Final context summary.

### Phase 7: Agentic Coding

Emit an implementation ticket:

```text
# Task: <FEATURE_NAME>
## Goal
## Scope
## Out of Scope
## Acceptance Criteria
## Required Context
## Constraints
## Test Requirements
## Review Notes
```

This skill only emits the ticket. Downstream implementation skills execute it.

### Phase 8: Review

Review against specification fit, BDD coverage, test adequacy, domain model fit, security, permission, privacy, performance, accessibility, maintainability, unnecessary changes, merge blockers, and improvement suggestions.

Use merge judgment labels: `merge-ready`, `merge-after-fixes`, or `block-merge`.

### Phase 9: SPDD Archive

Archive the feature overview, strategy, prompts, assumptions, artifacts, test results, review findings, reusable patterns, and anti-patterns.

Example archive path: `prompts/feature-development/<feature>/spdd-record.md`.

## Forbidden

- Starting implementation from "build this feature" without Phase 1-5 artifacts.
- Adding tests only after implementation as justification.
- Letting AI invent security, permission, or privacy policy.
- Throwing the whole repository into context.
- Bundling unrelated refactors into the feature task.
- Introducing new platform patterns without a specification.
- Allowing AI to delete or weaken tests.
- Executing the Phase 7 task inside this skill.
- Proceeding without out-of-scope boundaries.
- Skipping the SPDD archive when the workflow produced reusable decisions.

## Pitfall / anti-patterns

See [references/anti-patterns.md](references/anti-patterns.md).

| Pattern | Problem | Response |
|---|---|---|
| "Build login" | Intent, policy, and tests are guessed | Require Phase 1-5 artifacts |
| "Add tests too" | Tests become pass-oriented decoration | Use AI-TDD matrix and test-protection rules |
| "Read the whole repo and fix it" | Context explodes and architecture drifts | Build bounded Phase 6 context |
| "Use the best approach" | Criteria vary every run | Archive reusable SPDD decisions |
| Phase 7 without Phase 1-5 | Agent guesses the spec | Prefer `full` mode |
| Skipping DDD on high-risk policy | Business rules drift into controllers | Include Phase 4 for high-risk work |
| Weakening assertions | Regression protection collapses | Block in AI-TDD and Phase 8 review |

## Definition of Done

The full checklist is in [references/definition-of-done.md](references/definition-of-done.md).

Core DoD:

- Intent and success criteria are explicit.
- BDD scenarios exist.
- Feature specification exists.
- Domain complexity has been assessed.
- Test plan exists before implementation.
- AI context package is bounded.
- Agentic task ticket is ready.
- Implementation can be reviewed against the spec.
- Security, permission, privacy, performance, and accessibility were considered.
- Test and verification expectations are documented.
- Prompts and decisions are archived.

## Examples

- Login feature full workflow: [references/login-example.md](references/login-example.md).
- Other feature examples: [references/other-feature-examples.md](references/other-feature-examples.md).
- Quick-start patterns: [references/quick-start.md](references/quick-start.md).

Invocation examples:

```text
/ai-assisted-feature-development "email/password login" --risk high
/ai-assisted-feature-development "cart item add" --risk medium --depth design-only
/ai-assisted-feature-development "file upload" --risk medium --example upload
/ai-assisted-feature-development "order cancellation" --risk high --depth full
/ai-assisted-feature-development "post creation" --risk low --depth task-only
```

## Customization

| Mechanism | Purpose | Default |
|---|---|---|
| `$ARGUMENTS` | `<feature-name> [--risk ...] [--depth ...] [--example ...]` | none |
| `${AAFD_DEFAULT_RISK}` | Default risk override | `medium` |
| `${AAFD_DEFAULT_DEPTH}` | Default depth override | `full` |
| `${AAFD_ARTIFACT_DIR}` | Artifact directory | `docs/features/<feature>/` |

Precedence: `$ARGUMENTS` > environment variables > skill defaults.

## Artifact structure

Use [references/artifact-structure.md](references/artifact-structure.md).

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

## Self-validation

```bash
python3 plugins/elian-store/skills/ai-assisted-feature-development/scripts/validate_skill.py
python3 plugins/elian-store/skills/ai-assisted-feature-development/scripts/validate_skill.py --json
```

The validator checks frontmatter, all 9 phase names, required reference links, Standing rules, Forbidden, Pitfall, Where this fits, `$ARGUMENTS` or environment override support, and Definition of Done coverage.
