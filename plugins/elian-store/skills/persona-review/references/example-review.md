# Persona Review Examples

These examples show direction, not a fixed output template. Persona reviewers should keep their native shape and avoid shared scorecards.

## Single Persona Example

Request:

```text
/persona-review docs/feature/spec.md --persona evans --depth quick
```

Good output:

```markdown
## Evans Review

The model is using implementation language where it should expose domain language.

The strongest signal is that "status update" is doing three different jobs:
- user-visible lifecycle state
- fulfillment state
- payment state

Those are not the same invariant. If they stay in one field, the next feature will either over-protect simple transitions or under-protect refund and shipment cases.

Suggested model pressure:
- Name the lifecycle states in business language.
- Separate payment settlement from fulfillment progress.
- Decide whether cancellation is an aggregate invariant or an application-service policy.

Next move: define the one sentence invariant that must always hold when an order is cancelled.
```

Why this works:

- It starts with judgment.
- It uses Evans' modeling lens.
- It does not score every pressure question.
- It ends with one next move.

## Multi-Persona Example

Request:

```text
/persona-review docs/queue-design.md --persona daniel,dean --depth deep
```

Good output:

```markdown
## daniel

The operational gap is not the queue. It is the missing owner for the retry policy.

If a message fails after the third attempt, the design says "manual handling" but does not say who sees it, how quickly, or what data they need to act. That means the system is automated only until the first non-happy-path case.

Next move: define the failure inbox and owner before choosing retry counts.

## dean

The scale risk is tail amplification. The design retries every failed message with the same delay, so a downstream outage can create a synchronized retry wave.

Add jitter, cap concurrency, and define dead-letter behavior. Otherwise the queue can make recovery slower than the original outage.

Next move: model the retry distribution for a 10-minute downstream outage.

## Lead synthesis

- Common risk: failure handling is underspecified.
- Conflict: Daniel wants ownership defined first; Dean wants retry distribution modeled first.
- Next decision: decide whether operational ownership or retry mechanics is the immediate blocker.
```

## Bad Example

```markdown
| Question | Score | Comment |
|---|---|---|
| Is the domain model clear? | 7/10 | Maybe |
| Is it scalable? | 8/10 | Looks fine |
```

Why this fails:

- It flattens persona lenses into a scorecard.
- It gives weak evidence.
- It does not preserve each persona's judgment style.

## Handoff Example

When review should lead to implementation, emit a handoff payload:

```markdown
(handoff -> improve docs/queue-design.md)
- persona: dean
- judgment: retry behavior can amplify a downstream outage
- change intent: add jitter, concurrency cap, and dead-letter policy
- evidence: queue design retries all failures with the same delay
- risks to preserve: do not hide failed messages from operators
- out of scope: do not implement queue code in this review
```
