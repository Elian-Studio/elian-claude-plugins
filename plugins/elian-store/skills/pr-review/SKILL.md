---
name: pr-review
description: "Orchestrate a multi-perspective review of an existing pull request / merge request, the natural step after pr-writer creates or updates it. Resolve the PR (current branch, pr:<id>, or URL), gather its description, linked issue, commits, diff, and CI status, then dispatch a panel of independent read-only reviewers — engineering specialists (correctness, security, performance, architecture, maintainability, tests, requirements-fit, plus scope-triggered frontend/backend/data/API/ops/docs lenses) and persona judges (Beck, Dean, Evans, Fowler, Martin, Daniel) — and synthesize their findings into one prioritized verdict (Approve / Comment / Request changes) contrasted against the PR's stated intent. Local report by default; post to the PR only after explicit confirmation."
when_to_use: "Use right after pr-writer creates or updates a PR/MR, or whenever the user wants a many-angle panel review of an existing pull request before merge. Trigger phrases: 'review this PR', 'PR review panel', 'multi-perspective PR review', 'should we merge this PR', 'review PR #123 from every angle', '/pr-review'. Do NOT use for local-only diff review with handoff (use /review), persona-only critique of a plan or doc (use /persona-review), drafting the PR title/body (use /pr-writer), or editing code (use /fix or /improve)."
argument-hint: "[current | pr:<id> | <url> | branch:<base>] [--post] [--personas all|none|<list>] [--scope <areas>] [--depth quick|deep]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git status*), Bash(git diff*), Bash(git log*), Bash(git show*), Bash(git branch*), Bash(git rev-parse*), Bash(git merge-base*), Bash(git fetch*), Bash(gh pr view*), Bash(gh pr diff*), Bash(gh pr checks*), Bash(gh pr list*), Bash(glab mr view*), Bash(glab mr diff*), Agent, AskUserQuestion
---

# /pr-review — multi-perspective pull request review

Review an existing pull request (GitHub PR) or merge request (GitLab MR) through a panel of independent perspectives, then synthesize one prioritized verdict. This is the review counterpart to `pr-writer`: pr-writer explains *what and why* to the reviewer; pr-review *is* the reviewer, run as a panel rather than a single pass.

## Why this skill exists

A single reviewer has blind spots. The same person who is sharp on security misses the N+1 query; the one who sees the missing test misses the domain-model leak. Real review boards work because several minds with different priorities look at the same change.

This skill reproduces that on demand. It dispatches many read-only reviewers — engineering specialists that run grounded checklists, and persona judges that bring opinionated judgment — then merges their output. Two things make the result more than the sum of its parts:

- **Breadth catches more.** Independent lenses surface issues no one lens would. When several lenses flag the same line, confidence rises; when two lenses disagree, that tension is itself a finding.
- **Intent contrast catches scope drift.** Because the PR already carries a description (often written by pr-writer) and usually a linked issue, the panel can check the diff against *what it was supposed to do*, not just whether the code is clean. A clean diff that misses a requirement still fails review.

## Where this fits in the workflow

```text
implement / fix / improve -> pr-writer -> (PR created/updated on platform) -> pr-review -> fix / improve -> ship
                                                                          \-> post review to PR (on confirm)
```

- **Before** `/pr-review`: a PR/MR exists on the platform (or a branch ready to be reviewed as a PR diff). `pr-writer` has usually drafted the description.
- **This skill**: gather PR context, run the perspective panel, synthesize a verdict, optionally post it.
- **After** `/pr-review`: fix blocking findings (`/fix`, `/improve`), re-verify, then `/ship`.

Relationship to neighbors — pick the right tool:

| Skill | Role | Difference from pr-review |
|---|---|---|
| `/review` | Read-only engineering review of a local diff | No platform PR, no intent/CI context, never posts, single-pass |
| `/persona-review` | Persona judgment lenses on any target | Personas only; no specialist panel, no PR posting, no verdict synthesis |
| `/pr-writer` | Draft the PR title/body | Writes the PR; does not review it |

## Side-effect posture

Producing a review report is the only default behavior.

- Default output is a **local report** in the terminal. Read the PR; return findings and a verdict.
- **Posting to the PR is opt-in.** Only post inline or summary comments, or set a review state (approve / request-changes / comment), after the user explicitly confirms — show the exact draft and command first. `--post` signals intent but still confirms before the network call.
- **Never merge**, close, or push. Never edit source files. Review is read-only against the code.

This matches `pr-writer` (drafts only) and `review` (read-only): external, hard-to-reverse actions wait for an explicit yes.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| target | `current` (the open PR for this branch), `pr:<id>`, a PR/MR URL, or `branch:<base>` to review the branch as a diff when no PR exists yet | `current` |
| `--post` | After synthesis, offer to post the review to the PR (still confirms) | off (local report) |
| `--personas all\|none\|<list>` | Which persona judges to run | `all` |
| `--scope <areas>` | Force specific scope lenses (e.g. `frontend,data`) instead of inferring from the diff | inferred |
| `--depth quick\|deep` | `quick` reviews the diff; `deep` lets reviewers read call sites, contracts, and tests around the diff | `deep` |

`$ARGUMENTS` always wins. The default is deliberately thorough — full specialist panel plus all personas — because the value of this skill is breadth. Use `--personas none` or `--scope` to run lighter when you want speed over coverage.

## Procedure: GATHER -> PANEL -> SYNTHESIZE -> REPORT -> POST

### 1. GATHER — build the review packet

Detect the platform from the remote (`git remote get-url origin`): `github.com` or `gh auth status` -> GitHub; `gitlab` or `glab auth status` -> GitLab. Then resolve the target and collect, in one packet the panel will share:

- **Stated intent**: PR/MR title + body (`gh pr view --json title,body` / `glab mr view`), the linked issue if referenced, and the branch name.
- **Change**: the diff (`gh pr diff <id>` / `glab mr diff`, or `git diff $(git merge-base origin/<base> HEAD)` for `branch:<base>`), commit messages (`git log origin/<base>..HEAD --oneline`), and `--stat` for scope.
- **Signals**: CI status (`gh pr checks` / pipeline status), changed-file map (which areas: backend, frontend, data/migrations, infra, docs, tests).

If no PR exists and the target is not `branch:<base>`, ask once: review the current branch as a diff, or point at a specific PR? If a network call is needed and the environment may be offline, say so before relying on it.

### 2. PANEL — dispatch the perspectives in parallel

Dispatch every selected reviewer as an independent read-only subagent via the Agent tool, **all in one message** so they run concurrently with fresh, unbiased context. Give each the shared packet (intent + diff + scope map) and ask for structured findings.

**One agent, one subagent.** Several rows below can map to the same agent — `system-architect` owns architecture *and* the data/migration lens; `backend-architect` owns backend layering *and* the API-contract lens. When that happens for a given diff, dispatch that agent **once** with all of its concerns folded into the prompt, not once per row. This is what keeps a thorough panel from ballooning into redundant runs.

Run three layers (full catalog with the questions each lens asks and its red flags: [references/perspectives.md](references/perspectives.md)):

**Layer 1 — Functional specialists (always run):**

| Perspective | Subagent | Core question |
|---|---|---|
| Correctness & regression | `devil-advocate` | How does this break in production? edge/null/error paths, races, silent wrong results |
| Security & privacy | `security-engineer` | Authz, injection, secrets, input validation, trust boundaries, OWASP |
| Performance & scale | `performance-engineer` | N+1, hot paths, payload size, unbounded work, caching |
| Architecture & design | `system-architect` | Boundaries, coupling, does the change fit the system |
| Tests & maintainability | `quality-engineer` | Coverage of new behavior, edge/error-path tests, regression gaps, duplication, change blast radius (Fowler/Martin personas deepen the maintainability lens) |
| Requirements fit & scope | `requirements-analyst` | Does the diff satisfy the stated intent? missing reqs, scope creep, partial work |

**Layer 2 — Scope-triggered specialists (run when the diff touches the area; out-of-scope reviewers return NO FINDINGS quickly):**

| Area signal | Subagent | Looks for |
|---|---|---|
| UI / component / style files | `frontend-architect`, `ui-ux-designer` | State/loading/error/empty handling, a11y, user-visible regressions |
| service / controller / repo | `backend-architect` | Layering, transaction boundaries, error contracts |
| migrations / schema / DDL | `system-architect` (data lens) | Migration safety, backfill, rollback, lock risk |
| public API / events / DTO | `backend-architect` (contract lens) | Breaking changes, versioning, consumer impact |
| CI / infra / config / secrets | `devops-architect` | Deploy safety, rollback, config drift, observability |
| docs / README / public copy | `technical-writer` | Stale docs, missing docs for the change |

**Layer 3 — Persona judges (`--personas`, default all six):** different *minds*, not checklists. They critique in their own voice; do not force them into a shared template.

| Persona | Subagent | Lens |
|---|---|---|
| Beck | `persona-beck-reviewer` | TDD/XP: test-first, simplest thing, YAGNI, fast feedback |
| Dean | `persona-dean-reviewer` | Distributed systems: tail latency, SPOF, idempotency, backpressure |
| Evans | `persona-evans-reviewer` | DDD: ubiquitous language, bounded context, aggregate invariants |
| Fowler | `persona-fowler-reviewer` | Refactoring: code smells, module boundaries, evolutionary design |
| Martin | `persona-martin-reviewer` | Clean Code: SRP, SOLID, naming, small functions |
| Daniel | `persona-daniel-reviewer` | Operational: mechanism, axiom vs policy, failure modes, automation |

Each reviewer is read-only. If one fails or times out, log it and synthesize from the rest — partial coverage beats none. For very large panels, dispatch in concurrent batches rather than blocking on all at once.

### 3. SYNTHESIZE — merge into one verdict

The panel returns many overlapping voices. Turn that into a decision:

1. **Normalize** each finding to: severity, confidence (1-10), `path:line`, perspective, problem, suggested direction.
2. **Deduplicate** by fingerprint (`path:line:category`). When several perspectives raise the same issue, keep the strongest evidence, tag it `confirmed by N perspectives`, and raise confidence — agreement is signal.
3. **Surface conflicts, don't bury them.** When two lenses disagree (Beck: "delete this abstraction, YAGNI" vs system-architect: "keep it for the planned extension"), present both as a trade-off for the author to decide. Conflicting expert opinion is a finding, not noise.
4. **Contrast against intent.** Build a requirement-coverage view from the PR body / linked issue: each stated requirement marked satisfied / partial / missing / changed. An unmet requirement is at least HIGH.
5. **Rank** by severity (see rubric) then confidence. Drop confidence < 4 to an appendix.
6. **Decide one verdict:** `Request changes` if any CRITICAL/HIGH or unmet requirement remains; `Comment` if only MEDIUM/LOW notes; `Approve` if nothing blocks. State residual risk either way.

Severity rubric:

| Severity | Meaning |
|---|---|
| CRITICAL | likely data loss, auth bypass, outage, or unsafe deploy |
| HIGH | likely bug/regression, broken contract, or unmet requirement before merge |
| MEDIUM | plausible defect, missing test for risky behavior, near-term maintainability risk |
| LOW | minor issue, readability, local polish |
| INFO | useful note, not a finding |

### 4. REPORT — the output contract

Always lead with the verdict and the blocking items. Use this structure:

```text
PR Review — <title>  (PR #<id>, <base> <- <head>)
Verdict: REQUEST CHANGES | COMMENT | APPROVE
Panel: <N specialists + M personas>   CI: <pass/fail/none>

Blocking findings
- [HIGH] path/to/file.ext:42 - concise problem   (confirmed by: security, Dean)
  Evidence:
  Impact:
  Suggested fix:

Non-blocking notes
- [MEDIUM] ...
- [LOW] ...

Requirement coverage
- <requirement> : satisfied | partial | missing | changed (note)

Trade-offs raised (conflicting perspectives)
- <perspective A view>  vs  <perspective B view> — author decides

Residual risk
- <what the panel could not verify; CI gaps; needs-confirmation items>

Handoff
- Recommended next: /fix | /improve | /verify-implementation | /ship
```

When nothing blocks, say so plainly and state residual risk — do not pad with invented findings.

### 5. POST — only on explicit confirmation

If the user asked to post (or used `--post`), draft the comment, **show it and the exact command**, and confirm before running. Default to a single structured summary review comment; offer inline comments only if asked.

- **GitHub:** review state + body —
  `gh pr review <id> --request-changes --body-file <draft>` (or `--comment` / `--approve`), or a plain `gh pr comment <id> --body-file <draft>`.
- **GitLab:** `glab mr note <id> --message <draft>` for a summary note (and `glab mr approve <id>` only if explicitly approving).

Never post on the user's behalf without the confirm step. Map the verdict to the review state (`Request changes` -> `--request-changes`, etc.) but let the user override.

## What's automated vs what needs your taste

| Automated | You decide |
|---|---|
| Platform + PR resolution, context packet | Which PR when ambiguous |
| Scope-lens selection from the diff | Whether to force or skip a lens |
| Panel dispatch + dedupe + confidence | Whether a finding is acceptable to ship |
| Verdict draft from severity | Final approve / request-changes call |
| Comment + command draft | Whether and what to post to the PR |

## Forbidden

- Merge, close, push, or edit source files.
- Post any comment or review state without an explicit confirm.
- Invent findings, tests, metrics, or requirements not present in the change or its stated intent.
- Treat "CI passed" as a substitute for reading the diff.
- Collapse conflicting expert opinions into a single fake consensus.
- Report findings without `file:line` evidence or an explicit evidence gap.

## Pitfalls

| Pitfall | Symptom | Prevention |
|---|---|---|
| Panel theater | 19 reviewers, one real finding, lots of restated obvious points | Dedupe hard; only surface findings with evidence; out-of-scope lenses return NO FINDINGS |
| Intent blindness | Clean code, but it shipped the wrong thing | Always build the requirement-coverage view from the PR body / issue |
| False consensus | Trade-offs hidden behind a tidy verdict | Surface conflicting perspectives as explicit trade-offs |
| Accidental posting | A comment lands on a real PR unasked | Confirm-gate every network write; show command first |
| Cost blowup | Every tiny PR runs the full panel slowly | Honor the thorough default, but offer `--personas none` / `--scope` for light runs |

## Self-check before returning

- [ ] Platform and PR resolved (or asked).
- [ ] Stated intent + linked issue pulled; requirement coverage built.
- [ ] Full panel dispatched (or scope/personas narrowing was explicit).
- [ ] Findings deduped, confidence reflects cross-perspective agreement.
- [ ] Conflicts surfaced as trade-offs, not buried.
- [ ] One clear verdict with blocking items first; residual risk stated.
- [ ] Nothing posted without explicit confirmation.

## Supporting files

| File | Purpose |
|---|---|
| [references/perspectives.md](references/perspectives.md) | Full catalog: each perspective's questions, red flags, and when it matters most |
| [references/example-review.md](references/example-review.md) | A worked PR review with a BEFORE/AFTER and a full report example |
