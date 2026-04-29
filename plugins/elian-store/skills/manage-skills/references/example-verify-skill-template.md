# 새 verify-* 스킬 템플릿 — 6개 필수 섹션

manage-skills 의 Mode 2 (CREATE) 시 이 템플릿을 채워서 신규 verify-* 스킬을 생성한다.
모든 verify-* 스킬은 이 6개 섹션을 갖춰야 한다 (manage-skills 의 standing rules 참조).

---

## 템플릿

````markdown
---
name: verify-{kebab-case-name}
description: "{도메인 이름} {검증 목적}. {간단 출력 형태}."
disable-model-invocation: true
argument-hint: "[Optional: focus area]"
---

# verify-{name}

## Purpose

{이 스킬이 무엇을 검증하는지 1-2문장. 무엇을 보장하는가}

## When to Run

- {실행 시점 1: 예) 새로운 API endpoint 추가 후}
- {실행 시점 2: 예) PR 생성 전}
- {실행 시점 3: 예) {도메인} 코드 변경 후}

## Related Files

| File | Purpose |
|------|---------|
| `{경로 또는 glob 1}` | {역할} |
| `{경로 또는 glob 2}` | {역할} |

## Workflow

### 1. {검사 항목 1}

**탐지**:
```bash
{Grep / Glob / Bash 명령}
```

**PASS 기준**: {조건}

**FAIL 시**: {조치 또는 보고}

### 2. {검사 항목 2}

(같은 형식)

### 3. {...}

## Output Format

```markdown
## {스킬 이름} 검증 결과

| 검사 | 통과 | 실패 |
|------|-----|-----|
| 1. {검사 1} | {N개} | {위반 목록} |
| 2. {검사 2} | {N개} | {위반 목록} |

총: {Y}/{Z} 통과
```

또는 JSON:
```json
{
  "skill": "verify-{name}",
  "checks": [
    {"id": 1, "name": "{검사 1}", "pass": N, "fail": [...]},
    {"id": 2, "name": "{검사 2}", "pass": N, "fail": [...]}
  ]
}
```

## Exceptions

다음은 위반이 아닙니다:

1. **{면제 1}** — {이유}
2. **{면제 2}** — {이유}
3. **{면제 3}** — {이유}
````

---

## 채움 예시 — `verify-queue-conventions`

````markdown
---
name: verify-queue-conventions
description: "메시지 큐 (consumer/producer/dead-letter) 컨벤션 검증. 명명·에러 핸들링·schema 일치 일관성 보장."
disable-model-invocation: true
argument-hint: "[Optional: queue/{name}]"
---

# verify-queue-conventions

## Purpose

`src/queue/**` 의 메시지 큐 코드가 팀 컨벤션을 따르는지 검증한다.
consumer/producer 명명, dead-letter 핸들러 존재, 메시지 schema 일관성을 보장한다.

## When to Run

- 새로운 큐 consumer 또는 producer 추가 후
- dead-letter 핸들러 변경 후
- PR 생성 전

## Related Files

| File | Purpose |
|------|---------|
| `src/queue/**/*.ts` | 큐 도메인 |
| `src/queue/dead-letter-*.ts` | dead-letter 핸들러 |
| `src/queue/schemas/**/*.ts` | 메시지 schema |

## Workflow

### 1. consumer 명명 규칙

**탐지**:
```bash
grep -rE 'class\s+\w+' src/queue/ | grep -v Consumer | grep -v Producer
```

**PASS 기준**: `src/queue/` 안의 모든 클래스가 `*Consumer` 또는 `*Producer` 접미사

**FAIL 시**: 위반 클래스 목록 + 권장 이름 제안

### 2. dead-letter 핸들러 존재

**탐지**:
```bash
ls src/queue/dead-letter-*.ts 2>/dev/null
```

**PASS 기준**: 1개 이상 존재

**FAIL 시**: dead-letter 핸들러 부재 — 큐별로 추가 권장

### 3. 메시지 schema 일치성

**탐지**:
```bash
grep -lr 'export\s\+interface\s\+\w\+Message' src/queue/schemas/ | xargs grep -l '@deprecated'
```

**PASS 기준**: deprecated schema 가 사용처 0개

**FAIL 시**: deprecated schema 사용 위치 목록

## Output Format

```markdown
## verify-queue-conventions 검증 결과

| 검사 | 통과 | 실패 |
|------|-----|-----|
| 1. consumer 명명 | 5/5 | — |
| 2. dead-letter 핸들러 | 1/1 | — |
| 3. schema 일치 | 8/8 | — |

총: 14/14 통과
```

## Exceptions

다음은 위반이 아닙니다:

1. **테스트 파일** (`*.spec.ts`, `*.test.ts`) — 명명 규칙 면제
2. **mock consumer/producer** (`__mocks__/**`) — 명명 규칙 면제
3. **schema migration scripts** (`src/queue/schemas/migrations/**`) — deprecated 일시 사용 허용
````

---

## 작성 시 주의사항

### 1. 탐지 명령어가 실제로 작동해야 한다

```bash
# Bad — Grep 인용 누락
grep -rE class \w+Consumer src/queue/

# Good — 인용 + 정확한 정규식
grep -rE 'class\s+\w+Consumer' src/queue/
```

### 2. PASS 기준이 명시적이어야 한다

```markdown
# Bad — "잘 작동하면 OK"
PASS 기준: 큐 시스템이 정상 작동

# Good — 측정 가능
PASS 기준: 모든 consumer 클래스가 `*Consumer` 접미사 + dead-letter 핸들러 1+ 존재
```

### 3. Exceptions 가 현실적이어야 한다

```markdown
# Bad — 모든 케이스 면제 (검증 무력화)
1. **모든 테스트** — 면제
2. **모든 generated** — 면제
3. **모든 vendor** — 면제
4. **모든 deprecated** — 면제

# Good — 구체 케이스 + 이유
1. **테스트 fixture** (`**/fixtures/queue-*.json`) — 검증 대상 아님 (테스트 데이터)
2. **migration scripts** (`src/queue/schemas/migrations/**`) — 일시적 호환 코드
```

---

## CREATE 시 manage-skills 가 자동으로 채우는 부분 vs 사용자 입력

| 항목 | 자동 / 사용자 |
|------|------------|
| `name` | 자동 (도메인에서 추출) |
| `description` 첫 문장 | 자동 (placeholder) → 사용자 검토 권장 |
| `Purpose` | 자동 placeholder → **사용자 작성 필수** |
| `When to Run` | 자동 placeholder |
| `Related Files` | 자동 (변경 파일에서 도출한 패턴) |
| `Workflow` 검사 항목 | **사용자 작성 필수** (탐지 명령어 + PASS 기준) |
| `Output Format` | 자동 표 템플릿 |
| `Exceptions` | 자동 기본 면제 + **사용자 추가 검토** |

manage-skills 는 골격만 만들고 실제 검사 로직은 사용자가 채우는 것이 원칙. 자동 생성된 검사 명령어는 placeholder.
