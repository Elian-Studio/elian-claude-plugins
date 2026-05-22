---
name: fix
description: When the user reports a bug, asks to fix something, or runs /fix, drive the work through root-cause analysis → planning → user approval → TDD repair (regression test first) → verification → review → report, with conflict-free file ownership for multi-symptom fixes.
when_to_use: Use ONLY for bug repair invoked via /fix or explicit 'fix this bug', 'something broken', 'X is wrong' phrasing. Do NOT use for new features (use /implement) or behavior-preserving improvements (use /improve).
argument-hint: <issue-id> [--side back|front|both] [--step N] [--skip-docs]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git status*), Bash(git branch*), Bash(git diff*), Bash(git log*), Bash(npm test*), Bash(npm run*), Bash(./gradlew test*), Bash(mvn test*), Bash(pytest*), Bash(go test*), Bash(rspec*), AskUserQuestion, Agent
disable-model-invocation: true
---

# /fix — Root-cause-first bug fix

When the user reports a bug, this skill walks the work through root-cause analysis, then TDD repair starting with a failing regression test, with explicit gating for user approval.

## Parameters

| Option | Meaning | Default |
|--------|---------|---------|
| `<issue-id>` | Issue identifier (required) | — |
| `--side back\|front\|both` | Limit to one layer | `both` |
| `--step N` | Resume from a specific step | `1` |
| `--skip-docs` | Skip design-doc generation | `false` |

## Workflow

```
Step 0: Project recognition
Step 1: Bug analysis (symptom + root cause)
Step 2: Repair plan (multi-symptom decomposition + conflict matrix)
Step 3: ★ Approval gate ★
Step 4: TDD repair (regression test first → fix → verify)
Step 5: Integration verification
Step 6: Code review
Step 7: Completion report
```

### Step 0: Project recognition

Read `CLAUDE.md` plus any `*/CLAUDE.md` for tech stack, build / test commands, conventions. If absent, ask the user.

### Step 1: Bug analysis

1. `git status && git branch --show-current` — if on main, prompt for a feature branch.
2. **Symptom enumeration**: list each observed symptom (description, repro condition, blast radius).
3. **Root cause analysis**: for each symptom, trace code to the root cause.
   - Symptom → proximate cause → root cause → affected files.

> **Do not proceed to Step 2 without a confirmed root cause.** If unclear, request more information (logs, repro steps) from the user.

Templates: see [references/templates.md](references/templates.md).

### Step 2: Repair plan

1. **Symptom-to-fix mapping**: symptom / root cause / files to change / regression test.
2. **Conflict matrix** (multi-symptom): identify file overlap; mark parallelizable groups.
3. **Execution strategy** (use [../_shared/execution-strategy.md](../_shared/execution-strategy.md)):
   - 1 symptom → direct
   - N symptoms, no overlap → Subagent (parallel)
   - Symptoms intertwined or hypothesis-competing → Agent Team

### Step 3: ★ Approval gate ★

`AskUserQuestion` with options approve / modify / cancel. **No Step 4 without approval.**

### Step 4: TDD repair

**Regression test first** — unlike `/implement`, the failing test reproduces the bug:

1. **Regression test (Red)** — write a test that reproduces the bug (must fail now).
2. **Fix (Green)** — change the code so the test passes.
3. **Existing tests** — run the full relevant suite; ensure no collateral damage.
4. **Refactor** — clean up while keeping tests green.
5. **Commit per symptom** via `/commit`.

Parallel multi-symptom fixes use the spawn prompt template in [references/templates.md](references/templates.md).

### Step 5: Integration verification

Run project verify skills (`/verify-backend`, `/verify-frontend`, etc.). For cross-layer fixes also `/verify-api-contract`.

**Critical**: also run tests for modules you did **not** touch — root-cause fixes can have invisible blast radius.

### Step 6: Code review

Run `/simplify` and check:
- Does the fix address the root cause, not the symptom?
- Are there sibling sites with the same root cause?

Stage review fixes via `/commit`.

### Step 7: Completion report

See [references/templates.md](references/templates.md). Required fields:
- Summary (file counts, regression-test counts, commit counts)
- Per-symptom: root cause → fix outcome
- Verification (with side-effect check)
- Next steps

## Standing Rules

- **Root cause before fix**: never patch the symptom. If you can't name the root cause, you don't have a fix.
- **Regression test first**: the test must reproduce the bug before any code changes.
- **Approval-gated**: Step 3 must complete; do not skip.
- **Sibling-site search**: every root cause is a hypothesis that other places have the same bug. Search before declaring done.
- **Side-effect verification**: tests for modules you didn't touch. Bugs hide in seams.
- **Commit per symptom**: each fixed symptom = its own commit. Reviewers and bisect benefit.

## Procedure (one-time)

`/fix <issue-id>` runs Step 0 → 7. Resume with `--step N`. Don't skip Step 1 even if the bug "looks obvious" — the visible symptom and the root cause diverge often.

## Forbidden

- ❌ Patching the symptom without finding the root cause. The bug returns under a different name.
- ❌ Writing the fix before the failing regression test. The fix may pass tests for the wrong reason.
- ❌ Skipping Step 3 approval. The user owns scope.
- ❌ Skipping verification of unchanged modules. Root-cause fixes can radiate.
- ❌ "I'll add a test later" — adding tests after often misses the original failure mode.
- ❌ Bundling several symptom fixes into one commit. Bisect can't separate them.
- ❌ Catching exceptions to make the test pass without fixing the cause.
- ❌ Editing tests to match buggy behavior. The test is the contract; the bug is the violation.

## Pitfall / Known Issues

| Pitfall | Why it happens | Fix |
|---------|----------------|-----|
| Fix passes the regression test but breaks unrelated module | Shared state / global mutation | Run the full suite; check for hidden coupling |
| Root cause appears to be in third-party lib | True sometimes, often a misuse on our side | Read the docs; build a minimal repro outside our codebase |
| "Cannot reproduce" | Environment, data, or timing dependency | Capture exact conditions; if non-deterministic, log + extend test until reproducible |
| Symptom returns after weeks | Sibling sites had same root cause | Step 6 search wasn't thorough; widen grep / re-audit |
| Race condition fix randomly fails | Test timing-dependent | Make the test deterministic (fake clock, controlled scheduler) |
| Fix breaks the design intent | Design doc has a contradicting requirement | Loop back to design doc; talk to the requirement owner |

For failure recovery: every Step has an explicit fail action — Step 1 fail (root cause unclear) → request more info, do not proceed; Step 4 fail (Green won't hold) → re-examine root cause; Step 5 fail (side effect) → roll back, widen search.

## Where this fits in the workflow

```
bug reported → /investigate (if cause unknown) → /fix → /review → /ship
                                                  │
                                                  └── This skill: TDD-driven repair.
                                                      Pre: cause known (or willing to dig).
                                                      Post: PR-ready fix + regression tests.
```

Sequencing principles:
- **Before** /fix: have at least a hypothesis (gathered via /investigate or user dialogue). If the cause is opaque, run /investigate first.
- **During** /fix: regression test must come before the patch.
- **After** /fix: hand off to /review (PR review) and /ship (release).

## Manual decision gating (automated vs taste)

| Concern | Automated | Needs user taste |
|---------|-----------|------------------|
| Project recognition | ✅ | — |
| Symptom enumeration from inputs | ✅ | — |
| Root-cause search via grep / read | ✅ | — |
| Conflict matrix for multi-symptom | ✅ | — |
| Strategy selection per shared rules | ✅ | — |
| Regression test draft | ✅ | — |
| Approval to proceed past Step 3 | — | ✅ |
| "Is this the real root cause?" judgement | drafted automatically | ✅ user reviews |
| Whether to escalate (/investigate, on-call) | — | ✅ |
| Whether to ship a hotfix vs a full fix | — | ✅ |

## Reflection (end of skill)

Write 3 short observations into `claudedocs/{issueId}-fix-reflection.md`:

1. **Distance from symptom to root cause** — how many layers of indirection? Long chains hint at architectural smell.
2. **Sibling-site discovery** — were similar bugs found elsewhere? If yes, the root cause likely deserves a structural fix.
3. **Test gap** — which test, if it had existed, would have caught this? Add it now if affordable.

These feed into post-mortems and refactor candidates.

## Persistent artifacts for downstream

| Artifact | Producer step | Downstream consumer |
|----------|---------------|---------------------|
| Symptom + root-cause table | Step 1 | Post-mortem, retro |
| Repair plan + conflict matrix | Step 2 | /review (knows what each fix targets) |
| Regression tests | Step 4 | CI (prevent regression), future similar bugs |
| Side-effect verification report | Step 5 | /ship (release readiness) |
| Completion report | Step 7 | Project history; root-cause stats |

## BEFORE / AFTER patterns

### Symptom patch vs root-cause fix

❌ **BEFORE**:

```
Symptom: List endpoint returns 500 sometimes.
Patch: try { ... } catch (Exception e) { return [] }
```

The 500 stops, but the bug (e.g., race in cache warm-up) still happens — now silently returns empty data.

✅ **AFTER**:

```
Root cause: cache populated lazily; first request after restart races
the populator, which throws NPE on uninitialized map.
Fix: initialize cache eagerly during application startup.
Regression test: simulate fresh-start race; assert successful response.
```

The test reproduces the original symptom. The fix removes the cause, not the visibility.

### Test-after vs test-before

❌ **BEFORE**:

```
1. Diagnose bug; write fix
2. Tests still pass
3. Commit
4. (No test asserting the fix works)
```

Future regression invisible to the suite.

✅ **AFTER**:

```
1. Diagnose bug
2. Write failing regression test that reproduces it
3. Run: test fails (Red)
4. Apply fix
5. Run: test passes (Green); existing suite still green
6. Commit (test + fix together)
```

Suite now guards the fix.

### Patch one site vs audit siblings

❌ **BEFORE**:

```
Bug at services/user.ts:42. Fix: same.
(Two months later, identical bug at services/order.ts:88.)
```

Same root cause, different file. Two incidents instead of one.

✅ **AFTER**:

```
After fix at services/user.ts:42:
grep -rn "{root-cause-pattern}" src/
→ Found 4 sibling sites. Audit each.
→ 2 had same bug, 2 were fine.
Fix all in one PR with shared regression tests.
```

## Skill verification

```bash
python3 [scripts/validate_skill.py](scripts/validate_skill.py)
python3 [scripts/validate_skill.py](scripts/validate_skill.py) --json
```

## Pre-flight checklist

Before Step 4 (TDD repair):
- [ ] Project recognized
- [ ] Symptoms enumerated with repro conditions
- [ ] Root cause confirmed for each symptom
- [ ] Conflict matrix built (multi-symptom)
- [ ] Execution strategy chosen with rationale
- [ ] User approved via AskUserQuestion (Step 3)
- [ ] Regression test plan drafted

## Skill integrations

| Skill | Step |
|-------|------|
| `/commit` | Step 4 — incremental commits (mandatory) |
| `/verify-*` | Step 5 — integration verification |
| `/simplify` | Step 6 — self-review |
| `/investigate` | Pre-Step 1 — when cause unknown |
| `/generate-teammate` | Step 4 — 4+ symptoms warrant a team |
| `/defer` | Out-of-scope discoveries |

## Exceptions

1. **Single-file 1-line fix**: still TDD; the regression test is cheap.
2. **Configuration error**: TDD not applicable; smoke-test the config in CI.
3. **Shared-module bug**: dependent modules' tests are part of Step 5 — non-negotiable.
4. **Cannot reproduce**: do not "fix" guesses. Block on Step 1 until reproducible.
