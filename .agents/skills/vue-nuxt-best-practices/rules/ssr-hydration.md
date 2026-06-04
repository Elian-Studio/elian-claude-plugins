---
title: Keep SSR and hydration deterministic
impact: CRITICAL
tags: nuxt, ssr, hydration, client-only
---

# Keep SSR And Hydration Deterministic

Nuxt pages should render the same initial structure on the server and client unless a narrow client-only boundary is intentional.

## Apply When

- The task touches pages, layouts, plugins, route rules, or browser-only APIs.
- There is a hydration mismatch, flicker, layout shift, or SSR-only failure.
- The proposed fix uses `ssr: false`, `<ClientOnly>`, or a `.client.ts` plugin.

## Why

- Hydration mismatches are correctness issues, not cosmetic warnings.
- Broad CSR fallback loses SSR benefits and can hide security or data-loading bugs.
- Browser-only state in render paths creates unstable initial markup.

## Incorrect

```vue
<script setup lang="ts">
const theme = localStorage.getItem('theme') ?? 'light'
const id = Math.random().toString(36)
</script>

<template>
  <section :data-id="id" :class="theme">
    ...
  </section>
</template>
```

## Correct

```vue
<script setup lang="ts">
const theme = useState('theme', () => 'light')

onMounted(() => {
  theme.value = localStorage.getItem('theme') ?? 'light'
})
</script>

<template>
  <section :class="theme">
    ...
  </section>
</template>
```

Use `<ClientOnly>` only around the browser-dependent subtree, not the whole page.

## Verification

- Check the route with SSR enabled.
- Look for hydration warnings in the browser console.
- Confirm server-rendered HTML does not depend on `window`, `document`, `localStorage`, viewport size, dates, random IDs, or locale values that can differ at hydration time.

## References

- https://nuxt.com/docs/guide/concepts/rendering
