# /design-ui - UI/UX design artifacts before implementation (Codex Port)

Install path: `~/.codex/prompts/design-ui.md`.

Invocation:

```text
/design-ui <feature-name> [--out <dir>] [--skip-gate] [--from-brief <path>] [--refs <url,url,...>]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/design-ui/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

Read-only contract: do not edit files, create files, stage, commit, push, or run destructive commands. Output Markdown or HTML artifacts in the response when requested. If implementation is needed, hand off to frontend implementation and stop.

## Purpose

Design a new screen or product flow at page level. Start with a signed-off problem brief, gather references, create a gray wireframe, pause at a wireframe gate, then produce a clickable visual prototype and DESIGN.md handoff.

This prompt designs artifacts. It does not implement Vue, React, or production UI code.

## Common Contract

1. Do not skip the brief sign-off unless the user explicitly allows it.
2. Wireframe before visual. No colors, fonts, or icons before the gate.
3. Keep page IDs stable across flow, wireframe, and visual artifacts.
4. Preserve loading, empty, and error states in the visual prototype.
5. End with one next question, next action, or handoff payload.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `<feature-name>` | Feature or flow name to design | required |
| `--out <dir>` | Output directory | `claudedocs/design/<feature>/` |
| `--skip-gate` | Skip the wireframe approval gate | off |
| `--from-brief <path>` | Use an existing brief or PRD as Phase 1 input | none |
| `--refs <urls>` | Comma-separated reference URLs for Phase 2 | none |

`$ARGUMENTS` always wins over any local default.

## Workflow

```text
Phase 1: Interview
Phase 2: Reference
Phase 3: Wireframe
Gate: Wireframe approval
Phase 4: Visual
Phase 5: Deliver
```

### Phase 1: Interview

Iteratively gather a brief until it is signed off. Ask one or two questions at a time instead of running a bulk questionnaire. Capture problem, primary user, core tasks, use context, success state, guardrails, and page split.

If the page split is unclear, infer a conservative proposal and confirm it before moving on.

Output `brief.md` using the brief template pattern from the Claude skill.

### Phase 2: Reference

Use two or three analogous product references. For each reference, capture:

- Steal
- Adapt
- Reject
- Why this ref

If the user gives no references, propose candidates from the domain and let the user choose.

### Phase 3: Wireframe

Create a sitemap and a multi-page gray wireframe. Every page needs entry, exit, return path, above-the-fold region, and page-level data dependencies.

Every wireframe box should include:

- Order
- Label
- Intent
- Why here

Show default, empty, loading, and error variants where needed.

### Gate: Wireframe approval

Unless `--skip-gate` is set, ask whether the wireframe can move to visual design. The user can proceed, revise a part, or return to interview/references.

### Phase 4: Visual

Create a clickable prototype. Preserve page order, reading order, and intent. Use an existing design system when present. If no design system exists, define reasonable tokens rather than defaulting to generic direction.

The prototype must include:

- touch-friendly targets
- minimum readable typography
- contrast and accessibility baselines
- working toggles, filters, counts, and cross-page state when relevant

### Phase 5: Deliver

Emit the design artifact set and a DESIGN.md handoff. If the user approved opening the visual file, the prompt can instruct them to open it; otherwise keep the output text-only.

## Output Shapes

### Default output

```text
Design summary
- Feature: <feature-name>
- Brief: <signed-off / pending>
- Gate: <approved / pending>

Key decisions
- <decision 1>
- <decision 2>

Open questions
- <unresolved item>

Next
- <next question or next action>
```

### Deliverable set

```text
<out>/
  brief.md
  references.md
  flow.html
  wireframe.html
  visual.html
  DESIGN.md
```

## Forbidden

- Proceeding past Phase 1 without a signed-off brief unless the user explicitly skips it.
- Treating Phase 1 as a bulk questionnaire.
- Adding visual styling in the wireframe phase.
- Dropping loading, empty, or error states.
- Forcing all tasks onto one page without a reason.
- Writing files or modifying the repository.

## Pre-Output Self-Check

- [ ] Brief sign-off requirement is satisfied or explicitly skipped.
- [ ] References include Steal, Adapt, and Reject if references are used.
- [ ] Wireframe gate is explicit.
- [ ] Visual prototype preserves page order and intent.
- [ ] The output ends with one next question or next action.
