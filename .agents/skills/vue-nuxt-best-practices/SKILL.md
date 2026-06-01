---
name: vue-nuxt-best-practices
description: Use when writing, reviewing, refactoring, or optimizing Vue 3 and Nuxt 3/4 applications. Applies a rules-based Vue/Nuxt skill pack covering SSR and hydration, data fetching, component architecture, performance, Nitro/server boundaries, state management, accessibility, and testing.
---

# Vue Nuxt Best Practices

You help build and review Vue 3 and Nuxt 3/4 applications with production-oriented defaults.

This is a rules-based skill pack inspired by Vercel's `agent-skills` structure. Keep this `SKILL.md` as the router and load only the relevant rule files from `rules/` for the user's task.

## How It Works

1. Identify whether the request is implementation, review, debugging, performance optimization, migration, or test strategy.
2. Inspect the smallest useful context: user-provided code first, then relevant project files if available.
3. Select the applicable rule files from `rules/`.
4. Apply Vue/Nuxt idioms directly. Do not translate React/Next.js patterns mechanically.
5. If editing code, keep changes small and verify with existing project scripts.
6. If reviewing, lead with concrete findings ordered by severity.

## Rule Index

Read only the rule files needed for the current task.

| Area | Rule file | Use when |
|---|---|---|
| SSR and hydration | [rules/ssr-hydration.md](rules/ssr-hydration.md) | SSR, SSG, SPA fallback, hydration mismatch, client-only boundaries |
| Data fetching | [rules/data-fetching.md](rules/data-fetching.md) | `useFetch`, `useAsyncData`, `$fetch`, payload, cache, loading/error states |
| Component architecture | [rules/component-architecture.md](rules/component-architecture.md) | SFCs, `<script setup>`, props/emits, slots, composables |
| Performance | [rules/performance.md](rules/performance.md) | bundle size, re-rendering, lazy loading, large lists, images/scripts |
| Server and Nitro | [rules/server-nitro.md](rules/server-nitro.md) | `server/`, Nitro handlers, runtime config, secrets, middleware, route rules |
| State management | [rules/state-management.md](rules/state-management.md) | local state, `useState`, Pinia, SSR state isolation, persisted state |
| Accessibility and UX | [rules/accessibility-ux.md](rules/accessibility-ux.md) | semantic HTML, forms, focus, keyboard interaction, motion, layout shift |
| Testing | [rules/testing.md](rules/testing.md) | Vitest, component tests, composables, Nuxt pages/routes, server handlers |

Use [rules/_sections.md](rules/_sections.md) for section priorities and [rules/_template.md](rules/_template.md) when adding new rules.

## Context Gathering

If the user provides code, diff, route, error output, or test results, use that first.

If repository access is available, inspect only the smallest useful surface:

```sh
git status --short
git diff --stat
git diff --name-only
```

Then inspect relevant files only as needed:

```text
package.json
nuxt.config.ts
app.config.ts
app/
pages/
layouts/
components/
composables/
plugins/
middleware/
server/
stores/
tests/
```

Detect:

- Nuxt major version and compatibility mode
- package manager and scripts
- SSR mode and route rules
- module list
- state library
- test framework
- deployment target if visible

If the target is unclear, ask for the route, component, diff, or feature goal.

## Output For Reviews

Lead with findings ordered by severity.

```md
## Vue/Nuxt Review

### Findings

| Severity | Area | Evidence | Impact | Recommendation |
|---|---|---|---|---|
| P0/P1/P2/P3 | SSR/data/component/performance/server/state/a11y/test | file:line or observed fact | ... | ... |

### Notes

- ...

### Testing

- ...
```

Severity:

- P0: correctness, security, data loss, production outage
- P1: release-blocking SSR, data, auth, performance, or API risk
- P2: maintainability, architecture, test, or user-experience improvement
- P3: optional cleanup or long-term improvement

## Output For Implementation

For implementation requests:

- state which rule files guided the change
- keep changes small
- match local style and package manager
- preserve existing public behavior unless asked
- use Nuxt/Vue APIs directly instead of inventing wrappers
- report changed files and verification results

If the user asks only for advice or review, do not edit files.

## Forbidden

- Applying React/Next-specific APIs or patterns directly to Vue/Nuxt
- Claiming tests were run without evidence
- Hiding hydration or SSR risks as style issues
- Moving secrets or privileged logic into client code
- Recommending broad CSR fallback when a narrow client-only boundary is enough
- Adding dependencies without checking existing project conventions
- Turning simple local state into global state without a demonstrated need

## Maintenance

This skill follows a Vercel-style rules pack layout:

```text
vue-nuxt-best-practices/
├── SKILL.md
├── README.md
├── AGENTS.md
├── metadata.json
├── rules/
│   ├── _sections.md
│   ├── _template.md
│   └── *.md
└── references/
    └── official-docs.md
```

When adding or changing rules, keep each rule focused and include incorrect/correct examples where useful.
