#!/usr/bin/env bash
# codex/setup.sh — install this repo's Codex skills into ~/.codex/skills.
#
# Model: skills live once in the Claude plugin tree
# (plugins/elian-store/skills/<name>/). codex/skills/<name> is a relative
# symlink into that tree, so there is no duplicated content. This script then
# symlinks ~/.codex/skills/<name> -> <repo>/codex/skills/<name>. Codex follows
# symlinks, so a later `git pull` in this repo updates the installed skills
# with no re-copy.
#
# `_shared/` is installed alongside the skills, not as a skill: several shipped
# SKILL.md bodies link out to `../_shared/<file>` (review severity, execution
# strategy, the structural validator). Without it those references dangle in a
# Codex install even though every skill directory is present.
#
# Idempotent and safe:
# - Correct symlink already in place        -> skipped.
# - A real dir/file or a different symlink   -> backed up to <name>.bak.<ts>, then linked.
#
# Usage:
#   ./codex/setup.sh            # install all skills under codex/skills/ (plus _shared)
#   ./codex/setup.sh create-document [other-skill ...]   # install a subset
#
# Uninstall a skill: rm "${CODEX_HOME:-$HOME/.codex}/skills/<name>"

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$REPO_ROOT/codex/skills"
DEST_DIR="${CODEX_HOME:-$HOME/.codex}/skills"

if [ ! -d "$SRC_DIR" ]; then
  echo "error: $SRC_DIR not found" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

# Build the install list: explicit args, or every entry under codex/skills/.
if [ "$#" -gt 0 ]; then
  # A subset install still needs the shared payload the skills link into.
  names=("$@")
  case " ${names[*]} " in
    *" _shared "*) ;;
    *) [ -e "$SRC_DIR/_shared" ] && names+=("_shared") ;;
  esac
else
  names=()
  for path in "$SRC_DIR"/*; do
    [ -e "$path" ] || continue
    names+=("$(basename "$path")")
  done
fi

ts="$(date +%Y%m%d-%H%M%S)"
installed=0 skipped=0 backed_up=0

for name in "${names[@]}"; do
  src="$SRC_DIR/$name"
  dest="$DEST_DIR/$name"

  if [ ! -e "$src" ]; then
    echo "skip: $name (no codex/skills/$name in repo)" >&2
    continue
  fi

  # Already the correct symlink? Skip.
  if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
    echo "ok:   $name (already linked)"
    skipped=$((skipped + 1))
    continue
  fi

  # Anything else occupying the path gets backed up, never deleted.
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    mv "$dest" "$dest.bak.$ts"
    echo "back: $name -> $name.bak.$ts"
    backed_up=$((backed_up + 1))
  fi

  ln -s "$src" "$dest"
  echo "link: $name -> $src"
  installed=$((installed + 1))
done

echo "---"
echo "installed=$installed skipped=$skipped backed_up=$backed_up  (dest: $DEST_DIR)"
