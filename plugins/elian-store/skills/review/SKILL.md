---
name: review
description: "When the user asks for code review, PR review, diff review, or runs /review, perform a read-only engineering review of changed code to find production risks, regressions, broken contracts, missing tests, and verification gaps before merge. Lead with findings, cite file:line evidence, and hand off fixes/QA/ship instead of editing code."
when_to_use: "Use for current worktree, staged changes, branch diff, PR/MR diff, or specific files when the goal is engineering review before merge. Trigger phrases: '리뷰해줘', '코드 리뷰', 'PR 리뷰', 'diff review', '/review', '현재 변경사항 점검'. Do NOT use for persona lens reviews, running verify-* checks, browser QA, release readiness, or making code changes."
argument-hint: "[target: worktree|staged|branch:<base>|pr:<id>|<path>] [--depth quick|deep] [--lenses security,performance,quality,design,adversarial]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git status*), Bash(git diff*), Bash(git log*), Bash(git show*), Agent, AskUserQuestion
---

# /review - Read-only engineering review

Review changed code before merge. This skill reads diffs, files, and context, then returns findings with evidence. It does not edit files, run the release flow, or replace project verification.

Core contract:

- Findings first. Bugs, regressions, broken contracts, missing tests, and production risks lead the response.
- Evidence over vibe. Cite `file:line` when available; otherwise say what evidence is missing.
- Read-only. Do not create files, modify code, stage, commit, push, or apply fixes.
- Narrow role. Hand off to `/fix`, `/improve`, `/implement`, `/verify-implementation`, `/browser-qa`, or `/ship` instead of absorbing their work.
- No score padding. If there are no blocking issues, say so and state residual risk.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `target` | `worktree`, `staged`, `branch:<base>`, `pr:<id>`, or a file/path | `${REVIEW_DEFAULT_TARGET}` or `worktree` |
| `--depth quick\|deep` | `quick` reads the direct diff; `deep` reads related call sites and contracts | `${REVIEW_DEPTH}` or `quick` |
| `--lenses` | Comma-list of optional review lenses | `${REVIEW_LENSES}` or inferred from diff |

`$ARGUMENTS` always wins over environment defaults.

## Where this fits in the workflow

```text
implement / fix / improve -> review -> verify-implementation -> browser-qa -> ship
                         \-> fix / improve handoff when findings block merge
```

- **Before** `/review`: code, diff, or PR exists.
- **This skill**: read-only engineering risk review with findings.
- **After** `/review`: fix the findings, run verification, perform browser QA when user-visible behavior changed, then ship.

## Modes

### Mode 1: `quick`

Use for small diffs and targeted file review. Read the diff, changed files, nearby tests, and relevant project instructions. Prefer direct review over subagents.

### Mode 2: `deep`

Use for cross-module, security-sensitive, performance-sensitive, migration, or user-visible changes. Read call sites, contracts, tests, config, and prior commits as needed.

### Mode 3: multi-lens review

Use `--lenses` or infer it for large diffs. Run independent read-only subagents only when the lenses are separable:

| Lens | Suggested subagent | Use when |
|---|---|---|
| `security` | `security-engineer` | auth, secrets, input validation, tenant isolation, OWASP/AI risk |
| `performance` | `performance-engineer` | queries, queues, caching, hot paths, payload size |
| `quality` | `quality-engineer` | missing tests, flaky tests, regression gaps |
| `design` | `ui-ux-designer` | user-visible UI diff, copy/state/layout risk |
| `adversarial` | `devil-advocate` | assumptions, migration safety, operational blast radius |

If reviewers must debate trade-offs during the review, ask the user before switching to a team-style workflow.

## Standing Rules

- Review the current repository state, not memory or stale conclusions.
- Lead with findings ordered by severity.
- Prefer current diff evidence over generic best practices.
- Treat tests as evidence, not as proof. Passing tests can still miss behavior.
- When target is missing, ask one question: current worktree, staged changes, branch diff, PR/MR, or path?
- For large diffs, summarize reviewed scope before findings.
- If a finding depends on an assumption, mark it as `Needs confirmation`.
- Never bury a blocker under summary prose.

## Procedure

1. Parse `$ARGUMENTS` for target, depth, and lenses.
2. Inspect repo state with `git status --short` and choose the review target.
3. Collect evidence:
   - `worktree`: `git diff` plus changed file context.
   - `staged`: `git diff --cached`.
   - `branch:<base>`: `git diff <base>...HEAD`.
   - `pr:<id>` or MR URL: ask before using network-dependent tools.
   - path: read the file and, when useful, `git diff -- <path>`.
4. Identify change intent from docs, commit messages, branch name, or user request.
5. Review by risk axis:
   - correctness and regression
   - API, schema, event, or domain contract
   - test coverage and verification gaps
   - security and privacy
   - performance and reliability
   - UI/user-visible behavior when in scope
6. Optionally dispatch read-only subagents for independent lenses.
7. Aggregate findings. Deduplicate, keep the strongest evidence, and preserve conflicting lens notes.
8. Return the output contract.

## Output Contract

Always use findings-first structure:

```text
Findings
- [HIGH] path/to/file.ext:42 - concise problem
  Evidence:
  Impact:
  Suggested fix:
  Test/verification gap:

Open Questions
Residual Risk
Handoff
```

Severity rubric:

| Severity | Meaning |
|---|---|
| `CRITICAL` | likely data loss, auth bypass, production outage, or unsafe deploy |
| `HIGH` | likely bug/regression or broken contract before merge |
| `MEDIUM` | plausible defect, missing test for risky behavior, or maintainability risk with near-term impact |
| `LOW` | minor issue, readability, local polish, or non-blocking observation |
| `INFO` | useful note, not a finding |

No-findings response:

```text
Findings
- No blocking findings in the reviewed scope.

Reviewed Scope
- ...

Residual Risk
- ...
```

See [references/example-findings.md](references/example-findings.md) for BEFORE/AFTER examples and a compact checklist.

## What's Automated vs What Needs User Taste

| Automated | User decides |
|---|---|
| Target inference when obvious | Which diff/PR/path to review when ambiguous |
| Severity draft from impact | Whether to accept or defer a finding |
| Lens selection from changed files | Whether to run multi-lens subagents |
| Suggested fix direction | Exact implementation approach |
| Handoff target recommendation | Whether to run `/fix`, `/improve`, QA, or ship |

## Persistent Artifact for Downstream

When the user needs a durable handoff, emit a compact markdown block they can save or pass to another skill:

```text
Handoff
- Target: <diff/path/PR>
- Blocking findings: <count>
- Recommended next skill: /fix | /improve | /verify-implementation | /browser-qa | /ship
- Required verification: <commands or checks>
- Residual risk: <what remains unknown>
```

The review itself does not write this file automatically.

## Forbidden

- Edit, write, stage, commit, push, or open a PR.
- Run destructive commands or broad cleanup.
- Treat `/persona-review` style persona critique as engineering review.
- Run all project verification commands as a substitute for reading the code.
- Perform browser-visible QA or screenshot validation.
- Decide release readiness or deployment safety.
- Report vague findings without file/line evidence or an explicit evidence gap.

## Pitfalls

| Pitfall | Symptom | Prevention |
|---|---|---|
| Reviewing old conclusions | Same answer despite changed code | Re-read current diff and files every run |
| Test-pass tunnel vision | "CI passed" replaces review | Inspect behavior, contracts, and missing test cases |
| Over-scoped review | Findings become implementation plan | Keep suggested fixes concise and hand off execution |
| Persona drift | Style critique replaces code evidence | Use `/persona-review` for lenses, `/review` for engineering findings |
| QA confusion | UI behavior assumed from diff | Flag browser QA need, then hand off to `/browser-qa` |

### BEFORE / AFTER

BEFORE:

```text
Looks fine overall. Maybe add more tests.
```

AFTER:

```text
Findings
- [HIGH] src/auth/session.ts:88 - expired sessions are accepted when refreshToken is null.
  Evidence: the new branch returns early before `expiresAt` is checked.
  Impact: stale sessions can remain authenticated.
  Suggested fix: check expiry before the refresh-token branch.
  Test/verification gap: add a regression test for null refresh token + expired session.
```

## Validation

Run the skill self-check:

```bash
python3 plugins/elian-store/skills/review/scripts/validate_skill.py
python3 plugins/elian-store/skills/review/scripts/validate_skill.py --json
```

The validator checks frontmatter, read-only boundaries, required sections, reference links, and the findings-first contract.

## Reflection

At the end of a deep review, include up to three short observations:

1. Which class of risk dominated the findings?
2. Which missing test would have caught the highest-severity issue?
3. Which downstream skill should handle the next step?
