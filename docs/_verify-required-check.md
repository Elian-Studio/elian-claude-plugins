# Temporary required-check verification

This file exists only to verify that the `validate` status check is a required
check on `main`. It is not part of the product and must not be merged.

It contains [a deliberately missing target](./does-not-exist-verify-check.md).
That broken relative link makes `scripts/validate_repository.py` report a
`relative-link` error, so CI can demonstrate that a failing required check
blocks the merge. The follow-up commit repairs the link to restore a valid state.
