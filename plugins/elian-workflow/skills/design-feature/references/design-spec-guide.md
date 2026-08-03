# Design Spec Guide

Reference for `design-feature` Phase 4. Read this before writing `design-spec.md`.

`design-spec.md` is the FE-facing design document. Its job is to give designers
and frontend engineers a single source of truth for screen structure, flows,
and interaction behaviour — without repeating the domain model (that lives in
`design.md`).

---

## When to Generate

Generate `design-spec.md` whenever the feature changes any user-facing screen.
This includes UI-only changes with no backend model changes.

**Generate**: new screens, screen layout changes, new UI interactions, flow changes  
**Skip**: pure backend refactors, batch jobs with no UI surface, migration-only changes

---

## Mandatory 8-Section Structure

```markdown
# <label> <Feature Name> — Design Spec

| Item | Value |
|------|-------|
| Issue | <label> |
| Date | YYYY-MM-DD |
| Status | DRAFT |
| Readers | Designer, FE engineer |
| Source PRD | claudedocs/<label>/prd.md |

## 1. Overview
Purpose of this document. List of screens in scope.

## 2. Information architecture
- IA: menu tree from top level down to individual screens
- Route map: URL path → screen name mapping table
- Screen flow diagram (Mermaid `flowchart`)

## 3. Per-screen detail
One subsection per screen in scope:
### 3.1 <Screen Name>
- Entry paths (how the user arrives)
- Layout description (sections, columns, key elements)
- State diagram (Mermaid `stateDiagram-v2`) — loading / empty / data / error states
- Interactions (click / submit / scroll / filter behaviours)
- Mapped AC (which PRD acceptance criteria this screen satisfies)

## 4. Common components
Shared UI elements used across multiple screens:
- Filters, search bars
- Status badges and their values
- Confirmation dialogs (trigger condition + message + actions)
- Toast / notification patterns

## 5. User journeys
One subsection per PRD scenario (§5 Case N):
### 5.1 Case 1 — <scenario name>
Mermaid `flowchart` showing the screen-by-screen path through the scenario.

## 6. State diagrams
Entity lifecycle states that drive UI changes (Mermaid `stateDiagram-v2`).
Include: all states, all transitions, and which screens show each state.

## 7. Terminology
Internal concept name → UI label used in the product.

| Internal | UI label |
|----------|----------|
| PatientRecord | Patient chart |
| VisitStatus.SCHEDULED | Scheduled |

## 8. Open UX questions
Unresolved design decisions. Each item becomes a gate before implementation.
- [ ] OQ-1: …
- [ ] OQ-2: …
```

---

## Required Mermaid Diagrams

| Diagram type | Where | Rule |
|---|---|---|
| `stateDiagram-v2` | §3 per-screen, §6 entity lifecycle | Required for any entity with UI-visible states |
| `flowchart` | §2 screen flow, §5 user journeys | One per scenario in §5 |
| `sequenceDiagram` | §3 per screen (optional) | Use when screen involves an async call sequence that matters |

Mermaid diagrams replace text descriptions — if a flow can be drawn, draw it.

---

## Checklist

Before handing off to engineers:

- [ ] All screens in scope have a §3 subsection
- [ ] Each §3 subsection has a state diagram (if the screen has ≥ 2 states)
- [ ] All PRD §5 scenarios have a §5 user journey diagram
- [ ] §7 terminology table covers all labels visible in the UI
- [ ] §8 open questions are resolved or explicitly parked for a future decision
- [ ] No code terms (controller, service, repository, entity, DTO) in the body
- [ ] Route map in §2 matches actual router configuration (verify against codebase)
