# /fix — Templates

## Symptom + root-cause table

```markdown
## Symptoms

| # | Symptom | Repro condition | Blast radius |
|---|---------|-----------------|--------------|
| S1 | List endpoint returns 500 after restart | First request after cold start | List page; user-facing |
| S2 | Notification not delivered | Specific user role | One module |

## Root-cause analysis

| # | Symptom | Proximate cause | Root cause | Affected files |
|---|---------|-----------------|------------|----------------|
| S1 | 500 after restart | NPE in cache populator | Lazy init races first request | services/cache/*.ts, app/startup.ts |
| S2 | No delivery | Filter excludes role | Role list hardcoded; missing X | services/notification/role-filter.ts |
```

## Conflict matrix examples

### No conflicts

```
        S1    S2
S1      —     ✅
S2      ✅    —
→ Both parallelizable
```

### With conflicts

```
        S1    S2
S1      —     ❌    ← shared: services/notification/index.ts
S2      ❌    —
→ Sequential: S1 first, then S2
```

## Repair plan template

```markdown
## Repair plan — {issueId}

### Symptoms + root causes
| # | Symptom | Root cause | Files | Regression test |
|---|---------|-----------|-------|-----------------|

### Execution strategy
- Strategy: {direct | Subagent (parallel) | Agent Team | hybrid}
- Rationale: {which path of `_shared/execution-strategy.md` applies}
- Parallel groups: {composition}

### Sibling-site audit
| Pattern | Search command | Sites found | Status |
|---------|---------------|-------------|--------|
| {root-cause grep pattern} | grep -rn ... | N | audited |
```

## Spawn prompt template (parallel multi-symptom fix)

```markdown
## Role
TDD repair of symptom {Sn}

## Owned files (only these)
- src/.../the-buggy-file.ts
- src/.../the-buggy-file.test.ts (regression test)

## Bug
- Symptom: {description}
- Repro: {steps}
- Root cause: {confirmed cause}

## TDD rules
1. Regression test first — must reproduce the bug (Red)
2. Apply fix — minimum change to make test pass (Green)
3. Run full relevant suite — no collateral damage
4. Refactor if necessary

## Project conventions
- {coding conventions from CLAUDE.md}
- Test command: {build / test command}

## Definition of Done
- Regression test exists and passes
- Existing tests still green
- Sibling-site search performed
- Committed via /commit (one commit = one symptom)
```

## Completion report template

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Fix complete  |  {issueId}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Summary
| Item | Backend | Frontend |
|------|---------|----------|
| Files (changed) | N | N |
| Regression tests added | N | N |
| Commits | N | N |

## Per-symptom outcome
| # | Symptom | Root cause | Strategy | Tests | Status |
|---|---------|-----------|----------|-------|--------|

## Verification
| Check | Result |
|-------|--------|
| Regression tests | |
| Existing tests (unchanged modules) | |
| Format / lint | |
| Compile / typecheck | |

## Sibling-site audit
- Searched: {patterns}
- Found: {N sibling sites; M with same bug}
- Action: {fixed all / opened follow-up issue}

## Next steps
1. Mark issue → Done
2. Open MR / PR
3. Code review

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
