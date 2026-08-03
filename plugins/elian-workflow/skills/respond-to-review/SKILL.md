---
name: respond-to-review
description: "Consumer side of code review: how to respond to review feedback on your own change with technical rigor — verify each suggestion against the codebase before implementing, no performative agreement, push back with reasoning when a suggestion is wrong, clarify everything ambiguous before acting, and YAGNI-check 'implement properly' asks."
when_to_use: "Use when receiving code-review feedback on YOUR change — from the user, from /pr-review output, or as external PR/MR comments — and deciding how to respond and what to implement. This is the consumer side of review. Do NOT use to produce a review (use /review or /pr-review), to draft a PR description (use /pr-writer), or to execute the fixes (hand to /fix or /improve). Triggers: 'address this review', 'respond to these comments', 'the reviewer said X', pasted PR feedback."
argument-hint: "(paste or reference the review feedback)"
allowed-tools: Read, Glob, Grep, Bash(git diff*), Bash(git log*), Bash(git status*), AskUserQuestion
disable-model-invocation: false
---

# /respond-to-review — Receiving code review with rigor

Code review is a technical evaluation, not an emotional performance. When feedback lands on your
change, verify each point against the codebase before implementing, acknowledge correct points by
fixing them (not by thanking), and push back with technical reasoning when a suggestion is wrong.

**Core principle:** Verify before implementing. Ask before assuming. Technical correctness over
social comfort. (This matches the repo's "be direct, skip filler" ethos.)

## The response pattern

```
WHEN feedback arrives:

1. READ       — the complete feedback, without reacting
2. UNDERSTAND — restate each item in your own words (or ask)
3. VERIFY     — check each suggestion against codebase reality
4. EVALUATE   — is it technically sound for THIS codebase?
5. RESPOND    — technical acknowledgment, or reasoned pushback
6. IMPLEMENT  — one item at a time, verify each (hand execution to /fix or /improve)
```

## Forbidden responses

**Never:**
- "You're absolutely right!" — performative, and a direct instruction-file violation.
- "Great point!" / "Excellent feedback!" — performative agreement.
- "Thanks for catching that!" / any gratitude — the fix in the code is the acknowledgment.
- "Let me implement that now" — before verifying against the codebase.

**Instead:** restate the technical requirement, ask a clarifying question, push back with reasoning,
or just make the fix. If you catch yourself about to write "Thanks" — delete it and state the fix.

## Clarify everything before acting

```
IF any item is unclear:
  STOP — implement nothing yet
  ASK for clarification on the unclear items first
WHY: items may be related; partial understanding produces the wrong implementation.
```

Example — you understand items 1, 2, 3, 6 but not 4, 5:
> ✅ "I understand 1, 2, 3, 6. I need clarification on 4 and 5 before implementing."
> ❌ Implement 1, 2, 3, 6 now and ask about 4, 5 later.

## Source-specific handling

**From the user (trusted):** implement after understanding; still ask if scope is unclear; no
performative agreement — skip to a technical acknowledgment or just act.

**From external reviewers (be skeptical, verify carefully):**
```
BEFORE implementing, check:
  1. Technically correct for THIS codebase / stack?
  2. Does it break existing functionality?
  3. Is there a reason the current implementation is the way it is?
  4. Does it hold on all supported platforms/versions?
  5. Does the reviewer have the full context?
IF it seems wrong   → push back with technical reasoning
IF you can't verify → say so: "I can't verify this without [X]. Investigate / ask / proceed?"
IF it conflicts with the user's prior decisions → stop and discuss first
```

## YAGNI check on "implement properly"

```
IF a reviewer asks to "implement properly" / add a fuller version:
  grep the codebase for actual usage
  IF unused → "Nothing calls this. Remove it (YAGNI)?"
  IF used   → then implement it properly
```

## When to push back

Push back when a suggestion breaks existing functionality, the reviewer lacks context, it violates
YAGNI, it is technically wrong for this stack, legacy/compatibility reasons exist, or it conflicts
with the user's architectural decisions. Use technical reasoning and reference working tests/code —
not defensiveness. If you pushed back and were wrong, correct it factually and move on
("Verified — you're right, [X] does [Y]. Fixing.") without a long apology.

## Implementation order

```
1. Clarify anything unclear FIRST
2. Then: blocking issues (breaks, security) → simple fixes (typos, imports) → complex (refactors, logic)
3. Verify each fix individually (see /verify-before-claiming); confirm no regressions
4. Hand the actual edits to /fix (bug) or /improve (behavior change)
```

## Standing Rules

- **Verify before implementing.** Check each suggestion against the codebase first.
- **No performative agreement, no thanks.** The fix in the code is the acknowledgment.
- **Clarify all ambiguous items before acting.** Partial understanding = wrong implementation.
- **Push back on wrong suggestions** with technical reasoning, not deference.
- **Triage, don't execute here.** Hand the edits to `/fix` or `/improve`.

## Forbidden

- ❌ "You're absolutely right!", "Great point!", "Thanks for catching that!", or any gratitude.
- ❌ Implementing a suggestion before verifying it against the codebase.
- ❌ Implementing the understood items while leaving related unclear items for later.
- ❌ Accepting an "implement properly" ask for code nothing calls (YAGNI).
- ❌ Doing the fixes inside this skill instead of handing off to /fix or /improve.

## Pitfalls

| Pitfall | Why it happens | Fix |
|---------|----------------|-----|
| Performative agreement | Social reflex | State the requirement or just act |
| Blind implementation | Treating review as orders | Verify against the codebase first |
| Batch without testing | Speed | One item at a time, verify each |
| Avoiding pushback | Discomfort | Technical correctness over comfort |
| Partial implementation | Skipping clarification | Clarify all items first |
| Adding unused "proper" feature | Reviewer assumption | grep for usage; YAGNI |

## GitHub thread replies

When replying to inline review comments on GitHub, reply in the comment thread
(`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a top-level PR comment.

## Validation

```bash
python3 plugins/elian-store/skills/respond-to-review/scripts/validate_skill.py
python3 plugins/elian-store/skills/respond-to-review/scripts/validate_skill.py --json
```

## Pre-flight checklist

Before implementing any review item:
- [ ] Read all feedback; restated each item (or asked)
- [ ] Verified each suggestion against codebase reality
- [ ] Clarified every ambiguous item BEFORE starting
- [ ] Pushed back (with reasoning) on anything wrong for this codebase
- [ ] No performative agreement or thanks in the response
- [ ] Handed the edits to /fix or /improve, verifying each
