# /improve — Templates

## BEFORE snapshot template

```markdown
## BEFORE — current state

| Item | Current behavior | Problem | Existing tests | Dependencies |
|------|------------------|---------|----------------|--------------|
| I1 | List endpoint loads all rows | N+1 queries; p95 = 2.4s | 3 unit tests, no perf test | OrderService, OrderRepository |
| I2 | UI renders all rows synchronously | Janky scroll on >100 rows | 0 component tests | OrderListPage, OrderRow |
```

## Improvement plan template

```markdown
## Improvement plan — {issueId}

### Improvements
| # | Title | BEFORE metric | AFTER target | Files | Risk |
|---|-------|---------------|--------------|-------|------|
| I1 | Eager load orders | p95 = 2.4s | p95 ≤ 1.0s | OrderRepository, OrderService | low |
| I2 | Virtualize order list | jank @ 100 rows | smooth @ 1000 rows | OrderListPage, OrderRow | medium |

### Conflict matrix (multi-improvement)
        I1    I2
I1      —     ✅
I2      ✅    —

### Execution strategy
- Strategy: {direct | Subagent (parallel) | Agent Team | hybrid}
- Rationale: {which path of `_shared/execution-strategy.md` applies}

### Rollback criteria (per item)
| # | Rollback if | How verified |
|---|-------------|--------------|
| I1 | Existing tests Red, OR p95 doesn't improve | Step 5 BEFORE/AFTER table |
| I2 | UX broken on standard browsers | Step 5 manual verification |
```

## Characterization Test pattern

```ts
// Pin existing behavior BEFORE making changes
describe('OrderService.list (characterization)', () => {
  it('returns orders sorted by createdAt desc by default', async () => {
    const result = await service.list({})
    // Assertion captures CURRENT behavior, not the improvement target
    expect(result.map(o => o.id)).toEqual(['ord-3', 'ord-2', 'ord-1'])
  })
  it('respects page+size pagination params', async () => {
    const result = await service.list({ page: 1, size: 1 })
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('ord-2')
  })
  // ...more pins on observable behavior
})
```

## Spawn prompt template (parallel multi-improvement)

```markdown
## Role
TDD improvement of {Improvement In}

## Owned files (only these)
- src/.../{owned files}
- src/.../{owned tests}

## Context
- BEFORE: {current state}
- AFTER target: {measurable metric}
- Existing tests: {N or "missing — add Characterization first"}

## TDD rules
1. Run existing tests — must be Green before changes
2. If tests insufficient, write Characterization Tests first
3. Add new-expectation test (Red) for AFTER state
4. Apply minimum change (Green)
5. Run all tests (existing + new) — all green
6. Refactor with safety net

## Project conventions
- {coding conventions from CLAUDE.md}
- Test command: {build / test command}

## Definition of Done
- AFTER metric achieved (verified)
- Existing tests still green
- Characterization + new tests committed
- Single improvement unit committed via /commit
```

## Completion report template

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Improvement complete  |  {issueId}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Summary
| Item | Backend | Frontend |
|------|---------|----------|
| Files (changed) | N | N |
| Tests (Characterization + new) | N | N |
| Commits | N | N |

## BEFORE / AFTER comparison
| # | Item | BEFORE | AFTER | Delta | Target met? |
|---|------|--------|-------|-------|-------------|
| I1 | Order list endpoint p95 | 2.4s | 0.7s | -71% | ✅ |
| I2 | UI scroll smoothness @ 1000 rows | janky | smooth | qualitative | ✅ |

## Per-improvement outcome
| # | Title | Strategy | Status |
|---|-------|----------|--------|

## Verification
| Check | Result |
|-------|--------|
| Existing tests | |
| New tests | |
| Format / lint | |
| Compile / typecheck | |
| Performance bench | |

## Sibling-pattern audit
- Same pattern observed at: {sites}
- Action: {fixed all / opened follow-up}

## Next steps
1. Update dashboard / metric tracking
2. Open MR / PR
3. Code review

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
