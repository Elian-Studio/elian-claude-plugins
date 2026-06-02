# Claude Skill / Plugin Audit

Date: 2026-05-28

## Scope

Compare this repository's Claude plugin and skill documentation against:

- Claude Code Skills docs: https://code.claude.com/docs/en/skills
- Claude Code Plugins docs: https://code.claude.com/docs/en/plugins
- Claude Code Plugin marketplace docs: https://code.claude.com/docs/en/plugin-marketplaces
- Claude Code Plugins reference: https://code.claude.com/docs/en/plugins-reference
- alirezarezvani/claude-skills: https://github.com/alirezarezvani/claude-skills
- alirezarezvani Skill Authoring Standard: https://github.com/alirezarezvani/claude-skills/blob/main/SKILL-AUTHORING-STANDARD.md
- alirezarezvani Conventions: https://github.com/alirezarezvani/claude-skills/blob/main/CONVENTIONS.md

## Reference Findings

### Claude Code Skills

- A skill is a `<skill-name>/SKILL.md` package. The body loads only when invoked, while the description is used for discovery.
- Plugin skills are invoked as `/plugin-name:skill-name`; for skills under a plugin `skills/` directory, the directory name is the command name.
- Frontmatter fields are optional, but `description` is recommended. Claude Code currently supports optional fields such as `when_to_use`, `argument-hint`, `allowed-tools`, `disable-model-invocation`, `user-invocable`, `context`, `agent`, `hooks`, and `paths`.
- `description + when_to_use` is capped in the skill listing. Keep the key use case first and move procedure details into the body or supporting files.
- Supporting files should be referenced from `SKILL.md`. Keep `SKILL.md` under 500 lines and move large examples, API details, templates, and scripts into separate files.
- `allowed-tools` grants pre-approval for matching tools while the skill is active; it is not a deny-list. Use permission settings for denial.
- Side-effect workflows should usually set `disable-model-invocation: true` so the model cannot auto-trigger them.

### Claude Code Plugins / Marketplaces

- `.claude-plugin/plugin.json` defines plugin identity and optional component paths. `name` is the only required manifest field if a manifest exists.
- Only plugin metadata belongs inside `.claude-plugin/`. `skills/`, `agents/`, `hooks/`, `.mcp.json`, `.lsp.json`, and other components live at the plugin root.
- A marketplace catalog lives at root `.claude-plugin/marketplace.json`; plugin entries require `name` and `source`.
- `plugin.json.version` wins over marketplace `version` and acts as the update cache key. If a plugin declares an explicit version, changing files without bumping that version does not reach installed users through `/plugin update`.

### alirezarezvani/claude-skills

- The project is a large multi-tool skill marketplace. It packages skills with `SKILL.md`, stdlib Python tools, and reference docs, then distributes them through marketplace/plugin metadata and conversion scripts.
- Its Skill Authoring Standard emphasizes context-first behavior, practitioner voice, multi-mode workflows, related-skill navigation, reference separation, proactive triggers, output artifacts, quality loops, and stdlib-only Python tools.
- Its standard says `SKILL.md` should be a compact workflow/navigation file and heavy material should move into `references/`, `templates/`, and `scripts/`; it gives a 10KB target.
- Its `CONVENTIONS.md` is stricter than current Claude Code docs and says only `name` and `description` are allowed in `SKILL.md` frontmatter. This conflicts with current Claude Code support for optional fields. For this repository, use Claude Code docs as the compatibility baseline and treat alirezarezvani's stricter rule as a portability profile, not as the local rule.

## Current Repository Assessment

### Already Aligned

- Plugin layout is broadly correct: `plugins/elian-store/.claude-plugin/plugin.json`, `plugins/elian-store/skills/*/SKILL.md`, root `.claude-plugin/marketplace.json`.
- The plugin is a single bundle, which matches the current repo strategy and avoids one plugin per skill.
- The current skill set has `references/` and `scripts/` coverage, and `SKILL.md` frontmatter is expected to pass an actual YAML parse smoke test.
- Most side-effect workflows use `disable-model-invocation: true`.

### Problems Found

- README listed fewer skills than the actual `plugins/elian-store/skills/` directory.
- The independent Codex port still used the removed `on-call-elian` command name even though the Claude plugin skill had been renamed to `persona-review`.
- Marketplace and plugin descriptions were too long for discovery surfaces and repeated detailed release history.
- CONTRIBUTING still contained stale validation examples from the old standalone `decision-dashboard` layout.
- CONTRIBUTING did not explain the important official rule that `plugin.json.version` wins and must be bumped for installed users to receive updates.
- Several frontmatter descriptions carried procedure-level detail that belongs in the body, not in the always-visible skill listing.
- `persona-review` had no explicit `Modes` section, making its quick/deep/interview behavior harder to scan.
- Earlier local quality guidance cited alirezarezvani as a simple rule source without explaining the conflict between its stricter conventions and current Claude Code optional frontmatter support.

## Applied Changes

- Updated plugin and marketplace metadata to concise discovery text.
- Bumped marketplace and plugin version to `2.7.1` because plugin-distributed documentation changed.
- Updated README skill inventory to match all 12 bundled skills.
- Renamed the Codex prompt to `codex/prompts/persona-review.md` and aligned README, CONTRIBUTING, codex README, and Codex prompt rubric references.
- Updated CONTRIBUTING with current validation paths and explicit Claude skill/plugin operating rules.
- Updated local quality guidance to document the source-priority rule and the official optional-frontmatter baseline.
- Shortened high-noise frontmatter descriptions for:
  - `ai-assisted-feature-development`
  - `create-document`
  - `design-ui`
  - `persona-review`
- Added an explicit `Modes` section to `persona-review`.

## Ongoing Rules

- Use official Claude Code docs as the compatibility baseline.
- Use alirezarezvani/claude-skills as an operating-pattern reference, especially for progressive disclosure, stdlib tools, references, and marketplace discipline.
- Keep `description` short and trigger-oriented; move procedure detail to the body.
- Keep `when_to_use` trigger-rich but under the combined listing cap.
- Quote frontmatter strings that contain YAML control syntax such as `: `, bracket-style argument hints, or long trigger lists. YAML/frontmatter smoke tests should catch unsafe plain scalars before PR merge.
- Keep each `SKILL.md` under 500 lines and target 10KB where practical.
- Bump `plugin.json.version`, marketplace version, README, and CHANGELOG together for plugin-distributed changes.
- Keep generated artifacts out of plugin docs unless they are the requested deliverable or canonical examples.
