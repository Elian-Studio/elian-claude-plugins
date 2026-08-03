# Example Verification Report

Use this structure for `verify-implementation`.

```markdown
# Verification Report

Scope:
- Root: .claude/skills
- Mode: run-all
- Skills discovered: 5
- Skills run: 4
- Skills skipped: 1

## Summary

| Status | Count |
|---|---:|
| PASS | 3 |
| FAIL | 1 |
| SKIP | 1 |
| ERROR | 0 |

## Skill Results

| Skill | Status | Findings | Notes |
|---|---|---:|---|
| verify-api-contract | PASS | 0 | OpenAPI contract matched implementation |
| verify-i18n | FAIL | 3 | Missing keys in two locale files |
| verify-security-policy | PASS | 0 | Permission checks present |
| verify-message-cost | PASS | 0 | Cost mapping complete |
| verify-production-deploy | SKIP | 0 | manual-only marker |

## Findings

### verify-i18n

- [MEDIUM] src/i18n/en.json - missing key `profile.save.success`
  Evidence: `src/features/profile/ProfileForm.tsx` references the key.
  Suggested fix: add the key to all active locales.
  Verification: rerun verify-i18n.

- [MEDIUM] src/i18n/ko.json - missing key `profile.save.success`
  Evidence: English locale has no matching key pair.
  Suggested fix: add the matching locale value.
  Verification: rerun verify-i18n.

- [LOW] src/features/profile/ProfileForm.tsx - hardcoded fallback copy
  Evidence: fallback string appears next to translation call.
  Suggested fix: move fallback copy into locale files.
  Verification: rerun verify-i18n and UI smoke check.

## Exceptions Applied

| Skill | File | Reason |
|---|---|---|
| verify-i18n | tests/fixtures/missing-key.json | fixture intentionally invalid |

## Auto-Fix Gate

Found 3 issues in 1 skill.

Options:

1. Apply all suggested fixes.
2. Review fixes one by one.
3. Stop without changes.

## After Fix

| Skill | Before | After |
|---|---|---|
| verify-i18n | FAIL (3) | PASS (0) |

## Residual Issues

None.

## Next Step

Run browser QA if the changed copy is user-visible, then proceed to PR.
```
