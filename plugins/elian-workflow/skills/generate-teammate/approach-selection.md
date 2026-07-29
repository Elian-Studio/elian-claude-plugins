# Phase 2-3: Work Decomposition & Approach Selection (Detail)

## Phase 2.0: Delegation triage (do this first)

Before decomposing into a team, decide whether delegation is warranted **at all**. Decompose
mentally, then check for a positive signal:

- **Breadth-first / read-heavy parallelism** (many independent things to explore or gather) → Subagent fan-out is a fit.
- **Genuinely independent modules** with disjoint files and no shared decisions → parallel build is a fit.
- **High-value real-time reconciliation** (parties must converge on one shared interface) → Agent Team *may* be a fit.

If **none** of these holds, the answer is **Direct** — a single agent. Say so and stop. Forcing a
team onto a coherence-critical or sequential task is over-decomposition, a documented anti-pattern
(see [references/execution-evidence.md](references/execution-evidence.md)), not diligence.

## Phase 2: Work Phase Decomposition

Decompose the work into **execution phases**. Composite work has different characteristics per phase, so do not judge the whole task with a single approach.

### Standard Phase Types

| Phase Type | Description | Approach is decided by characteristic analysis (not fixed) |
|------------|-------------|------------------------------------------------------------|
| Explore | Codebase analysis, situation assessment | Subagent or Agent Team (when multi-perspective exploration is needed) |
| Design | Architecture, API contract, UI design | Agent Team or Subagent (when independent design suffices) |
| Implement | Coding, feature development | Subagent or Agent Team (when coordination is needed) |
| Verify | Testing, review, quality checks | Subagent or Agent Team (when cross-validation is needed) |

> **Phase type does not determine the approach.**
> Do not hardcode "exploration → Subagent" or "design → Agent Team."
> Always judge by the shared selection criteria.

### Phase Decomposition Output Format

```
Work phase decomposition:

┌─────────────┬────────────────────────────────┬──────────────────────────────────────┐
│    Phase    │            Content              │           Characteristics            │
├─────────────┼────────────────────────────────┼──────────────────────────────────────┤
│ A: Explore  │ {exploration target}            │ Independent / parallel; results only │
├─────────────┼────────────────────────────────┼──────────────────────────────────────┤
│ B: Design   │ {design target}                 │ Multi-perspective debate, cross-     │
│             │                                 │ layer coordination required          │
├─────────────┼────────────────────────────────┼──────────────────────────────────────┤
│ C: Build    │ {build target}                  │ File separation possible, no debate  │
└─────────────┴────────────────────────────────┴──────────────────────────────────────┘

Phase dependencies: A → B → C
```

---

## Phase 3: Per-Phase Approach Selection

Judge the optimal approach **independently for each phase**.

### Shared Selection Criteria (canonical)

The full criteria, decision tree, and GOOD / BAD examples for execution strategy are in the shared document:

> **[../_shared/execution-strategy.md](../_shared/execution-strategy.md)**

That document is the single source of truth used by `/generate-teammate` and any other skills that share execution strategy logic.

### Decision Output

You **must** output the per-phase comparison table to the user in this format:

```
Per-phase approach decision:

┌─────────────┬───────────────┬───────────────────┬───────────────┬──────────────────────────────────┐
│    Phase    │  Agent Team   │    Subagent       │   Direct      │              Reason              │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ A: Explore  │ Unfit         │ ★ Fit             │ Possible      │ No coordination needed; gather   │
│             │               │                   │               │ results only                     │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ B: Design   │ ★ Fit         │ Possible          │ Unfit         │ API contract negotiation +       │
│             │               │                   │               │ cross-perspective debate         │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ C: Build    │ Unfit         │ ★ Fit             │ Possible      │ Contract fixed, file separation  │
│             │               │                   │               │ clear                            │
└─────────────┴───────────────┴───────────────────┴───────────────┴──────────────────────────────────┘

Strategy: hybrid — Subagent (explore) → Agent Team (design) → Subagent (build)
```

Fit labels: `★ Fit` / `Possible` / `Unfit`

### Economic viability gate

A `★ Fit` for Subagent or Agent Team is **necessary but not sufficient** — it must also pay for
itself. Multi-agent orchestration costs roughly **15× the tokens of a single session**, and in
controlled evals token spend alone explained ~80% of the performance difference, so a large part of
any "multi-agent win" is just spending more. Apply the gate per phase:

| Approach | Rough cost vs Direct | Escalate only when |
|----------|----------------------|--------------------|
| **Direct** | 1× (baseline) | — default — |
| **Subagent (parallel)** | ~N× (N = fan-out width) | breadth-first / read-heavy / genuinely independent units |
| **Agent Team** | ~15× chat-equivalent + super-linear coordination (n agents → n(n−1)/2 interaction points) | real-time cross-perspective reconciliation that Subagent + a single synthesizer cannot do |

Rules:

1. If the parallel benefit of a phase does not clearly outweigh its cost multiplier, **downgrade to Direct**.
2. **Agent Team is the last resort** — it is the least-validated mode (no head-to-head benchmark shows inter-agent communication beating "independent subagents + single synthesis") and the highest-coordination-cost one (~31% of multi-agent failures are inter-agent misalignment). Use it only for genuine real-time reconciliation, never as a default for "debate."
3. Carry each phase's chosen multiplier into the Phase 6 confirmation so the **user** owns the spend decision.

### Strategy Type Decision

Combine the per-phase results into an overall strategy:

| Strategy Type | Condition | Description |
|---------------|-----------|-------------|
| **Single: Agent Team** | All phases are Agent Team-fit | Traditional team configuration |
| **Single: Subagent** | All phases are Subagent-fit | Parallel Agent tool calls |
| **Single: Direct** | All phases are direct-fit | No team / subagent needed |
| **Hybrid** | Optimal approach varies per phase | **Different approach per phase** |

### Common Hybrid Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| Explore → Design → Build | Parallel research, debated design, parallel build | Subagent → Agent Team → Subagent |
| Explore → Build → Verify | Research first, parallel build, multi-perspective review | Subagent → Subagent → Agent Team |
| Design → Build | Multi-perspective design, then parallel build | Agent Team → Subagent |

### Gate Decision

- **Single strategy** → proceed to Phase 4 with that approach
- **Hybrid strategy** → combine per-phase plans and proceed to Phase 4
- **All direct execution** → tell the user "Direct execution is the most efficient option for this task" and propose execution
