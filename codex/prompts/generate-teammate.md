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

1. Decompose the work before choosing an execution style — but the analysis may conclude **Direct** (a single agent). Over-decomposing a coherence-critical or sequential task is an anti-pattern.
2. Judge each phase independently, against the cost-and-risk prior **Direct < parallel subtask < coordinated team**. Default to the cheapest that fits; escalate only on need **and** value (coordinated/parallel runs cost many times the tokens of Direct).
3. Prefer the minimum viable team.
4. Do not assign overlapping file ownership — and remember file split ≠ semantic safety: after any parallel write, a single agent must reconcile the seams (cross-boundary build/typecheck).
5. Coherence-critical artifacts (one design doc / spec / report) are authored by a single agent; pass full artifacts, not lossy summaries, across handoffs.
6. End with one next question, next action, or handoff payload.

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

First triage: is delegation even warranted? Look for breadth-first/read-heavy parallelism, genuinely independent modules, or a high-value real-time reconciliation need. If none holds, the answer is **Direct** — say so and stop. Otherwise break the task into phases (explore, design, implement, verify, document) with explicit dependencies.

### Phase 3: Per-phase approach selection

Choose direct, parallel subtask, or coordinated team-style execution for each phase, applying the prior **Direct < parallel subtask < coordinated team**. For each non-Direct phase, state its rough cost multiplier and the parallel benefit that justifies it; if the benefit does not clearly outweigh the cost, downgrade to Direct. Coordinated team-style is a last resort for real-time reconciliation only (e.g. BE↔FE API-contract negotiation) — for "multi-perspective" work, prefer independent parallel subtasks + a single synthesizer.

### Phase 4: Role and task design

Map the phases to concrete roles, responsibilities, and file ownership. Keep the ownership disjoint.

### Phase 5: Parallel task planning

Plan the tasks in a way that avoids file conflicts and minimizes dependencies. For any phase with parallel writes, include an explicit **integration-reconciliation task** owned by a single agent — a cross-boundary build/typecheck over the merged surface to catch semantic seam conflicts (duplicate declarations, type mismatches, broken references) that disjoint file ownership cannot prevent. It is a team-level Definition of Done.

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
- Over-decomposing into a team a task a single agent does better.
- Choosing an execution style before analyzing phase characteristics.
- Escalating beyond Direct without stating the cost multiplier and the parallel benefit that justifies it.
- Using a coordinated team for "debate" when independent subtasks + a single synthesizer would do.
- Co-authoring one coherence-critical artifact across multiple agents.
- Marking a parallel write phase done without the cross-boundary integration check.

## Pre-Output Self-Check

- [ ] The request was decomposed into phases (and Direct was considered as a valid outcome).
- [ ] File ownership is disjoint.
- [ ] The selected strategy is justified per phase, with a cost multiplier for every non-Direct phase.
- [ ] Any parallel write phase has a single-agent integration-reconciliation task.
- [ ] Coherence-critical artifacts have a single author; handoffs pass full artifacts.
- [ ] The user has a confirmation point.
- [ ] The output ends with one next question or next action.
