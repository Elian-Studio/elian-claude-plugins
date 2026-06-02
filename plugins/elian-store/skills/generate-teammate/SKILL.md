---
name: generate-teammate
description: When the user explicitly invokes /generate-teammate or says 'create a team', 'build a team', or 'spawn teammates', decompose the work into phases, judge each phase independently (Agent Team / Subagent / direct), and produce a hybrid execution plan with file-conflict-free role assignment. JSON-first spawn prompt rendering via create-document blocks vague language (help build, TODO, ...) before any teammate is spawned.
when_to_use: Use ONLY when the user explicitly invokes /generate-teammate or asks to 'create a team', 'build a team', or 'spawn teammates'. Do NOT use for simple single-step tasks or when a direct edit suffices.
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
> **This skill's routing catalog uses 14 standalone custom agents** in `plugins/elian-store/agents/`. Engineering: `frontend-architect`, `backend-architect`, `system-architect`, `security-engineer`, `performance-engineer`, `quality-engineer`, `devops-architect`, `requirements-analyst`. Design / research / strategy: `ui-ux-designer`, `technical-writer`, `ux-researcher`, `marketing-strategist`, `business-analyst`, `devil-advocate`. They have no external skill dependencies and work as soon as the plugin is installed.

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
> **All 14 generate-teammate custom agents above ship with this plugin** as standalone definitions in `plugins/elian-store/agents/`. They do **not** depend on any other plugin or user-level skill — install elian-store and they work.

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
2. **Phase 6.5 — Spawn prompt rendering**: Author each teammate as JSON → run `create-document/scripts/render.py --template teammate-spawn`. Validation must pass before Phase 7.
3. **Phase 7**: Execute phases in order
   - Agent Team: `TeamCreate` → `TaskCreate` → `TaskUpdate(owner)` → `Agent(team_name, prompt: <rendered slot from spawn-plan.md>)` spawn
   - Subagent: parallel `Agent` tool calls with the same rendered slots
   - Hybrid: pass results across phases (preceding output → next prompt)
4. **Shutdown**: `SendMessage(shutdown_request)` → `TeamDelete()`

### Required Items in Teammate Spawn Prompt (JSON-first since v2.6)

**Do not hand-write spawn prompts.** Author each teammate as JSON, then render through `create-document`. The schema enforces every required slot and blocks vague language — no spawned teammate ships with missing context.

7 required slots per teammate (enforced by `schemas/teammate-spawn.schema.json`):

| Slot | Schema rule |
|------|-------------|
| `role` | minLength 15, forbid `help build` / `do something` |
| `owned_files` | array, minItems 1 (file-conflict prevention) |
| `tech_stack` | array, minItems 1 |
| `task` | minLength 30, **mustMatch** action verb (`implement` / `build` / `design` / `verify` / ...), forbid `TODO` / `...` |
| `reference_docs` | array (can be empty if none) |
| `interfaces` | minLength 20 (cross-teammate contract) |
| `definition_of_done` | minLength 30, **mustMatch** measurable signal (`test` / `pass` / `lint` / `cover` / ...) |
| `communication` | minLength 15 |

#### Render command

```bash
CD="${CLAUDE_PLUGIN_ROOT}/skills/create-document"
python3 "${CD}/scripts/render.py" \
  --template teammate-spawn \
  --data ./claudedocs/{team_name}/spawn.json \
  --out ./claudedocs/{team_name}/spawn-plan.md
```

If validation fails, stderr lists every violation by `teammates[i].field`. Fix the JSON, re-render. **Do not** skip render and hand-write.

Worked example: [example-teammate-spawn.json](../create-document/references/example-teammate-spawn.json) — 3 teammates (backend / frontend / test), all 7 slots, 43 fields validated.

Standard template definition: [create-document/templates/teammate-spawn.md](../create-document/templates/teammate-spawn.md). For details on file-conflict prevention and parallel task design see [execution-guide.md](execution-guide.md).

## Error Handling

| Error | Action |
|-------|--------|
| Unclear requirements | Ask clarification via AskUserQuestion |
| Cannot parallelize | Inform "single session is more efficient" |
| File conflict detected | Reassign roles or switch to sequential |
| Teammate count > 5 | Suggest role consolidation |
| Spawn JSON schema fails | Read stderr, fix offending slot, re-render. Never hand-write the prompt. |

See [references/known-issues.md#error-handling](references/known-issues.md#error-handling) for the same table with extended rationale.

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

These rules apply throughout the skill — not as one-time procedure steps but as ongoing behavior. Headline list:

- Phase decomposition is non-optional
- Per-phase independence beats whole-task judgment
- Core question: "Do workers need to communicate?" (No → Subagent, Handoff → chain, Debate → Agent Team)
- File ownership before parallelism
- Minimum viable team (2 over 5 if 2 suffice)
- Always confirm via AskUserQuestion before spawning
- Self-contained agents only (no dependency on user-level skills)
- Spawn prompt is JSON-first (rendered via `create-document/teammate-spawn`)

Full text with rationale: [references/standing-rules.md](references/standing-rules.md).

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

Top 5 (full list in [references/known-issues.md](references/known-issues.md#forbidden)):

- ❌ Skip Phase decomposition for "obvious" tasks
- ❌ Pick an approach by phase **type** instead of characteristics
- ❌ Allow two teammates to own the same file
- ❌ Skip the AskUserQuestion confirmation gate before spawning
- ❌ Hand-write spawn prompts without going through `create-document/teammate-spawn` (vague language and missing slots cause inconsistent results)

## Pitfall / Known Issues

Common failure modes (top 3 — full table in [references/known-issues.md](references/known-issues.md#pitfall--known-issues)):

| Pitfall | Fix |
|---------|-----|
| Lead starts implementing instead of waiting | Enable delegate mode (Shift+Tab); message lead "wait for teammates" |
| Two teammates touched the same file | Re-design role boundaries; rerun Phase 5 ownership validation |
| `create-document` schema fails on spawn JSON | Read stderr — every error names field + violation. Fix JSON, re-render. Do **not** hand-write the prompt. |

Failure-mode recovery: every spawn includes a verify step. Failed verifications are reassigned, not silently skipped. See [known-issues.md](references/known-issues.md#failure-mode-recovery).

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
| `subagent_type` selection from the 14-agent generate-teammate catalog | ✅ | — |
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

Four BEFORE/AFTER comparisons live in [references/before-after-patterns.md](references/before-after-patterns.md):

1. **Approach selection** — phase-type-based (❌) vs characteristic-based (✅)
2. **File ownership** — overlapping (❌) vs strict single-owner (✅)
3. **Spawn prompt completeness** — hand-written vague (❌) vs JSON-first via `create-document/teammate-spawn` (✅)
4. **Spawn prompt slot completeness** — silent missing slot (❌) vs schema-enforced 7 required fields (✅)

## Skill verification

Manual checks for this skill:

- `Agent({...})` examples do not include a `model` parameter.
- Legacy `Task({` usage is not reintroduced.
- `TaskCreate` examples do not use `addBlockedBy`; use `TaskUpdate` for dependencies.
- `disable-model-invocation: true` remains set.
- The 14 generate-teammate routing agents are present in `plugins/elian-store/agents/`.
- Plugin agent definitions remain self-contained and do not use `skills:` frontmatter.
- `references/` keeps at least four end-to-end traces.
- `team-patterns.md` keeps Documentation Team, Strategy Team, and Design Team variants.

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
7. **Quality Hooks**: `TeammateIdle` (when a teammate is about to go idle) and `TaskCompleted` (when a task is being marked complete) hooks can enforce automated checks. Exit code 2 returns feedback.
