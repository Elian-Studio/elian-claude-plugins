# /ai-assisted-feature-development - Feature planning before AI coding (Codex Port)

Install path: `~/.codex/prompts/ai-assisted-feature-development.md`.

Invocation:

```text
/ai-assisted-feature-development <feature-name> [--risk low|medium|high] [--depth full|design-only|task-only|review-only] [--example login|payment|upload|search]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/ai-assisted-feature-development/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

Read-only contract: do not edit files, create files, stage, commit, push, or run destructive commands. If the user needs a durable artifact, emit the requested Markdown in the response and stop. If implementation is needed, hand off to `/review`, `/implement`, `/fix`, or `/improve` and stop.

## Purpose

Turn a feature request into implementation-ready planning artifacts before AI writes code.

The planning flow should make intent, policy, tests, context, tasks, review criteria, and archive notes explicit before implementation starts.

## Common Contract

1. Do not hand vague requests directly to implementation.
2. Intent, behavior, specification, and tests come before code.
3. Keep the context bounded to the minimum useful files and rules.
4. Choose depth based on risk.
5. End with one next question, next action, or handoff payload.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `<feature-name>` | Feature subject or work item | required |
| `--risk low\|medium\|high` | Planning depth based on product and technical risk | `medium` |
| `--depth full\|design-only\|task-only\|review-only` | Which phases to run | `full` |
| `--example login\|payment\|upload\|search` | Use the closest example pattern | none |

`$ARGUMENTS` always wins over any local default.

## Workflow

```text
Phase 1: Feature framing
Phase 2: BDD
Phase 3: SDD
Phase 4: DDD when needed
Phase 5: AI-TDD
Phase 6: Context engineering
Phase 7: Agentic tasking
Phase 8: Review
Phase 9: SPDD archive
```

### Phase 1: Feature framing

Capture the feature intent, users, success criteria, non-negotiable conditions, edge cases, and risks. Ask questions before proceeding when product policy or scope is unclear.

### Phase 2: BDD

Write normal, failure, and exception scenarios in Given-When-Then form.

### Phase 3: SDD

Create the feature specification: purpose, scope, inputs, outputs, state changes, error policy, edge cases, security, performance, accessibility, logging, monitoring, tests, and acceptance criteria.

### Phase 4: DDD when needed

Use domain modeling only when the feature has meaningful domain complexity. Keep simple CRUD simple.

### Phase 5: AI-TDD

Create the test matrix and the pre-implementation test contract. Do not let implementation weaken or delete assertions.

### Phase 6: Context engineering

Build the minimum useful AI context package: required docs, required source files, optional background, rules, forbidden changes, verification commands, and a final context summary.

### Phase 7: Agentic tasking

Emit an implementation ticket rather than code. The ticket should contain goal, scope, out of scope, acceptance criteria, required context, constraints, test requirements, and review notes.

### Phase 8: Review

Review the planned feature against specification fit, BDD coverage, test adequacy, domain model fit, security, privacy, performance, accessibility, maintainability, and merge blockers.

Use one of these labels when closing the review: `merge-ready`, `merge-after-fixes`, or `block-merge`.

### Phase 9: SPDD archive

If the workflow produced reusable decisions, emit an archive note or Markdown record that captures the feature overview, strategy, prompts, assumptions, artifacts, test results, review findings, reusable patterns, and anti-patterns.

## Output Shapes

### Default output

```text
Planning summary
- Feature: <feature-name>
- Risk: <risk>
- Recommended depth: <depth>

Key decisions
- <decision 1>
- <decision 2>

Open questions
- <unresolved item>

Next
- <next question or next action>
```

### Ticket output

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

## Forbidden

- Starting implementation from a vague request without planning artifacts.
- Letting AI invent policy, security, permission, or privacy decisions.
- Throwing the whole repository into context.
- Bundling unrelated refactors into the feature task.
- Allowing AI to delete or weaken tests.
- Executing the implementation task inside this prompt.
- Skipping the archive when the workflow produced reusable decisions.

## Pre-Output Self-Check

- [ ] Feature intent is explicit.
- [ ] Risk and depth were chosen intentionally.
- [ ] Planning artifacts were created before implementation.
- [ ] Review and archive paths are clear.
- [ ] The output ends with one next question or next action.
