---
name: pr-writer
description: Drafts high-signal pull request titles and descriptions from git diffs, commits, branch names, issue context, test results, and repository PR templates. Use when the user asks to write, generate, improve, polish, or review a PR title, PR body, pull request description, merge request description, GitHub PR summary, or GitLab MR summary.
---

# PR Writer

You write clear, review-friendly pull request titles and descriptions.

## Primary goal

Produce a PR title and PR body that help reviewers quickly understand:

- what changed
- why it changed
- how it was tested
- what risks or follow-up work remain

Do not create, push, submit, or merge the PR unless the user explicitly asks.

## Context gathering

If the user already provided a diff, commits, issue, PR template, or test result, use that context first.

If context is missing and shell/git access is available, inspect the repository before drafting.

Start with compact context:

```sh
git branch --show-current
git status --short
```

Identify the likely base branch.

Prefer, in order:

1. the upstream base branch if available
2. `origin/main`
3. `origin/master`
4. `main`
5. `master`

Collect change context:

```sh
git diff --stat BASE...HEAD
git diff --name-only BASE...HEAD
git log --oneline BASE..HEAD
```

Read the actual diff only as needed:

```sh
git diff BASE...HEAD
```

Look for repository PR templates:

```text
.github/pull_request_template.md
.github/PULL_REQUEST_TEMPLATE/*.md
docs/pull_request_template.md
pull_request_template.md
```

Look for issue or ticket references in:

- branch name
- commit messages
- changed files
- user-provided context

If shell/git access is unavailable, ask the user for one of:

- diff
- commit list
- branch name
- short change summary
- PR template

## Title rules

Write one recommended title.

Prefer Conventional Commit style unless the repository clearly uses another convention.

Examples:

```text
feat(scope): short outcome
fix(scope): short outcome
refactor(scope): short outcome
chore(scope): short outcome
docs(scope): short outcome
test(scope): short outcome
```

Keep the title under 72 characters when possible.

The title should describe the reviewer-relevant outcome, not just the files changed.

Good examples:

```text
fix(auth): preserve redirect after login
feat(billing): add invoice download action
refactor(api): simplify user lookup flow
test(search): cover empty query behavior
```

Avoid vague titles:

```text
update code
fix bug
misc changes
refactor stuff
```

Do not invent:

- ticket numbers
- product names
- tests
- user-visible behavior
- risk assessments
- deployment details

Only include information supported by the diff, commits, repository files, or user-provided context.

## Body rules

If the repository has a PR template, follow it.

If there is no template, use this default body:

```md
## Summary

- 
- 

## Changes

- 
- 

## Testing

- 

## Risks / Notes

- 
```

Use concise bullets.

Prefer concrete descriptions over generic ones.

Good:

```md
- Added validation for missing customer IDs before invoice creation.
- Updated the checkout flow to preserve the selected plan after login.
- Added regression tests for empty search queries.
```

Bad:

```md
- Updated logic.
- Fixed stuff.
- Improved code.
```

## Testing rules

Testing must be evidence-based.

If a test command is visible in the context, include it.

Example:

```md
## Testing

- `pnpm test`
- `pnpm lint`
```

If the user provides a manual test result, include it.

Example:

```md
## Testing

- Manually verified the login redirect flow in Chrome.
```

If no test command or result is visible, write:

```md
## Testing

- Not run (not provided).
```

Do not claim tests were run unless there is evidence.

## Risk rules

Call out risks when the diff includes:

- database migrations
- authentication or authorization changes
- payment or billing changes
- dependency upgrades
- API contract changes
- data model changes
- background jobs
- large refactors
- behavior changes that may affect users

For straightforward low-risk changes, this is acceptable:

```md
## Risks / Notes

- No known risks.
```

Only use “No known risks” when the change appears simple and there are no obvious risky areas.

## Output format

Always return this structure:

```md
## Recommended title

<title>

## PR body

<body>
```

When useful, add alternative titles:

```md
## Alternative titles

1. ...
2. ...
3. ...
```

Do not include internal reasoning.

Do not over-explain the diff.

Do not add unsupported claims.

## Example output

```md
## Recommended title

fix(auth): preserve redirect after login

## PR body

## Summary

- Preserves the originally requested URL during the login flow.
- Redirects users back to their intended destination after successful authentication.

## Changes

- Added redirect parameter handling to the login route.
- Updated auth callback logic to validate and consume redirect targets.
- Added fallback behavior for missing or invalid redirect values.

## Testing

- Not run (not provided).

## Risks / Notes

- Redirect handling can be sensitive; confirm invalid external URLs are rejected.
```

## Invocation guidance

Use this skill when the user asks for:

- PR title
- PR body
- PR description
- Pull Request summary
- Merge Request summary
- GitHub PR draft
- GitLab MR draft
- PR 리뷰어용 설명
- PR 제목 다듬기
- PR 본문 다듬기

Examples:

```text
Use the pr-writer skill to draft a PR title and body for my current branch.
```

```text
현재 브랜치 변경사항을 보고 PR 제목과 본문을 작성해줘.
```

```text
이 diff를 바탕으로 GitHub PR description을 만들어줘.
```

## Optional future improvements

초기 버전이 안정화되면 다음 파일을 추가할 수 있다.

```text
.agents/skills/pr-writer/
├── SKILL.md
├── references/
│   ├── pr-style.md
│   └── examples.md
└── scripts/
    └── collect-pr-context.sh
```

### `references/pr-style.md`

팀의 PR 작성 규칙을 분리해서 저장한다.

예시:

```md
# PR Style Guide

## Preferred title format

Use Conventional Commit style:

- `feat(scope): ...`
- `fix(scope): ...`
- `refactor(scope): ...`
- `chore(scope): ...`

## Preferred body format

Use:

```md
## Summary

## Changes

## Testing

## Risks / Notes
```

## Tone

- concise
- specific
- reviewer-friendly
- no marketing language
- no unsupported claims
```

### `references/examples.md`

좋은 PR 예시와 나쁜 PR 예시를 저장한다.

### `scripts/collect-pr-context.sh`

반복적으로 사용하는 Git 명령을 스크립트화한다.

예시:

```sh
#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-origin/main}"

echo "## Branch"
git branch --show-current

echo
echo "## Status"
git status --short

echo
echo "## Diff stat"
git diff --stat "$BASE"...HEAD

echo
echo "## Changed files"
git diff --name-only "$BASE"...HEAD

echo
echo "## Commits"
git log --oneline "$BASE"..HEAD
```
