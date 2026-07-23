---
name: pr-writer
description: >-
  Drafts high-signal pull request / merge request titles and descriptions by reading the git diff,
  commits, branch name, issue or ticket references, test evidence, and any repository PR template,
  then contrasting the change against its stated intent. Use when the user asks to write, generate,
  improve, polish, or review a PR title, PR body, pull request description, GitHub PR summary,
  GitLab MR summary, or merge request description, or right before requesting review on a finished
  feature or bug branch. Detects GitHub (gh) vs GitLab (glab) from the remote and follows the repo
  template when present. Drafts only — never pushes, creates, submits, or merges a PR/MR.
  Not for single commit messages (use a commit skill).
argument-hint: "[base-branch | --target <branch> | ISSUE-id]"
allowed-tools: Bash(git branch*) Bash(git status*) Bash(git diff*) Bash(git log*) Bash(git remote*) Bash(git rev-parse*) Bash(git merge-base*) Bash(gh pr view*) Bash(glab mr view*) Read Grep Glob
---

# PR Writer

Write clear, review-friendly pull request (GitHub PR) and merge request (GitLab MR) titles and descriptions.

## Why this skill exists

The hardest part of a code review is understanding **why** a change was made — and the *why* is not in the diff. The diff only shows *what* changed. The *why*, the *required behavior*, and the *definition of done* live in the issue/ticket, the branch intent, and the commit messages.

So this skill does not stop at summarizing a diff. It contrasts **intent vs implementation**: it pulls the stated goal (issue, ticket, branch name, user description) and shows which part of the change satisfies it, what is still missing, and what went beyond scope. That contrast is the map a reviewer needs before reading a single line.

## Primary goal

Produce a title and body that let a reviewer quickly see:

- **what** changed
- **why** it changed (tied to the stated intent)
- **how** it was tested
- **what** risks or follow-up work remain

## Side-effect posture

Drafting is the only default behavior. Read the repository; return a draft.

- Do **not** push, create, open, submit, or merge a PR/MR.
- If the user asks for creation or submission, return the completed draft and
  hand off to an explicitly authorized ship/CLI workflow.
- Never edit source files as part of drafting.

## Non-use boundary

- Not for a single **commit message** — use a commit skill.
- Not a code **review** skill — use `/elian-store:review`.
- Not a release/ship skill.

## Procedure: PLAN → DRAFT → CONTRAST

### 1. PLAN — gather context

If the user already supplied a diff, commits, issue, PR template, or test result, use that first. Otherwise inspect the repo. Start compact:

```sh
git branch --show-current
git status --short
git remote -v
```

**Detect the platform** from the remote:

- remote host contains `github.com` (or a GitHub Enterprise host) → GitHub PR vocabulary, look for `gh`.
- remote host contains `gitlab` → GitLab MR vocabulary, look for `glab`.
- otherwise → keep platform-neutral wording ("pull request").

**Detect the base branch**, in order (use the integration branch, not the branch's own remote):

1. the remote default branch — `git symbolic-ref --short refs/remotes/origin/HEAD` (e.g. `origin/main`)
2. `origin/main`
3. `origin/master`
4. `main`
5. `master`

Do not use the current branch's `@{upstream}` as the base: for a pushed feature branch it points at `origin/<that-branch>` and would diff the branch against itself.

**Collect change context:**

```sh
git diff --stat BASE...HEAD
git diff --name-only BASE...HEAD
git log --oneline BASE..HEAD
```

Read the full diff only as needed:

```sh
git diff BASE...HEAD
```

The bundled `scripts/collect-pr-context.sh` runs the branch / status / base-detection / stat / files / commits block in one call.

**Find a PR/MR template:**

```text
.github/pull_request_template.md
.github/PULL_REQUEST_TEMPLATE.md
.github/PULL_REQUEST_TEMPLATE/*.md
.gitlab/merge_request_templates/*.md
docs/pull_request_template.md
pull_request_template.md
```

**Find the stated intent** in: branch name, commit messages, changed files, the issue/ticket id, and any user-provided context. Capture the ticket id if the branch or commits reference one — but never invent one.

If shell/git is unavailable, ask the user for one of: diff, commit list, branch name, short change summary, or PR template — then proceed.

### 2. DRAFT — title and body

Apply the title and body rules below, following the repo template when one exists.

### 3. CONTRAST — intent vs implementation

Before emitting, check the draft against the stated intent:

- Each stated requirement → is it satisfied by the change? Name the part that satisfies it.
- Anything required but **missing**? Call it out.
- Anything changed **beyond** the stated scope (scope creep)? Call it out.
- Anything intentionally **excluded**? State it as a non-goal.

Only include claims supported by the diff, commits, repo files, or user-provided context.

## Title rules

Write one recommended title. Prefer Conventional Commit style unless the repo clearly uses another convention:

```text
feat(scope): short reviewer-relevant outcome
fix(scope): short reviewer-relevant outcome
refactor(scope): ...
chore(scope): ...
docs(scope): ...
test(scope): ...
```

- Keep it under ~72 characters when possible.
- Describe the reviewer-relevant **outcome**, not the files touched.
- Do not invent ticket numbers, product names, tests, user-visible behavior, risk claims, or deploy details.

See `references/pr-style.md` for the full convention and anti-patterns, and `references/examples.md` for good vs bad titles and bodies.

## Body rules

If the repo has a template, **follow it**. Otherwise use this default:

```md
## Summary

-

## Changes

-

## Testing

-

## Risks / Notes

-
```

- Use concise, concrete bullets ("Added validation for missing customer IDs before invoice creation"), not generic ones ("Updated logic").
- When intent context exists, add a short **requirement → implementation** mapping in Summary or Changes so the reviewer sees coverage at a glance.

## Testing rules

Testing must be evidence-based.

- If a test command is visible in context, include it (e.g. `` `pnpm test` ``, `` `./gradlew test` ``).
- If the user reports a manual result, include it.
- If no test evidence is visible, write exactly: `- Not run (not provided).`
- Never claim tests were run without evidence.

## Risk rules

Call out risks when the diff touches: database migrations, auth/authorization, payments/billing, dependency upgrades, API contract changes, data-model changes, background jobs, large refactors, or other user-visible behavior changes.

For a clearly simple change with no risky surface, `- No known risks.` is acceptable.

## Output contract

Always return this structure:

```md
## Recommended title

<title>

## PR body

<body>
```

Add alternatives only when useful:

```md
## Alternative titles

1. ...
2. ...
```

Do not include internal reasoning, do not over-explain the diff, do not add unsupported claims.

## What's automated vs what needs your taste

| Automated | User decides |
|---|---|
| Base branch + platform detection | Which base/target when ambiguous |
| Diff / commit / template collection | Whether to follow or override the template |
| Title draft + alternatives | Final title wording |
| Intent → implementation contrast | Whether a scope gap is intended |
| Risk flags from the changed surface | Whether a risk is acceptable to ship |

## Forbidden

- Push, create, open, submit, or merge a PR/MR without an explicit request.
- Edit source files while drafting.
- Invent tickets, tests, metrics, or user-visible claims.
- Claim tests ran without evidence.
- Bury a missing requirement or scope creep under summary prose.

## Self-check before returning

- [ ] Base branch and platform identified (or explicitly asked).
- [ ] Title states a reviewer-relevant outcome, under ~72 chars.
- [ ] Body follows the repo template when one exists.
- [ ] Stated requirements are mapped; missing/extra scope is called out.
- [ ] Testing reflects real evidence, or says "Not run (not provided)".
- [ ] Risks reflect the actual changed surface.
- [ ] No unsupported claims; no side effects performed.

## Supporting files

| File | Purpose |
|---|---|
| [references/pr-style.md](references/pr-style.md) | Title/body conventions, sizing guidance, anti-patterns, tone |
| [references/examples.md](references/examples.md) | Good vs bad titles and bodies, intent-contrast example |
| [scripts/collect-pr-context.sh](scripts/collect-pr-context.sh) | One-shot git context collector with base-branch detection |
