#!/usr/bin/env bash
# elian-store — daily update check (SessionStart hook)
#
# Behavior:
# - Runs on every Claude Code SessionStart, but is throttled to one network
#   probe per 24 h.
# - Foreground path is fast (queued notification + local migration check).
#   The network call is forked to a background child so SessionStart latency
#   stays in the millisecond range.
# - Compares the locally installed elian-store version (read from this
#   plugin's plugin.json) against the latest entry in
#   marketplace.json on the GitHub main branch.
# - When a new version is found, writes a notification file. The next
#   SessionStart prints it once and removes it. If reachable, the notification
#   includes a short CHANGELOG excerpt for the target version.
# - Runs local version migrations from migrations/vX.Y.Z.sh once per installed
#   plugin version. First installs record the current version and skip old
#   migrations.
# - All failures are silent (offline, rate-limited, malformed JSON, etc.).
#
# Disabling: remove the SessionStart hook from
#   plugins/elian-store/.claude-plugin/plugin.json
# or delete this file. Background processes are short-lived (≤10 s) and
# never block a session.

set -e

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PLUGIN_JSON="$PLUGIN_ROOT/.claude-plugin/plugin.json"

# ${CLAUDE_PLUGIN_DATA} is a per-plugin persistent directory provided by
# Claude Code. Fall back to a deterministic path so the script still works
# when the env var is absent (e.g., running this hook by hand).
DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/elian-store-elian}"
MARKER="$DATA_DIR/last-update-check"
NOTIFY="$DATA_DIR/notify"
THROTTLE_MIN=$((24 * 60))

MARKETPLACE_URL='https://raw.githubusercontent.com/Elian-Studio/elian-claude-plugins/main/.claude-plugin/marketplace.json'
CHANGELOG_URL='https://raw.githubusercontent.com/Elian-Studio/elian-claude-plugins/main/CHANGELOG.md'
CHANGELOG_WEB_URL='https://github.com/Elian-Studio/elian-claude-plugins/blob/main/CHANGELOG.md'

read_plugin_version() {
  python3 -c '
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as f:
        print(json.load(f)["version"])
except Exception:
    pass
' "$1"
}

read_marketplace_version() {
  python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    p = next((p for p in d.get("plugins", []) if p.get("name") == "elian-store"), None)
    if p and p.get("version"):
        print(p["version"])
except Exception:
    pass
'
}

extract_changelog_notes() {
  local version="$1"
  python3 -c '
import sys

version = sys.argv[1].lstrip("v")
lines = sys.stdin.read().splitlines()
capture = False
skip_sub = False
out = []

for line in lines:
    stripped = line.strip()
    if stripped.startswith("### "):
        if capture:
            break
        heading = stripped[4:].strip()
        capture = heading == version or heading.startswith(version + " ")
        continue
    if not capture:
        continue
    if not stripped or stripped == "---" or stripped.startswith(">"):
        continue
    if stripped.startswith("#### "):
        sub = stripped[5:].strip()
        # Skip maintainer-facing housekeeping ("Notes") in the user notification.
        skip_sub = sub.lower() == "notes"
        if not skip_sub:
            out.append(sub + ":")
        continue
    if skip_sub:
        continue
    out.append(stripped)
    if len(out) >= 12:
        break

print("\n".join(out))
' "$version"
}

run_migrations() {
  local current="$1"
  local data_dir="$2"
  local plugin_root="$3"
  local migrations_dir="$plugin_root/migrations"
  local migrated_version="$data_dir/migrated-version"
  local migration_log="$data_dir/migration.log"
  local lock_dir="$data_dir/migration.lock"

  if [ -z "$current" ]; then
    return 0
  fi

  # Steady-state fast path: when the recorded version already matches the
  # current one (the common case after first install/upgrade), skip the
  # python3 spawn entirely so SessionStart stays in the millisecond range.
  # First install (marker missing), upgrade (marker != current), and a
  # corrupt marker all fall through to the python path, which handles them.
  if [ -f "$migrated_version" ] && [ "$(cat "$migrated_version" 2>/dev/null)" = "$current" ]; then
    return 0
  fi

  mkdir -p "$data_dir"

  # Serialize migrations across concurrent SessionStarts so two sessions never
  # run the same scripts at once. flock is absent on macOS, so use an atomic
  # mkdir lock. Steal a lock older than 5 minutes left by a hard-killed session
  # so migrations can never wedge permanently.
  if [ -d "$lock_dir" ] && [ -n "$(find "$lock_dir" -maxdepth 0 -mmin +5 2>/dev/null)" ]; then
    rmdir "$lock_dir" 2>/dev/null || true
  fi
  if ! mkdir "$lock_dir" 2>/dev/null; then
    return 0  # another SessionStart holds the lock and is doing the work
  fi

  python3 - "$current" "$data_dir" "$migrations_dir" "$migrated_version" "$migration_log" <<'PY' || true
import os
import re
import subprocess
import sys
from pathlib import Path

current, data_dir, migrations_dir, marker, log_path = sys.argv[1:]
data = Path(data_dir)
migrations = Path(migrations_dir)
marker_path = Path(marker)
log = Path(log_path)

def parse(version):
    m = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", (version or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None

def write_marker(version):
    data.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(version + "\n", encoding="utf-8")

def append_log(message):
    data.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(message.rstrip() + "\n")

current_key = parse(current)
if current_key is None:
    sys.exit(0)

if not marker_path.exists():
    write_marker(current)
    sys.exit(0)

previous = marker_path.read_text(encoding="utf-8").strip()
previous_key = parse(previous)
if previous_key is None:
    append_log(f"invalid migrated-version marker {previous!r}; recording {current}")
    write_marker(current)
    sys.exit(0)

if previous_key >= current_key:
    sys.exit(0)

if not migrations.is_dir():
    write_marker(current)
    sys.exit(0)

scripts = []
for path in migrations.glob("v*.sh"):
    key = parse(path.stem)
    if key and previous_key < key <= current_key:
        scripts.append((key, path))
scripts.sort(key=lambda item: item[0])

try:
    timeout_s = int(os.environ.get("ELIAN_STORE_MIGRATION_TIMEOUT", "60"))
except ValueError:
    timeout_s = 60

# Run migration scripts with a minimal environment so session secrets (tokens,
# API keys) present in the parent process are never handed to them.
env = {k: os.environ[k] for k in ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL") if k in os.environ}
env.update({
    "ELIAN_STORE_PREVIOUS_VERSION": previous,
    "ELIAN_STORE_CURRENT_VERSION": current,
    "ELIAN_STORE_DATA_DIR": str(data),
    "ELIAN_STORE_PLUGIN_ROOT": str(migrations.parent),
})

for key, path in scripts:
    append_log(f"running {path.name} for {previous} -> {current}")
    try:
        with log.open("a", encoding="utf-8") as f:
            result = subprocess.run(
                ["bash", str(path)],
                stdout=f, stderr=subprocess.STDOUT, env=env, timeout=timeout_s,
            )
    except subprocess.TimeoutExpired:
        append_log(f"timeout {path.name} after {timeout_s}s; will retry on next SessionStart")
        sys.exit(0)
    if result.returncode != 0:
        append_log(f"failed {path.name} with exit {result.returncode}; will retry on next SessionStart")
        sys.exit(0)
    # Per-script checkpoint: record this version so a later failure does not
    # re-run scripts that already succeeded on the next SessionStart.
    write_marker(".".join(str(x) for x in key))

write_marker(current)
PY
  rmdir "$lock_dir" 2>/dev/null || true
}

selftest() {
  local tmp
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT

  local notes
  notes="$(cat <<'EOF' | extract_changelog_notes "2.14.0"
# Changelog

### 2.14.0 — 2026-06-12

#### Added
- First line.
- Second line.

#### Notes
- Housekeeping line that should not reach users.

### 2.13.0 — 2026-06-12
- Older line.
EOF
)"
  case "$notes" in
    *"Added:"*"First line."*"Second line."*) ;;
    *) printf 'selftest failed: changelog extraction\n' >&2; exit 1 ;;
  esac
  case "$notes" in
    *"Notes:"*|*"Housekeeping"*) printf 'selftest failed: Notes subsection leaked into notification\n' >&2; exit 1 ;;
  esac

  local plugin_root="$tmp/plugin"
  local data_dir="$tmp/data"
  mkdir -p "$plugin_root/migrations" "$data_dir"
  printf '1.0.0\n' > "$data_dir/migrated-version"
  cat > "$plugin_root/migrations/v1.1.0.sh" <<'EOF'
printf 'v1.1.0 %s -> %s\n' "$ELIAN_STORE_PREVIOUS_VERSION" "$ELIAN_STORE_CURRENT_VERSION" >> "$ELIAN_STORE_DATA_DIR/order"
EOF
  cat > "$plugin_root/migrations/v2.0.0.sh" <<'EOF'
printf 'v2.0.0 %s -> %s\n' "$ELIAN_STORE_PREVIOUS_VERSION" "$ELIAN_STORE_CURRENT_VERSION" >> "$ELIAN_STORE_DATA_DIR/order"
EOF
  cat > "$plugin_root/migrations/v2.1.0.sh" <<'EOF'
printf 'v2.1.0 should-not-run\n' >> "$ELIAN_STORE_DATA_DIR/order"
EOF

  run_migrations "2.0.0" "$data_dir" "$plugin_root"
  if ! diff -u "$data_dir/order" - <<'EOF' >/dev/null; then
v1.1.0 1.0.0 -> 2.0.0
v2.0.0 1.0.0 -> 2.0.0
EOF
    printf 'selftest failed: migration order\n' >&2
    exit 1
  fi
  if [ "$(cat "$data_dir/migrated-version")" != "2.0.0" ]; then
    printf 'selftest failed: migrated-version marker\n' >&2
    exit 1
  fi

  local fresh_data="$tmp/fresh-data"
  mkdir -p "$fresh_data"
  run_migrations "2.1.0" "$fresh_data" "$plugin_root"
  if [ -f "$fresh_data/order" ]; then
    printf 'selftest failed: fresh install ran historical migrations\n' >&2
    exit 1
  fi
  if [ "$(cat "$fresh_data/migrated-version")" != "2.1.0" ]; then
    printf 'selftest failed: fresh install marker\n' >&2
    exit 1
  fi

  # Steady-state path: when the marker already equals current, run_migrations is
  # a no-op (the bash guard short-circuits before spawning python3).
  local guard_data="$tmp/guard-data"
  mkdir -p "$guard_data"
  printf '2.0.0\n' > "$guard_data/migrated-version"
  run_migrations "2.0.0" "$guard_data" "$plugin_root"
  if [ -f "$guard_data/order" ] || [ "$(cat "$guard_data/migrated-version")" != "2.0.0" ]; then
    printf 'selftest failed: steady-state path was not a no-op\n' >&2
    exit 1
  fi

  # Corrupt marker: an unparseable version is logged and rewritten to current,
  # and no historical migration runs.
  local corrupt_data="$tmp/corrupt-data"
  mkdir -p "$corrupt_data"
  printf 'not-a-version\n' > "$corrupt_data/migrated-version"
  run_migrations "2.0.0" "$corrupt_data" "$plugin_root"
  if [ "$(cat "$corrupt_data/migrated-version")" != "2.0.0" ]; then
    printf 'selftest failed: corrupt marker not rewritten to current\n' >&2
    exit 1
  fi
  if ! grep -q "invalid migrated-version marker" "$corrupt_data/migration.log" 2>/dev/null; then
    printf 'selftest failed: corrupt marker not logged\n' >&2
    exit 1
  fi
  if [ -f "$corrupt_data/order" ]; then
    printf 'selftest failed: corrupt marker ran historical migrations\n' >&2
    exit 1
  fi

  # Concurrency lock: a held lock makes run_migrations skip (no double-run).
  local lock_data="$tmp/lock-data"
  mkdir -p "$lock_data/migration.lock"
  printf '1.0.0\n' > "$lock_data/migrated-version"
  run_migrations "2.0.0" "$lock_data" "$plugin_root"
  if [ -f "$lock_data/order" ] || [ "$(cat "$lock_data/migrated-version")" != "1.0.0" ]; then
    printf 'selftest failed: held lock did not prevent migration\n' >&2
    exit 1
  fi
  rmdir "$lock_data/migration.lock" 2>/dev/null || true

  # Per-script checkpoint: a mid-chain failure leaves the marker at the last
  # successful script's version, not the original previous version.
  local cp_root="$tmp/cp-plugin"
  local cp_data="$tmp/cp-data"
  mkdir -p "$cp_root/migrations" "$cp_data"
  printf '1.0.0\n' > "$cp_data/migrated-version"
  cat > "$cp_root/migrations/v1.1.0.sh" <<'EOF'
printf 'ok\n' >> "$ELIAN_STORE_DATA_DIR/cp-order"
EOF
  cat > "$cp_root/migrations/v1.2.0.sh" <<'EOF'
exit 1
EOF
  run_migrations "1.2.0" "$cp_data" "$cp_root"
  if [ "$(cat "$cp_data/migrated-version")" != "1.1.0" ]; then
    printf 'selftest failed: per-script checkpoint (expected 1.1.0, got %s)\n' "$(cat "$cp_data/migrated-version" 2>/dev/null)" >&2
    exit 1
  fi

  # Timeout: a hung migration is killed and the marker is not advanced.
  local to_root="$tmp/to-plugin"
  local to_data="$tmp/to-data"
  mkdir -p "$to_root/migrations" "$to_data"
  printf '1.0.0\n' > "$to_data/migrated-version"
  cat > "$to_root/migrations/v1.1.0.sh" <<'EOF'
sleep 5
EOF
  export ELIAN_STORE_MIGRATION_TIMEOUT=1
  run_migrations "1.1.0" "$to_data" "$to_root"
  unset ELIAN_STORE_MIGRATION_TIMEOUT
  if [ "$(cat "$to_data/migrated-version")" != "1.0.0" ]; then
    printf 'selftest failed: timeout advanced the marker\n' >&2
    exit 1
  fi
  if ! grep -q "timeout v1.1.0.sh" "$to_data/migration.log" 2>/dev/null; then
    printf 'selftest failed: timeout not logged\n' >&2
    exit 1
  fi

  # Minimal env: session secrets are not exposed to migration scripts.
  local env_root="$tmp/env-plugin"
  local env_data="$tmp/env-data"
  mkdir -p "$env_root/migrations" "$env_data"
  printf '1.0.0\n' > "$env_data/migrated-version"
  cat > "$env_root/migrations/v1.1.0.sh" <<'EOF'
printf 'secret=[%s]\n' "${ELIAN_TEST_SECRET:-}" >> "$ELIAN_STORE_DATA_DIR/env-out"
EOF
  export ELIAN_TEST_SECRET="leaked"
  run_migrations "1.1.0" "$env_data" "$env_root"
  unset ELIAN_TEST_SECRET
  if ! grep -q 'secret=\[\]' "$env_data/env-out" 2>/dev/null; then
    printf 'selftest failed: session env leaked to migration script\n' >&2
    exit 1
  fi

  printf 'OK check-update selftest\n'
}

if [ "${1:-}" = "--selftest" ]; then
  selftest
  exit 0
fi

mkdir -p "$DATA_DIR"

# 1) Run local migrations before surfacing update notifications.
CURRENT="$(read_plugin_version "$PLUGIN_JSON" 2>/dev/null || true)"
run_migrations "$CURRENT" "$DATA_DIR" "$PLUGIN_ROOT" || true

# 2) Surface a queued notification (from a previous session's background probe).
if [ -f "$NOTIFY" ]; then
  # Strip ESC bytes so a tampered remote CHANGELOG/marketplace entry cannot inject
  # terminal escape sequences (ANSI/OSC/CSI all begin with ESC) into the session.
  # UTF-8 multibyte sequences never contain 0x1b, so the bell emoji survives.
  LC_ALL=C tr -d '\033' < "$NOTIFY"
  rm -f "$NOTIFY"
fi

# 3) Throttle to one probe per THROTTLE_MIN minutes.
if [ -f "$MARKER" ] && find "$MARKER" -mmin -"$THROTTLE_MIN" -print -quit 2>/dev/null | grep -q .; then
  exit 0
fi

# 4) Touch the marker now so concurrent SessionStarts don't race the same probe.
touch "$MARKER"

# 5) Fork the network probe to the background. The session continues immediately.
(
  if [ -z "$CURRENT" ]; then
    exit 0
  fi

  REMOTE="$(curl -fsSL --max-time 10 "$MARKETPLACE_URL" 2>/dev/null)" || exit 0
  LATEST="$(printf '%s' "$REMOTE" | read_marketplace_version 2>/dev/null || true)"

  if [ -z "$LATEST" ]; then
    exit 0
  fi

  if [ "$CURRENT" != "$LATEST" ]; then
    NOTES=""
    CHANGELOG="$(curl -fsSL --max-time 10 "$CHANGELOG_URL" 2>/dev/null || true)"
    if [ -n "$CHANGELOG" ]; then
      NOTES="$(printf '%s' "$CHANGELOG" | extract_changelog_notes "$LATEST" 2>/dev/null || true)"
    fi

    {
      printf '🔔 elian-store update available: v%s → v%s\n\n' "$CURRENT" "$LATEST"
      if [ -n "$NOTES" ]; then
        printf 'What changed in v%s:\n' "$LATEST"
        printf '%s\n' "$NOTES" | while IFS= read -r line; do
          printf '  %s\n' "$line"
        done
        printf '\n'
      fi
      printf 'To update:\n'
      printf '  /plugin marketplace update elian\n'
      printf '  /plugin update elian-store@elian\n\n'
      printf 'Release notes: %s\n' "$CHANGELOG_WEB_URL"
      printf '(This check runs once every 24 h. To disable, remove the SessionStart hook from plugin.json.)\n'
    } > "$NOTIFY"
  fi
) >/dev/null 2>&1 &

# Detach the child so the parent shell can exit even if the child is still
# running. `disown` is bash-builtin; ignore if unavailable.
disown 2>/dev/null || true

exit 0
