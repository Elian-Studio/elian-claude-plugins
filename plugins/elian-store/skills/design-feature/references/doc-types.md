# Document Types

Reference for `design-feature` Phase 3 and Phase 4. Each entry describes one
document type: what it contains, who reads it, when to generate it, and the
Mermaid diagrams that belong in it.

---

## Phase 3 — Domain Documents (always generate)

### design.md

**Readers**: Backend engineers, architects  
**Content**:
- Domain model: aggregates, entities, value objects, relationships
- State machine: all states + valid transitions
- Key scenarios: numbered flows (happy path, edge cases)
- Decision log: major design choices and their rationale

**Required Mermaid blocks**:
- `stateDiagram-v2` — for any entity with lifecycle states
- `sequenceDiagram` — for each key scenario involving ≥ 2 services
- `erDiagram` — if new tables or relations are introduced

**Skip when**: The change is purely UI with no backend model changes.

---

### ddl.sql

**Readers**: DBAs, backend engineers  
**Content**: CREATE TABLE / ALTER TABLE statements with column comments
explaining business meaning, constraints, and enum values.

**Required**: Only when new tables or columns are added / changed.

---

### architecture.md

**Readers**: All engineers  
**Content** (AS-IS / Δ / TO-BE for each section):
1. Domain model (Mermaid `classDiagram` or `erDiagram`)
2. Backend layers (Spring/NestJS/Django — layer diagram)
3. Frontend (menu tree, screen flow — Mermaid `flowchart`)
4. Infrastructure (queues, cron, external integrations)

**Required Mermaid blocks**:
- `flowchart LR` for the overall system topology
- `sequenceDiagram` for cross-service interactions

**Skip when**: The change is entirely self-contained within one service layer.

---

## Phase 4 — Stakeholder Documents (generate based on need)

### prd.md

**Readers**: Product managers, leadership  
**Content**: Problem statement, user stories, acceptance criteria, success
metrics, out-of-scope items. Written in user language (not code terms).

**Generate when**: The feature has product / business significance — new user
capability, policy change, or measurable metric change.

---

### api-spec.md

**Readers**: Frontend engineers, API consumers  
**Content**: Endpoint list (method + path + description), request/response
schemas, error codes. OpenAPI-style but in Markdown.

**Generate when**: New REST/GraphQL endpoints are introduced, or existing ones
change their contract.

---

### qa-checklist.md

**Readers**: QA engineers, developers doing self-review  
**Content**: Given-When-Then acceptance test cases derived from the spec's
requirements and acceptance criteria.

**Generate when**: Always, unless the change is a one-line fix with no
behaviour surface.

---

## Generation decision table

| Condition | design.md | ddl.sql | architecture.md | prd.md | api-spec.md | qa-checklist.md |
|-----------|:---------:|:-------:|:---------------:|:------:|:-----------:|:---------------:|
| New feature with DB | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| New feature, no DB  | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| UI-only change      | — | — | ✅ | ✅ | — | ✅ |
| Internal refactor   | ✅ | — | ✅ | — | — | ✅ |
| Bug fix             | — | — | — | — | — | ✅ |

When in doubt, generate. A document that turns out to be unnecessary is cheaper
than a missing one discovered mid-implementation.
