#!/usr/bin/env bash
# elian-store — daily update check (SessionStart hook)
#
# Behavior:
# - Runs on every Claude Code SessionStart, but is throttled to one network
#   probe per 24 h.
# - Foreground path is fast (only marker / notify file checks). The actual
#   network call is forked to a background child so SessionStart latency
#   stays in the millisecond range.
# - Compares the locally installed elian-store version (read from this
#   plugin's plugin.json) against the latest entry in
#   marketplace.json on the GitHub main branch.
# - When a new version is found, writes a notification file. The next
#   SessionStart prints it once and removes it.
# - All failures are silent (offline, rate-limited, malformed JSON, etc.).
#
# Disabling: remove the SessionStart hook from
#   plugins/elian-store/.claude-plugin/plugin.json
# or delete this file. Background processes are short-lived (≤10 s) and
# never block a session.

set -e

# ${CLAUDE_PLUGIN_DATA} is a per-plugin persistent directory provided by
# Claude Code. Fall back to a deterministic path so the script still works
# when the env var is absent (e.g., running this hook by hand).
DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/elian-store-elian}"
MARKER="$DATA_DIR/last-update-check"
NOTIFY="$DATA_DIR/notify"
THROTTLE_MIN=$((24 * 60))

mkdir -p "$DATA_DIR"

# 1) Surface a queued notification (from a previous session's background probe).
if [ -f "$NOTIFY" ]; then
  cat "$NOTIFY"
  rm -f "$NOTIFY"
fi

# 2) Throttle to one probe per THROTTLE_MIN minutes.
if [ -f "$MARKER" ] && find "$MARKER" -mmin -"$THROTTLE_MIN" -print -quit 2>/dev/null | grep -q .; then
  exit 0
fi

# 3) Touch the marker now so concurrent SessionStarts don't race the same probe.
touch "$MARKER"

# 4) Fork the network probe to the background. The session continues immediately.
(
  PLUGIN_JSON="${CLAUDE_PLUGIN_ROOT:-}/.claude-plugin/plugin.json"
  if [ ! -f "$PLUGIN_JSON" ]; then
    exit 0
  fi

  CURRENT=$(python3 -c "
import json, sys
try:
    print(json.load(open(sys.argv[1]))['version'])
except Exception:
    pass
" "$PLUGIN_JSON" 2>/dev/null) || exit 0

  if [ -z "$CURRENT" ]; then
    exit 0
  fi

  REMOTE_URL='https://raw.githubusercontent.com/Elian-Studio/elian-claude-plugins/main/.claude-plugin/marketplace.json'
  REMOTE=$(curl -fsSL --max-time 10 "$REMOTE_URL" 2>/dev/null) || exit 0

  LATEST=$(printf '%s' "$REMOTE" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    p = next((p for p in d.get('plugins', []) if p.get('name') == 'elian-store'), None)
    if p and p.get('version'):
        print(p['version'])
except Exception:
    pass
" 2>/dev/null) || exit 0

  if [ -z "$LATEST" ]; then
    exit 0
  fi

  if [ "$CURRENT" != "$LATEST" ]; then
    {
      printf '🔔 elian-store update available: v%s → v%s\n\n' "$CURRENT" "$LATEST"
      printf 'To update:\n'
      printf '  /plugin marketplace update elian\n'
      printf '  /plugin update elian-store@elian\n\n'
      printf 'Release notes: https://github.com/Elian-Studio/elian-claude-plugins/blob/main/CHANGELOG.md\n'
      printf '(This check runs once every 24 h. To disable, remove the SessionStart hook from plugin.json.)\n'
    } > "$NOTIFY"
  fi
) >/dev/null 2>&1 &

# Detach the child so the parent shell can exit even if the child is still
# running. `disown` is bash-builtin; ignore if unavailable.
disown 2>/dev/null || true

exit 0
