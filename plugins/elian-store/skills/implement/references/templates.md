# /implement — Templates

## Feature decomposition template

```markdown
## Feature list

| # | Feature | Changed files | Dependencies |
|---|---------|---------------|--------------|
| F1 | Schedule CRUD API | ScheduleController, ScheduleService | none |
| F2 | AlimTalk delivery integration | AlimTalkService, NotificationConfig | none |
| F3 | Admin UI page | SchedulePage.vue, schedule-api.ts | F1 (API first) |
```

## Conflict matrix examples

### No conflicts

```
        F1    F2    F3
F1      —     ✅    ✅
F2      ✅    —     ✅
F3      ✅    ✅    —
→ All parallelizable
```

### With conflicts

```
        F1    F2    F3
F1      —     ❌    ✅     ← F1↔F2 share BaseService.java
F2      ❌    —     ✅
F3      ✅    ✅    —
→ Group A: [F1, F2] sequential / Group B: [F3] independent
→ Run A and B in parallel
```

## Implementation plan template

```markdown
## Implementation plan — {issueId}

### Feature list
| # | Feature | Changed files | Execution group |
|---|---------|---------------|-----------------|

### Execution strategy
- Strategy: {direct | Subagent (parallel) | Agent Team | hybrid}
- Rationale: {which path of `_shared/execution-strategy.md` applies}
- Parallel groups: {composition}

### TDD scope
| Feature | Tests planned | Coverage target |
|---------|---------------|-----------------|
```

## Spawn prompt template (parallel multi-feature TDD)

```markdown
## Role
TDD implementation of {feature name}

## Owned files (only these)
- src/main/java/.../XxxService.java (new)
- src/test/java/.../XxxServiceTest.java (new)

## Requirements
1. {requirement 1}
2. {requirement 2}

## TDD rules
1. Write failing test first (Red)
2. Minimum implementation (Green)
3. Refactor with green tests as safety net

## Project conventions
- {coding conventions from CLAUDE.md}
- Test command: {build / test command}

## Definition of Done
- All tests PASS
- Format / lint pass
- Committed as a single feature unit via /commit
```

## Completion report template

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Implementation complete  |  {issueId}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Summary
| Item | Backend | Frontend |
|------|---------|----------|
| Files (new / changed) | N / N | N / N |
| Tests | N PASS | N PASS |
| Commits | N | N |

## Per-feature outcome (multi-feature only)
| # | Feature | Strategy | Tests | Status |
|---|---------|----------|-------|--------|

## Verification
| Check | Result |
|-------|--------|
| Format / lint | |
| Compile / typecheck | |
| Tests | |

## Commits
| Repo | SHA | Message |
|------|-----|---------|

## Next steps
1. Mark design doc status → Done
2. Open MR / PR
3. Code review

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
