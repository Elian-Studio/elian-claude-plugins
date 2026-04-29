<!--
PR guide:
- When SKILL.md changes, the Skill Quality Gate (90 points) runs automatically.
- Heuristic scorer (Python stdlib only, no external API dependency) posts the result as a PR comment.
- Below 90 = merge blocked (branch protection).
- Rubric: scripts/rubric.md. Scorer: scripts/score_skill.py.
- Local pre-check: `python3 scripts/score_skill.py <SKILL.md>` (zero dependencies).
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
- [ ] Local score passes — `python3 scripts/score_skill.py <SKILL.md>` (≥ 90)

### When adding a new plugin

- [ ] `plugins/<name>/.claude-plugin/plugin.json` written
- [ ] `marketplace.json` `plugins[]` updated with the new entry
- [ ] `README.md` plugin list updated
- [ ] License declared (`plugin.json.license`)

## Skill Quality Gate score (manual pre-check)

The CI scorer posts a result automatically after PR creation. Before that, self-check expected losses by axis:

- [ ] 1. Frontmatter compliance (10/10 expected)
- [ ] 2. Description auto-invocation reliability (10/10 expected)
- [ ] 3. Progressive disclosure (10/10 expected)
- [ ] 4. Standing instructions (10/10 expected)
- [ ] 5. Example completeness (10/10 expected)
- [ ] 6. Anti-pattern / failure-mode (10/10 expected)
- [ ] 7. Validation self-check (10/10 expected)
- [ ] 8. Security / permission (10/10 expected)
- [ ] 9. Generalization / portability (10/10 expected)
- [ ] 10. Decision design / artifacts (10/10 expected)

**Expected total**: ___ / 100 (≥ 90 required)

## Related issues / context

<!-- Closes #N, Refs #M, or decision background -->
