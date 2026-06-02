# codex/ - OpenAI Codex CLI Companion Tree

This tree is an independent Codex CLI distribution bundle. It is separate from the Claude Code marketplace tree under `plugins/`.

| | Claude Code | Codex CLI |
|---|---|---|
| Entry point | `plugins/elian-store/skills/*/SKILL.md` with YAML frontmatter | `codex/prompts/*.md`, plain Markdown, filename = slash command |
| Project guidance | `CLAUDE.md` + `.claude/` | `AGENTS.md` + `~/.codex/config.toml` |
| Permission model | Frontmatter `allowed-tools` | `config.toml` `approval_policy` / `sandbox_mode` |
| Distribution | Installed through marketplace metadata | Copied or symlinked into `~/.codex/` by the user |
| Validation | YAML/frontmatter smoke test + skill-owned validator | Prompt/config/parity review |

## Drift Warning

This repository intentionally uses an independent two-tree model. There is no single source of truth. `codex/prompts/ai-assisted-feature-development.md`, `codex/prompts/brainstorm.md`, `codex/prompts/create-document.md`, `codex/prompts/decision-dashboard.md`, `codex/prompts/design-ui.md`, `codex/prompts/fix.md`, `codex/prompts/generate-teammate.md`, `codex/prompts/improve.md`, `codex/prompts/implement.md`, `codex/prompts/manage-skills.md`, `codex/prompts/review.md`, `codex/prompts/verify-implementation.md`, `codex/prompts/persona-review.md`, and their Claude counterparts are separate files. When one side changes, the author must check the other side manually.

Forgetting one side can make Claude and Codex behave differently. Pull requests should inspect both diffs when a command exists in both trees.

## Install

```bash
# 1) Custom prompts, available as slash commands in Codex
mkdir -p ~/.codex/prompts
rm -f ~/.codex/prompts/on-call-elian.md
cp codex/prompts/*.md ~/.codex/prompts/

# 2) Optional project/global guidance
cp codex/AGENTS.md ~/.codex/AGENTS.md

# 3) Optional global config sample
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
  prompts/
    ai-assisted-feature-development.md
    brainstorm.md
    create-document.md
    decision-dashboard.md
    design-ui.md
    fix.md
    generate-teammate.md
    improve.md
    implement.md
    manage-skills.md
    review.md
    verify-implementation.md
    persona-review.md
  config.toml.example
```

Current porting scope: `ai-assisted-feature-development`, `brainstorm`, `create-document`, `decision-dashboard`, `design-ui`, `fix`, `generate-teammate`, `improve`, `implement`, `manage-skills`, `review`, `verify-implementation`, and `persona-review`. Other `elian-store` skills should be added gradually after the pattern is proven.

Claude/Codex catalog parity status and porting order are tracked in [`../docs/claude-codex-skill-parity.md`](../docs/claude-codex-skill-parity.md).
