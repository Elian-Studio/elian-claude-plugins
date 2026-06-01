---
title: Keep server-only work inside Nuxt server boundaries
impact: HIGH
tags: nuxt, nitro, server, runtime-config, security
---

# Keep Server-Only Work Inside Nuxt Server Boundaries

Secrets, privileged backend calls, and normalization logic belong in `server/` routes, Nitro handlers, or server-only utilities.

## Apply When

- The task touches `server/`, `plugins/`, runtime config, middleware, auth, API calls, or third-party SDKs.
- Client code imports secret-backed SDKs.
- Middleware performs data-heavy work globally.

## Why

- Nuxt exposes public runtime config to the client intentionally; private config must remain server-side.
- Nitro server routes provide a safe boundary for secrets, request validation, normalization, and cache headers.
- Global middleware can become a hidden performance bottleneck.

## Incorrect

```ts
// composables/useBilling.ts
const stripe = new Stripe(useRuntimeConfig().stripeSecretKey)
```

## Correct

```ts
// server/api/billing/session.post.ts
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)
  const body = await readBody(event)
  return createBillingSession(config.stripeSecretKey, body)
})
```

## Verification

- Confirm private runtime config is not referenced from client-reachable code.
- Check server handlers validate inputs and handle failures.
- Confirm cache headers or route rules are safe for the response.
- Check idempotency for retried POST-like operations.

## References

- https://nuxt.com/docs/guide/directory-structure/server
- https://nuxt.com/docs/guide/going-further/runtime-config
