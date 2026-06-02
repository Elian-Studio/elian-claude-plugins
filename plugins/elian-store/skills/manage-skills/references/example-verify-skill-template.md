# Example Verify Skill Template

Use this template when `manage-skills` creates a new `verify-*` skill.

```markdown
---
name: verify-<domain>
description: When <domain> changes, verify <specific contract> before PR.
when_to_use: "Use when files matching <patterns> change, before PR, or when the user asks to verify <domain>."
argument-hint: "[optional target path]"
disable-model-invocation: true
allowed-tools: Bash(grep*) Bash(find*) Bash(python3 *) Read Glob Grep
---

# verify-<domain>

## Purpose

Verify <specific contract>. This skill is read-only unless the user explicitly asks for a fix in another skill.

## When to Run

- Before PR when <domain> files changed.
- After `/manage-skills` reports drift in this domain.
- During code review when <specific risk> is suspected.

## Related Files

- `<glob-1>`
- `<glob-2>`
- `<test-glob>`

## Workflow

### Check 1: <name>

Command:

```bash
<safe detection command>
```

PASS:

- <explicit pass condition>

FAIL:

- <explicit failure condition>

Report:

- File path.
- Line number when available.
- Problem.
- Suggested fix direction.

### Check 2: <name>

Command:

```bash
<safe detection command>
```

PASS:

- <explicit pass condition>

FAIL:

- <explicit failure condition>

## Output Format

```text
Findings
- [HIGH|MEDIUM|LOW] path:line - issue
  Evidence:
  Suggested fix:
  Verification:

No Findings
- No <domain> verification issues found in the reviewed scope.
```

## Exceptions

- Generated files under `<glob>`.
- Test fixtures intentionally containing invalid examples.
- Archived docs not used by production code.

## Forbidden

- Modify files.
- Run destructive commands.
- Treat generated fixtures as production violations.
- Hide failures behind broad exceptions.

## Self-check

- [ ] Purpose is specific.
- [ ] Related Files globs match existing files.
- [ ] Workflow commands are safe.
- [ ] PASS/FAIL criteria are explicit.
- [ ] Exceptions are narrow.
```

## Fill-In Guidance

Use product or contract language in the name:

- Good: `verify-i18n`, `verify-api-contract`, `verify-message-cost`.
- Weak: `verify-files`, `verify-rules`, `verify-stuff`.

Prefer one clear verification domain. If the skill needs unrelated checks, create separate skills.
