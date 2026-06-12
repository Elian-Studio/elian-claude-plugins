---
name: manage-skills
description: When verify-* skills drift behind code changes (uncovered files / broken references / missing checks), auto-detect the drift and create or update verify-* skills so the project's verification stays current. Pairs with verify-implementation (orchestrator); this skill is the meta-tool that maintains the skill set.
when_to_use: "Use after introducing new patterns or rules, before PR to confirm verification coverage, when verification missed an expected issue, periodically to keep skills aligned with the codebase, or when the user asks to audit skill drift, repair verify skills, or run /manage-skills."
argument-hint: "[skill-name | focus-area | question]"
disable-model-invocation: true
allowed-tools: Bash(git diff*) Bash(git log*) Bash(grep*) Bash(awk*) Bash(find*) Bash(python3 *) Read Glob Grep Edit Write
---

# manage-skills

Code changes faster than verification skills. This skill compares the current session's changes against project-local `verify-*` skills, finds coverage gaps or stale references, and updates or creates verification skills when approved.

It pairs with `verify-implementation`: `manage-skills` maintains the verification skill set; `verify-implementation` runs it.

## Where this fits in the workflow

```text
implement / fix / improve
  -> manage-skills
  -> verify-implementation
  -> ship
```

- **Upstream**: code changes introduce new files, patterns, rules, or validation needs.
- **This skill**: maps changes to existing `verify-*` skills and detects drift.
- **Downstream**: `verify-implementation` runs the corrected verification set.

## What's automated vs what needs your taste

| Automated | User decides |
|---|---|
| Discover `.claude/skills/verify-*/SKILL.md` | Whether to accept CREATE proposals |
| Match changed files to Related Files and Workflow patterns | Which skill owns ambiguous mappings |
| Classify Coverage Gap, Invalid Reference, Missing Check, Outdated Value | Whether to mark an item EXEMPT |
| Draft CREATE, UPDATE, or EXEMPT judgment | Whether to apply, rewrite, or defer the judgment |
| Add or remove stale Related Files when approved | Intended verification command semantics |

Ask when the mapping is ambiguous. New skill creation always needs user approval.

## Modes

### Mode 1: `analyze` (default)

Analyze drift only. Do not edit files.

Output: console report with summary, detailed drift rows, and uncovered changes.

### Mode 2: `repair`

Apply approved updates from the analyze report.

Output:

- Updated `.claude/skills/verify-*/SKILL.md` files.
- Optional new `verify-{name}/SKILL.md`.
- Optional `verify-implementation` sync when the project uses a hardcoded list.

### Mode 3: `sync-with-verify-implementation`

If a project-local `.claude/skills/verify-implementation/SKILL.md` contains a hardcoded `verify-*` list, update it to match the actual local skill directory. The bundled elian-store `verify-implementation` uses dynamic discovery, so this mode is only for projects that own a local orchestrator.

## Standing rules

### Naming

- Verification skills must use the `verify-` prefix.
- Use lowercase kebab-case.
- Make the domain visible, for example `verify-i18n` or `verify-api-contract`.

### Required sections

Block publication if a new or updated `verify-*` skill lacks any required section:

1. `Purpose`
2. `When to Run`
3. `Related Files`
4. `Workflow`
5. `Output Format`
6. `Exceptions`

### Quality bar

- Paths must exist or globs must match.
- Detection commands must be runnable.
- PASS/FAIL criteria must be explicit.
- Exceptions must be realistic and not erase the rule.
- Formatting must be consistent with existing local skills.

### Scope

Operate only on the current working directory's `.claude/skills/`. Do not modify user-global `~/.claude/skills/`.

## Procedure: Mode 1 (`analyze`)

1. Discover project-local skills:

```bash
find .claude/skills -maxdepth 2 -name SKILL.md 2>/dev/null
```

2. Collect changed files:

```bash
git diff HEAD --name-only
git log --oneline main..HEAD 2>/dev/null
git diff main...HEAD --name-only 2>/dev/null
```

3. Map changed files to `verify-*` skills using Related Files and Workflow patterns. See [references/drift-detection.md](references/drift-detection.md).
4. Classify gaps as Coverage Gap, Invalid Reference, Missing Check, or Outdated Value.
5. Decide CREATE, UPDATE, or EXEMPT using [references/decision-matrix.md](references/decision-matrix.md).
6. Report using [references/example-drift-report.md](references/example-drift-report.md).

Mode 1 reports only. Use Mode 2 for edits.

## Procedure: Mode 2 (`repair`)

Apply each approved item:

| Judgment | Action | Approval |
|---|---|---|
| UPDATE Related Files | Add or remove file patterns | Batch approval is acceptable |
| UPDATE Workflow | Revise detection commands or PASS/FAIL text | Per-item approval |
| CREATE new skill | Create `verify-{name}/SKILL.md` | Required per card |
| EXEMPT | No file change | No approval needed |

After each create/update, run:

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/manage-skills}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/manage-skills}"
python3 "${SKILL_DIR}/scripts/check-skill-frontmatter.py" .claude/skills/verify-{name}/SKILL.md
```

Use [references/example-verify-skill-template.md](references/example-verify-skill-template.md) for new skills.

## Procedure: Mode 3 (`sync-with-verify-implementation`)

Read the project-local orchestrator. If it lists `verify-*` skills explicitly, replace that list with the current local skill directory. Do not apply this to the bundled elian-store dynamic-discovery orchestrator.

## Forbidden

- Modify or create user-global `~/.claude/skills/`.
- Treat non-`verify-` skills as verification skills.
- Delete skills without explicit user instruction.
- Publish a `verify-*` skill that lacks required sections.
- Use exceptions that make the rule meaningless.
- Auto-assign ambiguous ownership without asking.

## Known pitfalls

| Pitfall | Symptom | Prevention |
|---|---|---|
| Ambiguous mapping auto-assigned | A changed file belongs to two skills but only one is updated | Ask the user when multiple skills match |
| Stale Related Files | Deleted paths remain in a skill | Remove stale paths during approved UPDATE |
| Over-broad exception | A rule never fails | Require realistic exceptions and sample detection |
| Hardcoded orchestrator drift | `verify-implementation` misses a new local skill | Run Mode 3 only when the project uses hardcoded lists |

## Validation

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/manage-skills}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/manage-skills}"
python3 "${SKILL_DIR}/scripts/check-skill-frontmatter.py" .claude/skills/verify-{name}/SKILL.md
python3 "${SKILL_DIR}/scripts/check-skill-frontmatter.py" .claude/skills/verify-*/SKILL.md --json
```

Checks:

1. Valid YAML frontmatter with required fields.
2. All six required sections exist.
3. Related Files paths exist or glob patterns match.
4. `allowed-tools` avoids broad dangerous patterns such as `Bash(*)`.

## End-of-skill reflection

After Mode 2 or Mode 3, report observations rather than praise:

```text
Repaired 5 drift items. Patterns noticed:
- 4/5 were Coverage Gap, which may mean new domains are being added faster than verify skill boundaries.
- 1 Invalid Reference suggests file movement should be included in drift checks.
- 0 Missing Check items suggests existing detection commands are mostly aligned, but new domains still need manual review before the next PR.

Next recommended step: run /verify-implementation.
```

## Supporting files

| File | Purpose |
|---|---|
| [references/drift-detection.md](references/drift-detection.md) | Change-to-skill mapping and four drift classes |
| [references/decision-matrix.md](references/decision-matrix.md) | CREATE / UPDATE / EXEMPT decision rules |
| [references/example-drift-report.md](references/example-drift-report.md) | Mode 1 report example |
| [references/example-verify-skill-template.md](references/example-verify-skill-template.md) | Template for CREATE |
| [scripts/check-skill-frontmatter.py](scripts/check-skill-frontmatter.py) | Frontmatter and required-section validator |

## Self-check before publishing

- [ ] `check-skill-frontmatter.py` passes.
- [ ] All six required sections exist.
- [ ] Related Files paths exist or globs match.
- [ ] Workflow detection commands dry-run successfully.
- [ ] PASS/FAIL criteria are explicit.
- [ ] Exceptions are realistic.
- [ ] Hardcoded orchestrator lists are synced when applicable.
