# Architecture Guide

Reference for `design-feature` Phase 3. Read this before writing `architecture.md`.

---

## Mandatory 4-Section Structure

Every `architecture.md` must contain exactly these four top-level sections.
Do not merge, skip, or reorder them. A section that is not affected by this
feature still appears — use the one-liner note below.

| # | Section | Core content |
|---|---------|-------------|
| 1 | Overall architecture | DDD aggregates (Mermaid `classDiagram`), scenarios (Mermaid `flowchart`), table relations (Mermaid `erDiagram`), enums/states, references |
| 2 | Backend | Aggregate fields, invariants, methods; trigger events; send/processing flows |
| 3 | Frontend | **Real service menu tree** (top menu → sub menu → screen, not abstract components), screen flow (Mermaid `flowchart`), components, API call mapping table |
| 4 | Infrastructure | Message queues, batch schedules, external integrations, library rationale |

---

## AS-IS / Δ / TO-BE Skeleton

Every section must have exactly three subsections. This is non-negotiable —
the reader needs AS-IS context to understand what changed and why.

```markdown
## 1. Overall architecture
### 1.1 AS-IS — current state
### 1.2 Δ — changes
### 1.3 TO-BE — state after change

## 2. Backend
### 2.1 AS-IS
### 2.2 Δ
### 2.3 TO-BE

## 3. Frontend
### 3.1 AS-IS
### 3.2 Δ
### 3.3 TO-BE

## 4. Infrastructure
### 4.1 AS-IS
### 4.2 Δ
### 4.3 TO-BE
```

**When a layer is not affected by this feature**, fill the three subsections
with these one-liners instead of omitting them:

```markdown
### X.1 AS-IS
This layer is unchanged by this feature. See domain baseline for current state.

### X.2 Δ
No changes.

### X.3 TO-BE
Same as AS-IS.
```

---

## Mermaid Requirements

Every `architecture.md` must include at least:
- One `flowchart LR` showing the overall system topology
- One `sequenceDiagram` for any cross-service interaction

For domain models with new entities, include `classDiagram` or `erDiagram`.
Text description of flows is not a substitute for diagrams.

---

## Aggregate Color Convention

Copy this `classDef` block into every `flowchart` diagram for consistency
across documents and across developers reading them:

```mermaid
flowchart LR
    classDef aggTag    fill:#E8F5E9,stroke:#2E7D32,color:#2E7D32
    classDef aggRule   fill:#E6F1FB,stroke:#1565C0,color:#1565C0
    classDef aggBulk   fill:#FFF3CD,stroke:#E65100,color:#E65100
    classDef aggSpec   fill:#F3E5F5,stroke:#7B1FA2,color:#7B1FA2
    classDef aggRabbit fill:#FFEBEE,stroke:#C62828,color:#C62828
```

Apply with `class NodeName aggRule` inside the flowchart body.

| Class | Color | Aggregate type |
|-------|-------|----------------|
| `aggTag` | Green | Classification / Tag |
| `aggRule` | Blue | Policy / Rule |
| `aggBulk` | Orange | Batch / Bulk |
| `aggSpec` | Purple | Specification |
| `aggRabbit` | Red | Queue / Messaging |

---

## Frontend Section Rule

§3 Frontend must show the **real service menu** as it appears in the product,
not an abstract component hierarchy. A reader who has never seen the codebase
should recognise the screens from the menu tree.

**Good**:
```
Hospital Management
  └── Patients
        ├── Patient List
        └── Patient Detail
              ├── Basic Info tab
              └── Visit History tab
```

**Bad**:
```
<HospitalLayout>
  <PatientModule>
    <PatientListView />
    <PatientDetailContainer />
```

---

## Post-Generation Validation

Run these five checks after writing `architecture.md`. All must pass.

```bash
# 1. No unresolved placeholders
grep -n "{{" claudedocs/<label>/architecture.md
# Expected: no output

# 2. All four top-level sections present
grep -cE '^## [1-4]\.' claudedocs/<label>/architecture.md
# Expected: 4

# 3. All AS-IS / Δ / TO-BE subsections present
grep -cE '^### [1-4]\.1 AS-IS' claudedocs/<label>/architecture.md
# Expected: 4
grep -cE '^### [1-4]\.2 (Δ|changes)' claudedocs/<label>/architecture.md
# Expected: 4
grep -cE '^### [1-4]\.3 TO-BE' claudedocs/<label>/architecture.md
# Expected: 4

# 4. Mermaid fences are balanced (must be even count)
grep -c '^```' claudedocs/<label>/architecture.md
# Expected: even number

# 5. At least one Mermaid diagram
grep -c '^```mermaid' claudedocs/<label>/architecture.md
# Expected: >= 1
```

If any check fails, fix before proceeding to Phase 4.
