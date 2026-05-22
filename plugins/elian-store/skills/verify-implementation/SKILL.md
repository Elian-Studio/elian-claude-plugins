---
name: verify-implementation
description: When PR is about to ship, dynamically discover and run all verify-* skills in the current project, surface failures with concrete fix suggestions, and (with approval) auto-apply fixes + re-verify. One command instead of remembering which verify-* to run for which change. Pairs with manage-skills (drift maintenance).
when_to_use: before opening a PR, during code review, when auditing rule compliance, after implementing a feature, user says '검증 돌려줘'·'PR 전 점검'·'/verify-implementation'
argument-hint: [Optional: specific verify skill name]
disable-model-invocation: true
allowed-tools: Bash(grep*) Bash(awk*) Bash(find*) Bash(python3 *) Read Glob Grep Edit
---

# verify-implementation — 검증 스킬 통합 오케스트레이터

코드 변경 후 어떤 verify-* 스킬을 어느 순서로 돌려야 할지 외울 필요 없다. 이 스킬이 프로젝트의 `.claude/skills/verify-*/SKILL.md` 를 **동적으로 발견**해 Workflow / Exceptions 를 파싱하고 순차 실행, 발견된 이슈는 수정 권장과 함께 보고한다. 사용자 승인 시 자동 수정 + 재검증까지 한 흐름.

---

## Where this fits in the workflow

```
implement / fix / improve  →  manage-skills (verify-* 정정)  →  ▶ verify-implementation ◀  →  ship
                                       ↑                           (실제 검증 실행)              ↓
                                       └────── 매 PR 전 한 번 ───────┴──────────────────────────┘
```

- **선행**: `manage-skills` 가 verify-* 스킬들을 코드에 맞게 정정
- **이 스킬**: 정정된 verify-* 들을 모두 실행 + 통합 보고서 + 자동 수정
- **후행**: 모두 통과하면 `ship` (또는 PR 생성)

세트 관계: `manage-skills` (메타-도구) ↔ `verify-implementation` (오케스트레이터). 본 elian-store 안에 함께 번들됨.

---

## What's automated vs what needs your taste

| Claude 가 자동으로 결정 | 사용자가 결정 |
|--------------------------|-------------|
| `.claude/skills/verify-*/SKILL.md` 동적 탐색 | 어떤 verify 스킬만 골라 돌릴지 (인자로 명시) |
| 각 SKILL.md 의 Workflow / Exceptions 파싱 | 자동 수정 적용 범위 (전체 / 개별 / 건너뛰기) |
| Workflow 의 Grep/Glob 명령 실행 | 면제(EXEMPT) 처리 결정의 정확성 |
| Exceptions 매칭 + false positive 제거 | "수정 불가" 표시된 항목의 수동 해결 |
| 수정 권장 (코드 예시 포함) 생성 | 권장 수정의 채택 / 수정 / 거부 |
| Before/After 비교 + 잔여 이슈 식별 | 잔여 이슈 처리 우선순위 |

**파괴적 작업 차단**: `수동 실행 전용` 표식이 있는 verify-* 스킬은 자동 실행 시 SKIP. 사용자가 명시 호출(`/verify-implementation verify-{name}`) 시에만 실행.

---

## Modes

### Mode 1: `run-all` (기본)

프로젝트의 모든 verify-* 스킬 순차 실행 → 통합 보고서 → (이슈 발견 시) 자동 수정 게이트.

**산출물**: 통합 markdown 보고서 + (옵션) 수정된 소스 파일들.

### Mode 2: `run-specific {skill-name}`

특정 verify-* 스킬 1개만 실행. 빠른 검증용. 자동 수정 동일 흐름.

```
/verify-implementation verify-i18n
```

### Mode 3: `dry-run`

실행 없이 발견될 verify-* 목록 + 각 스킬의 Workflow 단계만 보여줌. 디버깅용.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check-skill-discovery.py" .claude/skills/
```

---

## Standing rules

(매 실행에 항상 적용. 절차 아닌 standing instructions.)

### 검사 범위

**현재 작업 디렉토리의 `.claude/skills/verify-*` 만** 대상. 사용자 글로벌 (`~/.claude/skills/`) 은 탐색 안 함. 프로젝트 격리 보장.

### 자기 자신 + manage-skills 제외

- `verify-implementation` 자체는 실행 대상에 포함하지 않음 (재귀 방지)
- `manage-skills` 는 `verify-` 접두사 아니므로 자동 제외

### "수동 실행 전용" 표식

SKILL.md 본문에 `수동 실행 전용` 또는 `수동 실행` 문구가 있는 스킬은 **자동 실행 시 SKIP**. 명시 호출 (Mode 2) 시에만 실행. 파괴적 작업 (DB drop, deploy 등) 보호 장치.

### Exceptions 우선

각 verify-* 스킬의 `Exceptions` 섹션에 해당하는 패턴은 이슈로 보고하지 않음. **검증 스킬의 자체 면제가 절대적**. 오케스트레이터가 임의로 무시 안 함.

---

## Procedure — Mode 1 (run-all)

### Step 1: 동적 탐색

```bash
SKILLS=$(find .claude/skills -maxdepth 2 -name SKILL.md | xargs -I {} dirname {} | xargs -I {} basename {} | grep '^verify-' | grep -v '^verify-implementation$')
```

또는 `Glob pattern=".claude/skills/verify-*/SKILL.md"` (Claude Code Glob 도구).

발견 0개:
```
이 프로젝트에 verify-* 스킬이 없습니다.
`/manage-skills` 를 실행해 프로젝트에 맞는 검증 스킬을 생성하세요.
또는 `.claude/skills/verify-{name}/SKILL.md` 를 직접 작성하세요.
```
종료.

발견 1+개: 각 SKILL.md 의 frontmatter (`name`, `description`) 추출하여 실행 대상 표 표시.

### Step 2: 순차 실행

각 verify-* 마다:

1. SKILL.md 본문에서 "수동 실행 전용" 검사 → 있으면 SKIP + 안내
2. Workflow 섹션 파싱: 검사 항목별 탐지 명령어 (Grep/Glob/Bash) + PASS/FAIL 기준
3. Exceptions 섹션 파싱: 면제 패턴
4. 각 검사 명령어 실행 → 탐지 결과를 PASS/FAIL 기준에 대조 → Exceptions 매칭 면제 처리
5. FAIL 항목 기록: 파일 경로, 라인 번호, 문제 설명, 수정 권장 (코드 예시)
6. 스킬 단위 결과 요약 표시

### Step 3: 통합 보고서

[`references/example-report.md`](references/example-report.md) 형식.

### Step 4: 자동 수정 게이트

이슈 발견 시 `AskUserQuestion`:

```
3개 verify-* 스킬에서 총 7개 이슈 발견. 어떻게 진행할까요?

1. 전체 수정 — 모든 권장 수정 자동 적용
2. 개별 수정 — 각 수정 검토 후 적용
3. 건너뛰기 — 변경 없이 종료
```

### Step 5: 수정 + 재검증

선택에 따라 수정 적용 → 영향 받은 verify-* 만 재실행 → Before/After 비교.

잔여 이슈 (자동 수정 불가) 는 명시 보고:
```
### 잔여 이슈 (수동 해결 필요)
| # | 스킬 | 파일 | 문제 |
|---|------|------|------|
| 1 | verify-business-rules | src/.../OrderService.java:88 | 도메인 로직 수정 필요 — 자동 수정 범위 초과 |
```

---

## Forbidden

- 사용자 글로벌 `~/.claude/skills/` 의 스킬 탐색/실행 — 프로젝트 격리 위반
- "수동 실행 전용" 표식 무시 — 파괴적 작업 안전장치
- 각 verify-* 의 Exceptions 임의 우회 — 자체 면제 절대 우선
- 자기 자신(verify-implementation) 실행 — 무한 재귀
- `manage-skills` 를 verify-* 처럼 실행 — 카테고리 위반

## Known pitfalls

### Pitfall 1: 잘못된 명명 규칙으로 누락

**Symptom**: 사용자가 `validate-payment.md` 라고 명명 → `verify-` 접두사 없어 탐색에서 누락 → 실행 안 됨 → 사용자가 "왜 검증 안 되지" 의아.

**Cause**: 동적 탐색이 `verify-` 접두사 강제.

**Prevention**: Mode 3 (dry-run) 으로 발견 목록을 미리 보여주고, 누락 의심 시 명명 규칙 안내. `manage-skills` 의 `check-skill-frontmatter.py` 가 명명 위반 탐지.

### Pitfall 2: Exceptions 누락으로 false positive

**Symptom**: 테스트 fixture, mock, vendor 등이 검증 위반으로 보고됨.

**Cause**: SKILL.md 의 `Exceptions` 섹션이 비어있거나 부족.

**Prevention**: false positive 발생 시 보고서에 "Exceptions 보강 필요" 힌트 포함. `manage-skills` 로 해당 SKILL.md 의 Exceptions 업데이트 권장.

### Pitfall 3: 자동 수정 후 부작용

**Symptom**: 자동 수정 적용 후 다른 verify-* 스킬에서 새 이슈 발생.

**Cause**: 한 스킬의 권장 수정이 다른 스킬의 규칙과 충돌.

**Prevention**: Step 5 의 재검증은 **모든** verify-* 가 아닌 **이슈 있던 스킬만** 재실행. 단, "전체 수정" 시는 모든 스킬을 1회 더 돌려 cross-check 권장.

---

## Validation

verify-implementation 자체의 동작 검증을 위해 dry-run 도구 제공:

```bash
# 현재 프로젝트의 verify-* 스킬 발견 여부 + frontmatter valid 여부 확인
python3 "${CLAUDE_SKILL_DIR}/scripts/check-skill-discovery.py" .claude/skills/
```

JSON 출력:
```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check-skill-discovery.py" .claude/skills/ --json
```

검증 항목:
1. `.claude/skills/verify-*/SKILL.md` 가 1개 이상 존재
2. 각 SKILL.md 가 frontmatter valid + 필수 필드 충족
3. 자기 자신(verify-implementation) 발견 시 실행 대상에서 제외 표시
4. "수동 실행 전용" 표식 스킬 SKIP 표시

---

## End-of-skill reflection

Mode 1 종료 후 사용자에게 보고할 때, 칭찬하지 말고 패턴을 관찰한다 (3개 항목, hedge 사용):

```
검증 5개 스킬, 7개 이슈 발견 → 자동 수정 6개 + 잔여 1개. 패턴 관찰:

- 7개 중 4개가 verify-i18n (i18n 키 누락) → 새 기능에서 번역 키를 항상 누락하는 경향. /implement 의 i18n 단계가 약할 수 있음.
- verify-api-contract 가 한 번도 실패한 적 없음 (5회 연속 PASS) → 프론트↔백 계약 안정. 다만 실제로 검사 명령어가 의도대로 작동하는지 sample 매뉴얼 확인 권장.
- 잔여 1개 (도메인 로직) 는 수동 해결 필요. 패턴 반복 시 verify-business-rules 의 자동 수정 범위 확장 검토 가능.

다음 권장: 잔여 이슈 1건 해결 후 PR 생성
```

---

## Supporting files

| 파일 | 용도 |
|------|------|
| [`references/example-report.md`](references/example-report.md) | Mode 1 통합 보고서 예시 (3개 verify-* 스킬, BEFORE/AFTER 포함) |
| [`references/skill-orchestration.md`](references/skill-orchestration.md) | 동적 탐색 + Workflow 파싱 + Exceptions 매칭 알고리즘 |
| [`scripts/check-skill-discovery.py`](scripts/check-skill-discovery.py) | dry-run 도구. `--help` / `--json` 지원. stdlib only |

---

## Self-check before claiming PR-ready (사람용)

- [ ] `dry-run` 으로 모든 의도된 verify-* 스킬 발견되는지 확인
- [ ] 누락된 스킬 있으면 명명 (`verify-` 접두사) 또는 위치 (`.claude/skills/`) 점검
- [ ] 자동 수정 적용 후 재검증에서 모두 PASS
- [ ] 잔여 이슈 (수동 해결 항목) 모두 처리됨
- [ ] "수동 실행 전용" 스킬도 필요시 명시 호출로 실행 완료
- [ ] verify-* 스킬의 Exceptions 가 false positive 충분히 커버
