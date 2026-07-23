# roadmap.json Schema Reference

`design-feature` Phase 5 writes `roadmap.json`. `create-document` then renders
it via `build_roadmap.py` → `index.html`.

---

## Top-level fields

```json
{
  "label":     "GH-42",               // required — issue key or slug
  "title":     "One-line feature name", // required
  "lead":      "One paragraph summary", // optional
  "startDate": "2026-06-26",           // optional ISO date
  "phases":    [...],                  // required — see below
  "docs":      [...],                  // optional — generated documents
  "stakeholders": [...]               // optional — role → doc mapping
}
```

---

## phases[]

```json
{
  "name":  "Phase name",   // required
  "color": "#6366f1",      // optional hex — auto-palette if omitted
  "tasks": [...]
}
```

---

## tasks[]

```json
{
  "title":    "Task title",              // required
  "status":   "todo|doing|done|dropped", // required
  "reason":   "2026-07-03 review decision: excluded from implementation", // optional — why dropped
  "hold":     false,                     // optional — exclude from progress %
  "owner":    "BE engineer",             // optional
  "period":   "2026-06-26 – 2026-06-28", // optional
  "estimate": "2d",                      // optional
  "ticket":   "GH-42",                  // optional — linked issue key
  "priority": "P0|P1|P2",               // optional
  "labels":   ["backend", "DB"],         // optional

  "desc": [
    "Plain text description line.",
    "```mermaid\nsequenceDiagram\n  A->>B: call\n```"
  ],

  "criteria": [
    { "text": "Acceptance criterion", "done": true }
  ],
  "subs": [
    { "text": "Subtask", "done": false }
  ],
  "features": [
    {
      "name": "Feature group",
      "items": [
        { "t": "User-facing capability", "done": true, "sub": ["Concrete behaviour 1", "Concrete behaviour 2"] }
      ]
    }
  ],
  "deps": [
    { "tag": "blocker|dep", "text": "Depends on X" }
  ],
  "links": [
    { "label": "PRD", "url": "prd.md" }
  ],
  "activity": [
    { "who": "Daniel", "date": "2026-06-26", "text": "Decision note" }
  ]
}
```

### features[] — product-facing checklist

Optional. A grouped "what can a user actually do on this screen" checklist,
kept separate from `criteria`/`subs` (which track implementation). Rendered in
the drawer under **Capabilities** with ✓ (done) / ◐ (not done) icons, and the
task's board row shows a compact `capabilities done/total` counter so functional
completeness is visible without opening the drawer. Use it for a screen or
menu complex enough to warrant a functional breakdown; skip it for small,
well-understood tasks.

```json
"features": [
  {
    "name": "Authentication",             // group name (required)
    "items": [                            // required, ≥ 1 item
      {
        "t":    "Users can sign in with email", // required — capability, behaviour-first
        "done": true,                     // required
        "sub":  ["Validate format", "Show failure message"] // optional — concrete behaviours
      }
    ]
  }
]
```

### dropped status + reason

`status: "dropped"` records an explicit decision **not** to build a
task/screen (descoped), instead of leaving it as `todo` forever. Dropped tasks
render with a **Dropped** badge and are excluded from the progress % denominator
(like `hold`). `reason` is **required** for dropped tasks — record why,
ideally naming the decision date / source. `hold: true` combined with
`status: "dropped"` is a validation error — set exactly one.

```json
{ "title": "SSO integration", "status": "dropped", "reason": "2026-07-03 review decision: excluded from implementation" }
```

### Mermaid in desc

Any `desc` item that is a fenced mermaid block is rendered as a diagram:

```
"```mermaid\nstateDiagram-v2\n  [*] --> Active\n```"
```

Use this for state machines, sequence diagrams, and flow diagrams that
illustrate what a task implements. Plain text items render as paragraphs.

---

## docs[]

```json
{
  "label":  "PRD",               // display name
  "href":   "prd.html",          // relative path from index.html
  "layer":  "Planning",           // optional — category badge
  "reader": "PM, leadership"     // optional — audience note
}
```

---

## stakeholders[]

```json
{
  "role": "Frontend engineer",
  "docs": "design-spec.md + api-spec.md"
}
```

---

## Minimal valid example

```json
{
  "label": "feat-login",
  "title": "Email + password login",
  "phases": [
    {
      "name": "Design",
      "tasks": [
        { "title": "Domain model", "status": "done" },
        { "title": "API spec",     "status": "doing" }
      ]
    },
    {
      "name": "Implementation",
      "tasks": [
        { "title": "Backend", "status": "todo" },
        { "title": "Frontend", "status": "todo" }
      ]
    }
  ]
}
```
