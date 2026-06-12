# Standing Rules — generate-teammate

These rules apply throughout the skill — not as one-time procedure steps but as ongoing behavior. Violations are bugs, not preferences.

## 1. Phase decomposition is non-optional — but it must not force a team

Even if the user describes a single task, run Phase decomposition **mentally**. Skipping the analysis
produces wrong-shape teams. But the analysis can — and often should — conclude **Direct**. Decomposing
a coherence-critical or sequential task into a team just because you decomposed it is
over-decomposition, a documented anti-pattern. Triage for an actual parallelism/reconciliation signal
first (see [approach-selection.md](../approach-selection.md#phase-20-delegation-triage-do-this-first)).

## 2. Per-phase independence beats whole-task judgment

Composite work has phases that prefer different approaches. Forcing one approach across the whole task is the most common failure mode.

## 3. The core question is "Do workers need to communicate with each other?"

From the official docs, refined by the cost-and-risk prior **Direct < Subagent < Agent Team**.
- **No** → Subagent (parallel, independent), or Direct if there is nothing to parallelize.
- **Yes, with handoff only** → Subagent chain (sequential), passing full artifacts not summaries.
- **Yes, but reconcilable after the fact** → independent Subagents (one per lens) + a single synthesizer. *This is the default for "multi-perspective" work.*
- **Yes, and they must converge in real time on one shared artifact** → Agent Team. **Last resort only** — it is the least-validated, highest-coordination-cost mode.

## 4. File ownership before parallelism

Two teammates editing the same file is a data race in disguise. Validate ownership separation **before** spawning, not after.

## 5. Minimum viable team

2 teammates beat 5 if 2 suffice. Coordination cost grows non-linearly past 5.

## 6. Always confirm with AskUserQuestion before spawning

The user owns the decision; the skill produces the recommendation. Never spawn without explicit gate.

## 7. Self-contained agents only

This skill's 14 routing agents work without external skills. Do not introduce dependencies on user-level skills the user may not have.

## 8. Spawn prompt is JSON-first

Since v2.6, spawn prompt content is authored as JSON and rendered via `create-document/scripts/render.py --template teammate-spawn`. This enforces all 7 slots (ROLE / OWNED FILES / TECH STACK / TASK / REFERENCE DOCS / INTERFACES / DOD / COMMUNICATION) and blocks vague language (`help build`, `do something`, `TODO`, `...`).

See [Phase 4-5 in SKILL.md](../SKILL.md#phase-4-team--task-design) for the procedure.

## 9. Cheaper-first prior, with an economic gate

Cost and coordination-risk rise sharply: **Direct < Subagent < Agent Team**. Default to the cheapest
approach that satisfies the phase. Before accepting any non-Direct approach, state its cost multiplier
(Direct 1× / Subagent ~N× / Agent Team ~15× + super-linear coordination) and confirm the parallel
benefit justifies it. If it does not, downgrade to Direct. Multi-agent is only economical for
high-value tasks — token spend alone explains most of any multi-agent "win."

## 10. Agent Team is a last resort, not a default for "debate"

It is the least-validated mode (no head-to-head benchmark shows inter-agent communication beating
independent subagents + a single synthesizer) and the highest-coordination-cost one (~31% of
multi-agent failures are inter-agent misalignment). Reserve it for genuine real-time reconciliation
on one shared artifact (e.g. BE↔FE API-contract negotiation).

## 11. File split ≠ semantic safety → integration reconciliation is mandatory

Disjoint file ownership prevents textual conflicts, not semantic ones (duplicate declarations, type
mismatches, broken cross-references at the seams). After any parallel write phase, a **single** agent
runs a cross-boundary build/typecheck over the merged surface and resolves seam conflicts. This is a
team-level Definition of Done, separate from each teammate's per-file DoD.

## 12. Single-agent synthesis, full-artifact handoffs

Coherence-critical artifacts (one design doc / report / schema) are authored by **one** agent in one
pass — never co-written. Across coherence-critical phase handoffs, pass the **full artifact**, not a
lossy summary, so the downstream agent does not silently re-decide and conflict.
