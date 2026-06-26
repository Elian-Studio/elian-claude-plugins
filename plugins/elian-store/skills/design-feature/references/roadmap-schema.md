# roadmap.json Schema Reference

`design-feature` Phase 5 writes `roadmap.json`. `create-document` then renders
it as `index.html` via `--template roadmap`.

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
  "status":   "todo|doing|done",         // required
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
  "layer":  "기획",               // optional — category badge
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
