#!/usr/bin/env bash
# dev-install.sh — install the WORKING-TREE elian-store plugin into the local
# Claude Code plugin cache so the WHOLE pipeline (/intake-spec, /design-feature,
# /implement, /review, …) runs as real installed skills for end-to-end
# testing — without merging to main or opening a PR.
#
# WHY: plugin skills load at session start from the installed cache, not from your
# git working tree. So a WIP skill on a feature branch is invisible to slash
# commands until "installed". This script copies your working tree into the cache
# (and the marketplace clone) so a session restart picks it up.
#
# USAGE:
#   tools/dev-install.sh            # install working tree into the local cache
#   tools/dev-install.sh --revert   # restore the marketplace clone from git (undo)
#
# AFTER INSTALL: fully restart the Claude Code session (skills load at startup),
# then run the pipeline normally: /intake-spec … → /design-feature … →
# /implement … → /review.
#
# This only touches your LOCAL ~/.claude plugin cache. It does not push or commit.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO/plugins/elian-store"
MKT_CLONE="$HOME/.claude/plugins/marketplaces/elian/plugins/elian-store"
CACHE_ROOT="$HOME/.claude/plugins/cache/elian/elian-store"

[ -f "$SRC/.claude-plugin/plugin.json" ] || { echo "ERROR: $SRC/.claude-plugin/plugin.json not found"; exit 1; }
VERSION="$(python3 -c "import json,sys;print(json.load(open('$SRC/.claude-plugin/plugin.json'))['version'])")"

if [ "${1:-}" = "--revert" ]; then
  if [ -d "$MKT_CLONE/../../.git" ]; then
    ( cd "$HOME/.claude/plugins/marketplaces/elian" && git checkout -- . && git clean -fd plugins/elian-store >/dev/null 2>&1 || true )
    echo "reverted marketplace clone from git. Run /plugin to re-sync, then restart the session."
  else
    echo "marketplace clone is not a git repo; nothing to revert. (Cache dev copy at $CACHE_ROOT/$VERSION left in place.)"
  fi
  exit 0
fi

echo "elian-store working tree version: $VERSION"

# 1) Copy working tree into the versioned cache dir the harness loads from.
DEST="$CACHE_ROOT/$VERSION"
mkdir -p "$DEST"
rsync -a --delete --exclude '.git' "$SRC/" "$DEST/"
echo "  → cached at $DEST"

# 2) Sync the marketplace clone so the version is 'available' and matches the code.
if [ -d "$MKT_CLONE" ]; then
  rsync -a --delete --exclude '.git' "$SRC/" "$MKT_CLONE/"
  echo "  → marketplace clone synced ($MKT_CLONE)"
else
  echo "  (marketplace clone not found at $MKT_CLONE — cache copy is still installed)"
fi

cat <<EOF

dev-install complete (v$VERSION).
Next:
  1. FULLY RESTART the Claude Code session (skills load at startup).
  2. Verify: /design-feature should appear; then run the pipeline end-to-end:
       /intake-spec <label>  →  /design-feature <label>  →  /implement <label>  →  /review
  3. Undo:  tools/dev-install.sh --revert   (and /plugin to re-sync to the published version)
EOF
