---
title: Preserve semantic and keyboard-accessible UI
impact: MEDIUM-HIGH
tags: vue, nuxt, accessibility, ux, forms
---

# Preserve Semantic And Keyboard-Accessible UI

Use semantic HTML first, then ARIA where it adds missing semantics. Keep forms, focus, keyboard behavior, and motion accessible.

## Apply When

- The task touches forms, dialogs, menus, tabs, buttons, links, transitions, or route changes.
- UI relies on click-only handlers or non-semantic elements.
- Validation and loading states are added.

## Why

- Semantic HTML gives accessibility, keyboard support, and browser behavior for free.
- Vue makes it easy to add click handlers to any element, but that can break keyboard and assistive technology behavior.
- Route and modal changes often need explicit focus handling.

## Incorrect

```vue
<div class="button" @click="submit">Save</div>
```

## Correct

```vue
<button type="button" :disabled="pending" @click="submit">
  <span v-if="pending">Saving...</span>
  <span v-else>Save</span>
</button>
```

## Verification

- Check keyboard navigation.
- Confirm labels and error messages are connected to form fields.
- Confirm visible focus states.
- Confirm transitions respect `prefers-reduced-motion`.
- Confirm images have useful dimensions and alt text.

## References

- https://vuejs.org/guide/best-practices/accessibility.html
