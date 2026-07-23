# Design artifact path migration (v3.2.0)

Version 3.2.0 changes the **default** output location of `/design-ui` and aligns the
design pipeline on a single canonical layout. This is a migration-required change:
nothing is moved or deleted automatically, but automation that assumed the old default
path must be updated.

## What changed

Old default output of `/design-ui`:

```text
claudedocs/design/<feature>/
```

New default output of `/design-ui`:

```text
claudedocs/<label>/mockups/
```

The pipeline now shares one canonical identifier `<label>` and one layout:

```text
claudedocs/<label>/
  spec.json          (from /intake-spec)
  mockups/           (from /design-ui, now including tokens.css)
    tokens.css
  functional-specs/  (from /functional-spec)
```

`/design-ui` now also emits `tokens.css` into the mockups dir, so the
`/functional-spec` connected view's `../mockups/tokens.css` link resolves.
`/functional-spec` already read `claudedocs/<label>/mockups/` by default; that
default is unchanged. `/design-feature` never emitted mockups — the documentation
that implied it did has been corrected.

## Impact on existing artifacts

- Existing artifacts under `claudedocs/design/<feature>/` are **not** moved or deleted.
- The new default applies only when neither `--out` (design-ui) nor `--from`
  (functional-spec) is given.
- Bookmarks or links pointing at `claudedocs/design/<feature>/` still work; the files
  are untouched. New runs simply write to the new default location.

## How to keep using existing artifacts

- Keep writing to the old location: `design-ui <label> --out claudedocs/design/<feature>/`.
- Read old mockups from functional-spec: `functional-spec <label> --from claudedocs/design/<feature>/`.
- `/functional-spec` input resolution priority: explicit `--from`, then the new default
  `claudedocs/<label>/mockups/`, then an unambiguous legacy `claudedocs/design/<label>/`
  (used only after telling you), otherwise it asks. It never silently reads a different
  project's artifacts.

## What to update in automation

- Scripts or docs that hardcode `claudedocs/design/<feature>/` as the design-ui output.
- Any handoff that passed `--from claudedocs/design/<feature>/` can drop the flag once
  mockups are produced at the new default.
- Roadmap or hub links already use `claudedocs/<label>/functional-specs/` and need no change.

## Before and after

Before (v3.1.2):

```text
design-ui checkout-flow        -> claudedocs/design/checkout-flow/{wireframe,visual,...}.html
functional-spec checkout-flow  -> input not found at claudedocs/checkout-flow/mockups/ (asks)
```

After (v3.2.0):

```text
design-ui checkout-flow        -> claudedocs/checkout-flow/mockups/{wireframe,visual,...}.html + tokens.css
functional-spec checkout-flow  -> reads claudedocs/checkout-flow/mockups/, writes claudedocs/checkout-flow/functional-specs/
```
