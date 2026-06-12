# Changelog

This file records significant changes for every plugin in this marketplace.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the version scheme follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> The marketplace itself and each plugin keep **independent versions**. The marketplace version tracks catalog-structure changes (adding / removing plugins, metadata). Plugin versions track functional changes inside that plugin.

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
