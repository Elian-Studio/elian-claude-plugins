# /pr-writer - Pull request / merge request description writer (Codex Port)

Install path: `~/.codex/prompts/pr-writer.md`.

Invocation:

```text
/pr-writer [base-branch | --target <branch> | ISSUE-id | --create]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/pr-writer/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

Draft-only contract: read the repository and return a title + body. Do not push, create, open, submit, or merge a PR/MR unless the user explicitly asks (e.g. `--create`). Output Markdown only.

## Purpose

Write a clear, review-friendly pull request (GitHub PR) or merge request (GitLab MR) title and description.

A reviewer's hardest task is understanding **why** a change was made, and the *why* is not in the diff — it is in the issue/ticket, the branch intent, and the commits. So this prompt contrasts **intent vs implementation**: it pulls the stated goal and shows which part of the change satisfies it, what is missing, and what went beyond scope.

This is not a commit-message writer and not a code-review prompt.

## Common Contract

1. Drafts only. No push/create/merge without an explicit request.
2. Evidence over claims. Only state what the diff, commits, repo files, or user context support.
3. Intent first. Tie the body to the stated requirement, not just the file list.
4. Read-only on source. Never edit files while drafting.
5. No padding. No invented tickets, tests, metrics, or user-visible claims.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `base-branch` / `--target <branch>` | Base to diff against | auto-detected |
| `ISSUE-id` | Ticket/issue to read for intent | inferred from branch/commits |
| `--create` | Explicit opt-in to create the PR/MR after the draft is approved | off |

`$ARGUMENTS` always wins over any local default.

## Procedure: PLAN -> DRAFT -> CONTRAST

### 1. PLAN — gather context

```sh
git branch --show-current
git status --short
git remote -v
```

Detect the platform from the remote: `github.com` -> GitHub PR vocabulary (`gh`); `gitlab` -> GitLab MR vocabulary (`glab`); otherwise neutral "pull request".

Detect the base branch in order (use the integration branch, not the branch's own remote): remote default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`, e.g. `origin/main`) -> `origin/main` -> `origin/master` -> `main` -> `master`. Do not use the current branch's `@{upstream}` as the base — for a pushed feature branch it points at `origin/<that-branch>` and diffs the branch against itself.

Collect change context:

```sh
git diff --stat BASE...HEAD
git diff --name-only BASE...HEAD
git log --oneline BASE..HEAD
git diff BASE...HEAD   # only as needed
```

Find a template: `.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE/*.md`, `.gitlab/merge_request_templates/*.md`, `docs/pull_request_template.md`, `pull_request_template.md`.

Find the stated intent in: branch name, commit messages, changed files, issue/ticket id, user context. Never invent a ticket id.

If git is unavailable, ask for one of: diff, commit list, branch name, change summary, or template — then proceed.

### 2. DRAFT — title and body

Title: prefer Conventional Commit style unless the repo clearly uses another convention. Under ~72 chars. Describe the reviewer-relevant outcome, not files.

Body: follow the repo template when present. Otherwise:

```md
## Summary

## Changes

## Testing

## Risks / Notes
```

### 3. CONTRAST — intent vs implementation

- Each stated requirement: satisfied? name where.
- Missing requirement? call it out.
- Scope creep beyond the goal? call it out.
- Deliberately excluded? state it as a non-goal.

## Testing rule

Evidence-based only. Visible test command -> include it. User-reported manual result -> include it. No evidence -> write `- Not run (not provided).` Never claim tests ran without evidence.

## Risk rule

Flag risk when the diff touches: migrations, auth/authorization, payments/billing, dependency upgrades, API contract changes, data-model changes, background jobs, large refactors, or user-visible behavior. For a clearly simple change, `- No known risks.` is acceptable.

## Output Contract

```md
## Recommended title

<title>

## PR body

<body>
```

Add `## Alternative titles` only when framing genuinely differs. No internal reasoning, no diff narration, no unsupported claims.

## Forbidden

- Push, create, open, submit, or merge a PR/MR without an explicit request.
- Edit source files while drafting.
- Invent tickets, tests, metrics, or user-visible claims.
- Claim tests ran without evidence.
- Bury a missing requirement or scope creep under summary prose.

## Pre-Output Self-Check

- [ ] Base branch and platform identified (or asked).
- [ ] Title states a reviewer-relevant outcome, under ~72 chars.
- [ ] Body follows the repo template when one exists.
- [ ] Requirements mapped; missing/extra scope called out.
- [ ] Testing reflects real evidence, or says "Not run (not provided)".
- [ ] No unsupported claims; no side effects performed.
