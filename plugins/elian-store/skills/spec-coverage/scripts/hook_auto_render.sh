#!/bin/bash
# spec-coverage PostToolUse hook — after a git commit that touched a
# spec-coverage.json, re-render its HTML view so the readable file never drifts
# from the source of truth.
#
# OPT-IN ONLY. This is deliberately NOT registered in the plugin manifest: a
# PostToolUse hook with `matcher: Bash` fires on every Bash call for everyone
# who installs the plugin. Register it per project in
# .claude/settings.local.json (see SKILL.md).
#
# The caller (Claude Code) passes the hook payload as JSON on stdin.

# No `set -e`: a hook failure must never block the user's git commit.
set -uo pipefail

# This script's own directory — no hardcoded home paths, works from any install.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PAYLOAD=$(cat 2>/dev/null || echo "{}")

TOOL_NAME=$(echo "$PAYLOAD" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name', d.get('toolName','')))" \
  2>/dev/null || echo "")
if [[ "$TOOL_NAME" != "Bash" ]]; then
  exit 0
fi

COMMAND=$(echo "$PAYLOAD" | python3 -c "
import sys, json
d = json.load(sys.stdin)
inp = d.get('tool_input', d.get('toolInput', {}))
print(inp.get('command', ''))
" 2>/dev/null || echo "")

# Only react to a git commit (covers --amend and friends).
if [[ ! "$COMMAND" =~ git[[:space:]]+commit ]]; then
  exit 0
fi

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [[ -z "$PROJECT_ROOT" ]] || [[ ! -d "$PROJECT_ROOT/claudedocs" ]]; then
  exit 0
fi

cd "$PROJECT_ROOT" || exit 0

CHANGED_FILES=$(git diff HEAD~1 --name-only 2>/dev/null \
  || git diff --cached --name-only 2>/dev/null || echo "")
if [[ -z "$CHANGED_FILES" ]]; then
  exit 0
fi

# Collect affected labels (macOS bash 3 compatible: no associative arrays).
AFFECTED=""
while IFS= read -r f; do
  case "$f" in
    claudedocs/*/spec-coverage.json)
      LABEL=$(echo "$f" | sed -E 's|claudedocs/([^/]+)/.*|\1|')
      AFFECTED="${AFFECTED}${LABEL}"$'\n'
      ;;
  esac
done <<< "$CHANGED_FILES"

UNIQUE_LABELS=$(echo "$AFFECTED" | grep -v '^$' | sort -u)
if [[ -z "$UNIQUE_LABELS" ]]; then
  exit 0
fi

# Re-render only. Never `git add` and never commit — the HTML is the user's to
# stage, and a hook that commits behind your back is how history gets polluted.
while IFS= read -r LABEL; do
  if [[ -f "claudedocs/$LABEL/spec-coverage.json" ]]; then
    echo "[spec-coverage hook] re-rendering $LABEL..." >&2
    python3 "$SCRIPT_DIR/render.py" "$LABEL" "$PROJECT_ROOT" >&2 || true
  fi
done <<< "$UNIQUE_LABELS"

exit 0
