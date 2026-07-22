---
name: finish-branch
description: "After implementation is complete and tests pass, decide how to integrate a development branch: verify tests, detect the workspace (normal repo / native worktree / detached HEAD), present a closed merge / push+PR / keep / discard menu, and execute the choice with strict safety invariants. Thin by design — it owns the disposition decision and cleanup, and delegates the full push+PR release flow to /ship and commit authoring to /commit when those host-provided skills are available, falling back to the plain git steps otherwise."
when_to_use: "Use when a feature branch is done, tests pass, and you need to decide what to do with it. Owns the keep/discard/local-merge paths and worktree cleanup. Do NOT use it as a release pipeline — for the push + version-bump + PR flow it prefers /ship if available; for commit messages it prefers /commit; for the PR body alone use /pr-writer. Triggers: 'finish this branch', 'wrap up this branch', 'merge or PR this?', 'what do I do with this branch'."
argument-hint: "[--base <branch>]"
allowed-tools: Read, Grep, Bash(git status*), Bash(git branch*), Bash(git diff*), Bash(git log*), Bash(git merge-base*), Bash(git rev-parse*), Bash(git checkout*), Bash(git pull*), Bash(git merge*), Bash(git push*), Bash(git worktree remove*), Bash(git worktree prune*), AskUserQuestion, EnterWorktree, ExitWorktree
disable-model-invocation: true
---

# /finish-branch — Disposition of a finished development branch

When implementation is complete, decide how to integrate the work through a closed menu, then
execute it safely. This skill is deliberately thin: it owns the *disposition decision* (merge /
push+PR / keep / discard) and worktree cleanup, and delegates the heavyweight release flow.

**Core principle:** Verify tests → detect workspace → present closed options → execute choice → clean up.

## Parameters

| Option | Meaning | Default |
|--------|---------|---------|
| `--base <branch>` | Base branch this split from | auto-detected (main/master) |

## Workflow

### Step 1: Verify tests

Run the project's test suite first. If tests fail, show the failures and stop — do not present the
menu. A branch is not finishable on red. (State the result with evidence per `/verify-before-claiming`.)

### Step 2: Detect the workspace

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
TOPLEVEL=$(git rev-parse --show-toplevel)
```

| State | Menu | Cleanup |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON` (normal repo) | 4 options | none |
| worktree, `TOPLEVEL` under `.claude/worktrees/` (harness-native) | 4 options | via `ExitWorktree` |
| worktree, `TOPLEVEL` under `.worktrees/` or `worktrees/` (self-owned) | 4 options | `git worktree remove` |
| worktree, other path (host-owned) | 4 options | leave to the harness |
| detached HEAD | 3 options (no local merge) | none / externally managed |

### Step 3: Determine the base branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Use `--base` if given; otherwise confirm: "This branch split from `main` — correct?"

### Step 4: Present the closed menu

Use `AskUserQuestion`. **Normal repo / named-branch worktree — exactly these 4:**

```
1. Merge back to <base> locally
2. Push and open a Pull Request
3. Keep the branch as-is (handle it later)
4. Discard this work
```

**Detached HEAD — exactly these 3** (no local merge): Push+PR / Keep / Discard.

Don't add explanation — keep the options concise. "What should I do next?" is the wrong, open-ended question.

### Step 5: Execute the choice

**Option 1 — Merge locally.** `cd` to the main repo root first; merge; re-run tests on the merged
result; only after the merge succeeds, clean up the worktree (Step 6), then delete the branch
(`git branch -d`). Order is load-bearing: merge → worktree remove → branch delete.

**Option 2 — Push + PR.** Prefer **`/ship`** for the full flow (detect base, tests, version bump,
CHANGELOG, commit, push, PR). `/ship` is host-provided, not part of this plugin — when it is not
available, do not stall and do not rebuild it: push the branch and open the PR directly, handing the
PR body to `/pr-writer` (bundled with this plugin).

```bash
git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
```

Then invoke `/pr-writer` — it owns `gh` / `glab` detection and the PR body, and this skill
deliberately does not pre-approve those CLIs.

**Keep the worktree** — it is needed to iterate on PR feedback.

**Option 3 — Keep as-is.** Report the branch and worktree path. No cleanup.

**Option 4 — Discard.** Confirm first — show the branch, the commit list, and the worktree path, and
require the user to type `discard` exactly. On confirmation: `cd` to the main repo root, clean up the
worktree (Step 6), then force-delete the branch (`git branch -D`).

If the tree is dirty before any of this, commit first — hand authoring to `/commit` when that
host-provided skill exists, otherwise write the message yourself and run `git add` / `git commit`.

### Step 6: Clean up the workspace

Only for Options 1 and 4 (2 and 3 always preserve the worktree).

- **Harness-native** (`TOPLEVEL` under `.claude/worktrees/`): use `ExitWorktree`
  (`action: remove`, `discard_changes: true` only when discarding) — do NOT raw-remove it.
- **Self-owned** (under `.worktrees/` or `worktrees/`): `cd` to the main repo root, then
  `git worktree remove "$TOPLEVEL"` and `git worktree prune`.
- **Host-owned** (any other path) or normal repo: leave the workspace in place; the harness owns it.

## Standing Rules — safety invariants

- **Verify tests before offering options.** Never present the menu on red.
- **Merge succeeds before worktree removal before branch deletion.** `git branch -d` fails while a
  worktree still references the branch.
- **Only remove worktrees you own.** `.claude/worktrees/` → `ExitWorktree`; `.worktrees/` → raw
  remove; anything else → leave it. Removing a harness-owned worktree creates phantom state.
- **`cd` to the main repo root before `git worktree remove`** — it fails silently from inside the worktree.
- **Typed `discard` confirmation** before any destructive delete.
- **Never force-push** without an explicit request.

## Forbidden

- ❌ Presenting the menu while tests fail.
- ❌ Reimplementing the push/bump/PR pipeline — Option 2 delegates to `/ship`, or falls back to a
  plain push + PR when `/ship` is unavailable. Never a version-bump/CHANGELOG flow of its own.
- ❌ Deleting a branch before removing the worktree that references it.
- ❌ Running `git worktree remove` from inside the worktree being removed.
- ❌ Removing a worktree you didn't create (no provenance check).
- ❌ Discarding without a typed `discard` confirmation.
- ❌ Force-pushing without an explicit request.

## Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Skipped test verification | Merge broken code / red PR | Always verify tests before the menu |
| Open-ended question | Decision drift | Present exactly 4 (or 3) closed options |
| Cleaned worktree on Option 2 | Lost the workspace for PR iteration | Cleanup only for Options 1 and 4 |
| Branch delete before worktree remove | `git branch -d` fails | Merge → remove worktree → delete branch |
| `worktree remove` from inside | Silent failure | `cd` to main root first |
| Removed harness-owned worktree | Phantom state | Provenance check; native → `ExitWorktree` |
| No discard confirmation | Accidental loss | Require typed `discard` |

## Quick reference

| Option | Merge | Push | Keep worktree | Delete branch |
|--------|-------|------|---------------|---------------|
| 1. Merge locally | yes | — | — | yes (`-d`) |
| 2. Push + PR (→ /ship, else push + `/pr-writer`) | — | yes | yes | — |
| 3. Keep as-is | — | — | yes | — |
| 4. Discard | — | — | — | yes (`-D`, after typed confirm) |

## Validation

No standalone validator script (matches `harness-manager`). Self-check before finishing:

- [ ] Tests pass (evidence shown) before the menu
- [ ] Workspace state detected; correct menu (4 or 3) presented
- [ ] Base branch confirmed
- [ ] Execution followed merge → worktree-remove → branch-delete ordering
- [ ] Worktree cleaned only for Options 1 / 4, only if owned (native → `ExitWorktree`)
- [ ] Discard required a typed `discard`; no unrequested force-push
- [ ] Option 2 delegated to `/ship` when available, else plain push + `/pr-writer` — not reimplemented
