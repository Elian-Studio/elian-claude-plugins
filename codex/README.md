# codex/ - OpenAI Codex CLI Companion Tree

This tree is an independent Codex CLI distribution bundle. It is separate from the Claude Code marketplace tree under `plugins/`.

| | Claude Code | Codex CLI |
|---|---|---|
| Entry point | `plugins/elian-store/skills/*/SKILL.md` with YAML frontmatter | `codex/skills/*/SKILL.md` (Agent Skills standard, shared with Claude) and legacy `codex/prompts/*.md` (plain Markdown, filename = slash command) |
| Project guidance | `CLAUDE.md` + `.claude/` | `AGENTS.md` + `~/.codex/config.toml` |
| Permission model | Frontmatter `allowed-tools` | `config.toml` `approval_policy` / `sandbox_mode` |
| Distribution | Installed through marketplace metadata | Copied or symlinked into `~/.codex/` by the user |
| Validation | YAML/frontmatter smoke test + skill-owned validator | Prompt/config/parity review |

## Drift Warning

This repository uses an independent two-tree model for **prompts**. Each legacy `codex/prompts/*.md` (`ai-assisted-feature-development`, `brainstorm`, `fix`, `generate-teammate`, `improve`, `implement`, `manage-skills`, `persona-review`, `pr-writer`, `review`, `verify-implementation`) and its Claude counterpart are separate files. When one side changes, the author must check the other side manually.

Forgetting one side can make Claude and Codex behave differently. Pull requests should inspect both diffs when a command exists in both trees.

> **Migrated skills do not drift.** `create-document`, `decision-dashboard`, and `design-ui` now
> ship once as skills: each `codex/skills/<name>` is a symlink into
> `plugins/elian-store/skills/<name>/`, so both tools read the same `SKILL.md` (made host-agnostic —
> no `CLAUDE_PLUGIN_ROOT`/`CLAUDE_SKILL_DIR` hard dependency). Migrated skills are exempt from the
> manual two-side check above. `generate-teammate` keeps its prompt for now: its `SKILL.md` is also
> host-agnostic, but the teammate-spawn flow cannot be reproduced on Codex (handoff-only). See
> [`../docs/claude-codex-skill-parity.md`](../docs/claude-codex-skill-parity.md).

## Install

```bash
# 1) Skills (Agent Skills standard) — symlinked from this repo, updated by `git pull`.
#    Each codex/skills/<name> is a symlink into the shared plugin tree, so there is no
#    duplicated content and migrated skills never drift between Claude and Codex.
./codex/setup.sh                    # install all skills under codex/skills/
# ./codex/setup.sh create-document  # or install a subset

# 2) Legacy custom prompts, available as slash commands in Codex
mkdir -p ~/.codex/prompts
rm -f ~/.codex/prompts/on-call-elian.md
cp codex/prompts/*.md ~/.codex/prompts/

# 3) Optional project/global guidance
cp codex/AGENTS.md ~/.codex/AGENTS.md

# 4) Optional global config sample
cp codex/config.toml.example ~/.codex/config.toml
```

After installation, use this command in Codex TUI:

```text
/ai-assisted-feature-development <feature-name> [--risk low|medium|high] [--depth full|design-only|task-only|review-only] [--example login|payment|upload|search]
/brainstorm <topic> [--depth shallow|deep] [--output plan|doc|none]
/create-document --template <name> --data <json-path> --out <out-path> [--schema <name>] [--json]
/decision-dashboard [issue-id] [--mode generate|finalize]
/design-ui <feature-name> [--out <dir>] [--skip-gate] [--from-brief <path>] [--refs <url,url,...>]
/implement <issue-id> [--side back|front|both] [--step N] [--skip-docs]
/fix <issue-id> [--side back|front|both] [--step N] [--skip-docs]
/improve <issue-id> [--side back|front|both] [--step N] [--skip-docs]
/manage-skills [skill-name | focus-area | question]
/verify-implementation [optional verify skill name]
/generate-teammate <project description or task requirements>
/review <target> [--depth quick|deep] [--lenses security,performance,quality,design,adversarial]
/persona-review <target> [--persona daniel|evans|dean|martin|all|comma-list|<path>] [--depth quick|deep|interview]
```

## Structure

```text
codex/
  README.md
  AGENTS.md
  setup.sh                 # installs codex/skills/* into ~/.codex/skills (symlinks)
  skills/                  # each entry is a symlink into ../../plugins/elian-store/skills/<name>
    create-document
    decision-dashboard
    design-ui
  prompts/
    ai-assisted-feature-development.md
    brainstorm.md
    fix.md
    generate-teammate.md
    improve.md
    implement.md
    manage-skills.md
    persona-review.md
    pr-writer.md
    review.md
    verify-implementation.md
  config.toml.example
```

Current porting scope (prompts): `ai-assisted-feature-development`, `brainstorm`, `fix`, `generate-teammate`, `improve`, `implement`, `manage-skills`, `persona-review`, `pr-writer`, `review`, and `verify-implementation`. `create-document`, `decision-dashboard`, and `design-ui` have graduated from prompts to **shared skills** (`codex/skills/`). `generate-teammate` is host-agnostic at the `SKILL.md` level but stays a prompt (Codex cannot reproduce its teammate-spawn flow). Remaining prompts follow the same skill-symlink pattern gradually.

Claude/Codex catalog parity status and porting order are tracked in [`../docs/claude-codex-skill-parity.md`](../docs/claude-codex-skill-parity.md).
