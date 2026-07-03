---
name: functional-spec
description: >
  Bridge a wireframe/mockup to code-grounded implementation intent BEFORE
  writing code. For each screen, decomposes every wireframe element into (a)
  what it does (function, states, done-criteria) and (b) the real components,
  composables, and API/data sources that implement it — every reuse claim
  resolved to an actual file path, every data source to a real endpoint/field.
  Produces a per-screen functional spec (.md), a wireframe↔spec split "connected"
  HTML view, and an index hub. Reads the codebase heavily; writes no product code.

  Use when a wireframe or mockup exists (from /design-ui, /design-feature
  mockups, or hand-built) and you need to nail down function + component
  contracts before /implement. Trigger phrases: "write the functional spec",
  "connect wireframe to spec", "component contract for this screen", "기능명세",
  "/functional-spec".
when_to_use: >
  A wireframe/mockup for one or more screens already exists and the next step is
  to define — grounded in the real codebase — what each element does and which
  existing components to reuse vs which new ones to create, before implementation
  starts. Sits after /design-ui or /design-feature mockups and before /implement.
  Skip when there is no wireframe yet (run /design-ui first), or for a pure
  backend change with no screen surface.
argument-hint: "<label> [screen...] [--out <dir>] [--from <mockups-dir>]"
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(mkdir *), Bash(ls *), Bash(open *), AskUserQuestion
disable-model-invocation: false
---

# /functional-spec — Wireframe → Code-Grounded Spec Bridge

Turn an approved wireframe into an implementation contract. The output answers,
for every element on the screen: **what does it do**, and **what real code
implements it** (reuse this existing file / create this new one / call this real
endpoint). This is the layer that makes `/implement` unambiguous.

This skill **reads code to ground its claims but writes no product code.** Its
job is a specification, not an implementation.

## Where this fits in the workflow

```text
/design-ui or /design-feature (mockups/)   → wireframe exists
  -> /functional-spec                        ← YOU ARE HERE
     P1 Codebase grounding
     P2 Functional decomposition
     P3 Component contract
     P4 BE dependency + open questions
     Gate
     P5 Render (.md + connected.html + index.html)
  -> /implement
```

- **Upstream**: an approved wireframe/mockup + `spec.json` / `design-spec.md`.
- **This skill**: per-screen function + component contract, bound to real code.
- **Downstream**: `/implement` builds from the contract; open questions gate it.

## References

- `references/functional-spec-guide.md` — the 5-section `.md` structure + golden example
- `references/connected-template.html` — the wireframe↔spec split-view shell
- `references/tokens.css` — shared visual tokens for the connected view

---

## Phase 0 — Resolve inputs

1. Parse `<label>` (e.g. `MPT-9457`). If absent, ask once.
2. Resolve the mockup source: `--from <dir>`, else `claudedocs/<label>/mockups/`,
   else ask for the wireframe path. Every screen must have a concrete wireframe
   file — this skill does not invent screens.
3. Load context if present: `spec.json`, `design-spec.md`, `api-spec.md`,
   `decisions*.json`. These constrain the spec; they do not replace codebase
   grounding.
4. **Resolve the codebase root** — Phase 1 greps *real* code, so pin which repo
   to grep before touching it. Resolution order:
   1. `spec.json` `context` field, which often names the repo/path
      (e.g. MPT-9457's says `front-doctor CRM: src/views/crm/...`).
   2. else infer from the git remote / current working directory.
   3. If **0 or >1** plausible roots exist (e.g. several checkouts of the same
      repo on disk), **ask the user once** to confirm the root. Do not guess a copy.
   Record the confirmed absolute root; **all Phase 1 grounding runs against it.**
5. **Resolve output dir** — default to a **sibling of the mockups dir**:
   `<mockups-parent>/functional-specs/` (in MPT-9457:
   `docs/domains/crm/<label>/functional-specs/` next to `.../mockups/`). This is
   what makes the connected view's `../mockups/tokens.css` link resolve. `--out`
   overrides. Only fall back to `claudedocs/<label>/functional-specs/` when the
   mockups live outside the repo.
6. Determine the screen list: explicit `[screen...]` args, else one per mockup
   file. Confirm the screen list **and the resolved codebase root** with the user
   before proceeding.

---

## Phase 1 — Codebase grounding (the differentiator)

This phase is what separates a functional spec from a design spec. **Do not
guess.** For each screen, inventory the real code that the wireframe elements map to:

- **Existing components** — Grep/Glob for tables, modals, inputs, selects,
  pagination, badges the wireframe shows (e.g. base `M*` components, `spec/`
  components). Record the exact file path.
- **Composables / services** — find the data-loading and state patterns already
  used by sibling screens; prefer reusing them over inventing new ones.
- **Endpoints & fields** — trace the real API the screen needs. Confirm the
  actual endpoint path and the actual response fields (VO/DTO). Read the
  controller/service/mapper to verify a field exists before claiming it.

Grounding rule: **every reuse claim must resolve to a verified `file:line`, and
every data source to a real endpoint/field cited at `file:line`.** A bare path is
not enough — Read/grep to the exact line that defines the component, method
signature, or field, and cite it (e.g. `PatientService.ts:28`,
`IHospitalPatient.ts:180`). Anything you cannot pin to a line does not become an
assumption — it becomes an open question in Phase 4.

State what you searched and what you found. If the codebase contradicts the
wireframe (element implies data that no endpoint returns, or the file sits
somewhere other than assumed — e.g. `HospitalPatientList.vue` under
`views/hospital/` not `views/crm/`), surface it — that is the highest-value
output of this phase.

---

## Phase 2 — Functional decomposition

For each screen, build the **기능 분해 표 (functional decomposition table)**.
One row per wireframe element:

| Column | Content |
|--------|---------|
| 요소 (element) | The wireframe element (search bar, row checkbox, pagination…) |
| 기능 (function) | What it does on interaction |
| 데이터 소스·BE 의존 | Real endpoint / VO field, or `UI-only` with justification |
| 상태 | empty / loading / error / selected / disabled behaviour |
| 상호작용·연동 | What it triggers, where it hands off |
| 완료 판정 (done) | Concrete, **real-server-round-trip** pass condition (no hardcoded shells) |

Number each element — the number is the anchor that ties the wireframe marker to
the spec row in the connected view (Phase 5).

---

## Phase 3 — Component contract

Split into **신규 (new)** and **재사용 (reuse)**, then a data-flow block.

**신규** — for each new file: target directory (following the project's existing
layout, not a new convention), role, props, emits/exposed API, owned state.
Justify each new component — if an existing one covers it, reuse instead (YAGNI).

**재사용** — for each reused component: **exact existing path** and the usage
contract (which props/slots/emits, and any constraint, e.g. "use slot not
built-in select-mode because pagination breaks it").

**데이터 흐름** — a short tree/diagram: view → composable → service → endpoint →
selection/handoff. Include any downstream handoff contract (e.g. the object
shape passed to the next screen) and the minimal change needed to enable it.

---

## Phase 4 — BE dependency + open questions

- **신규 (new BE)** — the real change: which VO field, which mapper/query, which
  table. State the honesty line: "신규 테이블 N개" / "신규 집계 N건". Prefer the
  smallest change that satisfies the wireframe.
- **기존 (BE unchanged)** — fields already provided, with their source.
- **UI-only justification** — why selection state / label mapping needs no server
  round-trip.
- **미결 질문 (open questions)** — every unverified assumption from Phase 1 and
  every real decision the wireframe leaves open. Each becomes a gate before
  `/implement`. Number them.

---

## Gate — confirm before render

Show, per screen: element count, how many are reuse vs new component vs new BE,
and the open-question count. Wait for the user to confirm before rendering.

---

## Phase 5 — Render

For each screen write:

1. **`<screen>.md`** — the full 5-section spec (① 화면 개요 ② 기능 분해 표
   ③ 컴포넌트 계약 ④ BE 의존/신규 ⑤ 미결 질문). Follow
   `references/functional-spec-guide.md`.
2. **`<screen>-connected.html`** — the wireframe↔spec split view from
   `references/connected-template.html`. Left = the actual wireframe with numbered
   `data-n` markers on each element; right = the decomposition table with matching
   `data-n`. Hovering either side highlights the pair. Tag each element 기존 /
   신규 BE / UI. Link `tokens.css` (co-located or the wireframe's own).
   - **Repeated-row rule**: for a table/list, elements that repeat per row
     (row checkbox, name cell, action icons…) get their `data-n` marker on the
     **first row only**, plus a caption like "6–14는 행마다 반복 (첫 행에만 번호)".
     Header-level and page-level elements (search, filter, select-all, pager) are
     numbered once. Keep the `data-n` numbers one-to-one with the ② table rows —
     a drifted or duplicated number is a broken anchor.
3. **`index.html`** — a hub linking every screen's `.md` and `-connected.html`,
   with a one-line status per screen (element count, new-BE count, open questions).

Then report the output paths and the aggregate open-question list — those are the
gates the user must clear before `/implement`.

---

## Standing rules

- Never write product code (views, components, controllers, migrations). Spec only.
- No unverified claim. A reuse path that does not resolve, or a field that does
  not exist, is a bug — verify with Read/Grep/`ls`, or demote it to an open question.
- Reuse-first: propose a new component only after confirming no existing one fits.
- Prefer the smallest BE change. Count new tables/aggregates honestly.
- Done-criteria are real-server-round-trip conditions, never "renders a shell".
- The connected view's `data-n` numbers must match one-to-one between the
  wireframe markers and the spec rows — a drifted number is a broken anchor.
- If no wireframe exists for a requested screen, stop and point to `/design-ui`.
