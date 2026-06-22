---
name: persona-review
description: "When a user wants a plan, design, document, PR description, code, or idea reviewed through expert personas, analyze the target and auto-select the matching read-only persona reviewer subagents (frontend, UX, accessibility, API, domain, scale, code, business, marketing, operations), dispatch them in parallel, and return each persona's native judgment with a short lead synthesis — no shared scorecard or fixed template. Falls back to Daniel when no axis clearly matches; honors an explicit --persona override."
when_to_use: "Use before locking a non-trivial decision, when a target spans several expertise axes, or when the user names a persona lens. Auto-selection picks reviewers from the target's signals; override with --persona <name>|all|auto|comma-list|<path>. Trigger phrases: 'persona review', 'review through a persona', 'which experts should review this', 'frontend/UX/accessibility/API/domain/scale review', '/persona-review', '--depth interview'."
argument-hint: "<target-path-or-text> [--persona auto|daniel|evans|dean|martin|beck|fowler|abramov|evanyou|norman|rams|dunford|christensen|watson|fielding|all|comma-list|<path>] [--depth quick|deep|interview]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git diff*), Bash(git log*), Bash(git status*), Agent, AskUserQuestion
---

# /persona-review

Route the user's plan, document, PR description, design, code diff, or idea to read-only persona reviewer subagents. The goal is not to fill a scorecard. The goal is to expose weak assumptions, hidden costs, model problems, operational risks, and the next useful question through each selected persona's judgment style.

By default this skill **auto-selects** the personas that match the target. It analyzes the target, detects which expertise axes it touches, and dispatches the matching reviewers in parallel (up to three), then adds one lead synthesis. A single-axis target runs one persona; a multi-axis target runs several; a target with no clear axis falls back to `daniel`. An explicit `--persona` always overrides auto-selection.

The main skill is a lead/router, not the reviewer. Built-in persona reviews must be performed by the matching `persona-<name>-reviewer` subagent (the full map is in the [Subagent Execution Contract](#subagent-execution-contract)), or by `persona-custom-reviewer` for a custom file.

If the user intent is unclear, do not critique prematurely. Ask one clarifying question before dispatch.

Core contract:

- Persona-native free-form review. Do not force a shared five-block template, shared table, or shared scorecard.
- `Pressure Questions` are an internal lens. Do not expand every question into rows or scores.
- Reviews are read-only. Neither the main skill nor subagents edit files, create files, stage, commit, or push.
- Built-in persona requests must go through the matching subagent.
- Do not guess. If evidence is missing, say what needs confirmation.
- End with one useful next question, next action, or handoff payload.

## Standing Rules

- The main skill owns target collection, thin-input judgment, persona auto-selection, subagent dispatch, and aggregation.
- Preserve subagent output as much as possible. Add lead synthesis only for multi-persona runs.
- `$ARGUMENTS` overrides environment variables and defaults.
- When no `--persona` is given, auto-selection runs by default (see Phase 0). `--persona auto` requests it explicitly.
- `${PERSONA_REVIEW_DEFAULT}` can pin a fixed default persona, replacing auto-selection.
- `${PERSONA_REVIEW_DEPTH}` can set the default depth.
- Every mode is read-only. If implementation is needed, emit a handoff payload only.

## Modes

| Mode | What it does | Use when |
|---|---|---|
| `quick` (default) | Runs the selected or auto-selected persona subagent(s) once each | Fast review of one idea, file, document, or diff |
| `deep` | Gives the subagent(s) more evidence or allows extra read-only exploration | Architecture, PR, domain, or operational changes |
| `interview` | Runs review, asks the single uncertainty that changes the conclusion, and can repeat up to three rounds | The answer depends on goal, constraint, or ownership clarification |

`--persona` and `--depth` are independent. `--persona evans --depth deep` runs an Evans-style review with deeper evidence. Depth controls evidence and rounds; persona selection (manual or auto) controls who reviews.

## Where this fits in the workflow

```text
brainstorm -> persona-review lead -> persona reviewer subagent(s) -> lead aggregation -> decision-dashboard
                                                            \-> handoff payload -> improve / implement / fix
```

- **Upstream**: `/brainstorm`, a draft, a design, a PR description, a diff, or a short idea.
- **This skill**: choose persona, judge input density, ask if needed, dispatch subagent, relay or aggregate results.
- **Downstream**: use `/decision-dashboard` to lock decisions or `/improve`, `/implement`, `/fix` to execute changes.

## Persona library

Auto-selection (Phase 0) chooses personas from the target by default. Use `--persona` to pin a specific lens, set, or `all`. A persona changes the judgment lens, not just the output format.

| Persona | subagent_type | Pressure axis | Strongest targets |
|---|---|---|---|
| [`daniel`](references/personas/daniel.md) (fallback) | `persona-daniel-reviewer` | Operability, mechanisms, axiom vs policy, automation, failure modes | Operational changes, infra, hooks, retries, everyday code |
| [`evans`](references/personas/evans.md) | `persona-evans-reviewer` | DDD, bounded context, ubiquitous language, aggregate, ACL | Domain models, architecture boundaries, new service seams |
| [`dean`](references/personas/dean.md) | `persona-dean-reviewer` | Distributed systems, scale, tail latency, SPOF, hot keys, backpressure | High-traffic flows, queues, caches, DB scaling |
| [`martin`](references/personas/martin.md) | `persona-martin-reviewer` | Clean Code, SOLID, naming, SRP, testability | Function/class design, OO structure, code quality |
| [`beck`](references/personas/beck.md) | `persona-beck-reviewer` | TDD, simple design, fast feedback, small steps, YAGNI | Test strategy, incremental delivery, refactoring safety |
| [`fowler`](references/personas/fowler.md) | `persona-fowler-reviewer` | Refactoring, structural (module-level) code smells, module boundaries, enterprise patterns, evolution | Architecture evolution, large refactors, migrations |
| [`abramov`](references/personas/abramov.md) | `persona-abramov-reviewer` | Frontend state ownership, unidirectional data flow, effects, async UI states | React/state-heavy UI, data-flow design |
| [`evanyou`](references/personas/evanyou.md) | `persona-evanyou-reviewer` | Reactivity boundary, computed vs watch, component-API ergonomics | Vue/reactive UI, component contracts |
| [`norman`](references/personas/norman.md) | `persona-norman-reviewer` | Mental-model match, discoverability, feedback, error recovery | UX flows, usability, interaction design |
| [`rams`](references/personas/rams.md) | `persona-rams-reviewer` | Necessity, visual hierarchy, token consistency, honest detail | UI visual design, design systems, component states |
| [`dunford`](references/personas/dunford.md) | `persona-dunford-reviewer` | Positioning, competitive alternative, value translation, best-fit customer | Marketing copy, landing pages, messaging |
| [`christensen`](references/personas/christensen.md) | `persona-christensen-reviewer` | Jobs-to-be-done, circumstance, disruption type, business-model fit | Product/strategy decisions, business model |
| [`watson`](references/personas/watson.md) | `persona-watson-reviewer` | Semantic HTML, keyboard, name/role/value, real AT verification | Accessibility, a11y, ARIA, inclusive design |
| [`fielding`](references/personas/fielding.md) | `persona-fielding-reviewer` | Resource design, HTTP semantics, statelessness, idempotency, evolution | API/REST design, HTTP contracts |
| custom path | `persona-custom-reviewer` | The provided custom persona file | User-defined lens |

Recommended selection (auto-selection applies these automatically; this table is for manual `--persona` choices):

| Situation | Recommended persona | Reason |
|---|---|---|
| Operational changes, notifications, retries, hooks | `daniel` | Operability and automation lens |
| Domain model, aggregate, service boundary | `evans` | Domain language and invariant pressure |
| 100x traffic, cache, queue, DB design, latency risk | `dean` | Distributed-systems and tail-latency lens |
| Function design, refactor, naming, SOLID | `martin` | Code structure and testability lens |
| Test strategy, TDD, small increments | `beck` | Test-first and simple-design lens |
| Large refactor, module boundaries, architecture evolution | `fowler` | Refactoring-sequence and evolution lens |
| React or state-heavy frontend, data flow | `abramov` | State-ownership and data-flow lens |
| Vue or reactive component design | `evanyou` | Reactivity-boundary and component-API lens |
| Usability, user flow, mental model | `norman` | Human-centered usability lens |
| Visual design, hierarchy, design tokens | `rams` | Restraint and visual-consistency lens |
| Positioning, landing page, marketing message | `dunford` | Positioning and value-translation lens |
| Product/business model or strategy decision | `christensen` | Jobs-to-be-done and disruption lens |
| Accessibility, keyboard, screen reader, ARIA | `watson` | Inclusive-design and AT lens |
| API/REST design, HTTP contract | `fielding` | Uniform-interface and evolution lens |
| Target spans several of the above | auto-selection or a comma-list | One persona per axis, run in parallel |

### Custom personas

A custom persona should preferably use this structure:

```markdown
# Persona: <name>

## Voice
## Hard Rules
## Decision Heuristics
## Priorities
## Forbidden
## Pressure Questions
## Blind Spots
```

`Pressure Questions` are prompts to think with, not a checklist to score. A custom persona may have its own output structure. The main skill reads the custom file and includes it in the `persona-custom-reviewer` prompt.

## What's automated vs what needs your taste

| Automated | User decides |
|---|---|
| Target file, text, or diff collection | What should be reviewed |
| Thin-input detection | Answer to the intent question |
| Auto-selection of matching personas (up to 3, `daniel` fallback) | A pinned persona, `all`, comma-list, or custom path |
| Built-in/custom persona dispatch | Whether to accept or challenge the persona judgment |
| Single-result relay or multi-persona aggregation | Whether to act on the result |
| Handoff payload when needed | Whether to run an implementation skill |

## Common Review Contract

This is the only shared contract. The rest belongs to the subagent's persona style.

1. **Lead with the useful judgment.** If the persona works better through a model, diagram, or number first, that is allowed.
2. **Use the persona's native shape.** Daniel focuses on operational mechanisms; Evans on model and language; Dean on bottlenecks and fault models; Martin on code smell, function structure, and tests.
3. **No scorecard.** Do not expand all `Pressure Questions` into rows, grades, or scores. Blend only useful questions into the review.
4. **Evidence over vibe.** Cite files, diffs, text, or explicit absence of evidence.
5. **Use tables only when they clarify judgment.** A table is optional, not a required format.
6. **End with one next move.** Use one next question, decision, strengthening request, or handoff payload.

## Subagent Execution Contract

The main skill is the lead/router. Built-in persona requests must dispatch to the matching subagent.

| persona arg | subagent_type |
|---|---|
| omitted or `auto` | Auto-select from the target's signals (Phase 0); dispatch up to three in parallel; `daniel` fallback |
| `daniel` | `persona-daniel-reviewer` |
| `evans` | `persona-evans-reviewer` |
| `dean` | `persona-dean-reviewer` |
| `martin` | `persona-martin-reviewer` |
| `beck` | `persona-beck-reviewer` |
| `fowler` | `persona-fowler-reviewer` |
| `abramov` | `persona-abramov-reviewer` |
| `evanyou` | `persona-evanyou-reviewer` |
| `norman` | `persona-norman-reviewer` |
| `rams` | `persona-rams-reviewer` |
| `dunford` | `persona-dunford-reviewer` |
| `christensen` | `persona-christensen-reviewer` |
| `watson` | `persona-watson-reviewer` |
| `fielding` | `persona-fielding-reviewer` |
| `all` | Run all built-in reviewers in parallel |
| comma-list such as `abramov,watson` | Run only the selected reviewers in parallel |
| custom file path | Run `persona-custom-reviewer` with the custom persona body |

### Agent prompt payload

Each subagent prompt must include:

```markdown
[ROLE]
Run a read-only persona review for /persona-review.

[USER INTENT]
<review intent, or "not specified">

[TARGET]
<file path, diff summary, or free text>

[DEPTH]
quick | deep | interview

[EVIDENCE]
<text, diff, file paths, or evidence already read by the main skill>

[CONSTRAINTS]
- Do not edit files.
- Do not create files.
- Do not run destructive commands.
- Do not output a scorecard or fixed five-block template.
- End with one next question/action/handoff.
```

### Result handling

- **single persona**: relay the subagent result. Do not rewrite it except for obvious duplicate headings.
- **multiple personas / `all`**: preserve each persona result separately and add only one `## Lead synthesis` section. Synthesis covers conflicts, common risks, and one next decision.
- **interview**: choose the one uncertainty that changes the conclusion, ask the user, then rerun the same subagent set after the answer.
- **custom persona**: if the custom file is missing or too thin, say so and ask whether to fall back to `daniel`.

## Workflow

```text
Phase 0: Persona selection or recommendation
Phase 1: Target collection and input-density judgment
Phase 2: Persona to subagent dispatch decision
Phase 3: Subagent prompt construction and Agent execution
Phase 4: Subagent result relay or aggregation
Phase 4.5: Interview convergence loop (--depth interview)
Phase 5: Handoff or close
```

### Procedure

1. Parse target, `--persona`, and `--depth` from `$ARGUMENTS`.
2. If persona is missing or `auto`, run auto-selection (Phase 0). `${PERSONA_REVIEW_DEFAULT}`, if set, pins a fixed persona instead.
3. If depth is missing, use `${PERSONA_REVIEW_DEPTH}` or `quick`.
4. Read the target and judge input density.
5. Map the chosen persona(s) to `subagent_type`(s).
6. Build a read-only evidence payload and run `Agent` for each persona (in parallel when more than one).
7. Relay a single persona result; add lead synthesis when more than one persona ran.
8. In `interview` mode, ask one conclusion-changing question and stop.

### Phase 0: Persona selection (auto by default)

When the user pins `--persona <name>`, `all`, a comma-list, or a custom path, honor it directly. Otherwise — no `--persona`, or `--persona auto` — **auto-select**: read the target, detect which expertise axes it touches, and dispatch the matching personas. Do not default to a single persona before looking at the target.

**Signal map** — match the target's path, content, and the user's intent against these axes:

| Target signal | Auto-selected persona |
|---|---|
| Operations, infra, hooks, retries, deployment, incident, runbook | `daniel` |
| Domain model, aggregate, entity, invariant, bounded context, ubiquitous language | `evans` |
| Queue, scheduler, cache, sharding, replication, latency, throughput, hot key | `dean` |
| Function/class design, SOLID, naming, function-level code smell, unit-level refactor | `martin` |
| Test strategy, TDD, test-first, small increments, characterization tests | `beck` |
| Module boundaries, structural (module-level) code smells, large refactor, enterprise patterns, architecture evolution, migration | `fowler` |
| React, state management, hooks, frontend data flow, async UI state | `abramov` |
| Vue, reactivity, ref/reactive, computed/watch, SFC, component API | `evanyou` |
| User flow, usability, mental model, discoverability, feedback | `norman` |
| Visual design, spacing, hierarchy, design tokens, component visual states | `rams` |
| Positioning, value proposition, landing page, marketing copy, messaging | `dunford` |
| Business model, product strategy, monetization, market, jobs-to-be-done | `christensen` |
| Accessibility, a11y, ARIA, keyboard, screen reader, WCAG, contrast | `watson` |
| REST, HTTP, endpoint, API contract, status code, resource design | `fielding` |
| No clear signal, or purely ambiguous | `daniel` (fallback) |

**Selection rule:**

- **1 axis matches** → run that one persona.
- **2–3 axes match** → run those personas in parallel and add one `## Lead synthesis`.
- **More than 3 match** → run only the 3 strongest (most central to the target) and note which axes were dropped so the user can re-run with a comma-list.
- **0 axes / ambiguous** → fall back to `daniel`.

Never dispatch more than three personas in auto mode. The user forces the full roster with `--persona all` or a specific set with a comma-list. State the auto-selected personas (and the signals that triggered them) in one line before dispatching.

### Phase 1: Target collection and input-density judgment

| Argument shape | Interpretation |
|---|---|
| File path (`.md`, `.ts`, `.java`, etc.) | Read the file |
| URL or PR/MR reference | Ask before using network-dependent tools |
| Free text | Use the argument itself as the target |
| Empty | Ask whether to review current git diff, a specific file, or text |

Ask before review when input is thin or ambiguous.

- **Thin**: one or two lines, unclear goal or scope.
- **Ambiguous**: document exists but goal or completion criteria are unclear.
- **Sufficient**: goal, scope, constraints, and completion criteria are available.

### Phase 2: Persona to subagent dispatch decision

- Auto (no `--persona` or `--persona auto`): use the Phase 0 selection; map each selected persona to its `subagent_type` and prepare parallel runs when more than one.
- Name arg: choose the matching `subagent_type`.
- `all` or comma-list: prepare parallel read-only subagent runs.
- Path arg: read the custom persona file and choose `persona-custom-reviewer`.
- Missing custom file: ask whether to fall back to `daniel`.

### Phase 3: Subagent prompt construction and Agent execution

The main skill reads only the needed evidence and passes it to `Agent`. Subagents may perform additional read-only exploration when the prompt and depth permit it.

```typescript
Agent({
  subagent_type: 'persona-evans-reviewer',
  prompt: '<payload>'
})
```

### Phase 4: Subagent result relay or aggregation

For multiple personas, preserve persona outputs and add one lead synthesis:

```markdown
## daniel
<persona-daniel-reviewer output>

## dean
<persona-dean-reviewer output>

## Lead synthesis
- Common risk: ...
- Conflict: ...
- Next decision: ...
```

See [references/example-review.md](references/example-review.md) for examples. The example is guidance, not a fixed output template.

### Phase 4.5: Interview convergence loop

`quick` and `deep` stop after one subagent run. `interview` can run up to three rounds.

1. Pick the biggest uncertainty that changes the conclusion.
2. Ask only that question.
3. Rerun the same subagent set after the answer.
4. Prefix each round with `(interview R{n}/3)`.
5. Stop when the conclusion is clear, the user stops, or round 3 is reached.

### Phase 5: Handoff or close

If the review should lead to implementation, emit a handoff payload only. Do not execute `/improve`, `/implement`, or `/fix` from this skill.

```markdown
(handoff -> improve/implement/fix <target>)
- persona: <name>
- judgment: <one-line judgment>
- change intent: <what should change>
- evidence: <key evidence>
- risks to preserve: <risks that must not be lost>
- out of scope: <what not to do now>
```

## Pitfalls

| Pitfall | Avoidance |
|---|---|
| Turning persona review into a scorecard | Use questions as an internal lens and write in the persona's style |
| Making every persona use the same structure | Apply the persona file's Voice and Forbidden sections first |
| Main skill writes the review directly | Built-in personas must run through subagents |
| Rewriting multi-persona output into one voice | Preserve subagent output and add only lead synthesis |
| Defaulting to `daniel` without reading the target | Auto-select from the Phase 0 signal map first; fall back only when no axis matches |
| Auto-selecting too many personas | Cap at the 3 strongest in auto mode; use a comma-list or `all` to go wider |
| Over-critiquing a one-line idea | Ask one intent or success-criteria question first |
| Filling gaps with guesses | Mark the missing evidence and ask the next question |
| Sliding from review into execution | Emit handoff only |

## Forbidden

- Code edits, file creation, staging, commits, or pushes.
- Forcing a common five-block output.
- Outputting score tables, grade tables, or exhaustive checklist rows.
- Mechanically evaluating every `Pressure Questions` item.
- Writing built-in persona reviews directly in the main skill.
- Flattening subagent results into one generic voice.
- Praise, motivational tone, marketing tone, emojis, or apologies.
- Conclusions based on unverified assumptions.
- Automatic external URL fetch.
- More than three interview rounds.
- Executing the handoff payload inside this skill.

## Validation

```bash
python3 plugins/elian-store/skills/persona-review/scripts/validate_skill.py
python3 plugins/elian-store/skills/persona-review/scripts/validate_skill.py --json
```

The validator checks frontmatter, read-only guardrails, Agent tool use, persona reviewer agents, persona references, example links, absence of fixed five-block or scorecard requirements, persona override support, and interview mode.

## Pre-flight

- [ ] Target and persona are clear.
- [ ] Thin input was clarified before review.
- [ ] Built-in persona was dispatched to its matching subagent.
- [ ] Subagent prompt includes user intent, target, depth, evidence, and constraints.
- [ ] No scorecard or fixed shared template was produced.
- [ ] Confirmed evidence and missing evidence are separated.
- [ ] The response ends with one next question or next action.
