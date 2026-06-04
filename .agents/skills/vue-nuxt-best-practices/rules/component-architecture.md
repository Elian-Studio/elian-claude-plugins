---
title: Keep Vue components explicit and composables focused
impact: MEDIUM-HIGH
tags: vue, components, composables, script-setup
---

# Keep Vue Components Explicit And Composables Focused

Prefer explicit component contracts, small composables, and derived state over watcher-driven or prop-heavy designs.

## Apply When

- The task touches SFCs, reusable components, props/emits, slots, or composables.
- A component has many boolean props or hidden side effects.
- A composable acts like a hidden global store.

## Why

- Vue component APIs are easier to review when props, emits, and slots describe the contract.
- Computed state is easier to reason about than watchers that mirror other state.
- Composables should reuse behavior, not hide domain-wide mutable state unless that is explicit.

## Incorrect

```vue
<script setup lang="ts">
const props = defineProps<{
  primary?: boolean
  danger?: boolean
  ghost?: boolean
  loading?: boolean
  disabled?: boolean
}>()
</script>
```

## Correct

```vue
<script setup lang="ts">
const props = withDefaults(defineProps<{
  variant?: 'primary' | 'danger' | 'ghost'
  loading?: boolean
  disabled?: boolean
}>(), {
  variant: 'primary'
})
</script>
```

Prefer computed derivation:

```ts
const visibleItems = computed(() => items.value.filter(matchesFilter))
```

over watcher-driven mirroring:

```ts
watch([items, filter], () => {
  visibleItems.value = items.value.filter(matchesFilter)
})
```

## Verification

- Check whether the component has one clear reason to change.
- Confirm props/emits are typed.
- Confirm composables clean up listeners/timers and avoid hidden request-specific module state.

## References

- https://vuejs.org/guide/reusability/composables.html
