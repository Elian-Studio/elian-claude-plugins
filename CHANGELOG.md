# Changelog

This file records significant changes for every plugin in this marketplace.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the version scheme follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> The marketplace itself and each plugin keep **independent versions**. The marketplace version tracks catalog-structure changes (adding / removing plugins, metadata). Plugin versions track functional changes inside that plugin.

---

## Marketplace (`elian`)

### 2.7.0 — 2026-05-23

#### BREAKING — `/on-call-elian` renamed to `/persona-review`

User feedback flagged that `on-call-elian` is too company-specific for a persona-library skill, and that the default persona's `Identity` section (의료/Vue3/Java/Kubernetes) is environment metadata, not persona essence. The 8 pressure questions are the essence — environment-agnostic. This release reshapes the skill around a **persona library** with multiple thinkers' lenses, not a single fixed Daniel persona.

Migration:
- Slash command `/on-call-elian` → `/persona-review`
- Skill directory `plugins/elian-store/skills/on-call-elian/` → `plugins/elian-store/skills/persona-review/`
- Env var `${ON_CALL_ELIAN_DEFAULT}` → `${PERSONA_REVIEW_DEFAULT}`
- Env var `${ON_CALL_ELIAN_DEPTH}` → `${PERSONA_REVIEW_DEPTH}`
- Persona file `references/persona-daniel.md` → `references/personas/daniel.md`
- Trigger phrases: replace `'/on-call-elian'` with `'/persona-review'`; add persona-specific phrases like `'에반스로 도메인 점검'`, `'딘 시각으로 스케일 압박'`, `'마틴으로 클린코드 점검'`

#### Added
- **`/ai-assisted-feature-development`** — disciplined 9-phase feature-development methodology skill at `plugins/elian-store/skills/ai-assisted-feature-development/`. Phases: Feature Framing → BDD → SDD → DDD (필요 시) → AI-TDD → Context Engineering → Agentic Coding → Review → SPDD Archive. Modes: `full` (all 9), `design-only` (1-5), `task-only` (6-7), `review-only` (8). Risk-gated depth (LOW/MEDIUM/HIGH). 8 references: master-prompt, stage-prompts (9 per-phase prompts), login-example, other-feature-examples (file-upload / order-cancel / post-create / search / notification / permissions / signup), artifact-structure, definition-of-done (11 DoD items + 10 merge-block conditions), anti-patterns (10 vibe-coding anti-patterns), quick-start. Applies to any feature — login is one example, not the scope.
- **`/persona-review`** — persona library skill at `plugins/elian-store/skills/persona-review/`. Default `daniel` (operational mindset). Library: `daniel.md`, `evans.md` (DDD), `dean.md` (distributed-scale), `martin.md` (Clean Code/SOLID/TDD). All four follow the same 7-section structure (Voice / Hard Rules / Decision Heuristics / Priorities / Forbidden / Pressure Questions / Blind Spots). Identity section is now **optional** (only when domain/stack genuinely changes the pressure axis).
- **Persona matching guide** in SKILL.md: which situation → which persona. Phase 0 of the workflow recommends a persona based on the target file path / diff pattern.
- **Custom persona authoring guide** simplified — 7 required sections, Identity demoted to optional with explicit "Vue 개발자·의료 도메인 같은 환경 정보는 페르소나가 아니다" guidance.

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
- `CONTRIBUTING.md`: new "Claude vs Codex — 어디를 수정하나" section + directory tree; `README.md`: Codex CLI section.

#### Notes
- **No single source of truth.** `codex/prompts/on-call-elian.md` and `plugins/elian-store/skills/on-call-elian/SKILL.md` are separate files; cross-tree sync is a manual PR-author responsibility. This is the intentional cost of the independent-tree model.
- Port scope: `on-call-elian` only (reference). Other skills deferred until the pattern proves out.

---

### [2.5.0] — 2026-05-15

#### Added
- **`/on-call-elian` — `--depth interview` mode** (new option, MINOR):
  - **Phase 4.5 convergence loop**: instead of a one-shot 5-block review, picks the 1–2 weakest points (압박 질문 `✗` > `△` > "상황에 따라 다름" branch var), re-interviews via `AskUserQuestion`, and re-emits the full 5 blocks. Terminates on any of: 결론 becomes 단정 / no `✗` left / user stops / **3-round hard cap** (infinite-loop guard). Round counter shown as `(interview R{n}/3)`.
  - **Phase 5 handoff payload**: once converged, emits a ready-to-run `/improve` invocation + context block (결론 / 채택 옵션 / 잔여 리스크 / In·Out). **Emit-only** — on-call-elian never calls `/improve` itself, preserving the read-only axiom.
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
  - `/on-call-elian` — Review a plan/design/document through a fixed persona lens (default `daniel`) with a **locked 5-block OUTPUT FORMAT** (결론 → 트레이드오프 표 → 운영 리스크 → 8가지 압박 질문 → 다음 질문). Read-only. Pairs with `/brainstorm` (발산) as the 수렴 압박 step. Persona body in `references/persona-daniel.md`; custom personas via `--persona <path>` or `${ON_CALL_ELIAN_DEFAULT}`. Self-contained, gate 98/100.

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
