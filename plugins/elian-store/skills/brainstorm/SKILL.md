---
name: brainstorm
description: "When the user has a fuzzy idea, ambiguous change request, or runs /brainstorm, drive a conversational discovery: context → Socratic requirements probing → 3+ option draft → tradeoff comparison → decision → handoff to implementation skills with persistent plan artifact."
when_to_use: Use when the request is ambiguous, multiple paths are possible, or the user explicitly invokes /brainstorm. Do NOT use when requirements are already clear (go straight to /implement) or when fixing a confirmed bug (use /fix).
argument-hint: "<topic-or-issue-id> [--depth shallow|deep] [--output plan|doc|none]"
allowed-tools: Read, Glob, Grep, Bash(git status*), Bash(git log*), AskUserQuestion, Agent, Write, Edit
disable-model-invocation: true
---

# /brainstorm — Conversational discovery for fuzzy requests

When the user has a vague idea, an ambiguous change, or wants to explore options before committing, this skill walks through context gathering, Socratic requirement probing, 3+ option drafting, tradeoff comparison, decision, and handoff to downstream implementation skills.

## Parameters

| Option | Meaning | Default |
|--------|---------|---------|
| `<topic>` | Subject (required) — issue ID or free-text | — |
| `--depth shallow\|deep` | Probing depth | `shallow` |
| `--output plan\|doc\|none` | Output artifact type | `none` |

## Workflow

```
Phase 1: Context recognition
Phase 2: Requirements probing (Socratic)
Phase 3: Option drafting (3+ approaches)
Phase 4: Tradeoff comparison
Phase 5: ★ Decision gate ★ ── HARD GATE: no implementation before approval
Phase 6: Handoff to implementation
```

> **★ Implementation Hard Gate ★**
> Do NOT write code, scaffold files, run mutating commands, or invoke an implementation skill
> (`/implement`, `/generate-teammate`, …) until the user has approved an option at the Phase 5
> decision gate. This holds for **every** topic regardless of perceived simplicity — "obviously
> trivial" requests are exactly where an unexamined assumption costs the most. Brainstorm produces
> a decision and a plan; it never implements.

### Phase 1: Context recognition

Extract:
| What | How |
|------|-----|
| Related code | Glob / Grep for existing implementations |
| Design docs | Search `docs/domains/`, `.claude/plans/` |
| Issue context | If issue ID given, look at prior work |

**Issue ID present**:
```bash
Glob pattern="**/.claude/plans/*{issueId}*"
Glob pattern="**/docs/**/{issueId}/**/*.md"
```

**Free topic**: Glob/Grep on user keywords for related code/domain.

Summarize the gathered context for the user.

#### Multi-topic detection

If the topic decomposes into **2+ independent decisions** (different domains / no inter-dependence / each needs separate option comparison), then:

1. **Parallel reconnaissance**: spawn `Agent({subagent_type: 'Explore'})` per topic to gather code / docs in parallel.
2. Summarize each topic's findings.
3. Use `AskUserQuestion`:
   - "I detected N independent topics. Which should we tackle first?"
     - "{Topic 1} — {one-line summary}"
     - "{Topic 2} — {one-line summary}"
     - "Wrap them into one umbrella topic"
4. **Single-topic choice** → Phase 2 with that topic only; surface remaining in Phase 6 next-steps.
5. **Umbrella choice** → redefine the umbrella; treat sub-topics as requirements; Phase 2.

> **Principle**: Phase 1 (no user input needed) is parallelizable. Phase 2-5 (user dialogue) stays serial on one focused topic.

### Phase 2: Requirements probing (Socratic)

**Core principle: ask, don't assume.**

Use `AskUserQuestion` to surface unstated requirements.

#### Question framework

| Dimension | Sample question |
|-----------|-----------------|
| **WHO** | Primary user? (clinician / patient / admin) |
| **WHAT** | Core behavior? What changes from now? |
| **WHY** | Why this change? Which problem does it solve? |
| **WHEN** | When is this triggered? |
| **WHERE** | Scope? (specific page / API / global) |
| **HOW MUCH** | Performance / cost / complexity constraints? |

#### Process

1. **Round 1**: 2-3 most important questions via `AskUserQuestion` (one batch).
2. **Analyze answers**: extract follow-ups.
3. **Round 2**: only if specifics still missing (max 2 rounds in `--depth shallow`).
4. **Summarize**: present captured requirements; ask for confirmation.

```markdown
## Captured requirements

### Core
1. {requirement 1}
2. {requirement 2}

### Constraints
- {constraint 1}
- {constraint 2}

### Open questions (need decision)
- {unresolved item}
```

`--depth deep` → up to 3 rounds; explicitly probe edge cases and exception paths.

### Phase 3: Option drafting

Draft **at least 3 approaches**.

```markdown
### Option A: {one-line summary}

**Approach**: {how — 2-3 sentences}

**Scope**:
- Frontend: {files / components}
- Backend: {files / modules}

**Pros**: {why good}
**Cons**: {what we worry about}
**Complexity**: low / medium / high
```

Drafting principles:
1. **MVP option** — simplest, fastest.
2. **Balanced option** — quality vs speed.
3. **Ideal option** — unconstrained, best design.
4. **Name the boundaries.** For each option, state more than the file scope: the module boundaries
   it draws, the interface/contract each unit exposes, and what it depends on — i.e. *what it does
   / how it's used / what it depends on*. A unit you can't describe that way isn't bounded yet, and
   an option that piles everything into one growing unit is a smell to split.

Match project conventions when relevant — refer to existing code patterns.

### Phase 4: Tradeoff comparison

```markdown
## Option comparison

| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| Implementation complexity | | | |
| Files changed | | | |
| Convention alignment | | | |
| Extensibility | | | |
| UX impact | | | |
| Risk | | | |

### Recommended: Option {X}
{1-2 sentence rationale}
```

### Phase 5: ★ Decision gate ★

`AskUserQuestion`:
```
"Which option to proceed with?"
  - "Option A — {summary}"
  - "Option B — {summary}"
  - "Option C — {summary}"
  - "Iterate — more discussion needed"
```

**"Iterate" choice** → loop back to Phase 2-4 partially.

### Phase 6: Handoff

Connect the decision to downstream skills. Templates for plan files, captured-requirements blocks, option drafts, and tradeoff matrices are in [references/templates.md](references/templates.md).

#### `--output plan` (default)

Write `.claude/plans/{issueId or topic}.md`:

```markdown
# {topic}

**Started**: YYYY-MM-DD
**Status**: planned

## Goal
{decision direction summary}

## Decision
- Selected option: {Option X}
- Rationale: {why}
- Rejected options: {Y, Z} — {why not}

## Requirements
1. {requirement 1}
2. {requirement 2}

## Phased plan
- [ ] Phase 1: {description}
- [ ] Phase 2: {description}

## Brainstorm record

### Probed questions
- Q: {q1} → A: {a1}
- Q: {q2} → A: {a2}
```

#### `--output doc`

Write to `docs/domains/{domain}/`. If `/manage-domain-docs` exists, integrate.

#### `--output none`

No file produced; conversation context only.

#### Plan self-review (when a file was written)

After writing the plan/doc (`--output plan` or `doc`), re-read it with fresh eyes and fix inline —
no re-review loop, just fix and move on. This checks the **artifact**, distinct from the process
**Reflection** at the end of the skill (which critiques the brainstorm, not the file):

1. **Placeholder scan** — any `TBD`, `TODO`, empty section, or vague requirement? Resolve it.
2. **Internal consistency** — does the Decision match the Requirements and the Phased plan? Any
   section contradict another?
3. **Scope** — is this focused enough for one implementation pass, or does it still need a split?
4. **Ambiguity** — could any requirement be read two ways? Pick one and make it explicit.

#### Written-plan review gate (when a file was written)

After the self-review passes, ask the user to review the **written file** before any handoff:

> "Plan written to `.claude/plans/{id}.md`. Please review it and tell me if anything should change
> before we hand off to `/implement`."

Wait for the response. On change request → edit the file and re-run the Plan self-review. Only once
the user approves do you surface the Next-steps card. (`--output none` skips both steps — there is
no artifact to review; go straight to the card.)

#### Next steps card

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Brainstorm complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Decision summary
- Option: {selected}
- Core: {one-line summary}

## Next
- `/implement {issueId}` — start build
- `/manage-domain-docs` — design doc generation
- `/brainstorm {related-topic}` — explore related topic

{If multi-topic split happened in Phase 1:}
## Pending topics
- `/brainstorm {topic 2}` — {one-line}
- `/brainstorm {topic 3}` — {one-line}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Standing Rules

- **Ask, don't assume.** Every assumption you skip is a misunderstanding waiting at integration.
- **3+ options.** A single option isn't a comparison; it's an instruction.
- **No implementation before the gate.** Don't write code, scaffold, or invoke an implementation
  skill until Phase 5 is approved — no matter how trivial the topic looks.
- **The user owns the decision.** The skill recommends, not decides.
- **Persist artifacts.** Conversation context dies; `.claude/plans/{id}.md` survives.
- **Match existing patterns** unless explicitly justified deviating.
- **Multi-topic = sequential.** Don't parallelize the user's attention; only the recon.

## Procedure (one-time)

`/brainstorm <topic>` runs Phase 1 → 6. Iterate Phase 2-4 if user picks "Iterate" in Phase 5.

## Forbidden

- ❌ Drafting only 1 option. That's an instruction, not a brainstorm.
- ❌ Writing code, scaffolding, or invoking an implementation skill before Phase 5 is approved. Brainstorm decides; it never implements.
- ❌ Handing off a plan file the user hasn't reviewed. The written-plan gate is not optional when a file was produced.
- ❌ Skipping `AskUserQuestion` in Phase 5. The user owns the decision.
- ❌ Recommending an option without naming the rejected ones. The "why not" is half the value.
- ❌ Asking 5+ questions in one round. Cognitive overload kills useful answers.
- ❌ Inventing requirements the user didn't state. Mark as "open question" if uncertain.
- ❌ Designing for hypothetical future requirements. Solve today's problem.
- ❌ Bypassing existing conventions without justification.
- ❌ Spawning parallel Agent recon AND parallel decision threads. Recon parallel is fine; decisions stay serial.

## Pitfall / Known Issues

| Pitfall | Why it happens | Fix |
|---------|----------------|-----|
| User picks an option that's actually outside scope | Option draft was too aspirational | Constrain options to feasible scope; mark stretch options explicitly |
| Decision made then user changes mind next session | Decision wasn't persisted | Use `--output plan`; the plan file is the contract |
| Sibling features ignored | Phase 1 didn't explore broadly | Re-run Glob with broader patterns; specifically search for similar past decisions |
| Options too similar | Brainstorm fell into one frame | Force "ideal option" to be radically different (different architecture, not different naming) |
| Probing dragged on forever | No depth budget | `--depth shallow` is 2 rounds max; respect it |
| User asked for X, brainstorm produced Y | Topic creep in Phase 2 | Confirm scope summary before Phase 3 |
| Multi-topic confusion | Phase 1 detection skipped | Detect early; user decides which topic first |

For failure recovery: every Phase has a re-entry path — Phase 5 "Iterate" loops to Phase 2; Phase 6 next-steps preserve unsplit topics for future runs.

## Where this fits in the workflow

```
fuzzy idea → /brainstorm → /implement (or /generate-teammate first if multi-domain) → /review → release
                  │
                  └── Pre: ambiguous request, multiple paths possible.
                      Post: decision + plan file; downstream skill picks up.
```

Sequencing principles:
- **Before** /brainstorm: don't pre-decide. The skill's value is exploring options.
- **During** /brainstorm: keep options generative — quantity then quality.
- **After** /brainstorm: hand off to /implement (single decision) or /generate-teammate (multi-decision composite).

## Manual decision gating (automated vs taste)

| Concern | Automated | Needs user taste |
|---------|-----------|------------------|
| Context gathering (Glob / Grep) | ✅ | — |
| Multi-topic detection | ✅ | — |
| Question framework selection | ✅ | — |
| Option drafting (3+ structured) | ✅ | — |
| Tradeoff matrix population | ✅ | — |
| Recommendation labeling | ✅ | — |
| Final decision (Phase 5) | — | ✅ |
| Whether captured requirements are right | drafted automatically | ✅ user confirms |
| Plan self-review (placeholder / consistency / scope / ambiguity) | ✅ | — |
| Whether the written plan file is correct | drafted automatically | ✅ user confirms |
| Whether to drop into "Iterate" loop | — | ✅ |
| Whether multi-topic should be wrapped vs split | — | ✅ |

## Reflection (end of skill)

Write 3 short observations into `claudedocs/{topic-slug}-brainstorm-reflection.md`:

1. **Question productivity** — which Phase 2 questions surfaced the most useful info? (Templates can iterate.)
2. **Option diversity** — did the 3 options really span the space, or were they 3 variants of one frame?
3. **Decision velocity** — how many rounds before convergence? Long iterations hint at unclear underlying constraints.

## Persistent artifacts for downstream

| Artifact | Producer phase | Downstream consumer |
|----------|----------------|---------------------|
| Captured requirements | Phase 2 | /implement (acceptance criteria), /create-prd |
| Option comparison table | Phase 4 | Future similar decisions; ADR seed |
| Decision + rationale | Phase 5 | /implement (knows what to build); ADR |
| Plan file (`.claude/plans/{id}.md`) | Phase 6 | /implement, /generate-teammate, project history |
| Reflection memo | Post-Phase 6 | Question framework iteration |

## BEFORE / AFTER patterns

### Single option vs 3+ options

❌ **BEFORE — instruction disguised as a brainstorm**:

```
"How should we add notifications?"
> "Use Firebase Cloud Messaging."
```

User has no decision to make. Tradeoffs invisible.

✅ **AFTER**:

```
"How should we add notifications?"
> Three approaches:
  A. Server-Sent Events (in-app only) — low complexity, no third-party
  B. Firebase Cloud Messaging — push outside app, third-party dep, vendor lock
  C. Self-hosted MQTT — full control, ops burden
> Recommended: A for MVP; B if push-outside-app is a v2 requirement.
> Rejected C unless ops capacity exists.
```

User can choose with rationale.

### Assumption-laden vs Socratic

❌ **BEFORE**:

```
User: "Add a search feature."
> Drafts: full-text Postgres, Elasticsearch, Algolia
> (no questions about WHO uses it, WHAT they search, scale, latency)
```

Options are technically diverse but probably don't match the user's actual need.

✅ **AFTER**:

```
Round 1: WHO will use search? WHAT do they search? scale (rows)? latency budget?
Round 2 (if needed): typo tolerance? sorting? facets?
Then options matched to the answers.
```

Options are scoped to actual requirements.

### Single-topic vs multi-topic

❌ **BEFORE**:

```
"We need notifications, billing, and analytics."
> Brainstorm tries to cover all three at once.
> Decisions tangled; Phase 5 produces a non-decision.
```

✅ **AFTER**:

```
Phase 1 detects 3 topics; AskUserQuestion picks order.
First topic only → Phase 2-5 with focused dialogue.
Phase 6 next-steps lists `/brainstorm billing`, `/brainstorm analytics` as follow-ups.
```

Decisions made cleanly, one at a time.

## Skill verification

```bash
python3 [scripts/validate_skill.py](scripts/validate_skill.py)
python3 [scripts/validate_skill.py](scripts/validate_skill.py) --json
```

## Pre-flight checklist

Before Phase 5 (decision):
- [ ] Context summarized (Phase 1 outputs)
- [ ] Multi-topic detection performed
- [ ] Requirements captured and confirmed by user
- [ ] At least 3 options drafted (each with pros / cons / complexity)
- [ ] Each option states its module boundaries / interface / dependencies (not just file scope)
- [ ] Tradeoff matrix populated with concrete values
- [ ] Recommendation given with rationale
- [ ] No implementation action taken yet (hard gate held)

Before handoff (Phase 6, when a file was written):
- [ ] Plan self-review done (placeholder / consistency / scope / ambiguity)
- [ ] User reviewed and approved the written plan file

## Skill integrations

| Skill | Phase |
|-------|-------|
| `Agent({subagent_type: 'Explore'})` | Phase 1 — multi-topic recon (parallel) |
| `/manage-domain-docs` | Phase 6 — `--output doc` mode |
| `/implement` | Post-Phase 6 — primary handoff |
| `/generate-teammate` | Post-Phase 6 — multi-domain composite work |
| `/create-prd` | Post-Phase 6 — formal PRD generation |

## Exceptions

1. **Pre-decided direction**: user has a clear path → shrink Phase 2; jump to Phase 3 with their direction as Option A.
2. **Simple Q&A**: comparison unnecessary → answer directly; no Phase 3-4.
3. **Existing design doc found**: Phase 1 → tune Phase 2 questions to gaps in the doc.
4. **`--depth shallow`**: 1 round in Phase 2; up to 2 options sufficient.
5. **Strong existing pattern**: codebase has the same pattern repeated → propose following pattern X; ask "explore alternatives?". If "no", skip to Phase 5. **Criteria**: change confined to one module + same structure repeats.
