# /improve - Behavior-changing improvement to working features (Codex Port)

Install path: `~/.codex/prompts/improve.md`.

Invocation:

```text
/improve <issue-id> [--side back|front|both] [--step N] [--skip-docs]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/improve/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

## Purpose

Improve an existing working feature without turning it into a new feature or a bug fix. Use this prompt for UX polish, performance optimization, edge-case hardening, and similar behavior-changing improvements.

Do not use it for new capabilities or broken behavior.

## Common Contract

1. Capture the current state before changing it.
2. Make the AFTER target measurable.
3. Protect existing tests before adding new expectations.
4. Approval gate is mandatory.
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
Step 1: BEFORE snapshot
Step 2: Improvement plan + conflict matrix
Step 3: Approval gate
Step 4: TDD improvement
Step 5: BEFORE/AFTER verification
Step 6: Code review
Step 7: Completion report
```

### Step 0: Project recognition

Read project guidance to capture stack, build commands, test commands, and conventions. If guidance is missing, ask the user for the stack and conventions before proceeding.

### Step 1: BEFORE snapshot

Capture current behavior, existing tests, pain points, and dependencies. If existing tests are thin, write characterization tests before changing behavior.

### Step 2: Improvement plan + conflict matrix

Break the request into improvement units, define the AFTER target and measurable impact, identify file overlap, and choose the execution strategy.

### Step 3: Approval gate

Ask the user to approve, modify, or cancel the plan. Do not proceed without explicit approval.

### Step 4: TDD improvement

Keep existing tests green, add new expectations for the AFTER state, then make the smallest change that moves the behavior. Refactor only after the tests are green.

### Step 5: BEFORE/AFTER verification

Run the relevant verification commands and compare the measured BEFORE and AFTER behavior. If the target is only qualitative, say so explicitly.

### Step 6: Code review

Check for behavior drift, scope creep, and sibling patterns that should be improved together.

### Step 7: Completion report

Summarize the improvement units, test counts, quantified BEFORE/AFTER comparison, verification, and next steps.

## Output Shapes

### Default output

```text
Improvement summary
- Issue: <issue-id>
- BEFORE: <current state>
- AFTER target: <target>

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
# Improvement: <FEATURE_NAME>
## BEFORE
## AFTER Target
## Plan
## Tests
## Verification
## Review Notes
```

## Forbidden

- Smuggling a new feature into an improvement.
- Fixing a bug under the guise of improvement.
- Skipping the approval gate.
- Skipping characterization tests when coverage is thin.
- Skipping quantified BEFORE/AFTER comparison when the metric is measurable.

## Pre-Output Self-Check

- [ ] BEFORE state is captured.
- [ ] AFTER target is measurable or explicitly qualitative.
- [ ] Existing test coverage was assessed.
- [ ] The user approved the plan.
- [ ] The output ends with one next question or next action.
