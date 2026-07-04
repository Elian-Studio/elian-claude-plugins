---
name: functional-spec
description: >
  Bridge one or more wireframes to code-grounded implementation intent BEFORE
  writing code. FIRST designs a shared component catalog across ALL wireframes
  (so recurring UI — rows, cards, nav, buttons — is designed once, not per
  screen), THEN decomposes each screen's elements into function + states +
  done-criteria and a component contract that reuses the shared catalog or adds
  screen-specific components. Every claim is grounded: on an existing codebase to
  a real file:line, on a greenfield product to the designed API/entities. Emits a
  component-design catalog, a per-screen functional spec (.md), a robust
  wireframe↔spec "connected" HTML view, and a hub. Writes no product code.

  Use when wireframes/mockups exist (from /design-ui, /design-feature mockups, or
  hand-built) and you need function + component design before /implement. Trigger
  phrases: "write the functional spec", "component design from these wireframes",
  "connect wireframe to spec", "기능명세", "컴포넌트 설계", "/functional-spec".
when_to_use: >
  Wireframes for one or more screens exist and the next step is to design the
  shared component set and per-screen function/component contracts before
  implementation. Works on an existing codebase (grounds reuse to file:line) or a
  greenfield product (grounds to the designed API/entities). Sits after /design-ui
  or /design-feature mockups and before /implement. Skip when no wireframe exists
  yet (run /design-ui first) or for a pure backend change with no screen surface.
argument-hint: "<label> [screen...] [--out <dir>] [--from <mockups-dir>]"
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(mkdir *), Bash(ls *), Bash(open *), AskUserQuestion
disable-model-invocation: false
---

# /functional-spec — Wireframes → Component Design + Code-Grounded Spec

Turn approved wireframes into an implementation contract. It answers, across the
whole screen set: **which components exist** (designed once, shared), and for
every element on every screen: **what it does** and **what implements it** (reuse
this shared/existing component, add this new one, call this real endpoint). This
is the layer that makes `/implement` unambiguous and stops duplicate component work.

This skill **grounds its claims but writes no product code.** It is a specification.

## Two grounding modes

- **Existing codebase** — grep the real repo; every reuse claim resolves to a real
  `file:line`, every data source to a real endpoint/field.
- **Greenfield** (no code yet) — there is nothing to grep, so ground against the
  **design docs** (`api-spec.md`, `ddl.sql`, `design.md`): every data source cites
  a designed endpoint/entity; every component is new, designed in the target
  stack's conventions. Greenfield is a first-class mode, not an error.

## Where this fits in the workflow

```text
/design-ui or /design-feature (mockups/)        → wireframes exist
  -> /functional-spec                             ← YOU ARE HERE
     P0 Resolve inputs + grounding mode
     P1 Grounding (codebase OR design-doc)         once
     P2 Component Design (cross-wireframe catalog)  once  ← designs shared components
     P3 Functional decomposition                    per screen
     P4 Component contract (reuses P2 catalog)       per screen
     P5 BE/API dependency + open questions           per screen
     Gate
     P6 Render (catalog + per-screen .md + connected.html + hub)
  -> /implement
```

- **Upstream**: approved wireframes/mockups + `spec.json` / design docs.
- **This skill**: a shared component catalog + per-screen function/component contracts.
- **Downstream**: `/implement` builds from the contract; open questions gate it.

## References

- `references/component-design-template.md` — the cross-wireframe component catalog (P2)
- `references/functional-spec-guide.md` — the per-screen 5-section `.md` structure + example
- `references/connected-template.html` — the robust, isolated, responsive wireframe↔spec view
- `references/tokens.css` — shared visual tokens for the connected view

---

## Phase 0 — Resolve inputs + grounding mode

1. Parse `<label>`. If absent, ask once.
2. Resolve the mockup source: `--from <dir>`, else `claudedocs/<label>/mockups/`,
   else ask. Every screen must have a concrete wireframe file — never invent screens.
3. Load context if present: `spec.json`, `design-spec.md`, `api-spec.md`, `ddl.sql`,
   `design.md`, `decisions*.json`.
4. **Determine the grounding mode + root:**
   - Look for a product codebase: `spec.json` `context` (often names the repo/path),
     else git remote / cwd.
   - If a real repo exists → **codebase mode**; pin the absolute root (if 0 or >1
     plausible roots, ask once — never guess a copy).
   - If there is no product code yet (greenfield) → **greenfield mode**; the
     grounding source is the design docs. State this explicitly; do not loop asking.
5. **Resolve output dir** — default to a **sibling of the mockups dir**
   (`<mockups-parent>/functional-specs/`), so the connected view's
   `../mockups/tokens.css` link resolves. `--out` overrides.
6. Confirm the screen list **and grounding mode/root** with the user before proceeding.

---

## Phase 1 — Grounding (once)

Inventory what the wireframe elements map to, across all screens.

- **Codebase mode**: Grep/Glob for existing components, composables/services, and
  the real endpoints/fields. Every reuse claim → verified `file:line`; every data
  source → real endpoint/field at `file:line`. A bare path is not enough.
- **Greenfield mode**: read `api-spec.md` / `ddl.sql` / `design.md`; map each
  element's data need to a **designed** endpoint + field. No code to reuse → every
  component will be new (designed in P2).

Anything you cannot pin (to a `file:line` or a designed endpoint) becomes an open
question in P5 — never a silent assumption. Surface contradictions (element implies
data no endpoint returns; a fabricated mockup value like a hardcoded price/percent
with no source) — that is the highest-value output.

---

## Phase 2 — Component Design (cross-wireframe, ONCE)  ← the anti-duplication phase

**Read every wireframe together** before writing any per-screen spec. Extract the
recurring UI and design a **shared component catalog** so a row / card / badge /
nav / button is designed once, not re-invented per screen.

Produce `component-design.md` (rendered to HTML in P6). Contents:

- **Component inventory** — each recurring element as a named component
  (`FoodRow`, `ExpiryBadge`, `BottomNav`, `PrimaryButton`, `RecipeHeroCard`…).
- **Usage matrix** — component × screen table showing where each is used. Anything
  used on ≥2 screens is **shared** (designed once); single-use ones are
  screen-specific (still listed, owned by their screen).
- **Contract per shared component** — target file path (stack conventions), props,
  variants/states, and in codebase mode the existing component it maps to (`file:line`).
- **Design-system note** — shared tokens (color/spacing/typography) the components use.

This catalog is the source of truth P4 references. Do not let per-screen work
re-declare a shared component.

─ **Gate** — show the usage matrix + shared-component list; confirm before per-screen work. ─

---

## Phase 3 — Functional decomposition (per screen)

For each screen, build the **기능 분해 표**. One numbered row per wireframe element:

| Column | Content |
|--------|---------|
| 요소 | The wireframe element |
| 기능 | What it does on interaction |
| 데이터 소스·BE 의존 | Real/designed endpoint + field, or `UI-only` with justification |
| 상태 | empty / loading / error / selected / disabled behaviour |
| 상호작용·연동 | What it triggers, where it hands off |
| 완료 판정 | Concrete **real-server-round-trip** pass condition (no hardcoded shells) |

Number each element — the number anchors the wireframe marker to the spec row in
the connected view (P6).

---

## Phase 4 — Component contract (per screen, references the P2 catalog)

For each screen, map its elements to components — **reuse the catalog, don't
re-design shared ones**:

- **재사용 (from catalog / existing)** — name the shared component (link
  `component-design.md`), or in codebase mode the existing `file:line`. State the
  props/variant used here.
- **신규 (screen-specific only)** — components genuinely unique to this screen
  (target path, props, emits, state). If it turns out to recur, promote it to the
  P2 catalog instead of duplicating.
- **데이터 흐름** — screen → hook/composable → api client → endpoint → handoff.

---

## Phase 5 — BE/API dependency + open questions (per screen)

- **신규 (new BE/endpoint)** — the real change (field/query/table or, greenfield,
  the designed endpoint that must exist). Honesty line: "신규 테이블 N개".
- **기존 (unchanged)** — data already provided, with its source.
- **UI-only justification** — why some state needs no server round-trip.
- **미결 질문** — every unpinned assumption + every decision the wireframe/PRD leaves
  open (incl. fabricated mockup values with no data source). Numbered; each gates `/implement`.

---

## Gate — confirm before render

Show, per screen: element count, reuse-from-catalog vs new-screen-specific vs new-BE,
open-question count. Wait for confirmation before rendering.

---

## Phase 6 — Render

1. **`component-design.md`** (+ HTML in the hub) — the P2 catalog.
2. **`<screen>.md`** — the 5-section per-screen spec (① 개요 ② 기능 분해 표
   ③ 컴포넌트 계약[재사용 catalog + 신규] ④ BE/API 의존 ⑤ 미결 질문). See guide.
3. **`<screen>-connected.html`** — from `references/connected-template.html`. Left =
   the wireframe with numbered `data-n` markers; right = the ② table with matching
   `data-n`; **below the split, a rendered §③ component contract** section (links
   the catalog). Hovering either side highlights the pair.
   - **Robust table (critical):** the connected view links the wireframe's
     `tokens.css` to render the left pane, so its global classes (`.row`, `.card`,
     `.tag`…) WILL leak. The template must therefore use **namespaced classes
     (`.fs-*`) + a scoped reset** (`.fs-spec :where(table,tr,td,th){display:revert}`)
     so no wireframe CSS can collapse the table, and be **responsive** (the split
     stacks and the table reflows on narrow widths). Never rely on generic class
     names for the spec pane.
   - **Repeated-row rule:** per-row-repeating elements get their `data-n` marker on
     the **first row only** + a caption. Keep `data-n` 1:1 with the ② rows.
4. **`index.html`** — a hub linking `component-design`, and each screen's `.md` +
   `-connected.html`, with a one-line status per screen.

Design docs referenced by the hub (`design.md`, `ddl.sql`, `prd.md`, etc.) should be
rendered to HTML (via `create-document` / `document-writer`) so they open readable,
not as raw `.md`. Then report output paths + the aggregate open-question list.

---

## Standing rules

- Never write product code. Spec only.
- **Design shared components ONCE (P2).** A component used on ≥2 screens is designed
  in the catalog; per-screen specs reference it. Re-inventing it per screen is the
  duplicate-work failure this skill exists to prevent.
- No unverified claim. Codebase mode: resolve to `file:line`. Greenfield: cite a
  designed endpoint/entity. Otherwise it is an open question, not an assumption.
- Never fabricate: a mockup's hardcoded value (price, %, name) with no data source is
  an open question, not a spec value.
- Done-criteria are real-server-round-trip conditions, never "renders a shell".
- The connected view's spec table must survive any linked wireframe CSS
  (namespaced `.fs-*` + scoped reset) and be responsive — a project-specific patch
  is not acceptable; fix the template.
- `data-n` numbers match one-to-one between wireframe markers and spec rows.
- If no wireframe exists for a requested screen, stop and point to `/design-ui`.
