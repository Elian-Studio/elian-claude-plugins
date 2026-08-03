# Elian Workflow — deprecated

**Install `elian-store` instead.** It ships `issue-open` and `issue-close` alongside the rest of
the workflow, so nothing here is unavailable there.

```shell
/plugin install elian-store@elian
/plugin uninstall elian-workflow@elian
```

This plugin still ships the two issue-cycle skills as generated copies of `elian-store`'s, so an
existing install keeps working. It receives no new skills.

## Why it was deprecated

1.0.0 shipped two skills — `issue-open` and `issue-close` — as a separate plugin, justified by
their being the only ones needing local Notion configuration.

2.0.0 expanded that to 19 skills and 30 agents to resolve a name collision: the same name was
reserved in `docs/plugin-layering-architecture.md` §2 for an 18-skill Workflow layer, and a
published plugin name cannot be changed. Because a plugin is copied as a unit at install time,
"two plugins ship the same skill" can only be implemented as physical duplication — so 2.0.0
committed **122 files byte-identical to `plugins/elian-store/`** and told users to install one
plugin, not both.

That inverted the two releases before it, which had removed a retired-skill set and 621
duplicated lines. It passed validation because the `composed-parity` check asks whether a copy
*matches* its source, never whether the copy *should exist*.

3.0.0 reverses it. `elian-store` absorbed both issue-cycle skills and the two shared documents
they read, and this plugin shrank back to generated copies of exactly those. Duplicated files:
122 → 5.

The deeper lesson is in `docs/plugin-portfolio-hybrid-model.md`: a second plugin needs a reason
that survives the next release, and "it needs configuration" was not one.

## Documentation

The issue cycle, the Notion setup procedure, the narrative template rules, and the list of what
these skills refuse to do are documented in `elian-store`'s README:
<https://github.com/Elian-Studio/elian-claude-plugins/blob/main/plugins/elian-store/README.md>

## Maintenance

Everything under `skills/` is generated. Edit the source in `plugins/elian-store/skills/`, then:

```shell
python3 tools/generate.py --sync        # refresh the copies
python3 scripts/validate_repository.py  # fails if a copy drifted
```

`tools/clusters.json` → `published.elian-workflow` declares what is copied here.
