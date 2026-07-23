---
name: spec-coverage
description: >
  Answers "is every PRD requirement actually proven?" by binding each
  acceptance criterion to a real test result instead of a hand-ticked box.
  Seeds a leaf-level checklist from the design docs a feature already has
  (tech-spec.md §2, prd.md §6, api-spec.md, design.md, ddl.sql,
  qa-checklist.md), runs the project's test suite, parses the JUnit XML, and
  marks each AC pass / fail / skipped / unchecked. An AC that no test names is
  reported as `unchecked` — an unproven requirement, however "done" it looks.
  Writes claudedocs/<label>/spec-coverage.json (source of truth) and
  spec-coverage.html (readable view, machine-verified items visually separated
  from human-asserted ones).
when_to_use: >
  Design docs exist under claudedocs/<label>/ and implementation is under way,
  and someone asks how much of the PRD is really done, which acceptance
  criteria are still unproven, or wants requirement-to-test traceability
  before a release or review. Triggers: "is the PRD satisfied", "requirement
  coverage", "which AC are unproven", "/spec-coverage". Not for running a
  project's verify-* rule skills (use verify-implementation), not for gating a
  single claim (use verify-before-claiming), and not for plan/board status
  (use the roadmap index.html).
argument-hint: "init|check|render|apply <label> [patches.json]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(python3 *)
  - Bash(./gradlew *)
  - Bash(mvn *)
  - Bash(npm test*)
  - Bash(npm run*)
  - Bash(pytest*)
  - Bash(go test*)
  - Bash(git status*)
  - Bash(git diff*)
  - Bash(git log*)
---

# spec-coverage — requirement-to-test traceability

Tests are the source of truth. A requirement is proven when a test names it and
that test passes. Nothing else counts as proof.

## Commands

| Command | What it does | What it writes |
|---|---|---|
| `/spec-coverage init <label>` | Extract the seed from the design docs, build the checklist with no test data yet | `claudedocs/<label>/spec-coverage.json`, `.html` |
| `/spec-coverage check <label>` | **Run the test suite**, collect JUnit XML, re-decide every test-backed item, re-render | same two files |
| `/spec-coverage render <label>` | Re-render the HTML from the existing JSON | `claudedocs/<label>/spec-coverage.html` |
| `/spec-coverage apply <label> <patches.json>` | Apply manual evidence for the categories tests cannot decide | `claudedocs/<label>/spec-coverage.json` |

`<label>` is the design-pipeline label — the same `claudedocs/<label>/` folder
`/design-feature` writes to. With no argument, derive it from the branch:

```bash
LABEL="${1:-$(git branch --show-current | grep -oE '[A-Z]+-[0-9]+' | head -1)}"
[ -n "$LABEL" ] || { echo "No label given and none in the branch name."; exit 1; }
```

## The AC ↔ test binding

An AC ID (`R1-AC1` form, matching `\bR[0-9]+-AC[0-9]+\b` — the same IDs
`design-feature` validates in `tech-spec.md` §2) goes in the test's display
name. That is the whole contract: no manifest, no annotation, no extra file.

```java
@DisplayName("R1-AC1 a name longer than 100 chars shows a validation error")
```

```ts
it('R1-AC2 the order button is disabled when stock is 0', () => {})
```

The project must adopt this convention — prefix the ID, keep the existing
display-name style otherwise. Without the prefix, the test exists but proves
nothing this skill can see, and its AC is reported `unchecked`.

The ID must be in the **display name**. The class name is deliberately not
scanned: binding on it would make every testcase in a class named after an AC
count as that AC's proof, so an unrelated passing helper could stand in after
the real test was deleted.

### Verdict rules

| Condition | Status |
|---|---|
| ≥1 test carries the AC ID and all such tests passed | `pass` |
| Any test carrying it failed or errored | `fail` |
| Only skipped/disabled tests carry it | `skipped` |
| **No test carries the AC ID at all** | `unchecked` |

A human can record evidence with `apply.py`, but a manual `pass` is **never**
counted in the `ac_proven` headline — that number means "proven by tests" and
must not be movable by hand. Manual claims are reported separately as
`ac_claimed_manual` and shown under the headline. A manual `skipped` ("not
applicable this release") survives a passing or skipped run, but a currently
**failing** test overrides it: a stale waiver must not hide something red.

That last row is the product. It is counted separately and shown as the
headline `ac_proven / ac_total` number.

## What is machine-verified and what is not

Do not read this table as "all six categories are checked". Half of them are a
person's word.

| Category | Source doc | Truth source |
|---|---|---|
| C1 Scenarios | `qa-checklist.md`, `prd.md` §5 | **Tests** — automatic |
| C2 Acceptance criteria | `tech-spec.md` §2 (preferred), else `prd.md` §6 | **Tests** — automatic |
| C3 API endpoints | `api-spec.md` | **Tests** — automatic |
| C4 State transitions | `design.md` §2 `stateDiagram-v2` | Tests when present, otherwise manual evidence |
| C5 Schema / DB verification | `ddl.sql` | **Manual only** — a query result a person ran |
| C6 Open decisions | `design.md` §4 decision log + `> ⚠ Open question:` callouts | **Manual only** — not testable by nature |

The HTML tags every item machine-verified or human-asserted and labels each
category with its truth source, so a reader can tell a test result from a claim
at a glance.

## Seed extraction

`init` reads the design docs and writes a seed JSON. Extract in this order:

| Category | Extract |
|---|---|
| C2 | One item per AC ID. Prefer `tech-spec.md` §2 — its rows already carry the owning component / endpoint / table, so prefill `where` from them. Fall back to `prd.md` §6 when no tech spec exists. |
| C1 | One item per Given-When-Then case in `qa-checklist.md`, plus `prd.md` §5 scenarios. Bind each to the AC IDs it exercises via `ac`. |
| C3 | One item per `method + path` in `api-spec.md`. Use two items (`API-01-BE`, `API-01-FE`) when back end and front end are verified separately. |
| C4 | One item per transition in the `design.md` §2 `stateDiagram-v2`. |
| C5 | One item per table/constraint check derived from `ddl.sql`, with the verification query in `expected`. |
| C6 | One item per unresolved entry in the `design.md` §4 decision log and per `> ⚠ Open question:` callout. |

Every AC ID in `prd.md` §6 must appear as a C2 item. A missing seed item is a
requirement this report will never mention — and worse, it shrinks the
denominator, so 10 of 12 ACs reads as a confident `10/10`. **Always pass
`--prd`** (repeatable; pass `prd.md` and `tech-spec.md` when both exist):
`build_status.py` then extracts the AC IDs itself and exits 3 if the seed misses
any or invents one. Without `--prd` it only warns, and the number is unverified.

### Seed format

Plain JSON — never executable code, never a `.py` module under `claudedocs/`.

```json
{
  "label": "MPT-9125",
  "title": "Order placement",
  "names": {"C2": "Acceptance Criteria"},
  "C2": [
    {"id": "R1-AC1", "title": "an order is created from a valid cart",
     "source": "tech-spec.md §2",
     "where": {"component": "OrderService.place", "endpoint": "POST /api/orders", "table": "order"}}
  ],
  "C3": [
    {"id": "API-01", "title": "POST /api/orders", "ac": ["R1-AC1"],
     "source": "api-spec.md", "steps": ["BE controller mapping", "FE call site"]}
  ],
  "C5": [
    {"id": "SQL-01", "title": "order table unique index", "source": "ddl.sql",
     "expected": "1 index"}
  ]
}
```

Per item only `id` and `title` are required. `ac` defaults to `[id]` when the
id is itself an AC ID. `names` overrides the default English category names —
set them in the team's language, since they appear in the rendered HTML.
`steps` is a manual sub-checklist; it is ignored once a test decides the item.

## Procedure

Every block resolves the skill's own directory first — no hardcoded paths.

### `init <label>`

1. Read `claudedocs/<label>/` and extract the seed per the table above.
2. Write the seed to `claudedocs/<label>/spec-coverage-seed.json`.
3. Build and render:

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/spec-coverage}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/spec-coverage}"

python3 "${SKILL_DIR}/scripts/build_status.py" "$LABEL" \
  --seed "claudedocs/$LABEL/spec-coverage-seed.json" \
  --prd "claudedocs/$LABEL/prd.md" --prd "claudedocs/$LABEL/tech-spec.md"
python3 "${SKILL_DIR}/scripts/render.py" "$LABEL" .
```

Report the AC count and tell the user every AC is `unchecked` until `check`
runs. That is correct, not a bug.

### `check <label>` — run the tests, then collect

**Run the suite in this same invocation.** A JUnit XML left over from an
earlier run is not evidence of the current code; presenting it as current is
exactly the failure `/elian-store:verify-before-claiming` exists to prevent.

Detect the project's command and run it (a failing suite is fine — failures are
data here, so do not stop on a non-zero exit):

| Marker file | Command |
|---|---|
| `gradlew` | `./gradlew test` |
| `pom.xml` | `mvn -q test` |
| `package.json` with a `test` script | `npm test -- --reporter=junit --outputFile=build/test-results/js/TEST-js.xml` (Vitest/Jest equivalent) |
| `pyproject.toml` / `pytest.ini` | `pytest --junitxml=build/test-results/py/TEST-py.xml` |

Then:

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/spec-coverage}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/spec-coverage}"

python3 "${SKILL_DIR}/scripts/collect_tests.py" \
  --out "claudedocs/$LABEL/test-results.json"
python3 "${SKILL_DIR}/scripts/build_status.py" "$LABEL" \
  --seed "claudedocs/$LABEL/spec-coverage-seed.json" \
  --prd "claudedocs/$LABEL/prd.md" --prd "claudedocs/$LABEL/tech-spec.md" \
  --tests "claudedocs/$LABEL/test-results.json"
python3 "${SKILL_DIR}/scripts/render.py" "$LABEL" .
```

`collect_tests.py` searches `**/build/test-results/**/TEST-*.xml` and
`**/target/surefire-reports/TEST-*.xml`; add `--results <glob>` (repeatable)
for any other reporter output path. **It exits non-zero when it finds no XML**
— "the tests were not run" and "no test covers this AC" are different facts,
and conflating them would make the report lie. If it fails, fix the test run;
do not proceed.

### `render <label>`

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/spec-coverage}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/spec-coverage}"

python3 "${SKILL_DIR}/scripts/render.py" "$LABEL" .
```

Status labels default to Korean (`--lang ko`); pass `--lang en` for an English view.
A back-link to `index.html` appears only when the roadmap hub exists in the same
folder.

### `apply <label> <patches.json>`

The manual-evidence path for C5, C6, and any C4 item no test covers. Everything
it writes is recorded as `decided_by: "manual"`.

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/spec-coverage}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/spec-coverage}"

python3 "${SKILL_DIR}/scripts/apply.py" "$LABEL" patches.json .
python3 "${SKILL_DIR}/scripts/render.py" "$LABEL" .
```

```json
{
  "SQL-01": {"status": "pass", "note": "count=1",
             "steps": {"SQL-01-1": {"status": "pass", "evidence": "SHOW INDEX -> 1 row"}}},
  "DEC-02": {"status": "fail", "blocker": "migration not started"}
}
```

A manual `skipped` means "deliberately not applicable" and survives later test
runs. Every other manual status on a test-backed category is replaced the next
time `check` runs — a test result is fresher evidence than an earlier note.

## Status codes

| Code | Meaning |
|---|---|
| `pass` | Proven — every test carrying the ID passed |
| `partial` | Mixed evidence across the bound AC IDs |
| `fail` | A test carrying the ID failed or errored |
| `unchecked` | **No proof** — no test carries the ID |
| `skipped` | Deliberately not applicable, or only skipped tests carry the ID |

## Reporting back

```
{LABEL} spec coverage
  AC proven: 3/12 (tests)
  Leaves: 41 — pass 9 / partial 0 / fail 2 / unchecked 28 / skipped 2
  Decided by: test 18 / manual 7 / undecided 16

  JSON: claudedocs/{LABEL}/spec-coverage.json
  HTML: claudedocs/{LABEL}/spec-coverage.html
```

Always lead with `ac_proven / ac_total`. Never summarise as "N% done" — leaf
progress and proven requirements are different numbers, and only the second one
answers the question.

## Optional: re-render on commit

A `PostToolUse` hook re-renders the HTML after a commit that touched a
`spec-coverage.json`. It is **not** registered by the plugin, because a
`matcher: Bash` hook would fire on every Bash call for every installed user.
Opt in per project in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "bash <path-to-installed-plugin>/skills/spec-coverage/scripts/hook_auto_render.sh"
        }]
      }
    ]
  }
}
```

Resolve `<path-to-installed-plugin>` once with the `SKILL_DIR` snippet above and
write the absolute path into the settings file — `CLAUDE_PLUGIN_ROOT` is not
expanded inside a project's own settings.

The hook only re-renders. It never stages and never commits.

## Self-check

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/spec-coverage}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/spec-coverage}"

python3 "${SKILL_DIR}/scripts/validate.py"
```

Runs the scripts against `fixtures/sample-junit.xml`: the four verdicts, the
zero-test → `unchecked` path, the non-zero exit on a missing XML, and the
manual-`skipped` survival rule.

## Forbidden

- Marking an item `pass` without a passing test that carries its AC ID.
- Editing `spec-coverage.html` by hand — the next render overwrites it.
- Overwriting a user-entered status outside the documented merge rules.
- Treating an empty `collect_tests.py` result as "no coverage" — it exits
  non-zero instead, and that failure must be surfaced, not swallowed.
- Auto-committing from the hook.
- Loading any executable seed file from `claudedocs/` — the seed is JSON.

## Related skills

| Skill | Question it answers |
|---|---|
| `/elian-store:verify-implementation` | Does the code follow the project's own `verify-*` rules? |
| `/elian-store:verify-before-claiming` | Is there fresh evidence for the claim I am about to make? |
| `/elian-store:spec-coverage` | **Is each requirement traceable to a passing test?** |

| Artifact | View |
|---|---|
| `claudedocs/<label>/index.html` (roadmap) | Plan and board — what work exists and how far it got |
| `claudedocs/<label>/spec-coverage.html` | **Proof** — which requirements are actually demonstrated |
