# elian-claude-plugins

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/Elian-Studio/elian-claude-plugins?label=release)](https://github.com/Elian-Studio/elian-claude-plugins/releases)
[![Plugin: elian-store](https://img.shields.io/badge/plugin-elian--store-blue)](plugins/elian-store/)

This repository ships `elian-store`, a Claude Code plugin marketplace bundle, plus a separate Codex CLI prompt/config tree.

Start here:

- Install the Claude plugin if you want the bundled skills, agents, and hooks.
- Open [plugins/elian-store/README.md](plugins/elian-store/README.md) for the plugin-local operating guide.
- Open [codex/README.md](codex/README.md) for the Codex companion tree.
- Open [docs/claude-codex-skill-parity.md](docs/claude-codex-skill-parity.md) when you need the current parity state.

This repo intentionally has two distribution surfaces:

- **Claude Code plugin**: install `elian-store` from this marketplace. This is the primary product.
- **Codex CLI config**: copy selected prompts/config from `codex/`. This is an independent companion tree, not a generated mirror.

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

Install or update the independent Codex prompt/config files:

```shell
mkdir -p ~/.codex/prompts
rm -f ~/.codex/prompts/on-call-elian.md
cp codex/prompts/*.md ~/.codex/prompts/
```

Optional project/global defaults:

```shell
cp codex/AGENTS.md ~/.codex/AGENTS.md
cp codex/config.toml.example ~/.codex/config.toml
```

Codex currently ships reference `/review`, `/brainstorm`, `/ai-assisted-feature-development`, `/design-ui`, `/decision-dashboard`, `/create-document`, `/implement`, `/fix`, `/improve`, `/manage-skills`, `/verify-implementation`, `/generate-teammate`, and `/persona-review` prompts. See [codex/README.md](codex/README.md).

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
| [generate-teammate](plugins/elian-store/skills/generate-teammate/) | Decide direct/subagent/team execution and render teammate prompts. | `/elian-store:generate-teammate` |
| [create-document](plugins/elian-store/skills/create-document/) | Render schema-validated JSON into HTML/Markdown templates. | `/elian-store:create-document` |
| [document-writer](plugins/elian-store/skills/document-writer/) | Turn arbitrary content into a self-contained, house-styled HTML (or Markdown) document. | `/elian-store:document-writer` |
| [persona-review](plugins/elian-store/skills/persona-review/) | Review plans/docs/ideas through selected persona lenses in each persona's native style. | `/elian-store:persona-review` |

### Codex Companion Tree

Path: [codex/](codex/)

| File | Role |
|---|---|
| [codex/prompts/ai-assisted-feature-development.md](codex/prompts/ai-assisted-feature-development.md) | Reference Codex prompt for `/ai-assisted-feature-development`. |
| [codex/prompts/create-document.md](codex/prompts/create-document.md) | Reference Codex prompt for `/create-document`. |
| [codex/prompts/brainstorm.md](codex/prompts/brainstorm.md) | Reference Codex prompt for `/brainstorm`. |
| [codex/prompts/implement.md](codex/prompts/implement.md) | Reference Codex prompt for `/implement`. |
| [codex/prompts/fix.md](codex/prompts/fix.md) | Reference Codex prompt for `/fix`. |
| [codex/prompts/improve.md](codex/prompts/improve.md) | Reference Codex prompt for `/improve`. |
| [codex/prompts/manage-skills.md](codex/prompts/manage-skills.md) | Reference Codex prompt for `/manage-skills`. |
| [codex/prompts/verify-implementation.md](codex/prompts/verify-implementation.md) | Reference Codex prompt for `/verify-implementation`. |
| [codex/prompts/generate-teammate.md](codex/prompts/generate-teammate.md) | Reference Codex prompt for `/generate-teammate`. |
| [codex/prompts/decision-dashboard.md](codex/prompts/decision-dashboard.md) | Reference Codex prompt for `/decision-dashboard`. |
| [codex/prompts/design-ui.md](codex/prompts/design-ui.md) | Reference Codex prompt for `/design-ui`. |
| [codex/prompts/review.md](codex/prompts/review.md) | Reference Codex prompt for `/review`. |
| [codex/prompts/persona-review.md](codex/prompts/persona-review.md) | Reference Codex prompt for `/persona-review`. |
| [codex/AGENTS.md](codex/AGENTS.md) | Codex project/global instruction template. |
| [codex/config.toml.example](codex/config.toml.example) | Safe read-only-oriented Codex config sample. |

The Claude and Codex trees are intentionally independent. When behavior changes in both, update both explicitly and record parity status in [docs/claude-codex-skill-parity.md](docs/claude-codex-skill-parity.md).

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
docs/                               # Architecture, parity, and roadmap docs
```

Important distinction:

- `.claude-plugin/marketplace.json` is the marketplace entrypoint.
- `plugins/elian-store/.claude-plugin/plugin.json` is the installed plugin manifest.
- `codex/` is not part of the Claude plugin install.
- `.claude/` is local Claude settings/state and is not the plugin source of truth.

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
| Change portfolio roadmap | `docs/plugin-portfolio-hybrid-model.md` and `docs/gstack-skill-review.md` |
| Change Claude/Codex parity | `docs/claude-codex-skill-parity.md` |

Version rule: plugin-distributed behavior changes require updating `plugin.json`, root marketplace metadata, README, and CHANGELOG together.

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
