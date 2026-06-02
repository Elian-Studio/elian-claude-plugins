# /verify-implementation - Verification-skill orchestrator (Codex Port)

Install path: `~/.codex/prompts/verify-implementation.md`.

Invocation:

```text
/verify-implementation [optional verify skill name]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/verify-implementation/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

## Purpose

Run the project-local verification prompts that apply to the current change, report failures with concrete suggestions, and ask before any auto-fix step.

Use this prompt after implementation or before release readiness. It is not the drift-maintenance prompt; that role belongs to `/manage-skills`.

## Common Contract

1. Discover applicable verification prompts.
2. Respect each prompt's own exceptions.
3. Skip manual-only checks unless explicitly requested.
4. Ask before applying fixes.
5. End with one next question, next action, or handoff payload.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `[optional verify skill name]` | Run one specific verification prompt instead of run-all | none |

`$ARGUMENTS` always wins over any local default.

## Workflow

```text
Phase 1: Discover verification prompts
Phase 2: Parse workflow and exceptions
Phase 3: Execute safe checks
Phase 4: Summarize failures
Phase 5: Auto-fix gate
Phase 6: Re-verify
```

### Phase 1: Discover verification prompts

Look for project-local verification prompts and list what can be run safely.

### Phase 2: Parse workflow and exceptions

Read each verification prompt's workflow, exceptions, and PASS/FAIL criteria before executing anything.

### Phase 3: Execute safe checks

Run the detection commands the prompts describe. Skip manual-only checks unless the user explicitly asked for one.

### Phase 4: Summarize failures

Report failures with the file, the problem, the suggested fix, and the verification gap.

### Phase 5: Auto-fix gate

If fixes are possible, ask before editing. Do not apply fixes without approval.

### Phase 6: Re-verify

After approved fixes, rerun the affected checks and report the remaining manual items, if any.

## Output Shapes

### Default output

```text
Verification summary
- Skill: <verify skill or run-all>
- Result: <pass / fail / partial>
- Recommendation: <next step>

Key findings
- <finding 1>
- <finding 2>

Open questions
- <unresolved item>

Next
- <next question or next action>
```

### Failure report

```text
## Failed checks
| Skill | File | Problem | Suggested fix |
|---|---|---|---|
| ... | ... | ... | ... |
```

## Forbidden

- Recursing into `/verify-implementation` itself.
- Treating `/manage-skills` as a verification prompt.
- Running user-global verification prompts.
- Applying fixes without approval.

## Pre-Output Self-Check

- [ ] Applicable verification prompts were discovered.
- [ ] Exceptions were parsed.
- [ ] Safe checks were executed.
- [ ] Auto-fix is gated by approval.
- [ ] The output ends with one next question or next action.
