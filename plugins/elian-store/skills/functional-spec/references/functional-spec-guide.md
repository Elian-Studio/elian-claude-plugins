# Functional Spec Guide

Reference for `/functional-spec` Phase 6 per-screen `.md`. Read after
`component-design-template.md` (the shared catalog is designed first, in Phase 2).

A functional spec is **not** a design spec. `design-spec.md` (from `/design-feature`)
describes screens in design language and deliberately bans code terms. A functional
spec does the opposite: it binds every wireframe element to code — components to
reuse (from the **shared catalog** or an existing file), new screen-specific
components, and the endpoint/field behind each element. It is the contract
`/implement` builds from.

**Grounding mode.** On an existing codebase, cite a real `file:line` for every
reuse and data source. On a **greenfield** product (no code yet), cite a
**designed** endpoint/entity from `api-spec.md` / `ddl.sql` / `design.md` instead —
every component is new (designed in the Phase 2 catalog). Never fabricate: a
mockup's hardcoded value (price, %, name) with no data source is an open question,
not a spec value.

**Shared components are NOT re-declared here.** §③ references the Phase 2
`component-design.md` catalog for anything used on ≥2 screens; this file only adds
components genuinely unique to this screen.

---

## Mandatory 5-section structure

Everything inside the fence below is the **literal skeleton of the generated artifact**. Emit the
headings, field names, column headers, and quoted example strings verbatim. The prose inside the
fence explains what to write under each label.

```markdown
# <Screen Name> V2 — Functional Specification

- Issue: <label> (context, parent if any)
- Source mockup: <path to the wireframe/mockup this spec is derived from>
- Plan: <path to the plan/roadmap task if one exists>
- Purpose: fix "what each element does + component contract" BEFORE code. This is a spec, not code.

## ① Screen overview
What the screen does, who uses it, the IA anchor (real menu/route), and the single
most important grounding fact (e.g. "Only one of six displayed fields needs new BE work; the rest already exist in the VO. Zero new tables.").

## ② Function decomposition
One numbered row per wireframe element. The number is the connected-view anchor.

| # | Element | Behavior | Data source / BE dependency | State (empty/loading/error/selected/disabled) | Interaction / handoff | Completion evidence |
|---|------|-----------|--------------------|------------------------------|--------------|----------|

- Data source: a **real** endpoint + field (`GET /patient` `VO.Simple.hpNo`) or `UI-only` with reason.
- Completion evidence: a real-server-round-trip condition — "The real API receives `keyword` and returns server-filtered rows (not client filtering)", never "the table renders".

## ③ Component contract
Front-end rules first (e.g. "Do not modify the existing view; use a new view; do not modify base components").

### Reuse (catalog / existing)
| Component | Source | Usage on this screen (props/variant) |
Shared components from `component-design.md` (name + "catalog"), or on a codebase
an existing component at its exact `file:line`. Do NOT re-design a shared component here.

### New (this screen only)
| Component/file | Placement (new) | Role | Props | Events/exposure | State |
Only components unique to this screen. If one turns out to recur, promote it to the
Phase 2 catalog instead of duplicating.

### Data flow
A short tree: view → composable → service → endpoint → selection/handoff. Include
the downstream handoff contract (object shape passed on) and the minimal change to enable it.

## ④ BE dependency / new work
### New (plan iN)
The real change: VO field, mapper/query (file + line range), table. Honesty line
("Zero new tables; one new aggregate"). Smallest change that satisfies the wireframe.
### Existing (BE unchanged)
Fields already provided + their source.
### UI-only justification
Why selection/label mapping needs no server round-trip.

## ⑤ Open questions
Numbered. Every unverified Phase-1 assumption + every real open decision. Each is a
gate before /implement. Tag `[BE]` / `[UX]` / `[Consistency]` as useful.
```

---

## Golden example (trimmed — real output shape)

Adapted from a real deliverable (issue `MPT-9457`, patient list V2). Note how every
claim is grounded:

**② Function decomposition (excerpt)**

| # | Element | Behavior | Data / completion evidence | Type |
|---|------|------|-----------------|------|
| 1 | Keyword search | Query the server by name, contact, or chart number (debounce, page=1) | `GET /patient` `search.keyword` → server-filtered rows (not client filtering) | Existing |
| 11 | Visit count | Show completed visit count | **New**: `consult_v2` COUNT(status∈CON-END/COM, type≠REC) → `visitCount:int`. The real API returns the count; no hardcoded shell | New BE |
| 13 | Send icon (row) | Open a single-recipient send window | `childWindowService.createCrmSendWindow({name,hpNo})` | Existing |

> Of 15 elements, exactly **one** is new BE (#11). The rest are existing-data display
> or client state. "Build the screen" really = assemble a new view + one aggregate.

**③ Reuse (excerpt)** — reuse is grounded in real paths:

| Component | Path | Usage contract |
|---------|------|----------|
| `MTable` | `src/components/base/MTable.vue` | Structure only. Built-in select mode conflicts with pagination → `selectable=false` plus a checkbox column slot |
| `MPagination` | `src/components/base/MPagination.vue` | `v-model="search.page"` `:totalRowCnt` `@change="movePage"` |
| `ModalPatientDetail` | `src/components/modal/ModalPatientDetail.vue` | Open with `showPatientDetail(seq)` |

**⑤ Open questions (excerpt)**

1. **[Consistency]** The plan says `GET /hospital/patient/search`, but `GET /patient` actually returns the rich mockup table. Correct the label.
2. **[BE]** Decide whether the visit-type dropdown filters through a server parameter or is display-only. `IHospitalPatientSearch` currently has no visit filter.

---

## Checklist

Before handing off to `/implement`:

- [ ] Every `②` row has a data source: codebase → `file:line`; greenfield → a designed endpoint+field; or a justified `UI-only`.
- [ ] Every `Completion evidence` cell in `②` is a real-server condition, not "renders".
- [ ] No fabricated value: any mockup hardcode (price/%/name) is in `⑤ Open questions`, not treated as real.
- [ ] Every `Reuse` entry in `③` names a catalog component or an existing `file:line` — shared components are NOT re-declared here.
- [ ] Every `New` component in `③` is genuinely screen-specific (recurring ones live in the catalog).
- [ ] `④ BE dependency / new work` counts new tables/endpoints honestly.
- [ ] `⑤ Open questions` lists every unpinned assumption — none silently promoted to fact.
- [ ] The connected view includes the §③ component section, its table survives the wireframe's linked CSS (`.fs-*` + scoped reset), and `data-n` matches ② rows one-to-one.
