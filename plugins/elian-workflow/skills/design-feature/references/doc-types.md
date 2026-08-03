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

### erd-preview.html

**Readers**: All engineers, reviewers, onboarding  
**Content**: Interactive single-file ERD **lineage explorer** built from `ddl.sql`
via the sibling `erd-preview` skill — click a record to trace its lineage across
hard FKs and soft references over real or representative data, with a zoom/pan
viewer. Complements `design.md`'s static Mermaid diagram with actual rows.

**Required**: Optional — offered at the Phase 3 gate **only when `ddl.sql` was
produced**, generated on user confirmation.

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

### design-spec.md

**Readers**: Designers, frontend engineers  
**Content**: Screen list, information architecture, route map, per-screen
detail (layout + state diagram + interactions + mapped AC), common components,
user journeys (Mermaid flowchart per PRD scenario), entity state diagrams,
terminology table, open UX questions.

**Required Mermaid blocks**:
- `stateDiagram-v2` — for any entity with UI-visible lifecycle states
- `flowchart` — for screen flow (§2) and each user journey (§5)

**Generate when**: The feature changes any user-facing screen (including UI-only
changes). Skip for pure backend refactors, batch jobs, or migration-only changes.

**Guide**: `references/design-spec-guide.md`

---

### prd.md

**Readers**: Product managers, leadership  
**Content**: Problem statement, user stories, acceptance criteria (Given-When-Then
table per requirement), success metrics, out-of-scope items. Written in user
language — no technical terms. Follow the 12-section structure in
`references/prd-guide.md`.

**Generate when**: The feature has product / business significance — new user
capability, policy change, or measurable metric change.

**Guide**: `references/prd-guide.md`

---

### tech-spec.md

**Readers**: Frontend engineers, backend engineers, QA, reviewers  
**Content**: The developer-facing counterpart to `prd.md` and the entry point
into the Phase 3 documents. Summary and scope, a requirement → implementation
mapping table (every `prd.md` §6 AC → owning component / endpoint / table),
domain and data deltas, changed API contracts, implementation order and
dependencies, risks and rollback, test strategy. Technical terms are allowed —
the opposite of `prd.md`. Content already written in `design.md`, `ddl.sql`,
`architecture.md`, or `api-spec.md` is linked, never restated.

**Generate when**: `prd.md` was generated and the feature will be implemented —
i.e. whenever an engineer needs a single starting point. §2 maps `prd.md` §6 AC
IDs, so this document requires `prd.md` to exist: without it there is nothing to
trace and `design.md` + `architecture.md` already carry the engineering plan.
For an internal refactor (no PRD), generate it only if the work spans enough
components that the implementation order in §5 is worth writing down. Skip for
bug fixes and documentation-only changes.

**Guide**: `references/tech-spec-guide.md`

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
requirements and the acceptance criteria in prd.md.

**Generate when**: Always, unless the change is a one-line fix with no
behaviour surface.

---

## Generation decision table

| Condition | design.md | ddl.sql | architecture.md | design-spec.md | prd.md | tech-spec.md | api-spec.md | qa-checklist.md |
|-----------|:---------:|:-------:|:---------------:|:--------------:|:------:|:------------:|:-----------:|:---------------:|
| New feature with DB | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| New feature, no DB  | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| UI-only change      | — | — | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| Internal refactor   | ✅ | — | ✅ | — | — | cond | — | ✅ |
| Bug fix             | — | — | — | — | — | — | — | ✅ |

When in doubt, generate. A document that turns out to be unnecessary is cheaper
than a missing one discovered mid-implementation.
