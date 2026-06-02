---
name: verify-implementation
description: When PR is about to ship, dynamically discover and run all verify-* skills in the current project, surface failures with concrete fix suggestions, and (with approval) auto-apply fixes + re-verify. One command instead of remembering which verify-* to run for which change. Pairs with manage-skills (drift maintenance).
when_to_use: "Use before opening a PR, during code review, when auditing rule compliance, after implementing a feature, or when the user asks to run verification, check before PR, audit implementation, or run /verify-implementation."
argument-hint: "[Optional: specific verify skill name]"
disable-model-invocation: true
allowed-tools: Bash(grep*) Bash(awk*) Bash(find*) Bash(python3 *) Read Glob Grep Edit
---

# verify-implementation

Run project-local `verify-*` skills without forcing the user to remember which verification skill applies to which change. This skill dynamically discovers `.claude/skills/verify-*/SKILL.md`, parses each workflow, runs safe checks, reports failures, and can apply approved fixes followed by re-verification.

It pairs with `manage-skills`: `manage-skills` keeps verification skills current; `verify-implementation` executes them.

## Where this fits in the workflow

```text
implement / fix / improve
  -> manage-skills
  -> verify-implementation
  -> ship
```

- **Upstream**: implementation exists and `manage-skills` has corrected drift if needed.
- **This skill**: run all or selected `verify-*` skills and produce an integrated report.
- **Downstream**: fix remaining failures, run browser QA when user-visible behavior changed, then ship.

## What's automated vs what needs your taste

| Automated | User decides |
|---|---|
| Discover `.claude/skills/verify-*/SKILL.md` | Whether to run all or one specific skill |
| Parse Workflow and Exceptions sections | Whether an EXEMPT match is acceptable |
| Run Grep, Glob, and Bash detection commands | Whether to accept, modify, or reject suggested fixes |
| Generate concrete fix suggestions | Scope of auto-fix |
| Compare before/after results | Priority of residual manual issues |

Skills marked manual-only are skipped during run-all and run only by explicit invocation.

## Modes

### Mode 1: `run-all` (default)

Run every safe project-local `verify-*` skill sequentially, then produce one integrated markdown report. If failures are found, ask before applying fixes.

### Mode 2: `run-specific {skill-name}`

Run one verification skill:

```text
/verify-implementation verify-i18n
```

### Mode 3: `dry-run`

Show the discovered `verify-*` skills and planned workflow steps without executing checks:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check-skill-discovery.py" .claude/skills/
```

## Standing rules

### Scope

Operate only on the current working directory's `.claude/skills/verify-*`. Do not inspect or execute user-global `~/.claude/skills/`.

### Exclusions

- Exclude `verify-implementation` itself to avoid recursion.
- Exclude `manage-skills` because it is not a `verify-*` skill.

### Manual-only marker

If a `verify-*` skill body says `manual-only` or `manual run only`, skip it in Mode 1. Run it only when the user explicitly invokes that skill by name.

### Exceptions first

Respect each `verify-*` skill's `Exceptions` section. The orchestrator must not override a skill's own exception rules.

## Procedure: Mode 1 (`run-all`)

### Step 1: Discover skills

```bash
find .claude/skills -maxdepth 2 -name SKILL.md \
  | xargs -I {} dirname {} \
  | xargs -I {} basename {} \
  | grep '^verify-' \
  | grep -v '^verify-implementation$'
```

If none are found, report:

```text
No project-local verify-* skills were found.
Run /manage-skills to create verification skills for this project, or add .claude/skills/verify-{name}/SKILL.md manually.
```

### Step 2: Execute skills sequentially

For each `verify-*` skill:

1. Read `SKILL.md`.
2. Skip if it is marked manual-only.
3. Parse Workflow checks, detection commands, and PASS/FAIL criteria.
4. Parse Exceptions.
5. Run safe detection commands.
6. Compare output with PASS/FAIL criteria.
7. Remove exception matches.
8. Record failures with file path, line number when available, problem description, suggested fix, and verification gap.

### Step 3: Integrated report

Use [references/example-report.md](references/example-report.md) as the report shape.

### Step 4: Auto-fix gate

When failures exist, ask the user before editing:

```text
Found 7 issues across 3 verify-* skills. How should I proceed?

1. Apply all suggested fixes.
2. Review fixes one by one.
3. Stop without changes.
```

### Step 5: Fix and re-verify

Apply approved fixes, rerun affected skills, and compare before/after results. If applying all fixes, also recommend one full run-all cross-check.

Residual issues must be explicit:

```text
### Residual issues requiring manual resolution
| # | Skill | File | Problem |
|---|---|---|---|
| 1 | verify-business-rules | src/.../OrderService.java:88 | Domain logic decision exceeds auto-fix scope |
```

## Forbidden

- Inspect or run user-global `~/.claude/skills/`.
- Ignore a manual-only marker.
- Override a `verify-*` skill's Exceptions.
- Run `verify-implementation` recursively.
- Treat `manage-skills` as a verification skill.
- Apply fixes without user approval.

## Known pitfalls

| Pitfall | Symptom | Prevention |
|---|---|---|
| Wrong naming | `validate-payment` is never discovered | Require `verify-` prefix and use dry-run |
| Missing Exceptions | Fixtures or vendor files become false positives | Report "Exceptions need strengthening" and use `/manage-skills` |
| Auto-fix side effects | One fix violates another rule | Rerun affected skills and recommend a full cross-check for broad fixes |
| Hardcoded discovery assumptions | Some projects use different skill roots | Scope to `.claude/skills/` unless user explicitly supplies a path |

## Validation

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check-skill-discovery.py" .claude/skills/
python3 "${CLAUDE_SKILL_DIR}/scripts/check-skill-discovery.py" .claude/skills/ --json
```

Checks:

1. Project-local `verify-*` skills exist.
2. Each `SKILL.md` has valid frontmatter and required fields.
3. `verify-implementation` is excluded from execution.
4. Manual-only skills are shown as skipped during run-all.

## End-of-skill reflection

After run-all, report observations rather than praise:

```text
Ran 5 verification skills and found 7 issues. Auto-fixed 6; 1 remains.

Patterns noticed:
- 4/7 were i18n key gaps, which may mean implementation prompts need an i18n step.
- verify-api-contract has passed five consecutive runs, but a sample manual check may still be useful.
- The remaining domain-logic issue needs a human decision before PR.

Next recommended step: resolve the residual issue, then create the PR.
```

## Supporting files

| File | Purpose |
|---|---|
| [references/example-report.md](references/example-report.md) | Integrated report example |
| [references/skill-orchestration.md](references/skill-orchestration.md) | Dynamic discovery and Workflow/Exceptions parsing |
| [scripts/check-skill-discovery.py](scripts/check-skill-discovery.py) | Dry-run discovery validator |

## Self-check before claiming PR-ready

- [ ] Dry-run discovers every intended project-local `verify-*` skill.
- [ ] Missing skills were fixed by naming or location.
- [ ] Auto-fixes were approved before editing.
- [ ] Re-verification passes after fixes.
- [ ] Residual manual issues are resolved or explicitly accepted.
- [ ] Manual-only skills were run explicitly when needed.
- [ ] Exceptions cover known false positives without weakening the rule.
