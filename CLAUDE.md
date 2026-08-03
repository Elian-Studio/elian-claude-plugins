# CLAUDE.md

Claude Code plugin marketplace shipping one plugin — `plugins/elian-store/` (the full bundle: 24 skills, 30 agents, hooks) — plus an independent Codex CLI distribution tree (`codex/`). `plugins/elian-workflow/` is deprecated as of 3.0.0: it ships generated copies of `issue-open` and `issue-close` only, so earlier installs keep working. Process details live in CONTRIBUTING.md — this file holds only the facts that prevent mistakes.

## Rules

- English only: repository docs, `SKILL.md` bodies, `when_to_use`, trigger phrases, references, templates, and Codex files. No Korean trigger phrases — Korean usage is served by slash commands and conversation context. This repository is English-only even where user-level settings prefer Korean.
- Never push to `main`; pull requests only. The orphaned status check "Evaluate skills (90+ required)" no longer blocks — PR #45 merged without an admin override on 2026-08-03.
- Claude and Codex are two independent trees with no single source of truth. When changing a command in one tree (`plugins/elian-store/skills/` ↔ `codex/prompts/`), check the other tree in the same PR, or document the exception in `docs/claude-codex-skill-parity.md`.
- Skills with side effects default to `disable-model-invocation: true`. Keep `SKILL.md` under 500 lines and `description + when_to_use` under 1,536 characters.
- **`plugins/elian-store/skills/` is the source of truth for every skill.** Nothing under `plugins/elian-workflow/skills/` is hand-authored — all 5 files there are generated copies. Editing one is wasted work: the next `python3 tools/generate.py --sync` reverts it, and `validate_repository.py`'s `composed-parity` check fails first. `tools/clusters.json` → `published` declares what is copied.
- A plugin is copied as a unit at install time, so no path may leave its plugin root — not a `../` link, and not a `${CLAUDE_PLUGIN_ROOT}/skills/<other>` bash reference. Enforced by the `plugin-self-containment` check. This is also why two plugins cannot share a skill without physically duplicating it, which is what made `elian-workflow` 2.0.0 a mistake worth not repeating.

## Release convention

Any user-visible plugin change must bump all of these together — without a `plugin.json` version bump, installed users receive nothing (`plugin.json.version` is the update cache key and wins over the marketplace entry):

- `plugins/<plugin>/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json` (that plugin's entry)
- `README.md`, `CHANGELOG.md`

A change to a skill `elian-workflow` also ships (`issue-open`, `issue-close`, and the two shared documents they read) is a release of **both** plugins — run `--sync` and bump both.

`codex/` changes are versioned independently and do not require a plugin version bump.

## Validation (run before opening a PR)

Every glob below says `plugins/*`, never `plugins/elian-store`. The repository ships more than one plugin, and a check scoped to the bundle skips the others silently — that gap let a second plugin drift its version and carry non-English content undetected until v4.1.0.

```bash
# Repository-wide static contract check, regression tests, cluster manifest + lint
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
python3 tools/generate.py

# After changing any skill/agent that a composed plugin ships, refresh its copies.
# validate_repository.py fails on drift, so run this before re-running it.
python3 tools/generate.py --sync

# SKILL.md frontmatter YAML smoke test
ruby -EUTF-8 -ryaml -e 'Dir.glob("plugins/*/skills/*/SKILL.md").sort.each { |p| s=File.read(p, encoding: "UTF-8"); YAML.safe_load(s.split(/^---\s*$/,3)[1] || "", permitted_classes: [], aliases: false); puts "OK #{p}" }'

# plugin / marketplace JSON parse check
ruby -rjson -e '[".claude-plugin/marketplace.json", *Dir.glob("plugins/*/.claude-plugin/plugin.json")].each { |p| JSON.parse(File.read(p)); puts "OK #{p}" }'
```

Also validate the changed skill. Skills owning a bespoke validator run their own (e.g. `python3 plugins/elian-store/skills/review/scripts/validate_skill.py`); `brainstorm`, `fix`, `implement`, and `improve` share `python3 tools/validate_skill.py <skill-dir>`.
