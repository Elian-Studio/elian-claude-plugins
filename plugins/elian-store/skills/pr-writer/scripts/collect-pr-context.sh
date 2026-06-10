#!/usr/bin/env bash
# Collect compact PR/MR context for pr-writer: branch, status, detected base,
# diff stat, changed files, and commits. Read-only — runs no write/push commands.
#
# Usage:
#   collect-pr-context.sh [BASE]
#
# BASE is optional. When omitted, the base branch is auto-detected in order:
#   remote default branch (origin/HEAD) -> origin/main -> origin/master -> main -> master.
set -euo pipefail

detect_base() {
  # Prefer the remote's default branch (e.g. origin/main), then common
  # integration branches. The current branch's own @{upstream} is deliberately
  # NOT used: for a pushed feature branch it points at origin/<that-branch>,
  # which would diff the branch against itself and show nothing.
  local def
  if def=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null) && [ -n "$def" ]; then
    echo "$def"
    return 0
  fi
  for ref in origin/main origin/master main master; do
    if git rev-parse --verify --quiet "$ref" >/dev/null 2>&1; then
      echo "$ref"
      return 0
    fi
  done
  return 1
}

BASE="${1:-}"
if [ -z "$BASE" ]; then
  if ! BASE=$(detect_base); then
    echo "Could not detect a base branch. Pass one explicitly: collect-pr-context.sh <base>" >&2
    exit 1
  fi
fi

printf '## Base\n%s\n\n' "$BASE"

printf '## Branch\n'
git branch --show-current

printf '\n## Remote\n'
git remote -v | sed -n '1,2p'

printf '\n## Status\n'
git status --short

printf '\n## Diff stat (%s...HEAD)\n' "$BASE"
git diff --stat "$BASE"...HEAD

printf '\n## Changed files\n'
git diff --name-only "$BASE"...HEAD

printf '\n## Commits\n'
git log --oneline "$BASE"..HEAD
