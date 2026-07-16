---
name: erd-preview
description: >
  Turn a table schema PLUS real rows into a single self-contained "Lineage
  Explorer" HTML file. Click one record and it highlights only that record's
  lineage — where it came from (upstream FK ancestors) and what it affects
  (downstream descendants) — dimming everything else. It follows both hard
  foreign keys (solid lines) and soft references (dashed lines: value-level
  logical joins that are NOT schema FKs, e.g. a non-PK column that points at
  another table's business key), writes an ancestors/impacts summary in a side
  panel, and ships a Figma-style zoom/pan viewer so large schemas stay
  navigable.

  Use this WHENEVER the user wants to see how tables relate over REAL data, or
  trace a single record end-to-end — even if they never say "ERD". Triggers:
  "ERD", "lineage", "trace this record", "data flow", "relationship diagram",
  "schema visualization", "table diagram", "show the relationships with real
  data", "soft reference", "DDL preview". The defining trait is that it fills
  the diagram with ACTUAL data (introspected from a DB or pasted), not invented
  example rows. Inputs: a live read-only DB tool, CREATE TABLE DDL, design docs,
  or pasted query results.
---

# ERD Lineage Explorer

Take a table schema + **real data** and fill a **validated HTML template** to
produce a single self-contained file where clicking a record traces its lineage.

The hard part — SVG wiring, up/down lineage traversal, soft references, zoom/pan,
the summary panel — is already solved in `assets/template.html`. This skill only
**fills five JS structures (`SCHEMA`/`RELS`/`DATA`/`LAYERS`/`KLABEL`) with real
data and validates them**. Never touch the JS below the `// ── render engine`
marker.

## Workflow

### 1. Pick a source

- **Live read-only DB** — the best source for real rows. Use whatever read-only
  database access is available (an MCP database tool, or a project `db-query`
  helper). Never issue writes.
- **DDL / CREATE TABLE** — establishes schema + hard FKs.
- **Design docs** — schema/columns/relationships from project design files.
- **Pasted query results** — a table the user already exported.

If no DB is reachable, ask the user for one of the offline sources above.

### 2. Establish schema + relationships

- **Hard FKs**: from DDL `FOREIGN KEY … REFERENCES`, or from the DB's
  `information_schema.key_column_usage`.
- **Soft references**: relationships that are not schema FKs but join by value
  (e.g. `send_history.patient_seq → consult.patient_seq`, or
  `group.category → category.name`). These do NOT come out of the schema —
  **confirm them with the user and add them to `RELS` with `soft:true`. Do not
  guess.** A soft reference's `to` column may not be a PK.
- **Cardinality**: FK column with a `UNIQUE` constraint → `1:1`; otherwise
  child→parent `N:1`. If ambiguous, ask.
- Before rendering, show the inferred hard/soft relationship list once and proceed.

### 3. Collect real data (the crux)

**If referential closure breaks, the lineage cannot be drawn.** Every FK cell
value must have its referenced row present in `DATA`. So:

- **Scope by a tenant key** to keep the set small and connected (e.g.
  `WHERE tenant_id = N`, `WHERE account_id = N`). Narrowing to one
  tenant/account/project makes the sampled rows actually reference each other.
- Sample rows per table, but ensure **each child's referenced parent row is
  included**. A safe method: pick a root record and walk the FK graph up/down.
- If a table has many rows, keep a representative slice (≤ ~12), preferring rows
  that are FK-connected to the others.
- If no DB is available, use the rows the user provided.

### 4. Compute LAYERS (left → right flow)

Topologically sort by hard-FK direction. **Parent (referenced) tables go in
earlier (left) layers.** Multiple tables may share one layer (same depth).
Exclude cycles and soft references from the ordering constraint.

### 5. Fill the five structures + header

Copy `assets/template.html` and replace the placeholders: `{{TITLE}}`,
`{{HEADER_TAG}}`, `{{SUBTITLE}}`, `{{QUICKCHIPS}}`, `{{SCHEMA}}`, `{{RELS}}`,
`{{DATA}}`, `{{LAYERS}}`, `{{KLABEL}}`.

**SCHEMA** — tables + columns. `pk:1` = primary key, `fk:1` = foreign-key column.
```js
[
  {name:'orders', cols:[
    {c:'id',t:'INT',pk:1},{c:'user_id',t:'INT',fk:1},{c:'status',t:'ENUM'}]},
]
```

**RELS** — relationships. `from`/`to` are `[table, column]`. `card` ∈
`{1:1,1:N,N:1}`. `color` is a per-relation hex. `soft:true` marks a soft
reference (dashed). The FK arrow runs child(from) → parent(to).
```js
[
  {from:['orders','user_id'], to:['users','id'], card:'N:1', color:'#2563eb'},
  {from:['send_history','patient_seq'], to:['consult','patient_seq'], card:'N:1', color:'#9aa3b2', soft:true},
]
```

**DATA** — real rows per table. **The first column is the PK/identifier** (used
as the row id). Every FK cell value must reference a row that exists in `DATA`.
```js
{
  users:{cols:['id','name'], rows:[[1,'Kim'],[2,'Lee']]},
  orders:{cols:['id','user_id','status'], rows:[[100,1,'DONE'],[101,2,'PENDING']]},
}
```

**LAYERS** — left→right layers, parents first.
```js
[['users'],['orders'],['order_items']]
```

**KLABEL** — table name → human label (used in the summary panel and boxes).
```js
{users:'User', orders:'Order', order_items:'Order Item'}
```

**Header**: `{{TITLE}}` = short title (browser tab). `{{HEADER_TAG}}` = a small
mono tag line (e.g. `ACME · ORDERS SCHEMA`), or empty string. `{{SUBTITLE}}` =
one-line description (the default sentence is fine). `{{QUICKCHIPS}}` = 2–3
representative-record chips (or empty string):
```html
<button class="qchip" data-t="orders" data-id="100" style="font-family:inherit;font-size:12.5px;font-weight:600;background:#fff;border:1px solid #c7ccd6;border-radius:999px;padding:7px 13px;cursor:pointer;color:#334155;">📦 Order #100</button>
```

### 6. Validate (required self-check)

After generating, always run:
```bash
python3 <skill-path>/scripts/validate.py <generated.html>
```
It checks referential integrity, cardinality labels, column existence, LAYERS
coverage, layer ordering, row counts, and KLABEL. **If it FAILs, fix the data
until it PASSes** before handing off. (It parses the JS literals with Node.)

## Output rules

- **Single HTML file.** No external CSS/JS/font/image references — everything is
  inline (the template already is). A system font stack keeps it self-contained.
- File location: where the user specifies; for project issue work, follow the
  project's doc convention; otherwise ask for a path.
- After finishing, report the path and tell the user to open it in a browser. If
  `file://` is blocked, suggest serving it with `python3 -m http.server`.

## Traps

- Never modify the JS below `// ── render engine`. Only fill the five structures.
- For arrows to connect, `RELS.from`/`to` column names must match `DATA`/`SCHEMA`
  column names **exactly** (character for character).
- **A soft reference's `to` may not be a PK** — use the value-matching join column.
- Scope real data so **every FK value has its referenced row in `DATA`**; otherwise
  that relationship won't be drawn (the validator warns "0 matches").
- Without scoping, row counts explode — narrow by a tenant key.
- In LAYERS, parents come first; a reversed order makes lines flow right→left
  (the validator catches this).
