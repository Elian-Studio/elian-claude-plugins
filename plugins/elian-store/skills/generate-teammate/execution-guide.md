# Phase 6-7: Execution Guide

## Phase 6: User Confirmation Output Format

Always confirm via AskUserQuestion before execution. For hybrid strategies, explicitly mark phase transitions.

### Single-strategy output format

```
Team composition:
┌─────────────────────────────────────────────┐
│ Team: {team-name}                           │
│ Pattern: {pattern-name}                     │
│ Teammates: {count}                          │
├─────────┬──────────────────┬────────────────────────┤
│ Role    │ Agent Type       │ Assigned Tasks         │
├─────────┼──────────────────┼────────────────────────┤
│ {role1} │ {subagent_type}  │ {tasks}                │
│ {role2} │ {subagent_type}  │ {tasks}                │
└─────────┴──────────────────┴────────────────────────┘

Parallel execution plan:
├── [parallel] Task A, Task B, Task C
├── [sequential] Task D (← after Task A)
└── [parallel] Task E, Task F
```

### Hybrid-strategy output format

```
Hybrid execution plan:

Phase A: Explore (Subagent parallel)
├── Explore: {target 1}
└── Explore: {target 2}
    ↓ pass results
Phase B: Design (Agent Team — {pattern})
├── Teammate 1: {role} — {responsibility}
├── Teammate 2: {role} — {responsibility}
└── Teammate 3: {role} — {responsibility}
    Deliverables: {design.md, api-spec.md, etc.}
    ↓ pass design
Phase C: Build (Subagent parallel)
├── Task: {target 1}
└── Task: {target 2}
```

---

## Phase 7: Execution

### Single strategy: Agent Team

```typescript
// 1. Create team
TeamCreate({ team_name: teamName, description: projectDescription });

// 2. Create tasks (no owner yet)
const taskA = TaskCreate({ subject: "Build API endpoint", description: "..." });
const taskB = TaskCreate({ subject: "Build UI component", description: "..." });
const taskC = TaskCreate({ subject: "Write integration tests", description: "..." });

// 3. Set task dependencies via TaskUpdate
TaskUpdate({ task_id: taskC.id, addBlockedBy: [taskA.id, taskB.id] });

// 4. Assign tasks via TaskUpdate(owner)
TaskUpdate({ task_id: taskA.id, owner: "backend-dev" });
TaskUpdate({ task_id: taskB.id, owner: "frontend-dev" });
// taskC will be assigned after blocking tasks complete

// 5. Spawn teammates (Agent tool)
Agent({
  subagent_type: "frontend-architect",
  team_name: teamName,
  name: "frontend-dev",
  prompt: "<spawn prompt — see template below>",
});

Agent({
  subagent_type: "backend-architect",
  team_name: teamName,
  name: "backend-dev",
  prompt: "<spawn prompt — see template below>",
});
```

### Hybrid strategy

Run phases sequentially; within each phase, run in parallel.
**Pass preceding phase results into the next phase's input.**

```
Phase A (Subagent) → result summary → Phase B (Agent Team) → deliverables → Phase C (Subagent)
```

#### Phase transition rules

1. **Subagent → Agent Team**: summarize Subagent results and include in each teammate's spawn prompt
2. **Agent Team → Subagent**: have Subagent prompts reference Agent Team deliverables (design.md, api-spec.md, etc.)
3. **Subagent → Subagent**: include preceding Subagent's result in the following Subagent's prompt

#### Hybrid execution example (explore → design → build)

```typescript
// Phase A: Explore (Subagent parallel via Agent tool)
const exploreResults = await Promise.all([
  Agent({ subagent_type: "Explore", prompt: "Analyze BE API + DTO + Service..." }),
  Agent({ subagent_type: "Explore", prompt: "Analyze FE pages + components..." }),
]);

// Phase B: Design (Agent Team)
TeamCreate({ team_name: "design-team", description: "..." });
// Pass exploration summaries into each teammate
Agent({
  subagent_type: "frontend-architect",
  team_name: "design-team",
  name: "fe-designer",
  prompt: `Exploration results: ${exploreResults}. Design from UI/UX perspective...`,
});
Agent({
  subagent_type: "backend-architect",
  team_name: "design-team",
  name: "be-designer",
  prompt: `Exploration results: ${exploreResults}. Design from API/DTO perspective...`,
});
// → Deliverables: design.md, api-spec.md

// Phase C: Build (Subagent parallel)
// Reference design docs
Agent({ subagent_type: "backend-architect", prompt: "Build BE per design.md..." });
Agent({ subagent_type: "frontend-architect", prompt: "Build FE per design.md..." });
```

---

## Teammate Spawn Prompt Template

Use this template for every teammate spawn. Fill all 7 slots.

```
You are the {ROLE_NAME} on the {TEAM_NAME} team.

[ROLE]
{One-line role summary}

[OWNED FILES]
{Directory globs / file patterns this teammate may modify}

[TECH STACK]
{Frameworks + versions + project conventions}

[TASK]
Claim tasks from the shared TaskList where owner == "{ROLE_NAME}" and complete them.

[REFERENCE DOCS]
{Paths to design docs, API specs, ADRs, exploration reports — pass anything from preceding phases}

[INTERFACES]
- {other teammate name}: {data / API contract reference, format}

[DEFINITION OF DONE]
- {tests pass}
- {lint / typecheck pass}
- {deliverable produced}

[COMMUNICATION]
- Report progress / blockers to lead via SendMessage
- For cross-cutting changes that affect other teammates, broadcast or message lead first
- Do not modify other teammates' OWNED FILES directly
```

### Filled example (frontend-architect on a fullstack team)

```
You are the frontend-dev on the notification-feature team.

[ROLE]
Build the user-facing UI for the notification center feature.

[OWNED FILES]
- src/components/notifications/
- src/pages/NotificationCenter.vue
- src/stores/notification.ts
- src/locales/ko.json (notification.* keys)
- tests/components/notifications/

[TECH STACK]
- Vue 3 Composition API + <script setup>
- TypeScript strict
- Pinia
- SCSS (existing token system in src/styles/tokens/)
- i18n via vue-i18n; all Korean text must be extracted to keys

[TASK]
Claim tasks from the shared TaskList where owner == "frontend-dev" and complete them.

[REFERENCE DOCS]
- docs/design/notification-center.md (UX flow + component tree)
- docs/api/notification-api.md (API contract — agreed with backend-dev)

[INTERFACES]
- backend-dev: GET /api/notifications response shape per docs/api/notification-api.md §3
- quality-engineer: Will write E2E tests; you write component / store unit tests

[DEFINITION OF DONE]
- All assigned tasks Done in TaskList
- npx tsc --noEmit passes
- npx vitest run passes
- All Korean strings extracted to ko.json
- Component renders correctly in dev server (verified manually)

[COMMUNICATION]
- Progress / blockers → SendMessage lead
- API contract change requests → broadcast (affects backend-dev)
- Do not modify src/api/ or backend code directly
```

---

## Team Communication (SendMessage)

Inter-teammate communication must use the **SendMessage** tool. Plain text output does not reach other teammates.

### Message types

| Type | Use | Cost |
|------|-----|------|
| `message` | DM to a specific teammate (default) | low |
| `broadcast` | Send to all teammates simultaneously | **high** — only for blocker / urgent situations |
| `shutdown_request` | Request a teammate to terminate | — |

### Delivery rules

- Teammate → Lead: automatic (no manual confirmation needed)
- Lead → Teammate: `SendMessage({ type: "message", recipient: "{name}", content: "...", summary: "..." })`
- **Idle is normal** — sending a message to an idle teammate auto-wakes them

### Shutdown workflow (mandatory)

After work completion, clean up in this order:

```typescript
// 1. Send shutdown_request to each teammate
SendMessage({ type: "shutdown_request", recipient: "frontend-dev", content: "Work complete" });
SendMessage({ type: "shutdown_request", recipient: "backend-dev", content: "Work complete" });

// 2. Each teammate replies with shutdown_response (automatic)
// 3. After all teammates have shut down, delete the team
TeamDelete();
```

> **Caution**: TeamDelete fails if any teammate is still active. Always wait for all teammates to shut down before calling.
