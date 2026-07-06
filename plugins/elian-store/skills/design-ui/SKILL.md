---
name: design-ui
description: When a user needs UI/UX design for a new screen or flow, drive Interview -> Reference -> Wireframe -> Gate -> Visual -> Deliver before implementation.
when_to_use: "Use for new page/flow design, feature-level UX shaping, wireframes, visual HTML, and DESIGN.md handoff. Trigger phrases: 'create a wireframe', 'design this UI flow', 'prepare a visual mock', 'improve this UX', 'make the experience better', '/design-ui'. If the requirement is fuzzy, run /brainstorm first; if only one existing component needs minor styling, direct implementation is faster."
argument-hint: "<feature-name> [--out <dir>] [--skip-gate] [--from-brief <path>] [--refs <url,url,...>]"
allowed-tools: Read, Write, Edit, Bash(mkdir *), Bash(ls *), Bash(open *), Glob, Grep, AskUserQuestion, WebFetch
disable-model-invocation: false
---

# /design-ui

Design a new screen or product flow at page level. Start with a signed-off problem brief, gather references, create a gray wireframe, pause at a wireframe gate, then produce a clickable visual prototype and DESIGN.md handoff.

This skill designs artifacts. It does not implement Vue, React, or production UI code.

## Where this fits in the workflow

```text
/brainstorm (optional when requirements are fuzzy)
  -> /design-ui
     Phase 1: Interview
     Phase 2: Reference
     Phase 3: Wireframe
     Gate: wireframe approval
     Phase 4: Visual
     Phase 5: Deliver
  -> frontend implementation
```

- **Upstream**: user request, issue body, PRD, or brainstorm output.
- **This skill**: deterministic UX pipeline from brief to prototype.
- **Downstream**: hand off HTML artifacts and DESIGN.md to implementation.

## Parameters

`$ARGUMENTS` follows the frontmatter argument hint. Precedence: `$ARGUMENTS` > environment variables > skill defaults.

| Option | Meaning | Default |
|---|---|---|
| `<feature-name>` | Feature or flow name to design | required |
| `--out <dir>` | Output directory | `claudedocs/design/<feature>/` |
| `--skip-gate` | Skip the Phase 3 to Phase 4 approval gate | off |
| `--from-brief <path>` | Use an existing brief or PRD as Phase 1 input | none |
| `--refs <urls>` | Comma-separated reference URLs for Phase 2 | none |

Environment overrides:

| Env var | Meaning | Default |
|---|---|---|
| `${DESIGN_UI_OUT}` | Output directory when `--out` is omitted | `claudedocs/design/<feature>/` |
| `${CLAUDE_PLUGIN_ROOT}` | Plugin root (Claude Code only) | set by Claude Code; unset on Codex |
| `${CLAUDE_SKILL_DIR}` | This skill's directory (Claude Code only) | set by Claude Code; on Codex use `${CODEX_HOME:-$HOME/.codex}/skills/design-ui` |

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

Interview iteratively until the brief is clear and the user signs it off. Do not ask a bulk four-question questionnaire. Ask one or two questions, update the brief, show the current brief, and continue until the user says it is correct.

Ask about the most uncertain slot first:

| Slot | What to capture |
|---|---|
| Problem | What the user currently cannot do |
| Primary user | Role, context, device, and frequency |
| Core tasks | One to three actions the flow must complete |
| Use context | When and why the user arrives |
| Success state | What must be true after the flow works |
| Guardrails | Product, technical, policy, or UX constraints |
| Page split | One to five pages/views and each page's purpose |

If the user does not know the page split, infer a conservative proposal and confirm it:

- One simple lookup or input task: one page.
- Review -> confirm: main page plus confirmation page.
- Batch action: main page plus batch confirmation page.
- Shareable result or report: add a result summary page.

Output `brief.md` using [templates/brief.md](templates/brief.md). Do not enter Phase 2 before the brief is signed off unless the user explicitly asks to skip.

### Phase 2: Reference

Use two or three competitor or analogous product references. The point is not copying; it is choosing and rejecting proven UX patterns consciously.

If `--refs` is provided, analyze those URLs. If not, ask for two or three examples. If the user has none, propose candidates from the domain and let the user choose.

For each reference, capture only:

| Slot | Meaning |
|---|---|
| Steal | One specific pattern to reuse |
| Adapt | One pattern to reshape for this product |
| Reject | One pattern to reject and why |
| Why this ref | One sentence explaining fit |

Output `references.md` using [templates/references.md](templates/references.md). If the user explicitly says to skip references, record that decision and state that Phase 3 will rely on general UX heuristics.

### Phase 3: Wireframe

Create both a sitemap and a multi-page wireframe.

1. Build `flow.html` from [templates/flow.html](templates/flow.html). Show page boxes and transition arrows. Every arrow must name the trigger and destination page.
2. Build `wireframe.html` from [templates/wireframe.html](templates/wireframe.html). Stack each page as `<section class="wf-page" id="page-N">`.
3. Keep page slugs stable across all artifacts.
4. Every page must show entry, exit, return path, above-the-fold region, and page-level data dependencies.

Each wireframe section must have four slots:

| Slot | Meaning |
|---|---|
| Order | Intended reading order, starting from 1 on each page |
| Label | Box name |
| Intent | What the user should understand or feel here |
| Why here | Reference or heuristic supporting the placement |

Wireframe rules:

- Gray boxes only. No color, typography, icons, or visual polish.
- Show `default`, `empty`, `loading`, and `error` variants for data regions.
- Note responsive behavior at 360, 768, and 1280 px.
- Decide reading order before drawing boxes.
- Keep one primary action visually isolated.

### Gate: Wireframe approval

Unless `--skip-gate` is set, ask whether the wireframe can move to visual design.

Options:

- Proceed to visual.
- Revise a specific part of the wireframe.
- Return to interview or references because the brief or reference choice was wrong.

The gate exists to settle experience and layout before color and typography distract the discussion.

### Phase 4: Visual

Create a clickable prototype from [templates/visual.html](templates/visual.html). Preserve the wireframe's page order, reading order, and intent.

Visual requirements:

- Use an existing design system when present. Detect `DESIGN.md`, `design-tokens.*`, `tokens.scss`, `tailwind.config.*`, or `_variables.scss`.
- Define typography, color, spacing, and motion tokens when no system exists.
- Body text must be at least 16 px, line-height at least 1.5, contrast at least 4.5:1, and touch targets at least 44 x 44 px.
- Do not default to generic Inter/Roboto/Arial/system-ui fallback stacks when a better design direction is needed.
- Avoid one-note purple gradients, generic card grids, and vague "modern clean" direction.
- Put all pages in one `visual.html` using hash routing with `<section class="page-mock" id="page-N">`.
- Add a page selector so reviewers can jump between pages.
- Wire every primary task to a demonstrable click path.
- Add state switches for `default`, `empty`, `loading`, and `error`.
- Make toggles, filters, checkboxes, masks, timers, counts, and cross-page state actually work with vanilla JavaScript.
- Keep the file usable without a build step or external JS dependency.

Before delivery, check [references/ux-checklist.md](references/ux-checklist.md).

### Phase 5: Deliver

Write the following files to `<out>/`:

```text
<out>/
  brief.md
  references.md
  flow.html
  wireframe.html
  visual.html
  DESIGN.md
```

Use [templates/DESIGN.md](templates/DESIGN.md) for DESIGN.md. It should capture tokens, reference decisions, per-page order preservation, UX checklist results, and implementation notes.

End with:

```text
Design ready at <out>/. Open visual.html in a browser.
Next: /functional-spec <label> --from <out>  (bind each element to real components + APIs), then /implement.
```

Run `open <out>/visual.html` only after user approval.

Downstream: before implementation, run `/functional-spec` to turn this wireframe
into a code-grounded contract (per-element function + reuse/new component +
real endpoint), so `/implement` has an unambiguous starting point.

## Standing rules

- Do not proceed past Phase 1 without a signed-off brief unless the user explicitly skips.
- References must include Steal, Adapt, and Reject; otherwise they are incomplete.
- A wireframe is an experience map, not a box grid.
- Every wireframe box needs Order, Label, Intent, and Why here.
- Wireframe first. No colors, fonts, or icons before the gate.
- Reuse the project's design system when it exists.
- Every data area needs default, empty, loading, and error states.
- Accessibility baselines are not optional.
- Output HTML must work as standalone files.
- Phase 4 must be a prototype, not a static image.
- Design by page. Do not force all tasks into one page or split into too many pages without a reason.
- `flow.html`, `wireframe.html`, and `visual.html` must share page IDs.
- Every page must have a way back to the entry path.

## Automated vs needs your taste

| Automated | User decides |
|---|---|
| Next interview question based on weakest brief slot | Whether the brief is signed off |
| Reference candidate proposals when the user has none | Which references and patterns to accept |
| Grid and responsive layout draft | Emotional tone and brand fit |
| Box slot placement | Whether the reading order and intent are correct |
| Existing design system detection | Whether new tokens fit the product |
| Accessibility minimum enforcement | Copy tone for empty and error states |
| UX checklist pass/fail | Whether the gate is approved |

## Boundaries

| This skill owns | This skill does not own |
|---|---|
| Wireframe HTML, visual HTML, and DESIGN.md | Production component implementation |
| Design system detection and reuse | Creating a full design system |
| UX checklist review | QA, E2E, or visual regression testing |
| Empty/loading/error state placement | Final product copywriting |
| Token documentation | Brand guideline authoring |

## Templates and references

| File | Purpose |
|---|---|
| [templates/brief.md](templates/brief.md) | Phase 1 signed-off problem brief |
| [templates/references.md](templates/references.md) | Phase 2 Steal/Adapt/Reject cards |
| [templates/flow.html](templates/flow.html) | Phase 3-A sitemap |
| [templates/wireframe.html](templates/wireframe.html) | Phase 3-B multi-page wireframe |
| [templates/visual.html](templates/visual.html) | Phase 4 prototype base |
| [templates/DESIGN.md](templates/DESIGN.md) | Phase 5 handoff document |
| [references/ux-checklist.md](references/ux-checklist.md) | Required UX checklist |
| [scripts/validate_skill.py](scripts/validate_skill.py) | Skill self-validation |

## Pitfall / Failure modes

- Treating Phase 1 as a bulk questionnaire.
- Skipping references without explicit user direction.
- Leaving wireframe Intent or Order slots empty.
- Adding visual styling in Phase 3.
- Placing primary and secondary actions with equal weight.
- Ignoring an existing design system.
- Deferring loading or error states to implementation.
- Using vague aesthetic direction.
- Forcing too many tasks into one page.
- Creating six or more pages without a strong reason.
- Letting page names or slugs drift across artifacts.
- Handling transitions as separate browser pages instead of one prototype.
- Creating pages with no return path.

## Pre-flight checklist

- [ ] Phase 1 -> 2: brief has explicit user sign-off.
- [ ] Phase 2 -> 3: each reference has Steal, Adapt, and Reject.
- [ ] Phase 3 -> Gate: each box has Order, Label, Intent, and Why here.
- [ ] Gate: user approved visual work or `--skip-gate` is set.
- [ ] Phase 4 -> 5: `references/ux-checklist.md` passed.
- [ ] Phase 5: brief.md, references.md, flow.html, wireframe.html, visual.html, and DESIGN.md exist.
- [ ] `scripts/validate_skill.py` passes.
