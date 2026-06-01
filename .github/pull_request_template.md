<!--
PR guide:
- SKILL.md changes are reviewed manually against the operating rules in CONTRIBUTING.md.
- Keep frontmatter YAML-safe (quote values containing ": ", brackets, or quotes) so Claude/GitHub parsers do not fail.
-->

## Summary

<!-- One line: what changed. -->

## Change type

- [ ] New plugin (`plugins/<name>/` directory)
- [ ] Existing plugin: feature added (MINOR — `1.0.0 → 1.1.0`)
- [ ] Existing plugin: bug fix (PATCH — `1.0.0 → 1.0.1`)
- [ ] Existing plugin: breaking change (MAJOR — `1.0.0 → 2.0.0`)
- [ ] Marketplace metadata only (no skill content change)
- [ ] Infra / docs / CI (no skill content change)

## Checklist

### Always

- [ ] Working on `feature/*` or `fix/*` branch (no direct push to `main`)
- [ ] Single-responsibility PR (one change to one plugin)

### When SKILL.md changes

- [ ] `plugin.json` `version` bumped
- [ ] `marketplace.json` plugin entry `version` bumped (both recommended)
- [ ] `CHANGELOG.md` updated (Added / Changed / Fixed / Removed)
- [ ] Frontmatter parses as YAML (no unquoted `: `, brackets, or quotes in string values)

### When adding a new plugin

- [ ] `plugins/<name>/.claude-plugin/plugin.json` written
- [ ] `marketplace.json` `plugins[]` updated with the new entry
- [ ] `README.md` plugin list updated
- [ ] License declared (`plugin.json.license`)

## Related issues / context

<!-- Closes #N, Refs #M, or decision background -->
