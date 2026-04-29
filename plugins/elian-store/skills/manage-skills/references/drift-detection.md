# Drift Detection — 변경 ↔ 스킬 매핑 + 4종 갭 분류

manage-skills 의 핵심 알고리즘. Mode 1 (analyze) 의 Step 3-4 에 해당.

---

## 입력

- `CHANGED_FILES`: `git diff HEAD --name-only` + `git diff main...HEAD --name-only` 합집합
- `SKILLS`: 프로젝트의 모든 `.claude/skills/verify-*/SKILL.md`

## 출력

각 변경 파일별 1개의 **갭 분류 카드**:

```
File: src/payment/refund-policy.ts (NEW)
Classification: COVERAGE_GAP
Hint: verify-payment-rules 의 Related Files 가 명시 리스트 사용 — 추가 필요
Action proposal: UPDATE-ADD
```

---

## 매핑 알고리즘

각 SKILL.md 에서 다음을 추출:

1. **Related Files 섹션** — 명시 경로 리스트 또는 glob 패턴
2. **Workflow 섹션 안의 Grep / Glob 명령어** — 검사 대상 파일 패턴
3. **Workflow 섹션 안의 직접 경로 참조** — 코드블록 안의 path

이 세 개를 모아 **`SkillCoveragePattern[]`** 만든다:

```
{
  skill: "verify-payment-rules",
  patterns: [
    "src/payment/payment.service.ts",
    "src/payment/payment.repository.ts",
    "src/payment/**/*.test.ts"  // glob
  ]
}
```

각 변경 파일에 대해 모든 SkillCoveragePattern 을 순회하며 매칭:

- 명시 경로: 정확 일치
- glob: fnmatch 또는 minimatch
- 매칭되는 스킬 0개, 1개, 2+개 별 분기

---

## 4종 갭 분류

### 1. Coverage Gap

**정의**: 변경 파일이 어떤 verify-* 스킬에도 매핑되지 않음.

**탐지**:
```
for f in CHANGED_FILES:
    matches = [s for s in SKILLS if matches_pattern(f, s.patterns)]
    if not matches:
        emit COVERAGE_GAP(f)
```

**Action 후보**: UPDATE-ADD (가장 가까운 스킬에 추가) 또는 CREATE (3+ 누적 시).

### 2. Invalid Reference

**정의**: 스킬의 Related Files / Workflow 가 **실제 존재하지 않는 파일/디렉토리** 를 참조.

**탐지**:
```
for s in SKILLS:
    for path in s.explicit_paths:  # 명시 경로만 (glob 제외)
        if not file_exists(path):
            emit INVALID_REFERENCE(s, path)
```

**Action 후보**: UPDATE-REMOVE (stale 제거).

> 주의: 변경 파일이 RENAME 됐을 가능성 — `git log --follow` 로 새 경로 추적 후 UPDATE-ADD 가 더 적절할 수 있음.

### 3. Missing Check

**정의**: 새 패턴/규칙이 코드에 도입됐지만 어떤 verify-* 스킬도 그 패턴을 검사 안 함.

**탐지 (heuristic)**:
- 변경 파일에서 새로 등장한 import, decorator, 함수 호출, naming 컨벤션 추출
- 같은 패턴이 3+ 파일에 등장하면 후보
- 어떤 verify-* 의 Workflow Grep 도 그 패턴을 검사 안 하면 MISSING_CHECK

**Action 후보**: UPDATE (기존 스킬에 새 Workflow 단계 추가) 또는 CREATE.

### 4. Outdated Value

**정의**: 스킬의 Workflow Grep/Glob 패턴이 코드 변경으로 더 이상 매칭 안 됨.

**탐지**:
```
for s in SKILLS:
    for cmd in s.workflow_commands:
        if cmd.is_grep_or_glob:
            result = execute(cmd)  # dry-run
            if result.empty and was_non_empty_at_last_commit:
                emit OUTDATED_VALUE(s, cmd)
```

**Action 후보**: UPDATE (Grep/Glob 패턴 갱신).

---

## 매칭 신뢰도 (선택)

각 매칭에 0.0~1.0 신뢰도 부여 (사용자 결정 보조용):

| 신호 | 신뢰도 |
|------|------|
| 명시 경로 정확 일치 | 1.0 |
| glob 명확 매칭 (`src/auth/**`) | 0.9 |
| 디렉토리만 매칭 (`src/auth/` 일부) | 0.6 |
| 확장자만 매칭 (`*.ts`) | 0.3 |
| 명명 규칙만 매칭 (`use*.ts`) | 0.4 |

신뢰도 < 0.5 인 매칭은 사용자 질문 (다중 매칭 또는 모호 케이스).

---

## 면제 규칙 (drift 검사 대상에서 제외)

다음은 변경됐어도 갭 분석 안 함:

- Lock files (`*.lock`, `package-lock.json` 등)
- Generated (`dist/**`, `build/**`, `*.generated.*`)
- Test fixtures (`**/fixtures/**`)
- Vendor (`vendor/**`, `node_modules/**`)
- CLAUDE.md 자체

면제된 변경은 보고서의 "면제된 변경" 섹션에 카운트만 남김.

---

## 의사 코드

```python
def detect_drift(changed_files, skills):
    gaps = []
    for f in changed_files:
        if is_exempt(f):
            continue
        matches = [s for s in skills if matches_pattern(f, s.patterns)]
        if not matches:
            gaps.append(("COVERAGE_GAP", f, hint(f)))
        elif len(matches) > 1:
            gaps.append(("AMBIGUOUS", f, matches))

    for s in skills:
        for path in s.explicit_paths:
            if not file_exists(path):
                gaps.append(("INVALID_REFERENCE", s, path))
        for cmd in s.workflow_commands:
            if cmd.is_grep_or_glob and dry_run_empty(cmd):
                gaps.append(("OUTDATED_VALUE", s, cmd))

    new_patterns = extract_new_patterns(changed_files)
    for pat in new_patterns:
        if not any(s.checks(pat) for s in skills) and pat.count >= 3:
            gaps.append(("MISSING_CHECK", pat))

    return gaps
```

실제 구현은 manage-skills 가 Claude 에이전트 워크플로우로 실행 — 위 로직을 코드로 자동화하지 않고 reasoning + tool use 로 수행.
