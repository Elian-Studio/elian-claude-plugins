# Forbidden + Pitfall + Error Handling — generate-teammate

## Forbidden (wrong by design, not preference)

- ❌ Skip the **mental** Phase decomposition for "obvious" tasks. The skill's core value is the per-phase judgment.
- ❌ Over-decompose into a team a task a single agent does better, just to use a team. Decomposition may legitimately conclude **Direct**; forcing a team is a documented anti-pattern.
- ❌ Pick an approach by phase **type** (e.g., "exploration is always Subagent"). Always judge by characteristics.
- ❌ Escalate beyond Direct without stating the cost multiplier and the parallel benefit that justifies it. Multi-agent ≈ 15× tokens; the value must clear the cost.
- ❌ Use a communicating Agent Team for "debate" when independent Subagents + a single synthesizer would do. Agent Team is the least-validated, highest-cost mode — last resort for real-time reconciliation only.
- ❌ Spawn an Agent Team for independent work just because the task feels big. Token cost without benefit.
- ❌ Spawn Subagents in parallel before an unsettled API contract. They will produce inconsistent shapes and re-work.
- ❌ Allow two teammates to own the same file. This is a deterministic conflict, not a probabilistic one.
- ❌ Mark a parallel write phase done without the single-agent cross-boundary integration check. File ownership stops textual conflicts, not semantic seam conflicts (up to ~80% on complex tasks).
- ❌ Co-author one coherence-critical artifact (a single design doc / report / schema) across multiple teammates. Conflicting implicit decisions ruin coherence — one author, one pass.
- ❌ Hand off a coherence-critical phase result as a lossy summary. Pass the full artifact so the downstream agent does not silently re-decide.
- ❌ Skip the AskUserQuestion confirmation gate before spawning teammates.
- ❌ Bundle `Bash(*)` or unrestricted destructive permissions in `allowed-tools`. Scope every tool.
- ❌ Use `model:` parameter on `Agent({...})` calls. Resolve via env var → invocation override → definition → session.
- ❌ Use legacy `Task({...})` syntax. Use `Agent({...})` (renamed in v2.1.63).
- ❌ Set task dependencies inside `TaskCreate`. Use `TaskUpdate({ task_id, addBlockedBy: [...] })`.
- ❌ Hand-write spawn prompts without going through `create-document/teammate-spawn`. Vague language and missing slots cause spawned teammates to produce inconsistent results.

## Pitfall / Known Issues

| Pitfall | Why it happens | Fix |
|---------|----------------|-----|
| Lead starts implementing instead of waiting | Without delegate mode, the lead does work itself | Enable delegate mode (Shift+Tab); message lead "wait for teammates" |
| Teammates idle, task list stalls | Tasks have unresolved `blockedBy` after upstream tasks completed but weren't marked done | Tell lead to mark stale tasks complete or rerun TaskList review |
| TeamDelete fails with active members | Teammates didn't shut down cleanly | Always do `SendMessage(shutdown_request)` first; verify all teammates idle |
| `/resume` after lead session restart loses teammates | In-process teammates aren't restored | Spawn fresh teammates with the same context summary |
| Two teammates touched the same file | File ownership wasn't enforced | Re-design role boundaries; rerun Phase 5 ownership validation |
| Parallel build compiles per-file but breaks when merged (duplicate decls, type mismatches, broken cross-refs) | File ownership prevents textual conflicts, not semantic seam conflicts; no integration step ran | Run the mandatory single-agent integration reconciliation (cross-boundary build/typecheck) after every parallel write phase; reassign the specific seam fix and re-check |
| Agent Team token cost balloons | Each teammate keeps full context | Switch to Subagent for any phase that doesn't need real-time debate |
| `tmux` split-pane mode breaks on Windows / VS Code terminal | Display mode unsupported on those terminals | Switch to `teammateMode: "in-process"` |
| `create-document` schema fails on spawn prompt JSON | Missing slot, vague language, or short field | Read stderr — every error names the field and what's wrong. Fix JSON, re-render. |

## Error Handling

| Error | Action |
|-------|--------|
| Unclear requirements | Ask clarification via AskUserQuestion |
| Cannot parallelize | Inform "single session is more efficient" |
| File conflict detected | Reassign roles or switch to sequential |
| Teammate count > 5 | Suggest role consolidation |
| Spawn JSON schema validation failed | Show stderr to user; fix the offending slot; re-run. Do **not** skip render and hand-write prompts. |

## Failure-mode recovery

Every spawn includes a "verify completion" step. Tasks that fail to verify are reassigned, not silently skipped. Use rollback (revert produced files) when a phase produces unusable output. The reflection memo (see SKILL.md `Reflection` section) is the persistent record so the same failure doesn't recur in future invocations.
