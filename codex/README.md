# codex/ - OpenAI Codex CLI Companion Tree

This tree is an independent Codex CLI distribution bundle. It is separate from the Claude Code marketplace tree under `plugins/`.

| | Claude Code | Codex CLI |
|---|---|---|
| Entry point | `plugins/elian-store/skills/*/SKILL.md` with YAML frontmatter | `codex/skills/*/SKILL.md` (Agent Skills standard, shared with Claude) and `codex/prompts/*.md` platform adapters |
| Project guidance | `CLAUDE.md` + `.claude/` | `AGENTS.md` + `~/.codex/config.toml` |
| Permission model | Frontmatter `allowed-tools` | `config.toml` `approval_policy` / `sandbox_mode` |
| Distribution | Installed through marketplace metadata | Copied or symlinked into `~/.codex/` by the user |
| Validation | Repository validator + YAML/frontmatter + skill-owned validator | Repository validator + prompt/config/parity review |

## Drift model

Most commands ship as **shared skills**: `codex/skills/<name>` is a symlink into
`plugins/elian-store/skills/<name>/`, so Claude and Codex read the same host-agnostic `SKILL.md`
and **cannot drift**. The shared set is whatever `tools/clusters.json` does not mark
`claude_only`, `prompt_only`, or `deferred`; `tools/generate.py` maintains the symlinks and
lints every `SKILL.md` for host-agnostic script paths.

Two commands stay hand-authored `codex/prompts/*.md` because their core is **Claude subagent
dispatch**, which Codex cannot reproduce:
- `generate-teammate` — teammate-spawn / subagent team flow (handoff-only on Codex).
- `persona-review` — per-persona subagent dispatch + aggregation.

For these two only, the Codex prompt and the Claude `SKILL.md` are separate files; a change on one
side must be checked against the other. Three skills are runtime-blocked **Claude-only**
(`harness-manager`, `pr-review`, `finish-branch`) and seven portable skills are
explicitly **deferred** (`document-writer`, `intake-spec`, `design-feature`, `update-design`,
`erd-preview`, `kanban-board`, `spec-coverage`). Everything else is a drift-free shared skill. See
[`../docs/claude-codex-skill-parity.md`](../docs/claude-codex-skill-parity.md).

## Install

```bash
# 1) Skills (Agent Skills standard) — symlinked from this repo, updated by `git pull`.
#    Each codex/skills/<name> is a symlink into the shared plugin tree, so there is no
#    duplicated content and migrated skills never drift between Claude and Codex.
./codex/setup.sh                    # install all skills under codex/skills/
# ./codex/setup.sh create-document  # or install a subset

# 2) Hand-authored platform prompts, available as slash commands in Codex
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
/brainstorm <topic> [--depth shallow|deep] [--output plan|doc|none]
/create-document --template <name> --data <json-path> --out <out-path> [--schema <name>] [--json]
/decision-dashboard [issue-id] [--mode generate|finalize]
/design-ui <feature-name> [--out <dir>] [--skip-gate] [--from-brief <path>] [--refs <url,url,...>]
/functional-spec <wireframe-paths...> [--out <dir>]
/implement <issue-id> [--side back|front|both] [--step N] [--skip-docs]
/fix <issue-id> [--side back|front|both] [--step N] [--skip-docs]
/improve <issue-id> [--side back|front|both] [--step N] [--skip-docs]
/manage-skills [skill-name | focus-area | question]
/verify-implementation [optional verify skill name]
/verify-before-claiming
/respond-to-review <review feedback>
/generate-teammate <project description or task requirements>
/review <target> [--depth quick|deep] [--lenses security,performance,quality,design,adversarial]
/persona-review <target> [--persona daniel|evans|dean|martin|all|comma-list|<path>] [--depth quick|deep|interview]
/pr-writer [optional PR/MR intent or ticket]
```

## Structure

```text
codex/
  README.md
  AGENTS.md
  setup.sh                 # installs codex/skills/* into ~/.codex/skills (symlinks)
  skills/                  # symlinks into ../../plugins/elian-store/skills/<name>
    ...                    # shared skills (14; see tools/clusters.json)
  prompts/
    generate-teammate.md   # subagent-core — stays a prompt
    persona-review.md      # subagent-core — stays a prompt
  config.toml.example
```

The `skills/` symlinks are generated and lint-checked by `tools/generate.py` from the
`tools/clusters.json` manifest — run it instead of editing `codex/skills/` by hand. The Codex
catalog is **14 shared skills + 2 prompts** (`generate-teammate`, `persona-review`); three
runtime-blocked and seven deferred skills do not appear here.

Claude/Codex catalog parity status and porting order are tracked in [`../docs/claude-codex-skill-parity.md`](../docs/claude-codex-skill-parity.md).
