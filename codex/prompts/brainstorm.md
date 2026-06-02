# /brainstorm - Conversational discovery for fuzzy requests (Codex Port)

Install path: `~/.codex/prompts/brainstorm.md`.

Invocation:

```text
/brainstorm <topic> [--depth shallow|deep] [--output plan|doc|none]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/brainstorm/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

Read-only contract: do not edit files, create files, stage, commit, push, or run destructive commands. If the result should become a durable artifact, emit the requested Markdown in the response and stop. If implementation is needed, hand off to `/implement`, `/generate-teammate`, or `/review` and stop.

## Purpose

Use this prompt when the request is fuzzy, multiple paths are possible, or the user explicitly wants to explore options before choosing a direction.

Do not use it when requirements are already clear or when the user is fixing a confirmed bug.

## Common Contract

1. Ask, do not assume.
2. Produce at least 3 options before recommending one unless the user has already clearly chosen a path.
3. Keep decisions serial. Explore in parallel only when there are multiple independent topics.
4. Preserve the decision and rationale in the requested artifact format when `--output plan` or `--output doc` is used.
5. End with one next question, next action, or handoff payload.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `<topic>` | Subject, issue ID, or free text | required |
| `--depth shallow\|deep` | Probing depth | `shallow` |
| `--output plan\|doc\|none` | Output artifact type | `none` |

`$ARGUMENTS` always wins over any local default.

## Workflow

```text
Phase 1: Context recognition
Phase 2: Requirements probing
Phase 3: Option drafting
Phase 4: Tradeoff comparison
Phase 5: Decision gate
Phase 6: Handoff or artifact output
```

### Phase 1: Context recognition

Look for related code, docs, previous decisions, or issue context from the topic text. If the topic splits into 2+ independent decisions, surface the split and ask which one to tackle first.

If the input is thin, ask the single most important intent question and stop.

### Phase 2: Requirements probing

Use a small number of plain-text questions to surface the missing facts that change the decision:

- WHO is the primary user?
- WHAT changes from the current behavior?
- WHY is the change needed?
- WHEN does it happen?
- WHERE does it apply?
- HOW MUCH scale, latency, cost, or complexity is acceptable?

Use one round for shallow mode and up to three rounds for deep mode.

### Phase 3: Option drafting

Draft at least 3 approaches:

- MVP option
- Balanced option
- Ideal option

Keep each option grounded in the requirements that were actually confirmed.

### Phase 4: Tradeoff comparison

Compare the options against complexity, files changed, convention alignment, extensibility, user impact, and risk.

Recommend one option and state why the rejected options are not the best fit.

### Phase 5: Decision gate

Ask for the final choice if it is still not clear. If the user says "Iterate", return to the probing or option-drafting phase instead of guessing.

### Phase 6: Handoff or artifact output

If `--output plan`, emit a compact plan artifact in Markdown with goal, decision, requirements, phased plan, and brainstorm record.

If `--output doc`, emit the document artifact requested by the topic.

If `--output none`, emit only the conversational recommendation and handoff.

## Output Shapes

### Default output

```text
Decision summary
- Topic: <topic>
- Recommendation: <option>
- Why: <1-2 lines>

Open questions
- <unresolved item>

Next
- <next question or next action>
```

### Plan output

```text
# <topic>

**Started**: YYYY-MM-DD
**Status**: planned

## Goal
<decision direction summary>

## Decision
- Selected option: <Option X>
- Rationale: <why>
- Rejected options: <Y, Z> - <why not>

## Requirements
1. <requirement 1>
2. <requirement 2>

## Phased plan
- [ ] Phase 1: <description>
- [ ] Phase 2: <description>

## Brainstorm record

### Probed questions
- Q: <q1> -> A: <a1>
- Q: <q2> -> A: <a2>
```

## Forbidden

- Pretend a single option is a brainstorm.
- Invent requirements that were not stated or confirmed.
- Run a decision gate without naming rejected options.
- Drag the user through unlimited questioning.
- Write files or modify the repository.

## Pre-Output Self-Check

- [ ] Topic is clear enough to explore.
- [ ] Thin input was clarified before option drafting.
- [ ] At least 3 options were drafted when comparison was needed.
- [ ] Decision and rationale are separated from open questions.
- [ ] The output ends with one next question or next action.
