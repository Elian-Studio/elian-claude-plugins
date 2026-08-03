---
name: verify-before-claiming
description: "Claim-time honesty gate: never assert that work passes, is fixed, builds, or is done without having run the proving command in this same message and read its output. Forces fresh evidence before any success or completion claim, including before commit/PR and before trusting a subagent's success report."
when_to_use: "Use the instant before any completion, pass, fixed, builds, or 'works now' claim — including before commit/PR, before moving to the next task, and before trusting a subagent's success report. This is a claim-time evidence gate, NOT a verification-suite runner: to discover and run project verify-* skills use /verify-implementation; to track which PRD acceptance criteria a passing test proves use /spec-coverage; to review someone else's diff use /review. Triggers: about to write 'tests pass', 'done', 'fixed', 'should work', 'looks correct', or any satisfaction phrase about work state."
argument-hint: "(no args — a claim-time gate; optionally name the claim to prove)"
allowed-tools: Read, Glob, Grep, Bash(git status*), Bash(git diff*), Bash(git log*), Bash(npm test*), Bash(npm run*), Bash(./gradlew*), Bash(mvn test*), Bash(pytest*), Bash(go test*), Bash(cargo test*), Bash(rspec*)
disable-model-invocation: false
---

# /verify-before-claiming — Evidence before claims

Claiming work is complete without verification is dishonesty, not efficiency. This skill is the
honesty gate that fires the instant before any success or completion claim: identify the command
that proves the claim, run it fresh in this message, read the output, and only then make the claim
— with the evidence attached.

**Core principle:** Evidence before claims, always. Violating the letter of this rule violates its
spirit — a paraphrase, synonym, or implied success is still a claim.

## The Iron Law

```
NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION EVIDENCE
```

If you have not run the proving command **in this message**, you cannot say it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY  — what command proves this exact claim?
2. RUN       — execute the FULL command, fresh and complete
3. READ      — full output, exit code, count of failures
4. VERIFY    — does the output actually confirm the claim?
                 NO  → state the real status with evidence
                 YES → state the claim WITH the evidence
5. ONLY THEN — make the claim

Skipping any step is lying, not verifying.
```

## Claim → Requires → Not sufficient

| Claim | Requires | Not sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures, fresh run | A previous run, "should pass" |
| Linter clean | Linter output: 0 errors | "build succeeds", partial check |
| Build succeeds | Build command: exit 0 | Linter passing, logs "look fine" |
| Bug fixed | Re-test the original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red→green cycle verified (revert fix → fails) | Test passes once |
| Requirements met | Line-by-line checklist against the spec | "tests pass, so it's done" |
| Subagent completed | VCS diff shows the actual changes | The agent's "success" report |

## Red flags — STOP and run the command

- Using "should", "probably", "seems to", "looks correct".
- Expressing satisfaction before evidence ("Great!", "Perfect!", "Done!").
- About to commit / push / open a PR without a fresh verification run.
- Trusting a subagent's success report instead of the diff.
- Relying on a partial or earlier check.
- Thinking "just this once" or tired and wanting it over.
- **Any wording implying success without having run verification this message.**

## Rationalization table

| Excuse | Reality |
|--------|---------|
| "Should work now" | Run the verification. |
| "I'm confident" | Confidence is not evidence. |
| "Just this once" | No exceptions. |
| "Linter passed" | Linter is not the compiler. |
| "The agent said success" | Verify independently from the diff. |
| "I'm tired" | Exhaustion is not an excuse. |
| "Partial check is enough" | Partial proves nothing. |
| "Different words, so the rule doesn't apply" | Spirit over letter. |

## When to apply

Always, before: any success/completion/pass/fixed claim, any expression of satisfaction about work
state, committing, opening a PR, moving to the next task, or relaying a subagent's result. The rule
covers exact phrases, paraphrases, synonyms, and anything implying the work is correct.

## Standing Rules

- **Run, read, then claim.** The command output is the only thing that licenses the claim.
- **Fresh and full.** A stale or partial run does not count; run the complete command this message.
- **Attach the evidence.** State the proof inline (e.g. `34/34 passed`, `exit 0`), not just the verdict.
- **Verify subagents from the diff**, never from their self-report.
- **No suite-running here.** This gate proves the claim you are about to make; to orchestrate the
  project's verify-* skills use `/verify-implementation`.

## Forbidden

- ❌ Saying "tests pass" / "fixed" / "done" / "should work" without a fresh proving run this message.
- ❌ Expressing satisfaction ("Great!", "Perfect!") before the evidence exists.
- ❌ Committing, pushing, or opening a PR on an unverified claim.
- ❌ Trusting a subagent's success report without checking the VCS diff.
- ❌ Treating a paraphrase or synonym as exempt from the rule.

## Pitfalls

| Pitfall | Why it happens | Fix |
|---------|----------------|-----|
| "Linter passed, so it builds" | Conflating distinct checks | Each claim needs its own proving command |
| Regression test that never failed | Skipped the red step | Revert the fix, confirm the test fails, restore |
| Reporting a subagent "done" | Trusting the report | Read the diff before relaying |
| Stale green from an earlier run | Reusing old output | Re-run fresh in the claiming message |
| Requirements "met" via tests only | Tests ≠ spec coverage | Line-by-line checklist against the spec |

## Validation

```bash
python3 plugins/elian-store/skills/verify-before-claiming/scripts/validate_skill.py
python3 plugins/elian-store/skills/verify-before-claiming/scripts/validate_skill.py --json
```

## Pre-flight checklist

Before stating any completion/success claim:
- [ ] I identified the exact command that proves this claim
- [ ] I ran it fresh and complete in THIS message
- [ ] I read the full output and exit code
- [ ] The output confirms the claim (else I state the real status)
- [ ] The evidence is attached to the claim
- [ ] For subagent work, I checked the VCS diff, not the report
