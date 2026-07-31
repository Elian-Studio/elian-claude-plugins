# Changelog

This file records significant changes for every plugin in this marketplace.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the version scheme follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> The marketplace itself and each plugin keep **independent versions**. The marketplace version tracks catalog-structure changes (adding / removing plugins, metadata). Plugin versions track functional changes inside that plugin.

---

## elian-store Plugin

### [4.1.1] — 2026-07-31

#### Fixed
- **`spec-coverage/build_status.py` silently destroyed human-entered evidence on a corrupt
  prior file.** `merge_existing` caught `(ValueError, OSError)` and fell back to the freshly
  built data, and `main()` overwrites `spec-coverage.json` on the very next line — so an
  unreadable or half-written existing file made every human-entered `status` / `evidence` /
  `note` / `blocker` vanish with no error, the exact "hard no" the function's own docstring
  forbids. It now fails loudly (exit `4`) and leaves the file untouched for repair, matching
  `collect_tests.py`'s "refuse to report partial results as current" posture. A read error
  (`OSError`) and a parse error (`json.JSONDecodeError`) get distinct messages so the fix is
  obvious. Added a `validate.py` regression that corrupts the output and asserts the run aborts
  without rewriting it.

### [4.1.0] — 2026-07-29

Layering work driven by measurement rather than by taxonomy. An architecture proposal
predicted six duplicated conventions; a line-by-line audit found one, and found the largest
duplication in the tree somewhere the proposal never looked.

#### Removed
- **`validate_skill.py`: four byte-identical copies collapsed into one** (`brainstorm`, `fix`,
  `implement`, `improve` — 207 lines each, identical MD5, **621 lines deleted**). They were
  identical because the script self-identified from its own location; the shared
  `tools/validate_skill.py` takes the skill directory as an argument instead and accepts
  several at once. Changing a structural rule is now one edit rather than four-or-three-silent-
  divergences. Output is unchanged except for the retired `scripts/ directory exists` check,
  which only ever passed because the checker itself lived in that directory.

#### Fixed
- **`document-writer` produced documents that were not self-contained.**
  `assets/house-style.css` carried an `@import` of a jsDelivr-hosted webfont, and
  `build_doc.py` inlines that file wholesale — so every "opens anywhere" document shipped a
  CDN dependency, contradicting four separate documented rules (`document-writer/SKILL.md:30`
  and `:109`, `decision-dashboard/SKILL.md:271`, `erd-preview/SKILL.md:146`). The `@import`
  also sat *after* `:root {…}`, where CSS requires it to come first, so browsers were already
  ignoring it: a broken promise that bought nothing. Removed; the existing system font stack
  covers the fallback. A generated document now contains zero external URLs.
- `_shared/execution-strategy.md` claimed a single consumer (`/generate-teammate`). It has four.

#### Changed
- **Review severity is defined once.** `review` and `pr-review` each carried a five-row rubric
  and they had drifted in four of five rows — `CRITICAL` said "production outage" versus
  "outage", `HIGH` gained "or unmet requirement" on one side only, `LOW` lost "non-blocking
  observation". Both now read `skills/_shared/review-severity.md`, reconciled to the superset,
  so a `HIGH` means the same thing in both lanes. The domain rubrics in
  `agents/security-engineer.md` (exploitability) and `agents/ux-researcher.md` (task
  completion) are deliberately left separate — they measure a different axis.
- **The validation substrate is no longer `elian-store`-shaped.** Four checks silently skipped
  every other plugin:
  - `validate_versions()` walks `plugins/*/.claude-plugin/plugin.json`. Before this,
    `elian-workflow`'s `plugin.json` could drift from its marketplace entry with nothing
    catching it — precisely the failure that leaves installed users receiving nothing while
    the catalog claims a new version.
  - `_policy_files()` covers every plugin's `skills/`, so the English-only rule now applies
    beyond the bundle.
  - CI validates YAML frontmatter across `plugins/*/` and runs bundled validators from
    `plugins/*/skills/*/scripts/`.
  Both new checks were confirmed by deliberately introducing a violation and watching them fail.

#### Documentation
- **The documented validation commands were scoped to the bundle too.** `CLAUDE.md`,
  `README.md`, and `plugins/elian-store/README.md` all told contributors to run
  `Dir["plugins/elian-store/skills/*/SKILL.md"]`, so anyone following the documented
  procedure would have validated 22 of 24 skills and never known. All globs are now
  `plugins/*`, `tools/generate.py` is listed alongside the other checks, and the shared
  `tools/validate_skill.py` is documented next to the bespoke per-skill validators. Every
  command in those blocks was executed verbatim to confirm it runs.
- `TODOS.md` gains the three deferrals this release created rather than leaving them in
  commit messages: the `generate-teammate` → `create-document` invocation conversion
  (only blocking if the layers are published), the 18× `SKILL_DIR` snippet duplication,
  and the fact that CI never verifies the emitted cluster output.
- `docs/plugin-layering-architecture.md` — the Workflow / Standards / Common layering, with §1.1
  corrected against the audit. It records what the extraction *did not* find, because the useful
  result was negative: three skills all saying "TDD" were running three different disciplines
  (3-step, 4-step regression-first, 6-step characterization), and merging them would have
  destroyed information. A shared vocabulary is not shared rules.
- The root `standards/` directory with build-time vendoring and a parity validator is dropped
  as premature — every standards document's consumers sit inside one plugin, and
  `skills/_shared/` plus the existing `"shared": true` already covers that case.

### [4.0.0] — 2026-07-29

#### Removed
- **Four skills retired on usage evidence** (26 → 22): `finish-branch` (0 invocations in 36
  days), `functional-spec` (0 in 22), `design-ui` (3 in 67), and `kanban-board` (2 in 28).
  Counts come from the maintainer's `skillUsage` record cross-checked against each skill's
  first commit, so "unused" is distinguished from "too new to judge" — `spec-coverage` also
  shows 0 but is 7 days old and stays, and `respond-to-review` / `verify-before-claiming`
  show 0 only because `disable-model-invocation: false` reflex gates are not counted as
  invocations at all.
- Their Codex symlinks (`codex/skills/design-ui`, `codex/skills/functional-spec`) are gone,
  leaving 12 shared skills.

#### Changed
- `design-feature` no longer routes screens through a mockup → functional-spec pipeline. Its
  roadmap `links[]` guidance is now tool-agnostic ("whatever UI tooling the project uses"),
  and its Next steps hand off to `/spec-coverage` and `/implement` instead of the retired
  `/finish-branch`.
- `update-design` drops the `functional-specs/` artifact row, its conditional-update rule, and
  its handoff-table entry.
- The `design-contract` validator no longer guards the retired mockups/functional-specs path
  strings. What remains worth guarding is that the surviving design skills (`design-feature`,
  `update-design`) have not drifted back to the older `claudedocs/design/<feature>/` layout,
  so the check now covers exactly that. Its tests were rewritten to match.
- `HIGH_IMPACT_SKILLS` drops `finish-branch`; `harness-manager` remains.
- **`validate_repository.py` now enforces the `SKILL.md` contract across every plugin**, not
  just `elian-store`. `skill_directories()` walks all of `plugins/*/skills/`, while the new
  `store_skill_directories()` keeps the cluster-manifest check scoped to the bundle it
  describes. Without this a second plugin would ship with no frontmatter, naming, line-limit,
  or side-effect-gate validation at all.
- **`tools/generate.py`'s bare-`${CLAUDE_*}` lint now scans every plugin**, not just the
  cluster source directory. A bare `${CLAUDE_PLUGIN_ROOT}` is host-dependent wherever it
  lives, and scoping the lint to `elian-store` meant the first `elian-workflow` draft shipped
  one — caught only by reading the lint's own scope. Found and fixed in review.
- **`tools/clusters.json` regrouped from five thematic clusters into two by purpose** —
  `elian-dev` (13 skills: needs a code repository, git, and tests) and `elian-common`
  (9 skills: works outside one). This also fixes a latent bug in the staged split:
  `generate-teammate` hard-references `../_shared/execution-strategy.md`, but the cluster
  that owned it did not carry `shared: true`, so `--emit` would have shipped a broken link.
  Both clusters now carry `_shared`.

#### Added
- **New plugin `elian-workflow` 1.0.0** (`/issue-open`, `/issue-close`) — the issue cycle,
  which had no skill of its own. Commit-level and day-level records existed; the level that
  carries design decisions, architecture, and remaining checks did not.
  `/issue-close` interviews against the commit list (recognition beats recall on a blank
  page), upserts a narrative into the issue page body under section-scoped supersede rules,
  backfills commits missing from the audit log, transitions status, and renders a
  before/after viewer.
  Workspace-agnostic: every database id, property name, and status value is read from a local
  config file the skill builds on first run by inspecting live databases. No workspace
  identifiers are baked into the distributed skills.

#### Marketplace
- Catalog version 2.8.2 → 2.9.0 for the added plugin entry. `elian-store` stays published —
  the marketplace has no `deprecated` / `replaces` / `alias` field, so removing an entry
  silently orphans existing installs.

### [3.2.0] — 2026-07-23

Aligns the design pipeline on one canonical artifact layout. **Breaking / migration
required**: the default output path of `/design-ui` changes. Existing artifacts are not
moved or deleted; `--out` / `--from` preserve the old locations. See
`docs/migrations/design-artifact-path-v3.2.md`.

#### Changed
- `/design-ui` default output moves from `claudedocs/design/<feature>/` to
  `claudedocs/<label>/mockups/`, and the skill unifies on the canonical `<label>`
  identifier (the same one used by spec.json, `/design-feature`, and the roadmap).
  `--out` still overrides.
- `/design-ui` now emits `tokens.css` into the mockups dir (the Phase 4 design tokens as
  CSS custom properties; falls back to the shared `functional-spec/references/tokens.css`
  neutral system when no project tokens are defined), so the `/functional-spec` connected
  view's `../mockups/tokens.css` link resolves.
- `/functional-spec` keeps its canonical default input `claudedocs/<label>/mockups/` and
  documents the input-resolution priority (explicit `--from`, then the new default, then an
  unambiguous legacy path used only after telling the user, else ask). Added error handling
  for missing/ambiguous mockups, missing tokens.css, existing output, bad `--from`/`--out`.
- `/functional-spec` no longer claims `/design-feature` produces mockups (it never did).
  `/design-feature` now states the pipeline flow: it emits design docs and the roadmap,
  `/design-ui` emits `mockups/` + `tokens.css`, `/functional-spec` emits `functional-specs/`.

#### Added
- `docs/migrations/design-artifact-path-v3.2.md` — migration notes and compatibility guidance.
- Repository validator gains a `design-contract` check (canonical mockups path present, retired
  `claudedocs/design/<feature>/` path absent, no false design-feature-mockups claim, connected
  template links `../mockups/tokens.css`) plus three regression tests.

### [3.1.2] — 2026-07-23

Low-risk policy alignment after the safety baseline: correct one Codex classification and
close the `pr-review` posting gate. No Codex deployment changes.

#### Changed
- `spec-coverage` is reclassified from `claude_only` to `deferred`. Its coverage core
  (test-runner discovery, status/render scripts) is portable via Read/Write/Bash; only the
  optional PostToolUse auto-render hook is Claude-only. `deferred` reflects an intentional
  hold, not a runtime block. It is still not shipped to Codex — no symlink, no `setup.sh`
  entry — and Codex shipping stays pending host-conditioning of the hook guidance and a
  smoke test. Codex catalog counts updated to three Claude-only and seven deferred skills.
- `pr-review` review-posting commands (`gh pr review`, `gh pr comment`, `glab mr note`,
  `glab mr approve`) are removed from `allowed-tools`. Posting is now double-gated: an
  explicit user confirmation plus a capability/OS approval at execution time. The posting
  feature and all read-only query commands are retained; only the pre-authorization is
  removed.

#### Added
- The repository validator now flags any skill that pre-allowlists PR/MR posting commands,
  and flags a disposition-listed (`claude_only` / `prompt_only` / `deferred`) skill that
  also carries a `codex/skills` symlink. Two regression tests cover both rules.

### [3.1.1] — 2026-07-23

Hardens repository-defined skill safety and makes distribution drift mechanically detectable.

#### Fixed
- Side-effect-capable artifact, design, implementation, and maintenance skills now require
  explicit invocation through `disable-model-invocation: true`; broad shell permissions were
  narrowed, and decision-dashboard no longer exposes wildcard deletion.
- `review` and `pr-review` now use a capability-enforced read-only engineering reviewer. Persona
  reviewers no longer expose Bash.
- The `pr-review` perspective catalog and example review now dispatch every engineering lens to
  the read-only `engineering-reviewer`, matching the SKILL contract instead of naming
  write-capable domain agents.
- `update-design` guide references now resolve to `../design-feature/references/` instead of a
  nonexistent local `references/` directory.
- `fix`, `implement`, and `improve` skill-verification commands are now runnable shell syntax
  instead of Markdown links inside Bash code blocks.
- `pr-writer` is draft-only end to end and cannot create, submit, or merge a PR/MR.
- Core implementation workflows no longer assume that optional host skills such as `/commit`,
  `/simplify`, `/code-reviewer`, `/ship`, or `/document-release` are installed.
- Codex distribution now distinguishes 14 shared skills, two prompt-only skills, four
  runtime-blocked Claude-only skills, and six intentionally deferred portable skills.
- English-only distribution content is restored in Codex configuration, functional-spec
  guidance, design examples, and bundled HTML templates.

#### Added
- `scripts/validate_repository.py` checks skill contracts, side-effect gates, tool policies,
  read-only reviewer capabilities, cluster registration, Codex disposition, version parity,
  relative links, English-only distribution content, and source syntax.
- Ten stdlib regression tests cover frontmatter parsing, naming, duplicate IDs, side-effect
  gates, unsafe tool scopes, link handling, and cluster-disposition failures.
- `.github/workflows/validate-repository.yml` runs repository, YAML, bundled-validator, hook, and
  cluster checks on pull requests and pushes to `main`.
- `docs/repository-wide-ai-skills-audit.md` records the full inventory, skill-by-skill audit,
  scenario review, issue register, target architecture, migration phases, and post-change status.

### [3.1.0] — 2026-07-22

Adds requirement coverage tracking. The pipeline could produce a PRD and design
set, but nothing answered the question that matters during implementation:
**is every acceptance criterion actually proven?**

#### Added
- **`spec-coverage`** — requirement-to-test traceability. It seeds a leaf-level
  checklist from the design documents a feature already has, runs the project's
  test suite, parses the JUnit XML, and decides each item from the result.

  **Tests are the source of truth.** An acceptance criterion is `pass` only when
  a passing test carries its `R#-AC#` ID in its display name
  (`@DisplayName("R1-AC1 …")`, `it('R1-AC2 …')`). Any failing test carrying it →
  `fail`; only skipped tests → `skipped`; **no test at all → `unchecked`**, which
  is the "requirement not yet proven" signal and the reason the skill exists. The
  headline number is `ac_proven / ac_total`.

  Six categories are seeded, and the skill is explicit about which of them a
  machine actually checked: acceptance criteria (from `tech-spec.md` §2 when
  present — its rows already name the owning component / endpoint / table — else
  `prd.md` §6), scenarios (`qa-checklist.md`, `prd.md` §5), and API endpoints
  (`api-spec.md`) are decided by tests; state transitions (`design.md` §2) fall
  back to manual evidence; schema checks (`ddl.sql`) and open decisions
  (`design.md` §4) are manual only. Every rendered item is tagged
  machine-verified or human-asserted so a reader can tell a test result from a
  claim.

  Outputs `claudedocs/<label>/spec-coverage.json` (source of truth) and
  `spec-coverage.html` (view), in the same folder as the rest of the design set.
  `check` runs the suite in the same invocation — it will not present a stale
  JUnit XML from an earlier run as current evidence, the same discipline
  `verify-before-claiming` enforces. If no XML is found at all it fails loudly
  rather than reporting every criterion `unchecked`; "tests were not run" and "no
  test covers this" are different facts.

  Ported from the maintainer's personal global skill `verify-impl-status` rather
  than written from scratch — the leaf-checklist model, HTML renderer, and patch
  applier already worked. What changed: the checklist is now derived from the
  design documents instead of a hand-written Python data file, and status comes
  from test results instead of manual marking. The old `checklist-data.py`
  `importlib` path was dropped outright (executing a user-authored Python module
  out of `claudedocs/` is an arbitrary-code-execution path); its
  `merge_existing` / `recount` logic was preserved, so user-entered status still
  survives a regenerate. A bundled JUnit-XML fixture plus `scripts/validate.py`
  cover all four verdicts, the no-XML error path, and manual-evidence survival.

  The auto-render `PostToolUse` hook ships with the skill but is **not**
  registered in `plugin.json` — a `matcher: Bash` hook would fire on every Bash
  call for every user. `SKILL.md` documents opt-in via the project's own
  settings.

  **Five defects were found by adversarial review before this first shipped**,
  all of the same class: a confidently wrong number. Each is fixed and has a
  regression check in `scripts/validate.py` (12 checks total).
  - A manual `pass` written through `apply.py` counted toward the headline the
    renderer labels "AC proven by tests" — `{"R1-AC1":{"status":"pass"}}` could
    produce `AC proven: 1/1` with no test in existence. `ac_proven` now counts
    only items whose verdict came from a test; hand-asserted ACs are reported
    separately as `ac_claimed_manual` and shown under the headline.
  - A seed that missed an acceptance criterion silently shrank the denominator,
    so 10 of 12 ACs read as `10/10`. `build_status.py` gained `--prd`
    (repeatable): it extracts `R#-AC#` IDs from the PRD itself and exits 3 when
    the seed misses or invents one. Both documented invocations now pass it.
  - AC IDs were matched against `classname` as well as the test name, so every
    testcase in a class named after an AC bound to it — an unrelated passing
    helper could stand in as the proof after the real test was deleted. Binding
    is now display-name only, matching the documented convention.
  - A manual `skipped` waiver outranked every later test run, including a
    currently failing one, so something red rendered as "deliberately skipped".
    A waiver still survives a passing or skipped run; a failing test now wins.
  - Unparseable JUnit XML was warned about and skipped, so a truncated report
    from the run you just did, sitting beside an older parseable one, yielded
    stale verdicts presented as current. Any parse error is now fatal.

  `apply.py` also validates status against the allowlist before writing —
  `recount()` tallies with `{s: 0 for s in STATUSES}`, so a typo like `"passed"`
  did not raise, it dropped out of the counts and under-reported the totals.

#### Changed
- **`design-feature`** — Phase 5.1 adds a `spec-coverage.html` entry to
  `roadmap.json`'s `docs[]` (existing schema, no new fields), and Phase 5.3
  "Next steps" points at `/spec-coverage init <label>` for when implementation
  begins.
- **`update-design`** — `spec-coverage.json` joins the inventory, the impact
  matrix (✅ where the AC set moves, `cond` for API/flow changes), and the
  sequential update order at step 10. Re-seeding touches only the ACs a change
  added or removed; recorded evidence on untouched items survives.
- **`verify-implementation`** and **`verify-before-claiming`** — one boundary
  line each. Three verify-shaped skills now coexist: `verify-implementation`
  runs the project's `verify-*` rule skills, `verify-before-claiming` gates a
  single claim at the moment it is made, and `spec-coverage` traces requirements
  to the tests that prove them. The roadmap hub remains the plan/board view;
  `spec-coverage.html` is the proof view.

#### Fixed
- **`tools/generate.py`** — `--bump` scaffolded its CHANGELOG stub in the middle
  of the file. The anchor regex `^### \d+\.\d+\.\d+ ` did not match the
  bracketed `### [3.0.0] — …` form recent entries use, so it skipped every one
  of them and inserted before an older bare-form heading. It now matches both
  and emits the bracketed form.
- **`spec-coverage/scripts/collect_tests.py`** — an absolute `--results` glob
  (CI artifact directory, out-of-tree build) crashed with an unhandled
  `NotImplementedError` from `Path.glob`, which rejects non-relative patterns.
  Absolute patterns are now anchored at the filesystem root.
- **`TODOS.md`** — added, recording the deferred items this release produced:
  the end-to-end smoke that has not run against a real test suite, the Codex
  port of the design-pipeline skills, and the Korean console output in
  `verify-implementation/scripts/check-skill-discovery.py`.

#### Notes
- `spec-coverage` is recorded as a fifth Claude-only skill in
  `docs/claude-codex-skill-parity.md` — its contract is "run this project's test
  suite now and decide from the result", which needs the bundled scripts to be
  deterministic; a Codex prompt that guessed at status would defeat its purpose.
- The same parity document had prose left stale by v3.0.0: it still counted
  "six exceptions / four Claude-only", claimed 15 shared skills (14), and gave
  `document-writer`'s Claude-only reason as `~/.claude/skills/...` hardcoding —
  which v3.0.0 removed. Corrected; `document-writer` is now recorded as a
  deferred port, not a platform limitation.
- `docs/plugin-portfolio-hybrid-model.md` gains a *Requirement coverage*
  lifecycle slot and a written Skill Intake Record for `spec-coverage` —
  adding a skill one release after removing two warrants the checklist on the
  record rather than assumed.

### [3.0.0] — 2026-07-22

Design-pipeline consistency pass plus a portfolio trim. **Breaking**: two skills are removed.

#### Removed — BREAKING
- **`ai-assisted-feature-development`** — its nine phases duplicated skills that
  already exist: phases 1–5 are `intake-spec` + `design-feature`, phases 6–7 are
  `implement`, phase 8 is `review`. It wrote artifacts to its own layout
  (`references/artifact-structure.md`) rather than the shared
  `claudedocs/<label>/` set, so nothing downstream could consume them, and
  `disable-model-invocation: false` let it auto-trigger in competition with
  `intake-spec`.
  **Migration**: `/intake-spec` → `/design-feature` → `/implement` → `/review`.
- **`skill-dispatcher`** — duplicated the host's built-in skill discovery and
  each skill's own `when_to_use`. **Migration**: none needed; the host routes on
  `description` / `when_to_use`.

Both were removed from the Codex tree in the same change. Rationale and
migration paths are recorded in `docs/claude-codex-skill-parity.md`
("Retired Commands"). The catalog goes from 27 to 25 skills.

#### Added
- **`design-feature`** Phase 4 now generates **`tech-spec.md`**, the
  developer-facing counterpart to `prd.md`. `references/prd-guide.md` bans
  technical terms from the PRD body, which made `prd.md` explicitly a
  non-developer document while the developer-facing content stayed scattered
  across `design.md` / `architecture.md` / `api-spec.md` / `ddl.sql` with no
  entry point — the PRD's own checklist said "enough for BE to derive a Tech
  Spec", but no tech spec was ever produced.
  New guide `references/tech-spec-guide.md` defines a 7-section structure whose
  core is a **requirement → implementation mapping table** (every `prd.md` §6
  AC → owning component / endpoint / table). It is a map, not a copy: anything
  already in a Phase 3 document is linked, never restated. Technical terms are
  allowed — the inverse of `prd-guide.md`.
  The document-set gate becomes `A) Full — design-spec + prd + tech-spec +
  api-spec + qa-checklist`, `B) Core — prd + tech-spec + api-spec`, `C) PRD
  only`, `D) Stop here`.
  Phase 4 validation gains an AC-ID cross-check (`comm` over
  `R#-AC#` tokens) that fails on both a fabricated ID in `tech-spec.md` and an
  unmapped AC in `prd.md`.

#### Changed
- **`intake-spec` / `design-feature`** — `spec.json` moves from
  `claudedocs/plans/<label>/spec.json` to `claudedocs/<label>/spec.json`, so one
  feature lives in one directory instead of splitting the spec away from the
  documents generated from it. `design-feature` §0.2 still reads the legacy path
  as a fallback and says so on stdout when it hits, so existing specs keep
  working.
- **`update-design`** — the impact matrix was still describing the v2.25
  document set and knew nothing about the artifacts added in v2.26–v2.29.
  The inventory, impact matrix, and update order now cover `spec.json`,
  `tech-spec.md`, `roadmap.json`, `index.html`, `erd-preview.html`, and
  `functional-specs/`. Notably:
  - `spec.json` is updated first when requirements or AC change, so a later
    `/design-feature` re-run no longer regresses to a stale spec.
  - the `index.html` re-render step now carries the actual `build_roadmap.py`
    invocation (the same `CD=` resolver `design-feature` §5.2 uses). Before, the
    step said "re-render" with no command and could not be executed.
  - `erd-preview.html` is offered for regeneration only when `ddl.sql` changed
    **and** the file already exists — never created or regenerated silently.
  - consistency verification gains a `tech-spec.md` ↔ `prd.md` AC-ID check and a
    `roadmap.json` JSON-validity check.
- **`update-design` / `finish-branch`** — `/commit` and `/ship` are not part of
  this plugin; they are host-provided. Both skills now prefer them when present
  and fall back to the plain git steps otherwise, instead of hard-calling a
  skill that a plugin-only install does not have. `finish-branch` hands the PR
  body to the bundled `/pr-writer` rather than pre-approving `gh` / `glab`.
- **`document-writer`** — `SKILL.md` was entirely Korean, violating the
  repository's English-only rule, and every `build_doc.py` invocation hardcoded
  `~/.claude/skills/document-writer/scripts/build_doc.py`, a path that does not
  exist for anyone who installs this as a plugin even though the script ships in
  the bundle. Rewritten in English, and all invocations now use the
  `${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+...}}` resolver its sibling skills
  already use. A reference to a non-existent `document-generate` skill is gone;
  the real boundary against `create-document` is kept.
- **`document-writer/scripts/build_doc.py`** — the table-of-contents heading was
  hardcoded to `목차` regardless of `--lang`. It now follows the flag: `목차`
  for `ko` (still the default), `Contents` otherwise.
- **`harness-manager`** — Korean trigger phrases removed from the frontmatter
  description, which the repository rule explicitly forbids; English equivalents
  put in their place.
- **`functional-spec`** — instructions and trigger phrases translated to
  English. Korean strings that are *literal output labels* of the generated spec
  (`요소`, `기능 분해 표`, `재사용` / `신규`, …) are kept and now marked as such
  in the surrounding English text — the same treatment `kanban-board` gives its
  default board columns.

#### Fixed
- **`tools/generate.py`** — `discover_skills` treated any dot-directory under
  `skills/` as a skill, so a stray `.cc-writes` scratch directory made manifest
  validation fail with "skill '.claude' is not assigned to any plugin". It now
  skips dot-directories as well as `_`-prefixed ones.
- **`tools/clusters.json`** — `intake-spec`, `design-feature`, `update-design`,
  `erd-preview`, and `kanban-board` had never been assigned to a cluster. They
  now belong to `elian-design`, so `python3 tools/generate.py` validates again.
  (The 5-plugin split remains staged-only and unpublished.)

#### Notes
- The design-pipeline skills (`intake-spec`, `design-feature`, `update-design`,
  `erd-preview`, `kanban-board`) still have no `codex/skills/` counterpart. This
  is pre-existing drift, now recorded as a documented exception in
  `docs/claude-codex-skill-parity.md`: the artifact contract is still moving
  (this release relocated `spec.json` and added `tech-spec.md`), and porting a
  moving contract to a second tree doubles the churn. Port once it settles.

### [2.29.0] — 2026-07-16

#### Changed
- **`design-feature`** roadmap hub gains three additions. (1) Task drawers now
  support an optional **`features[]`** — a grouped, product-facing "what can a
  user do on this screen" checklist (✓/◐ per capability), rendered under **실제
  기능** and kept deliberately separate from the implementation-tracking
  `criteria`/`subs` (different audience: PM/QA verifying functional completeness
  vs. an implementer's checklist); the task's board row also shows a compact
  `기능 done/total` counter so completeness is scannable without opening the
  drawer. (2) Task `status` gains a **`dropped`** value
  plus a required **`reason`** field to record an explicit descope decision,
  instead of leaving descoped work as `todo` forever; dropped tasks show a
  **폐기** badge and are excluded from the progress % denominator (like `hold`;
  combining `hold` with `dropped` is a validation error). `links[]`/`docs[]`
  URLs with `javascript:`/`data:`-style schemes are neutralized at render time.
  (3) Phase 5 guidance now instructs auto-linking a screen task to its
  `functional-spec` document via the existing `links[]` field. All three are
  optional and backward compatible — roadmaps without them render unchanged.
  `create-document`'s `roadmap.schema.json` + `build_roadmap.py` and the
  `roadmap-schema.md` / `roadmap-task-guide.md` references updated accordingly.

### [2.28.0] — 2026-07-16

#### Changed
- **`design-feature`** Phase 3 now offers an optional **`erd-preview.html`** — when
  the design produces a `ddl.sql`, the Phase 3 gate asks whether to also emit an
  interactive ERD **lineage explorer** (via the sibling `erd-preview` skill) built
  from that DDL, so the schema is reviewable with real/representative rows and
  click-to-trace lineage, not just the static Mermaid `classDiagram`. Gated —
  generated only on confirmation, only when `ddl.sql` exists. `references/doc-types.md`
  updated to document the new optional Phase 3 artifact.

### [2.27.0] — 2026-07-16

#### Added
- **`erd-preview`** — a "Lineage Explorer" skill. Given a table schema plus **real
  rows** (introspected from a live read-only DB, or supplied via DDL / design docs /
  pasted query results), it fills a validated self-contained HTML template where
  clicking one record highlights only that record's lineage: upstream FK ancestors
  ("sources") and downstream descendants ("impacts"), dimming the rest. Follows both
  **hard foreign keys** (solid lines) and user-declared **soft references** (dashed
  lines — value-level joins that are not schema FKs, e.g. a non-PK business-key
  match), summarizes sources/impacts in a side panel, and ships a Figma-style
  zoom/pan viewer for large schemas. A bundled `scripts/validate.py` checks
  referential integrity, cardinality, LAYERS coverage, and left→right layer ordering
  (parsing the JS literals with Node). Standalone — no external skill dependency.

### [2.26.0] — 2026-07-03

#### Changed
- **`functional-spec`** gained a cross-wireframe **Component Design phase** (Phase 2):
  before any per-screen spec, it now surveys *all* wireframes together and designs a
  **shared component catalog** (usage matrix + shared vs screen-specific), so recurring
  UI (rows, cards, nav, buttons) is designed once and each screen's §③ references it —
  eliminating the duplicate component work that per-screen-only design produced.
  **Greenfield** is now a first-class grounding mode (ground to the designed
  API/entities when there is no codebase to grep). New reference:
  `references/component-design-template.md`.
- **`functional-spec` connected view** rebuilt to be project-independent and robust:
  the wireframe's linked `tokens.css` no longer breaks the spec table (namespaced
  `.fs-*` classes + a scoped `:where(table,tr,td,th)` reset), the layout is responsive
  (split stacks, table scrolls on narrow widths), and the page now renders the **§③
  component contract** inline (not just the ② decomposition). Fixes a real collision
  where a wireframe `.row{display:flex}` collapsed the table.

#### Added
- `tools/dev-install.sh` — installs the working-tree `elian-store` into the local
  plugin cache so the **whole pipeline** runs as real installed skills for end-to-end
  testing (no merge/PR needed); `--revert` to undo.

### [2.25.0] — 2026-07-03

#### Added
- New skill **`functional-spec`**: bridges an approved wireframe/mockup to a
  **code-grounded implementation contract** before any code is written — the
  layer that was missing between `/design-ui` (design-only, no code) and
  `/implement`. For each screen it (1) grounds every wireframe element in the
  real codebase (existing components to reuse resolved to actual file paths,
  real endpoints/fields, new-vs-existing components), (2) produces a numbered
  **기능 분해 표** with real-server-round-trip done-criteria, (3) writes a
  component contract (신규/재사용 + data flow), (4) records BE dependency and
  numbered open questions, and (5) renders a per-screen `.md`, a
  wireframe↔spec split **`-connected.html`** view (hovering either side
  highlights the matching element), and an `index.html` hub. Reads code
  heavily; writes no product code. Positioned after `/design-ui` or
  `/design-feature` mockups and before `/implement`.
- `design-ui` (Phase 5) and `design-feature` (Phase 5 report) now point
  downstream to `/functional-spec` before `/implement`.

### [2.24.0] — 2026-07-01

#### Added
- New skill **`kanban-board`**: generates a self-contained, interactive HTML
  Kanban board (draggable columns/cards, card detail panel with assignee,
  due date, labels, checklist, comments, and linked files, search/filters,
  and a cobalt/sage/grape theme switcher) from the project's own local task
  data — a `/intake-spec` `spec.json`, a `/design-feature` roadmap or PRD, a
  `.claude/plans/` file, or tasks described directly in chat. No
  GitHub/GitLab/Jira integration by design; the board is a single offline
  HTML file with no server, and in-board edits persist via `localStorage`
  plus an Export/Import JSON control for committing snapshots back to the
  repo. Re-running the skill merges in new cards from the source without
  overwriting prior in-board edits. Ships `scripts/build_board.py` (stdlib
  Python, validates list/member/label cross-references before rendering)
  and `assets/kanban-board-template.html` (vanilla JS/CSS, no framework or
  build step). Visual/interaction design based on a user-supplied Claude
  Design reference ("Kanflow").

### [2.23.0] — 2026-06-26

#### Added
- New skill **`update-design`**: design-change propagation orchestrator. When
  `design-feature` docs already exist and something changes (meeting feedback,
  review findings, requirement revision), runs an impact matrix across all
  generated documents (`design.md`, `ddl.sql`, `architecture.md`,
  `design-spec.md`, `prd.md`, `api-spec.md`, `qa-checklist.md`), confirms
  scope with the user, and updates only the affected files sequentially.
  Reads `references/prd-guide.md` and `references/architecture-guide.md`
  before editing those documents. Delegates 3+ pending decisions to
  `/decision-dashboard`. Pair with `/design-feature` (creates docs) and
  `/intake-spec` (re-capture requirements if they changed dramatically).

---

## elian-workflow Plugin

### [1.0.0] — 2026-07-29

Initial release. Issue-cycle bookends that record engineering work history to Notion.

#### Added
- **`/issue-open`** — start an issue: verify the branch upstream points at itself (a
  base-branch upstream makes `git pull` drag the base into the feature branch and `git push`
  risk overwriting it, and worktrees inherit it silently), move the task to in-progress with
  a start date, report whether design documents and open decisions exist, and seed the issue
  page body with the metadata and background that are only clear at kickoff. Never creates,
  switches, or deletes a branch.
- **`/issue-close`** — close an issue: interview against the commit list for the design
  decisions and dropped alternatives that a diff cannot show, upsert a narrative into the
  issue page body under section-scoped supersede rules, backfill commits missing from the
  audit log, transition status, and render a before/after HTML viewer. Recording only — it
  never merges, pushes, or deletes, and it must run while the branch still exists because
  the commit range is its source.
- `skills/_shared/narrative-template.md` — the canonical issue-history format (metadata →
  summary → background → decisions → alternatives → changes → verification → outcome →
  references → collapsed commit log), with the supersede safety rules that keep an update
  from overwriting hand-written sections.
- `skills/_shared/notion-workspace-config.md` — the local config schema and its
  discovery-based first-run setup.

#### Why this plugin exists
Development work has three nested cycles — commit, issue, day. Per-commit logging and daily
wrap-ups existed; the issue level, which carries the decisions, architecture, and remaining
checks, had no skill at all. That content is exactly what a diff cannot reconstruct.

#### Design constraint
Workspace-agnostic by construction. Every database id, property name, and status value is
read from `~/.claude/notion-workspace.json` (or `.claude/notion-workspace.json` per
repository), which the skill helps build on first run by inspecting live databases rather
than guessing. No workspace identifier is baked into the distributed skills — that is what
makes them publishable rather than personal.

#### Not shipped to Codex
Both skills depend on a Notion MCP server, which is a Claude-side integration. Recorded as a
deliberate parity exception in `docs/claude-codex-skill-parity.md`, not an oversight.

---

## Marketplace (`elian`)

### Unreleased

#### Added
- Added a **thematic-cluster generator** at `tools/generate.py` (config: `tools/clusters.json`) for the Phase A dual-tool distribution. Report-only by default; lints every `SKILL.md` for host-agnostic script paths, reports `codex/skills/` symlink status, gates version drift (`plugin.json` vs marketplace entry), and (with `--emit`) renders five composition-respecting plugins (`elian-artifacts`, `elian-tdd`, `elian-review`, `elian-design`, `elian-harness`) plus a marketplace catalog to the gitignored `dist/`. `--bump {patch|minor|major}` automates the release ratchet (bump `plugin.json` + the marketplace entry + a dated CHANGELOG stub). The live `plugins/elian-store/` bundle is untouched; the split is staged, not cut over. Design recorded in `.claude/plans/dual-tool-skill-distribution.md`.
- Added a **Claude workflows distribution tree** at `.claude/workflows/` — a third copy-distributed surface (alongside `codex/`), since Claude Code plugins cannot register Workflow-tool workflows. Ships `harness-legacy-scan.js`, a portable, read-only AI-coding-harness audit (`/harness-legacy-scan [project-path]`) that discovers the environment at runtime and classifies findings KEEP/SHRINK/MOVE/SPLIT/CONVERT/DELETE. Documented in `.claude/workflows/README.md`, the root README, and `docs/repository-operating-map.md`. (`harness-diet` is intentionally not included — its existing form is a machine-specific one-time replay, not a reusable tool.)
- Removed the duplicate `.agents/skills/` tree (a byte-for-byte copy of `.claude/skills/`) and documented `.claude/skills/` ownership (maintainer dev tooling, not product) in `docs/repository-operating-map.md`.
- Ported all 13 bundled Claude skills to Codex prompts under `codex/prompts/`, covering `brainstorm`, `review`, `persona-review`, `ai-assisted-feature-development`, `design-ui`, `decision-dashboard`, `create-document`, `implement`, `fix`, `improve`, `manage-skills`, `verify-implementation`, and `generate-teammate`.
- Added and refreshed the Codex docs entry points so `README.md` and `codex/README.md` describe the prompt catalog, install flow, and current scope.
- Added `plugins/elian-store/README.md` as a plugin-local guide for real usage, edit locations, and validation boundaries.

#### Changed
- Refreshed `docs/claude-codex-skill-parity.md` to reflect the shared-skill Codex catalog and the remaining platform-limited gaps.
- Kept Codex prompts as plain Markdown on purpose; no YAML frontmatter was added to the prompt files.
- Added an explicit output contract to `codex/prompts/persona-review.md` so all Codex prompts now share the same invocation / forbidden / output-contract shape.

#### Notes
- The thematic 5-plugin split (`tools/generate.py --emit` → gitignored `dist/`) is **intentionally staged-only, not published**. `elian-store` stays the single published plugin per `docs/plugin-portfolio-hybrid-model.md` ("Split decision, 2026-06-12"): the clusters share one audience, permission profile, and release cadence, so the bundle is not harmful, and the marketplace has no graceful-removal path. It will be published cluster-by-cluster only when a real divergence appears.
- `generate-teammate` remains handoff-only on Codex because the runtime cannot reproduce the plugin-side teammate-spawn flow exactly.
- `manage-skills` and `verify-implementation` remain prompt-level orchestration equivalents rather than byte-for-byte skill/runtime matches.

### 2.22.0 — 2026-06-26

#### Fixed

- **`intake-spec/scripts/detect_provider.sh`** — git remote origin is now checked first (before installed CLI tools). Prevents incorrectly returning `gitlab` when `glab` is authenticated but the current repo is GitHub.
- **`intake-spec/SKILL.md`** — Phase B adds question 6 (done condition / AC). Phase C `spec.json` schema adds optional `acceptanceCriteria` field so downstream `design-feature` Phase 4 has a seed for G-W-T tables.
- **`design-feature/SKILL.md`** — Phase 3 `architecture.md` now explicitly references `references/architecture-guide.md` before writing, matching the same pattern already applied to `prd.md` and `design-spec.md`.

### 2.21.0 — 2026-06-26

#### Added

- **`design-feature/references/roadmap-task-guide.md`** — task writing guide ported from local MPT-9419 project learnings. Covers: behaviour-first title principle, `desc`/`criteria`/`subs` section roles, before/after examples (real alimtalk notification task), title checklist (class names / file paths / vague verbs to avoid), and Mermaid `sequenceDiagram` usage in `desc` with role-naming rules.

#### Changed

- **`design-feature/SKILL.md`** — Phase 5.1 now references `references/roadmap-task-guide.md` before writing task objects; References section updated.
- **`design-feature/references/roadmap-schema.md`** — Fixed stale reference: `--template roadmap` → `build_roadmap.py`.

### 2.20.0 — 2026-06-26

#### Added

- **`design-feature/references/prd-guide.md`** — PRD authoring guide ported from the local `create-prd` skill. Specifies the 12-section mandatory structure, technical term blacklist (Aggregate/Entity/Mapper/JSON/XOR/…), mandatory Given-When-Then AC table format for every §6 requirement, and three post-generation consistency checks (tech term grep, AC coverage, OOS consistency).
- **`design-feature/references/architecture-guide.md`** — Architecture document guide ported from local `manage-architecture-doc`. Defines the 4-section mandatory structure (Overall / Backend / Frontend / Infrastructure), AS-IS/Δ/TO-BE skeleton with one-liner rules for unchanged layers, Mermaid aggregate color convention (`aggTag`, `aggRule`, `aggBulk`, `aggSpec`, `aggRabbit`), and five post-generation validation commands.
- **`design-feature/references/design-spec-guide.md`** — New document type: FE design spec (`design-spec.md`). Covers 8-section structure (IA, per-screen detail, user journeys, entity state diagrams, terminology), Mermaid requirements (`stateDiagram-v2` for entity lifecycle, `flowchart` for user journeys), and a pre-handoff checklist.

#### Changed

- **`design-feature/references/doc-types.md`** — Added `design-spec.md` as a Phase 4 document type with generation conditions and guide reference. Generation decision table expanded from 6 to 7 columns.
- **`design-feature/SKILL.md`** — Three improvements:
  1. **Phase 0.4 auto-restart detection**: when `--start-from` is not supplied, scans `claudedocs/<label>/` and suggests the correct restart point (index.html → re-render; prd.md → Phase 5; design.md → Phase 4; nothing → Phase 1).
  2. **Phase 4 gate**: changed from a binary confirm to a 4-option selector (A: full set / B: core / C: PRD only / D: stop). `design-spec.md` generation is gated on FE screen changes per the decision table.
  3. **Phase 5.3 report**: upgraded from a 3-line file list to a structured completion report with artifact inventory table, stakeholder access matrix, and next-steps section.

### 2.19.0 — 2026-06-26

#### Added

- **`/intake-spec`** (`skills/intake-spec/`) — provider-agnostic requirements front door. Replaces the JIRA-specific local `intake-issue` for contexts without an issue tracker. Auto-detects authenticated providers via `scripts/detect_provider.sh` (GitLab/glab → GitHub/gh → JIRA env → none). Works entirely from free-text requirements when no issue tracker is available. Produces `claudedocs/plans/<label>/spec.json` and hands off to `/design-feature`.
- **`/design-feature`** (`skills/design-feature/`) — self-contained design orchestrator. Takes a `spec.json` or inline requirements and generates a full design document set (design.md, ddl.sql, architecture.md, prd.md, api-spec.md, qa-checklist.md) through five gated phases. Requires Mermaid diagrams for state machines and cross-service flows. Renders a Mermaid-capable roadmap hub (`index.html`) via `create-document`'s `build_roadmap.py`. Supports `--start-from phaseN` for resuming mid-pipeline.
- **`create-document/scripts/build_roadmap.py`** — standalone roadmap renderer bundled in `create-document`. Validates `roadmap.json` against `roadmap.schema.json`, renders a self-contained `index.html` with the interactive vertical timeline, task drawer, and **Mermaid diagram support** in task `desc` fields (`` ```mermaid `` blocks render as live diagrams via the Mermaid.js CDN). Ported and extended from the local `design-issue/scripts/build_index.py`.
- **`create-document/schemas/roadmap.schema.json`** — JSON schema for `roadmap.json`. Validates label, title, phases/tasks (status enum, optional fields), docs, and stakeholders.
- **`create-document/scripts/render.py`** — added Mermaid block detection to `{{key}}` substitution. String values matching the `` ```mermaid\n...\n``` `` pattern now render as `<div class="mermaid">...</div>` instead of HTML-escaped text, enabling Mermaid diagrams in any template that uses the FOREACH engine.

### 2.18.0 — 2026-06-23

#### Added
- **Three new skills derived from [obra/superpowers](https://github.com/obra/superpowers)**, each filling a gap elian-store had nowhere else. The skills borrow superpowers' mechanisms but not its always-on/coercive framing — two are always-on read-only behavioral gates, one is opt-in and side-effecting.
  - **`/verify-before-claiming`** (`skills/verify-before-claiming/`, elian-review) — a claim-time honesty gate: "no completion claim without fresh verification evidence." Ships the Iron Law, a Gate Function (IDENTIFY→RUN→READ→VERIFY→claim), a `Claim → Requires → Not sufficient` table, and a rationalization table. Always-on (`disable-model-invocation: false`), read-only. Its `when_to_use` explicitly disambiguates from `/verify-implementation` (which discovers/runs project verify-* skills) — this gate proves the specific claim you are about to make.
  - **`/respond-to-review`** (`skills/respond-to-review/`, elian-review) — the consumer side of code review (the producer side is `/review` and `/pr-review`): verify each suggestion against the codebase before implementing, no performative agreement ("You're absolutely right!"/thanks), push back with technical reasoning when wrong, clarify all ambiguous items first, YAGNI-grep "implement properly" asks. Triages and hands execution to `/fix` or `/improve`. Always-on, read-only.
  - **`/finish-branch`** (`skills/finish-branch/`, elian-harness) — disposition of a finished branch: verify tests → detect workspace → present a closed merge / push+PR / keep / discard menu → execute with safety invariants (merge before worktree-remove before branch-delete; only remove worktrees you own; typed `discard` confirmation; never force-push unrequested). Thin by design: the push+PR option delegates to `/ship` and commit authoring to `/commit`; native worktrees are cleaned via `ExitWorktree`. Opt-in (`disable-model-invocation: true`); registered as the fourth Claude-only skill (native worktree tooling) in `docs/claude-codex-skill-parity.md`.
- `verify-before-claiming` and `respond-to-review` ship to Codex as shared `codex/skills/` symlinks (portable); each carries its own `scripts/validate_skill.py`. `finish-branch` is Claude-only (no validator script, matching `harness-manager`).

#### Notes
- Bumped the `elian-store` plugin version (`2.17.0` → `2.18.0`, minor — three new user-visible skills, backward compatible). The marketplace metadata version stays at `2.8.2` (no catalog-structure change). Registered all three in `tools/clusters.json` (elian-review ×2, elian-harness ×1; `finish-branch` in `codex.claude_only`).

### 2.17.0 — 2026-06-23

#### Added
- **`/brainstorm` gained four design-discipline gates**, borrowing the back-half rigor of [obra/superpowers](https://github.com/obra/superpowers)' `brainstorming` skill without adopting its always-on auto-invocation posture (the skill stays `disable-model-invocation: true`, opt-in, and keeps its MVP/Exceptions philosophy):
  - **Implementation Hard Gate** — a callout after the Workflow diagram plus a Standing Rule and two Forbidden items: no code, scaffolding, mutating command, or implementation-skill invocation (`/implement`, `/generate-teammate`) until the Phase 5 decision is approved, regardless of perceived simplicity. Reflected in the Phase-5 line of the workflow diagram.
  - **Plan self-review** — a Phase 6 sub-step that re-reads the written plan/doc artifact for placeholders, internal contradictions, scope, and ambiguity and fixes them inline. Explicitly distinct from the end-of-skill process **Reflection** (which critiques the brainstorm, not the file).
  - **Written-plan review gate** — after self-review, the user reviews the written `.claude/plans/{id}.md` before any downstream handoff; change requests loop back through self-review. `--output none` skips both file-gated steps. Added to the **Manual decision gating** table.
  - **Design-quality guidance** — a fourth Phase 3 drafting principle: each option names its module boundaries, the interface/contract each unit exposes, and its dependencies (*what it does / how it's used / what it depends on*), not just file scope. Mirrored in the **Pre-flight checklist**.
  - `scripts/validate_skill.py` continues to PASS (all 10 required sections intact); `SKILL.md` is 466/500 lines. The Codex companion (`codex/skills/brainstorm`) is a symlink, so it inherits these changes automatically — no separate prompt edit and no parity-doc change.

#### Notes
- Bumped the `elian-store` plugin version (`2.16.0` → `2.17.0`, minor — new backward-compatible behavior gates inside an existing skill; no parameter, output mode, or invocation contract changed). The marketplace metadata version stays at `2.8.2` (no catalog-structure change).

### 2.16.0 — 2026-06-19

#### Changed
- **`/persona-review` now auto-selects reviewers by default.** Previously the skill defaulted to a single `daniel` review and required an explicit `--persona` (or `all`/comma-list) to use more lenses, so most runs returned one or two perspectives. Phase 0 is rewritten: when no `--persona` is given (or `--persona auto`), the skill reads the target, matches it against a **signal map** of expertise axes, and dispatches the matching read-only persona reviewers in parallel — one persona for a single-axis target, several for a multi-axis target (capped at the 3 strongest), with a `daniel` fallback when no axis clearly matches. Multi-persona runs add one `## Lead synthesis`. An explicit `--persona <name>|all|comma-list|<path>` still overrides auto-selection.

#### Added
- **8 new built-in personas**, expanding the roster beyond its backend/code-quality focus into frontend, UX, accessibility, API, business, and marketing lenses: `abramov` (Dan Abramov — frontend state ownership and data flow), `evanyou` (Evan You — reactivity boundary and component-API ergonomics), `norman` (Don Norman — human-centered usability), `rams` (Dieter Rams — UI visual hierarchy and restraint), `dunford` (April Dunford — marketing positioning), `christensen` (Clayton Christensen — jobs-to-be-done and disruption), `watson` (Léonie Watson — accessibility and assistive-technology), and `fielding` (Roy Fielding — REST/HTTP contract design). Each ships a persona definition (`references/personas/<slug>.md`) and a read-only reviewer subagent (`agents/persona-<slug>-reviewer.md`).
- **Wired the two existing orphan personas** `beck` (Kent Beck — TDD/XP) and `fowler` (Martin Fowler — refactoring/enterprise architecture) into the router; their definition and agent files already existed but were unreachable from `SKILL.md`. The selectable roster is now 14 personas plus custom. Their definition files were also translated from Korean to English (now that real dispatch routes to them, they fall under the repo's English-only rule).
- Updated `scripts/validate_skill.py` to require and read-only/no-scorecard-check all 14 named persona reviewer agents (plus the existing custom reviewer), and ported the auto-selection signal map, expanded persona table, and per-persona lens bullets to the Codex companion prompt (`codex/prompts/persona-review.md`) for parity.

#### Fixed
- De-collided overlapping persona axes introduced while wiring the roster: `martin` owns **function-level** code smells and `fowler` owns **structural (module-level)** code smells in both the persona-library and the signal map; removed the stale `TDD` / `test strategy` descriptors from `martin` in the Codex Phase 2 table (those belong to `beck`) so the Codex prompt matches `SKILL.md`. Refreshed the `persona-review` row in `docs/claude-codex-skill-parity.md`, which still described the old single-`daniel` default and 4-persona roster.

#### Notes
- Bumped the `elian-store` plugin version (`2.15.0` → `2.16.0`, minor — new personas and a changed default selection behavior, backward compatible since `--persona` still pins a single lens). The marketplace metadata version stays at `2.8.2` (no catalog-structure change).
- Security (`schneier`) was intentionally left out of this batch. With `beck` and `fowler` translated, all 14 persona definition files under `references/personas/` are now English, satisfying the repo's English-only rule.

### 2.15.0 — 2026-06-12

#### Added
- **`/pr-review`** — new skill at `plugins/elian-store/skills/pr-review/`. Orchestrates a multi-perspective review of an existing pull request (GitHub PR) or merge request (GitLab MR) — the review counterpart to `/pr-writer`. Resolves the PR (current branch, `pr:<id>`, or URL), gathers its description, linked issue, commits, diff, and CI status, then dispatches a panel of independent read-only reviewers: always-on engineering specialists (correctness, security, performance, architecture, tests/maintainability, requirements-fit), scope-triggered specialists (frontend/UX, backend, data/migrations, API contract, devops, docs), and all six persona judges (Beck, Dean, Evans, Fowler, Martin, Daniel) reusing the bundled `agents/`. Synthesizes the panel into one verdict (Approve / Comment / Request changes) — deduping by `path:line:category`, raising confidence on cross-perspective agreement, surfacing conflicting opinions as trade-offs, and contrasting the diff against stated intent. Local report by default; posts to the PR (`gh pr review` / `glab mr note`) only after explicit confirmation; never merges or edits code. References: `perspectives.md` (per-lens questions and red flags) and `example-review.md` (worked BEFORE/AFTER report).

#### Fixed
- Addressed `/pr-review` panel findings on the introducing PR (#23): added the POST + auth commands (`gh pr review`/`gh pr comment`, `glab mr note`/`glab mr approve`, `gh`/`glab auth status`, `git remote`) to the `pr-review` `allowed-tools`; the SessionStart update hook now strips ESC bytes from queued notifications (terminal-escape hardening), excludes the maintainer-facing `#### Notes` subsection from the CHANGELOG excerpt, and derives `ELIAN_STORE_PLUGIN_ROOT` from the bound migrations path. Added `--selftest` cases for the steady-state guard, a corrupt marker, and Notes exclusion. Fixed a stale "four exceptions" reference in `docs/claude-codex-skill-parity.md` and clarified the README Claude-only wording.
- Hardened the migration runner ahead of its first script: concurrent SessionStarts are serialized with an atomic `mkdir` lock (portable — `flock` is absent on macOS — with 5-minute stale-lock recovery); a per-script checkpoint advances the recorded version after each success so a mid-chain failure no longer re-runs already-applied scripts; each script gets a wall-clock budget (`ELIAN_STORE_MIGRATION_TIMEOUT`, default 60s) so a hung script can't wedge SessionStart; and scripts run with a minimal environment (`PATH`/`HOME`/`TMPDIR`/`LANG`/`LC_ALL` + `ELIAN_STORE_*`) so session secrets are never exposed. New `--selftest` cases cover the lock, checkpoint, timeout, and env isolation.

#### Notes
- `pr-review` is documented as a **Claude-only** skill in `docs/claude-codex-skill-parity.md`; its core is parallel multi-subagent panel dispatch, which the Codex runtime cannot reproduce (same rationale as `generate-teammate` / `persona-review`).
- Bumped the `elian-store` plugin version (`2.14.0` → `2.15.0`, minor — new user-visible skill). The marketplace metadata version stays at `2.8.2` (no catalog-structure change).

### 2.14.0 — 2026-06-12

#### Added
- Extended the SessionStart update hook with short CHANGELOG excerpts in queued update notifications. When the remote `CHANGELOG.md` is reachable, users now see the relevant release section before the manual `/plugin marketplace update` and `/plugin update` commands.
- Added the version migration runner structure under `plugins/elian-store/migrations/`. Future `vX.Y.Z.sh` scripts run once after an installed plugin moves from an older recorded version to the current local `plugin.json.version`; first installs record the current version and skip historical migrations.
- Added `plugins/elian-store/hooks/check-update.sh --selftest` to cover CHANGELOG extraction, migration ordering, marker updates, and first-install skip behavior without network access.

#### Notes
- Bumped the `elian-store` plugin version (`2.13.0` → `2.14.0`, minor — update lifecycle behavior change). The marketplace metadata version stays at `2.8.2` (no catalog-structure change).

### 2.13.0 — 2026-06-12

#### Added
- **`/skill-dispatcher`** — new opt-in router at `plugins/elian-store/skills/skill-dispatcher/`. It recommends the smallest relevant `elian-store` skill for a request, says when no special skill is needed, and stops instead of chaining into downstream workflows. This adds a discovery layer without making every task pass through a proactive dispatcher.
- Added the matching Codex shared-skill symlink target via `tools/clusters.json` / `codex/skills/skill-dispatcher`, keeping the Claude and Codex routing behavior on one `SKILL.md`.

#### Changed
- Documented Claude Code marketplace auto-update guidance in the root README and plugin README while keeping the explicit `/plugin marketplace update` + `/plugin update` commands for manual refreshes.
- Recorded the current multi-host decision in `docs/claude-codex-skill-parity.md`: keep the current symlink + hand-authored prompt model for Claude + Codex, and defer template/adapter generation until a third host is a real target.

#### Notes
- Bumped the `elian-store` plugin version (`2.12.0` → `2.13.0`, minor — new user-visible skill). The marketplace metadata version stays at `2.8.2` (no catalog-structure change).

### 2.12.0 — 2026-06-12

#### Changed
- Reworked `generate-teammate`'s execution-mode decision logic to match the empirical evidence on multi-agent orchestration (deep-research synthesis of Anthropic's multi-agent research system, Cognition's "Don't Build Multi-Agents," the MAST failure taxonomy / NeurIPS 2025, and the CodeCRDT coding benchmark). Seven changes:
  1. **Cheaper-first prior.** Core Philosophy now states `Direct < Subagent < Agent Team` as a cost-and-risk prior instead of "no fixed priority." Phase-type still does not dictate the approach, but ties go to the cheaper option.
  2. **Economic viability gate (Phase 3).** A mandatory gate names each non-Direct phase's cost multiplier (Direct 1× / Subagent ~N× / Agent Team ~15× + super-linear coordination) and forces a downgrade to Direct when the parallel benefit does not justify it. The multiplier is surfaced in the Phase 6 confirmation.
  3. **Integration reconciliation (Phase 7).** A new mandatory single-agent cross-boundary build/typecheck after any parallel write phase — file-ownership separation prevents textual conflicts, not the ~5–10% (up to ~80% on complex tasks) semantic seam conflicts. Tracked as a team-level Definition of Done.
  4. **Multi-perspective default inverted.** Research / Design / Strategy patterns now default to independent Subagents (one per lens) + a single synthesizer; a *communicating* Agent Team is reserved for genuine real-time reconciliation (e.g. BE↔FE API-contract negotiation).
  5. **Single-agent synthesis is a hard rule.** Coherence-critical artifacts (one design doc / report / schema) are authored by one agent; co-writing is forbidden.
  6. **Full-artifact handoffs.** Coherence-critical phase handoffs pass the full artifact, not a lossy summary, to stop downstream agents from silently re-deciding.
  7. **Delegation triage.** A Phase 2.0 triage can short-circuit to Direct, and over-decomposition is now an explicit anti-pattern in the Forbidden list and standing rules.
- Added `references/execution-evidence.md` (the cited empirical basis), four new standing rules (9–12), spec criterion I-10, and synced the Codex prompt (`codex/prompts/generate-teammate.md`) to parity.

#### Notes
- Bumped the `elian-store` plugin version (`2.11.2` → `2.12.0`, minor — decision-logic behavior change). The marketplace metadata version stays at `2.8.2` (no catalog-structure change).

### 2.11.2 — 2026-06-12

#### Added
- Skills-based Codex distribution. `codex/skills/<name>` are relative symlinks into the shared plugin skill tree, and `codex/setup.sh` installs them into `~/.codex/skills/` (Codex follows symlinks, so `git pull` updates them with no re-copy). Migrated **12 commands** from hand-mirrored Codex prompts to shared skills (symlinks generated by `tools/generate.py`), retiring the corresponding `codex/prompts/*.md`. Only `generate-teammate` and `persona-review` stay prompts — their core is Claude subagent dispatch that Codex cannot reproduce. Codex catalog is now 2 prompts + 12 shared skills.

#### Fixed
- Made six skills' `SKILL.md` host-agnostic so one file runs on both Claude Code and Codex: `create-document`, `decision-dashboard`, `design-ui`, `generate-teammate`, `manage-skills`, and `verify-implementation` no longer hard-depend on `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}`. Script paths resolve via a `${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+...}}` → `${CODEX_HOME:-$HOME/.codex}/skills/...` fallback. On Codex (both vars unset) those scripts were previously unreachable. `manage-skills` and `verify-implementation` were caught by the new `tools/generate.py` lint.

#### Notes
- Bumped the `elian-store` plugin version (`2.11.1` → `2.11.2`). The marketplace metadata version stays at `2.8.2` (no catalog-structure change).
- `generate-teammate` is host-agnostic at the `SKILL.md` level but stays a Codex prompt — its teammate-spawn/subagent dispatch flow cannot be reproduced on Codex (handoff-only), so shipping it as a Codex skill would advertise a flow that does not run there.

### 2.11.1 — 2026-06-11

#### Fixed
- Corrected the Codex skills surface in `plugins/elian-store/skills/harness-manager/references/harness-map.md`. Codex loads skills from both `~/.codex/skills/` (legacy, still active) and the Agent Skills open-standard locations (`.agents/skills/`, `$HOME/.agents/skills`, `/etc/codex/skills`); the previous map listed only `~/.codex/skills/`. Added a note that Claude Code and Codex have converged on the same `SKILL.md` Agent Skills standard — empirically verified on Codex CLI 0.139 that Codex loads a `SKILL.md` carrying Claude-only frontmatter keys (`disable-model-invocation`, `user-invocable`, `allowed-tools`) without error — which makes the `Commands ↔ Prompts` mapping partly legacy.

#### Notes
- Bumped the `elian-store` plugin version (`2.11.0` → `2.11.1`). The marketplace metadata version is intentionally left at `2.8.2` because the catalog structure (the set of plugins) did not change — only the plugin's contents did.

### 2.11.0 — 2026-06-10

#### Added
- **`/pr-writer`** — new skill at `plugins/elian-store/skills/pr-writer/`. Drafts review-friendly pull request (GitHub PR) and merge request (GitLab MR) titles and descriptions from the git diff, commits, branch name, issue/ticket references, test evidence, and any repository PR/MR template. Goes beyond diff-summary by contrasting **intent vs implementation** (which requirement each change satisfies, what is missing, what went beyond scope). Detects GitHub (`gh`) vs GitLab (`glab`) from the remote and auto-detects the base branch (upstream → `origin/main` → `origin/master` → `main` → `master`). Draft-only posture: never pushes, creates, or merges unless explicitly asked. References: `pr-style.md` (title/body conventions, sizing, anti-patterns, tone) and `examples.md` (good vs bad PRs, intent-contrast block); `scripts/collect-pr-context.sh` is a read-only one-shot git context collector.
- Added the matching Codex prompt `codex/prompts/pr-writer.md` so `/pr-writer` ships in both trees, and recorded the parity in `docs/claude-codex-skill-parity.md`.

#### Notes
- Bumped the `elian-store` plugin version (`2.10.0` → `2.11.0`). The marketplace metadata version is intentionally left at `2.8.2` because the catalog structure (the set of plugins) did not change — only the plugin's contents did.

### 2.10.0 — 2026-06-08

#### Added
- **`/harness-manager`** — new skill at `plugins/elian-store/skills/harness-manager/`. Detects and reconciles drift between the **Codex** and **Claude Code** *global* harnesses — behavioral rules (`~/.claude/CLAUDE.md` ↔ `~/.codex/AGENTS.md`), MCP servers (`~/.claude.json` ↔ `~/.codex/config.toml`), commands ↔ prompts, and skills. Runs scan → drift report (HTML) → user approval → backed-up edits, with a six-bucket drift classification (in-sync / delegated / diverged / missing / broken-port / tool-specific). Phases 1–3 are read-only; Phase 4 mutates real files only after the user approves specific items and after backing every target up to `~/.claude/backups/`. References: `harness-map.md` (exact paths and per-tool gotchas) and `sync-recipes.md` (JSON↔TOML MCP translation, pointer-pattern rule propagation).

#### Notes
- Bumped the `elian-store` plugin version (`2.9.0` → `2.10.0`). The marketplace metadata version is intentionally left at `2.8.2` because the catalog structure (the set of plugins) did not change — only the plugin's contents did.
- `harness-manager` ships Claude-only for now; its Codex prompt counterpart is a documented parity exception in `docs/claude-codex-skill-parity.md` (it is a meta-tool operating on both harnesses' global files, so a Codex port is a reasonable future addition rather than a behavioral mirror).

### 2.9.0 — 2026-06-08

#### Added
- **`/document-writer`** — new skill at `plugins/elian-store/skills/document-writer/`. Turns arbitrary content (analysis, reports, technical/design docs, guides) into a self-contained, house-styled HTML document (Markdown when asked). Content is authored as Markdown and rendered by a stdlib-only converter (`scripts/build_doc.py` — zero dependencies, raw block-level HTML passthrough, GitHub-style callouts, auto TOC, `--selftest`) with a fixed house stylesheet (`assets/house-style.css`) so every document shares one consistent look: warm off-white background, ink body text, a single `#185FA5` accent, Pretendard. References: `components.md` (callout / card / KPI / steps / badge / table catalog) and `doc-types.md` (report / technical / guide blueprints). Defaults output to `claudedocs/`.

#### Notes
- Bumped the `elian-store` plugin version (`2.8.2` → `2.9.0`). The marketplace metadata version is intentionally left at `2.8.2` because the catalog structure (the set of plugins) did not change — only the plugin's contents did.

### 2.8.2 — 2026-06-02

#### Changed
- Standardized plugin-distributed skill documents, references, templates, Codex companion prompt, and persona agent instructions in English.
- Rewrote high-detail skill documents into leaner workflow contracts with supporting references/templates.
- Updated `/persona-review` validation markers to the English free-form, no-scorecard contract.
- Updated decision-dashboard and teammate-spawn examples/schemas/templates to English-only content.
- Marketplace + plugin metadata bumped to `2.8.2` because plugin-distributed skill documents and templates changed.

#### Removed
- Removed the legacy `create-document` persona review output renderer: `review-output.md`, `review-output.schema.json`, and `example-review-output.json`.

#### Fixed
- Fixed broken example links in the `technical-writer` agent documentation by making them example paths instead of repository-local links.

### 2.8.1 — 2026-06-02

### Removed
- Removed the repository-wide numeric score gate: `scripts/score_skill.py`, `scripts/score_codex_prompt.py`, their rubric docs, and the GitHub Actions workflows that enforced them.
- Removed `plugins/elian-store/skills/generate-teammate/scripts/validate_skill.py`; `/generate-teammate` now documents manual validation checks instead of shipping that validator.

### Changed
- Validation guidance now centers on YAML/frontmatter smoke tests, skill-owned validators, artifact checks, purpose review, and Claude/Codex parity review.
- Marketplace + plugin metadata bumped to `2.8.1` because plugin-distributed validation docs changed.
- Active operating docs now use English as the documentation language.

### 2.8.0 — 2026-06-02

#### Added
- **`/review`** — read-only engineering review skill at `plugins/elian-store/skills/review/`. Reviews worktree/staged/branch/PR/path targets, leads with severity-ordered findings, cites file/line evidence, names test/verification gaps, and hands off fixes/QA/ship instead of editing code.
- **`/review` self-validator** — stdlib-only `scripts/validate_skill.py` with `--json` and `--quiet`, checking read-only boundaries, required sections, reference links, and the findings-first contract.
- **Review findings reference** — `references/example-findings.md` with BEFORE/AFTER examples, severity examples, and no-findings output guidance.

#### Changed
- **Marketplace + plugin metadata** bumped to `2.8.0` for the new bundled skill.
- **README skill inventory** now includes `/review` and updates the lifecycle gap note so engineering review is no longer listed as missing.

#### Notes
- `/review` intentionally does not replace `/persona-review`, `/verify-implementation`, `/browser-qa`, or `/ship`. It fills the engineering findings gap between implementation/fix/improve and verification/release readiness.

### 2.7.3 — 2026-05-29

#### Changed
- **gstack-based portfolio review**: added `docs/gstack-skill-review.md` to compare the current bundle against `garrytan/gstack` lifecycle patterns and identify gaps across review, browser QA, release, canary, benchmark, security, and learning workflows.
- **README roadmap note**: linked the gstack review and clarified that the current bundle is structurally healthy but not yet lifecycle-complete.
- **Claude/Codex parity docs** now distinguish Codex CLI prompt/config parity from a non-existent Codex plugin marketplace model and list the gstack-derived roadmap gaps.
- **Rubric and CONTRIBUTING** now include a non-blocking portfolio review checklist for lifecycle coverage beyond the 90-point per-skill gate.
- **Marketplace + plugin metadata** bumped to `2.7.3` because plugin-distributed documentation changed.

#### Notes
- No skill runtime behavior changed. This release documents portfolio-level gaps and follow-up PR order; it does not add new skills.

### 2.7.2 — 2026-05-29

#### Fixed
- **Claude skill YAML frontmatter**: quoted YAML-unsafe `description`, `when_to_use`, and `argument-hint` values so Claude/GitHub parsers no longer fail on `: `, quotes, or bracket-style argument hints.
- **Skill quality gate**: `scripts/score_skill.py` now unwraps quoted scalar values and fails PRs with blocking issues when frontmatter contains YAML-unsafe plain scalars.
- **README Codex setup**: top-level README now shows the full `/persona-review` Codex argument contract and the legacy `~/.codex/prompts/on-call-elian.md` cleanup command.
- **Docs-only PR checks**: Skill Quality Gate now runs for README, CHANGELOG, CONTRIBUTING, and docs changes so branch protection does not leave required checks missing.

#### Notes
- This is a hotfix for the `2.7.1` documentation alignment release. No Claude skill workflow behavior changed.
- All 12 bundled skills now pass both the local 90-point gate and an actual YAML frontmatter parse smoke test.

### 2.7.1 — 2026-05-28

#### Changed
- **Claude skill/plugin documentation alignment**: added `docs/claude-skill-plugin-audit.md` comparing this repository against current Claude Code skill/plugin docs and `alirezarezvani/claude-skills`.
- **Claude/Codex parity review**: added `docs/claude-codex-skill-parity.md` to define what "same catalog" means, identify the current 12-vs-1 parity gap, and assess whether each skill matches its purpose.
- **Marketplace + plugin metadata** shortened for discovery surfaces. `plugin.json.version` and marketplace entry bumped together because plugin-distributed docs changed.
- **README skill inventory** now matches all 12 bundled skills under `plugins/elian-store/skills/`.
- **Codex prompt rename**: `codex/prompts/on-call-elian.md` is now `codex/prompts/persona-review.md`, so the independent Codex command matches the Claude plugin skill name.
- **CONTRIBUTING** now documents the current skill/plugin operating rules: official Claude Code docs as compatibility baseline, `alirezarezvani/claude-skills` as operating-pattern reference, 1,536-character listing cap, side-effect auto-invocation policy, plugin-root component layout, and version bump rule.
- **Skill frontmatter cleanup** for `/ai-assisted-feature-development`, `/create-document`, `/design-ui`, and `/persona-review`; high-detail procedure text moved out of discovery metadata.
- **`/persona-review`** now has an explicit `Modes` section for `quick`, `deep`, and `interview`.
- **Rubric wording** updated to explain the optional-frontmatter source-priority rule instead of treating external conventions as uniformly authoritative.

#### Notes
- No Claude plugin workflow behavior changed. The independent Codex prompt command changed from `/on-call-elian` to `/persona-review`; existing Codex users should remove `~/.codex/prompts/on-call-elian.md` during reinstall so the stale slash command does not remain available.
- All bundled skills still pass the local 90-point `score_skill.py` gate.

### 2.7.0 — 2026-05-23

#### BREAKING — `/on-call-elian` renamed to `/persona-review`

User feedback flagged that `on-call-elian` is too company-specific for a persona-library skill, and that the default persona's `Identity` section (healthcare/Vue 3/Java/Kubernetes) is environment metadata, not persona essence. The 8 pressure questions are the essence — environment-agnostic. This release reshapes the skill around a **persona library** with multiple thinkers' lenses, not a single fixed Daniel persona.

Migration:
- Slash command `/on-call-elian` → `/persona-review`
- Skill directory `plugins/elian-store/skills/on-call-elian/` → `plugins/elian-store/skills/persona-review/`
- Env var `${ON_CALL_ELIAN_DEFAULT}` → `${PERSONA_REVIEW_DEFAULT}`
- Env var `${ON_CALL_ELIAN_DEPTH}` → `${PERSONA_REVIEW_DEPTH}`
- Persona file `references/persona-daniel.md` → `references/personas/daniel.md`
- Trigger phrases: replace `'/on-call-elian'` with `'/persona-review'`; add persona-specific English phrases such as `'Evans domain review'`, `'Dean scale review'`, and `'Martin clean-code review'`.

#### Added
- **`/ai-assisted-feature-development`** — disciplined 9-phase feature-development methodology skill at `plugins/elian-store/skills/ai-assisted-feature-development/`. Phases: Feature Framing -> BDD -> SDD -> DDD (when needed) -> AI-TDD -> Context Engineering -> Agentic Coding -> Review -> SPDD Archive. Modes: `full` (all 9), `design-only` (1-5), `task-only` (6-7), `review-only` (8). Risk-gated depth (LOW/MEDIUM/HIGH). 8 references: master-prompt, stage-prompts (9 per-phase prompts), login-example, other-feature-examples (file-upload / order-cancel / post-create / search / notification / permissions / signup), artifact-structure, definition-of-done (11 DoD items + 10 merge-block conditions), anti-patterns (10 vibe-coding anti-patterns), quick-start. Applies to any feature — login is one example, not the scope.
- **`/persona-review`** — persona library skill at `plugins/elian-store/skills/persona-review/`. Default `daniel` (operational mindset). Library: `daniel.md`, `evans.md` (DDD), `dean.md` (distributed-scale), `martin.md` (Clean Code/SOLID/TDD). All four follow the same 7-section structure (Voice / Hard Rules / Decision Heuristics / Priorities / Forbidden / Pressure Questions / Blind Spots). Identity section is now **optional** (only when domain/stack genuinely changes the pressure axis).
- **Persona matching guide** in SKILL.md: which situation → which persona. Phase 0 of the workflow recommends a persona based on the target file path / diff pattern.
- **Custom persona authoring guide** simplified — 7 required sections, Identity demoted to optional with explicit "environment metadata such as Vue developer or healthcare domain is not persona essence" guidance.

#### Changed
- `validate_skill.py`: recognizes both `references/personas/*.md` (new layout) and `references/persona-*.md` (legacy) so persona files can live either way. 5-block contract check accepts Korean + English header variants.
- All 11 skills + 1 new (persona-review) pass `score_skill.py` 90+ gate.

#### Removed
- `references/persona-daniel.md` (moved into `references/personas/daniel.md` with Identity section stripped)
- `${ON_CALL_ELIAN_*}` env var names

#### Notes
- The `codex/prompts/on-call-elian.md` Codex port still uses the legacy name; it is on a separate lifecycle and will be reconciled in a follow-up.
- `example-review.md` examples remain Korean-flavored (mobidoc-context). Persona-specific examples for evans/dean/martin are future work.
- The default `daniel` persona's Identity section was removed in v2.6.0 + #11; persona body is now domain-agnostic.

---

### 2.6.0 — 2026-05-22

#### Added
- **`/create-document`** — new skill at `plugins/elian-store/skills/create-document/`. JSON content → schema validation → HTML/MD template substitution engine. stdlib-only. Schema-level `forbid` patterns block identifier leakage (`#143`, `*.class`, `*Entity`, snake_case columns) before any output is written. Supports `{{key}}`, `{{{key}}}` (raw), `{{.}}` / `{{_}}` (primitive element in FOREACH), and nested `<!-- FOREACH key --> ... <!-- END -->` blocks.
- **`teammate-spawn` schema + template** under `create-document/schemas/` and `create-document/templates/`. Enforces 7 required slots (ROLE / OWNED FILES / TECH STACK / TASK / REFERENCE DOCS / INTERFACES / DEFINITION OF DONE / COMMUNICATION) with bilingual `mustMatch` (en/ko action verbs) and vague-language `forbid` (`help build`, `do something`, `TODO`, `...`).
- **`/design-ui` scripts/validate_skill.py** — self-validation: frontmatter, 5 Phases, templates, references, override mechanism.

#### Changed
- **`/decision-dashboard`** SKILL.md rewritten: sed+Edit handwritten HTML blocks → JSON authoring + `create-document` call. `template.html` moved to `create-document/templates/decision-dashboard.html`. Card body identifiers (`#N`, `*.class`, `*Entity`) now blocked structurally by the schema.
- **`/generate-teammate`** spawn prompts: hand-written 7-slot template → JSON-first authoring rendered via `create-document --template teammate-spawn`. SKILL.md sections (Standing Rules / Forbidden / Pitfall / Error Handling / BEFORE-AFTER) split into `references/{standing-rules,known-issues,before-after-patterns}.md`; SKILL.md keeps headlines + links.
- **`/on-call-elian`** frontmatter description: Korean tokens inside English sentences translated to English for consistency. (Conclusion / Trade-offs / Operational risks / 8 pressure questions / Next question.) Korean user-utterance triggers in `when_to_use` preserved.
- **`/design-ui`** SKILL.md: `$ARGUMENTS` + `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` / `${DESIGN_UI_OUT}` env overrides documented; templates/references/scripts now use Markdown links; "Failure modes" renamed to "Pitfall / Failure modes"; Pre-flight checklist added. Score 76 → 98.
- **All 11 skills** frontmatter `description` / `when_to_use` / `argument-hint`: quoted → unquoted (consistency + `score_skill.py` axis2 alignment).

#### Removed
- `plugins/elian-store/skills/decision-dashboard/template.html` — canonical version moved to `create-document/templates/decision-dashboard.html`.

#### Notes
- All 11 skills pass `score_skill.py` 90-point gate (range 92–100).
- `create-document` is dual-use: callable directly by users or by other skills (currently `decision-dashboard` and `generate-teammate`).
- `design-ui` shipped without version bump in 2.5.x — first release in this changelog at 2.6.0.

---

### Repo infra — Codex CLI config tree — 2026-05-19 (no plugin version bump)

Not a plugin release. `codex/` is a sibling distributable tree, independent of the `elian-store` Claude plugin, so `plugin.json`/`marketplace.json` versions are unchanged.

#### Added
- **`codex/` independent config tree** (decision: independent 2-tree, no shared source — trade-off accepted in an `/on-call-elian` review):
  - `codex/prompts/on-call-elian.md` — Codex-native port of `/on-call-elian` (reference; `AskUserQuestion` steps → ask-and-wait, no frontmatter, `$ARGUMENTS`).
  - `codex/AGENTS.md` — Daniel standing-rules project-instruction template.
  - `codex/config.toml.example` — `~/.codex/config.toml` sample (read-only-review-safe defaults).
  - `codex/README.md` — identity, install, explicit drift warning.
- **Independent Codex quality gate**: `scripts/score_codex_prompt.py` + `scripts/rubric-codex.md` (8 axes, stdlib-only, 90 gate; axes 1/2/5 = 5-block order + Phase consistency + counterpart cross-ref to catch tree-level drift). Reference scores 100/100.
- **CI**: `.github/workflows/codex-config-gate.yml` (path-filtered to `codex/prompts/**`, mirrors the skill gate).

#### Changed
- `.gitignore`: Codex per-developer state (`.codex/`, `codex/config.toml`) + gate artifacts.
- `CONTRIBUTING.md`: new "Claude vs Codex — where to edit" section + directory tree; `README.md`: Codex CLI section.

#### Notes
- **No single source of truth.** `codex/prompts/on-call-elian.md` and `plugins/elian-store/skills/on-call-elian/SKILL.md` are separate files; cross-tree sync is a manual PR-author responsibility. This is the intentional cost of the independent-tree model.
- Port scope: `on-call-elian` only (reference). Other skills deferred until the pattern proves out.

---

### [2.5.0] — 2026-05-15

#### Added
- **`/on-call-elian` — `--depth interview` mode** (new option, MINOR):
  - **Phase 4.5 convergence loop**: instead of a one-shot 5-block review, picks the 1–2 weakest points (pressure question failure > partial concern > context-dependent branch variable), re-interviews via `AskUserQuestion`, and re-emits the full 5 blocks. Terminates when the conclusion becomes firm, no blocking concern remains, the user stops, or the **3-round hard cap** is reached. Round counter shown as `(interview R{n}/3)`.
  - **Phase 5 handoff payload**: once converged, emits a ready-to-run `/improve` invocation + context block (conclusion / selected option / residual risk / in-out scope). **Emit-only** — on-call-elian never calls `/improve` itself, preserving the read-only axiom.
- `references/example-review.md`: Example 3 (interview 1-round → converge → handoff).

#### Changed
- `argument-hint`, `--depth` table, `${ON_CALL_ELIAN_DEPTH}` enum now include `interview`.
- Workflow diagram, "automated vs taste" table, Forbidden, Pitfalls, Pre-flight checklist extended with interview/handoff guards (3R cap, emit-only, ≤2 questions/round).
- Marketplace + plugin descriptions mention the convergence loop.

#### Notes
- 5-block OUTPUT FORMAT contract unchanged — interview *repeats* the blocks, never alters the format. `quick`/`deep` behavior unchanged (default still `quick`).
- Self-validator (`scripts/validate_skill.py`): unchanged, still passes (5-block order intact).

---

### [2.4.0] — 2026-05-15

#### Added
- **New skill** in `elian-store`:
  - `/on-call-elian` — Review a plan/design/document through a fixed persona lens (default `daniel`) with a **locked 5-block OUTPUT FORMAT** (conclusion -> trade-off table -> operational risks -> 8 pressure questions -> next question). Read-only. Pairs with `/brainstorm` as the divergent-input step followed by convergence pressure. Persona body in `references/persona-daniel.md`; custom personas via `--persona <path>` or `${ON_CALL_ELIAN_DEFAULT}`. Self-contained, gate 98/100.

#### Changed
- Marketplace and plugin descriptions updated to mention `/on-call-elian`.

#### Notes
- Persona built from repo SKILL.md/hooks/agents patterns + user CLAUDE.md + general-conversation behavior cases + Claude/GPT persona analysis.
- Self-validator (`scripts/validate_skill.py`): argparse + `--json` + `--quiet`, verifies the 5-block contract order.

---

### [2.3.0] — 2026-04-29

#### Added
- **Two new skills** in `elian-store`:
  - `/manage-skills` — Auto-detect verify-skill drift after code changes and create or update verify-* skills so the project's verification stays current. Pairs with `/verify-implementation`. Self-contained, English, gate 97/100.
  - `/verify-implementation` — Discover and run all verify-* skills in the current project, surface failures with concrete fix suggestions, and (with approval) auto-apply fixes + re-verify. One command instead of remembering which verify-* to run for which change. Self-contained, English, gate 97/100.

#### Changed
- Marketplace and plugin descriptions updated to mention the skill-meta pair.

#### Notes
- Both skills are self-contained (no external skill dependencies).
- Self-validators (each skill's `scripts/check-*.py`): argparse + `--json`.

---

### [2.2.0] — 2026-04-29

#### Added
- **Four new skills** in `elian-store`:
  - `/implement` — TDD-driven feature implementation. Workflow: project recognition → context gathering → plan + conflict matrix → approval gate → Red→Green→Refactor (parallel where safe) → integration verification → code review → completion report. Self-contained, English, gate 96/100.
  - `/fix` — Root-cause-first bug repair. Workflow: bug analysis → repair plan → approval gate → TDD repair (regression test first) → side-effect verification → review → report. Self-contained, English, gate 92/100.
  - `/improve` — Behavior-changing improvement to working features. Workflow: BEFORE snapshot → improvement plan → approval gate → TDD improvement protecting existing tests → quantified BEFORE/AFTER verification → review → report. Includes Characterization Test guidance. Gate 94/100.
  - `/brainstorm` — Conversational discovery for fuzzy requests. Workflow: context recognition → Socratic requirements probing → 3+ option drafting → tradeoff comparison → decision gate → handoff with persistent plan artifact. Gate 91/100.
- Each new skill ships with `references/templates.md` and `scripts/validate_skill.py` (stdlib only, argparse + `--json`).

#### Changed
- **All in-plugin documentation unified to English.** Every SKILL.md, references file, agent definition, and accompanying doc inside `plugins/elian-store/` now uses English. Marketplace metadata, README, CHANGELOG, PR template, and workflow comments aligned to the same language policy.
- `marketplace.json` and `plugin.json` descriptions updated to reflect the new skill catalog.
- `plugin.json` keywords now include `tdd` and `brainstorm`.

#### Notes
- The new skills depend on `plugins/elian-store/skills/_shared/execution-strategy.md` shipped with this plugin (no external dependency). Self-validators in each skill's `scripts/` confirm structural correctness.

---

### [2.1.0] — 2026-04-29

#### Added
- **`/generate-teammate` skill** — Decompose work into phases, judge each phase independently (Agent Team / Subagent / direct), produce a hybrid execution plan. Phase decomposition → fit scoring (★ Fit / Possible / Unfit) → strategy selection → team / task design → user confirmation → execution. Built around the official-doc primary question: "Do workers need to communicate with each other?"
- **14 plugin-bundled domain agents** in `plugins/elian-store/agents/`, all self-contained (zero external skill deps):
  - Engineering (8): `frontend-architect` (React / Vue / Angular / Svelte / Solid framework-agnostic), `backend-architect` (Spring Boot / Express / NestJS / Django / FastAPI / Rails / Go / .NET multi-stack), `system-architect` (ADR + domain modeling), `security-engineer` (OWASP + AI / cloud), `performance-engineer` (measurement-first), `quality-engineer` (test pyramid), `devops-architect` (Docker / K8s / Terraform / CI / CD), `requirements-analyst` (PRD + acceptance criteria).
  - Design / research / strategy (6): `ui-ux-designer` (design tokens + components + a11y), `technical-writer` (Diátaxis), `ux-researcher` (interviews + personas + journey maps), `marketing-strategist` (positioning + GTM), `business-analyst` (unit economics + ROI + decision frameworks), `devil-advocate` (pre-mortems + assumption excavation + ethical lens).
- **`references/` directory** — End-to-end traces of 4 scenarios (fullstack feature, competing-hypothesis debugging, multi-lens PR review, non-engineering launch strategy).
- **Documentation Team / Strategy Team patterns** — Design Team expanded with technical and UX variants. Catalog evolved from a single-domain focus to full-domain coverage.
- All in-skill documentation unified to English (multinational marketplace audience).

#### Changed
- Marketplace / plugin descriptions updated to reflect the new skill + agent catalog.
- `plugin.json` keywords now include `agent-team` and `subagent`.

#### Notes
- Agent Teams is an experimental feature. Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `settings.json` or environment before use. Requires Claude Code v2.1.32 or later.
- The 14 agents do not use the `skills:` frontmatter — they work standalone with this plugin.

---

### [2.0.1] — 2026-04-28

#### Fixed
- **Skill Quality Gate detection leak** — The previous workflow's `git diff --diff-filter=AM` missed git renames (R), causing PRs that moved SKILL.md to be detected as "0 changed SKILL.md" and have evaluation / comment skipped (PR #3 case). Adding `--no-renames` decomposes a rename into add+delete so the new path is captured as `A`. Future path-and-content combined changes will now flow through the gate normally.

---

### [2.0.0] — 2026-04-28 ⚠ BREAKING

#### Changed (BREAKING for users)
- **Switched to a single bundled-plugin model** — The previous standalone `decision-dashboard` plugin became a skill inside the new `elian-store` bundle plugin. One install gives you many skills, and new skills land via `/plugin update elian-store@elian`.
- Migration:
  ```shell
  /plugin uninstall decision-dashboard@elian
  /plugin install elian-store@elian
  ```
- Invocation format change: `/decision-dashboard:decision-dashboard` → `/elian-store:decision-dashboard` (natural-language invocation "make a decision dashboard" is unchanged).
- The `decision-dashboard` skill content itself didn't change — only its location moved to `plugins/elian-store/skills/decision-dashboard/`.

#### Migration rationale

The old shape (one plugin per skill) required a separate `plugin.json`, marketplace entry, and per-user install for every new skill. Bundling fixes this:

- For users: one install → all skills automatically.
- For maintainers: a new skill is just a directory + `plugin.json` version bump.

Planned follow-up skills: `manage-skills`, `brainstorm`, `commit`, etc.

---

### [1.2.0] — 2026-04-28

#### Changed (BREAKING for maintainers)
- **Migrated Skill Quality Gate from LLM-based scoring to a stdlib heuristic.** No more `ANTHROPIC_API_KEY` secret to set up. Scoring is deterministic, free, and depends on nothing external.
- Scoring signals are deterministic pattern matching (section presence, length, keywords, directory structure). Semantic quality (writing fluency) isn't evaluated, but well-built skills usually have the structure to clear a 90-point gate.
- Self-validation: pre-improvement SKILL.md = 54 (FAIL), post-improvement = 97 (PASS). The gate behaves as intended.

#### Added
- `scripts/score_skill.py` — Python-stdlib heuristic scorer. argparse, `--help`, `--json`. Scores multiple SKILL.md files in one run.

#### Removed
- `scripts/evaluate_skill.py` — the Anthropic-SDK-based LLM evaluator (replaced by the heuristic).
- `scripts/static_checks.sh` — `score_skill.py` absorbed the static checks.
- `ANTHROPIC_API_KEY` secret dependency — removed from workflow, README, and PR template.

#### Future LLM augmentation (optional, unimplemented)
- A hybrid model could call an LLM only for the 80–89 heuristic range — saves cost while still capturing semantic quality. Out of scope for this PR.

---

### [1.1.0] — 2026-04-28

#### Added
- **PR-based workflow + Skill Quality Gate** — Every SKILL.md change must pass a PR before reaching `main`. GitHub Actions runs the gate automatically and blocks merge below 90.
- `scripts/rubric.md` — 100-point evaluation rubric synthesizing the official Claude Code guide + [garrytan/gstack](https://github.com/garrytan/gstack/blob/main/docs/skills.md) + [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) best practices.
- `.github/workflows/skill-quality-gate.yml` — PR trigger, evaluates only changed SKILL.md, posts results as a PR comment.
- `.github/pull_request_template.md` — Change-type / checklist standardization.
- A Contributing section in `README.md`.

### [1.0.0] — 2026-04-28

#### Added
- Registered `decision-dashboard` plugin v1.0.0.
- Marketplace metadata (`metadata.pluginRoot = ./plugins`).

---

## elian-store (bundle)

### [2.2.0] — 2026-04-29

See marketplace 2.2.0 notes above.

### [2.1.0] — 2026-04-29

See marketplace 2.1.0 notes above.

### [2.0.0] — 2026-04-28 ⚠ BREAKING

#### Changed
- New bundled plugin — absorbed the `decision-dashboard` plugin (v1.0.0) as its first skill.
- Future skills land just by adding `plugins/elian-store/skills/<name>/` (no separate user install).

#### Migration from decision-dashboard@1.0.0
- `/plugin uninstall decision-dashboard@elian` → `/plugin install elian-store@elian`
- Invocation: `/decision-dashboard:decision-dashboard` → `/elian-store:decision-dashboard`

---

## decision-dashboard (legacy plugin, 1.0.0 only — superseded by elian-store@2.0.0)

### [1.0.0] — 2026-04-28

First public release. Packaged the personal `~/.claude/skills/decision-dashboard/` as a plugin and applied marketplace-distribution-ready best practices from [garrytan/gstack](https://github.com/garrytan/gstack/blob/main/docs/skills.md) + [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills).

#### Added — core
- Single-HTML decision dashboard generator (radio choice + notes + MD/JSON download + JSON clipboard copy).
- Priority colors (P0/P1/P2) + sidebar card navigation.
- Card-body LANGUAGE GATE — class names, table names, internal acronyms are filtered out (developer rationale lives in a collapsible details panel).
- "Other — custom input" option standardized as the last option on every card.

#### Added — best-practice adoption (gstack + alirezarezvani)
- **Outcome-focused description** — "When 3+ pending decisions block PO/team progress, capture them in a printable HTML artifact so the team can decide in 5 minutes" (outcome over process). gstack: *"Lead with the concrete problem the skill solves, not aspirational framing."*
- **Mode differentiation** — `generate` (first creation) vs `finalize` (persist decisions + clean up). Borrows gstack's `/plan-ceo-review` 4-mode pattern.
- **Skill sequencing** — "Where this fits in the workflow" section: `brainstorm → design → DECISION-DASHBOARD → implement → review → ship`.
- **Manual decision gating** — "What's automated vs what needs your taste" table. Claude decides priority classification, label conversion, GATE filtering; user decides A/B/C, option definitions.
- **Persistent artifact for downstream** — `decisions-final.json` (issue, decisions[], summary, rejected_alternatives). Consumed as context by downstream skills (`/implement`, `/ship`).
- **End-of-skill reflection** — at finalize, observe decision patterns (3 items, hedged language). gstack: *"specific callbacks, not generic praise"*.
- **Three-file minimum** — `references/` directory:
  - `references/example-good-card.md` — BEFORE / AFTER card comparison + self-checklist.
  - `references/example-card-snippet.html` — A single good-card HTML fragment (copy-paste).
- **`scripts/validate-dashboard.py`** — pulled inline bash validation into a Python script. argparse-based `--help` + `--json` output (chainable with other skills). stdlib only (zero pip installs). alirezarezvani's *"All CLI tools tested with --help and --json flag support"* standard.
- **`argument-hint`** carries the second / third arguments (output-dir, mode).
- **`${CLAUDE_SKILL_DIR}`** used (the skill's own path, not the plugin root).
- **Standing Instructions section isolated** — card-writing rules (LANGUAGE GATE, 3-sentence background, option labels, guiding question) separated from per-mode procedures and surfaced as standing instructions.

#### Changed (vs personal version)
- **Output path generalized** — default `claudedocs/{ISSUE}/decisions-{DATE}.html`. Override with `DECISIONS_DIR` env var or `$ARGUMENTS[2]`.
- **Issue ID auto-extraction** — `git branch --show-current` matched against `[A-Z]+-[0-9]+` (vendor-neutral company-issue prefix detection).

#### Fixed (vs personal version)
- **Auto-validation shell-variable bug** — the prior `FILE=claudedocs/{ISSUE}/...` used a placeholder where a shell variable belonged, so validation always broke → replaced with a real shell variable + a separate Python script.
- **Python-heredoc variable non-substitution** — inside `<<'EOF'` (quoted heredoc), `$FILE` was empty, so the LANGUAGE GATE always failed → resolved by extracting to a separate script with argparse.

#### Removed (vs personal version)
- **Removed the entire PENDING.md archival flow** — coupled to a personal workflow (claudedocs/{ISSUE}/PENDING.md 6-block decision cards), not appropriate for general distribution. Decision rationale is preserved via `decisions-final.json` + commit messages instead.
- mobidoc-project-specific examples (MPT-####, ShedLock refund scenario, etc.) — replaced with generic ones (PROJ-123, push-notification re-send scenario).

---

## Versioning policy

- **Always bump the `version` field on changes.** If `plugin.json`'s `version` stays the same, Claude Code uses the cached copy and updates never reach users.
- Catalog-only changes → bump only `marketplace.json`'s `metadata.version`.
- Plugin-content changes → bump the plugin's `plugin.json.version` and the marketplace entry's `version` together (per the [official doc](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels), `plugin.json` wins on conflict — managing one source of truth is safer).

### SemVer guide

| Change type | Example | Bump |
|-------------|---------|------|
| MAJOR (breaking) | placeholder name change, default output-dir change, allowed-tools narrowing | `1.0.0 → 2.0.0` |
| MINOR (feature) | new validation rule, new option, new card type | `1.0.0 → 1.1.0` |
| PATCH (fix/docs) | bug fix, documentation polish, examples added | `1.0.0 → 1.0.1` |
