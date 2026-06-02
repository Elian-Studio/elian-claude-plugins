# Before / After: Decision Card Authoring

This reference shows why decision-dashboard cards are authored as JSON and rendered through `create-document`.

## Before: Hand-Written HTML

Bad pattern:

```html
<div class="card" id="c1">
  <div class="card-title">#143 add NotificationRetryScheduler</div>
  <div class="info-box">
    notification_send_log rows with status=FAILED are lost.
  </div>
</div>
```

Problems:

- Internal identifiers leak to the decision-maker.
- One card takes too much HTML to edit safely.
- The author must remember every language gate manually.
- Product choices are hidden behind implementation terms.

## After: JSON With Schema Validation

Good pattern:

```json
{
  "card_id": "c1",
  "num": 1,
  "title": "Automatic resend for failed receipt notifications",
  "background": {
    "situation": "Seven paying users did not receive a receipt notification yesterday after temporary device delivery failures.",
    "pain": "Without a retry decision, users can wait 6 hours or request refunds because they do not know whether payment succeeded.",
    "divergence": "The choice decides whether recovery is automatic, operator-led, or user-triggered."
  },
  "judgment_question": "Should every user receive the receipt within 1 hour, or is a daily operator batch acceptable?",
  "options": [
    {
      "key": "A",
      "label": "Automatic resend - users receive receipts within 1 hour",
      "rec_badge": "<span class=\"rec-badge\">Recommended</span>"
    },
    {
      "key": "B",
      "label": "Operator batch - users wait around 6 hours"
    },
    {
      "key": "C",
      "label": "User-triggered retry - users request resend themselves"
    }
  ]
}
```

If a card includes `#143`, `*.class`, or snake_case table names, the schema blocks it before HTML is produced.

## Comparison

| Axis | Before | After |
|---|---|---|
| Authoring unit | Large HTML block | Small JSON card |
| Identifier blocking | Manual discipline | Schema gate |
| Rework cost | Edit HTML structure | Edit data field |
| Decision-maker view | Implementation terms leak | Product outcome language |
| Downstream use | Hard to parse | JSON can be persisted |

The main value is not speed. The main value is preventing malformed decision cards from being published.
