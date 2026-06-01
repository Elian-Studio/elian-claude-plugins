---
title: Optimize rendering and bundle cost with evidence
impact: HIGH
tags: vue, nuxt, performance, bundle, rendering
---

# Optimize Rendering And Bundle Cost With Evidence

Start with stable rendering, smaller bundles, and lazy loading before adding complex memoization or dependencies.

## Apply When

- The task touches large lists, heavy components, charts, icons, SDKs, media, or slow routes.
- Code imports broad utility/UI libraries.
- Rendering work repeats unnecessarily.

## Why

- Vue's reactivity is fast, but large DOM trees and heavy dependencies still dominate user-visible performance.
- Stable props and computed values reduce child updates.
- Client-only SDKs and large visualizations should not inflate first-load bundles.

## Incorrect

```ts
import * as Icons from 'some-large-icon-pack'
```

```vue
<template>
  <HeavyChart :rows="rows" />
</template>
```

## Correct

```ts
import { SearchIcon } from 'some-large-icon-pack/search'
```

```vue
<script setup lang="ts">
const HeavyChart = defineAsyncComponent(() => import('~/components/HeavyChart.vue'))
</script>

<template>
  <ClientOnly>
    <HeavyChart v-if="showChart" :rows="rows" />
  </ClientOnly>
</template>
```

For large lists, use virtualization instead of rendering thousands of rows.

## Verification

- Inspect bundle impact when dependencies are added.
- Check route-level loading and interaction latency.
- Confirm lazy-loaded components are not needed for first meaningful paint.
- Verify image dimensions and avoid layout shift.

## References

- https://vuejs.org/guide/best-practices/performance.html
