# Example 2: Competing-Hypothesis Debugging

A single-phase **Agent Team** scenario. Multiple investigators argue different theories and rebut each other. Demonstrates the Research Team pattern adapted for debugging.

This is the classic "Sequential investigation suffers from anchoring" use case from the official docs.

---

## Input

```
/generate-teammate The WebSocket connection drops after the first message in production.
Cannot reproduce locally. We've spent two days on it.
Spawn investigators to compete on different hypotheses and challenge each other.
```

---

## Phase 1: Request Analysis

```typescript
{
  domain: 'backend',
  techStack: ['WebSocket', 'production-only'],
  deliverables: ['root cause identification', 'reproducer', 'fix recommendation'],
  constraints: ['cannot reproduce locally', 'production traffic only', 'time-sensitive'],
  parallelizableUnits: ['hypothesis A', 'hypothesis B', 'hypothesis C', 'hypothesis D']
}
```

---

## Phase 2: Work Phase Decomposition

```
┌────────────┬────────────────────────────────┬──────────────────────────────────────┐
│   Phase    │            Content              │           Characteristics            │
├────────────┼────────────────────────────────┼──────────────────────────────────────┤
│ A: Investigate │ 4 hypotheses in parallel    │ Multi-perspective, mutual rebuttal,  │
│            │ Hypotheses must compete         │ findings affect each other           │
└────────────┴────────────────────────────────┴──────────────────────────────────────┘

Phase dependencies: single phase
```

---

## Phase 3: Approach Decision

```
┌────────────────┬───────────────┬───────────────────┬───────────────┬──────────────────────────────────┐
│     Phase      │  Agent Team   │    Subagent       │   Direct      │              Reason              │
├────────────────┼───────────────┼───────────────────┼───────────────┼──────────────────────────────────┤
│ A: Investigate │ ★ Fit         │ Unfit             │ Unfit         │ Mutual rebuttal is the value.    │
│                │               │                   │               │ Sequential anchors on first      │
│                │               │                   │               │ hypothesis. Subagent can't talk. │
└────────────────┴───────────────┴───────────────────┴───────────────┴──────────────────────────────────┘

Strategy: single — Agent Team (Research Team adapted for debugging)
```

> **Why not Subagents in parallel?**
> Subagents can't see each other's findings during execution. If teammate A rules out cache expiry and teammate B builds an argument depending on cache being the cause, B wastes effort. With Agent Team, B sees A's evidence in real time and pivots.

---

## Phase 4-5: Team & Task Design

```
Team: ws-debug
Pattern: Research Team (debugging variant)
Teammates: 5 (4 hypotheses + 1 critic)

| Role           | subagent_type    | Hypothesis                              |
|----------------|------------------|------------------------------------------|
| h1-cache       | general-purpose  | Cache expiry causing reconnect loop     |
| h2-concurrency | general-purpose  | Race condition on session-init handler  |
| h3-network     | devops-architect | LB / proxy timing-out idle connections  |
| h4-payload     | backend-architect| Server-side payload limit triggering close |
| critic         | devil-advocate   | Pre-mortem each hypothesis; surface bias |
```

Tasks (the lead creates one finding-doc per hypothesis):

| Task | Owner |
|------|-------|
| Investigate cache-expiry theory | h1-cache |
| Investigate concurrency theory | h2-concurrency |
| Investigate network / LB theory | h3-network |
| Investigate payload theory | h4-payload |
| Stress-test each theory's evidence | critic |
| Synthesize findings into root-cause memo | (lead) |

No file conflicts: each teammate writes to `docs/debug/ws-drop/h1-cache.md`, `h2-concurrency.md`, etc.

---

## Phase 6: Confirmation Output

```
Hybrid execution plan:

Phase A: Investigate (Agent Team — Research Team)
├── h1-cache (general-purpose) — write h1-cache.md with evidence
├── h2-concurrency (general-purpose) — write h2-concurrency.md with evidence
├── h3-network (devops-architect) — write h3-network.md with evidence
├── h4-payload (backend-architect) — write h4-payload.md with evidence
└── critic (devil-advocate) — challenge each, surface biases

    Cross-talk: SendMessage between teammates as evidence accumulates.
    "I ruled out X" → other teammates pivot away from depending on X.
    "I found a clue that contradicts Y" → Y's owner addresses or concedes.

Lead synthesizes: docs/debug/ws-drop/root-cause.md
```

---

## Phase 7: Execution (sketch)

```typescript
TeamCreate({ team_name: 'ws-debug', description: 'Compete hypotheses on WebSocket drop' });

['h1-cache', 'h2-concurrency', 'h3-network', 'h4-payload'].forEach(role => {
  TaskCreate({ subject: `Investigate ${role}`, description: '...' });
});
TaskCreate({ subject: 'Critique all hypotheses', description: '...' });

// Spawn each teammate. The lead instructs them to read other teammates' findings
// as they're written, and to challenge them via SendMessage.
Agent({
  subagent_type: 'general-purpose',
  team_name: 'ws-debug',
  name: 'h1-cache',
  prompt: spawnPromptH1(),  // see below
});
// ... etc for h2, h3, h4, critic
```

---

## Spawn prompt example (h1-cache)

```
You are h1-cache on the ws-debug team.

[ROLE]
Investigate the hypothesis: "Cache expiry on the auth-token cache causes the WebSocket
to drop after the first message because the server invalidates the session."

[OWNED FILES]
- docs/debug/ws-drop/h1-cache.md (you author your findings here)
- Read-only: src/, logs/, deploy config

[TECH STACK]
WebSocket server (identify the framework from package.json / pom.xml).
Read production-relevant config and recent code changes.

[TASK]
1. Investigate the hypothesis in your dedicated finding doc.
2. Look for: cache TTL settings, session-token lifecycle, recent cache-related deploys, log patterns at the timing of drops.
3. Build evidence both supporting AND refuting your hypothesis. Don't just confirm; falsify.
4. As other teammates write their findings, READ them. If their evidence undermines your hypothesis, acknowledge and pivot. If their evidence is wrong, push back with SendMessage.

[INTERFACES]
- h2-concurrency: if both cache and concurrency could be at play, coordinate.
- critic: expect challenges. Be ready to defend with evidence, not opinion.
- All teammates: cross-read each other's docs. Update yours when others' evidence applies.

[REFERENCE]
- Public incident notes: {paste any}
- Production log access: {how to query}

[DEFINITION OF DONE]
- h1-cache.md updated with: hypothesis statement, supporting evidence, refuting evidence, conclusion (confirmed / refuted / partial).
- Engaged with at least 2 other teammates' findings via SendMessage.
- If your hypothesis is refuted, say so explicitly. Pivoting fast is more valuable than being right.

[COMMUNICATION]
- Real-time challenges: SendMessage to the relevant teammate.
- Major findings: broadcast (affects everyone).
- Idle when waiting for evidence: that's fine, the lead will message you.
```

---

## Why this works

- **Sequential debugging anchors on the first hypothesis.** A single agent picks one theory and confirmation-biases its way through.
- **Subagents in parallel** would each work in isolation. They'd produce 4 separate confirmation-biased reports, with no cross-pollination.
- **Agent Team enables real-time rebuttal**. When h2 finds evidence ruling out concurrency, h1 sees it and refines its cache theory. When h4 finds the actual root cause (payload limit), the others pivot to support / refine.

The team converges on the truth faster than any individual investigator.
