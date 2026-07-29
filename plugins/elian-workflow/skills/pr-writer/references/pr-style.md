# PR Style Guide

The conventions `pr-writer` follows when a repository does not impose its own.

## Title

Use Conventional Commit style unless the repository's history clearly uses something else:

- `feat(scope): ...` — new user-visible capability
- `fix(scope): ...` — bug fix
- `refactor(scope): ...` — behavior-preserving restructure
- `perf(scope): ...` — performance change
- `chore(scope): ...` — tooling, deps, housekeeping
- `docs(scope): ...` — docs only
- `test(scope): ...` — tests only

Rules:

- Under ~72 characters when possible.
- Describe the reviewer-relevant **outcome**, not the files touched.
- One title is recommended; offer alternatives only when the framing genuinely differs.
- Match the repository's existing casing and scope vocabulary. If history uses `[JIRA-123]` prefixes or plain sentences, mirror that instead of forcing Conventional Commits.

## Body

Default structure when there is no repository template:

```md
## Summary

## Changes

## Testing

## Risks / Notes
```

- **Summary**: the why and the outcome, tied to the stated intent. 1–3 bullets.
- **Changes**: concrete, file/area-anchored bullets a reviewer can map to the diff.
- **Testing**: evidence only (see below).
- **Risks / Notes**: real risk surface and follow-ups.

When intent context (issue/ticket/branch goal) exists, add a short requirement → implementation mapping so coverage is visible before the reviewer opens the diff.

## Sizing guidance

Smaller, single-purpose PRs review faster and merge with fewer defects. When a diff is large or mixes unrelated concerns, say so in `Risks / Notes` and suggest splitting — do not silently bless a 2,000-line mixed change as routine.

## Testing evidence

- Visible test command in context → include it verbatim.
- User-reported manual result → include it.
- No evidence → write exactly `- Not run (not provided).`
- Never assert tests passed without evidence.

## Anti-patterns

Avoid vague titles:

```text
update code
fix bug
misc changes
refactor stuff
```

Avoid empty body bullets:

```md
- Updated logic.
- Fixed stuff.
- Improved code.
```

Avoid:

- inventing ticket numbers, product names, metrics, or user-visible claims
- claiming tests ran without evidence
- restating the diff line-by-line instead of explaining intent and risk
- hiding a missing requirement or scope creep inside prose

## Tone

- Concise, specific, reviewer-friendly.
- No marketing language, no fake metrics, no padding.
- State "untested", "MVP", or "needs validation" honestly when true.
