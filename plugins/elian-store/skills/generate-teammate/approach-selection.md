# Phase 2-3: Work Decomposition & Approach Selection (Detail)

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
