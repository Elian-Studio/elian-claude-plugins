# /decision-dashboard - Decision dashboard assembly (Codex Port)

Install path: `~/.codex/prompts/decision-dashboard.md`.

Invocation:

```text
/decision-dashboard [issue-id] [--mode generate|finalize]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/decision-dashboard/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

Read-only contract: do not edit files, create files, stage, commit, push, or run destructive commands. Output Markdown, JSON, or HTML artifact content only. If the user needs a durable artifact, emit the render-ready JSON and the derived HTML in the response and stop. If the request really needs repo writes or file cleanup, hand off to a file-writing workflow instead of pretending to do it here.

## Purpose

Turn 3 or more blocking decisions into a printable dashboard and a downstream JSON decision record.

The dashboard should let a decision-maker choose quickly, preserve the rationale, and make the result usable by downstream implementation or planning work.

This prompt owns decision shaping, option wording, priority grouping, and final choice capture. It does not implement code.

## Common Contract

1. Use this only when 3+ decisions are blocking progress or the explanation would be too long to keep in chat.
2. Keep the output artifact-first: normalize the decision set into JSON before presenting HTML or a final summary.
3. Rewrite implementation language into product language for card bodies.
4. Require a memo for `Other` whenever a final choice is exported with that option selected.
5. End with one next question, next action, or handoff payload.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `[issue-id]` | Issue key, branch-derived slug, or `decision` fallback | current branch slug or `decision` |
| `--mode generate\|finalize` | Build a dashboard or merge user choices into the final record | `generate` |

`$ARGUMENTS` always wins over any local default.

## Workflow

```text
Phase 1: Decision recognition
Phase 2: Card shaping
Phase 3: JSON assembly
Phase 4: HTML rendering contract
Gate: content and language validation
Phase 5: Finalization or handoff
```

### Phase 1: Decision recognition

Identify the pending decisions from the current context. If there are fewer than 3, do not force a dashboard; ask directly in chat or ask for more decisions.

### Phase 2: Card shaping

For each decision:

- Write one judgment question that ends in `?`.
- Phrase the title and body from a product perspective, not implementation jargon.
- Draft outcome-focused options A/B/C.
- Add `Other` only when it is genuinely needed.

If the user cannot decide the memo text for `Other`, stop and ask for it before finalizing.

### Phase 3: JSON assembly

Build the dashboard data first. Preserve:

- issue metadata
- priority grouping
- card order
- option keys
- recommendation badges
- memo fields

The JSON should be deterministic enough to feed a renderer or a downstream export step.

### Phase 4: HTML rendering contract

Treat HTML as a rendering of the JSON, not a separate design exercise.

If the response includes HTML, keep it printable, compact, and readable:

- first card open by default
- no internal identifiers in card body
- clear decision question and option labels
- `Other` memo visible when selected

### Gate: content and language validation

Before exporting, check:

1. There are 3 or more cards.
2. Every card has one judgment question.
3. Every card has at least 3 concrete options.
4. Card body text stays in product language.
5. `Other` is not exported without a memo.

If a gate fails, stop and ask the smallest useful question.

## Modes

### Mode 1: `generate`

Use when the user wants the initial dashboard artifact.

Output:

- a dashboard-ready JSON record
- a rendered HTML representation or render-ready HTML block
- a short summary of the decisions and what remains open

Do not pretend the response wrote files.

### Mode 2: `finalize`

Use when the user has already chosen options and wants the record closed out.

Merge the user choices into the final JSON view:

- keep the original decision text
- preserve the selected options
- preserve rejected options when useful for auditability
- retain memo text for `Other`

If the user choices are incomplete, ask the one missing question and stop.

## Output Shapes

### Default output

```text
Decision summary
- Issue: <issue-id>
- Mode: <generate|finalize>
- Recommendation: <what should happen next>

Key decisions
- <decision 1>
- <decision 2>

Open questions
- <unresolved item>

Next
- <next question or next action>
```

### Generate output

## Dashboard JSON

```json
<render-ready JSON>
```

## Dashboard HTML

```html
<render-ready HTML>
```

### Finalize output

## Final JSON

```json
<final decision JSON>
```

## Final summary

- <what changed>
- <what still needs attention, if anything>

## Forbidden

- Editing files, writing files, staging, committing, or pushing.
- Running destructive cleanup or pretending to clean up disposable artifacts.
- Using implementation identifiers in card body text outside the technical rationale area.
- Exporting a final `Other` choice without a memo.
- Turning a 1-2 decision chat into a dashboard.
- Replacing the JSON-first contract with hand-written HTML-only output.

## Pre-Output Self-Check

- [ ] There are at least 3 blocking decisions.
- [ ] The card text is written for a decision-maker, not an engineer.
- [ ] The JSON is assembled before the HTML view.
- [ ] The output keeps `Other` memo handling explicit.
- [ ] The output ends with one next question or next action.
