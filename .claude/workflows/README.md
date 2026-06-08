# .claude/workflows/ — Claude Code Workflow Distribution Tree

This directory ships reusable **Workflow-tool workflows** — the JavaScript scripts the Claude Code
Workflow tool discovers from `~/.claude/workflows/*.js` and exposes as slash commands.

It is **not** part of the `elian-store` plugin. Claude Code plugins cannot register workflows (a
plugin ships skills / agents / hooks / MCP / LSP / monitors / themes / bin / settings only), so —
like `codex/` — these files are distributed by **copying them into your user config**, not through
the marketplace.

> Naming: the directory mirrors its install destination (`~/.claude/workflows/`) so the copy
> command is obvious, and the `.claude/` prefix keeps it from being confused with
> `.github/workflows/` (which is GitHub Actions CI, a completely different thing run by GitHub).

## What Ships

| Workflow | Command | What it does | Writes files? |
|---|---|---|---|
| [`harness-legacy-scan.js`](harness-legacy-scan.js) | `/harness-legacy-scan [project-path]` | Read-only audit of your AI coding harness (global `~/.claude` + `~/.codex`, optionally a project). Four phases — Inventory → Analyze (context-tax / skill-quality / product-overlap / safety) → Classify → adversarial Challenge — classifying each finding KEEP / SHRINK / MOVE / SPLIT / CONVERT / DELETE. | No (read-only) |

The workflow discovers the current environment at runtime; it has no machine-specific paths baked
in. Pass an optional project root as the argument to also audit that project's `CLAUDE.md` /
`AGENTS.md` / `.claude/`.

## Install

```bash
mkdir -p ~/.claude/workflows
cp .claude/workflows/*.js ~/.claude/workflows/
```

Then invoke from Claude Code:

```text
/harness-legacy-scan                 # audit the global harness (+ cwd project if present)
/harness-legacy-scan ~/path/to/repo  # also audit that project's harness files
```

Update later by re-copying after `git pull`.

## Not Included

`harness-diet` (the companion that *applies* low-risk legacy-scan findings) is intentionally **not**
distributed here. The existing implementation is a one-time replay hard-coded to a specific machine
and audit run, not a reusable tool; a portable, report-driven version is future work. Until then,
treat `harness-legacy-scan` as read-only audit only.

## Authoring Notes

- A workflow file must begin with `export const meta = { name, description, phases }` (a pure
  literal), where `meta.name` equals the filename without `.js`.
- The body runs inside the Workflow runtime, which injects `agent()`, `parallel()`, `pipeline()`,
  `phase()`, `log()`, `args`, and `budget`, and allows top-level `await` and a top-level `return`.
  (Plain `node --check` flags the top-level `return` — that is expected; validate by wrapping the
  body in an `async function` first.)
- Keep these scripts portable: discover the environment at runtime, never bake in absolute paths,
  a personal skill/MCP inventory, or one run's findings.
