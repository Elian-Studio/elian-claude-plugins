# elian-claude-plugins

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/Elian-Studio/elian-claude-plugins?label=release)](https://github.com/Elian-Studio/elian-claude-plugins/releases)
[![Plugin: elian-store](https://img.shields.io/badge/plugin-elian--store-blue)](plugins/elian-store/)

This repository ships `elian-store`, a Claude Code plugin marketplace bundle, plus a separate Codex CLI prompt/config tree and a small Claude workflows distribution tree.

Start here:

- Install the Claude plugin if you want the bundled skills, agents, and hooks.
- Open [plugins/elian-store/README.md](plugins/elian-store/README.md) for the plugin-local operating guide.
- Open [codex/README.md](codex/README.md) for the Codex companion tree.
- Open [.claude/workflows/README.md](.claude/workflows/README.md) for the Claude Workflow-tool scripts.
- Open [docs/claude-codex-skill-parity.md](docs/claude-codex-skill-parity.md) when you need the current parity state.

This repo intentionally has three distribution surfaces:

- **Claude Code plugin**: install `elian-store` from this marketplace. This is the primary product.
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

Update later:

```shell
/plugin marketplace update elian
/plugin update elian-store@elian
```

If you prefer Claude Code's native marketplace auto-update behavior, enable marketplace/plugin
auto-update in your Claude Code settings. `elian-store` already uses `plugin.json.version` as the
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

Codex ships **13 shared skills** (`codex/skills/`, symlinked into the plugin tree so they never drift) plus **2 reference prompts** — `/generate-teammate` and `/persona-review`, which stay prompts because their core is Claude subagent dispatch that Codex cannot reproduce. (`document-writer`, `harness-manager`, and `pr-review` are Claude-only.) See [codex/README.md](codex/README.md).

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

`elian-store` is a single bundled Claude Code plugin. One install gives all bundled skills, agents, and hooks.

| Skill | Purpose | Invocation |
|---|---|---|
| [brainstorm](plugins/elian-store/skills/brainstorm/) | Clarify fuzzy thoughts and surface criteria before committing to a direction. | `/elian-store:brainstorm` |
| [decision-dashboard](plugins/elian-store/skills/decision-dashboard/) | Turn 3+ blocking decisions into a printable HTML + downstream JSON artifact. | `/elian-store:decision-dashboard` |
| [ai-assisted-feature-development](plugins/elian-store/skills/ai-assisted-feature-development/) | Structure AI-assisted feature work through framing, specs, tests, context, tasks, review, and archive. | `/elian-store:ai-assisted-feature-development` |
| [design-ui](plugins/elian-store/skills/design-ui/) | Produce UI/UX design artifacts through interview, references, wireframe, gate, visual, and delivery. | `/elian-store:design-ui` |
| [implement](plugins/elian-store/skills/implement/) | Build new features through approval-gated TDD. | `/elian-store:implement` |
| [fix](plugins/elian-store/skills/fix/) | Repair bugs through root-cause analysis and regression-test-first TDD. | `/elian-store:fix` |
| [improve](plugins/elian-store/skills/improve/) | Make behavior-changing improvements with BEFORE/AFTER evidence. | `/elian-store:improve` |
| [review](plugins/elian-store/skills/review/) | Perform read-only engineering review of code, diffs, PRs, or changed files with findings-first output. | `/elian-store:review` |
| [verify-implementation](plugins/elian-store/skills/verify-implementation/) | Discover and run project verify-* skills before shipping. | `/elian-store:verify-implementation` |
| [manage-skills](plugins/elian-store/skills/manage-skills/) | Detect and repair verify-skill drift after code changes. | `/elian-store:manage-skills` |
| [generate-teammate](plugins/elian-store/skills/generate-teammate/) | Decide direct/subagent/team execution (cheaper-first prior + cost gate + post-parallel integration check) and render teammate prompts. | `/elian-store:generate-teammate` |
| [create-document](plugins/elian-store/skills/create-document/) | Render schema-validated JSON into HTML/Markdown templates. | `/elian-store:create-document` |
| [document-writer](plugins/elian-store/skills/document-writer/) | Turn arbitrary content into a self-contained, house-styled HTML (or Markdown) document. | `/elian-store:document-writer` |
| [persona-review](plugins/elian-store/skills/persona-review/) | Auto-select matching expert personas (frontend, UX, a11y, API, domain, scale, code, business, marketing, ops) from the target and review in each persona's native style. | `/elian-store:persona-review` |
| [harness-manager](plugins/elian-store/skills/harness-manager/) | Detect and reconcile drift between the Codex and Claude Code global harnesses (rules, MCP, commands, skills). | `/elian-store:harness-manager` |
| [pr-writer](plugins/elian-store/skills/pr-writer/) | Draft a review-friendly PR/MR title and body from the diff, commits, and stated intent (GitHub `gh` / GitLab `glab` aware). | `/elian-store:pr-writer` |
| [pr-review](plugins/elian-store/skills/pr-review/) | Review an existing PR/MR through a panel of specialist + persona perspectives, synthesize one verdict, and post to the PR only on confirmation. | `/elian-store:pr-review` |
| [skill-dispatcher](plugins/elian-store/skills/skill-dispatcher/) | Opt-in router that recommends the smallest relevant `elian-store` skill before work starts. | `/elian-store:skill-dispatcher` |
| [verify-before-claiming](plugins/elian-store/skills/verify-before-claiming/) | Claim-time honesty gate — require fresh verification evidence before any pass/fixed/done claim. | `/elian-store:verify-before-claiming` |
| [respond-to-review](plugins/elian-store/skills/respond-to-review/) | Consumer side of review — verify feedback before implementing, no performative agreement, push back with reasoning. | `/elian-store:respond-to-review` |
| [finish-branch](plugins/elian-store/skills/finish-branch/) | Decide how to finish a branch (merge / push+PR / keep / discard) with worktree-safe cleanup; delegates the release flow to `/ship`. | `/elian-store:finish-branch` |

### Codex Companion Tree

Path: [codex/](codex/)

| File | Role |
|---|---|
| [codex/setup.sh](codex/setup.sh) | Installs `codex/skills/*` into `~/.codex/skills` as symlinks (idempotent). |
| [codex/skills/](codex/skills/) | 13 shared skills — symlinks into `plugins/elian-store/skills/<name>/`, generated/lint-checked by `tools/generate.py`. |
| [codex/prompts/generate-teammate.md](codex/prompts/generate-teammate.md) | Reference prompt for `/generate-teammate` — subagent-core, stays a prompt. |
| [codex/prompts/persona-review.md](codex/prompts/persona-review.md) | Reference prompt for `/persona-review` — subagent-core, stays a prompt. |
| [codex/AGENTS.md](codex/AGENTS.md) | Codex project/global instruction template. |
| [codex/config.toml.example](codex/config.toml.example) | Safe read-only-oriented Codex config sample. |

Shared skills read one host-agnostic `SKILL.md` and cannot drift between the trees. Only the two
subagent-core prompts (`generate-teammate`, `persona-review`) are independent files that must be
kept in sync by hand; the three Claude-only skills (`document-writer`, `harness-manager`, `pr-review`)
have no Codex counterpart at all. Parity status is tracked in [docs/claude-codex-skill-parity.md](docs/claude-codex-skill-parity.md).

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
  elian-store/                     # Primary Claude plugin
    README.md                      # Plugin-local usage guide
    .claude-plugin/plugin.json      # Plugin metadata and version
    agents/                         # Plugin-bundled Claude agents
    hooks/                          # Plugin hooks
    skills/<skill>/                 # Skill packages
      SKILL.md
      scripts/
      references/
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

- `.claude-plugin/marketplace.json` is the marketplace entrypoint.
- `plugins/elian-store/.claude-plugin/plugin.json` is the installed plugin manifest.
- `codex/` is not part of the Claude plugin install.
- `.claude/workflows/` is a copy-distributed Workflow-tool tree (not a plugin component); `.claude/skills/` is maintainer-only dev tooling; `.claude/settings.local.json` is local state. None are the plugin source of truth.

---

## Where To Edit

| Task | Edit |
|---|---|
| Change a Claude skill | `plugins/elian-store/skills/<skill>/SKILL.md` and its `references/` or `scripts/` |
| Add a Claude skill | new `plugins/elian-store/skills/<skill>/`, then update plugin metadata, marketplace metadata, README, CHANGELOG, and parity docs |
| Change plugin-local usage guide | `plugins/elian-store/README.md` |
| Change plugin install metadata | `plugins/elian-store/.claude-plugin/plugin.json` |
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

There is no repository-wide numeric score gate. Use concrete checks instead: parse metadata, run the validator owned by the changed skill, and review purpose/boundaries manually.

```shell
ruby -EUTF-8 -ryaml -e 'Dir["plugins/elian-store/skills/*/SKILL.md"].sort.each { |p| s=File.read(p, encoding: "UTF-8"); YAML.safe_load(s.split(/^---\s*$/,3)[1] || "", permitted_classes: [], aliases: false); puts "OK #{p}" }'
```

When changing a skill, run that skill's self-validator when present:

```shell
python3 plugins/elian-store/skills/review/scripts/validate_skill.py
```

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
