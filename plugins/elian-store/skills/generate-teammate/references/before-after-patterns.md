# BEFORE / AFTER patterns — generate-teammate

## 1. Approach selection

### ❌ BEFORE — phase-type-based selection (anti-pattern)

> "It's a build phase, so spawn a fullstack team of 4."

This produces a team where every phase forces the same shape. The build phase doesn't need cross-perspective debate; it needs files split. Result: 4 teammates idle waiting for synchronization that doesn't exist.

### ✅ AFTER — characteristic-based per-phase selection (correct)

> "Build phase: file ownership clear, no debate needed → Subagent (parallel). Design phase before it: API contract unsettled, FE/BE need to negotiate → Agent Team."

This matches each phase's coordination requirement. Build runs cheaply in parallel; design uses the heavy-coordination tool only where it pays.

---

## 2. File ownership

### ❌ BEFORE — overlapping ownership

```
frontend-dev → src/components/, src/app.tsx, src/api-client.ts
backend-dev  → src/api/, src/api-client.ts (shared client config)
```

Two teammates own `src/api-client.ts`. The last writer wins; bug discovered at integration.

### ✅ AFTER — strict ownership

```
frontend-dev → src/components/, src/app.tsx
backend-dev  → src/api/
api-contract → src/api-client.ts (single owner — could be either, decided up front)
```

Every file has exactly one owner. Conflicts are impossible.

---

## 3. Spawn prompt completeness

### ❌ BEFORE — hand-written vague prompt

```
"Help build the notification feature."
```

Teammate has no role, no scope, no DoD. Will produce something but it will not match the team's plan. Triggered by LLM filling the 7-slot template loosely under time pressure.

### ✅ AFTER — JSON-first authoring (v2.6+)

LLM writes the teammate as JSON; `create-document/scripts/render.py --template teammate-spawn` validates 7 required slots, blocks vague language (`help build`, `do something`, `TODO`, `...`), and produces a uniform Markdown spawn prompt.

```json
{
  "name": "frontend-builder",
  "subagent_type": "frontend-architect",
  "role": "Implement the resend trigger UI and status display for the Vue 3 admin screen.",
  "owned_files": ["mobidoc-front/src/views/notifications/"],
  "tech_stack": ["Vue 3", "TypeScript", "Pinia", "SCSS"],
  "task": "Build the resend trigger button, progress polling, and failure-reason display components.",
  "interfaces": "Call backend /api/notifications/retry and cache the response in the Pinia store.",
  "definition_of_done": "vue-tsc passes, unit tests cover loading/error/success states, and keyboard accessibility is checked.",
  "communication": "Ask backend-builder in a PR comment before changing the API contract."
}
```

Schema enforces:
- 7 required fields
- minLength on every field (long enough to be useful, not "thing")
- `mustMatch` on `task` (must contain an action verb such as implement, design, verify, build, or test)
- `mustMatch` on `definition_of_done` (must contain a measurable signal such as pass, cover, lint, or test)
- `forbid` patterns: `help build`, `do something`, `TODO`, `FIXME`, `...`

Failure mode: render exits 1, stderr lists every violating field. Fix JSON, re-render. No partial output.

See [example-teammate-spawn.json](../../create-document/references/example-teammate-spawn.json) for a 3-teammate end-to-end example.

---

## 4. Spawn prompt slot completeness

### ❌ BEFORE — missing communication slot

```
[ROLE] frontend-builder
[OWNED FILES] src/views/notifications/
[TECH STACK] Vue 3, TypeScript
[TASK] Build the retry UI.
[REFERENCE DOCS] design-spec.md
[INTERFACES] Calls /api/notifications/retry.
[DEFINITION OF DONE] Tests pass.
```

`COMMUNICATION` slot omitted entirely. Result: teammate operates in isolation, no PR-comment protocol, integration bugs surface late.

### ✅ AFTER — schema requires all 7 slots

If JSON omits `communication`, render fails:

```
schema invalid (1 error):
  teammates[0].communication: required field missing
exit 1
```

Cannot ship an incomplete prompt — the schema blocks it structurally.
