# Example 4: Product Launch Strategy (Non-Dev)

A **non-engineering scenario** showing that `/generate-teammate` is not just for code work. Demonstrates the Strategy Team pattern with marketing-strategist, business-analyst, ux-researcher, and devil-advocate.

---

## Input

```
/generate-teammate We're launching a B2B SaaS analytics tool in 6 weeks.
Need positioning, pricing, GTM channels, and risks identified.
No code work — strategy and decision deliverables only.
```

---

## Phase 1: Request Analysis

```typescript
{
  domain: 'strategy / launch',
  techStack: [],   // not a code task
  deliverables: ['positioning brief', 'pricing model', 'GTM plan', 'risk register', 'launch sequence'],
  constraints: ['6-week timeline', 'B2B SaaS analytics', 'pre-launch'],
  parallelizableUnits: [
    'competitive teardown',
    'pricing model',
    'positioning + messaging',
    'channel plan',
    'pre-mortem'
  ]
}
```

---

## Phase 2: Decomposition

```
┌────────────┬────────────────────────────────┬──────────────────────────────────────┐
│   Phase    │            Content              │           Characteristics            │
├────────────┼────────────────────────────────┼──────────────────────────────────────┤
│ A: Research │ Competitive analysis, customer │ Independent, factual gathering       │
│            │ interviews, market sizing       │                                      │
├────────────┼────────────────────────────────┼──────────────────────────────────────┤
│ B: Decide  │ Position, price, channels      │ Real-time tradeoff debate;           │
│            │                                 │ marketing / business / risk lenses   │
│            │                                 │ collide and must reconcile           │
├────────────┼────────────────────────────────┼──────────────────────────────────────┤
│ C: Plan    │ Launch sequence, content       │ Independent execution per            │
│            │ calendar, owner per item       │ workstream after decisions land      │
└────────────┴────────────────────────────────┴──────────────────────────────────────┘

Phase dependencies: A → B → C
```

---

## Phase 3: Approach Decision

```
┌─────────────┬───────────────┬───────────────────┬───────────────┬──────────────────────────────────┐
│    Phase    │  Agent Team   │    Subagent       │   Direct      │              Reason              │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ A: Research │ Unfit         │ ★ Fit             │ Possible      │ Each researcher gathers facts in │
│             │               │                   │               │ their lane independently         │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ B: Decide   │ ★ Fit         │ Unfit             │ Unfit         │ Tradeoffs across positioning,    │
│             │               │                   │               │ price, risk MUST be debated;     │
│             │               │                   │               │ cannot be Subagent-aggregated    │
├─────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ C: Plan     │ Unfit         │ ★ Fit             │ Possible      │ Workstreams independent after    │
│             │               │                   │               │ decision; each owns separate doc │
└─────────────┴───────────────┴───────────────────┴───────────────┴──────────────────────────────────┘

Strategy: hybrid — Subagent (research) → Agent Team (decision) → Subagent (planning)
```

---

## Phase 4-5: Team & Task Design

### Phase A — Subagents (parallel research)

| Subagent | subagent_type | Task |
|----------|---------------|------|
| competitor-research | marketing-strategist | Teardown of 3-5 closest competitors. Output: positioning matrix, pricing comparison, channel observations. |
| user-research | ux-researcher | Synthesize what we know about target users. JTBD, willingness-to-pay signals, current alternatives. |
| market-sizing | business-analyst | Bottom-up TAM / SAM / SOM. Identify killer assumptions. |

Outputs feed into Phase B as reference docs.

### Phase B — Agent Team (Strategy Team)

```
Team: launch-strategy
Pattern: Strategy Team
Teammates: 4

| Role        | subagent_type        | Lens                                          |
|-------------|----------------------|-----------------------------------------------|
| positioning | marketing-strategist | Position, message hierarchy, channel mix      |
| economics   | business-analyst     | Pricing, unit economics, ROI, decision logic  |
| user-voice  | ux-researcher        | "Does this match what users actually want?"   |
| critic      | devil-advocate       | Pre-mortem, assumption excavation, ethics     |
```

Tasks (each leads to a section in the launch brief):

| Task | Notes |
|------|-------|
| Author positioning statement | positioning leads, others react |
| Decide pricing model + tiers | economics leads, positioning + critic react |
| Decide top 3 channels | positioning + economics co-author |
| Risk register | critic leads, all contribute |
| Pre-launch / launch / post-launch sequence | positioning leads |

Deliverable: `docs/launch/strategy.md`

### Phase C — Subagents (parallel execution planning)

After the strategy doc is finalized:

| Subagent | subagent_type | Task |
|----------|---------------|------|
| content-plan | technical-writer | Author 8-week content calendar based on strategy.md positioning |
| landing-copy | marketing-strategist | Draft landing page copy aligned to messaging hierarchy |
| sales-deck | marketing-strategist | Draft deck for outbound channel |
| risk-monitoring | devops-architect | Set up monitoring / alerts for launch-critical metrics |

---

## Phase 6: Confirmation Output

```
Hybrid execution plan:

Phase A: Research (Subagent parallel)
├── marketing-strategist: competitor teardown
├── ux-researcher: user / JTBD synthesis
└── business-analyst: market sizing
    ↓ pass research results

Phase B: Decide (Agent Team — Strategy Team)
├── marketing-strategist (positioning lead)
├── business-analyst (economics)
├── ux-researcher (user voice)
└── devil-advocate (pre-mortem)
    Deliverable: docs/launch/strategy.md
    ↓ pass strategy

Phase C: Plan (Subagent parallel)
├── technical-writer: content calendar
├── marketing-strategist: landing copy
├── marketing-strategist: sales deck
└── devops-architect: launch metric monitoring
```

---

## Phase 7: Execution (sketch)

```typescript
// Phase A
const [competitorNotes, userNotes, marketNotes] = await Promise.all([
  Agent({ subagent_type: 'marketing-strategist', prompt: 'Teardown of 3-5 closest competitors. Output positioning matrix.' }),
  Agent({ subagent_type: 'ux-researcher',        prompt: 'Synthesize known target user JTBD, willingness-to-pay signals.' }),
  Agent({ subagent_type: 'business-analyst',     prompt: 'Bottom-up TAM/SAM/SOM. Surface killer assumptions.' }),
]);

// Phase B
TeamCreate({ team_name: 'launch-strategy', description: 'Decide positioning, pricing, channels, risk for 6-week launch' });
// ...
Agent({
  subagent_type: 'marketing-strategist',
  team_name: 'launch-strategy',
  name: 'positioning',
  prompt: spawnPromptPositioning({ competitorNotes, userNotes, marketNotes }),
});
Agent({
  subagent_type: 'business-analyst',
  team_name: 'launch-strategy',
  name: 'economics',
  prompt: spawnPromptEconomics({ marketNotes }),
});
Agent({
  subagent_type: 'ux-researcher',
  team_name: 'launch-strategy',
  name: 'user-voice',
  prompt: spawnPromptUserVoice({ userNotes }),
});
Agent({
  subagent_type: 'devil-advocate',
  team_name: 'launch-strategy',
  name: 'critic',
  prompt: spawnPromptCritic(),
});

// ... wait for docs/launch/strategy.md, then Phase C in parallel
```

---

## Spawn prompt example (critic)

```
You are the critic on the launch-strategy team.

[ROLE]
Adversarial review and pre-mortem on every decision the team makes.

[OWNED FILES]
- docs/launch/risks.md (you author)
- May comment on docs/launch/strategy.md sections via SendMessage

[TASK]
1. Read other teammates' draft sections as they appear.
2. For each major decision (positioning, pricing, channel mix), run the pre-mortem protocol:
   - Imagine the launch fails 6 months later. Why?
   - Excavate the killer assumptions behind the decision.
   - Score risks (severity × likelihood).
3. For each risk, produce: prevent / monitor / accept recommendation.
4. Surface biases: confirmation bias on competitor data, optimism bias on conversion, etc.
5. Apply the ethical lens: who could this harm? Disproportionate impact on any segment?

[OUTPUT]
docs/launch/risks.md with:
- Pre-mortem failure modes (≥ 5)
- Killer assumptions (per major decision)
- Risk register (severity × likelihood × mitigation)
- Bias audit (what might the team be missing?)
- Falsifiable success criteria (e.g., "≥ 3% landing-page conversion to retain pricing model")

[CONSTRAINTS]
- Steel-man before attacking. If you can't restate the position generously, you don't understand it.
- Every critique includes a falsifiable test or alternative. "I disagree" is not enough.
- Severity matters: don't treat a typo and a pricing-model risk as equal.

[COMMUNICATION]
- For each major draft from another teammate, send a critique within 1-2 turns.
- For CRITICAL risks, broadcast immediately.
- Acknowledge when an argument survives scrutiny — adversarial ≠ contrarian.
```

---

## Why hybrid here

- **Phase A** (research) is independent fact-gathering. Subagents are the right tool — competitor teardown doesn't depend on user research mid-flight.
- **Phase B** (decision) is exactly where Agent Team shines. Marketing wants premium positioning; business says market won't pay it; user-voice says current alternatives are free; critic flags assumption that we have channel access. These tensions must be resolved in real-time debate, not in series.
- **Phase C** (planning) is independent again. Content calendar doesn't need to talk to landing copy mid-draft.

This is the canonical "diverge → converge → diverge" hybrid shape, applied to a non-engineering domain.

---

## What this example proves

`/generate-teammate` is not a fullstack-only tool. The same Phase decomposition + per-Phase approach decision applies to:

- Product launches
- Strategic decisions (build / buy / partner)
- Documentation overhauls
- Brand / positioning workshops
- Research synthesis
- Crisis response (incident commander pattern)

The 14 plugin-bundled agents cover engineering, design, research, marketing, business, and adversarial lenses, so non-code teams are first-class.
