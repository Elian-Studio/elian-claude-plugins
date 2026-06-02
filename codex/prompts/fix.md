# /fix - Root-cause-first bug fix (Codex Port)

Install path: `~/.codex/prompts/fix.md`.

Invocation:

```text
/fix <issue-id> [--side back|front|both] [--step N] [--skip-docs]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/fix/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

## Purpose

Repair a confirmed bug by tracing symptom to root cause, writing a regression test first, then fixing the code and verifying the result before reporting.

Use this prompt only when behavior is broken. Do not use it for new features or behavior-changing improvements.

## Common Contract

1. Root cause before fix.
2. Regression test before code changes.
3. Approval gate is mandatory.
4. Search for sibling sites that may share the same root cause.
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
Step 1: Bug analysis
Step 2: Repair plan + conflict matrix
Step 3: Approval gate
Step 4: TDD repair
Step 5: Integration verification
Step 6: Code review
Step 7: Completion report
```

### Step 0: Project recognition

Read project guidance to capture stack, build commands, test commands, and conventions. If guidance is missing, ask the user for the stack and conventions before proceeding.

### Step 1: Bug analysis

Enumerate symptoms, repro conditions, blast radius, proximate cause, root cause, and affected files. If the root cause is not clear, ask for more information and stop.

### Step 2: Repair plan + conflict matrix

Map each symptom to a fix, a regression test, and the files that will change. If multiple symptoms are independent, identify the file-overlap matrix and choose the execution strategy accordingly.

### Step 3: Approval gate

Ask the user to approve, modify, or cancel the plan. Do not proceed without explicit approval.

### Step 4: TDD repair

Write the failing regression test first, then fix the code, then run the relevant suite. For multi-symptom bugs, keep commits per symptom when practical.

### Step 5: Integration verification

Run the relevant verification commands and any adjacent module tests that could expose blast radius from the root-cause fix.

### Step 6: Code review

Check that the fix addresses the root cause, not just the symptom, and search for sibling sites with the same pattern.

### Step 7: Completion report

Summarize the symptoms, root causes, fixes, regression tests, verification, and next steps.

## Output Shapes

### Default output

```text
Fix summary
- Issue: <issue-id>
- Root cause: <root cause>
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
# Bug: <BUG_NAME>
## Symptoms
## Root Cause
## Fix Plan
## Regression Tests
## Verification
## Review Notes
```

## Forbidden

- Patching symptoms without confirming the root cause.
- Writing the fix before the failing regression test.
- Skipping the approval gate.
- Ignoring sibling-site search.
- Editing the test to match buggy behavior instead of fixing the bug.

## Pre-Output Self-Check

- [ ] Symptoms and root cause are explicit.
- [ ] Regression test is written first.
- [ ] Sibling-site search was considered.
- [ ] The user approved the plan.
- [ ] The output ends with one next question or next action.
