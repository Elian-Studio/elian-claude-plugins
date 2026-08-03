# PRD Guide

Reference for `design-feature` Phase 4. Read this before writing `prd.md`.

---

## Mandatory 12-Section Structure

Every PRD must follow this skeleton exactly. Do not add sections between §1–12
or remove any of them. The sections exist to cover every stakeholder's question
in a predictable order.

```markdown
# <label> <Feature Name> — PRD

| Item | Value |
|------|-------|
| Issue | <label> |
| Date | YYYY-MM-DD |
| Status | DRAFT |
| Readers | PM / leadership / designer / FE / BE / QA |
| Source design | claudedocs/<label>/design.md |

## 1. Overview
### 1.1 One-line summary
### 1.2 Why now
### 1.3 Value by user type (table: user role → value delivered)

## 2. Background
### 2.1 Current pain (what users do today without this)
### 2.2 Differentiation (vs. workaround or alternative)
### 2.3 What this release does NOT solve (→ §9)

## 3. Goals
### 3.1 Business goals (B-1, B-2, … with measurable target)
### 3.2 User goals (U-1, U-2, …)
### 3.3 Success criteria (numbers + deadline)

## 4. User personas
### 4.1 Primary user (role / skill level / daily job / pain)
### 4.2 Secondary user
### 4.3 Affected parties

## 5. Use scenarios
(Each as: situation → user expectation → success state)
### 5.1 Case 1: …
### 5.2 Case 2: …

## 6. Functional requirements
(Each requirement = user story + AC table)
### 6.1 <Domain 1>
### 6.2 <Domain 2>

## 7. Non-functional requirements
### 7.1 Performance / responsiveness
### 7.2 Reliability
### 7.3 Usability
### 7.4 Language / terminology (forbidden ↔ replacement table)

## 8. Key UX decisions
(Meeting or audit decisions that affect user-facing behaviour)

## 9. Out of scope
(Items explicitly excluded from this release, with reason and future issue)

## 10. Success metrics (detailed)
### 10.1 Adoption rate
### 10.2 UX quality
### 10.3 Operational efficiency
### 10.4 Stability

## 11. Open questions
### 11.1 …

## 12. Appendix
### 12.1 Glossary (internal concept → UI label)
### 12.2 References
### 12.3 Change log

## Review checklist
- [ ] No technical terms in body (see forbidden list below)
- [ ] Every §6 requirement has a user story + AC table
- [ ] Out-of-scope items listed in §9
- [ ] Success metrics are measurable
- [ ] Personas are specific (not "the user")
- [ ] Scenarios read as user journeys, not feature lists
- [ ] Readable by a non-technical executive
- [ ] Enough for a designer to start screen design
- [ ] Enough for BE to derive a Tech Spec
- [ ] Enough for QA to derive Given-When-Then cases
```

---

## AC Format (mandatory for every §6 requirement)

Every requirement in §6 must have a Given-When-Then acceptance criteria table.
Vague acceptance criteria ("should work correctly", "handle appropriately") are
rejected — they cannot be tested.

```markdown
| AC | Given | When | Then |
|----|-------|------|------|
| R1-AC1 | Precondition state | User action | Expected outcome |
| R1-AC2 | … | … | … |
```

**Good**: `Given hospital admin is logged in, When name field exceeds 100 chars and save is clicked, Then validation error appears and save does not occur`

**Bad**: `The system should validate the input correctly`

---

## Technical Term Blacklist

These terms are forbidden in the PRD body (§1–§8, §10–§11). The forbidden list
exists because these terms are meaningless to non-engineers and imply
implementation rather than behaviour.

| Forbidden | Allowed replacement |
|-----------|---------------------|
| Aggregate | Group / classification unit |
| Entity | Subject / object (or rephrase entirely) |
| Mapper | (rephrase as the behaviour it performs) |
| Controller, Service, Repository | (rephrase as the behaviour) |
| JSON | Configuration data / input format |
| SQL, DDL | Data storage / data structure |
| XOR | Exactly one of / mutually exclusive |
| Spec | Specification / rule |
| Endpoint | (avoid; describe the action instead) |
| `<ClassName>` references | (describe the feature, not the class) |

**Permitted exceptions**: §12.1 Glossary, §12.2 References, §9 Out of Scope
may mention technical terms when necessary for precision.

---

## Consistency Validation

Run these checks after Phase 4 document generation before reporting completion:

```bash
# 1. Tech term audit — output should be empty or contain only allowed sections
grep -nE "Aggregate|Entity|Mapper|XOR|DDL|Endpoint" claudedocs/<label>/prd.md

# 2. AC coverage — every sub-doc should reference PRD AC codes
grep -c "AC[0-9]" claudedocs/<label>/qa-checklist.md   # must be > 0

# 3. Out-of-scope consistency — spot-check that §9 items are excluded in QA
# (manual: scan PRD §9 list, confirm qa-checklist.md has no test for those items)
```

If check 1 finds hits outside §9, §12.1, §12.2 — revise before finalising.
If check 2 returns 0 — QA checklist is not linked to PRD requirements; revise.
