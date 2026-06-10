# PR Examples

Good and bad titles and bodies, plus an intent-contrast example.

## Titles

Good — reviewer-relevant outcome:

```text
fix(auth): preserve redirect after login
feat(billing): add invoice download action
refactor(api): simplify user lookup flow
test(search): cover empty query behavior
```

Bad — vague or file-centric:

```text
update code
fix bug
changes to AuthService.java
misc
```

## Body — full example

```md
## Recommended title

fix(auth): preserve redirect after login

## PR body

## Summary

- Preserves the originally requested URL through the login flow.
- Redirects users back to their intended destination after authentication.
- Closes AUTH-214 (deep links dropped the user on the dashboard after login).

## Changes

- Added redirect-parameter handling to the login route.
- Updated the auth callback to validate and consume the redirect target.
- Added a fallback for missing or invalid redirect values.

## Testing

- `pnpm test`
- Manually verified the login redirect flow in Chrome.

## Risks / Notes

- Redirect handling is security-sensitive; external/open-redirect URLs are rejected by the validator. Confirm the allowlist in review.
```

## Intent-contrast example

When the branch/ticket states a goal, surface coverage explicitly:

```md
## Summary

Implements AUTH-214 "keep the user's deep link through login".

| Requirement (AUTH-214) | Status | Where |
|---|---|---|
| Return user to original URL after login | Done | login route + callback |
| Reject open-redirect targets | Done | redirect validator |
| Remember link across OAuth bounce | Not in this PR | tracked in AUTH-219 |
```

This block tells the reviewer what to verify before reading the diff, and makes the deliberately-deferred item visible instead of looking like a miss.

## Low-risk change

For a small, self-contained change, a short body is correct — do not pad it:

```md
## Summary

- Fix typo in the checkout empty-state copy.

## Testing

- Not run (not provided).

## Risks / Notes

- No known risks.
```
