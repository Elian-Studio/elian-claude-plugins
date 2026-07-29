# Example 1: Fullstack Feature — Notification Center

End-to-end trace from user input to spawned teammates. Demonstrates the **explore → design → build → verify hybrid strategy**.

---

## Input

```
/generate-teammate Add a notification center feature.
Vue 3 frontend + Spring Boot backend. Push, email, and in-app channels.
Users can see history, mark as read, and configure preferences.
```

---

## Phase 1: Request Analysis

```typescript
{
  domain: 'fullstack',
  techStack: ['Vue 3', 'TypeScript', 'Pinia', 'Spring Boot', 'JPA'],
  deliverables: ['notification list UI', 'preferences UI', 'API endpoints', 'DB schema', 'channel adapters'],
  constraints: ['3 channels (push/email/in-app)', 'history persistence', 'preference per channel'],
  parallelizableUnits: ['BE API', 'FE UI', 'DB migration', 'channel adapters', 'tests']
}
```

---

## Phase 2: Work Phase Decomposition

```
┌────────────┬───────────────────────────────────┬──────────────────────────────────────┐
│   Phase    │              Content              │            Characteristics           │
├────────────┼───────────────────────────────────┼──────────────────────────────────────┤
│ A: Explore │ Existing notification code, BE/FE │ Independent / parallel; results only │
├────────────┼───────────────────────────────────┼──────────────────────────────────────┤
│ B: Design  │ API contract, DB schema, UI flow  │ Multi-perspective debate;            │
│            │                                   │ cross-layer coordination required    │
├────────────┼───────────────────────────────────┼──────────────────────────────────────┤
│ C: Build   │ BE API + FE UI in parallel        │ File-level separation; no debate     │
├────────────┼───────────────────────────────────┼──────────────────────────────────────┤
│ D: Verify  │ Security, perf, E2E               │ Independent reviews → aggregate      │
└────────────┴───────────────────────────────────┴──────────────────────────────────────┘

Phase dependencies: A → B → C → D
```

---

## Phase 3: Per-Phase Approach Decision

```
┌────────────┬───────────────┬───────────────────┬───────────────┬──────────────────────────────────┐
│   Phase    │  Agent Team   │    Subagent       │   Direct      │              Reason              │
├────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ A: Explore │ Unfit         │ ★ Fit             │ Possible      │ BE / FE separately, no debate    │
├────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ B: Design  │ ★ Fit         │ Possible          │ Unfit         │ API contract negotiation +       │
│            │               │                   │               │ FE / BE / DB coordination        │
├────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ C: Build   │ Unfit         │ ★ Fit             │ Possible      │ Contract fixed, files separated  │
├────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ D: Verify  │ Unfit         │ ★ Fit             │ Possible      │ Independent reviews, aggregate   │
└────────────┴───────────────┴───────────────────┴───────────────┴──────────────────────────────────┘

Strategy: hybrid — Subagent (explore) → Agent Team (design) → Subagent (build) → Subagent (verify)
```

---

## Phase 4-5: Team & Task Design

### Phase A — Subagents (parallel)

| Subagent | subagent_type | Task |
|----------|---------------|------|
| be-explorer | Explore | Find existing notification-related code in `src/main/java/`. Report any current `Notification*` classes, services, or DB tables. |
| fe-explorer | Explore | Find existing notification UI in `src/components/`, `src/pages/`. Report existing badge / toast components. |

### Phase B — Agent Team (Design Team — Variant A: Technical design)

```
Team: notification-design
Pattern: Design Team (Variant A)
Teammates: 4

| Role           | subagent_type        | Owned area                                |
|----------------|----------------------|-------------------------------------------|
| be-designer    | backend-architect    | api-spec.md, db schema, service interface |
| fe-designer    | frontend-architect   | UI flow, page structure, state shape      |
| ui-designer    | ui-ux-designer       | Visual spec for notification list, toasts |
| critic         | devil-advocate       | Pre-mortem: spam risk, retry storms, etc. |
```

**Deliverables**: `docs/design/notification-center.md`, `docs/api/notification-api.md`, `docs/design-system/notification-components.md`

### Phase C — Subagents (parallel)

| Subagent | subagent_type | Task | Reference |
|----------|---------------|------|-----------|
| be-builder | backend-architect | Implement `NotificationController`, `NotificationService`, `NotificationRepository`, DB migration | `docs/api/notification-api.md` |
| fe-builder | frontend-architect | Implement `NotificationCenter.vue`, `NotificationItem.vue`, Pinia store, i18n | `docs/design/notification-center.md` + `docs/design-system/notification-components.md` |

### Phase D — Subagents (parallel)

| Subagent | subagent_type | Task |
|----------|---------------|------|
| sec-reviewer | security-engineer | XSS in notification body, CSRF on mark-read, rate limiting on send |
| perf-reviewer | performance-engineer | N+1 on history load, list virtualization, payload size |
| qa-reviewer | quality-engineer | E2E: read flow, preference flow, multi-channel delivery |

---

## Phase 7: Execution (sketch)

```typescript
// Phase A — parallel Subagents
const [beNotes, feNotes] = await Promise.all([
  Agent({ subagent_type: 'Explore', prompt: 'Find existing notification code in src/main/java/. Report Notification* classes, services, tables.' }),
  Agent({ subagent_type: 'Explore', prompt: 'Find existing notification UI in src/components/, src/pages/. Report toast / badge components.' }),
]);

// Phase B — Agent Team
TeamCreate({ team_name: 'notification-design', description: 'Design notification center across BE/FE/UX' });
const taskApi  = TaskCreate({ subject: 'Author api-spec.md', description: '...' });
const taskDb   = TaskCreate({ subject: 'Author db-schema.md', description: '...' });
const taskUi   = TaskCreate({ subject: 'Author component spec',  description: '...' });
const taskFlow = TaskCreate({ subject: 'Author ui flow doc', description: '...' });
const taskCrit = TaskCreate({ subject: 'Pre-mortem',         description: '...' });

TaskUpdate({ task_id: taskApi.id, owner: 'be-designer' });
TaskUpdate({ task_id: taskDb.id,  owner: 'be-designer' });
TaskUpdate({ task_id: taskUi.id,  owner: 'ui-designer' });
TaskUpdate({ task_id: taskFlow.id, owner: 'fe-designer' });
TaskUpdate({ task_id: taskCrit.id, owner: 'critic' });

Agent({ subagent_type: 'backend-architect',  team_name: 'notification-design', name: 'be-designer',
        prompt: spawnPromptBeDesigner(beNotes) });
Agent({ subagent_type: 'frontend-architect', team_name: 'notification-design', name: 'fe-designer',
        prompt: spawnPromptFeDesigner(feNotes) });
Agent({ subagent_type: 'ui-ux-designer',     team_name: 'notification-design', name: 'ui-designer',
        prompt: spawnPromptUiDesigner() });
Agent({ subagent_type: 'devil-advocate',     team_name: 'notification-design', name: 'critic',
        prompt: spawnPromptCritic() });

// Wait for design deliverables, then Phase C
// ... (Subagent build), then Phase D (Subagent verify)
// Final: SendMessage(shutdown_request) → TeamDelete()
```

---

## Spawn prompt example (be-designer)

```
You are the be-designer on the notification-design team.

[ROLE]
Design the backend API contract and DB schema for the notification feature.

[OWNED FILES]
- docs/api/notification-api.md (you author)
- docs/design/db-schema.md (you author)
- Read-only: src/main/java/** (existing code)

[TECH STACK]
Java 17, Spring Boot 3.x, JPA / Hibernate, PostgreSQL.
Existing convention: Controller > Service > Repository > Domain.
Korean @DisplayName on tests; OpenAPI v3 for API spec.

[TASK]
Claim tasks where owner == "be-designer" from the shared TaskList and complete them.

[REFERENCE DOCS]
- Exploration result (from Phase A be-explorer): summarized in this prompt below
{paste beNotes summary}

[INTERFACES]
- fe-designer: API contract is jointly negotiated. Reach agreement before authoring.
- ui-designer: notification body length / styling constraints affect schema (max length).
- critic: pre-mortem may surface risks (e.g., notification spam) that affect the schema.

[DEFINITION OF DONE]
- api-spec.md complete: every endpoint has request, response, error codes
- db-schema.md complete: tables, columns, indexes, constraints
- Both docs reviewed and accepted by fe-designer (API contract) and ui-designer (length / style fields)

[COMMUNICATION]
- Negotiate API contract with fe-designer via SendMessage when shapes differ.
- Broadcast to lead when contract is finalized.
- Do not modify FE or UX docs directly.
```
