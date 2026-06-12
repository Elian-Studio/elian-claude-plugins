# Team Patterns

> **Read first — these patterns describe Agent Team *shapes*, not a recommendation to use a team.**
> The default is still the cheapest approach that works (**Direct < Subagent < Agent Team**; see
> [approach-selection.md](approach-selection.md#economic-viability-gate)). For the "multi-perspective"
> patterns below (Research / Design / Strategy / Review / Documentation), the empirically safer and
> cheaper default is **independent Subagents — one per lens — followed by a single synthesizing
> agent**, which mirrors how production multi-agent research systems are actually built. Reach for a
> *communicating* Agent Team only when the lenses must reconcile **in real time** to converge on one
> shared artifact (e.g. BE↔FE API-contract negotiation). Evidence: [references/execution-evidence.md](references/execution-evidence.md).

## Pattern Catalog

### 1. Implementation Team

**Suitable for**: new project setup, fullstack feature development, parallel module-by-module build.

```
┌──────────────────────────────────────────────────┐
│ Lead (coordinator, delegate mode)                │
├──────────┬──────────┬──────────┬─────────────────┤
│ frontend │ backend  │ infra    │ tester          │
│ UI/pages │ API/svc  │ DB/conf  │ tests / verify  │
└──────────┴──────────┴──────────┴─────────────────┘
```

| Role | subagent_type | Owned area |
|------|---------------|------------|
| frontend-dev | frontend-architect | src/components/, src/pages/, src/styles/ |
| backend-dev | backend-architect | src/api/, src/services/, src/models/ |
| infra-dev | devops-architect | docker/, config/, scripts/ |
| tester | quality-engineer | tests/, __tests__/ |

**Parallel execution example**:
```
frontend-dev (UI build)        ─┐
backend-dev  (API build)       ─┤ parallel
infra-dev    (env setup)        ─┘
         │
tester (integration tests)     ← after backend, frontend complete
```

---

### 2. Research Team

**Suitable for**: new project design, technology selection, problem-solving exploration.

```
┌──────────────────────────────────────────────────┐
│ Lead (synthesizer)                               │
├───────────────┬───────────────┬──────────────────┤
│ ux-researcher │ architect     │ devil-advocate   │
│ user lens     │ technical lens│ adversarial lens │
└───────────────┴───────────────┴──────────────────┘
```

| Role | subagent_type | Analysis lens |
|------|---------------|---------------|
| ux-researcher | requirements-analyst | User experience, workflow, accessibility |
| architect | system-architect | Technical architecture, scalability, performance |
| devil-advocate | general-purpose | Counterarguments, edge cases, risks |

**Default to Subagents + single synthesizer**: run one independent Subagent per lens, then have a
single agent synthesize. This is cheaper, lower-risk, and matches how production research systems
are built. Use a *communicating* Research Team (the shape above) **only** when the lenses must
rebut each other in real time to converge — and even then, the synthesis itself stays with one
lead in a single pass (collaborative writing breeds conflicting decisions).

---

### 3. Review Team

**Suitable for**: code review, security audit, quality check.

```
┌──────────────────────────────────────────────────┐
│ Lead (aggregator)                                │
├────────────┬────────────┬────────────┬───────────┤
│ security   │ quality    │ perf       │ test      │
│ sec lens   │ qual lens  │ perf lens  │ test lens │
└────────────┴────────────┴────────────┴───────────┘
```

| Role | subagent_type | Analysis lens |
|------|---------------|---------------|
| security-reviewer | security-engineer | Security vulnerabilities |
| quality-reviewer | general-purpose | Code quality, SOLID |
| perf-reviewer | performance-engineer | Performance bottlenecks |
| test-reviewer | quality-engineer | Test coverage |

**Note**: when reviewers don't need to communicate with each other, **Subagents (Agent tool)** are more efficient. Use a Review Team only when reviewers must reconcile conflicting recommendations.

---

### 4. Design Team

**Suitable for**: system architecture design, API design, DB schema design, UX / UI design.

#### Variant A — Technical design

```
┌──────────────────────────────────────────────────┐
│ Lead (decision maker)                            │
├──────────────┬──────────────┬────────────────────┤
│ architect    │ domain-expert│ critic             │
│ structural   │ domain rules │ feasibility check  │
└──────────────┴──────────────┴────────────────────┘
```

| Role | subagent_type | Analysis lens |
|------|---------------|---------------|
| architect | system-architect | Technical architecture, pattern selection |
| domain-expert | Explore | Existing codebase analysis, domain rules |
| critic | devil-advocate | Complexity, maintainability, tradeoffs |

#### Variant B — Product / UX design

```
┌──────────────────────────────────────────────────┐
│ Lead (decision maker)                            │
├──────────────┬──────────────┬────────────────────┤
│ ui-ux        │ ux-researcher│ requirements       │
│ visual / IA  │ user evidence│ scope / criteria   │
└──────────────┴──────────────┴────────────────────┘
```

| Role | subagent_type | Analysis lens |
|------|---------------|---------------|
| ui-ux | ui-ux-designer | Visual hierarchy, components, tokens, a11y |
| ux-researcher | ux-researcher | User behavior, personas, usability evidence |
| requirements | requirements-analyst | Acceptance criteria, edge cases, scope |

---

### 5. Documentation Team

**Suitable for**: documentation overhaul, API reference rewrite, onboarding-doc rebuild, release-note polish across multiple components.

```
┌──────────────────────────────────────────────────┐
│ Lead (editorial direction)                       │
├──────────────┬──────────────┬────────────────────┤
│ tech-writer  │ architect    │ domain expert      │
│ docs author  │ source truth │ accuracy check     │
└──────────────┴──────────────┴────────────────────┘
```

| Role | subagent_type | Responsibility |
|------|---------------|----------------|
| tech-writer | technical-writer | Voice, structure, examples, editorial flow |
| architect | system-architect | Architectural truth, ADR cross-reference |
| domain-expert | Explore or backend-architect / frontend-architect | Verify code-level claims |

**Note**: when writers can work independently across separate doc sets (no overlap), Subagents are more efficient. Use Documentation Team when docs cross-reference each other and require editorial consistency.

---

### 6. Strategy Team

**Suitable for**: launch planning, positioning decisions, build-vs-buy, market entry, pricing strategy.

```
┌──────────────────────────────────────────────────┐
│ Lead (decision maker)                            │
├──────────────┬──────────────┬────────────────────┤
│ marketing    │ business     │ devil-advocate     │
│ positioning  │ economics    │ assumption stress  │
└──────────────┴──────────────┴────────────────────┘
```

| Role | subagent_type | Analysis lens |
|------|---------------|---------------|
| marketing | marketing-strategist | Positioning, JTBD, GTM, channels |
| business | business-analyst | Unit economics, ROI, market sizing, pricing |
| devil-advocate | devil-advocate | Pre-mortem, assumption testing, ethical lens |
| (optional) ux-researcher | ux-researcher | User evidence backing claims |

**Default to Subagents + single synthesizer**: one independent Subagent per lens (marketing /
business / risk), then a single lead synthesizes the decision memo with falsifiable success
criteria. Escalate to a *communicating* Strategy Team only when the tradeoffs must be debated in
real time to converge — the synthesis still stays single-author.

---

### 7. Focused Team

**Suitable for**: large parallel work in a single layer (e.g., migrating 10 components in parallel).

```
┌──────────────────────────────────────────────────┐
│ Lead (distributor + integrator)                  │
├─────────┬─────────┬─────────┬────────────────────┤
│ worker1 │ worker2 │ worker3 │ ...                │
│ mod A   │ mod B   │ mod C   │                    │
└─────────┴─────────┴─────────┴────────────────────┘
```

All workers use the same `subagent_type`. Each owns a different file / module.

---

### 8. Hybrid Patterns

**Suitable for**: composite work with phases of different character (explore + design + build).

A hybrid pattern is not a single pattern but a **meta-pattern that combines different patterns / approaches per phase**.

#### Common combinations

> **Caution: the examples below are not fixed patterns.** Each phase's approach is decided by characteristic analysis. The same "explore → design → build" structure can map to different combinations depending on characteristics.

| Pattern Name | Phase Composition Example | Suitable For |
|--------------|---------------------------|--------------|
| **Explore → Design → Build** | {by characteristics} → {by characteristics} → {by characteristics} | Extending existing code, adding new variants |
| **Explore → Build → Verify** | {by characteristics} → {by characteristics} → {by characteristics} | Large refactors with multi-perspective review |
| **Design → Build** | {by characteristics} → {by characteristics} | Greenfield feature from design to build |
| **Explore → Design** | {by characteristics} → {by characteristics} | When the design document is the deliverable |

#### Hybrid Triggers

If **any** of the following holds, consider hybrid:

1. Work decomposes into 2+ phases (explore → design → build, etc.)
2. Per-phase optimal approach differs (per characteristic analysis)
3. **Cross-layer API contract** is decided in the design phase, but build is independent per layer
4. Preceding phase results affect the next phase's direction

#### Example 1: Independent exploration → multi-perspective design → independent build (Subagent → Agent Team → Subagent)

When exploration is independent (BE/FE current state separately) and design needs coordination:

```
Phase A: Explore (Subagent parallel)              ← Independent, gather results
├── Explore: BE API + DTO + Service analysis
└── Explore: FE pages + components analysis
         │
Phase B: Design (Agent Team — Design / Research)  ← Multi-perspective debate
├── UI/UX designer: variant preview UI, user flow
├── FE engineer: component structure, integration with existing code
├── BE engineer: API extension design, DTO structure
└── Output: design.md + api-spec.md
         │
Phase C: Build (Subagent parallel)                ← Files separated, no debate
├── Task: BE API extension (per design doc)
└── Task: FE UI build (per design doc)
```

#### Example 2: Multi-perspective exploration → independent build (Agent Team → Subagent)

When exploration itself is multi-perspective (UX / architecture / domain) and findings need cross-validation:

```
Phase A: Explore (Agent Team — Research)          ← Multi-perspective, cross-validation
├── UX researcher: user flow, current UX issues
├── Architect: technical structure, dependencies, scalability
├── Domain expert: business rules, edge cases
└── Output: exploration report (cross-validated)
         │
Phase B: Build (Subagent parallel)                ← Based on exploration, independent build
├── Task: BE feature build
└── Task: FE UI build
```

---

## Pattern Selection Decision Tree

```
Requirements analysis
    │
    ├── 1. Decompose work into phases (explore / design / build / verify)
    │
    ├── 2. Are there 2+ phases with different character?
    │   ├── Yes → evaluate each phase independently (consider hybrid)
    │   │   │
    │   │   ├── Per phase: multi-perspective debate needed?
    │   │   │   ├── Yes → that phase: Agent Team
    │   │   │   └── No → that phase: Subagent or direct execution
    │   │   │
    │   │   └── Combine per-phase decisions → hybrid strategy
    │   │
    │   └── No → single approach decision (below)
    │
    ├── 3. Single-phase case:
    │   │
    │   ├── Inter-agent debate / rebuttal needed?
    │   │   ├── Yes → Research Team or Design Team
    │   │   └── No
    │   │       ├── Cross-layer change? (frontend + backend + DB)
    │   │       │   ├── Yes → Implementation Team
    │   │       │   └── No
    │   │       │       ├── Same pattern repeated?
    │   │       │       │   ├── Yes → Focused Team
    │   │       │       │   └── No
    │   │       │       │       ├── Independent perspective analysis?
    │   │       │       │       │   ├── Yes → Review Team
    │   │       │       │       │   └── No → Subagent or direct execution
    │   │       │       │       └──
    │   │       │       └──
    │   │       └──
    │   └──
    └──
```

### Core Principle

> **Per-phase independent evaluation takes priority over a single overall judgment.**
>
> Judging composite work by "file count" or "layer" alone misses the multi-perspective debate
> needed in the design phase. Always decompose into phases first, then evaluate each phase's
> characteristics independently.

## Teammate Count Guide

| Work Scale | Recommended Teammate Count | Reason |
|------------|---------------------------|--------|
| Small (3~5 tasks) | 2 | Minimize coordination overhead |
| Medium (6~15 tasks) | 3 | 5~6 tasks per teammate is optimal |
| Large (16+ tasks) | 4~5 | Coordination cost spikes beyond 5 |

## subagent_type Selection Guide

### Built-in (no definition needed)

| Work Characteristic | Recommended subagent_type | Reason |
|---------------------|---------------------------|--------|
| Code exploration / search only | Explore | Read-only optimized; Haiku model (fast, cheap) |
| Plan-mode research | Plan | Read-only; runs during plan mode |
| General implementation | general-purpose | Universal, fits most work |

### Engineering / build (plugin-bundled)

| Work Characteristic | Recommended subagent_type | Reason |
|---------------------|---------------------------|--------|
| System design / architecture | system-architect | ADRs, domain modeling, observability |
| Security audit | security-engineer | OWASP, threat modeling, AI / cloud security |
| Performance | performance-engineer | Profiling, load testing, regression prevention |
| Frontend | frontend-architect | Framework-agnostic (React / Vue / Angular / Svelte / Solid) |
| Backend | backend-architect | Multi-stack (Spring / Node / Python / Ruby / Go / .NET) |
| Test / quality | quality-engineer | Unit / integration / E2E strategy and coverage |
| Infra / DevOps | devops-architect | Docker, K8s, Terraform, CI / CD, secrets |
| Requirements / PM | requirements-analyst | PRDs, acceptance criteria, story slicing |

### Design / research / strategy (plugin-bundled)

| Work Characteristic | Recommended subagent_type | Reason |
|---------------------|---------------------------|--------|
| UI / UX design | ui-ux-designer | Tokens, components, interaction, a11y from design lens |
| Documentation | technical-writer | README, API docs, tutorials, runbooks |
| User research | ux-researcher | Interviews, personas, journey maps, usability |
| Marketing / positioning | marketing-strategist | Positioning, JTBD, GTM, content strategy |
| Business / strategy | business-analyst | Unit economics, ROI, decision frameworks |
| Adversarial review / pre-mortem | devil-advocate | Assumption challenge, ethical lens, bias detection |
