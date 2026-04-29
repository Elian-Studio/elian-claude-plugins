# Good decision card vs bad decision card

A BEFORE / AFTER pair that demonstrates the skill's LANGUAGE GATE / 3-sentence background skeleton / option-label rule / judgment-question rule **simultaneously, on a single card**.

This file is the reference Claude consults when authoring a decision card.

---

## Scenario

**Situation**: Push-notification delivery failures are accumulating in the notification system. We need to decide how to handle them.

---

## ❌ BAD — card that violates the rules

### Title
> Whether to introduce `NotificationRetryScheduler`

> ⚠ Violation: class name exposed in card title (LANGUAGE GATE).

### Background (info-box box-context)
> The `notification_log` table has rows with `send_status = FAILED` accumulating.
> Per requirement R6, we need a retry policy. Decision #38 is debating polling vs queue.
> Whether to introduce ShedLock has to be decided too.

> ⚠ Violations: table / column names (`notification_log`, `send_status`), requirement number (R6), decision number (#38), stack name (ShedLock) — the decision-maker can't understand without reading code.

### Judgment axis (info-box box-judge)
> Should we secure operational efficiency, or accept system simplicity?

> ⚠ Violation: abstract phrasing "secure X or accept Y" — the decision-maker cannot answer.

### Options
- **A. Generalize — introduce a `RetryScheduler` class + ShedLock + 5-minute cron**
- **B. Polling — add a `next_retry_dtm` column and poll**
- **C. Defer**

> ⚠ Violations:
> - Option A: class names / stack names / impl jargon (impl-term).
> - Option B: column name exposed.
> - Option C: "Defer" is decision avoidance, and there's no "Other (custom input)" option.

---

## ✅ GOOD — card that passes every rule

### Title
> Add automatic retry for failed push notifications

> ✓ Outcome-centered title, no internal identifiers.

### Background (info-box box-context, 3-sentence skeleton)
> Yesterday, of 100 users who paid, 7 didn't receive the receipt push (transient device errors on the recipient side).
> Right now a first-send failure means lost — the user doesn't know whether the payment went through, and refund requests come in (4 yesterday alone).
> This decision splits "automated retry" vs "ops-team manual handling".

> ✓ 1. What's happening now (user-perspective, concrete numbers 7 / 100).
> ✓ 2. Pain if no decision (4 refund requests).
> ✓ 3. Difference between options (retry vs manual).

### Judgment question (info-box box-judge)
> Should the user receive the receipt within 1 hour 100% of the time, or is it acceptable for the ops team to manually handle missed deliveries each day?

> ✓ Concrete question the decision-maker can answer directly (1 hour / 100% / manual handling).

### Options (1 rec-badge + mandatory "Other")
- **A. Switch to automatic retry — users get the receipt within 1 hour at the latest, ops manual handling drops to 0** [recommended]
- **B. Keep ops manual handling — once a day, ops collects misses and sends manually; users wait 6 hours on average**
- **C. Show the user a "send failed" notice with a "retry" button — user-triggered**
- **D. Other — fill in below**

> ✓ All end with "what becomes different" (user-perspective).
> ✓ "Other" is always the last option.

### Memo
> Empty (free input when D is selected).

---

## detail-panel (developer-rationale area) — internal identifiers allowed

The GOOD card's `detail-trigger` + `detail-panel` may carry the following (the decision-maker doesn't have to expand it):

```html
<div class="detail-trigger">▷ Show technical rationale</div>
<div class="detail-panel">
  <h4>Related code / schema</h4>
  <ul>
    <li>New class: NotificationRetryScheduler</li>
    <li>Add `retry_count`, `next_retry_dtm` to `notification_log`</li>
    <li>Refs: requirement R6, PRD decision #38</li>
    <li>Use ShedLock to prevent duplicates under multi-server deployments</li>
  </ul>
</div>
```

> This area is exempt from LANGUAGE GATE — the developer-rationale sandbox.

---

## Self-checklist (decidable in 5 minutes?)

After writing a card, all 6 must be ✓ before publishing:

- [ ] The decision-maker (PO / team lead) can understand every body without reading code or DB.
- [ ] Background includes at least one concrete user-or-admin-perspective scene of "what's happening now".
- [ ] Background includes at least one concrete number or scenario (e.g., "7 / 100", "4 refunds").
- [ ] Judgment question is directly answerable (yes / no or A / B form).
- [ ] Every option label ends in "what becomes different" (no impl verbs).
- [ ] Last option is "Other — fill in below" + at most one rec-badge.

If fewer than 5 / 6, rewrite the card.
