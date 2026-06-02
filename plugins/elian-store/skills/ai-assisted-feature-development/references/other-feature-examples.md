# Other Feature Examples

Use these examples to calibrate phase depth and review focus.

## Payment Capture

Risk: high.

Run: Phase 1-9.

Key concerns:

- Idempotency.
- Amount and currency correctness.
- Authorization.
- Audit trail.
- Retry policy.
- External provider failures.
- Data privacy.

Required tests:

- Successful capture.
- Duplicate request is idempotent.
- Provider timeout.
- Provider decline.
- Partial or mismatched amount is rejected.
- Unauthorized user cannot capture.

Block merge if idempotency, audit, or failure handling is unspecified.

## Order Cancellation

Risk: high when inventory, refunds, fulfillment, or notifications are involved.

Run: Phase 1-9, with DDD if cancellation policy is complex.

Key concerns:

- Cancellation eligibility.
- Inventory release.
- Refund policy.
- Notification timing.
- Race conditions with shipment.
- User-visible status.

Required tests:

- Eligible order cancels.
- Shipped order cannot cancel.
- Double cancellation is safe.
- Refund and inventory behavior match policy.
- User-visible status updates correctly.

Block merge if policy is guessed or status transitions are inconsistent.

## File Upload

Risk: medium or high depending on security.

Run: Phase 1, 3, 5, 6, 7, 8. Add Phase 4 if upload state is domain-significant.

Key concerns:

- File size.
- Type validation.
- Malware scanning policy.
- Storage location.
- Access control.
- Retry/resume behavior.
- Error states.

Required tests:

- Allowed file uploads.
- Disallowed type fails.
- Oversized file fails.
- Unauthorized access fails.
- Empty/error states display correctly.

Block merge if validation or access policy is missing.

## Search

Risk: low to medium.

Run: Phase 1, 2, 3, 5, 6, 7, 8.

Key concerns:

- Query parsing.
- Empty query behavior.
- Ranking.
- Pagination.
- Performance.
- Permission filtering.

Required tests:

- Normal query returns expected results.
- Empty query behavior is defined.
- Unauthorized results are hidden.
- Pagination works.
- Slow query limit or timeout is defined.

Block merge if permission filtering is not tested.

## Post Creation

Risk: low to medium.

Run: Phase 1, 2, 3, 5, 6, 7, 8.

Key concerns:

- Draft versus publish.
- Validation.
- Permission.
- Rich text or markdown sanitization.
- Attachments.
- Notifications.

Required tests:

- Valid post creates.
- Missing required fields fail.
- Unauthorized user cannot create.
- Sanitization prevents unsafe content.
- Draft/publish state is correct.

Block merge if content sanitization or permission is undefined.
