# Example Drift Report

Use this shape for Mode 1 `analyze`.

```markdown
# Skill Drift Report

Scope:
- Base: main...HEAD
- Changed files: 12
- Project skill root: .claude/skills

## Summary

| Class | Count |
|---|---:|
| Coverage Gap | 2 |
| Invalid Reference | 1 |
| Missing Check | 1 |
| Outdated Value | 0 |

## Findings

| # | Class | Changed file | Matching skill | Proposed action | Confidence |
|---|---|---|---|---|---|
| 1 | Coverage Gap | src/i18n/en.json | none | CREATE verify-i18n | medium |
| 2 | Coverage Gap | src/i18n/ko.json | none | CREATE verify-i18n | medium |
| 3 | Invalid Reference | src/api/openapi.yaml | verify-api-contract | UPDATE stale path | high |
| 4 | Missing Check | src/messages/cost.ts | verify-message-cost | UPDATE Workflow for ALIMTALK | high |

## Ambiguous Items

| # | File | Candidate skills | Question |
|---|---|---|---|
| 1 | src/billing/refund-policy.ts | verify-payment, verify-business-rules | Which skill should own refund eligibility checks? |

## Proposed Repairs

### CREATE verify-i18n

Reason: new translation files and UI copy are not covered by any verifier.

Draft scope:
- Related Files: `src/i18n/**/*.json`, `src/**/*Copy.ts`
- Workflow: detect missing keys, untranslated placeholders, and locale mismatch.
- Exceptions: test fixtures and archived docs.

Approval required.

### UPDATE verify-api-contract

Reason: Related Files references `docs/api/openapi.yaml`, but the file moved to `src/api/openapi.yaml`.

Proposed edit:
- Replace stale path with current path.

### UPDATE verify-message-cost

Reason: message type `ALIMTALK` was added, but the verifier only checks SMS and LMS pricing.

Proposed edit:
- Add ALIMTALK expected cost mapping.
- Add a fixture or grep check for missing message type handling.

## Deferred / Exempt

None.

## Next Step

Run:

```text
/manage-skills repair
```

Then run:

```text
/verify-implementation
```
```
