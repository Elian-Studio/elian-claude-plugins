# Drift Detection

This reference defines how `manage-skills` maps code changes to project-local `verify-*` skills.

## Inputs

- Changed files from `git diff`, branch diff, and recent commits.
- Project-local `.claude/skills/verify-*/SKILL.md`.
- Each verification skill's `Related Files`, `Workflow`, and `Exceptions` sections.

## Mapping Algorithm

1. Discover all local `verify-*` skills.
2. Extract candidate file patterns from `Related Files`.
3. Extract command patterns from `Workflow`.
4. Compare each changed file with every candidate pattern.
5. Mark a direct match when a file path or glob matches.
6. Mark a weak match when a workflow command clearly inspects the changed path family.
7. If one file maps to multiple skills, stop and ask the user which skill owns it.
8. If no skill maps, classify the file as a coverage gap.

## Drift Classes

| Class | Meaning | Example |
|---|---|---|
| Coverage Gap | Changed file is not covered by any `verify-*` skill | New `src/i18n/` file with no i18n verifier |
| Invalid Reference | Skill references a path that no longer exists | `Related Files` points to deleted `src/old-api/` |
| Missing Check | Skill covers the file but does not test a new rule | New enum value is added, but verifier checks only old values |
| Outdated Value | Skill encodes a stale constant or threshold | Validator expects max length 100 but product changed to 120 |

## Matching Signals

Strong signals:

- Exact path match.
- Glob match.
- Workflow command explicitly scans the changed path.
- The changed file imports or updates a symbol named in the skill.

Weak signals:

- Same directory but no explicit glob.
- Same domain term in skill name and file name.
- Test file names imply the same contract.

Weak signals should produce a question, not an automatic update.

## Ambiguity Rules

Ask the user when:

- Two or more skills match with similar strength.
- A file belongs to both domain and infrastructure rules.
- A verifier would need a new rule, not just a new path.
- A change looks intentional but could be exempt.

Question format:

```text
This file matches multiple verify skills:
- verify-api-contract
- verify-business-rules

Which skill should own the new check, or should this be exempt?
```

## Stale Reference Detection

For each path or glob in `Related Files`:

- Exact path must exist.
- Glob must match at least one file.
- Deleted paths should be proposed for removal.
- Empty globs may be valid only when the skill explicitly says the path is optional.

## Output Fields

Each drift row should include:

- `changed_file`
- `matching_skills`
- `drift_class`
- `proposed_action`
- `confidence`
- `question` when ambiguous

Example:

```text
changed_file: src/features/messages/i18n/en.json
matching_skills: []
drift_class: Coverage Gap
proposed_action: CREATE verify-i18n or UPDATE existing language verifier
confidence: medium
question: Should this project have a dedicated verify-i18n skill?
```
