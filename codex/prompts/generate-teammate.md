# /generate-teammate - Hybrid execution planning (Codex Port)

Install path: `~/.codex/prompts/generate-teammate.md`.

Invocation:

```text
/generate-teammate <project description or task requirements>
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/generate-teammate/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

## Purpose

Decompose a task into execution phases, judge each phase independently, and produce a file-conflict-free hybrid execution plan. Codex does not have Claude Agent Team primitives, so this prompt produces the plan and handoff structure rather than attempting to spawn teammates.

## Common Contract

1. Decompose the work before choosing an execution style.
2. Judge each phase independently.
3. Prefer the minimum viable team.
4. Do not assign overlapping file ownership.
5. End with one next question, next action, or handoff payload.

## Workflow

```text
Phase 1: Request analysis
Phase 2: Work phase decomposition
Phase 3: Per-phase approach selection
Phase 4: Role and task design
Phase 5: Parallel task planning
Phase 6: Confirmation
Phase 7: Handoff
```

### Phase 1: Request analysis

Extract the domain, tech stack, deliverables, constraints, and parallelizable units from the user request.

### Phase 2: Work phase decomposition

Break the task into phases such as explore, design, implement, verify, or document. Make dependencies explicit.

### Phase 3: Per-phase approach selection

Choose direct, parallel subtask, or coordinated team-style execution for each phase. Explain the reason per phase.

### Phase 4: Role and task design

Map the phases to concrete roles, responsibilities, and file ownership. Keep the ownership disjoint.

### Phase 5: Parallel task planning

Plan the tasks in a way that avoids file conflicts and minimizes dependencies.

### Phase 6: Confirmation

Ask the user to confirm the plan, especially when a hybrid or parallel strategy is proposed.

### Phase 7: Handoff

Return a handoff plan that another workflow can execute. Do not pretend to create actual teammates in Codex.

## Output Shapes

### Default output

```text
Team plan
- Domain: <domain>
- Strategy: <direct / parallel / hybrid>
- Recommendation: <what to do next>

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
# Hybrid execution plan
## Request Analysis
## Phase Breakdown
## Per-Phase Approach
## Role and Ownership Table
## File Conflict Notes
## Confirmation Needed
## Handoff
```

## Forbidden

- Pretending Codex can spawn Claude Agent Team tasks.
- Assigning overlapping ownership.
- Skipping phase decomposition.
- Choosing an execution style before analyzing phase characteristics.

## Pre-Output Self-Check

- [ ] The request was decomposed into phases.
- [ ] File ownership is disjoint.
- [ ] The selected strategy is justified per phase.
- [ ] The user has a confirmation point.
- [ ] The output ends with one next question or next action.
