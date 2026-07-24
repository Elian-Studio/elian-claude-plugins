---
name: design-feature
description: >
  Self-contained design orchestrator. Takes a spec.json (from /intake-spec) or
  inline requirements and produces a full design document set: domain model,
  architecture, PRD, API spec, QA checklist, and a Mermaid-capable roadmap hub
  (index.html). Every phase is gated — the user confirms before proceeding.

  Use when requirements are clear and it is time to produce design artifacts.
  Trigger phrases: "design this feature", "generate the design docs", "run the
  design pipeline", "create the PRD and architecture", "/design-feature <label>".
  Can start from any phase with --start-from.
when_to_use: >
  Design work is ready to start — either /intake-spec just produced a spec.json,
  or the user has stated clear requirements and wants design artifacts. Phrases:
  "design this", "generate design docs", "create the architecture", "produce the
  PRD", "run design-feature". Also auto-follows /intake-spec when the user
  confirms the spec and says "proceed" or "next step".
argument-hint: "<label> [--start-from phase1|phase2|phase3|phase4|phase5] [--stop-after phase1|phase2|phase3|phase4|phase5] [--skip-value-check]"
allowed-tools: Bash(mkdir *) Bash(ls *) Bash(python3 *) Read Write Edit Glob Agent
disable-model-invocation: true
---

# design-feature — Feature Design Orchestrator

## Purpose

Turn a spec into a full design document set without touching the IDE.
Each phase has a clear output and ends with a user confirmation gate.
Resume any time with `--start-from phaseN`.

## References

- `references/doc-types.md` — which documents to generate and when
- `references/roadmap-schema.md` — roadmap.json format for Phase 5
- `references/roadmap-task-guide.md` — task title / desc / criteria / subs writing rules
- `references/prd-guide.md` — PRD 12-section structure, tech term blacklist, AC format, validation
- `references/architecture-guide.md` — 4-section structure, AS-IS/Δ/TO-BE rules, Mermaid conventions, validation
- `references/design-spec-guide.md` — FE design spec 8-section structure

---

## Phase 0 — Load spec

### 0.1 Resolve label

Parse `<label>` from the argument. If absent, ask once.

### 0.2 Load spec.json

Look for `claudedocs/<label>/spec.json`. If it is missing, fall back to the
legacy path `claudedocs/plans/<label>/spec.json` and, when that hits, print one
line: *"Loaded spec from the legacy path — new specs are written to `claudedocs/<label>/`."*

If found: read it and summarise in one sentence to confirm context.

If not found: prompt the user to paste requirements directly, then build an
in-memory spec with `label`, `title`, and `requirements` only.

### 0.3 Handle --start-from

If `--start-from phaseN` is supplied, jump to that phase. All prior phases are
treated as complete. If `--stop-after phaseN` is supplied, stop after that
phase and report what is remaining.

### 0.4 Auto-detect restart point

If `--start-from` was **not** supplied, scan `claudedocs/<label>/` and suggest
the appropriate start point based on what already exists:

| File present | Suggested action |
|-------------|-----------------|
| `index.html` | Pipeline complete — offer Phase 5 re-render only |
| `prd.md` | Phase 4 done — jump to Phase 5 (roadmap hub) |
| `design.md` | Phase 3 done — jump to Phase 4 (stakeholder docs) |
| nothing / spec.json only | Start from Phase 1 |

Show the detected start point and ask the user to confirm before jumping.
If the user supplied `--start-from`, skip this detection entirely.

---

## Phase 1 — Value validation [skip with --skip-value-check]

Ask these five questions in **one message** (not one per turn — they set the
frame, not interrogate):

1. What happens today when this feature does not exist?
2. What is the smallest version that would be useful?
3. What must be explicitly excluded from this iteration?
4. Who owns this feature's success metric?
5. What would cause this feature to be rolled back?

Listen to answers, identify if any response reveals a scope problem, and
surface it. Then ask:

> "Based on this, should we proceed with the full design, scope it down, or
> park it?"

─ **Gate** — wait for user choice before continuing. ─

---

## Phase 2 — Solution exploration

Run the solution exploration inline: present 2–3 distinct approaches using the
spec's `requirements` and `constraints`, compare complexity / time / risk, and
let the user pick. This mirrors the relevant brainstorm mechanics without
assuming another side-effect-gated skill can be model-invoked.

─ **Gate** — confirm chosen approach before generating documents. ─

---

## Phase 3 — Domain design documents

Read `references/doc-types.md` to decide which documents to generate.

### Output location

```
claudedocs/<label>/
  design.md
  ddl.sql          (if DB changes)
  erd-preview.html (optional — offered only when ddl.sql is produced)
  architecture.md
```

### Generation rules

**design.md**

- Section 1: Domain model — aggregates, entities, value objects (Mermaid `classDiagram`)
- Section 2: State machine — for any entity with lifecycle states (Mermaid `stateDiagram-v2`)
- Section 3: Key scenarios — numbered flows using Mermaid `sequenceDiagram`
- Section 4: Decision log — numbered decisions (D1, D2…) with rationale

Every new entity or flow that has states **must** have a Mermaid diagram.
Do not describe diagrams in text when a diagram communicates them better.

**ddl.sql** (when needed)

Include column comments explaining business meaning, not just field names.
Mark enum values with their allowed transitions.

**erd-preview.html** (optional — offer only when `ddl.sql` was produced)

When the design introduces or changes tables, offer to also emit an interactive
**ERD lineage explorer** via the sibling `erd-preview` skill: click a record to
trace its lineage across hard FKs and soft references, over real or
representative data. This makes the schema reviewable with actual rows, not just
the static Mermaid `classDiagram` in `design.md`.

- **Source**: the `ddl.sql` just written (tables, columns, FKs).
- **Data**: if the feature touches an existing DB the user can reach, sample real
  rows scoped by a tenant key so FK closure holds; otherwise fill representative
  FK-connected sample rows (3–5 per table) so every FK value has its referenced
  row present.
- **Soft references** (non-schema value joins) are not in the DDL — confirm them
  with the user before drawing.
- Follow `/elian-store:erd-preview`: fill its template's five structures
  (`SCHEMA`/`RELS`/`DATA`/`LAYERS`/`KLABEL`), run its `scripts/validate.py` until
  it PASSes, and write the single self-contained HTML to
  `claudedocs/<label>/erd-preview.html`.

Do not generate it silently — offer it at the Phase 3 gate and generate on
confirmation.

**architecture.md** — Read `references/architecture-guide.md` before writing.

Structure as AS-IS / Δ / TO-BE for each section. Use Mermaid `flowchart LR`
for system topology and `sequenceDiagram` for cross-service interactions.

### Execution strategy

For features touching ≥ 3 files or services, use a subagent per document to
avoid context pollution. For small features, write inline.

─ **Gate** — show document list + a one-paragraph summary of each. When `ddl.sql`
was produced, also ask: *"Generate an interactive ERD lineage explorer
(`erd-preview.html`) from the DDL?"* and produce it (per the erd-preview step
above) only on confirmation. ─

---

## Phase 4 — Stakeholder documents

Read `references/doc-types.md` for the generation decision table.

### Output location

```
claudedocs/<label>/
  design-spec.md  (if FE screens change)
  prd.md          (if product significance)
  tech-spec.md    (developer-facing counterpart to prd.md)
  api-spec.md     (if new/changed endpoints)
  qa-checklist.md
```

### Gate — choose document set

Before generating, ask the user:

> **Which document set?**
> A) Full — design-spec + prd + tech-spec + api-spec + qa-checklist
> B) Core — prd + tech-spec + api-spec
> C) PRD only
> D) Stop here

Include `design-spec.md` in option A only when the feature changes FE screens
(check `references/doc-types.md` generation table).

─ **Wait for user choice before generating anything.** ─

### Generation rules

Spawn parallel subagents (one per document) when generating 2+ documents.
Each subagent reads the Phase 3 documents as source material.

**design-spec.md** — Read `references/design-spec-guide.md` before writing.
8-section structure covering IA, per-screen detail, user journeys, state
diagrams, and terminology.

**prd.md** — Read `references/prd-guide.md` before writing. 12-section
structure, user language only (no tech terms). Every §6 requirement must have
a Given-When-Then AC table.

**tech-spec.md** — Read `references/tech-spec-guide.md` before writing.
7-section structure mapping every prd.md §6 AC to its owning component,
endpoint, and table. Technical terms are allowed; restating Phase 3 documents
is not — link to them.

**api-spec.md** — One section per endpoint: method + path, request schema,
response schema (200, 4xx, 5xx), auth requirement.

**qa-checklist.md** — Given-When-Then format. Derive cases from the spec's
`requirements` and the acceptance criteria in prd.md.

### Post-generation validation

After writing prd.md, run the consistency checks from `references/prd-guide.md`:

```bash
grep -nE "Aggregate|Entity|Mapper|XOR|DDL|Endpoint" claudedocs/<label>/prd.md
grep -c "AC[0-9]" claudedocs/<label>/qa-checklist.md
```

When `tech-spec.md` was generated, also run the AC-ID cross-check from
`references/tech-spec-guide.md` — no AC ID may appear in tech-spec.md §2 that is
absent from prd.md, and no prd.md AC may be left unmapped:

```bash
comm -3 \
  <(grep -oE '\bR[0-9]+-AC[0-9]+\b' claudedocs/<label>/tech-spec.md | sort -u) \
  <(grep -oE '\bR[0-9]+-AC[0-9]+\b' claudedocs/<label>/prd.md      | sort -u)
# Expected: no output
```

Fix before proceeding to Phase 5.

─ **Gate** — list generated documents and line counts. ─

---

## Phase 5 — Roadmap hub

### 5.1 Write roadmap.json

Read `references/roadmap-schema.md` for the schema and
`references/roadmap-task-guide.md` before writing task objects.

Create `claudedocs/<label>/roadmap.json` reflecting:
- phases derived from the design pipeline (Design, Implementation, QA…)
- tasks mapping to the documents and work items identified above
- `docs[]` linking to all generated HTML/MD files
- `stakeholders[]` mapping roles to which documents they should read

Also add a `docs[]` entry for `spec-coverage.html` so the hub links it once
implementation starts. The file does not exist yet — the sibling `spec-coverage`
skill writes it on the first `/spec-coverage init <label>` — but the entry belongs
in the hub from the start. Use the existing schema fields, no new ones:

```json
{ "label": "Spec coverage", "href": "spec-coverage.html",
  "layer": "Implementation", "reader": "Engineers, QA" }
```

Include Mermaid blocks in task `desc` where useful — e.g., a state diagram
in the "Domain design" task, a sequence diagram in the "API spec" task.

For a complex screen/menu task, optionally add a `features[]` product-facing
capability checklist (grouped ✓/◐ list, separate from `criteria`/`subs`) — see
`references/roadmap-task-guide.md`. Skip it for small, well-understood tasks.
Use `status: "dropped"` + `reason` to record a screen/task you explicitly
decided not to build (rather than leaving it as `todo`).

This skill produces design documents and the roadmap; it does **not** emit
wireframes/mockups. Screen artifacts flow through the pipeline as:
`design-feature` (design docs + roadmap) → `/design-ui` (writes
`claudedocs/<label>/mockups/` incl. `tokens.css`) → `/functional-spec`
(writes `claudedocs/<label>/functional-specs/`). All three share the same
canonical `<label>` and live under `claudedocs/<label>/`.

When a task represents a screen/menu that has a corresponding functional-spec
document — a `functional-specs/<screen>-connected.html` from the sibling
`functional-spec` skill, or any doc already in this feature's `docs[]` — add a
`links[]` entry on that task pointing to it, e.g.
`{"label": "Functional spec", "url": "functional-specs/<screen>-connected.html"}`.
Check the actual emitted filename before linking — do not guess.
A reviewer opening the screen's task drawer can then jump straight to its spec
instead of hunting through `docs[]`. Reuse the existing `links[]` field — no new
schema.

### 5.2 Render index.html

Locate `create-document` and call `build_roadmap.py` (which validates and renders):

```bash
CD="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/create-document}"
CD="${CD:-${CODEX_HOME:-$HOME/.codex}/skills/create-document}"
python3 "${CD}/scripts/build_roadmap.py" \
  claudedocs/<label>/roadmap.json \
  --out claudedocs/<label>/index.html
```

If the script exits non-zero, show the error and stop.

### 5.3 Report

Print a structured completion report:

```markdown
## <label> — Design Complete

### Artifacts
| Document | Path | Key metrics |
|----------|------|-------------|
| design.md | claudedocs/<label>/design.md | N Mermaid diagrams, M decisions |
| architecture.md | claudedocs/<label>/architecture.md | N sections, M diagrams |
| prd.md | claudedocs/<label>/prd.md | N AC, M scenarios |
| tech-spec.md | claudedocs/<label>/tech-spec.md | N AC mapped, M work items |
| design-spec.md | claudedocs/<label>/design-spec.md | N screens, M journeys |
| api-spec.md | claudedocs/<label>/api-spec.md | N endpoints |
| qa-checklist.md | claudedocs/<label>/qa-checklist.md | N test cases |
| index.html | claudedocs/<label>/index.html | roadmap hub |

(omit rows for documents that were not generated)

### Stakeholder access
| Role | Documents to read |
|------|-------------------|
| PM | prd.md |
| Designer | design-spec.md + prd.md §5–6 |
| FE engineer | tech-spec.md + design-spec.md + api-spec.md |
| BE engineer | tech-spec.md + design.md + ddl.sql + api-spec.md |
| QA | prd.md §6 + qa-checklist.md |

### Next steps
- Roadmap hub: claudedocs/<label>/index.html
- If screens change: /functional-spec <label> — bind each wireframe element to
  real components + APIs (code-grounded contract) before /implement.
- When implementation starts: /spec-coverage init <label> — seed the requirement
  → test checklist from these docs, so every AC is tracked until a passing test
  proves it.
- Commit and open PR: /finish-branch
```

---

## Standing rules

- Never generate code (controllers, services, migrations). Design only.
- Phase 3 documents drive Phase 4. Do not skip Phase 3 to "save time".
- Mermaid diagrams are required for state machines and cross-service flows.
  A paragraph of text describing a flow is not a substitute.
- Do not invent requirements not in the spec. If something is unclear,
  flag it with a `> ⚠ Open question:` callout in the document.
- When a phase's output would be empty (e.g., no DB changes → no ddl.sql),
  skip it silently. Report it in the Phase gate summary.
