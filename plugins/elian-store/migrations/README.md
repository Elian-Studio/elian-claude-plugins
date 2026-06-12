# elian-store migrations

Place one-off installed-user migration scripts here as `vX.Y.Z.sh`.

The SessionStart hook `hooks/check-update.sh` runs these scripts after an installed plugin moves
from an older recorded version to a newer local `plugin.json.version`.

Rules:

- Name scripts with the target version, for example `v2.14.0.sh`.
- Keep scripts idempotent. If a script fails, the hook leaves the recorded version unchanged and
  retries on the next SessionStart.
- Scripts run with `bash`, so executable bits are not required.
- First installs record the current version and skip historical migrations.
- Hook output is silent; write diagnostic details to `$ELIAN_STORE_DATA_DIR` when needed.

Available environment:

| Variable | Meaning |
|---|---|
| `ELIAN_STORE_PREVIOUS_VERSION` | Last successfully migrated installed version |
| `ELIAN_STORE_CURRENT_VERSION` | Current local `plugin.json.version` |
| `ELIAN_STORE_DATA_DIR` | Per-plugin persistent data directory |
| `ELIAN_STORE_PLUGIN_ROOT` | Installed plugin root |
