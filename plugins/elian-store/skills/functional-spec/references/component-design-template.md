# Component Design Guide (functional-spec Phase 2)

Read before writing `component-design.md`. This runs **once across ALL wireframes**,
before any per-screen spec. Its job: design the shared component set so recurring UI
is designed a single time and every screen references it — eliminating the duplicate
component work that per-screen-only design produces.

The rule of thumb: **a component used on ≥2 screens is shared** (designed here);
single-use components are listed too but owned by their screen.

---

## Structure

```markdown
# <label> — Component Design (cross-wireframe)

- Wireframes surveyed: <list of mockup files>
- Grounding mode: existing-codebase | greenfield (target stack: <e.g. React Native/Expo>)

## 1. Usage matrix (component × screen)
A table: rows = components, columns = screens, cell = ✓ where used. This is the
evidence for what is shared. Sort most-used first.

| Component | home | add | list | recommend | detail | shopping | Kind |
|-----------|:----:|:---:|:----:|:---------:|:------:|:--------:|------|
| BottomNav | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | shared |
| FoodRow | ✓ |  | ✓ |  |  |  | shared |
| ExpiryBadge | ✓ |  | ✓ |  |  |  | shared |
| PrimaryButton |  | ✓ |  | ✓ | ✓ | ✓ | shared |
| RecipeHeroCard |  |  |  | ✓ | ✓ |  | shared |
| ScanFrame |  | ✓ |  |  |  |  | screen-specific |
| CookStepChecklist |  |  |  |  | ✓ |  | screen-specific |

## 2. Shared component contracts
One subsection per shared component:
### FoodRow
- Path (stack convention): `src/components/FoodRow.tsx`
- Used by: home, ingredient-list
- Props: `{ icon, name, expiryLabel?, onPress? }`
- Variants/states: default / with-expiry-badge / pressable
- Codebase mode only: maps to existing `<path:line>` (or "new")
- Data: presentational — fed by the screen's hook; no direct API call

## 3. Screen-specific components
Short list — name, owning screen, one-line purpose, path. (Full contract lives in
that screen's §③.) If any later recurs, PROMOTE it here rather than duplicating.

## 4. Design system note
Shared tokens the components consume: color roles, spacing scale, typography, radius,
the token file (`../mockups/tokens.css` or the project's design tokens). Keep the
component set visually consistent by pulling from one token source.

## 5. Open component questions
Ambiguities that affect the shared set (e.g. "is the home 임박 card the same component
as shopping 지출 card, or two variants of one BigStatCard?"). Numbered; resolve before
/implement.
```

---

## Rules

- Survey **all** wireframes first. Do not design components screen-by-screen — that is
  exactly what produces `RecipeHeroCard` twice.
- Prefer one component with variants over two near-identical components.
- Codebase mode: a shared component that already exists must cite its `file:line`;
  don't propose a new one that duplicates it.
- Greenfield: name components in the target stack's conventions (RN: `PascalCase.tsx`
  under `src/components/`; Vue: `PascalCase.vue`; etc.).
- The per-screen §③ (Phase 4) must **reference** this catalog for shared components and
  only declare genuinely screen-specific ones.
