---
title: Test observable Vue and Nuxt behavior
impact: MEDIUM-HIGH
tags: vue, nuxt, testing, vitest
---

# Test Observable Vue And Nuxt Behavior

Prefer behavior tests that describe user-visible output, composable contracts, server handler behavior, and SSR/hydration-sensitive paths.

## Apply When

- The task adds or changes components, composables, pages, server handlers, stores, or data fetching.
- The change affects SSR, auth, payments, data models, or user-visible behavior.
- Existing tests assert implementation details instead of behavior.

## Why

- Vue component tests should protect rendered behavior and interaction.
- Composable tests should protect inputs, returned refs, side effects, cleanup, and error paths.
- Nuxt route/server behavior often needs integration-like coverage rather than isolated unit tests only.

## Incorrect

```ts
expect(wrapper.vm.internalFlag).toBe(true)
```

## Correct

```ts
await user.click(screen.getByRole('button', { name: 'Save' }))
expect(await screen.findByText('Saved')).toBeVisible()
```

For composables:

```ts
const { data, error, refresh } = useCustomerSummary('123')
await refresh()
expect(error.value).toBeNull()
expect(data.value?.id).toBe('123')
```

## Verification

- Use existing package scripts first.
- Report exact commands run.
- If no tests were run, say `Not run (not provided)` or explain why.
- For SSR/hydration-sensitive work, include a browser or Nuxt render smoke check when practical.

## References

- https://nuxt.com/docs/getting-started/testing
