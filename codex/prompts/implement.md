# /implement - TDD-driven feature implementation (Codex Port)

Install path: `~/.codex/prompts/implement.md`.

Invocation:

```text
/implement <issue-id> [--side back|front|both] [--step N] [--skip-docs]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/implement/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

## Purpose

Build a new feature through a TDD pipeline. Gather context, plan with explicit file ownership, ask for approval, then run Red -> Green -> Refactor with verification and review before reporting.

Use this prompt only for new feature work. Do not use it for bug repair or behavior-preserving improvement.

## Common Contract

1. Requirements come before code.
2. Tests come before implementation.
3. File ownership must be explicit before parallel work starts.
4. The approval gate is mandatory. If the user does not approve, stop.
5. End with one next question, next action, or handoff payload.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `<issue-id>` | Issue identifier | required |
| `--side back\|front\|both` | Limit to one layer | `both` |
| `--step N` | Resume from a specific step | `1` |
| `--skip-docs` | Skip design-doc generation | `false` |

`$ARGUMENTS` always wins over any local default.

## Workflow

```text
Step 0: Project recognition
Step 1: Context gathering
Step 2: Plan + conflict matrix
Step 3: Approval gate
Step 4: TDD execution
Step 5: Integration verification
Step 6: Code review
Step 7: Completion report
```

### Step 0: Project recognition

Read project guidance (`CLAUDE.md` or equivalent) to capture stack, build commands, test commands, and conventions. If no project guidance exists, ask the user for the stack and conventions before proceeding.

### Step 1: Context gathering

Inspect the current branch, design docs, and existing patterns in the affected area. If requirements are missing and `--skip-docs` is not set, ask for the missing design input before planning.

### Step 2: Plan + conflict matrix

Decompose the request into independent feature units, identify file overlap, and choose the execution strategy:

- one unit with no overlap -> direct
- multiple disjoint units -> parallel subagents
- multiple units needing contract negotiation -> agent team

Keep backend and frontend work ordered to match existing project conventions.

### Step 3: Approval gate

Ask the user to approve, modify, or cancel the plan. Do not proceed to implementation without explicit approval.

### Step 4: TDD execution

For each feature unit:

1. Write failing tests first.
2. Implement the minimum change to make them pass.
3. Refactor while keeping tests green.
4. Commit per unit when the codebase expects incremental commits.

### Step 5: Integration verification

Run relevant verification commands and project verify skills when they exist. For cross-layer changes, include the matching contract checks.

### Step 6: Code review

Review the diff against the plan, tests, and conventions. If the review reveals missing work, fix it before completion.

### Step 7: Completion report

Summarize file counts, test counts, commit counts, verification results, and next steps.

## Output Shapes

### Default output

```text
Implementation summary
- Issue: <issue-id>
- Side: <back|front|both>
- Step: <current step>

Key decisions
- <decision 1>
- <decision 2>

Open questions
- <unresolved item>

Next
- <next question or next action>
```

### Handoff output

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

- Skipping the approval gate.
- Writing implementation before a failing test exists.
- Mixing unrelated refactors into the feature unit.
- Letting parallel workers touch the same file.
- Committing megadiffs that cannot be reviewed or bisected.

## Pre-Output Self-Check

- [ ] Project context was gathered.
- [ ] Feature units and ownership are explicit.
- [ ] The user has approved the plan.
- [ ] Tests were written before implementation.
- [ ] The output ends with one next question or next action.
