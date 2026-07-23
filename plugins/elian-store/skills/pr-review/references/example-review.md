# Example review

A worked example of what the panel turns into. The point is the shape: verdict
first, blocking items with evidence, intent contrast, and conflicting opinions
surfaced rather than hidden.

## BEFORE / AFTER

A single-pass review reads like this:

```text
Looks mostly good. The new endpoint works. Might want more tests and check
the query performance. Approving.
```

The panel produces this instead:

```text
PR Review — Add member search endpoint  (PR #142, main <- feature/member-search)
Verdict: REQUEST CHANGES
Panel: 7 specialists + 6 personas   CI: pass

Blocking findings
- [CRITICAL] api/members/search.java:38 - search term is concatenated into the SQL
  WHERE clause.   (confirmed by: security, Evans)
  Evidence: "where name like '%" + term + "%'" — term is the raw request param.
  Impact: SQL injection; any caller can read or drop arbitrary tables.
  Suggested fix: bind the parameter; never interpolate request input into SQL.

- [HIGH] api/members/search.java:51 - results are unbounded.   (confirmed by:
  performance, Dean)
  Evidence: the query has no LIMIT and the handler returns the full list.
  Impact: a broad term loads the whole members table into memory; tail latency
  and OOM risk at scale.
  Suggested fix: add pagination (page/size) with a max page size.

- [HIGH] (requirement) PR body says "search by name or phone"; only name is
  searched.   (perspective: requirements-fit)
  Evidence: the query filters on name only; no phone column in the WHERE clause.

Non-blocking notes
- [MEDIUM] api/members/search.java:22 - no test for an empty search term.
  (perspective: tests/Beck)
- [LOW] api/members/SearchController.java:14 - handler also formats the response;
  consider moving formatting out of the controller.   (perspective: Martin)

Requirement coverage
- Search by name : satisfied
- Search by phone : missing
- Paginate results : missing

Trade-offs raised (conflicting perspectives)
- Beck: "drop the SearchCriteria builder, only one field is used — YAGNI."
  architecture lens: "keep it; the phone field and filters are still to come."
  -> author decides based on whether phone search lands this sprint.

Residual risk
- CI passed but covers only the name path; the phone requirement has no test at all.

Handoff
- Recommended next: /fix (injection + pagination + phone search), then re-run /pr-review.
```

## What the example demonstrates

- **Agreement raises confidence.** Security and Evans both flagged the SQL line, so
  it leads as CRITICAL with `confirmed by`.
- **Intent contrast is a first-class finding.** The missing phone search is not a
  code smell — the code is clean — but it fails the requirement, so it blocks.
- **Conflicts are surfaced, not resolved.** Beck and the architect disagree about
  the builder; the report hands that judgment to the author instead of silently
  picking one.
- **The verdict is honest.** One CRITICAL and an unmet requirement mean
  `REQUEST CHANGES`, not a soft "approving with comments".
