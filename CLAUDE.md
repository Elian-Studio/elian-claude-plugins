# CLAUDE.md

Claude Code plugin marketplace shipping two plugins — `plugins/elian-store/` (bundled workflow skills, agents, hooks) and `plugins/elian-workflow/` (issue-cycle work-history recording to Notion) — plus an independent Codex CLI distribution tree (`codex/`). Process details live in CONTRIBUTING.md — this file holds only the facts that prevent mistakes.

## Rules

- English only: repository docs, `SKILL.md` bodies, `when_to_use`, trigger phrases, references, templates, and Codex files. No Korean trigger phrases — Korean usage is served by slash commands and conversation context. This repository is English-only even where user-level settings prefer Korean.
- Never push to `main`; pull requests only. `main` still requires the orphaned status check "Evaluate skills (90+ required)" whose workflow was removed, so merges currently need admin override.
- Claude and Codex are two independent trees with no single source of truth. When changing a command in one tree (`plugins/elian-store/skills/` ↔ `codex/prompts/`), check the other tree in the same PR, or document the exception in `docs/claude-codex-skill-parity.md`.
- Skills with side effects default to `disable-model-invocation: true`. Keep `SKILL.md` under 500 lines and `description + when_to_use` under 1,536 characters.

## Release convention

Any user-visible plugin change must bump all of these together — without a `plugin.json` version bump, installed users receive nothing (`plugin.json.version` is the update cache key and wins over the marketplace entry):

- `plugins/elian-store/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json` (`elian-store` entry)
- `README.md`, `CHANGELOG.md`

`codex/` changes are versioned independently and do not require a plugin version bump.

## Validation (run before opening a PR)

Every glob below says `plugins/*`, never `plugins/elian-store`. The repository ships more than one plugin, and a check scoped to the bundle skips the others silently — that gap let a second plugin drift its version and carry non-English content undetected until v4.1.0.

```bash
# Repository-wide static contract check, regression tests, cluster manifest + lint
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
python3 tools/generate.py

# SKILL.md frontmatter YAML smoke test
ruby -EUTF-8 -ryaml -e 'Dir.glob("plugins/*/skills/*/SKILL.md").sort.each { |p| s=File.read(p, encoding: "UTF-8"); YAML.safe_load(s.split(/^---\s*$/,3)[1] || "", permitted_classes: [], aliases: false); puts "OK #{p}" }'

# plugin / marketplace JSON parse check
ruby -rjson -e '[".claude-plugin/marketplace.json", *Dir.glob("plugins/*/.claude-plugin/plugin.json")].each { |p| JSON.parse(File.read(p)); puts "OK #{p}" }'
```

Also validate the changed skill. Skills owning a bespoke validator run their own (e.g. `python3 plugins/elian-store/skills/review/scripts/validate_skill.py`); `brainstorm`, `fix`, `implement`, and `improve` share `python3 plugins/elian-store/skills/_shared/validate_skill.py <skill-dir>`. It sits inside the plugin rather than in `tools/` because `tools/` is not distributed, and a command a shipped `SKILL.md` documents must resolve in an installed plugin too.
