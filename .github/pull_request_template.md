<!--
PR guide:
- There is no repository-wide numeric score gate.
- When SKILL.md changes, run YAML/frontmatter smoke checks and the changed skill's own validator when present.
- Review purpose, non-use boundary, output contract, references, and side-effect posture manually.
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
- [ ] Single-responsibility PR

### When SKILL.md changes

- [ ] `plugin.json` `version` bumped when installed behavior changes
- [ ] `marketplace.json` plugin entry `version` bumped when plugin version changes
- [ ] `CHANGELOG.md` updated
- [ ] YAML/frontmatter smoke check passed
- [ ] Changed skill's own validator passed when present
- [ ] Purpose, non-use boundary, output contract, and side-effect posture reviewed

### When adding a new plugin

- [ ] `plugins/<name>/.claude-plugin/plugin.json` written
- [ ] `.claude-plugin/marketplace.json` `plugins[]` updated with the new entry
- [ ] `README.md` plugin list updated
- [ ] License declared (`plugin.json.license`)

## Skill Quality Notes

<!--
For skill changes, summarize:
- why this skill should exist or why this change fits its current purpose
- what it refuses to do
- what validator/example/manual path proves it still works
- whether Codex parity changed or was intentionally deferred
-->

## Related issues / context

<!-- Closes #N, Refs #M, or decision background -->
