# Temporary required-check verification

This file exists only to verify that the `validate` status check is a required
check on `main`. It is not part of the product and must not be merged.

It previously contained a deliberately broken relative link so CI could
demonstrate that a failing required check blocks the merge. The link now points
at [the repository README](../README.md), which exists, so
`scripts/validate_repository.py` passes and the required check clears.
