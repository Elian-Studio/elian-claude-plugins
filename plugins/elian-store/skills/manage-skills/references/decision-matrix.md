# CREATE vs UPDATE vs EXEMPT 판정 매트릭스

manage-skills 의 Mode 1 (analyze) 이 변경 파일별로 다음 매트릭스를 적용해 판정한다.
Mode 2 (repair) 는 이 판정을 받아 실제 액션을 취한다.

---

## 판정 알고리즘 (요약)

```
입력: 변경 파일 X
1. X 가 기존 verify-* 스킬의 Related Files / Workflow 패턴에 매칭?
   - YES, 단일 스킬 매칭 → UPDATE 그 스킬
   - YES, 다수 스킬 매칭 → 사용자 질문 (귀속 결정)
   - NO → 다음
2. X 와 같은 도메인 (디렉토리 / 확장자 / 패턴) 의 다른 변경 파일이 3개 이상?
   - YES → CREATE 새 verify-* 스킬
   - NO → 다음
3. X 가 lock/generated/test fixture/vendor 등 면제 후보?
   - YES → EXEMPT
   - NO → "커버되지 않은 변경" 으로 보고
```

---

## 판정별 세부 기준

### UPDATE — 기존 스킬 도메인에 관련

| 신호 | 액션 |
|------|------|
| X 의 디렉토리가 verify-A 의 Related Files glob 에 매칭 | verify-A.Related Files 에 명시 경로 추가 (또는 glob 가 이미 커버하면 변경 불필요) |
| X 가 verify-A 의 Workflow Grep 패턴에 매칭 | 변경 불필요 (이미 커버) |
| X 가 신규 파일이고 verify-A 가 그 파일 타입 검증 중 | verify-A.Related Files 에 추가 |
| X 가 삭제됐고 verify-A 가 그 파일을 참조 | verify-A 에서 stale path 제거 |
| 새 패턴/규칙이 도입됐고 verify-A 가 같은 도메인 검증 | verify-A.Workflow 에 새 탐지 명령어 추가 |

### CREATE — 새 verify-* 스킬 신규 생성

다음 조건 **모두** 만족 시:

1. X 가 어떤 verify-* 스킬에도 매핑 안 됨
2. X 와 같은 도메인의 변경 파일이 **3개 이상** 누적
3. 그 파일들이 **공통 규칙**을 공유 (검증 가능한 패턴 존재)

도메인 식별 신호:
- 같은 디렉토리 (`mobidoc-front/src/components/payment/*`)
- 같은 확장자 + 의미 (`*.test.ts` 신규 추가 다수)
- 같은 명명 규칙 (`use*Composable.ts` 새 컴포저블 다수)
- 같은 의존성 도입 (새 라이브러리 사용 파일들)

### EXEMPT — 조치 불필요

기본 면제 후보:
- Lock files: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Gemfile.lock`, `*.lock`
- Generated files: `dist/**`, `build/**`, `*.generated.*`, `__generated__/**`
- Test fixtures: `**/fixtures/**`, `**/__fixtures__/**`
- Vendor: `vendor/**`, `node_modules/**`
- CI/CD config: `.github/workflows/**` (별도 정책)
- Minor config bumps: `version` 만 바뀐 `package.json` 등
- CLAUDE.md 자체 (별도 관리)

---

## BEFORE / AFTER 예시

### 예시 1: UPDATE — Related Files 추가

**상황**: 사용자가 `src/lib/auth/jwt.ts` 신규 추가. `verify-auth-security` 가 `src/lib/auth/**` glob 으로 커버.

**BEFORE** (`verify-auth-security/SKILL.md`):
```markdown
## Related Files
| File | Purpose |
|------|---------|
| `src/lib/auth/**/*.ts` | 인증 로직 검사 대상 |
```

**AFTER**: glob 이 이미 커버 → 변경 불필요. `EXEMPT (이미 커버됨)` 로 보고.

---

### 예시 2: UPDATE — 명시 경로 추가

**상황**: `src/payment/refund-policy.ts` 신규 추가. `verify-payment-rules` 가 명시 경로 리스트 사용.

**BEFORE**:
```markdown
## Related Files
| File | Purpose |
|------|---------|
| `src/payment/payment.service.ts` | 결제 서비스 |
| `src/payment/payment.repository.ts` | 결제 저장소 |
```

**AFTER**:
```markdown
## Related Files
| File | Purpose |
|------|---------|
| `src/payment/payment.service.ts` | 결제 서비스 |
| `src/payment/payment.repository.ts` | 결제 저장소 |
| `src/payment/refund-policy.ts` | 환불 정책 검증 (신규 추가) |
```

---

### 예시 3: CREATE — 새 verify-* 스킬

**상황**: 사용자가 `src/queue/` 디렉토리 신설. `consumer.ts`, `producer.ts`, `dead-letter-handler.ts` 3개 파일 생성. 모두 공통 규칙 (메시지 큐 컨벤션) 공유. 기존 어떤 verify-* 도 큐 도메인 검증 안 함.

**판정**: CREATE — `verify-queue-conventions/SKILL.md` 신규 생성

생성된 SKILL.md 골격 (6개 필수 섹션):
```markdown
---
name: verify-queue-conventions
description: 메시지 큐 (consumer/producer/dead-letter) 컨벤션 검증.
disable-model-invocation: true
---

## Purpose
src/queue/** 의 큐 컨벤션 일관성 검증.

## When to Run
큐 관련 코드 변경 후, PR 전.

## Related Files
| File | Purpose |
|------|---------|
| `src/queue/**/*.ts` | 큐 도메인 |

## Workflow
### 1. consumer 명명
- Grep `class \w+Consumer` in src/queue/
- PASS: 모든 consumer 클래스가 `*Consumer` 접미사

### 2. dead-letter 핸들러 존재
- Glob `src/queue/dead-letter-*.ts`
- PASS: 1개 이상 존재

## Output Format
| 검사 | 통과 | 실패 |
|------|-----|-----|
| consumer 명명 | N/M 매칭 | 미스매치 목록 |

## Exceptions
- 테스트 파일 (`*.spec.ts`) — 명명 규칙 면제
- mock consumer (`__mocks__/**`)
```

---

### 예시 4: EXEMPT — 면제

**상황**: `package-lock.json` 변경 (의존성 추가).

**판정**: EXEMPT (lock file). 어떤 스킬도 수정 안 함. 보고서의 "면제된 변경" 섹션에만 기록.

---

## 판정 결과 다섯 가지

| 결과 | 의미 |
|------|------|
| `UPDATE-COVER` | 기존 스킬이 이미 커버 (변경 불필요) |
| `UPDATE-ADD` | Related Files 또는 Workflow 에 추가 필요 |
| `UPDATE-REMOVE` | stale 항목 제거 필요 |
| `CREATE` | 새 verify-* 스킬 생성 |
| `EXEMPT` | 조치 불필요 |
| `UNCOVERED` | 매핑 안 되고 CREATE 조건도 미달 (3개 미만) — 사용자 검토 |

---

## 사용자 결정이 필요한 상황 (자동 판정 금지)

다음은 항상 `AskUserQuestion` 으로 사용자 의도 확인:

1. **다중 스킬 매칭** — X 가 verify-A, verify-B 양쪽 패턴 매칭. 어디 귀속할지
2. **CREATE 후보** — 항상 사용자 승인 게이트
3. **모호한 도메인** — 같은 디렉토리이지만 의미가 다른 파일들 (예: `src/utils/` 안에 인증/암호화/캐시 헬퍼 혼재)
4. **stale path 제거** — 삭제로 인한 제거는 의도된 삭제인지 사용자 확인
5. **검증 명령어 변경** — Workflow 의 Grep/Glob 패턴 수정은 의도 영향 큼
