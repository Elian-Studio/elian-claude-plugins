# DESIGN

Feature: `<feature-name>`

## Artifact Paths

- Brief: `brief.md`
- References: `references.md`
- Sitemap: `flow.html`
- Wireframe: `wireframe.html`
- Visual prototype: `visual.html`

## Design Direction

`<one precise aesthetic direction, not "modern clean">`

## Tokens

### Typography

| Role | Token | Value |
|---|---|---|
| Display | `--font-display` | `<font stack>` |
| Body | `--font-body` | `<font stack>` |
| Body size | `--text-body` | `16px` |
| Line height | `--line-body` | `1.5` |

### Color

| Role | Token | Value |
|---|---|---|
| Background | `--color-bg` | `<hex>` |
| Text | `--color-text` | `<hex>` |
| Primary | `--color-primary` | `<hex>` |
| Accent | `--color-accent` | `<hex>` |
| Border | `--color-border` | `<hex>` |

### Spacing

Base scale: `<4px or 8px>`

### Motion

- Duration:
- Easing:
- Reduced-motion behavior:

## Page Map

| Page ID | Purpose | Entry | Exit |
|---|---|---|---|
| page-1 | Overview and task selection | Initial route | page-2 or page-3 |
| page-2 | Focused detail or edit | page-1 row/action | page-1 or page-3 |
| page-3 | Confirm or result | page-1/page-2 action | page-1 |

## Order Preservation

| Page | Wireframe order | Visual component |
|---|---|---|
| page-1 | 1. Header, 2. Summary, 3. Work area, 4. Primary action | `<components>` |
| page-2 | 1. Context, 2. Detail, 3. Side actions | `<components>` |
| page-3 | 1. Review, 2. Result, 3. Return action | `<components>` |

## State Coverage

| Area | Default | Empty | Loading | Error |
|---|---|---|---|---|
| page-1 work area | yes | yes | yes | yes |
| page-2 detail | yes | yes | yes | yes |
| page-3 result | yes | yes | yes | yes |

## UX Checklist Result

Checklist source: `references/ux-checklist.md`

- Passed items:
- Failed items:
- Rework performed:

## Implementation Notes

- Reuse existing components:
- New components likely needed:
- Data dependencies:
- Accessibility notes:
- Browser QA notes:

## Next Step

Implement the production UI using this artifact set. Preserve page IDs, state coverage, and task paths unless the user approves a design change.
