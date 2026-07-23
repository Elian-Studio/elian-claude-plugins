---
name: update-design
description: >
  Design-change propagation orchestrator. When an existing feature already has
  design documents (produced by /design-feature) and something changes —
  meeting feedback, code review findings, requirement additions — this skill
  analyses which documents are affected and updates only those, leaving the
  rest untouched. Runs an impact matrix, confirms scope with the user, then
  updates documents sequentially (spec.json → PRD → tech spec → schema →
  design → architecture → API spec → QA checklist → roadmap) and verifies
  consistency.

  Use when design docs already exist and must be brought in sync with new
  decisions. Trigger phrases: "update the design", "reflect this change in
  the docs", "propagate this decision", "the architecture changed", "update
  after review feedback", "sync the design docs", or when the user describes
  a requirement change after /design-feature has completed.
when_to_use: >
  Design documents exist under claudedocs/<label>/ and a change has occurred:
  meeting feedback, code review outcome, new constraint, revised requirement,
  or post-design decision. The scope of what to update is unknown — this skill
  figures that out. Do NOT use for: brand-new features (use /intake-spec +
  /design-feature), minor typo fixes (just Edit), or code implementation
  (use /implement).
argument-hint: "<label> [--scope design|ddl|arch|prd|api|qa|all] [--feedback \"<one-line change summary>\"]"
allowed-tools: Bash(ls *) Bash(grep *) Bash(git log*) Bash(git status*) Bash(git diff*) Bash(python3 *) Read Write Edit Glob Agent
disable-model-invocation: true
---

# update-design — Design-Change Propagation

## Philosophy

Design documents are **living snapshots**, not finished artifacts. Requirements
change, reviews surface problems, meetings settle open questions — the docs
must follow. This skill updates only what changed. Untouched documents stay
untouched; unnecessary diffs create review fatigue.

| | `/design-feature` | `/update-design` |
|---|---|---|
| Target | New feature (0 → 1) | Existing docs (update in place) |
| Phase order | Fixed pipeline | Dynamic — driven by impact |
| Value validation | Required | Skipped (already validated) |
| Solution exploration | Required | Only for major structural changes |
| Output | Full document set | Only affected files |

---

## Phase 0 — Preflight

### 0.1 Parse arguments

- `<label>` (required) — the `claudedocs/<label>/` folder key. If absent,
  extract from the current branch name or ask once.
- `--scope <area>` — if supplied, skip the impact matrix and target that area
  only. Areas: `design`, `ddl`, `arch`, `prd`, `api`, `qa`, `all`.
- `--feedback "<summary>"` — if supplied, skip the change-collection interview
  (Phase 1) and jump straight to Phase 2.

### 0.2 Document inventory

```bash
ls claudedocs/<label>/ 2>/dev/null
```

Show the user a table of what exists:

| Document | Path | Present |
|----------|------|---------|
| spec.json | `claudedocs/<label>/spec.json` | ✅ / ❌ |
| design.md | `claudedocs/<label>/design.md` | ✅ / ❌ |
| ddl.sql | `claudedocs/<label>/ddl.sql` | ✅ / ❌ |
| architecture.md | `claudedocs/<label>/architecture.md` | ✅ / ❌ |
| design-spec.md | `claudedocs/<label>/design-spec.md` | ✅ / ❌ |
| prd.md | `claudedocs/<label>/prd.md` | ✅ / ❌ |
| tech-spec.md | `claudedocs/<label>/tech-spec.md` | ✅ / ❌ |
| api-spec.md | `claudedocs/<label>/api-spec.md` | ✅ / ❌ |
| qa-checklist.md | `claudedocs/<label>/qa-checklist.md` | ✅ / ❌ |
| spec-coverage.json | `claudedocs/<label>/spec-coverage.json` | ✅ / ❌ |
| roadmap.json | `claudedocs/<label>/roadmap.json` | ✅ / ❌ |
| index.html | `claudedocs/<label>/index.html` | ✅ / ❌ |
| erd-preview.html | `claudedocs/<label>/erd-preview.html` | ✅ / ❌ |
| functional-specs/ (directory) | `claudedocs/<label>/functional-specs/` | ✅ / ❌ |

### 0.3 No-documents guard

If `claudedocs/<label>/` does not exist or contains no design documents:

> "No design documents found for `<label>`. Run `/design-feature <label>` to
> create them first, then return here."

Stop.

---

## Phase 1 — Collect change summary

Skip if `--feedback` was supplied.

Collect the change from the most available source (in priority order):

1. **Current user message** — extract the change description directly.
2. **Recent git log** — `git log -5 --oneline` for post-design decisions.
3. **Ask the user** with `AskUserQuestion`.

Structure the change internally as:

```
WHAT changed: <concise factual statement>
WHY it changed: <reason — review finding, requirement update, decision>
WHERE the impact likely lands: <initial guess at document areas>
```

If multiple independent changes are described, separate them — each has its
own impact scope.

---

## Phase 2 — Impact analysis

For each change item, run the following matrix against the documents that
actually exist (skip rows for absent files):

| Change type | spec.json | design.md | ddl.sql | architecture.md | design-spec.md | prd.md | tech-spec.md | api-spec.md | qa-checklist.md | spec-coverage.json | roadmap.json |
|-------------|:---------:|:---------:|:-------:|:---------------:|:--------------:|:------:|:------------:|:-----------:|:---------------:|:------------------:|:------------:|
| Requirement add/remove | ✅ | ✅ | cond | ✅ | cond | ✅ | ✅ | cond | ✅ | ✅ | ✅ |
| Schema / table change | — | ✅ | ✅ | ✅ | — | — | ✅ | cond | cond | — | cond |
| Flow / scenario change | — | ✅ | — | ✅ | cond | cond | ✅ | cond | ✅ | cond | cond |
| API contract change | — | cond | — | cond | — | cond | ✅ | ✅ | ✅ | cond | cond |
| Term / naming change | cond | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | cond |
| Business rule change | ✅ | ✅ | — | cond | — | ✅ | cond | — | ✅ | ✅ | cond |
| UX / screen change | — | — | — | cond | ✅ | cond | cond | — | ✅ | — | cond |

**cond** = re-evaluate against the specific change; default to "no impact"
unless the detail clearly touches that document.

Two documents are not in the matrix because they are conditional on a single
row each:

- `erd-preview.html` — **cond** on "Schema / table change": regenerate only if
  the file already exists (Phase 5 step 13). Never create it here.
- `functional-specs/` — **cond** on "UX / screen change": a screen document is
  only touched when that specific screen changed. Regenerate with
  `/functional-spec`, do not hand-edit the connected HTML.

`spec.json` is ✅ only where requirements themselves move — it stores
`requirements[]` / `acceptanceCriteria[]` / `outOfScope[]` and nothing else.
`roadmap.json` upgrades from **cond** to ✅ whenever the change adds work items
or drops planned ones.
`spec-coverage.json` follows the AC set, not the prose: ✅ when AC rows are added
or removed, **cond** when an API or flow change only moves where an existing AC
is proven. It exists only after `/spec-coverage init` — skip the column when the
file is absent.

Output a per-change verdict table:

```
## Impact analysis — <change title>

| Document | Impact | Reason |
|----------|--------|--------|
| design.md | ✅ Required | Domain model changes (entity X) |
| ddl.sql | ✅ Required | Table Y renamed, column Z added |
| architecture.md | ✅ Required | Flow updated (step 3 removed) |
| prd.md | ❌ None | Requirement level unchanged |
| api-spec.md | cond → ❌ | Endpoint signature unchanged |
| qa-checklist.md | ✅ Required | New AC derived from requirement |
```

Combine changes with OR union into a single update scope:

> **Update scope: `design.md`, `ddl.sql`, `architecture.md`, `qa-checklist.md`**

---

## Phase 3 — Pending decisions

Scan the change list for items that still require a decision before
the update can be written:

- Change offers alternatives ("option A or B")
- Change impacts multiple layers with trade-offs
- Open question in existing `design.md` (`> ⚠ Open question:`) becomes
  answerable by this change

| Pending decisions | Action |
|-------------------|--------|
| 0 | Continue to Phase 4 |
| 1–2 | Ask inline with `AskUserQuestion` |
| 3+ | Prepare a decision-dashboard input summary, stop, and ask the user to run `/decision-dashboard`; resume only after the decisions are returned |

---

## Phase 4 — Confirm scope

Show the impact summary and ask:

> **`<N>` documents need updating. How would you like to proceed?**
> A) Update all listed documents (recommended)
> B) Exclude some — tell me which ones to skip
> C) Revise the change description — go back to Phase 1
> D) Stop — save the analysis for later

On **D**: write the analysis to
`.claude/plans/<label>-update-<YYYYMMDD-HHmm>.md` so it can be resumed.

---

## Phase 5 — Sequential updates

Update documents **one at a time in this order** (skip absent or excluded docs):

1. **spec.json** — only when requirements or AC changed. Update
   `requirements[]`, `acceptanceCriteria[]` and `outOfScope[]` so a later
   `/design-feature` re-run does not regress to a stale spec — that regression
   is the entire reason this step exists.
2. **prd.md** — requirements level settles next; other docs follow
3. **tech-spec.md** — developer-facing PRD; requirement → implementation mapping
4. **ddl.sql** — schema is the ground truth for design.md / architecture.md
5. **design.md** — domain model, scenarios, decision log
6. **architecture.md** — flows, system topology — read `../design-feature/references/architecture-guide.md` before editing
7. **design-spec.md** — FE screens (if present and impacted)
8. **api-spec.md** — endpoint contracts
9. **qa-checklist.md** — Given-When-Then cases derived from updated AC
10. **spec-coverage.json** — re-seed the AC entries this change added or removed
11. **roadmap.json** — added / removed work items and `status: "dropped"`
12. **index.html** — re-render only if roadmap.json changed
13. **erd-preview.html** — only if ddl.sql changed and the file already exists

**Do not run updates in parallel.** Later documents reference earlier ones —
parallel edits risk contradictions.

### Per-document pre-edit read

Before editing each document:

1. Read the full current file.
2. Identify exactly which sections are affected by this change.
3. Edit only those sections.

### prd.md

Read `../design-feature/references/prd-guide.md` before editing. If adding a requirement:
add a new row in §6 with a Given-When-Then AC. If removing: strike or
delete the row and note in the decision log.

### tech-spec.md

Read `../design-feature/references/tech-spec-guide.md` before editing. Every
row of §2 (requirement → implementation mapping) must cite an `R#` / `AC#` ID
that exists in the **updated** `prd.md` §6 — update prd.md first, then bring
the mapping rows in line. Link to `design.md` / `ddl.sql` / `api-spec.md`
instead of restating their content.

### architecture.md

Read `../design-feature/references/architecture-guide.md` before editing. Keep the
AS-IS / Δ / TO-BE structure. Update only the affected section(s).

### spec-coverage.json

Only when the file already exists — `/spec-coverage init <label>` creates it, this
skill never does. Re-seed just the AC entries this change added or removed, and
leave every untouched entry alone: recorded evidence must survive the update.
Then either run the bundled renderer script directly or hand off an explicit
`/spec-coverage render <label>` command. Do not imply that a side-effect-gated
skill was invoked automatically.

### roadmap.json

Read `../design-feature/references/roadmap-task-guide.md` before editing.
Add tasks for new work, and record work that was explicitly cancelled with
`status: "dropped"` plus a `reason` — do not delete the task object, the
dropped record is the audit trail.

### index.html

Re-render only when `roadmap.json` actually changed in step 11. Use the same
invocation as `/design-feature` §5.2:

```bash
CD="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/create-document}"
CD="${CD:-${CODEX_HOME:-$HOME/.codex}/skills/create-document}"
python3 "${CD}/scripts/build_roadmap.py" \
  claudedocs/<label>/roadmap.json \
  --out claudedocs/<label>/index.html
```

If the script exits non-zero, show the error and stop.

### erd-preview.html

Only when `ddl.sql` changed **and** `claudedocs/<label>/erd-preview.html`
already exists. Never regenerate silently — offer it:

> "`ddl.sql` changed and `erd-preview.html` exists. Regenerate it with
> `/elian-store:erd-preview`?"

### Post-edit check

After each file:

```bash
git diff --stat claudedocs/<label>/
```

If diff is empty despite predicted impact, report it:
> "Predicted impact on `<file>` but no diff produced — please verify manually."

---

## Phase 6 — Consistency verification

Run these checks across the updated document set:

```bash
# 1. Term consistency — old term must not survive
grep -rn "<old-term>" claudedocs/<label>/

# 2. DDL ↔ design.md sync — table names must match
grep -oE "CREATE TABLE \w+" claudedocs/<label>/ddl.sql | sort

# 3. AC count — qa-checklist must have at least as many cases as prd AC rows
grep -c "AC[0-9]" claudedocs/<label>/prd.md 2>/dev/null
grep -c "Given" claudedocs/<label>/qa-checklist.md 2>/dev/null

# 4. Broken references inside updated docs
grep -oE '\[.*\]\([^)]+\.(md|sql|html)\)' claudedocs/<label>/*.md 2>/dev/null

# 5. tech-spec.md §2 AC IDs must all exist in prd.md — any output is a FAIL.
#    Match the full `R#-AC#` ID, not a bare `AC#`: R1-AC1 and R2-AC1 both
#    reduce to "AC1", so a bare match would let a wrong requirement prefix pass.
comm -23 \
  <(grep -oE '\bR[0-9]+-AC[0-9]+\b' claudedocs/<label>/tech-spec.md 2>/dev/null | sort -u) \
  <(grep -oE '\bR[0-9]+-AC[0-9]+\b' claudedocs/<label>/prd.md 2>/dev/null | sort -u)

# 6. roadmap.json is valid JSON
python3 -c 'import json;json.load(open("claudedocs/<label>/roadmap.json"));print("roadmap.json OK")'
```

Report:

```
## Consistency check

| Check | Result |
|-------|--------|
| Term consistency | ✅ PASS / ⚠ 1 stale occurrence in architecture.md |
| DDL ↔ design.md | ✅ PASS |
| AC coverage | ✅ PASS |
| Internal links | ✅ PASS |
| tech-spec AC IDs ⊆ prd AC IDs | ✅ PASS / ⚠ AC7 cited but missing from prd.md |
| roadmap.json valid JSON | ✅ PASS |
```

On any FAIL: fix it before Phase 7.

---

## Phase 7 — Summary and commit

### Change inventory

```markdown
## <label> — Design update complete

### Changes applied
1. <change item 1 — one line>
2. <change item 2 — one line>

### Files updated
| File | Lines changed | Summary |
|------|--------------|---------|
| `claudedocs/<label>/design.md` | +N / -M | <what changed> |
| `claudedocs/<label>/ddl.sql` | +N / -M | <what changed> |

### Files skipped
- `<file>` — no impact / excluded by user

### Open items
- None / <any item deferred>
```

### Commit prompt

Ask the user:

> **Ready to commit?**
> A) Yes — commit the updated documents (recommended)
> B) No — I need to review first

On **A**: if a `/commit` skill is available in this session, hand off to it.
It is not part of this plugin, so when it is missing do not fail — print the
plain git steps for the changed files instead. Do not execute them without the
user's explicit commit authorization:

```bash
git add claudedocs/<label>/
git commit -m "docs(<label>): propagate <one-line change summary>"
```

---

## Standing rules

- Never regenerate a document from scratch — update in place only.
- Never update a document that is not in the confirmed scope.
- If a Phase 5 edit would require understanding the full system context
  beyond what's in `claudedocs/<label>/`, read the relevant source files
  first rather than guessing.
- `design.md` open questions (`> ⚠ Open question:`) that this change
  resolves must be replaced with the settled decision.
- Do not invent new requirements. Only propagate what was stated in Phase 1.

## Related skills

| Skill | Relationship |
|-------|-------------|
| `/design-feature` | Creates the document set this skill updates |
| `/intake-spec` | Re-run before `/design-feature` if requirements changed dramatically |
| `/decision-dashboard` | Explicit handoff from Phase 3 when 3+ decisions are pending |
| `/spec-coverage` | Explicit handoff or direct bundled-script use for coverage artifacts |
| `/erd-preview` | Explicit handoff offered when `ddl.sql` changed |
| `/functional-spec` | Explicit handoff for an affected connected screen artifact |
| `/commit` | Optional, host-provided, and only after commit authorization |
