---
title: Choose the smallest SSR-safe state boundary
impact: MEDIUM-HIGH
tags: vue, nuxt, state, pinia, usestate
---

# Choose The Smallest SSR-Safe State Boundary

Use local state first, `useState` for SSR-safe shared Nuxt state, and Pinia for cross-route domain state that benefits from store semantics.

## Apply When

- The task touches local refs, shared state, Pinia stores, persisted state, or SSR request behavior.
- Module-scope mutable state appears in server-rendered code.
- A composable is becoming a hidden global store.

## Why

- Local state is easiest to reason about and test.
- `useState` prevents cross-request state pollution when used correctly.
- Pinia is useful for domain state, devtools, and testing, but it should not replace simple local state by default.

## Incorrect

```ts
let currentUser: User | null = null

export function useCurrentUser() {
  return {
    currentUser
  }
}
```

## Correct

```ts
export function useCurrentUser() {
  return useState<User | null>('current-user', () => null)
}
```

Use Pinia when the state has domain behavior:

```ts
export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const total = computed(() => items.value.reduce((sum, item) => sum + item.price, 0))
  return { items, total }
})
```

## Verification

- Confirm state does not leak across SSR requests.
- Confirm persisted state is minimal and versioned.
- Confirm tests cover observable behavior rather than store internals only.

## References

- https://nuxt.com/docs/getting-started/state-management
