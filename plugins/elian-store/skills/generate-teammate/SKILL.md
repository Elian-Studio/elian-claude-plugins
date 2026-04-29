---
name: generate-teammate
description: "When the user explicitly invokes /generate-teammate or says 'create a team', 'build a team', or 'spawn teammates', decompose the work into phases, judge each phase independently (Agent Team / Subagent / direct), and produce a hybrid execution plan with file-conflict-free role assignment."
when_to_use: "Use ONLY when the user explicitly invokes /generate-teammate or asks to 'create a team', 'build a team', or 'spawn teammates'. Do NOT use for simple single-step tasks or when a direct edit suffices."
argument-hint: "<project description or task requirements>"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python3 *), Bash(ls *), Agent, TeamCreate, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage, TeamDelete, AskUserQuestion
disable-model-invocation: true
---

# /generate-teammate — Agent Team Generator

## Prerequisites

> **Agent Teams is an experimental feature** and is disabled by default.
> Before use, add the following to `settings.json` or set as an environment variable:
> ```json
> { "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
> ```

> **Custom agent types**: Custom `subagent_type` values like `frontend-architect`, `backend-architect` require an agent definition file at `~/.claude/agents/{name}.md`, `.claude/agents/{name}.md`, or a plugin's `agents/` directory. Built-in types (`Explore`, `Plan`, `general-purpose`) work immediately without a definition file.
>
> **This plugin ships 14 standalone custom agents** in `plugins/elian-store/agents/`. Engineering: `frontend-architect`, `backend-architect`, `system-architect`, `security-engineer`, `performance-engineer`, `quality-engineer`, `devops-architect`, `requirements-analyst`. Design / research / strategy: `ui-ux-designer`, `technical-writer`, `ux-researcher`, `marketing-strategist`, `business-analyst`, `devil-advocate`. They have no external skill dependencies and work as soon as the plugin is installed.

## Core Philosophy

**Each work phase determines its own execution approach.**
- Do not apply a single approach to the entire task — judge each phase independently
- Agent Team / Subagent / direct execution have no fixed priority — phase characteristics decide
- Reject fixed mappings like "exploration = Subagent, design = Agent Team" — always analyze characteristics
- Role separation that prevents file conflicts between teammates is essential
- Use the minimum configuration that fits the task scale

## Parameters

`$ARGUMENTS` carries the project description or task requirements.

## Execution Flow

```
Phase 1: Request Analysis
    │
    ├── Parse user requirements
    ├── Identify project domain
    └── Extract tech stack, constraints, goals
    │
Phase 2: Work Phase Decomposition
    │
    ├── Decompose work into execution phases
    │   (e.g., explore → design → implement → verify)
    ├── Analyze each phase's characteristics:
    │   ├── Whether independent parallel execution is possible
    │   ├── Whether multi-perspective discussion / feedback is needed
    │   └── Whether cross-layer interface coordination is needed
    └── Map phase dependencies
    │
Phase 3: Per-Phase Approach Selection  ← Key Gate
    │
    ├── Score each phase independently
    ├── Pick the best approach per phase (Agent Team / Subagent / direct)
    ├── Combine into an overall strategy: single or hybrid
    └── Output a hybrid strategy comparison table
    │
Phase 4: Team & Task Design
    │
    ├── Agent Team phases: match a team pattern (see team-patterns.md)
    ├── Subagent phases: plan parallel Agent tool calls
    ├── Determine teammate count (2~5)
    └── Map roles to subagent_types
    │
Phase 5: Parallel Task Planning
    │
    ├── Decompose work into parallel-safe units
    ├── Identify task dependencies
    ├── Assign owned files / directories to each teammate
    └── Verify no file conflicts
    │
Phase 6: User Confirmation
    │
    ├── Present the full execution plan (per-phase approach + roles + tasks)
    ├── For hybrid strategies, mark phase transition points clearly
    └── Confirm via AskUserQuestion
    │
Phase 7: Execution
    │
    ├── Execute phases in order
    ├── Agent Team phases: TeamCreate → TaskCreate → Teammate Spawn
    ├── Subagent phases: parallel Agent tool calls
    └── Pass results between phases (preceding phase output → next phase input)
```

## Phase 1: Request Analysis

Extract the following from `$ARGUMENTS`:

```typescript
interface RequestAnalysis {
  domain: 'frontend' | 'backend' | 'fullstack' | 'design' | 'research' | 'review' | 'devops';
  techStack: string[];           // mentioned technologies (Next.js, Spring Boot, etc.)
  deliverables: string[];        // outputs (API, UI, docs, etc.)
  constraints: string[];         // constraints (performance, security, etc.)
  parallelizableUnits: string[]; // independently progressable work units
}
```

## Phase 2-3: Work Decomposition & Approach Selection

See [approach-selection.md](approach-selection.md) for detailed criteria.

### Summary

1. **Decompose work into phases** (explore / design / implement / verify)
2. **Analyze 5 characteristics per phase**: need for multi-perspective discussion, cross-layer coordination, independent parallelism, mutual result dependency, expertise differentiation
3. **Judge each phase independently**: Agent Team / Subagent / direct execution
4. **Strategy decision**: single or hybrid

> **Phase type does not determine the approach.** Always judge by characteristic analysis.

### Required Output (mandatory)

```
Per-phase approach decision:

┌─────────────┬───────────────┬───────────────────┬───────────────┬──────────────────────────────────┐
│    Phase    │  Agent Team   │    Subagent       │   Direct      │              Reason              │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ A: Explore  │ Unfit         │ ★ Fit             │ Possible      │ Independent exploration, gather  │
│             │               │                   │               │ results only                     │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ B: Design   │ ★ Fit         │ Possible          │ Unfit         │ UX/FE/BE perspective debate +    │
│             │               │                   │               │ API contract negotiation         │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ C: Build    │ Possible      │ ★ Fit             │ Possible      │ Clear file separation, no debate │
└─────────────┴───────────────┴───────────────────┴───────────────┴──────────────────────────────────┘

Strategy: hybrid — Subagent (explore) → Agent Team (design) → Subagent (build)
```

### Gate Decision

- **Single strategy** → proceed to Phase 4 with that approach
- **Hybrid strategy** → combine per-phase plans and proceed to Phase 4
- **All direct execution** → tell the user "Direct execution is the most efficient option for this task" and propose execution

## Phase 4: Team & Task Design

Design Agent Team phases and Subagent phases separately.

### Agent Team Phase Design

See [team-patterns.md](team-patterns.md) for full pattern details.

#### Pattern Selection Criteria

| Condition | Pattern |
|-----------|---------|
| UI + API + DB all required | **Implementation Team** |
| New project design / exploration | **Research Team** |
| Existing code review / analysis | **Review Team** |
| System architecture design | **Design Team** |
| Documentation overhaul (README, API docs, migration guides) | **Documentation Team** |
| Strategy / launch / positioning decision | **Strategy Team** |
| Single-layer focused work | **Focused Team** |

#### Teammate → subagent_type Mapping

**Built-in agent types** (no definition file required):

| Role | subagent_type | Suitable for | Notes |
|------|---------------|--------------|-------|
| Code exploration / research | `Explore` | Codebase analysis, pattern survey | **Read-only**, Haiku model (fast, low-cost) |
| Planning / design | `Plan` | Implementation plans, architecture analysis | **Read-only**, inherits model |
| General (explore + implement) | `general-purpose` | Complex research, multi-step tasks, code edits | inherits model, full tool access |

**Plugin-bundled custom agent types** (shipped with this plugin, no setup needed):

Engineering / build roles:

| Role | subagent_type | Suitable for |
|------|---------------|--------------|
| Frontend development | `frontend-architect` | Framework-agnostic FE: React / Vue / Angular / Svelte / Solid |
| Backend development | `backend-architect` | Multi-stack: Spring Boot / Express / NestJS / Django / FastAPI / Rails / Go / .NET |
| System design | `system-architect` | Architecture, ADRs, domain modeling, observability standards |
| Security review | `security-engineer` | OWASP Top 10, threat modeling, secrets, AI / LLM security |
| Performance | `performance-engineer` | Profiling, bottleneck analysis, load testing |
| Test / quality | `quality-engineer` | Unit / integration / E2E test design, coverage strategy |
| Infra / DevOps | `devops-architect` | Docker, K8s, Terraform, CI/CD, secret management |
| Requirements analysis | `requirements-analyst` | PRDs, acceptance criteria, story slicing |

Design / research / strategy roles:

| Role | subagent_type | Suitable for |
|------|---------------|--------------|
| UI / UX design | `ui-ux-designer` | Design tokens, component specs, interaction patterns, a11y from design lens |
| Technical writing | `technical-writer` | README, API docs, tutorials, runbooks, release notes |
| User research | `ux-researcher` | Interviews, personas, journey maps, usability testing |
| Marketing / positioning | `marketing-strategist` | Positioning, messaging, GTM, launch planning, content strategy |
| Business / strategy | `business-analyst` | Business model, ROI, unit economics, market sizing, decision frameworks |
| Critical review | `devil-advocate` | Pre-mortems, assumption excavation, ethical lens, adversarial review |

> **Read-only built-in caution** — `Explore` and `Plan` only allow Read/Grep/Glob; they cannot Edit/Write.
> Never assign implementation work to them. Use them for exploration / analysis / planning only.
>
> **All 14 custom agents above ship with this plugin** as standalone definitions in `plugins/elian-store/agents/`. They do **not** depend on any other plugin or user-level skill — install elian-store and they work.

### Subagent Phase Design

Subagent phases run as parallel Agent tool calls. Define each task's role, input, and output clearly.

## Phase 5: Parallel Task Planning

### Parallelization Principles

1. **File ownership separation**: each teammate's owned files / directories must not overlap
2. **Minimize dependencies**: minimize blocking dependencies between tasks
3. **Right-sized**: 5~6 tasks per teammate is optimal (per official docs)
4. **Sequential dependencies**: when design → build → test order matters, link with `addBlockedBy`

### File Conflict Prevention

```
# GOOD: separation by role
frontend-dev → src/components/, src/pages/, src/styles/
backend-dev  → src/api/, src/services/, src/db/
test-dev     → tests/, __tests__/

# BAD: multiple teammates editing the same file
frontend-dev → src/app.tsx
backend-dev  → src/app.tsx  ← conflict!
```

## Phase 6-7: Execution

See [execution-guide.md](execution-guide.md) for output format, execution code, and communication details.

### Execution Summary

1. **Phase 6**: AskUserQuestion confirms team composition (role + agent type + assigned tasks table)
2. **Phase 7**: Execute phases in order
   - Agent Team: `TeamCreate` → `TaskCreate` → `TaskUpdate(owner)` → `Agent(team_name)` spawn
   - Subagent: parallel `Agent` tool calls
   - Hybrid: pass results across phases (preceding output → next prompt)
3. **Shutdown**: `SendMessage(shutdown_request)` → `TeamDelete()`

### Required Items in Teammate Spawn Prompt

Role / responsibility scope, owned files / directories, tech stack, definition of done, inter-teammate interfaces. See `execution-guide.md` for the standard template.

## Error Handling

| Error | Action |
|-------|--------|
| Unclear requirements | Ask clarification via AskUserQuestion |
| Cannot parallelize | Inform "single session is more efficient" |
| File conflict detected | Reassign roles or switch to sequential |
| Teammate count > 5 | Suggest role consolidation |

## Examples

```bash
/generate-teammate Build a developer blog. Next.js, Shadcn, Markdown.
/generate-teammate CLI tool design. Need exploration from UX, architecture, and adversarial perspectives.
/generate-teammate Refactor the notification system in the api-common module.
/generate-teammate Payment system security review. 2 security experts + 1 performance expert.
```

See [references/](references/) for end-to-end traces of each scenario (input → phase decomposition → approach decision → team composition → spawn prompts):

- [01-fullstack-feature.md](references/01-fullstack-feature.md) — hybrid: Subagent → Agent Team → Subagent → Subagent
- [02-competing-hypothesis-debugging.md](references/02-competing-hypothesis-debugging.md) — Agent Team for mutual rebuttal
- [03-parallel-pr-review.md](references/03-parallel-pr-review.md) — Subagent (parallel) for independent review
- [04-product-launch-strategy.md](references/04-product-launch-strategy.md) — non-engineering domain (marketing / business / risk)

## Standing Rules

These rules apply throughout the skill — not as one-time procedure steps but as ongoing behavior.

- **Phase decomposition is non-optional.** Even if the user describes a single task, run Phase decomposition mentally. Skipping it produces wrong-shape teams.
- **Per-phase independence beats whole-task judgment.** Composite work has phases that prefer different approaches. Forcing one approach across the whole task is the most common failure mode.
- **The core question is "Do workers need to communicate with each other?"** — from the official docs. If no, Subagent. If yes-with-handoff, Subagent chain. If yes-with-debate, Agent Team.
- **File ownership before parallelism.** Two teammates editing the same file is a data race in disguise. Validate ownership separation before spawning.
- **Minimum viable team.** 2 teammates beat 5 if 2 suffice. Coordination cost grows non-linearly past 5.
- **Always confirm with AskUserQuestion before spawning.** The user owns the decision; the skill produces the recommendation.
- **Self-contained agents only.** This plugin's 14 agents work without external skills. Do not introduce dependencies on user-level skills the user may not have.

## Procedure (one-time)

Phase 1 → 2 → 3 → 4 → 5 → 6 → 7 (see flow diagram above). For each user invocation:

1. Parse `$ARGUMENTS` into RequestAnalysis.
2. Decompose into phases.
3. Judge each phase via the per-phase decision table.
4. Produce the team / subagent plan.
5. Verify file ownership and minimal team size.
6. Confirm with AskUserQuestion.
7. Execute using the documented sequence.

## Forbidden

> Do **not** do any of these. They are wrong by design, not preference.

- ❌ Skip Phase decomposition for "obvious" tasks. The skill's core value is the per-phase judgment.
- ❌ Pick an approach by phase **type** (e.g., "exploration is always Subagent"). Always judge by characteristics.
- ❌ Spawn an Agent Team for independent work just because the task feels big. Token cost without benefit.
- ❌ Spawn Subagents in parallel before an unsettled API contract. They will produce inconsistent shapes and re-work.
- ❌ Allow two teammates to own the same file. This is a deterministic conflict, not a probabilistic one.
- ❌ Skip the AskUserQuestion confirmation gate before spawning teammates. The user must own the team-shape decision.
- ❌ Bundle `Bash(*)` or unrestricted destructive permissions in `allowed-tools`. Scope every tool.
- ❌ Use `model:` parameter on `Agent({...})` calls. Resolve via env var → invocation override → definition → session.
- ❌ Use legacy `Task({...})` syntax. Use `Agent({...})` (renamed in v2.1.63).
- ❌ Set task dependencies inside `TaskCreate`. Use `TaskUpdate({ task_id, addBlockedBy: [...] })`.

## Pitfall / Known Issues

| Pitfall | Why it happens | Fix |
|---------|----------------|-----|
| Lead starts implementing instead of waiting | Without delegate mode, the lead does work itself | Enable delegate mode (Shift+Tab); message lead "wait for teammates" |
| Teammates idle, task list stalls | Tasks have unresolved `blockedBy` after upstream tasks completed but weren't marked done | Tell lead to mark stale tasks complete or rerun TaskList review |
| TeamDelete fails with active members | Teammates didn't shut down cleanly | Always do `SendMessage(shutdown_request)` first; verify all teammates idle |
| `/resume` after lead session restart loses teammates | In-process teammates aren't restored | Spawn fresh teammates with the same context summary |
| Two teammates touched the same file | File ownership wasn't enforced | Re-design role boundaries; rerun Phase 5 ownership validation |
| Agent Team token cost balloons | Each teammate keeps full context | Switch to Subagent for any phase that doesn't need real-time debate |
| `tmux` split-pane mode breaks on Windows / VS Code terminal | Display mode unsupported on those terminals | Switch to `teammateMode: "in-process"` |

For failure-mode handling: every spawn includes a "verify completion" step. Tasks that fail to verify are reassigned, not silently skipped. Use rollback (revert produced files) when a phase produces unusable output.

## Where this fits in the workflow

```
brainstorm → /generate-teammate → execute (or hand off to /implement, /fix) → /review → /ship
                       │
                       └── This skill produces the team plan + execution.
                           Other skills consume it (decisions, code, review docs).
```

Sequencing principles:
- **Before** /generate-teammate: have a clear problem statement. If the problem is fuzzy, run /brainstorm first.
- **During** /generate-teammate: produce phase decisions, team plan, and (if confirmed) spawn teammates.
- **After** /generate-teammate: hand off persistent artifacts to downstream skills (/implement, /review, /ship).

## Manual decision gating (automated vs taste)

What this skill decides automatically vs what needs the user's taste:

| Concern | Automated | Needs user taste |
|---------|-----------|------------------|
| Phase decomposition (explore / design / build / verify) | ✅ | — |
| Per-phase fit scoring (★ Fit / Possible / Unfit) | ✅ | — |
| Strategy classification (single / hybrid) | ✅ | — |
| Pattern matching (Implementation / Research / Review / Design / Documentation / Strategy / Focused) | ✅ | — |
| File-ownership conflict detection | ✅ | — |
| `subagent_type` selection from the 14 catalog | ✅ | — |
| Team size 2-5 recommendation | ✅ | — |
| Final approval to spawn | — | ✅ (AskUserQuestion gate) |
| Per-teammate spawn prompt content | drafted automatically | ✅ user reviews before spawn |
| Whether to use plan approval mode | — | ✅ user opts in for risky tasks |
| Whether to deviate from the recommended pattern | — | ✅ user can override |

The automated decisions are deterministic given the same input. The taste decisions require human context the skill cannot infer.

## Reflection (end of skill)

After the team finishes, write 3 short observations into `claudedocs/team-{date}-reflection.md`:

1. **Coordination patterns observed** — did teammates over- or under-communicate? Where did handoffs stall?
2. **Approach validation** — was the per-phase decision correct? Should any phase have been Subagent instead of Team (or vice versa)?
3. **Reuse signal** — did this team's structure suggest a future skill or template? (E.g., recurring "review across N lenses" → bake into a slash command.)

Reflections feed back into pattern selection over time. Repeat patterns become templates; broken patterns get retired.

## Persistent artifacts for downstream

The skill produces files that downstream skills consume:

| Artifact | Producer phase | Downstream consumer |
|----------|---------------|---------------------|
| Phase decomposition table | Phase 2 | /implement (knows what to build first) |
| Per-phase decision table | Phase 3 | Future invocations (pattern memory) |
| Spawn prompts | Phase 6 | Re-spawn / resume after compaction |
| Team config (`~/.claude/teams/{name}/`) | Phase 7 (TeamCreate) | Lead sessions; teammates discover each other |
| Task list (`~/.claude/tasks/{name}/`) | Phase 7 (TaskCreate) | Status, blockers, ownership |
| Reflection memo | Post-execution | Future generate-teammate invocations |

Persistent artifacts make the workflow resumable across sessions and give downstream skills (e.g., /review) a structured input.

## BEFORE / AFTER patterns

### Approach selection

❌ **BEFORE — phase-type-based selection** (anti-pattern):

> "It's a build phase, so spawn a fullstack team of 4."

This produces a team where every phase forces the same shape. The build phase doesn't need cross-perspective debate; it needs files split. Result: 4 teammates idle waiting for synchronization that doesn't exist.

✅ **AFTER — characteristic-based per-phase selection** (correct):

> "Build phase: file ownership clear, no debate needed → Subagent (parallel). Design phase before it: API contract unsettled, FE/BE need to negotiate → Agent Team."

This matches each phase's coordination requirement. Build runs cheaply in parallel; design uses the heavy-coordination tool only where it pays.

### File ownership

❌ **BEFORE — overlapping ownership**:

```
frontend-dev → src/components/, src/app.tsx, src/api-client.ts
backend-dev  → src/api/, src/api-client.ts (shared client config)
```

Two teammates own `src/api-client.ts`. The last writer wins; bug discovered at integration.

✅ **AFTER — strict ownership**:

```
frontend-dev → src/components/, src/app.tsx
backend-dev  → src/api/
api-contract → src/api-client.ts (single owner — could be either, decided up front)
```

Every file has exactly one owner. Conflicts are impossible.

### Spawn prompt completeness

❌ **BEFORE — vague prompt**:

```
"Help build the notification feature."
```

Teammate has no role, no scope, no DoD. Will produce something but it will not match the team's plan.

✅ **AFTER — full template** (see [execution-guide.md](execution-guide.md)):

```
[ROLE] [OWNED FILES] [TECH STACK] [TASK]
[REFERENCE DOCS] [INTERFACES] [DEFINITION OF DONE] [COMMUNICATION]
```

Every slot filled. Teammate knows what to do, what to touch, and what "done" means.

## Skill verification

To validate that the skill follows its own rules, run:

```bash
python3 [scripts/validate_skill.py](scripts/validate_skill.py)
python3 [scripts/validate_skill.py](scripts/validate_skill.py) --json
```

The validator (stdlib only, argparse + `--json` support) checks: no `model:` on Agent, no legacy `Task({`, no `addBlockedBy` in TaskCreate, `disable-model-invocation: true` set, all 14 agents present and self-contained, references/ has ≥ 4 traces, team-patterns includes Documentation + Strategy + Design variants. Exits 0 on PASS, 1 on FAIL.

## Pre-flight checklist

Before spawning the team, confirm each of:

- [ ] All phases decomposed; per-phase decision table produced
- [ ] Strategy classified (single / hybrid) with clear rationale
- [ ] No two teammates own overlapping files
- [ ] Team size ≤ 5 (if larger, role consolidation suggested)
- [ ] Each teammate's spawn prompt has all 7 slots (ROLE / OWNED FILES / TECH STACK / TASK / REFERENCE DOCS / INTERFACES / DOD / COMMUNICATION)
- [ ] User has approved the plan via AskUserQuestion

## Notes

1. **Token cost**: Agent Team incurs higher cost than a single session. Use only when parallel benefit is clear.
2. **Delegate Mode**: enable delegate mode (Shift+Tab) so the lead does not implement directly.
3. **Monitoring**: Shift+Down cycles teammates, Ctrl+T toggles the task list.
4. **Cleanup**: always finish with `SendMessage(shutdown_request)` → `TeamDelete()` in that order.
5. **Display Mode**: configure `teammateMode` to `"in-process"` (default, all terminals) or `"tmux"` (split-pane, requires tmux/iTerm2).
6. **Plan Approval**: for risky tasks, spawn teammates in plan mode; the lead approves before they switch to implementation. Use the prompt "Require plan approval before they make any changes."
7. **Quality Gate Hooks**: `TeammateIdle` (when a teammate is about to go idle) and `TaskCompleted` (when a task is being marked complete) hooks can enforce automated checks. Exit code 2 returns feedback.
