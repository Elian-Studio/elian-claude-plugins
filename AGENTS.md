# AGENTS.md — Working on this repository (Codex & other agents)

Contributor guardrails for anyone working **on** the `elian-claude-plugins` marketplace itself.
`CLAUDE.md` at the repo root is the canonical source; this file mirrors the must-not-break rules
so a Codex agent — which reads `AGENTS.md` from the working directory upward — gets them too.
When the two ever differ, **`CLAUDE.md` wins**: update it, then reflect the change here.

> Not to be confused with `codex/AGENTS.md`, which is a *shippable* Codex behavior template that
> end users copy to `~/.codex/AGENTS.md`. That file is distribution content; this one governs
> development of the repo.

## Hard rules

- English only: repo docs, `SKILL.md` bodies, `when_to_use`, trigger phrases, references,
  templates, and Codex files. No Korean trigger phrases — Korean usage is served by slash commands
  and conversation context. English-only even where user-level settings prefer Korean.
- Never push to `main`; pull requests only. `main` carries an orphaned required check
  ("Evaluate skills (90+ required)") whose workflow was removed, so merges currently need admin override.
- Two independent trees, no single source of truth. When you change a command in one tree
  (`plugins/elian-store/skills/` ↔ `codex/prompts/`), check the other in the same PR, or record
  the exception in `docs/claude-codex-skill-parity.md`.
- Release bump: any user-visible plugin change must update `plugins/elian-store/.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json` (`elian-store` entry), `README.md`, and `CHANGELOG.md` together.
  `codex/` is versioned independently. See `CLAUDE.md` for the full procedure and the pre-PR validation commands.
- Skills with side effects default to `disable-model-invocation: true`. Keep each `SKILL.md` under
  500 lines and its `description` + `when_to_use` under 1,536 characters (the character limit is hard-enforced).
