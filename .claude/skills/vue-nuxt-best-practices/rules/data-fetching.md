---
title: Use Nuxt data fetching APIs intentionally
impact: HIGH
tags: nuxt, data-fetching, usefetch, useasyncdata
---

# Use Nuxt Data Fetching APIs Intentionally

Choose `useFetch`, `useAsyncData`, and `$fetch` based on SSR behavior, caching, payload serialization, and refresh/error needs.

## Apply When

- The task touches API calls, page data, composables, loading states, or server routes.
- Code calls `$fetch` directly from setup.
- Data fetching is duplicated between SSR and hydration.

## Why

- `useFetch` and `useAsyncData` integrate with Nuxt SSR payloads.
- Raw `$fetch` in component setup can fetch on the server and again on the client.
- Missing stable keys can make wrapped async data hard to cache, refresh, and reason about.

## Incorrect

```vue
<script setup lang="ts">
const products = await $fetch('/api/products')
</script>
```

## Correct

```vue
<script setup lang="ts">
const { data: products, pending, error, refresh } = await useFetch('/api/products', {
  key: 'products:list'
})
</script>
```

For custom async work:

```ts
export function useProductSummary(id: MaybeRef<string>) {
  return useAsyncData(
    () => `product-summary:${toValue(id)}`,
    () => $fetch(`/api/products/${toValue(id)}/summary`)
  )
}
```

## Verification

- Confirm loading, error, empty, and refresh behavior.
- Check that SSR and hydration do not duplicate unnecessary network work.
- Confirm credentials or secrets are hidden behind server routes when needed.

## References

- https://nuxt.com/docs/getting-started/data-fetching
