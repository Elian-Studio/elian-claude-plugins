# Repository-wide AI Skills and Plugins Audit

Date: 2026-07-23  
Scope: repository definitions only  
Baseline: `main` before the v3.1.1 hardening changes  
Post-change state: `refactor/repository-audit-safety-baseline`

This audit intentionally excludes local installation state, MCP connectivity,
credentials, environment variables, host registrations, and whether a command
can run on this machine. Findings are based on the repository's definitions,
implementation files, references, templates, scripts, manifests, and tests.

## A. Executive Summary

The repository has a useful product shape: one installable Claude plugin, 26
explicitly named skills, two Codex prompt adapters, 14 shared Codex skill
symlinks, bundled deterministic renderers, and a cluster manifest that can build
five thematic distribution bundles. The strongest parts are the narrow TDD
entry points (`implement`, `fix`, `improve`), the evidence-oriented verification
lane, asset-backed document generation, and the explicit Claude/Codex parity
record.

The baseline was not safe enough to scale. Repository behavior depended on
prose conventions that were not mechanically checked. Side-effect skills could
be selected automatically, one dashboard skill exposed wildcard deletion,
"read-only" reviewers had Bash access, core flows assumed optional host skills,
and the Codex manifest did not distinguish runtime blockers from intentionally
deferred ports. There was no repository CI to stop these conditions from
returning.

The five most serious baseline problems were:

1. **Critical — unsafe automatic side effects:** artifact and design skills
   that write files did not consistently set `disable-model-invocation: true`;
   `decision-dashboard` also exposed `Bash(rm claudedocs/*)`.
2. **High — read-only enforcement existed only in prose:** all persona reviewer
   agents exposed Bash, and engineering review reused broad domain agents whose
   capabilities were not read-only.
3. **High — core workflows assumed unbundled commands:** TDD and design flows
   could require `/commit`, `/simplify`, `/code-reviewer`, `/ship`, or
   `/document-release` even though those are not guaranteed by this plugin.
4. **High — Codex omissions were ambiguous:** five missing symlinks were
   reported without distinguishing a runtime limitation from an intentional
   deferred port.
5. **High — no repository contract gate:** manifest, link, language, permission,
   ID, size, version, and parity drift could merge without an automated check.

The v3.1.1 changes fix those five conditions without moving or deleting active
skills. The remaining work is structural rather than emergency remediation:
standardize per-skill input/output contracts, extract repeated TDD and review
policy, split the largest orchestrators, and add semantic prompt regression
fixtures.

**Recommendation:** major skill redesign is still warranted for the design
pipeline and repeated orchestration policy, but a repository-wide rewrite is
not. Preserve the public skill names and improve them incrementally behind
machine-checked contracts.

## Current Structure Visualization

```text
Repository
├── Marketplace
│   └── .claude-plugin/marketplace.json
├── Claude plugin
│   └── plugins/elian-store
│       ├── .claude-plugin/plugin.json
│       ├── Skills (26)
│       │   ├── brainstorm — fuzzy request → decision + persistent plan; depends on local context
│       │   ├── intake-spec — requirements/issue → spec.json; optional issue-provider lookup
│       │   ├── design-feature — spec/requirements → gated design document set; uses bundled renderers
│       │   ├── update-design — change + existing design set → affected document updates
│       │   ├── design-ui — screen/flow request → brief, references, wireframe, visual artifacts
│       │   ├── functional-spec — wireframes + code/design → component catalog + screen contracts
│       │   ├── implement — approved feature plan → tested implementation + evidence
│       │   ├── fix — reproducible defect → regression test + repair + evidence
│       │   ├── improve — measured baseline → behavior improvement + before/after evidence
│       │   ├── review — diff/files → read-only findings; uses engineering-reviewer
│       │   ├── pr-review — PR/MR context → panel verdict; uses read-only reviewers
│       │   ├── persona-review — review target → persona-native judgments; uses persona agents
│       │   ├── respond-to-review — review feedback + code → verified response decisions
│       │   ├── verify-before-claiming — proposed success claim → fresh evidence gate
│       │   ├── verify-implementation — project + verify-* skills → verification results
│       │   ├── manage-skills — code drift → updated project verify-* skills
│       │   ├── spec-coverage — design ACs + fresh test results → JSON/HTML coverage
│       │   ├── create-document — schema + JSON + template → deterministic HTML/Markdown
│       │   ├── document-writer — arbitrary content → house-style HTML/Markdown
│       │   ├── decision-dashboard — 3+ decisions → HTML dashboard + JSON record
│       │   ├── kanban-board — local task data → interactive offline HTML board
│       │   ├── erd-preview — schema + real rows → validated lineage HTML
│       │   ├── generate-teammate — explicit team request → execution plan + optional spawn
│       │   ├── harness-manager — two global harnesses → drift report + approved reconciliation
│       │   ├── pr-writer — diff/commits/intent → PR/MR title and body draft
│       │   └── finish-branch — completed branch + user choice → disposition/cleanup
│       ├── Shared
│       │   └── skills/_shared — common TDD execution strategy
│       ├── Agents (30 after this change)
│       │   ├── 14 domain agents
│       │   ├── 15 persona reviewers
│       │   └── engineering-reviewer
│       ├── Hooks
│       │   └── check-update.sh
│       └── Migrations
│           └── README.md
├── Codex companion
│   ├── skills/ — 14 source-sharing symlinks
│   ├── prompts/ — generate-teammate, persona-review
│   ├── setup.sh
│   ├── AGENTS.md
│   └── config.toml.example
├── Distribution model
│   ├── tools/clusters.json — five thematic output clusters + Codex dispositions
│   └── tools/generate.py — validate, plan, and optionally emit ignored dist artifacts
├── Maintainer-only content
│   ├── .claude/skills/vue-nuxt-best-practices
│   ├── .claude/workflows/harness-legacy-scan.js
│   └── .claude/plans/dual-tool-skill-distribution.md
├── Scripts
│   └── scripts/validate_repository.py
├── Tests
│   └── tests/test_repository_validation.py
└── Documentation
    ├── README.md and CONTRIBUTING.md
    ├── plugins/elian-store/README.md
    ├── docs/claude-codex-skill-parity.md
    ├── docs/plugin-portfolio-hybrid-model.md
    ├── docs/repository-operating-map.md
    └── this audit
```

## B. Repository Inventory

| Category | Name | Path | Purpose | Status | Notes |
|---|---|---|---|---|---|
| Plugin | elian-store | `plugins/elian-store/` | Installable Claude workflow bundle | Needs improvement | Strong bundle boundary; per-skill manifests are absent |
| Skill | brainstorm | `plugins/elian-store/skills/brainstorm/` | Decision discovery | Needs improvement | 466 lines; broad but distinct |
| Skill | intake-spec | `plugins/elian-store/skills/intake-spec/` | Requirements intake | Needs improvement | Provider fallback is documented; output contract needs schema-version policy |
| Skill | design-feature | `plugins/elian-store/skills/design-feature/` | Design-set orchestrator | Needs improvement | Large responsibility surface |
| Skill | update-design | `plugins/elian-store/skills/update-design/` | Design change propagation | Needs improvement | 425 lines and many document contracts |
| Skill | design-ui | `plugins/elian-store/skills/design-ui/` | UI design workflow | Needs improvement | Safe invocation gate fixed |
| Skill | functional-spec | `plugins/elian-store/skills/functional-spec/` | Wireframe-to-code contract | Needs improvement | Output labels aligned to English policy |
| Skill | implement | `plugins/elian-store/skills/implement/` | New feature TDD | Normal | Optional host handoffs clarified |
| Skill | fix | `plugins/elian-store/skills/fix/` | Regression-first repair | Normal | Optional host handoffs clarified |
| Skill | improve | `plugins/elian-store/skills/improve/` | Measured behavior improvement | Normal | Optional host handoffs clarified |
| Skill | review | `plugins/elian-store/skills/review/` | Read-only engineering review | Normal | Capability-enforced reviewer added |
| Skill | pr-review | `plugins/elian-store/skills/pr-review/` | Multi-perspective PR review | Needs improvement | Posting is gated; panel cost remains high |
| Skill | persona-review | `plugins/elian-store/skills/persona-review/` | Persona-native critique | Needs improvement | Fifteen largely parallel agent definitions |
| Skill | respond-to-review | `plugins/elian-store/skills/respond-to-review/` | Feedback triage | Normal | Correctly read-only and auto-invocable |
| Skill | verify-before-claiming | `plugins/elian-store/skills/verify-before-claiming/` | Fresh-evidence gate | Normal | Correctly read-only and auto-invocable |
| Skill | verify-implementation | `plugins/elian-store/skills/verify-implementation/` | Discover/run project verification | Needs improvement | Project verify-* convention is implicit |
| Skill | manage-skills | `plugins/elian-store/skills/manage-skills/` | Repair verify-skill drift | Needs improvement | Writes project harness files; now gated |
| Skill | spec-coverage | `plugins/elian-store/skills/spec-coverage/` | AC-to-test coverage | Normal | Strong deterministic tests and honest unchecked state |
| Skill | create-document | `plugins/elian-store/skills/create-document/` | Schema-validated rendering | Normal | Clear deterministic entry point |
| Skill | document-writer | `plugins/elian-store/skills/document-writer/` | General document authoring | Needs improvement | Boundary with create-document must stay explicit |
| Skill | decision-dashboard | `plugins/elian-store/skills/decision-dashboard/` | Decision artifact | Normal | Wildcard deletion removed |
| Skill | kanban-board | `plugins/elian-store/skills/kanban-board/` | Offline task board | Needs improvement | Browser/localStorage behavior needs end-to-end tests |
| Skill | erd-preview | `plugins/elian-store/skills/erd-preview/` | Real-data lineage explorer | Needs improvement | Good static validator; browser behavior untested |
| Skill | generate-teammate | `plugins/elian-store/skills/generate-teammate/` | Explicit team orchestration | Needs improvement | 496 lines, four below hard limit |
| Skill | harness-manager | `plugins/elian-store/skills/harness-manager/` | Global harness reconciliation | Needs improvement | High-impact scope; approval and backup rules are essential |
| Skill | pr-writer | `plugins/elian-store/skills/pr-writer/` | Draft PR/MR content | Normal | Draft-only contract fixed |
| Skill | finish-branch | `plugins/elian-store/skills/finish-branch/` | Branch disposition | Needs improvement | Destructive options are explicit and gated |
| Agent group | Domain agents | `plugins/elian-store/agents/*-architect.md` and peers | Specialist design/review lenses | Needs improvement | Tool policies vary by role |
| Agent group | Persona reviewers | `plugins/elian-store/agents/persona-*-reviewer.md` | Read-only persona judgments | Duplicate suspected | Repeated shell-free read-only contract |
| Agent | engineering-reviewer | `plugins/elian-store/agents/engineering-reviewer.md` | Capability-enforced engineering review | Normal | New canonical read-only engineering reviewer |
| Hook | Update hook | `plugins/elian-store/hooks/check-update.sh` | Update notice/migration runner | Needs improvement | Self-test exists; network behavior remains environment-dependent |
| Workflow | harness-legacy-scan | `.claude/workflows/harness-legacy-scan.js` | Maintainer-distributed harness audit | Legacy suspected | Not plugin content; classification is documented |
| Dev skill | vue-nuxt-best-practices | `.claude/skills/vue-nuxt-best-practices/` | Maintainer-only guidance | Legacy suspected | Valid content, but separate lifecycle from marketplace |
| Cluster manifest | Thematic distribution | `tools/clusters.json` | Defines five optional generated bundles | Normal | Now covers every skill and Codex disposition |
| Generator | Cluster generator | `tools/generate.py` | Validate/emit distributions | Normal | Report-only by default |
| Validator | Repository validator | `scripts/validate_repository.py` | Enforce repository contracts | Normal | New in v3.1.1 |
| CI | Validate repository | `.github/workflows/validate-repository.yml` | PR/main validation | Normal | New in v3.1.1 |

## C. Skill-by-Skill Review

### brainstorm

- Path: `plugins/elian-store/skills/brainstorm/SKILL.md`
- Current purpose: Convert ambiguous ideas into an explicit decision and persisted plan.
- Actual behavior: Context scan, bounded Socratic interview, at least three options, trade-off comparison, decision, and handoff.
- Input: Ambiguous request plus optional depth/output arguments.
- Output: Decision summary and optional plan artifact.
- Dependencies: Local repository reads; optional downstream implementation/team workflows.
- Strengths: Clear non-use boundary and re-entry paths.
- Problems: 466 lines; orchestration and teaching material are interleaved.
- Severity: Medium.
- Evidence: The skill is close to the 500-line cap and repeats downstream workflow policy.
- Improvement: Move extended examples/failure tables into `references/`; keep the public workflow stable.
- Merge/delete: Keep; do not merge with intake-spec because decision discovery and structured intake differ.
- Recommended final responsibility: Own ambiguity resolution only.

### intake-spec

- Path: `plugins/elian-store/skills/intake-spec/SKILL.md`
- Current purpose: Normalize a request or optional issue into `spec.json`.
- Actual behavior: Uses user text first, optionally reads GitHub/GitLab/JIRA context, then writes structured intake.
- Input: Requirement text, issue URL/key, or both.
- Output: `claudedocs/<label>/spec.json`.
- Dependencies: Optional provider tools; local renderer/handoff conventions.
- Strengths: Works without an issue tracker and now has narrow provider commands.
- Problems: Schema version, overwrite behavior, and migration policy are not a standalone machine contract.
- Severity: Medium.
- Evidence: Contract is distributed across `SKILL.md`, design references, and downstream assumptions.
- Improvement: Publish a versioned intake schema and idempotency rules.
- Merge/delete: Keep; feed design-feature through a stable schema.
- Recommended final responsibility: Requirements normalization, not design.

### design-feature

- Path: `plugins/elian-store/skills/design-feature/SKILL.md`
- Current purpose: Produce the complete gated design artifact set.
- Actual behavior: Coordinates domain, architecture, PRD/tech spec, API/QA, and roadmap generation.
- Input: `spec.json` or inline requirements.
- Output: Multiple Markdown, SQL, JSON, and HTML artifacts.
- Dependencies: Bundled references/renderers and optional specialist agents.
- Strengths: User gates, explicit artifact set, and cross-document checks.
- Problems: One skill owns too many document domains; partial failure and resume state are prose-defined.
- Severity: High.
- Evidence: The entry point spans five phases and many output contracts in one 373-line prompt.
- Improvement: Keep it as a thin orchestrator over versioned artifact contracts and resumable phase state.
- Merge/delete: Keep orchestrator; extract document-specific policy.
- Recommended final responsibility: Route and verify design phases, not author every schema inline.

### update-design

- Path: `plugins/elian-store/skills/update-design/SKILL.md`
- Current purpose: Propagate an approved decision through an existing design set.
- Actual behavior: Builds an impact matrix, asks for scope approval, updates documents sequentially, verifies consistency.
- Input: Existing design folder plus a change decision.
- Output: Minimal affected-file edits and validation summary.
- Dependencies: Design-feature artifact naming and bundled renderer scripts.
- Strengths: Explicit impact analysis and minimal-update intent.
- Problems: 425 lines; artifact ordering and commit behavior are tightly coupled to one folder convention.
- Severity: Medium.
- Evidence: Nine document types and multiple gates live in one prompt.
- Improvement: Read a design-set manifest rather than hard-coding the full artifact graph in prose.
- Merge/delete: Keep separate from design-feature because change propagation has different risk.
- Recommended final responsibility: Impact analysis and consistency-preserving updates.

### design-ui

- Path: `plugins/elian-store/skills/design-ui/SKILL.md`
- Current purpose: Create gated UI/UX artifacts before implementation.
- Actual behavior: Interview, references, wireframe, user gate, visual design, delivery.
- Input: Screen/flow request and optional existing design context.
- Output: Brief, references, wireframe, visual artifacts, delivery notes.
- Dependencies: Optional WebFetch and local file/browser capabilities.
- Strengths: Strong stage gate before visual polish.
- Problems: External-tool failure behavior and reusable output schema are mostly natural language.
- Severity: Medium.
- Evidence: Frontmatter allows WebFetch while output artifacts are not represented by a manifest.
- Improvement: Add offline-reference fallback and `design-ui.manifest.json`.
- Merge/delete: Keep.
- Recommended final responsibility: UI design decisions and artifacts, never product implementation.

### functional-spec

- Path: `plugins/elian-store/skills/functional-spec/SKILL.md`
- Current purpose: Bridge wireframes to code-grounded component and behavior contracts.
- Actual behavior: Builds a shared component catalog, per-screen decomposition, connected HTML, and hub.
- Input: One or more wireframes plus codebase or greenfield design context.
- Output: Component catalog, Markdown specs, connected HTML, hub.
- Dependencies: Existing code paths or designed API/entity contracts.
- Strengths: Explicit anti-fabrication grounding and reuse-first component design.
- Problems: Large mixed artifact set; connected-view behavior lacks automated browser regression.
- Severity: Medium.
- Evidence: Four outputs and code/greenfield modes share one prompt; template checks are static.
- Improvement: Add fixture-driven connected-view interaction tests and a shared artifact manifest.
- Merge/delete: Keep.
- Recommended final responsibility: Implementation contracts from approved wireframes.

### implement

- Path: `plugins/elian-store/skills/implement/SKILL.md`
- Current purpose: Build new behavior through approval-gated TDD.
- Actual behavior: Context, plan, approval, Red-Green-Refactor, verification, direct review, report.
- Input: Clear feature request and repository context.
- Output: Code/tests plus verification and change report.
- Dependencies: Repository test commands; optional host review/commit capabilities.
- Strengths: Clear feature-only trigger and approval gate.
- Problems: Repeats most execution policy with fix and improve.
- Severity: Medium.
- Evidence: Three skills separately encode planning, test execution, review, and reporting.
- Improvement: Expand `_shared` into a versioned execution contract while retaining separate entry points.
- Merge/delete: Keep public skill; share internals.
- Recommended final responsibility: New feature behavior only.

### fix

- Path: `plugins/elian-store/skills/fix/SKILL.md`
- Current purpose: Repair a confirmed bug with a regression test first.
- Actual behavior: Root-cause analysis, approved repair plan, failing regression, repair, verification, review.
- Input: Symptom/reproduction and repository context.
- Output: Regression test, minimal fix, evidence report.
- Dependencies: Repository test commands; optional host review/commit capabilities.
- Strengths: Distinct root-cause and regression-first contract.
- Problems: Shared workflow duplication with implement/improve.
- Severity: Medium.
- Evidence: TDD execution and reporting sections substantially parallel the sibling skills.
- Improvement: Share execution/report fragments, preserve bug-specific gates.
- Merge/delete: Keep public skill.
- Recommended final responsibility: Confirmed defects only.

### improve

- Path: `plugins/elian-store/skills/improve/SKILL.md`
- Current purpose: Change working behavior with measurable before/after evidence.
- Actual behavior: Baseline measurement, approval, protected TDD change, remeasurement, review.
- Input: Working feature and desired measurable improvement.
- Output: Tests/code plus before/after evidence.
- Dependencies: Repository test/measurement tools; optional host review/commit capabilities.
- Strengths: Separates improvement from bug repair and new features.
- Problems: Measurement schemas are domain-specific and prose-only; shared workflow duplication remains.
- Severity: Medium.
- Evidence: The skill requires quantified comparison but defines no reusable result schema.
- Improvement: Standardize `before`, `after`, `metric`, `method`, and confidence fields.
- Merge/delete: Keep public skill.
- Recommended final responsibility: Behavior-changing optimization/hardening.

### review

- Path: `plugins/elian-store/skills/review/SKILL.md`
- Current purpose: Read-only engineering review of local changes.
- Actual behavior: Resolve scope, inspect diff/context, dispatch read-only lenses, lead with prioritized findings.
- Input: Worktree, branch diff, PR diff, files, or explicit scope.
- Output: Findings with severity and file:line evidence.
- Dependencies: `engineering-reviewer` and read-only git/file tools.
- Strengths: Clear non-editing boundary and findings-first format.
- Problems: Agent result quality remains prompt-based and lacks seeded defect regression fixtures.
- Severity: Medium.
- Evidence: Structural validator checks capabilities, not whether reviewers find known bugs.
- Improvement: Add golden diff fixtures with expected minimum findings.
- Merge/delete: Keep; share reviewer policy with pr-review.
- Recommended final responsibility: Local engineering findings only.

### pr-review

- Path: `plugins/elian-store/skills/pr-review/SKILL.md`
- Current purpose: Multi-perspective review of an existing PR/MR.
- Actual behavior: Gathers remote context, dispatches engineering/persona panels, synthesizes verdict, optionally posts after confirmation.
- Input: PR/MR ID, URL, or current branch.
- Output: Local prioritized verdict; optional confirmed remote comment/review.
- Dependencies: GitHub/GitLab CLI, Agent tool, read-only reviewers.
- Strengths: Local-by-default and explicit posting gate.
- Problems: Potentially excessive panel fan-out and remote-fetch dependency.
- Severity: Medium.
- Evidence: The prompt supports many lenses even when a smaller scope would suffice.
- Improvement: Cap automatic lenses, publish selection reasons, and define offline local-diff fallback.
- Merge/delete: Keep separate from local review; share the engineering reviewer contract.
- Recommended final responsibility: Remote change review and optional confirmed posting.

### persona-review

- Path: `plugins/elian-store/skills/persona-review/SKILL.md`
- Current purpose: Review a target through selected expert personas.
- Actual behavior: Detects axes, selects up to several persona agents, returns native judgments.
- Input: Document/code/idea plus optional persona/depth override.
- Output: Short synthesis and persona-native critiques.
- Dependencies: Fifteen persona agent definitions and Agent tool.
- Strengths: Explicitly avoids a fake shared scorecard.
- Problems: Agent frontmatter and read-only boilerplate are duplicated across 15 files.
- Severity: Medium.
- Evidence: `plugins/elian-store/agents/persona-*-reviewer.md` repeats common boundaries.
- Improvement: Generate agent frontmatter from a reviewed persona registry or validate a shared fragment.
- Merge/delete: Keep personas; do not collapse their judgment styles.
- Recommended final responsibility: Perspective-specific critique, not engineering sign-off.

### respond-to-review

- Path: `plugins/elian-store/skills/respond-to-review/SKILL.md`
- Current purpose: Triage feedback on the user's own change.
- Actual behavior: Verifies each suggestion, clarifies ambiguity, accepts or rejects with technical reasons.
- Input: Review comments and relevant code/diff.
- Output: Per-comment decision and implementation handoff.
- Dependencies: Read-only repository inspection.
- Strengths: Correctly separates review consumption from editing.
- Problems: No structured decision schema for large comment sets.
- Severity: Low.
- Evidence: Output is natural-language-only.
- Improvement: Add optional comment ID/status/evidence table.
- Merge/delete: Keep.
- Recommended final responsibility: Review-feedback decisions only.

### verify-before-claiming

- Path: `plugins/elian-store/skills/verify-before-claiming/SKILL.md`
- Current purpose: Prevent unsupported completion claims.
- Actual behavior: Identifies the proving command, runs it fresh, reads output, then qualifies the claim.
- Input: Intended success claim and repository state.
- Output: Fresh evidence or an honest failure/unknown statement.
- Dependencies: Read-only test/build/status commands.
- Strengths: Narrow, auto-invocable, and distinct from suite orchestration.
- Problems: Host command allowlist can never cover every project runner.
- Severity: Low.
- Evidence: Supported commands are explicit but finite.
- Improvement: Define a safe escalation rule for project-owned verification commands.
- Merge/delete: Keep.
- Recommended final responsibility: Claim-time honesty only.

### verify-implementation

- Path: `plugins/elian-store/skills/verify-implementation/SKILL.md`
- Current purpose: Discover and run project-local verify-* skills.
- Actual behavior: Finds verification skills, excludes itself/manual-only flows, executes applicable checks, optionally fixes with approval.
- Input: Current repository and change scope.
- Output: Check inventory, failures, evidence, and optional fix results.
- Dependencies: Project-local verify-* conventions and discovery script.
- Strengths: Dynamic discovery avoids a hard-coded central list.
- Problems: Project conventions are not represented by a schema; Edit capability makes the name sound safer than the optional behavior is.
- Severity: Medium.
- Evidence: The skill can edit after approval, while its primary name sounds verification-only.
- Improvement: Split `--fix` into an explicit mode and version the verify-skill metadata contract.
- Merge/delete: Keep; retain explicit fix gate.
- Recommended final responsibility: Verification orchestration, with mutations only in explicit fix mode.

### manage-skills

- Path: `plugins/elian-store/skills/manage-skills/SKILL.md`
- Current purpose: Detect and repair drift in project verify-* skills.
- Actual behavior: Maps code changes to verification coverage, creates/updates project skill files, validates them.
- Input: Repository patterns, changes, and current verify-* skills.
- Output: Updated project verification skills and drift report.
- Dependencies: Project harness layout and frontmatter checker.
- Strengths: Treats verification definitions as maintainable code.
- Problems: Writes another repository's harness definitions and relies on broad grep/find semantics.
- Severity: High.
- Evidence: `allowed-tools` includes Edit/Write and the workflow can create or change project skills.
- Improvement: Require a dry-run manifest before edits and constrain write roots to resolved verify-* targets.
- Merge/delete: Keep, but do not auto-invoke.
- Recommended final responsibility: Explicit verification-skill maintenance.

### spec-coverage

- Path: `plugins/elian-store/skills/spec-coverage/SKILL.md`
- Current purpose: Bind acceptance criteria to fresh test results.
- Actual behavior: Seeds requirements, runs the project suite, parses JUnit XML, renders JSON/HTML coverage.
- Input: Design documents, project test runner, and test results produced in the same run.
- Output: `spec-coverage.json` and `spec-coverage.html`.
- Dependencies: Project test runner and bundled build/apply/render/validate scripts.
- Strengths: Distinguishes machine proof, manual evidence, unchecked, skipped, and failed.
- Problems: Runner discovery and JUnit normalization will require more ecosystem fixtures.
- Severity: Medium.
- Evidence: Current self-test is strong but bounded to bundled fixtures and supported runners.
- Improvement: Add fixtures for multi-module and large-report repositories.
- Merge/delete: Keep.
- Recommended final responsibility: Requirement evidence, not generic test execution.

### create-document

- Path: `plugins/elian-store/skills/create-document/SKILL.md`
- Current purpose: Deterministically validate JSON and substitute it into a bundled template.
- Actual behavior: Resolve template/schema, validate, render, and return a file.
- Input: JSON, template ID/path, schema, output path.
- Output: HTML or Markdown artifact.
- Dependencies: Bundled stdlib scripts and templates.
- Strengths: Clear validate-before-render contract and automation-friendly errors.
- Problems: Template discovery/versioning is implicit.
- Severity: Low.
- Evidence: Templates are bundled, but no registry records template version compatibility.
- Improvement: Add a template registry with IDs, schema versions, and output media types.
- Merge/delete: Keep separate from document-writer.
- Recommended final responsibility: Deterministic rendering only.

### document-writer

- Path: `plugins/elian-store/skills/document-writer/SKILL.md`
- Current purpose: Author a readable house-style document from arbitrary content.
- Actual behavior: Structures content, renders self-contained HTML or Markdown, optionally supports browser PDF printing.
- Input: Arbitrary source content and requested format/path.
- Output: One human-readable document.
- Dependencies: Bundled build script; optional host/browser PDF capability.
- Strengths: Explicitly distinguishes authoring from fixed-schema rendering.
- Problems: Very broad trigger language can overlap ordinary responses and create unwanted files.
- Severity: Medium.
- Evidence: Description says to use whenever a result is something a person will read or keep.
- Improvement: Require an explicit artifact/save/share intent before writing.
- Merge/delete: Keep separate; narrow invocation boundary.
- Recommended final responsibility: Explicitly requested durable narrative artifacts.

### decision-dashboard

- Path: `plugins/elian-store/skills/decision-dashboard/SKILL.md`
- Current purpose: Consolidate 3+ blocking decisions into a fast decision artifact.
- Actual behavior: Generates validated JSON/HTML, records selections and memo, preserves artifacts.
- Input: Three or more pending decisions and their options.
- Output: Printable HTML and downstream JSON.
- Dependencies: Bundled template, schema, validator, and optional browser open.
- Strengths: Strong structured output and selection traceability.
- Problems: Finalization/deletion policy was unsafe in the baseline.
- Severity: Critical, fixed.
- Evidence: Baseline frontmatter exposed wildcard deletion; v3.1.1 removes it and requires an exact confirmed target.
- Improvement: Keep immutable decision history and add migration tests for schema changes.
- Merge/delete: Keep.
- Recommended final responsibility: Decision capture, never workspace cleanup.

### kanban-board

- Path: `plugins/elian-store/skills/kanban-board/SKILL.md`
- Current purpose: Generate an offline interactive board from local task data.
- Actual behavior: Converts spec/roadmap/chat tasks into embedded JSON, supports drag/drop, editing, filters, localStorage, import/export.
- Input: Local task source and optional existing board snapshot.
- Output: Self-contained HTML and optional exported JSON.
- Dependencies: Bundled template/build script and browser runtime.
- Strengths: No hidden external issue-tracker dependency.
- Problems: Import overwrite, localStorage migration, drag/drop, and mobile layout lack automated browser coverage.
- Severity: Medium.
- Evidence: Most behavior lives in `assets/kanban-board-template.html`; no browser test exists.
- Improvement: Add Playwright fixtures for persistence, invalid import, reset, keyboard/mobile, and existing-output refresh.
- Merge/delete: Keep.
- Recommended final responsibility: Offline visualization/editing of existing local tasks.

### erd-preview

- Path: `plugins/elian-store/skills/erd-preview/SKILL.md`
- Current purpose: Visualize schema relationships over real rows.
- Actual behavior: Fills a fixed template, validates relationship integrity/layers, and provides interactive lineage.
- Input: DDL/schema, real data rows, relationships, layers, labels.
- Output: One lineage HTML file plus static validation result.
- Dependencies: Bundled HTML template, Python validator, and Node for data extraction.
- Strengths: Explicit real-data requirement and hard/soft relationship distinction.
- Problems: Large schemas, malformed value types, and browser interactions have limited regression coverage.
- Severity: Medium.
- Evidence: Static validator covers integrity but not rendered interaction/layout.
- Improvement: Add small/large fixtures and headless browser assertions.
- Merge/delete: Keep.
- Recommended final responsibility: Read-only lineage visualization.

### generate-teammate

- Path: `plugins/elian-store/skills/generate-teammate/SKILL.md`
- Current purpose: Plan and optionally spawn a team only when explicitly requested.
- Actual behavior: Decomposes phases, chooses direct/subagent/team execution, validates JSON prompts, spawns after confirmation.
- Input: Explicit team request and clear problem statement.
- Output: Team plan, task prompts, optional spawned team.
- Dependencies: Team/Agent tools and create-document rendering.
- Strengths: Explicit trigger, cost gate, ownership planning.
- Problems: 496 lines; any small addition will violate the hard limit.
- Severity: High.
- Evidence: Current `SKILL.md` is four lines below 500.
- Improvement: Move examples, known issues, and matrices to references immediately.
- Merge/delete: Keep; reduce entry point before feature work.
- Recommended final responsibility: Explicit multi-agent execution planning and spawn.

### harness-manager

- Path: `plugins/elian-store/skills/harness-manager/SKILL.md`
- Current purpose: Reconcile Claude and Codex global harness drift.
- Actual behavior: Scans global rules/config/commands/skills, produces a report, then applies approved backed-up changes.
- Input: Two global harness roots and desired reconciliation choices.
- Output: Drift report, backups, and approved edits.
- Dependencies: Host global filesystem and tool-specific config formats.
- Strengths: Separates project scope and requires approval.
- Problems: Very high blast radius and host-specific schemas; rollback verification is prose-defined.
- Severity: High.
- Evidence: The workflow edits global files outside a project and is intentionally Claude-only.
- Improvement: Emit a machine-readable change plan and verify backup restoration in tests.
- Merge/delete: Keep Claude-only.
- Recommended final responsibility: Explicit global harness reconciliation only.

### pr-writer

- Path: `plugins/elian-store/skills/pr-writer/SKILL.md`
- Current purpose: Draft a high-signal PR/MR title and body.
- Actual behavior: Reads diff/commits/template/intent, contrasts intent and implementation, returns a draft.
- Input: Local branch context and optional issue/PR template.
- Output: Draft title/body; no remote mutation.
- Dependencies: Read-only git and optional read-only GitHub/GitLab context.
- Strengths: Clear output contract and platform detection.
- Problems: Baseline mixed drafting with creation language.
- Severity: High, fixed.
- Evidence: v3.1.1 removes `--create` semantics and explicitly forbids push/create/submit/merge.
- Improvement: Add fixture tests for GitHub/GitLab templates and missing intent.
- Merge/delete: Keep.
- Recommended final responsibility: Draft only.

### finish-branch

- Path: `plugins/elian-store/skills/finish-branch/SKILL.md`
- Current purpose: Execute a user-selected disposition for a completed branch.
- Actual behavior: Verifies state, detects worktree mode, presents closed choices, then merges/pushes/keeps/discards.
- Input: Clean or explicitly handled branch plus user choice.
- Output: Branch disposition and cleanup report.
- Dependencies: Git/worktree commands and optional host commit/release skills with plain-git fallback.
- Strengths: Closed menu and explicit destructive choice.
- Problems: Combines non-destructive status reporting with merge/push/discard operations.
- Severity: High.
- Evidence: Frontmatter exposes checkout, merge, push, and worktree removal commands.
- Improvement: Keep confirmation immediately adjacent to destructive execution and add worktree-state fixtures.
- Merge/delete: Keep Claude-only; do not auto-invoke.
- Recommended final responsibility: Final branch disposition after verified completion.

## D. Complete Issue Register

| ID | Severity | Target | File path | Problem | Impact | Recommendation |
|---|---|---|---|---|---|---|
| R-001 | Critical | decision-dashboard | `plugins/elian-store/skills/decision-dashboard/SKILL.md` | Baseline auto-invocation plus wildcard artifact deletion | Unrequested file loss | Fixed: explicit invocation, no wildcard deletion, exact confirmed target only |
| R-002 | High | Side-effect skills | `plugins/elian-store/skills/{create-document,design-ui,functional-spec,...}/SKILL.md` | Invocation gates were inconsistent | Unrequested writes | Fixed and enforced by repository validator |
| R-003 | High | Review agents | `plugins/elian-store/agents/persona-*-reviewer.md` | "Read-only" agents exposed Bash | Review could mutate or execute | Fixed; read-only tools only |
| R-004 | High | Engineering review | `plugins/elian-store/skills/{review,pr-review}/SKILL.md` | Broad domain agents enforced read-only only by prose | Capability mismatch | Fixed with `engineering-reviewer.md` |
| R-005 | High | pr-writer | `plugins/elian-store/skills/pr-writer/SKILL.md` | Draft/create responsibility was ambiguous | Unexpected remote mutation | Fixed; draft-only |
| R-006 | High | Core flows | `plugins/elian-store/skills/{implement,fix,improve,update-design}/SKILL.md` | Required optional host skills | Core path could stop despite valid repository | Fixed with direct fallback and optional handoffs |
| R-007 | High | Codex parity | `tools/clusters.json`, `tools/generate.py` | Missing ports lacked a disposition reason | False failure or silent omission | Fixed with `deferred` disposition and overlap checks |
| R-008 | High | Repository | `.github/workflows/` | No active repository validation workflow | Drift could merge | Fixed with `validate-repository.yml` |
| R-009 | High | design-feature | `plugins/elian-store/skills/design-feature/SKILL.md` | Too many authoring responsibilities | Partial failures and expensive changes | Make it a thin resumable orchestrator |
| R-010 | High | generate-teammate | `plugins/elian-store/skills/generate-teammate/SKILL.md` | 496 lines | Next small change can break hard limit | Extract examples and matrices |
| R-011 | High | harness-manager | `plugins/elian-store/skills/harness-manager/SKILL.md` | Global mutation scope | Large blast radius | Add machine change plan and rollback tests |
| R-012 | Medium | TDD triad | `plugins/elian-store/skills/{implement,fix,improve}/SKILL.md` | Repeated execution/review/report policy | Contract drift | Expand versioned `_shared` policy |
| R-013 | Medium | Persona agents | `plugins/elian-store/agents/persona-*-reviewer.md` | Repeated frontmatter/boundary text | Multi-file churn | Registry/generation or shared validator |
| R-014 | Medium | Artifact contracts | `plugins/elian-store/skills/*/SKILL.md` | No standard per-skill manifest | Automation must parse prose | Introduce versioned manifest schema incrementally |
| R-015 | Medium | Browser artifacts | `functional-spec`, `kanban-board`, `erd-preview` templates | Static checks do not prove interaction/layout | User-facing regressions | Add headless browser fixtures |
| R-016 | Medium | Language policy | Codex config, functional-spec refs, design examples, templates | Baseline distribution content contained Korean | Violated repository rules and mixed defaults | Fixed for distribution docs/templates; runtime localization remains allowed |
| R-017 | Medium | Relative links | Markdown reference scanning | Fenced example paths looked like broken live links | Noisy audits encourage ignoring failures | Validator now excludes fenced examples |
| R-018 | Medium | Semantic regression | All prompt skills | Structure tests do not prove prompt quality | Confident but wrong behavior can pass CI | Add scenario/golden-output tests |
| R-019 | Low | Maintainer content | `.claude/skills/`, `.claude/workflows/`, `.claude/plans/` | Separate lifecycles share repository root | Contributor confusion | Keep labels in operating map; consider `dev/` later |
| R-020 | Low | Historical output | `CHANGELOG.md`, ignored `dist/` | Historical/generated content resembles active source | False duplicate/legacy signals | Keep history; regenerate dist only for release validation |

No unresolved Critical finding remains after v3.1.1. High findings R-009,
R-010, and R-011 remain planned structural work.

## E. Duplicate and Consolidation Candidates

| Target A | Target B | Duplicate content | Difference | Recommended action |
|---|---|---|---|---|
| implement | fix | Plan, TDD loop, verification, review, report | Feature vs confirmed defect; Red strategy differs | Keep public skills; extract shared execution/report contract |
| implement/fix | improve | Same execution and review shell | Improve requires before/after measurement | Keep; share common policy |
| create-document | document-writer | Both emit HTML/Markdown | Deterministic rendering vs narrative authoring | Keep separate; narrow document-writer trigger |
| review | pr-review | Engineering findings and severity | Local diff vs remote context/panel/posting | Keep; share read-only reviewer and finding schema |
| review | persona-review | Both critique targets | Engineering risk vs persona-native judgment | Keep distinct and document selection boundary |
| verify-before-claiming | verify-implementation | Both run verification | One proves a claim; one discovers suites | Keep distinct; share evidence vocabulary |
| verify-implementation | manage-skills | Both inspect verify-* skills | Consumer vs maintainer | Keep pair; standardize verify-skill manifest |
| design-feature | update-design | Same artifact graph | Initial generation vs change propagation | Keep; extract artifact dependency manifest |
| 15 persona agents | persona-review registry | Repeated tools/boundary/frontmatter | Persona voice and domain differ | Generate/validate common metadata; retain persona bodies |
| README | plugin README | Skill catalog and validation text | Repository vs installed-plugin audience | Keep both; generate catalog table or test parity |

## F. Deletion and Legacy Candidates

References were checked before making recommendations. No active skill is a safe
deletion candidate in this first pass.

| Path | Basis for deletion/move | Reference status | Recommended action |
|---|---|---|---|
| `.claude/plans/dual-tool-skill-distribution.md` | Historical plan, not runtime input | Referenced as maintainer context only | Move to `docs/archive/` after confirming no active workflow consumes it |
| `.claude/skills/vue-nuxt-best-practices/` | Maintainer-only skill inside product repo | Documented by repository operating map | Keep or move to a clearly named `dev/skills/`; do not delete |
| `.claude/workflows/harness-legacy-scan.js` | Copy-distributed workflow, not plugin content | Referenced by root/workflow READMEs | Keep; consider separate dev-tools distribution later |
| `dist/marketplace/` | Generated and ignored | Produced by `tools/generate.py --emit` | Do not commit; regenerate for release checks |
| `claudedocs/` | Local evaluation artifacts and ignored output | Some local test protocols refer to it | Do not delete in repository refactor |
| Retired command names in `CHANGELOG.md` | Historical references only | Not active entry points | Keep history; validator checks current catalogs, not changelog prose |

## Scenario-based Validation

| Scenario | Selected skill(s) | Expected sequence | Main failure risk | Verifiable? | Required rule |
|---|---|---|---|---|---|
| 1. Complete valid input | Narrowest matching skill | Validate input → plan/gate if needed → execute → verify → report | Over-orchestration | Yes, outputs/tests | Prefer exact public responsibility |
| 2. Partially missing input | brainstorm, intake-spec, or selected skill | Reuse supplied facts → ask only blocking question → continue | Re-asking known facts | Partly | Distinguish required vs optional fields |
| 3. Missing path/target | Selected skill | Resolve read-only → fail with exact missing target → no writes | Creating guessed paths | Yes | Never invent source targets |
| 4. External tool unavailable | intake-spec, design-ui, pr-review, etc. | Use local/user-provided context or report environment-dependent block | Treating host absence as repository defect | Yes, static/fallback | Every optional tool needs a fallback or explicit block |
| 5. Mid-flow step fails | Any orchestrator | Preserve completed artifacts → report failed step → offer resume point | Claiming full success | Yes | Phase state and completion conditions |
| 6. Output already exists | Artifact skills | Inspect ownership → update/alternate/confirm overwrite | Silent overwrite | Yes | Idempotency and exact overwrite rule |
| 7. Multiple triggers match | brainstorm/intake/design or review/persona/pr-review | Select narrowest purpose; explain handoff | Duplicate work or conflicting gates | Partly | Central responsibility map |
| 8. User asks analysis only | review/persona-review | Read-only inspection → findings → stop | Editing because a fix is obvious | Yes | Capability-enforced read-only agents |
| 9. User asks actual modification | implement/fix/improve/update-design | Plan/approval where material → edit/test/review/report | Ending after a plan | Yes | Explicit implementation completion condition |
| 10. Large repository | Any search-heavy skill | Scope → sample/map → batch checks → progress → targeted execution | Unbounded context/tool fan-out | Partly | Budgets, progress, resumable artifacts |

The v3.1.1 validator covers structural selection prerequisites, permissions,
references, and manifests. Scenarios 1, 5, 7, 9, and 10 still need semantic
prompt-regression fixtures; static validation alone cannot prove them.

## G. Target Architecture

```text
.claude-plugin/
  marketplace.json

plugins/
  elian-store/
    .claude-plugin/plugin.json
    skills/
      <skill-name>/
        SKILL.md
        manifest.json          # versioned input/output/side-effect contract
        prompts/               # only when multiple prompt fragments are real
        schemas/
        scripts/
        references/
        templates/
        fixtures/
        tests/
      _shared/
        execution/             # TDD plan/gate/verify/report contract
        evidence/              # common finding and verification vocabulary
        artifact-set/          # design document dependency manifest
    agents/
      registry.json            # ID, role, capability class
      engineering-reviewer.md
      persona-*.md
    hooks/
    migrations/

codex/
  skills/                      # source-sharing symlinks only
  prompts/                     # platform adapters only
  AGENTS.md
  config.toml.example

scripts/
  validate_repository.py
  validate_skill_manifest.py
  check_links.py               # may remain a validator module, not necessarily a file
  check_prompt_fixtures.py

tests/
  repository/
  prompts/
  artifacts/
  browser/

docs/
  architecture.md
  claude-codex-skill-parity.md
  skill-development-standard.md
  migration-guide.md
  audits/

.github/workflows/
  validate-repository.yml
```

Why these directories are needed:

- `manifest.json` makes inputs, outputs, risk class, dependencies, and version
  available without parsing prose.
- `_shared/execution` reduces real duplication across the TDD triad without
  collapsing their public purposes.
- `_shared/evidence` lets review and verification results compose.
- `_shared/artifact-set` gives design-feature and update-design one dependency
  graph.
- Per-skill `fixtures/tests` keep deterministic tests next to the owning skill.
- Repository `tests/prompts` handles cross-skill selection/conflict scenarios.
- `agents/registry.json` centralizes capability class while persona bodies retain
  independent judgment styles.

## H. Phased Refactoring Plan

### Phase 1: Safe Cleanup

| Work | Target | Reason | Expected effect | Risk | Prerequisite | Completion criterion |
|---|---|---|---|---|---|---|
| Gate side effects | Writing/posting/destructive skills | Prevent unrequested mutation | Explicit invocation for risky work | Missed auto-use convenience | Skill inventory | Validator reports zero gate failures |
| Remove broad tools | Dashboard, intake, design, review agents | Reduce blast radius | Capability matches purpose | Too-narrow command blocks valid flow | Actual command audit | No unsafe allowed-tools patterns |
| Fix host assumptions | TDD/design/release handoffs | Core path must be self-contained | Graceful optional integration | Duplicate fallback prose | Dependency inventory | Missing host skill does not block core path |
| Restore language policy | Distribution docs/templates | Consistent repository contract | Predictable shipped defaults | Intentional localization removal | Identify runtime localization separately | Policy scan passes |
| Repair parity classification | `clusters.json`, parity docs | Separate blocked vs deferred | No ambiguous missing links | Wrong disposition claim | Runtime capability review | Generator and validator agree |

Status: completed in v3.1.1.

### Phase 2: Structural Improvement

| Work | Target | Reason | Expected effect | Risk | Prerequisite | Completion criterion |
|---|---|---|---|---|---|---|
| Standard manifest schema | All skills | Prose contracts are not composable | Machine-readable I/O and risk | Metadata duplication | Schema design | 26 valid manifests, generated docs parity |
| Extract TDD execution policy | implement/fix/improve | Repeated workflow drifts | One tested execution contract | Over-generalization | Diff common vs unique steps | Public behavior unchanged, duplication reduced |
| Artifact dependency manifest | design-feature/update-design | Hard-coded document graph | Resumable minimal updates | Migration complexity | Inventory current outputs | Both skills consume same graph |
| Agent capability registry | All agents | Tool classes are scattered | Enforced read-only/write classes | Generated-file churn | Decide source of truth | Agent files validate against registry |
| Naming/lifecycle standard | Plugin, dev workflow, dev skill | Root mixes distribution types | Clear ownership | File moves break docs | Reference map | Operating map and paths agree |

### Phase 3: Skill Refactoring

| Work | Target | Reason | Expected effect | Risk | Prerequisite | Completion criterion |
|---|---|---|---|---|---|---|
| Thin design orchestrator | design-feature | Too many responsibilities | Resumable phase routing | Contract break | Artifact manifest | Each phase independently testable |
| Reduce large entry points | generate-teammate, brainstorm, update-design | Near size limits | Easier maintenance | Context split hurts usability | Reference routing tests | Each SKILL under target size with valid links |
| Clarify document writer trigger | document-writer | Overlaps normal chat/artifacts | Fewer unwanted files | Under-triggering | Usage examples | Explicit durable-artifact intent required |
| Explicit fix modes | verify-implementation | Verification name hides optional edit | Clear read/write boundary | Command compatibility | Manifest modes | Default cannot edit; `--fix` is gated |
| Browser artifact hardening | functional-spec, kanban-board, erd-preview | Static checks miss UX defects | Real interaction confidence | Browser test maintenance | Stable fixtures | Headless scenarios pass |

### Phase 4: Quality Automation

| Work | Target | Reason | Expected effect | Risk | Prerequisite | Completion criterion |
|---|---|---|---|---|---|---|
| Extend repository validator | Manifests/agents/docs | Prevent structural regression | Fast deterministic CI | False positives | Stable schemas | Fixture tests for every rule |
| Prompt selection fixtures | Cross-skill triggers | Static metadata cannot prove routing | Detect overlap/conflict | Model nondeterminism | Scenario corpus | Stable rubric and bounded retries |
| Prompt behavior fixtures | Core skills | Structure does not prove completion | Known failure regression | Cost/time | Representative fixtures | Minimum required assertions per skill |
| Link/reference graph | Entire repo | Moves can leave stale references | Safer refactors | Code examples misclassified | Parser rules | Live links/paths all resolve |
| Release CI | Version/docs/dist | Manual release synchronization | Repeatable release | Generated churn | Validator stable | Version parity and clean generated diff |

## Change Record

### Created

- `plugins/elian-store/agents/engineering-reviewer.md`: canonical
  capability-enforced read-only engineering reviewer.
- `scripts/validate_repository.py`: repository contract validator.
- `tests/test_repository_validation.py`: validator regression suite.
- `.github/workflows/validate-repository.yml`: pull-request/main validation.
- `docs/repository-wide-ai-skills-audit.md`: durable audit and migration record.

### Modified

| File/group | Baseline problem | Change | Reason | Impact |
|---|---|---|---|---|
| Side-effect skill frontmatter | Automatic mutation possible | Added invocation gates, narrowed tools | Safety | Artifact/design/maintenance skills |
| `decision-dashboard/SKILL.md` | Wildcard deletion | Removed delete permission and changed finalization contract | Prevent data loss | Dashboard artifacts |
| `review` and `pr-review` | Read-only only by prose | Route engineering lenses to engineering-reviewer | Enforce capability | Review workflows |
| `persona-*-reviewer.md` | Bash exposed | Removed Bash and shell instructions | Enforce read-only | 15 persona agents |
| TDD triad | Required unbundled helpers | Direct review/test flow; optional host handoffs | Self-contained core path | implement/fix/improve |
| `pr-writer/SKILL.md` | Draft/create ambiguity | Draft-only contract | Avoid remote mutation | PR/MR authoring |
| `tools/clusters.json`, `tools/generate.py` | Ambiguous Codex omissions | Added deferred disposition and overlap validation | Accurate parity | Codex distribution |
| Codex config and shipped docs/templates | English policy drift | Translated current distribution content | Repository rule compliance | Codex/spec/design/artifacts |
| Metadata/docs | Version and counts stale | Bumped 3.1.1 and synchronized guidance | Release correctness | Marketplace/install users |

### Moved

- None. The first pass avoids path churn.

### Deleted

- None. No file was deleted without a confirmed unreferenced status.

## Post-change Verification

| Check | Status | Evidence/limitation |
|---|---|---|
| Repository structural validator | Verified | `python3 scripts/validate_repository.py` |
| Validator unit tests | Verified | Ten unittest fixtures |
| Cluster/Codex generation plan | Verified | `python3 tools/generate.py`; all 14 shared links resolve |
| Skill-owned validators | Verified | All nine `validate_skill.py` entry points after contract updates |
| spec-coverage self-test | Verified | 12 bundled checks |
| document-writer self-test | Verified | Bundled `--selftest` |
| update hook self-test | Verified | `check-update.sh --selftest` |
| YAML frontmatter parse | Verified | Ruby safe-load across skills and agents |
| JSON and source syntax | Verified | Repository validator plus JSON parse |
| Internal Markdown links | Static verification complete | Fenced examples excluded; external URLs not fetched |
| Manifest-to-file references | Static verification complete | Cluster, agent, skill, and Codex paths |
| Common secret/private-key patterns | Static verification complete | No source hits outside ignored/generated output |
| Shell-injection patterns | Static verification complete | Hits are labeled BAD examples in `security-engineer.md`; implementation subprocess calls use argument arrays |
| Browser interaction/layout | Additional confirmation needed | No headless browser regression suite yet |
| External GitHub/GitLab/JIRA/MCP behavior | Environment-dependent, not tested | Outside repository-only scope |
| Prompt semantic quality | Additional confirmation needed | Scenario analysis complete; automated semantic fixtures remain |

## Final Conclusions

1. **Core skills to retain:** `brainstorm`, `intake-spec`, `design-feature` as a
   thinner orchestrator, `design-ui`, `functional-spec`, the TDD triad,
   `review`, the verification lane, `create-document`, and the explicit
   artifact generators.
2. **Skills to consolidate internally:** share implementation policy across
   `implement`/`fix`/`improve`; share reviewer/evidence contracts across
   `review`/`pr-review`; share one artifact graph across
   `design-feature`/`update-design`. Keep their public names separate.
3. **Delete or legacy:** delete no active skill. Treat `.claude/plans` as an
   archive candidate and keep maintainer-only workflow/skill content explicitly
   separated from plugin distribution.
4. **First Critical/High fixes:** wildcard deletion and automatic side effects,
   read-only capability mismatches, optional-host assumptions, ambiguous Codex
   omissions, and absent repository CI. These are fixed in v3.1.1.
5. **Is the current structure extensible?** Moderately. The cluster manifest and
   self-contained skill directories scale, but prose-only contracts and large
   orchestrators will make the next wave of skills expensive.
6. **Before adding a new skill:** introduce the manifest standard, extract
   repeated execution/evidence policy, and reduce the 496-line teammate entry
   point.
7. **Recommended development standard:** one public responsibility, explicit
   required/optional inputs, versioned structured outputs, explicit failure and
   idempotency behavior, least-privilege tools, side-effect gate, direct
   repository fallback, fixtures for normal/error paths, and CI validation of
   IDs/links/manifests/parity.
8. **One-sentence summary:** keep the portfolio, enforce its safety and contracts
   mechanically, and refactor repeated orchestration behind stable public skill
   boundaries.

**Final rating: Major skill redesign needed.** The repository does not require a
blank-slate rewrite: its public taxonomy and deterministic assets are worth
preserving. The rating is driven by design-feature's responsibility breadth,
near-limit orchestrators, repeated TDD/review policy, prose-only input/output
contracts, and missing semantic/browser regression coverage.
