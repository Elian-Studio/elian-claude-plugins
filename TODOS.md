# TODOS

Open work for this repository, grouped by skill/component, then priority
(P0 highest through P4), with completed items at the bottom.

## spec-coverage

### End-to-end smoke on a project with a real test suite
**Priority:** P1
**Noticed:** v3.1.0 (2026-07-22)

`spec-coverage` has only ever run against its own bundled JUnit fixture. The
full loop — seed from real design docs → run a real suite → collect → render —
has never executed against a live project. The 12 fixture checks cover the
verdict logic, but not the parts that touch a real build: test-runner detection
per marker file, the reporter flags in the `check` table (Vitest/Jest `--reporter=junit`,
`pytest --junitxml`), and whether Gradle/Maven actually drop XML where
`collect_tests.py` looks.

Do this on a repo that already has JUnit-5 tests, adding `R#-AC#` prefixes to a
handful of `@DisplayName`s, and confirm the six steps in the plan's Verification
section.

### Decide whether `ac_claimed_manual` needs a per-item filter in the HTML
**Priority:** P3
**Noticed:** v3.1.0 (2026-07-22)

The headline now shows human-asserted ACs separately from test-proven ones, but
there is no way to list just those items. Worth adding only if the separation
turns out to be something people act on.

## Codex parity

### Port the design-pipeline skills to `codex/skills/`
**Priority:** P2
**Noticed:** v3.0.0 (2026-07-22)

`intake-spec`, `design-feature`, `update-design`, `erd-preview`, and
`kanban-board` have no `codex/skills/<name>` symlink. Recorded as a documented
exception in `docs/claude-codex-skill-parity.md`: the artifact contract was still
moving (v3.0.0 relocated `spec.json`, v3.1.0 added `tech-spec.md`), and porting a
moving contract doubles the churn. Revisit once the design set is stable.

`document-writer` is also listed Claude-only but is now a straightforward port —
v3.0.0 removed the `~/.claude/skills/...` hardcoding that used to block it.

## verify-implementation

### `check-skill-discovery.py` prints Korean
**Priority:** P3
**Noticed:** v3.1.0 (2026-07-22)

`plugins/elian-store/skills/verify-implementation/scripts/check-skill-discovery.py`
emits Korean status lines (`발견된 verify-* 스킬`, `자동 실행 대상`). The
repository is English-only for everything except literal output labels of a
generated artifact, and this is console output from a validator, not a
deliverable label. Pre-existing; out of scope for v3.1.0.

## Repository

### Orphaned required status check on `main`
**Priority:** P2
**Noticed:** before v3.0.0 (documented in CLAUDE.md)

`main` still requires the status check "Evaluate skills (90+ required)" whose
workflow was removed, so every merge needs an admin override. Either restore a
workflow that reports that check name or drop the branch-protection requirement.

## Completed

### Retire duplicate skills (`ai-assisted-feature-development`, `skill-dispatcher`)
**Completed:** v3.0.0 (2026-07-22)

### Unify `spec.json` into `claudedocs/<label>/`
**Completed:** v3.0.0 (2026-07-22)

### Add `tech-spec.md` (developer-facing PRD)
**Completed:** v3.0.0 (2026-07-22)

### Bring `update-design` up to date with v2.26–v2.29 artifacts
**Completed:** v3.0.0 (2026-07-22)

### Add requirement-coverage tracking (`spec-coverage`)
**Completed:** v3.1.0 (2026-07-22)
