# Perspective catalog

The questions each reviewer asks, the red flags it hunts for, and when it matters
most. The orchestrator gives every reviewer the shared packet (stated intent +
diff + scope map) and asks for structured findings. Out-of-scope reviewers should
recognize they have nothing to add and return `NO FINDINGS` fast rather than
inventing weak ones.

## Table of contents

- [How the layers differ](#how-the-layers-differ)
- [Layer 1 — Functional specialists (always run)](#layer-1--functional-specialists-always-run)
- [Layer 2 — Scope-triggered specialists](#layer-2--scope-triggered-specialists)
- [Layer 3 — Persona judges](#layer-3--persona-judges)
- [Finding shape every reviewer returns](#finding-shape-every-reviewer-returns)

## How the layers differ

Two kinds of reviewer, on purpose:

- **Specialists (Layers 1-2)** run a grounded checklist over the diff. They are
  exhaustive within a domain: a security specialist will walk OWASP whether or not
  the change "feels" security-relevant. Their value is coverage — they do not get
  bored or skip the boring path.
- **Personas (Layer 3)** bring a point of view. They are not trying to be
  complete; they ask the one question their philosophy makes them ask. Their value
  is judgment — they catch the design smell or the operational trap a checklist
  never lists. Keep their voice; do not flatten them into the specialist template.

Breadth (specialists) + judgment (personas) is why the panel beats one reviewer.

## Layer 1 — Functional specialists (always run)

### Correctness & regression — `engineering-reviewer` (correctness lens)
- **Asks:** How does this fail in production? What input was not considered?
- **Red flags:** unhandled null/empty/zero, off-by-one, error paths that swallow
  failures, races on shared state, conditional logic that silently returns the
  wrong result, removed validation, changed default that flips behavior.
- **Matters most:** state transitions, money/auth/permission logic, concurrency,
  anything with an early `return`/`continue` that skips later checks.

### Security & privacy — `engineering-reviewer` (security lens)
- **Asks:** Can input reach somewhere dangerous? Is authority checked? Are secrets
  and PII handled?
- **Red flags:** SQL/command/template injection, missing authorization (IDOR),
  string-interpolated queries, secrets in code/logs, unvalidated external input,
  broad CORS, LLM output written to a trust-sensitive sink without validation,
  tenant isolation gaps.
- **Matters most:** new endpoints, query construction, auth flows, file/HTTP I/O,
  anything that consumes user or model output.

### Performance & scale — `engineering-reviewer` (performance lens)
- **Asks:** What happens at 100x rows / requests / payload size?
- **Red flags:** N+1 queries, queries inside loops, unbounded result sets,
  missing pagination, sync work on a hot path, no caching where it is cheap,
  large allocations, chatty network calls.
- **Matters most:** list/search endpoints, loops over collections, new DB access,
  serialization of large objects.

### Architecture & design — `engineering-reviewer` (architecture lens)
- **Asks:** Does this change belong here? What did it couple that should be apart?
- **Red flags:** business logic in the controller/view, a module reaching across a
  boundary, a new dependency pointing the wrong way, leaked abstraction, a
  decision that deserves an ADR made silently.
- **Matters most:** new modules, cross-service calls, shared utilities, anything
  that changes who-depends-on-whom.

### Maintainability — `engineering-reviewer` (same dispatch as Tests below; personas Fowler/Martin add the judgment layer)
- **Asks:** How expensive is the next change to this code?
- **Red flags:** duplication, dead code, names that lie, functions doing several
  jobs, comments that restate the code, magic numbers, premature abstraction.
- **Matters most:** code other people will touch, hot files, anything copy-pasted.

### Tests & verification — `engineering-reviewer` (tests lens)
- **Asks:** Would a test catch the next break? Are the new paths covered?
- **Red flags:** new behavior with no test, only happy-path tests, tests that
  assert nothing meaningful, mocked-away integration, edge/error paths untested,
  flaky timing assumptions, deleted tests.
- **Matters most:** bug fixes (needs a regression test), new branches, error
  handling, boundary values.

### Requirements fit & scope — `engineering-reviewer` (requirements lens)
- **Asks:** Did the diff do what the PR/issue said — no more, no less?
- **Red flags:** a stated requirement with no corresponding change, "while I was in
  there" edits unrelated to intent, partial implementation, a feature half-built
  behind a flag with no follow-up.
- **Matters most:** every PR with a linked issue or a written description. Build the
  requirement-coverage view here.

## Layer 2 — Scope-triggered specialists

Run when the diff touches the area; otherwise return `NO FINDINGS` quickly.

### Frontend / UX — `engineering-reviewer` (frontend/UX lens)
- **Trigger:** component, template, style, or client-state files.
- **Asks:** Does every state render? Is the interaction accessible?
- **Red flags:** missing loading/error/empty states, unhandled rejected promises,
  layout shift, no keyboard path, missing labels, hardcoded copy that should be
  i18n, rapid-click / double-submit races.

### Backend / API layering — `engineering-reviewer` (backend layering lens)
- **Trigger:** service, controller, repository, or handler files.
- **Asks:** Is the layering clean and the transaction boundary right?
- **Red flags:** repository logic in the controller, transaction spanning a network
  call, inconsistent error contract, business rules in the persistence layer.

### Data & migrations — `engineering-reviewer` (data/migrations lens)
- **Trigger:** migration, schema, DDL, or model files.
- **Asks:** Is this migration safe to run against production data?
- **Red flags:** non-idempotent migration, no rollback, long lock on a large table,
  backfill without batching, nullable/notnull change without a default, data loss
  on down-migration, new column read by code before the migration runs.

### API contract — `engineering-reviewer` (API contract lens)
- **Trigger:** public DTO, endpoint signature, event payload, or shared type.
- **Asks:** Will this break an existing consumer?
- **Red flags:** removed/renamed field, changed type or nullability, new required
  request field, changed status code or error shape, version not bumped.

### DevOps / deploy / ops — `engineering-reviewer` (devops lens)
- **Trigger:** CI, Dockerfile, IaC, config, or secret-handling files.
- **Asks:** Is this safe to deploy and to roll back?
- **Red flags:** secret in config, no rollback path, env-specific value hardcoded,
  pipeline step that can't fail safely, missing health/observability for a new
  service, ordering dependency between deploy and migration.

### Docs — `engineering-reviewer` (docs lens)
- **Trigger:** behavior change with public docs, README, or help text.
- **Asks:** Does the documentation still match the code?
- **Red flags:** changed flag/endpoint/behavior with stale docs, new feature with
  no docs, example that no longer runs.

## Layer 3 — Persona judges

Default all six (`--personas all`). Preserve each voice; do not template them.

The canonical persona definitions live in `../persona-review/references/personas/*.md` (beck, dean, evans, fowler, martin, daniel). The one-line lenses below are a quick index for dispatch — when a persona's voice or rules change, update the `persona-review` file as the source of truth and keep this index in sync rather than letting the two drift.

### Beck — `persona-beck-reviewer`
TDD/XP. Was this driven by a test? Is it the simplest thing that works? What was
built that nobody needs yet (YAGNI)? Is feedback fast?

### Dean — `persona-dean-reviewer`
Distributed systems. Where is the tail latency, the SPOF, the hot key? Is retry
idempotent with a budget and jitter? Where is backpressure? Are performance claims
measured or asserted?

### Evans — `persona-evans-reviewer`
DDD. Does the code speak the domain's language? Are aggregate boundaries and
invariants respected? Is there a model insight being missed, or domain logic
leaking into infrastructure?

### Fowler — `persona-fowler-reviewer`
Refactoring. What are the code smells? Where are module boundaries blurred? Is this
an evolutionary step or an accreting mess? What small refactor would unlock the
change?

### Martin — `persona-martin-reviewer`
Clean Code. Single responsibility, SOLID, naming, small functions, dependency
direction. Where does a function do more than its name says?

### Daniel — `persona-daniel-reviewer`
Operational reliability. Do we understand the mechanism, or are we cargo-culting a
policy? What is the failure mode? What should be automated? What breaks at 3am and
who gets paged?

## Finding shape every reviewer returns

Ask each subagent to return findings the orchestrator can merge. One object per
finding, or the literal `NO FINDINGS`:

```json
{"severity":"CRITICAL|HIGH|MEDIUM|LOW|INFO","confidence":1-10,"path":"file","line":42,"perspective":"security","problem":"one line","evidence":"the line/contract that proves it","suggestion":"direction, not a full patch"}
```

Rules given to every reviewer:
- Read-only. No edits, no file creation, no destructive commands.
- Cite `file:line` or state the evidence gap. No vibe findings.
- Quote the motivating line; if you cannot, lower confidence.
- Stay in your lane — another lane will cover what you skip.
