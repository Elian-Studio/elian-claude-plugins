# Rule Sections

Use these section prefixes for new rule files.

| Prefix | Section | Default impact | Description |
|---|---|---:|---|
| `ssr-` | SSR and Hydration | CRITICAL | Universal rendering, hydration, client-only boundaries, route rendering |
| `data-` | Data Fetching | HIGH | `useFetch`, `useAsyncData`, `$fetch`, payload, refresh, error states |
| `component-` | Component Architecture | MEDIUM-HIGH | SFC structure, props/emits, slots, composables |
| `performance-` | Performance | HIGH | bundle size, lazy loading, re-rendering, large lists, media |
| `server-` | Server and Nitro | HIGH | `server/`, Nitro handlers, middleware, runtime config, secrets |
| `state-` | State Management | MEDIUM-HIGH | local state, `useState`, Pinia, SSR isolation, persistence |
| `a11y-` | Accessibility and UX | MEDIUM-HIGH | semantic HTML, forms, focus, keyboard, motion |
| `test-` | Testing | MEDIUM-HIGH | behavior tests, component tests, composables, server handlers |

Impact levels:

- `CRITICAL`: correctness, security, data loss, hydration failure, production outage
- `HIGH`: release-blocking performance, SSR, auth, API, or server boundary risk
- `MEDIUM-HIGH`: meaningful maintainability, UX, state, or test risk
- `MEDIUM`: localized improvement with moderate future cost
- `LOW-MEDIUM`: cleanup that prevents drift
- `LOW`: optional convention or readability improvement
