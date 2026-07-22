# House component catalog

The rich components that make a document look "designed". **Paste them straight into the Markdown
as raw HTML blocks** — `build_doc.py` passes them through and the house CSS styles them automatically.

**Hard rule**: never write inline `style=` or new CSS. Combine only the classes below — that is what
keeps every document in the same tone. If you genuinely need a color, reuse the variables only
(`var(--accent)`, `var(--tip)`, `var(--warn)`, `var(--danger)`, `var(--muted)`).

---

## Callouts (Markdown syntax preferred)

Most of the time the GitHub-style syntax is enough, with no raw HTML:

```markdown
> [!NOTE]
> General reference. Context or background.

> [!TIP]
> A recommendation or a trick.

> [!IMPORTANT]
> The key point that must not be missed.

> [!WARNING]
> A risk to watch out for.

> [!CAUTION]
> Something not to do / a destructive operation.

> [!INFO]
> Supplementary information (neutral tone).
```

Multiple lines and lists work inside a callout too (prefix each line with `>`).

---

## Cards

A single card — one grouped idea in a box:

```html
<div class="card">
  <div class="card-title">Architecture decision</div>
  Standardize the connection pool on HikariCP and raise the maximum pool size to 50.
</div>
```

Card grid — 2-4 parallel items side by side (auto-fit, wraps to one per row when narrow):

```html
<div class="card-grid">
  <div class="card"><div class="card-title">Backend</div>Spring Boot 3.x</div>
  <div class="card"><div class="card-title">Frontend</div>Vue 3 + Pinia</div>
  <div class="card"><div class="card-title">DB</div>PostgreSQL 16</div>
</div>
```

---

## KPI tiles

Highlight numeric metrics. `delta up` (green) / `delta down` (red) show the direction of change:

```html
<div class="kpi-grid">
  <div class="kpi">
    <div class="num">820ms</div>
    <div class="label">p95 response time</div>
    <div class="delta down">+210ms</div>
  </div>
  <div class="kpi">
    <div class="num">99.2%</div>
    <div class="label">Availability</div>
    <div class="delta up">+0.3%p</div>
  </div>
</div>
```

Include the `delta` line only when there is a real change. Omit it for a plain current-state number.

---

## Two-column comparison (before / after, inside / outside, pros / cons)

```html
<div class="cols2">
  <div class="card"><div class="card-title">AS-IS</div>Synchronous call, 820ms average</div>
  <div class="card"><div class="card-title">TO-BE</div>Async + cache, 90ms average</div>
</div>
```

---

## Step list (procedures / workflows)

Numbered visual steps. Good for guides, tutorials, and procedure walk-throughs:

```html
<div class="steps">
  <div class="step">
    <div class="n">1</div>
    <div class="st-body"><b>Install dependencies</b><br>Run <code>./gradlew build</code> from the project root.</div>
  </div>
  <div class="step">
    <div class="n">2</div>
    <div class="st-body"><b>Set environment variables</b><br>Fill the DB connection details into <code>.env</code>.</div>
  </div>
</div>
```

> For a plain ordered list, Markdown's `1. 2. 3.` is enough. Use `.steps` when each step carries
> an explanation — an actual procedure walk-through.

---

## Badges / tags

Inline status labels:

```html
<span class="badge badge-accent">In progress</span>
<span class="badge badge-tip">Done</span>
<span class="badge badge-warn">Needs review</span>
<span class="badge badge-danger">Blocked</span>
<span class="badge badge-muted">On hold</span>
```

They can be mixed inline into table cells or next to a heading.

---

## Data tables

Write tables in Markdown — they get styled automatically, no extra class needed:

```markdown
| Metric | Before | After | Change |
|--------|-------:|------:|:------:|
| p95 response | 820ms | 90ms | <span class="badge badge-tip">−89%</span> |
| Error rate | 3.4% | 0.8% | <span class="badge badge-tip">Improved</span> |
```

- Alignment: `:---` left, `---:` right, `:---:` center.
- Line breaks inside a cell use `<br>`; inline code uses backticks.

---

## Code blocks

Specify a language and a small label appears at the top:

````markdown
```java
public record PaymentResult(String id, long amountKrw) {}
```
````

---

## Collapsible (long appendices / raw data)

Use raw HTML `<details>` directly:

```html
<details>
  <summary>Full log (click to expand)</summary>

  ```
  2026-06-07 12:00:01 WARN  pool exhausted
  ```
</details>
```

---

## Images / figures

```markdown
![Payment flow diagram](./images/payment-flow.png)
```

If you need a caption, use a raw HTML `figure`:

```html
<figure>
  <img src="./images/payment-flow.png" alt="Payment flow">
  <figcaption>Figure 1. Payment request processing flow</figcaption>
</figure>
```

Keep images in an `images/` directory next to the output HTML and reference them relatively (a
self-contained HTML inlines text only — images stay external files, so share them together).
