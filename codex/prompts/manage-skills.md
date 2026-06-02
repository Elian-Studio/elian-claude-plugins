# /manage-skills - Verification-skill drift maintenance (Codex Port)

Install path: `~/.codex/prompts/manage-skills.md`.

Invocation:

```text
/manage-skills [skill-name | focus-area | question]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/manage-skills/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

## Purpose

Detect drift between the current project changes and the project-local verification catalog, then propose or apply the minimum verification updates needed to keep coverage current.

Use this prompt to audit or repair verification drift. It is not a code implementation prompt.

## Common Contract

1. Compare the current change set against the local verification catalog.
2. Classify drift explicitly.
3. Ask when ownership is ambiguous.
4. New verification entries need approval before they are created.
5. End with one next question, next action, or handoff payload.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `[skill-name]` | Verification skill name or focus area | none |
| `[focus-area]` | Area that needs verification coverage | none |
| `[question]` | Clarifying question when the mapping is ambiguous | none |

`$ARGUMENTS` always wins over any local default.

## Workflow

```text
Phase 1: Discover current verification catalog
Phase 2: Map changed files to coverage
Phase 3: Classify drift
Phase 4: Propose update, create, or exempt
Phase 5: Repair or hand off
```

### Phase 1: Discover current verification catalog

Find project-local verification files and read their required sections and related file patterns.

### Phase 2: Map changed files to coverage

Compare the current working changes with the verification catalog and identify which areas are covered, which are stale, and which are missing.

### Phase 3: Classify drift

Use explicit drift labels:

- Coverage Gap
- Invalid Reference
- Missing Check
- Outdated Value

### Phase 4: Propose update, create, or exempt

Decide whether each item should be updated, created, or exempted. If ownership is ambiguous, ask before editing.

### Phase 5: Repair or hand off

If repair is approved, update the verification prompt or catalog file. If the drift belongs to another workflow, hand it off instead of pretending it belongs here.

## Output Shapes

### Default output

```text
Drift summary
- Focus: <skill-name or focus-area>
- Classification: <coverage gap / invalid reference / missing check / outdated value>
- Recommendation: <update / create / exempt>

Key decisions
- <decision 1>
- <decision 2>

Open questions
- <unresolved item>

Next
- <next question or next action>
```

### Repair output

```text
# Verification drift repair
## Coverage Gaps
## Invalid References
## Missing Checks
## Outdated Values
## Proposed Updates
## Approval Needed
```

## Forbidden

- Modifying user-global verification skills.
- Creating a new verification skill without approval.
- Treating non-`verify-` prompts as verification skills.
- Silently changing a rule to make drift disappear.

## Pre-Output Self-Check

- [ ] Current verification catalog was read.
- [ ] Drift was classified explicitly.
- [ ] Ownership ambiguity was handled.
- [ ] New skill creation is gated by approval.
- [ ] The output ends with one next question or next action.
