# elian-store migrations

Place one-off installed-user migration scripts here as `vX.Y.Z.sh`.

The SessionStart hook `hooks/check-update.sh` runs these scripts after an installed plugin moves
from an older recorded version to a newer local `plugin.json.version`.

Rules:

- Name scripts with the target version, for example `v2.14.0.sh`.
- Keep scripts idempotent. The runner records progress per script (the recorded version advances to
  the last script that succeeded) and retries from there on the next SessionStart, but a script that
  fails partway is itself re-run — so each script must be safe to run again.
- Each script has a wall-clock budget (`ELIAN_STORE_MIGRATION_TIMEOUT`, default `60` seconds); a
  script that exceeds it is killed and retried next session.
- Concurrent SessionStarts are serialized by an atomic lock, so the same script never runs twice at
  once. A lock left by a hard-killed session is reclaimed after 5 minutes.
- Scripts run with a **minimal environment** — only `PATH`, `HOME`, `TMPDIR`, `LANG`, `LC_ALL`, and the
  `ELIAN_STORE_*` variables below. Session secrets (tokens, API keys) are deliberately not exposed.
- Scripts run with `bash`, so executable bits are not required.
- First installs record the current version and skip historical migrations.
- Hook output is silent; write diagnostic details to `$ELIAN_STORE_DATA_DIR` (the runner appends its
  own progress and failures to `migration.log` there).

Available environment:

| Variable | Meaning |
|---|---|
| `ELIAN_STORE_PREVIOUS_VERSION` | Last successfully migrated installed version |
| `ELIAN_STORE_CURRENT_VERSION` | Current local `plugin.json.version` |
| `ELIAN_STORE_DATA_DIR` | Per-plugin persistent data directory |
| `ELIAN_STORE_PLUGIN_ROOT` | Installed plugin root |
