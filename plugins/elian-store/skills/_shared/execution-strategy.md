# Execution Strategy — Subagent vs Agent Team vs Direct Execution

This document is the canonical **execution-strategy decision criteria** shared by skills in this plugin (currently `/generate-teammate`). Changes here affect every consumer.

## Sources

- [Claude Code Official: Sub-agents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Official: Agent Teams](https://code.claude.com/docs/en/agent-teams)

---

## Core Decision Question

> **"Do the workers need to communicate with each other?"**
> — Claude Code official docs: "Choose based on whether your workers need to **communicate with each other**"

```
                Do the workers need to communicate?
               /                                  \
             Yes                                  No
              │                                    │
       Nature of communication?           ──→ Subagent
       /                  \                    (returning results is enough)
   Real-time debate     Result handoff
   (rebuttal, sync)     (sequential dep)
      │                    │
   Agent Team            Subagent
   (shared tasks,        (chaining: A result → B input)
    inter-messaging)
```

### Auxiliary questions (when communication is needed: distinguish Team vs Subagent chaining)

| Question | Yes → Agent Team | No → Subagent |
|----------|------------------|---------------|
| Do teammates' deliverables need to **reference / negotiate** with each other? | FE/BE API contract negotiation, design debate | Independent exploration, separate file edits |
| Does mid-task work shift direction based on **another teammate's intermediate result**? | Design decision affects build | No conflict even when run in parallel |
| Do workers need to **rebut / verify** each other's results? | Competing-hypothesis debugging, multi-perspective review | Aggregating results is enough |

---

## Three-approach Comparison

| | Subagent | Agent Team | Direct execution |
|---|---------|-----------|------------------|
| **Context** | Own window; results returned to caller | Own window; fully independent | Current session |
| **Communication** | Returns result to main only | Direct messaging between teammates | N/A |
| **Coordination** | Main agent manages all work | Self-coordination via shared task list | N/A |
| **Best for** | Focused work where only the result matters | Complex work needing discussion + collaboration | Simple work |
| **Token cost** | Low (summary returned) | High (each teammate is a full instance) | Lowest |

---

## GOOD Examples: Agent Team is the right choice

### 1. FE/BE API contract design (cross-layer coordination)

```
FE teammate: "This field should be an array — easier for pagination."
BE teammate: "An array causes N+1 queries. Should we split the DTO?"
→ Real-time debate to settle the contract → Agent Team
```

**Why Team**: The API contract is unsettled, and one side's decision changes the other's build direction. With Subagents, each side picks a different contract and they collide on integration.

### 2. Competing-hypothesis debugging

```
Teammate A: "Cache expiry is the cause" → presents evidence
Teammate B: "Concurrency issue" → rebuts A, presents new evidence
Teammate C: "Query timeout" → rebuts both A and B
→ Rebuttal between hypotheses is the value → Agent Team
```

**Why Team**: A single agent anchors on the first hypothesis. Mutual rebuttal raises the chance of finding the actual root cause.
Official docs: "Sequential investigation suffers from anchoring"

### 3. Multi-perspective code review (perspective conflict reconciliation)

```
Security reviewer: "Add this input validation — required."
Performance reviewer: "That validation in a hot path causes regressions."
→ Resolve security vs performance tradeoff via reviewer debate → Agent Team
```

**Why Team**: Review perspectives conflict; without debate, priorities cannot be set.

### 4. Multi-perspective exploration (cross-validation needed)

```
UX researcher: User flow analysis → "This step is unnecessary"
Architect: Tech structure analysis → "That step warms a cache; removing degrades performance"
→ Cross-validation of findings required → Agent Team
```

**Why Team**: One worker's finding shifts the others' direction.

---

## GOOD Examples: Subagent is the right choice

### 1. Independent codebase exploration

```
Subagent A: BE module structure analysis → returns result
Subagent B: FE component structure analysis → returns result
Lead synthesizes
```

**Why Subagent**: Each explores and returns; no communication needed.
Official docs: "Use subagents when you need quick, focused workers that report back"

### 2. Independent build after design is fixed

```
API contract already agreed (design.md + api-spec.md committed)
Subagent A: BE API build (per design)
Subagent B: FE UI build (per design)
```

**Why Subagent**: Contract is fixed, no mid-flight coordination needed. File ownership is also clearly separated.

### 3. N independent bug fixes

```
Subagent A: Fix B1 (ScheduleService.java)
Subagent B: Fix B2 (AlimTalkService.java)
Subagent C: Fix B3 (ConsultStatus.java)
→ Different files, zero communication
```

**Why Subagent**: File ownership separated + no mutual references.

### 4. Same-pattern repeated work

```
Subagent A: CRUD API for Entity1
Subagent B: CRUD API for Entity2
Subagent C: CRUD API for Entity3
→ Identical pattern, no debate needed
```

**Why Subagent**: When pattern is identical, coordination is wasted. Team overhead only.

### 5. Test / verification execution (isolate noisy output)

```
Subagent: Run full test suite → returns only failed cases summary
→ Verbose output stays out of main context
```

**Why Subagent**: Official docs: "isolate high-volume operations"

### 6. Independent reviews + aggregate (the /generate-mr pattern)

```
Subagent A: Security review → writes result file
Subagent B: Quality review → writes result file
Subagent C: Performance review → writes result file
Lead aggregates result files
```

**Why Subagent**: Reviewers don't need to talk; aggregating results is enough.
(If reviewers must reconcile conflicts → Agent Team)

---

## BAD Examples: wrong choice

### BAD 1: Agent Team for independent work

```
Spawning an Agent Team for 3 independent bug fixes
→ Zero inter-teammate communication, only coordination overhead
→ 3x token cost (each teammate has its own context)
```

**Lesson**: No communication → Team is wasteful. 3 Subagents are faster and cheaper.

### BAD 2: Subagents in parallel before contract is fixed

```
FE/BE API contract not yet agreed → spawned Subagents to build FE/BE in parallel
→ FE built `{ items: [...] }`, BE built `{ data: { list: [...] } }`
→ Integration breaks → rework
```

**Lesson**: When the contract is unsettled, first use Team to negotiate, then Subagents to build.

### BAD 3: Agent Team for same-pattern repetition

```
3 CRUD endpoints as a Team → no debate to have, teammates idle
→ Pure team-management overhead
```

**Lesson**: Identical pattern + no cross-reference → Subagents are efficient.

### BAD 4: Agent Team for sequentially dependent work

```
"Design → build → test" as a 3-person Team
→ Build can't start until design is done; test can't start until build is done
→ 2 teammates always idle, no parallel benefit
```

**Lesson**: Strong sequential dependency → direct execution or Subagent chaining is better.

---

## When Direct Execution Fits

- 1 work unit, simple
- < 3 files changed
- Can finish quickly in a single session
- Frequent user interaction needed (iterative confirmation / tweaking)

---

## generate-teammate Application

### Per-phase decision

`/generate-teammate` decomposes work into phases and applies the criteria above **independently per phase**.

```
Phase A: Explore  → no communication needed   → Subagent
Phase B: Design   → API contract negotiation  → Agent Team
Phase C: Build    → contract fixed, indep.    → Subagent
```

The same task may use different approaches per phase; this is called the **hybrid strategy**.

### Required per-phase output

```
Per-phase approach decision:

┌─────────────┬───────────────┬───────────────────┬───────────────┬──────────────────────────────────┐
│    Phase    │  Agent Team   │    Subagent       │   Direct      │              Reason              │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ A: Explore  │ Unfit         │ ★ Fit             │ Possible      │ No comm needed, gather only      │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ B: Design   │ ★ Fit         │ Possible          │ Unfit         │ API contract + perspective debate│
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ C: Build    │ Unfit         │ ★ Fit             │ Possible      │ Contract fixed, files separate   │
└─────────────┴───────────────┴───────────────────┴───────────────┴──────────────────────────────────┘

Strategy: hybrid — Subagent (explore) → Agent Team (design) → Subagent (build)
```

---

## Team Size Guide (when picking Agent Team)

| Work scale | Recommended teammate count | Reason |
|------------|---------------------------|--------|
| Small (3~5 tasks) | 2 | Minimize coordination overhead |
| Medium (6~15 tasks) | 3 | 5~6 tasks per teammate is optimal |
| Large (16+ tasks) | 4~5 | Coordination cost spikes beyond 5 |

Official docs: "Start with 3-5 teammates for most workflows"
Official docs: "Having 5-6 tasks per teammate keeps everyone productive"
