# Contributing

Use this guide when changing this marketplace or preparing a pull request.

## Workflow

```text
1. Create a branch: feature/<scope> or fix/<scope>
2. Change SKILL.md, plugin.json, marketplace.json, Codex files, or docs
3. Run local checks: parser smoke tests, changed-skill validators, and relevant examples/templates
4. Open a pull request
5. Review and merge
6. Publish a GitHub Release when needed
```

Do not push directly to `main`. All changes should go through a pull request.

## Validation Principles

This repository does not use a repository-wide numeric score gate. The previous self-scoring approach only checked structural signals, which was not enough to prove document quality or operational fit.

Documentation language: write repository documents, skill bodies, references, templates, and Codex companion files in English. Current compatibility decision: do not keep Korean trigger phrases in `SKILL.md`, `when_to_use`, references, templates, or examples. Use slash commands and English trigger phrases for discovery.

Use these checks instead:

- **Repository contract check**: run `python3 scripts/validate_repository.py`.
- **Parse check**: ensure Claude `SKILL.md` frontmatter parses as real YAML.
- **Skill-owned validator**: when the changed skill has a validator such as `scripts/validate_skill.py`, run it.
- **Artifact check**: confirm templates, schemas, examples, and references still match the workflow.
- **Purpose review**: review the skill purpose, non-use boundary, output contract, and side-effect posture.
- **Parity review**: when a command exists in both Claude and Codex trees, compare both purpose and output contracts.

## Local Checks

Run the repository contract validator and its regression tests first:

```bash
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
```

Smoke test all `SKILL.md` frontmatter:

```bash
ruby -EUTF-8 -ryaml -e 'Dir["plugins/elian-store/skills/*/SKILL.md"].sort.each { |p| s=File.read(p, encoding: "UTF-8"); YAML.safe_load(s.split(/^---\s*$/,3)[1] || "", permitted_classes: [], aliases: false); puts "OK #{p}" }'
```

Parse plugin and marketplace metadata:

```bash
ruby -rjson -e '[".claude-plugin/marketplace.json","plugins/elian-store/.claude-plugin/plugin.json"].each { |p| JSON.parse(File.read(p)); puts "OK #{p}" }'
```

Examples of skill-owned validators:

```bash
python3 plugins/elian-store/skills/review/scripts/validate_skill.py
python3 plugins/elian-store/skills/persona-review/scripts/validate_skill.py
```

When adding a validator, prefer stdlib-only scripts when practical and include automation-friendly options such as `--json` or `--quiet` when useful. Build it on `tools/skill_check.py` — it provides the frontmatter parser, `CheckResult`, the reusable checks, and the `--json` / `--quiet` report, so a new validator only declares the checks specific to its skill. A script that runs on a *user's* machine rather than in this checkout cannot import `tools/` (it is not installed); shared parsing for those lives in `plugins/elian-store/skills/_shared/scripts/skill_md.py`.

## Claude Skill And Plugin Rules

Claude Code official docs are the compatibility baseline. External repositories are operating-pattern references. If references conflict, prefer the official docs and this repository's current intent.

- `SKILL.md` frontmatter: `description` is the official recommended field. This repository also prefers explicit `name`, `argument-hint`, and `allowed-tools` fields for discoverability and maintainability.
- Quote `description`, `when_to_use`, and `argument-hint` values when they contain YAML-sensitive syntax such as `: `, brackets, quotes, or long trigger lists.
- Keep trigger phrases in English. Korean user phrasing is supported by conversation context and slash commands, not by embedding Korean compatibility exceptions in repository documents.
- Keep `description + when_to_use` under the official skill listing cap of 1,536 characters. Put the key use case first and move procedure detail into the body or `references/`.
- Workflows with side effects should default to `disable-model-invocation: true`. Auto-invocable skills should be limited to low-impact read or document-generation behavior.
- Keep `SKILL.md` under the official 500-line limit and target roughly 10 KB where practical. Move long examples and domain details into `references/`, repeated output forms into `templates/`, and deterministic checks into `scripts/`.
- Plugin layout: `.claude-plugin/` contains only `plugin.json`. Components such as `skills/`, `agents/`, `hooks/`, `.mcp.json`, and `.lsp.json` live at the plugin root.
- Marketplace layout: root `.claude-plugin/marketplace.json` is the catalog, and plugin content lives under `plugins/elian-store/`.
- Version rule: when `plugin.json.version` exists, it wins over the marketplace entry version and acts as the update cache key. Plugin-distributed changes should update `plugin.json`, root marketplace metadata, `README.md`, and `CHANGELOG.md` together.

## Single Bundle Plugin Model

This marketplace ships one bundled plugin, `elian-store`, with multiple skills. Users install once and receive the whole bundle. New skills are delivered through `/plugin update elian-store@elian`.

```text
plugins/elian-store/
|-- .claude-plugin/
|   `-- plugin.json
|-- agents/
|-- hooks/
`-- skills/
    |-- review/
    |   |-- SKILL.md
    |   |-- scripts/
    |   `-- references/
    `-- ...
```

## Add A New Skill

1. Create `plugins/elian-store/skills/<new-skill>/SKILL.md`.
2. Add `references/`, `scripts/`, `templates/`, or `schemas/` in the same skill directory when needed.
3. Document the skill purpose, non-use boundary, output contract, and side-effect posture in `SKILL.md`.
4. Bump `plugins/elian-store/.claude-plugin/plugin.json` version.
5. Bump the `elian-store` entry version in `.claude-plugin/marketplace.json`.
6. Update `README.md`, `CHANGELOG.md`, and relevant parity or portfolio docs.
7. Register the skill in `tools/clusters.json`: add it to exactly one plugin's `skills` array, and set its Codex disposition (`codex.claude_only`, `codex.prompt_only`, or `codex.deferred`; omit all three only when it ships as a `codex/skills/<name>` symlink). This is easy to miss — `README`/`CHANGELOG`/parity docs get attention, but the machine manifest does not, and an unregistered skill makes validation fail.
8. Run `python3 scripts/validate_repository.py` and its unit tests.
9. Run `python3 tools/generate.py` and confirm it exits 0 (manifest + bare-`CLAUDE_*` lint + version consistency + `codex/skills` symlink status).
10. Run YAML smoke tests and any skill-owned validators.
11. Open a pull request, review, and merge.

Adding a completely separate plugin requires a separate pull request and a separate guide. The current default is one bundled plugin.

## Claude vs Codex

This repository uses two independent trees. There is no single source of truth.

| | Claude Code | Codex CLI |
|---|---|---|
| Tree | `plugins/elian-store/skills/*/SKILL.md` | `codex/prompts/*.md` |
| Entry format | YAML frontmatter + Markdown | Markdown, filename = slash command, `$ARGUMENTS` |
| Project guidance | `CLAUDE.md` / `.claude/` | `codex/AGENTS.md` / `~/.codex/config.toml` |
| Permission model | Frontmatter `allowed-tools` | `config.toml` `approval_policy` / `sandbox_mode` |
| Validation | YAML smoke test + skill-owned validator + review | Prompt review + config review + parity review |

Rules:

1. When changing behavior in one tool tree, the pull request author is responsible for checking the other tree.
2. If the same command exists in both trees, inspect both diffs in the same pull request.
3. A new Claude skill should include a matching Codex prompt or a documented exception in `docs/claude-codex-skill-parity.md`.
4. `codex/` changes are independent of the `elian-store` plugin version because `codex/` is a sibling distribution tree, not a Claude marketplace plugin.
5. Use `docs/plugin-portfolio-hybrid-model.md` for portfolio-level decisions.

## Maintainer Setup

Branch protection should focus on blocking direct pushes and requiring pull requests. This repository no longer requires a self-scoring status check.

GitHub UI example:

```text
Settings -> Branches -> Add branch ruleset
- Branch name pattern: main
- Require a pull request before merging: enabled
- Block force pushes: enabled
- Require branches to be up to date before merging: project preference
- Require status checks: only real tests/checks that currently exist
```

## Release Process

1. Merge the pull request.
2. If `plugin.json.version` changed, existing installed users can receive the update.
3. Publish a GitHub Release.

```bash
gh release create vX.Y.Z \
  --target main \
  --title "vX.Y.Z - <one-line summary>" \
  --notes "$(cat <<'NOTES'
## Summary
...
## Plugin changes
- elian-store `vX.Y.Z` - ...
NOTES
)"
```

If `plugin.json.version` stays the same, pushing new commits does not update existing installed users. Any user-visible plugin-distributed change should include a version bump.

## Directory Structure

```text
elian-claude-plugins/
|-- .claude-plugin/
|   `-- marketplace.json
|-- .github/
|   |-- pull_request_template.md
|   `-- workflows/validate-repository.yml
|-- plugins/
|   `-- elian-store/
|       |-- .claude-plugin/
|       |   `-- plugin.json
|       |-- agents/
|       |-- hooks/
|       `-- skills/
|           `-- <skill>/
|               |-- SKILL.md
|               |-- scripts/
|               `-- references/
|-- codex/
|   |-- README.md
|   |-- AGENTS.md
|   |-- prompts/
|-- scripts/
|   `-- validate_repository.py
|-- tests/
|   `-- test_repository_validation.py
|   `-- config.toml.example
|-- docs/
|-- CHANGELOG.md
|-- CONTRIBUTING.md
|-- LICENSE
`-- README.md
```

## License

MIT. Keep the root `LICENSE` and each plugin's `plugin.json.license` field aligned.
