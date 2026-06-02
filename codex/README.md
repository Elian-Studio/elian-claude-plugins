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

This repository intentionally uses an independent two-tree model. There is no single source of truth. `codex/prompts/persona-review.md` and `plugins/elian-store/skills/persona-review/SKILL.md` are separate files. When one side changes, the author must check the other side manually.

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
/persona-review <target> [--persona daniel|evans|dean|martin|all|comma-list|<path>] [--depth quick|deep|interview]
```

## Structure

```text
codex/
  README.md
  AGENTS.md
  prompts/
    persona-review.md
  config.toml.example
```

Current porting scope: `persona-review` only. Other `elian-store` skills should be added gradually after the pattern is proven.

Claude/Codex catalog parity status and porting order are tracked in [`../docs/claude-codex-skill-parity.md`](../docs/claude-codex-skill-parity.md).
