# Skill Orchestration

This reference defines how `verify-implementation` discovers and runs project-local `verify-*` skills.

## Discovery

Search only:

```text
.claude/skills/verify-*/SKILL.md
```

Exclude:

- `verify-implementation` itself.
- Skills without the `verify-` prefix.
- User-global skill directories.

Dry-run command:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check-skill-discovery.py" .claude/skills/
```

## Skill Metadata

For each discovered skill, read:

- frontmatter `name`
- frontmatter `description`
- body `Workflow`
- body `Exceptions`
- body `Output Format`

If frontmatter is invalid, report the skill as failed before executing any checks.

## Manual-Only Detection

Skip a skill during run-all when the body contains:

- `manual-only`
- `manual run only`

Run it only when the user explicitly invokes:

```text
/verify-implementation verify-name
```

## Workflow Parsing

The orchestrator should look for:

- Check headings.
- Command blocks.
- PASS/FAIL criteria.
- Report fields.

If a workflow is too vague to execute safely, do not guess. Report:

```text
verify-<name>: workflow is not executable
Reason: missing PASS/FAIL criteria or command
Suggested next step: run /manage-skills repair for this verifier
```

## Exceptions Matching

Exceptions are evaluated before final findings are reported.

Use exception categories:

- Generated files.
- Test fixtures.
- Archived docs.
- Vendor files.
- User-approved one-off exceptions.

Do not create new exceptions during `verify-implementation`; recommend `/manage-skills` if exceptions need updating.

## Execution Order

Default order:

1. Contract and schema verifiers.
2. Security or permission verifiers.
3. Domain/business-rule verifiers.
4. UI/copy/i18n verifiers.
5. Catch-all quality verifiers.

If order is unknown, use alphabetical order and state that order was inferred.

## Report Aggregation

For each skill, collect:

- result: PASS, FAIL, SKIP, or ERROR
- findings
- exception matches
- suggested fixes
- verification commands run

Integrated summary:

```text
Skills run: 5
PASS: 3
FAIL: 1
SKIP: 1
ERROR: 0
Findings: 4
```

## Auto-Fix Rules

Auto-fix is allowed only after user approval.

Safe auto-fix candidates:

- Add missing i18n key.
- Update stale path in a verifier.
- Add missing enum case when the expected value is explicit.
- Fix template placeholder mismatch when schema and template make the correction obvious.

Do not auto-fix:

- Product policy.
- Security or permission decisions.
- Database migrations.
- Deploy or environment settings.
- Broad refactors.

## Re-Verification

After approved fixes:

1. Rerun affected skills.
2. Compare before/after.
3. List residual manual issues.
4. Recommend a full run-all cross-check when many fixes were applied.
