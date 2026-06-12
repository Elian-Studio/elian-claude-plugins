# Execution-Mode Evidence — why Direct < Subagent < Agent Team

This file is the empirical basis for the skill's execution-mode prior, the economic
viability gate, the integration-reconciliation step, and the single-agent-synthesis rule.
The headline message: **the choice is task-dependent, but it is not a free tie — there is a
strong cost-and-risk prior toward the cheapest approach that works.**

> Source strength is uneven — read the confidence column before leaning on any number.
> The strongest single thread (Anthropic's 90.2% / 15×) is a first-party, non-reproduced
> internal eval; the only controlled coding benchmark (CodeCRDT) is a single-author preprint;
> the most rigorous source (MAST) is peer-reviewed but *descriptive* (it catalogs failures,
> it does not prove multi-agent is worse on net).

## The three modes, mapped to evidence

### Subagent (parallel, independent, fire-and-forget)

| | |
|---|---|
| **GOOD** | Breadth-first, read-heavy, genuinely independent exploration; comparisons; map-reduce; multi-source gathering. Context isolation (each subagent gets a clean window) is the benefit. |
| **BAD** | Write-heavy, interdependent coding; small/simple tasks (over-decomposition → redundant duplicate work). Parallelism is **not** uniformly beneficial: a controlled coding study found anywhere from **+21% speedup to −39% slowdown** depending on component interdependence, and parallel agents that ran *faster* still produced **−7.7% code quality**. |
| **Sizing** | Scale to complexity: 1 agent for simple fact-finding, 2–4 for comparisons, 10+ only for genuinely complex research. |

### Agent Team (persistent agents communicating via messages + shared task list)

| | |
|---|---|
| **GOOD (narrow)** | Genuine real-time reconciliation where parties must converge on one shared interface — e.g. BE↔FE API-contract negotiation — or cross-perspective debate that must reach a single decision. |
| **BAD / RISKY** | Highest coordination cost (n agents → n(n−1)/2 interaction points; 4→6, 10→45 — super-linear). "Agents talking past each other" (inter-agent misalignment) is **~31% of measured multi-agent failures**. Conflicting implicit decisions across agents produce broken integrations. |
| **Honest caveat** | **This is the least-validated of the three modes.** No published head-to-head benchmark isolates the value of inter-agent *communication* itself against (a) independent subagents + a single synthesizer or (b) a single agent. Prefer it last; do not make it a default for "debate." |

### Direct (single agent, no delegation)

| | |
|---|---|
| **GOOD** | Most coding; "deep and narrow" coherence-critical work; synthesis and any long-form writing (one unified call); tasks needing full shared context; sequential dependencies; small tasks; whenever the ~15× cost is not justified. For coding specifically, the documented recommendation is a single-threaded linear agent. |
| **BAD** | Breadth-first research too large for one context window — that, and only that, is where fan-out clearly wins. |

## Cost and failure facts (cross-cutting)

- **Cost.** Multi-agent ≈ **15× the tokens of a plain chat** (single agent ≈ 4×). In browsing
  evals, **token spend alone explained ~80% of performance variance** — so a large share of the
  multi-agent "win" is just spending more compute. Only economical for high-value tasks.
- **Multi-agent frequently fails to beat single-agent.** Gains on popular benchmarks are "often
  minimal" (peer-reviewed). Defaulting to multi-agent is not justified.
- **File separation ≠ semantic safety.** Character-level merge can be made 100% conflict-free and
  still leave a **~5–10% semantic conflict rate** (duplicate declarations, type mismatches, broken
  cross-references) at the seams — measured at **20% for simple tasks, 80% for complex** — which
  requires a dedicated post-build reconciliation / evaluator step. This is *why* the skill's
  file-ownership rule is necessary but not sufficient.
- **Synthesis must be consolidated.** Collaborative writing introduces conflicting decisions;
  synthesis is best handled by a single main agent in one unified call.

## What was tested and *refuted* (do not lean on these)

- ❌ The clean "reads parallelize / writes conflict" dichotomy — refuted (1-2). The real axis is
  task **interdependence/coupling**, not read-vs-write.
- ❌ "Single agents recently beat multi-agent baselines by large margins" — refuted (0-3).
- ❌ "Most multi-agent breakdowns are single-agent spec flaws, not coordination" — refuted (0-3).

## Open questions (carried as honest unknowns)

1. No source gives a *measurable* coupling threshold predicting in advance whether a given coding
   task benefits from fan-out or is harmed by it.
2. No head-to-head benchmark isolates the value of inter-agent communication (Agent Team) vs.
   subagents-plus-synthesizer vs. single agent.
3. How much of the multi-agent research advantage is architecture vs. simply spending ~15× tokens?
4. Do these findings shrink as single-model capability and context windows grow?

## Sources

| Source | Type | Used for |
|--------|------|----------|
| [Anthropic — Building a multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | primary (first-party, non-reproduced) | 90.2% breadth-first win; 15× / 4× cost; 80% variance; complexity-scaled sizing; over-decomposition anti-pattern |
| [Cognition — Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) | primary (essay) | Share full traces not summaries; conflicting decisions; single-threaded linear agent for coding |
| [Cemri et al. — Why Do Multi-Agent LLM Systems Fail? (MAST), NeurIPS 2025](https://arxiv.org/abs/2503.13657) | peer-reviewed | 14 failure modes / 3 categories; inter-agent misalignment ~31%; minimal benchmark gains |
| [CodeCRDT (Pugachev, 2025)](https://arxiv.org/pdf/2510.18893) | preprint (single-author) | +21%/−39% task-dependent; +25% runtime / −7.7% quality; 5–10% semantic conflict rate |
| [LangChain — How and when to build multi-agent systems](https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems) | primary (vendor) | Synthesis consolidated in one agent; orchestrator-worker tradeoffs |

Verification: of 25 adversarially checked claims, 21 confirmed (≥2/3 votes), 4 killed. Source set:
19 fetched across 5 angles (broad/contrarian/practitioner/academic/cost).
