# elian-claude-plugins

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/Elian-Studio/elian-claude-plugins?label=release)](https://github.com/Elian-Studio/elian-claude-plugins/releases)
[![Plugin: elian-store](https://img.shields.io/badge/plugin-elian--store-blue)](plugins/elian-store/)
[![Plugin: elian-workflow](https://img.shields.io/badge/plugin-elian--workflow-blue)](plugins/elian-workflow/)

This repository ships two Claude Code plugins — `elian-store` (workflow bundle) and `elian-workflow` (issue-cycle work history) — plus a separate Codex CLI prompt/config tree and a small Claude workflows distribution tree.

Start here:

- Install `elian-store` for the bundled skills, agents, and hooks; `elian-workflow` if you record issue history to Notion.
- Open [plugins/elian-store/README.md](plugins/elian-store/README.md) or [plugins/elian-workflow/README.md](plugins/elian-workflow/README.md) for the plugin-local operating guides.
- Open [codex/README.md](codex/README.md) for the Codex companion tree.
- Open [.claude/workflows/README.md](.claude/workflows/README.md) for the Claude Workflow-tool scripts.
- Open [docs/claude-codex-skill-parity.md](docs/claude-codex-skill-parity.md) when you need the current parity state.

This repo intentionally has three distribution surfaces:

- **Claude Code plugins**: install `elian-store` and/or `elian-workflow` from this marketplace. These are the primary product.
- **Codex CLI config**: copy selected prompts/config from `codex/`. This is an independent companion tree, not a generated mirror.
- **Claude workflows**: copy Workflow-tool `.js` scripts from `.claude/workflows/` into `~/.claude/workflows/`. Plugins cannot register workflows, so these are distributed by copy (like `codex/`).

For the full structure and edit map, see [docs/repository-operating-map.md](docs/repository-operating-map.md).

---

## Install

### Claude Code

```shell
/plugin marketplace add Elian-Studio/elian-claude-plugins
/plugin install elian-store@elian
```

The marketplace ships two plugins. Install either or both — they are independent.

```shell
/plugin install elian-store@elian       # workflow bundle: design, TDD, review, verification
/plugin install elian-workflow@elian    # issue-cycle work history recorded to Notion
```

`elian-workflow` needs one local setup step before it does anything: a Notion MCP server and a
`~/.claude/notion-workspace.json` describing your databases. The skills build that file with
you on first run by inspecting your live databases — nothing about any particular workspace is
baked into the plugin. Skip the install if you do not use Notion.

Update later:

```shell
/plugin marketplace update elian
/plugin update elian-store@elian
/plugin update elian-workflow@elian
```

If you prefer Claude Code's native marketplace auto-update behavior, enable marketplace/plugin
auto-update in your Claude Code settings. Both plugins use `plugin.json.version` as the
installed update cache key, so installed users receive plugin-content releases when Claude Code
performs marketplace auto-update. Keep the manual commands above for explicit refreshes or when
auto-update is disabled.

On SessionStart, `elian-store` also checks for updates once every 24 hours. When it finds a newer
version, the next session shows the update command plus a short CHANGELOG excerpt when the release
notes are reachable. The same hook records installed versions and can run versioned migrations from
`plugins/elian-store/migrations/vX.Y.Z.sh` after future upgrades.

Claude invocation format:

```text
/elian-store:<skill-name>
```

Example:

```text
/elian-store:review worktree --depth deep
```

For the bundled plugin guide, use [plugins/elian-store/README.md](plugins/elian-store/README.md).

### Codex CLI

Install or update the independent Codex skill/prompt/config files:

```shell
# Skills (shared with the Claude plugin via symlink, updated by `git pull`)
./codex/setup.sh

# Legacy prompts
mkdir -p ~/.codex/prompts
rm -f ~/.codex/prompts/on-call-elian.md
cp codex/prompts/*.md ~/.codex/prompts/
```

Optional project/global defaults:

```shell
cp codex/AGENTS.md ~/.codex/AGENTS.md
cp codex/config.toml.example ~/.codex/config.toml
```

Codex ships **12 shared skills** (`codex/skills/`, symlinked into the plugin tree so they never
drift) plus **2 reference prompts** — `/generate-teammate` and `/persona-review`, which stay
prompts because their core is Claude subagent dispatch that Codex cannot reproduce. Two skills
are runtime-blocked Claude-only and six portable skills are explicitly deferred; see
[codex/README.md](codex/README.md) and the
[parity record](docs/claude-codex-skill-parity.md).

### Claude Workflows

Copy the Workflow-tool scripts into your user config:

```shell
mkdir -p ~/.claude/workflows
cp .claude/workflows/*.js ~/.claude/workflows/
```

Then invoke from Claude Code, e.g. `/harness-legacy-scan`. See [.claude/workflows/README.md](.claude/workflows/README.md).

---

## What Ships

### Claude Plugin: `elian-store`

Path: [plugins/elian-store/](plugins/elian-store/)

`elian-store` is the bundled workflow plugin. One install gives all its skills, agents, and hooks.

| Skill | Purpose | Invocation |
|---|---|---|
| [intake-spec](plugins/elian-store/skills/intake-spec/) | Provider-agnostic requirements front door. Works without any issue tracker; optionally links to GitHub, GitLab, or JIRA. Produces `spec.json` for `/design-feature`. | `/elian-store:intake-spec` |
| [design-feature](plugins/elian-store/skills/design-feature/) | Self-contained design orchestrator. Generates design.md, architecture, a non-developer PRD **and its developer-facing `tech-spec.md` counterpart** (requirement → implementation mapping, AC-ID cross-checked against the PRD), API spec, QA checklist, and a Mermaid-capable roadmap hub (index.html) through five gated phases. When a `ddl.sql` is produced, Phase 3 optionally emits an interactive `erd-preview.html` lineage explorer from it. Roadmap tasks support an optional product-facing `features[]` capability checklist and a `dropped` status (with `reason`) for recording descoped work. | `/elian-store:design-feature` |
| [brainstorm](plugins/elian-store/skills/brainstorm/) | Clarify fuzzy thoughts and surface criteria before committing to a direction. | `/elian-store:brainstorm` |
| [decision-dashboard](plugins/elian-store/skills/decision-dashboard/) | Turn 3+ blocking decisions into a printable HTML + downstream JSON artifact. | `/elian-store:decision-dashboard` |
| [implement](plugins/elian-store/skills/implement/) | Build new features through approval-gated TDD. | `/elian-store:implement` |
| [fix](plugins/elian-store/skills/fix/) | Repair bugs through root-cause analysis and regression-test-first TDD. | `/elian-store:fix` |
| [improve](plugins/elian-store/skills/improve/) | Make behavior-changing improvements with BEFORE/AFTER evidence. | `/elian-store:improve` |
| [review](plugins/elian-store/skills/review/) | Perform read-only engineering review of code, diffs, PRs, or changed files with findings-first output. | `/elian-store:review` |
| [verify-implementation](plugins/elian-store/skills/verify-implementation/) | Discover and run project verify-* skills before shipping. | `/elian-store:verify-implementation` |
| [spec-coverage](plugins/elian-store/skills/spec-coverage/) | Track requirement coverage during implementation: seed a leaf checklist from the design docs (AC, scenarios, API, state transitions, schema, open decisions), then decide each item from **actual test results** — an acceptance criterion is `pass` only when a passing test carries its `R#-AC#` ID. Criteria with no test at all stay `unchecked`, which is the "PRD not yet satisfied" signal. | `/elian-store:spec-coverage` |
| [manage-skills](plugins/elian-store/skills/manage-skills/) | Detect and repair verify-skill drift after code changes. | `/elian-store:manage-skills` |
| [generate-teammate](plugins/elian-store/skills/generate-teammate/) | Decide direct/subagent/team execution (cheaper-first prior + cost gate + post-parallel integration check) and render teammate prompts. | `/elian-store:generate-teammate` |
| [create-document](plugins/elian-store/skills/create-document/) | Render schema-validated JSON into HTML/Markdown templates. | `/elian-store:create-document` |
| [document-writer](plugins/elian-store/skills/document-writer/) | Turn arbitrary content into a self-contained, house-styled HTML (or Markdown) document. | `/elian-store:document-writer` |
| [persona-review](plugins/elian-store/skills/persona-review/) | Auto-select matching expert personas (frontend, UX, a11y, API, domain, scale, code, business, marketing, ops) from the target and review in each persona's native style. | `/elian-store:persona-review` |
| [harness-manager](plugins/elian-store/skills/harness-manager/) | Detect and reconcile drift between the Codex and Claude Code global harnesses (rules, MCP, commands, skills). | `/elian-store:harness-manager` |
| [pr-writer](plugins/elian-store/skills/pr-writer/) | Draft a review-friendly PR/MR title and body from the diff, commits, and stated intent (GitHub `gh` / GitLab `glab` aware). | `/elian-store:pr-writer` |
| [pr-review](plugins/elian-store/skills/pr-review/) | Review an existing PR/MR through a panel of specialist + persona perspectives, synthesize one verdict, and post to the PR only on confirmation. | `/elian-store:pr-review` |
| [verify-before-claiming](plugins/elian-store/skills/verify-before-claiming/) | Claim-time honesty gate — require fresh verification evidence before any pass/fixed/done claim. | `/elian-store:verify-before-claiming` |
| [respond-to-review](plugins/elian-store/skills/respond-to-review/) | Consumer side of review — verify feedback before implementing, no performative agreement, push back with reasoning. | `/elian-store:respond-to-review` |
| [update-design](plugins/elian-store/skills/update-design/) | Design-change propagation orchestrator — runs an impact matrix across existing `/design-feature` docs and updates only the affected ones. | `/elian-store:update-design` |
| [erd-preview](plugins/elian-store/skills/erd-preview/) | Turn a schema + real rows into a single self-contained "Lineage Explorer" HTML: click a record to trace its lineage (upstream FK ancestors → downstream impacts), with hard-FK (solid) vs soft-reference (dashed) links, an ancestors/impacts summary panel, and a Figma-style zoom/pan viewer. Fills a validated template from a live read-only DB, DDL, design docs, or pasted query results. | `/elian-store:erd-preview` |

### Claude Plugin: `elian-workflow`

Path: [plugins/elian-workflow/](plugins/elian-workflow/)

Issue-cycle bookends that record engineering work history to Notion. Development work has three
nested cycles — commit, issue, day — and this plugin owns the **issue** cycle: the one that
carries the decisions, architecture, and remaining checks that a diff can never show.

Workspace-agnostic by construction. Every database id, property name, and status value comes
from a local config file (`~/.claude/notion-workspace.json`, or `.claude/notion-workspace.json`
per repository) that the skill helps you build on first run by reading your live databases.
Nothing about any particular Notion workspace is baked into the skills.

| Skill | Purpose | Invocation |
|---|---|---|
| [issue-open](plugins/elian-workflow/skills/issue-open/) | Start an issue: verify the branch upstream points at itself, move the task to in-progress with a start date, report whether design documents and open decisions exist, and seed the issue page body with the metadata and background that are only clear at kickoff. Never creates, switches, or deletes a branch. | `/elian-workflow:issue-open` |
| [issue-close](plugins/elian-workflow/skills/issue-close/) | Close an issue: interview for the design decisions and dropped alternatives that code cannot show, upsert a readable narrative into the issue page body under section-scoped supersede rules, backfill commits missing from the audit log, transition status, and render a before/after HTML viewer. Recording only — it never merges, pushes, or deletes. | `/elian-workflow:issue-close` |

### Codex Companion Tree

Path: [codex/](codex/)

| File | Role |
|---|---|
| [codex/setup.sh](codex/setup.sh) | Installs `codex/skills/*` into `~/.codex/skills` as symlinks (idempotent). |
| [codex/skills/](codex/skills/) | 12 shared skills — symlinks into `plugins/elian-store/skills/<name>/`, generated/lint-checked by `tools/generate.py`. |
| [codex/prompts/generate-teammate.md](codex/prompts/generate-teammate.md) | Reference prompt for `/generate-teammate` — subagent-core, stays a prompt. |
| [codex/prompts/persona-review.md](codex/prompts/persona-review.md) | Reference prompt for `/persona-review` — subagent-core, stays a prompt. |
| [codex/AGENTS.md](codex/AGENTS.md) | Codex project/global instruction template. |
| [codex/config.toml.example](codex/config.toml.example) | Safe read-only-oriented Codex config sample. |

Shared skills read one host-agnostic `SKILL.md` and cannot drift between the trees. Only the two
subagent-core prompts (`generate-teammate`, `persona-review`) are independent files that must be
kept in sync by hand. Two skills are Claude-only because of runtime constraints
(`harness-manager`, `pr-review`), and six portable skills are
explicitly deferred (`document-writer`, `intake-spec`, `design-feature`, `update-design`,
`erd-preview`, `spec-coverage`). Parity status is tracked in
[docs/claude-codex-skill-parity.md](docs/claude-codex-skill-parity.md).

### Claude Workflows

Path: [.claude/workflows/](.claude/workflows/)

| Workflow | Command | Role |
|---|---|---|
| [harness-legacy-scan.js](.claude/workflows/harness-legacy-scan.js) | `/harness-legacy-scan [project-path]` | Read-only audit of your AI coding harness (global `~/.claude` + `~/.codex`, optionally a project); classifies findings KEEP/SHRINK/MOVE/SPLIT/CONVERT/DELETE. |

Workflow-tool scripts are not plugin components, so they are distributed by copying into `~/.claude/workflows/`. See [.claude/workflows/README.md](.claude/workflows/README.md).

---

## Repository Map

```text
.claude-plugin/
  marketplace.json                 # Claude marketplace catalog
plugins/
  elian-store/                     # Workflow bundle plugin
    README.md                      # Plugin-local usage guide
    .claude-plugin/plugin.json      # Plugin metadata and version
    agents/                         # Plugin-bundled Claude agents
    hooks/                          # Plugin hooks
    skills/_shared/                 # Documents shared by sibling skills in this plugin
    skills/<skill>/                 # Skill packages
      SKILL.md
      scripts/
      references/
  elian-workflow/                  # Issue-cycle work-history plugin
    README.md
    .claude-plugin/plugin.json
    skills/_shared/                 # Narrative template + workspace config schema
    skills/<skill>/
codex/                              # Independent Codex CLI companion tree
  prompts/
  AGENTS.md
  config.toml.example
.claude/
  workflows/                         # Workflow-tool .js, copied into ~/.claude/workflows/
  skills/                            # Maintainer-only dev skills (not distributed)
docs/                               # Architecture, parity, and roadmap docs
```

Important distinction:

- `.claude-plugin/marketplace.json` is the marketplace entrypoint and lists every plugin.
- Each `plugins/<name>/.claude-plugin/plugin.json` is that plugin's installed manifest. Its
  `version` is the update cache key and wins over the marketplace entry, so the two must move
  together — `scripts/validate_repository.py` enforces this for every plugin, not just the bundle.
- A relative path inside a skill (`../_shared/x.md`) cannot cross a plugin boundary; a plugin is
  copied as a unit. Cross-plugin dependencies must be skill invocations, not file references.
- `codex/` is not part of the Claude plugin install.
- `.claude/workflows/` is a copy-distributed Workflow-tool tree (not a plugin component); `.claude/skills/` is maintainer-only dev tooling; `.claude/settings.local.json` is local state. None are the plugin source of truth.

---

## Where To Edit

| Task | Edit |
|---|---|
| Change a Claude skill | `plugins/<plugin>/skills/<skill>/SKILL.md` and its `references/` or `scripts/` |
| Add a Claude skill | new `plugins/<plugin>/skills/<skill>/`, then update that plugin's metadata, marketplace metadata, README, CHANGELOG, and parity docs |
| Change issue-cycle / Notion behavior | `plugins/elian-workflow/skills/issue-{open,close}/SKILL.md` |
| Change the issue-history format | `plugins/elian-workflow/skills/_shared/narrative-template.md` |
| Change plugin-local usage guide | `plugins/<plugin>/README.md` |
| Change plugin install metadata | `plugins/<plugin>/.claude-plugin/plugin.json` (bump with the marketplace entry) |
| Change marketplace catalog metadata | `.claude-plugin/marketplace.json` |
| Change Codex prompt behavior | `codex/prompts/<command>.md` |
| Change Codex setup guidance | `codex/README.md`, `codex/AGENTS.md`, or `codex/config.toml.example` |
| Change a Claude workflow | `.claude/workflows/<name>.js` (keep it portable — no machine-specific paths/inventory) |
| Add a Claude workflow | new `.claude/workflows/<name>.js` + row in `.claude/workflows/README.md`, root README, and CHANGELOG |
| Change portfolio roadmap | `docs/plugin-portfolio-hybrid-model.md` and `docs/gstack-skill-review.md` |
| Change Claude/Codex parity | `docs/claude-codex-skill-parity.md` |

Version rule: plugin-distributed behavior changes require updating `plugin.json`, the marketplace `elian-store` entry version (not the root `metadata.version`), README, and CHANGELOG together.

---

## Validate

There is no repository-wide numeric score gate. The repository validator checks structural
contracts, tool safety, links, distribution language, cluster registration, Codex disposition,
version parity, and source syntax. Skill-owned validators still test skill-specific semantics.

```shell
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
python3 tools/generate.py
ruby -EUTF-8 -ryaml -e 'Dir.glob("plugins/*/skills/*/SKILL.md").sort.each { |p| s=File.read(p, encoding: "UTF-8"); YAML.safe_load(s.split(/^---\s*$/,3)[1] || "", permitted_classes: [], aliases: false); puts "OK #{p}" }'
```

The globs say `plugins/*`, not `plugins/elian-store` — the repository ships more than one
plugin, and a check scoped to the bundle silently skips the others.

When changing a skill, validate it. Skills owning a bespoke validator run their own:

```shell
python3 plugins/elian-store/skills/review/scripts/validate_skill.py
```

`brainstorm`, `fix`, `implement`, and `improve` share one structural validator (they used to
carry four byte-identical copies), which takes the skill directories as arguments:

```shell
python3 tools/validate_skill.py plugins/elian-store/skills/implement
```

Every validator — shared and bespoke — is built on `tools/skill_check.py`, which owns the
frontmatter parser (the same one `scripts/validate_repository.py` uses), the reusable checks,
and the `--json` / `--quiet` report. A skill-owned validator declares only what is specific to
its skill.

---

## Operating Model

The repo follows a hybrid model:

- Anthropic-style marketplace/plugin boundary.
- Vercel-style self-contained skill packages with scripts and references.
- gstack-style lifecycle portfolio planning.

See [docs/plugin-portfolio-hybrid-model.md](docs/plugin-portfolio-hybrid-model.md).

Current high-priority gaps:

1. `browser-qa` or `qa`
2. `ship`
3. `learn` or `retro`

---

## Releases

Full change history: [CHANGELOG.md](CHANGELOG.md).

For v1.x users:

```shell
/plugin uninstall decision-dashboard@elian
/plugin install elian-store@elian
```

The old standalone invocation changed:

```text
/decision-dashboard:decision-dashboard -> /elian-store:decision-dashboard
```

---

## License

MIT. See [LICENSE](LICENSE).
