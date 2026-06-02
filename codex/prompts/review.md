# /review - Read-only engineering review (Codex Port)

Install path: `~/.codex/prompts/review.md`.

Invocation:

```text
/review <target> [--depth quick|deep] [--lenses security,performance,quality,design,adversarial]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/review/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

Read-only contract: do not edit files, create files, stage, commit, push, or run destructive commands. Output Markdown only. If implementation is needed, emit a handoff payload and stop.

## Purpose

Review changed code before merge. The goal is to find production risks, regressions, broken contracts, missing tests, and verification gaps.

This is not a fix skill, not a release skill, and not a browser QA skill.

## Common Contract

1. Findings first. Bugs, regressions, broken contracts, missing tests, and production risks lead the response.
2. Evidence over vibe. Cite `file:line` when available; otherwise say what evidence is missing.
3. Read-only. Do not modify code or run destructive commands.
4. Narrow role. Hand off to `/fix`, `/improve`, `/implement`, `/verify-implementation`, `/browser-qa`, or `/ship` instead of absorbing their work.
5. No score padding. If there are no blocking issues, say so and state residual risk.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `target` | `worktree`, `staged`, `branch:<base>`, `pr:<id>`, or a file/path | `worktree` |
| `--depth quick\|deep` | `quick` reads the direct diff; `deep` reads related call sites and contracts | `quick` |
| `--lenses` | Comma-list of optional review lenses | inferred from diff |

`$ARGUMENTS` always wins over any local default.

## Where This Fits

```text
implement / fix / improve -> review -> verify-implementation -> browser-qa -> ship
                         \-> fix / improve handoff when findings block merge
```

- **Before** `/review`: code, diff, or PR exists.
- **This skill**: read-only engineering risk review with findings.
- **After** `/review`: fix the findings, run verification, perform browser QA when user-visible behavior changed, then ship.

## Modes

### Mode 1: `quick`

Use for small diffs and targeted file review. Read the diff, changed files, nearby tests, and relevant project instructions.

### Mode 2: `deep`

Use for cross-module, security-sensitive, performance-sensitive, migration, or user-visible changes. Read call sites, contracts, tests, config, and prior commits as needed.

### Mode 3: multi-lens review

Use `--lenses` or infer it for larger diffs. Split the review by risk axis when useful:

| Lens | Use when |
|---|---|
| `security` | auth, secrets, input validation, tenant isolation, OWASP/AI risk |
| `performance` | queries, queues, caching, hot paths, payload size |
| `quality` | missing tests, flaky tests, regression gaps |
| `design` | user-visible UI diff, copy/state/layout risk |
| `adversarial` | assumptions, migration safety, operational blast radius |

Keep lens notes separate when they disagree.

## Standing Rules

- Review the current repository state, not memory or stale conclusions.
- Lead with findings ordered by severity.
- Prefer current diff evidence over generic best practices.
- Treat tests as evidence, not as proof. Passing tests can still miss behavior.
- When the target is missing, ask one question: current worktree, staged changes, branch diff, PR/MR, or path?
- For large diffs, summarize the reviewed scope before findings.
- If a finding depends on an assumption, mark it as `Needs confirmation`.
- Never bury a blocker under summary prose.

## Procedure

1. Parse `$ARGUMENTS` for target, depth, and lenses.
2. Inspect repo state and choose the review target.
3. Collect evidence from the diff, files, tests, and surrounding context.
4. Identify change intent from docs, commit messages, branch name, or user request.
5. Review by risk axis:
   - correctness and regression
   - API, schema, event, or domain contract
   - test coverage and verification gaps
   - security and privacy
   - performance and reliability
   - UI/user-visible behavior when in scope
6. Aggregate findings. Deduplicate, keep the strongest evidence, and preserve conflicting lens notes.
7. Return the output contract.

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

## What's Automated vs What Needs User Taste

| Automated | User decides |
|---|---|
| Target inference when obvious | Which diff/PR/path to review when ambiguous |
| Severity draft from impact | Whether to accept or defer a finding |
| Lens selection from changed files | Whether to pursue a deeper review path |
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

## Reflection

At the end of a deep review, include up to three short observations:

1. Which class of risk dominated the findings?
2. Which missing test would have caught the highest-severity issue?
3. Which downstream skill should handle the next step?

## Pre-Output Self-Check

- [ ] Target is clear.
- [ ] Thin input was clarified before review.
- [ ] Findings are ordered by severity.
- [ ] Confirmed evidence and missing evidence are separated.
- [ ] The output ends with one next question or next action.
