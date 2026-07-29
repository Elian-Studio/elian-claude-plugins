# /brainstorm — Templates

## Captured requirements template

```markdown
## Captured requirements

### Core
1. {requirement 1 — concrete + observable}
2. {requirement 2}

### Constraints
- {constraint 1 — performance / compliance / time}
- {constraint 2}

### Non-goals
- {explicitly out of scope}

### Open questions (need decision in Phase 5 or follow-up brainstorm)
- {unresolved item}

### Assumptions (flag if any becomes false)
- {assumption}
```

## Option draft template

```markdown
### Option A: {one-line summary}

**Approach**: {how — 2-3 sentences}

**Scope**:
- Frontend: {files / components}
- Backend: {files / modules}
- Data: {DB / migration impact}

**Pros**:
- {concrete pro 1}
- {concrete pro 2}

**Cons**:
- {concrete con 1}
- {concrete con 2}

**Complexity**: low / medium / high
**Reversibility**: easy / medium / hard
**Convention alignment**: matches / new pattern (with rationale)
```

## Tradeoff matrix template

```markdown
## Option comparison

| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| Implementation complexity | low | medium | high |
| Files changed | 2 | 5 | 12 |
| Convention alignment | strong | weak | new pattern |
| Extensibility | limited | medium | broad |
| UX impact | minimal | improved | major |
| Risk | low | medium | medium-high |
| Reversibility | easy | medium | hard |

### Recommended: Option {X}
{1-2 sentence rationale tied to constraints / requirements}

### Why not the others
- Option {Y}: {one-line trade rejected}
- Option {Z}: {one-line trade rejected}
```

## Plan file template (`.claude/plans/{issueId}.md`)

```markdown
# {topic}

**Started**: YYYY-MM-DD
**Status**: planned
**Origin**: /brainstorm session {date}

## Goal
{decision direction summary}

## Decision
- Selected option: {Option X}
- Rationale: {why}
- Rejected: {Y, Z} — {why not}

## Requirements
1. {requirement 1}
2. {requirement 2}

## Constraints
- {constraint 1}

## Phased plan
- [ ] Phase 1: {description}
  - Files: {expected change set}
  - Tests: {expected coverage}
- [ ] Phase 2: {description}

## Brainstorm record
### Probed questions
- Q: {q1} → A: {a1}
- Q: {q2} → A: {a2}

### Multi-topic split (if applicable)
- This brainstorm covered: {primary topic}
- Pending follow-ups: {topic 2}, {topic 3}
```

## Multi-topic split detection prompt

```markdown
I detected N independent topics in your request:

1. {Topic 1} — {one-line context summary from Phase 1 recon}
2. {Topic 2} — {one-line context summary}
3. {Topic 3} — {one-line context summary}

These appear independent because:
- Different domains: {domain A vs B}
- No mutual dependency: {evidence}
- Each needs its own option comparison

How should we proceed?
- A) Tackle Topic 1 first; queue 2 and 3 as `/brainstorm` follow-ups
- B) Tackle Topic 2 first
- C) Wrap them into a single umbrella topic (treats them as sub-requirements)
```

## Reflection memo template

```markdown
# Brainstorm reflection — {topic-slug}

**Date**: YYYY-MM-DD
**Outcome**: {selected option / iterated / aborted}

## Question productivity
- Most useful Q: {q} — surfaced {key requirement}
- Least useful Q: {q} — answer didn't change anything

## Option diversity
- Were the 3 options spanning the design space, or 3 variants of one frame?
- Reason: {evaluation}

## Decision velocity
- Rounds in Phase 2: {N}
- Iterations through Phase 5: {N}
- If high, what underlying ambiguity caused it?

## Carryover
- Pending topics for future brainstorm: {list}
- New question template ideas: {if any}
```
