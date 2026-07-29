# Tech Spec Guide

Reference for `design-feature` Phase 4. Read this before writing `tech-spec.md`.

`prd.md` is the non-developer PRD — `references/prd-guide.md` bans technical
terms from its body. `tech-spec.md` is its developer-facing counterpart: the
single entry point an engineer opens to find out what to build and in what
order.

**It is a map, not a copy.** Phase 3 already produced `design.md`, `ddl.sql`,
`architecture.md`, and Phase 4 produces `api-spec.md`. Anything written there is
**linked**, never restated. Duplication is the failure mode this document exists
to avoid: a restated schema goes stale the moment `ddl.sql` changes, and the
reader then has two contradictory sources.

---

## Mandatory 7-Section Structure

Every `tech-spec.md` must follow this skeleton exactly. Do not add sections
between §1–7 or remove any of them.

```markdown
# <label> <Feature Name> — Tech Spec

| Item | Value |
|------|-------|
| Issue | <label> |
| Date | YYYY-MM-DD |
| Status | DRAFT |
| Readers | FE / BE / QA / reviewer |
| Product PRD | claudedocs/<label>/prd.md |
| Source design | claudedocs/<label>/design.md |

## 1. Summary & scope
### 1.1 What is being built (2–4 sentences, technical framing)
### 1.2 In scope (bullet list of the systems/modules touched)
### 1.3 Out of scope (link: prd.md §9 — do not restate the list)

## 2. Requirement → implementation mapping
(The core of this document. One row per AC in prd.md §6.)

| Req | AC | Owning component | Endpoint | Table / store | Notes |
|-----|----|------------------|----------|---------------|-------|
| R1 | R1-AC1 | OrderService.place | POST /api/orders | order, order_item | idempotent on client key |
| R1 | R1-AC2 | OrderValidator | — | — | rejects qty <= 0 |

Every AC listed in prd.md §6 appears here exactly once. Use `—` when a column
does not apply; never leave a cell blank.

## 3. Domain & data impact
Deltas only. Link, do not copy.
- Domain model: claudedocs/<label>/design.md §1
- Schema: claudedocs/<label>/ddl.sql
- New tables / columns: <name> — one line each on why it exists
- Migration-relevant changes: nullability, defaults, backfill needs

## 4. API contract summary
Changed endpoints only. Full schemas live in claudedocs/<label>/api-spec.md.

| Method + path | Change | Breaking? | Consumers to notify |
|---------------|--------|:---------:|---------------------|
| POST /api/orders | new | no | web, mobile |

## 5. Implementation order & dependencies
Ordered list of work items, each with what must land first.

1. <item> — depends on: none
2. <item> — depends on: 1

Include a Mermaid `flowchart LR` when the dependency graph is not a straight line.

## 6. Risks, migration & rollback
| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|

- Migration steps (forward)
- Rollback plan (what to revert, what is irreversible, feature-flag state)

## 7. Test strategy
Layer-by-layer intent only — the case list belongs in
claudedocs/<label>/qa-checklist.md.

| Layer | What it must prove | Owner |
|-------|--------------------|-------|
| Unit | invariants in §3 | BE |
| Integration | endpoints in §4 | BE |
| E2E / manual | AC in §2 | QA |

## Review checklist
- [ ] Every AC in prd.md §6 has a row in §2
- [ ] Every AC ID in §2 exists in prd.md (no invented IDs)
- [ ] §3–§4 link to the Phase 3 / Phase 4 documents instead of restating them
- [ ] §5 order is executable — no item depends on a later one
- [ ] §6 has a rollback plan, not just a migration plan
- [ ] A new engineer can start work from this document alone
```

---

## Writing Rules

**Technical terms are allowed — this is the inverse of `prd-guide.md`.**
Aggregate, Entity, Repository, Endpoint, DDL, SQL, JSON, XOR, class names, and
table names are all expected here. The blacklist in `prd-guide.md` applies to
`prd.md` only. If you find yourself writing "the group classification unit" in
this document, write "the aggregate" instead.

**Cite real AC IDs.** Every §2 row must reference an AC ID that literally
appears in `prd.md` §6 (`R1-AC1` style). An invented ID silently breaks
traceability from product requirement to code — §2 is the only place that link
exists, so a wrong ID is worse than a missing row. The validation below catches
both directions.

**Link, never restate.** Anything already written in `design.md`, `ddl.sql`,
`architecture.md`, or `api-spec.md` gets a path reference and, at most, a
one-line "what changed". If a section is growing past a screenful of prose, you
are restating a Phase 3 document.

**Deltas only in §3 and §4.** An unchanged table or endpoint does not belong in
this document.

**No code.** File paths, class names, and endpoint signatures — yes. Method
bodies, migrations, and controller code — no. Design only.

**Unknowns are flagged, not guessed.** Use `> ⚠ Open question:` callouts, the
same convention as the other design documents.

---

## Consistency Validation

Run these checks after writing `tech-spec.md`. All must pass before reporting
Phase 4 complete. Replace `<label>` with the actual feature label.

```bash
# 1. AC IDs in tech-spec §2 that do NOT exist in prd.md  → fabricated IDs
comm -23 \
  <(grep -oE '\bR[0-9]+-AC[0-9]+\b' claudedocs/<label>/tech-spec.md | sort -u) \
  <(grep -oE '\bR[0-9]+-AC[0-9]+\b' claudedocs/<label>/prd.md      | sort -u)
# Expected: no output

# 2. AC IDs in prd.md that are NOT mapped in tech-spec.md  → unimplemented AC
comm -13 \
  <(grep -oE '\bR[0-9]+-AC[0-9]+\b' claudedocs/<label>/tech-spec.md | sort -u) \
  <(grep -oE '\bR[0-9]+-AC[0-9]+\b' claudedocs/<label>/prd.md      | sort -u)
# Expected: no output

# 3. All seven top-level sections present
grep -cE '^## [1-7]\.' claudedocs/<label>/tech-spec.md
# Expected: 7

# 4. The Phase 3 / Phase 4 documents are linked, not orphaned
grep -cE 'claudedocs/<label>/(design\.md|ddl\.sql|api-spec\.md|qa-checklist\.md)' \
  claudedocs/<label>/tech-spec.md
# Expected: >= 3

# 5. No unresolved placeholders
grep -n "{{" claudedocs/<label>/tech-spec.md
# Expected: no output
```

Checks 1 and 2 require `bash` (process substitution); they do not run under
`sh`. If check 1 prints anything, the ID is invented — fix the row or add the AC
to `prd.md`. If check 2 prints anything, a product requirement has no
implementation owner — add the missing §2 row.
