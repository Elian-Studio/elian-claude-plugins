---
name: implement
description: "When the user asks to implement a feature, build a new capability, or runs /implement, drive the work through TDD with a parallel-or-sequential plan: gather context, propose a plan, gate user approval, run Red→Green→Refactor with conflict-free file ownership, verify, and report."
when_to_use: Use ONLY for new feature work invoked via /implement or explicit 'build / implement / add this feature' phrasing. Do NOT use for bug fixes (use /fix), behavior-preserving refactors (use /improve only when the user wants improvement, not pure rename), or single-line config edits.
argument-hint: "<issue-id> [--side back|front|both] [--step N] [--skip-docs]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git status*), Bash(git branch*), Bash(git diff*), Bash(npm test*), Bash(npm run*), Bash(./gradlew test*), Bash(mvn test*), Bash(pytest*), Bash(go test*), Bash(rspec*), AskUserQuestion, Agent
disable-model-invocation: true
---

# /implement — TDD-driven feature implementation

When the user wants to build a new feature, this skill walks the work through a TDD pipeline: read the project, gather feature requirements, plan with explicit file ownership, gate user approval, run Red→Green→Refactor (parallel where safe), verify, review, and report.

## Parameters

| Option | Meaning | Default |
|--------|---------|---------|
| `<issue-id>` | Issue identifier (required) | — |
| `--side back\|front\|both` | Limit to one layer | `both` |
| `--step N` | Resume from a specific step | `1` |
| `--skip-docs` | Skip design-doc generation | `false` |

## Workflow

```
Step 0: Project recognition (CLAUDE.md scan)
Step 1: Context gathering
Step 2: Plan + conflict matrix
Step 3: ★ Approval gate ★          ← user owns this
Step 4: TDD execution (single direct or parallel via Subagent / Agent Team)
Step 5: Integration verification
Step 6: Code review
Step 7: Completion report
```

### Step 0: Project recognition

Read `CLAUDE.md` plus any `*/CLAUDE.md` to capture tech stack, build / test commands, and conventions. If absent, ask the user before proceeding.

### Step 1: Context gathering

1. `git status && git branch --show-current` — if on the main branch, prompt for a feature branch.
2. Look for design docs at `**/docs/**/$ARGUMENTS[0]/**/*.md`.
   - Found: extract requirements, scope, API contract.
   - Missing: ask the user (skip when `--skip-docs`).
3. Read existing patterns in the affected domain to match conventions.

### Step 2: Plan

1. **Decompose** the request into independent feature units (each with files + dependencies).
2. **Conflict matrix** (multi-feature only): build the file-overlap matrix; identify parallelizable groups.
3. **Execution strategy** (use [../_shared/execution-strategy.md](../_shared/execution-strategy.md)):
   - 1 unit → direct
   - N units, no conflicts, no inter-worker debate → Subagent (parallel)
   - N units, mid-flight contract negotiation needed → Agent Team
4. **Build order**: backend (model → repository → service → API) then frontend (API client → state → UI).

Templates: see [references/templates.md](references/templates.md).

### Step 3: ★ Approval gate ★

Use `AskUserQuestion` with options: approve / modify / cancel. **Do not proceed to Step 4 without explicit approval.** This is a hard rule.

### Step 4: TDD execution

For each file unit, run **Red → Green → Refactor**:

1. **Red** — write failing tests covering boundaries, state transitions, error paths.
2. **Green** — minimum implementation that passes the tests.
3. **Test run** — PASS → next; FAIL → fix.
4. **Refactor** — improve while keeping tests green.
5. **Incremental checkpoint** — keep each feature unit reviewable in the diff.
   Commit only when the user requested it; use a host-provided `/commit` skill
   when available, otherwise leave the verified changes uncommitted.

For parallel multi-feature work, see the spawn prompt template in [references/templates.md](references/templates.md).

### Step 5: Integration verification

Run the repository's documented test, lint, typecheck, and build commands. If
project-local `verify-*` skills exist, run the relevant ones as an additional
layer; their names are project capabilities, not bundled dependencies.

### Step 6: Code review

Review the diff directly for unnecessary complexity, broken contracts, and
missing tests. A host-provided `/simplify` or `/code-reviewer` may be offered as
an optional extra; the core workflow must complete without either one.

### Step 7: Completion report

Output a report following [references/templates.md](references/templates.md). Required fields:

- Summary (file counts, test counts, commit counts)
- Per-feature outcome (when multi-feature)
- Verification results
- Next steps

## Standing Rules

- **Approval-gated**: Step 3 must complete before Step 4. Never skip.
- **TDD non-negotiable**: tests precede implementation. No exceptions for "trivial" features — they're often where edge cases hide.
- **File ownership over parallelism**: never spawn parallel workers on overlapping files. Conflicts are deterministic, not probabilistic.
- **Conventions over novelty**: follow existing project patterns. New abstractions need 3 use sites of justification.
- **Commit per unit**: feature-sized commits, not megacommits. Each commit reviewable in isolation.
- **No half-finished work**: if a feature unit fails Step 4, finish or roll back. Never leave partial state on disk.

## Procedure (one-time)

`/implement <issue-id>` runs Step 0 → 7 in order. Skip steps only when explicitly directed (`--step N`) or when an Exception below applies.

## Forbidden

- ❌ Skipping Step 3. The user owns approval; bypass = breach of trust.
- ❌ Implementing without a failing test first. "I'll add tests after" never happens reliably.
- ❌ Two parallel workers touching the same file. The conflict matrix exists for this reason.
- ❌ Committing all features as one giant commit. Reviewers cannot bisect.
- ❌ "While I was in there" refactors mixed into a feature commit. Separate concerns.
- ❌ Adding error handling for impossible cases. Validate at boundaries; trust internal calls.
- ❌ Overriding the user's approval decision because "the right answer is obvious." It isn't.
- ❌ Switching strategy mid-execution (e.g., Subagent → direct) without re-gating.

## Pitfall / Known Issues

| Pitfall | Why it happens | Fix |
|---------|----------------|-----|
| Tests pass but feature is wrong | Tests written from the implementation, not the requirement | Write tests from the requirement, before reading any existing code |
| Conflict matrix missed a hidden dep | Shared util / config / migration not declared | Re-scan: any imports / calls / env-var reads count as deps |
| Parallel workers break each other's commits | One worker rebases another's branch | Each worker on its own branch; main lead merges sequentially |
| Tests pass locally but fail in CI | Time-zone, locale, FS-case-sensitivity drift | Run with the project's CI-equivalent commands; capture full env |
| "TDD too slow" tempts skipping Red | Pressure to ship | Skip tests now = debug for 3× the time later. Don't. |
| Approval feedback ignored | Lead drafts plan and sprints past `AskUserQuestion` | Treat the answer as a contract; mid-stream changes need a re-gate |

For failure recovery: every Step has an explicit fail action — Step 4 fail → fix or revert; Step 5 fail → roll back the offending unit; Step 6 fail → re-run Step 4 on flagged files. Never silently skip.

## Where this fits in the workflow

```
brainstorm → /generate-teammate (if multi-domain) → /implement → /review
                                                       │
                                                       └── This skill builds the feature.
                                                           Pre: requirements settled.
                                                           Post: PR-ready code + tests.
```

Sequencing principles:
- **Before** /implement: requirements clear (use /brainstorm if fuzzy). Design doc exists or is intentionally skipped.
- **During** /implement: each step's exit criterion must hold before the next begins.
- **After** /implement: hand off to `/review`. If the host provides a release
  or documentation workflow, offer it explicitly rather than assuming it exists.

## Manual decision gating (automated vs taste)

| Concern | Automated | Needs user taste |
|---------|-----------|------------------|
| Project tech-stack detection (CLAUDE.md scan) | ✅ | — |
| Feature decomposition into units | ✅ | — |
| File-conflict matrix | ✅ | — |
| Strategy selection (direct / Subagent / Team) per shared rules | ✅ | — |
| Test cases for boundary / null / error | ✅ | — |
| Approval to proceed past Step 3 | — | ✅ (hard gate) |
| Domain naming, API shape, UX wording | drafted automatically | ✅ user reviews |
| Whether a borderline feature deserves multi-PR split | — | ✅ |
| Whether to bypass Step 5 (skip verify) | — | ✅ explicit only |

The automated decisions are deterministic given the same input. The taste decisions require human context the skill cannot infer.

## Reflection (end of skill)

After Step 7, write 3 short observations into `claudedocs/{issueId}-implement-reflection.md`:

1. **Test gaps caught** — what edge cases did Red surface that the requirements doc missed?
2. **Parallelism payoff** — was the chosen strategy (direct vs Subagent vs Team) the right call? Where did it stall?
3. **Convention drift** — did this feature fit existing patterns, or did it suggest a new pattern needs discussion?

These feed into future planning (over time, repeated drift signals a refactor candidate).

## Persistent artifacts for downstream

| Artifact | Producer step | Downstream consumer |
|----------|---------------|---------------------|
| Feature decomposition + conflict matrix | Step 2 | /review (knows which files relate to which feature) |
| TDD test files | Step 4 | /review, CI, future regression detection |
| Per-feature commits | Step 4 | /review (one commit = one reviewable unit), bisect tooling |
| Verification report | Step 5 | Reviewer or optional host release workflow |
| Completion report | Step 7 | Post-mortem, retro, project-history |

## BEFORE / AFTER patterns

### Test-first vs implementation-first

❌ **BEFORE**:

```
1. Write the implementation
2. Add tests later "to cover it"
3. Realize tests just validate what was built — not the requirement
```

The tests confirm the bug, not the requirement. Useless for catching the next regression.

✅ **AFTER (TDD)**:

```
1. Read the requirement; write tests for it (Red)
2. Implement the minimum to make Red turn Green
3. Refactor with green tests as a safety net
```

Tests express the requirement, independent of implementation. Refactors won't break them.

### Single mega-commit vs incremental

❌ **BEFORE**:

```
git add -A
git commit -m "Implement feature X"
```

Reviewer must read 800-line diff. Bisect can't pinpoint regressions. Rollback is all-or-nothing.

✅ **AFTER**:

```
commit 1: Add Order entity + repository (BE)
commit 2: Add OrderService + tests (BE)
commit 3: Wire OrderController + integration tests (BE)
commit 4: Add api-client.ts for orders (FE shared)
commit 5: Add OrderListPage + component tests (FE)
commit 6: Add OrderDetailPage + state wiring (FE)
```

Each commit reviewable, bisectable, revertable.

### Parallel without ownership vs with ownership

❌ **BEFORE — undeclared shared file**:

```
worker-1 (BE)  → src/api/orders.ts, src/utils/format.ts
worker-2 (FE)  → src/components/Order.tsx, src/utils/format.ts
                                                   ^^^^^^^^^^^^ both touched
```

Last writer wins. Subtle bug surfaces at integration.

✅ **AFTER — explicit conflict matrix**:

```
            worker-1   worker-2
worker-1     —          ❌ shared: src/utils/format.ts
worker-2     ❌          —

Resolution: extract format change to its own commit before parallel work,
            OR assign format.ts to a single owner.
```

## Skill verification

```bash
python3 tools/validate_skill.py plugins/elian-store/skills/implement
python3 tools/validate_skill.py plugins/elian-store/skills/implement --json
```

The shared validator (`tools/validate_skill.py`, stdlib only, argparse + `--json`) checks: frontmatter has the required fields and `name` matches the directory, the invocation gate is set, the body contains the required policy sections (Workflow / Standing Rules / Forbidden / Pitfall / Where this fits / Manual gating / Reflection / Persistent artifacts / BEFORE-AFTER / Pre-flight), and `references/` exists and is linked. Exits 0 on PASS, 1 on FAIL. `brainstorm`, `fix`, `implement`, and `improve` share it rather than each carrying a copy.

## Pre-flight checklist

Before Step 4 (TDD execution), confirm:

- [ ] Project recognized (Step 0 outputs captured)
- [ ] Requirements clear (from design doc or user dialogue)
- [ ] Feature decomposition complete with file lists
- [ ] Conflict matrix built (multi-feature only)
- [ ] Execution strategy chosen with cited rationale
- [ ] User approved via AskUserQuestion (Step 3)

## Skill integrations

| Skill | Step |
|-------|------|
| `/commit` | Optional host capability, only when the user requested commits |
| project `verify-*` | Optional project-local checks after documented commands |
| `/simplify`, `/code-reviewer` | Optional host capabilities after direct review |
| `/generate-teammate` | Step 4 — when 4+ parallel features warrant a team |
| `/defer` | Optional host capability; otherwise record follow-up work in the report |

## Exceptions

1. **Single-file trivial change**: skip parallelization; still TDD.
2. **Configuration-only change**: TDD not applicable; build verification only.
3. **Shared-module change**: scan dependents; run their tests too.
4. **No CLAUDE.md**: ask the user for stack and conventions before Step 1.
