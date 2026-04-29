# 예시: Mode 1 (analyze) 산출물

manage-skills 가 Mode 1 종료 시 출력하는 보고서 형식. 실제 산출물 본보기.

---

## 스킬 유지보수 보고서

### 분석 요약

| 항목 | 수 |
|------|---|
| 변경된 파일 (검사 대상) | 23 |
| 면제된 변경 (lock/generated 등) | 5 |
| 발견된 verify-* 스킬 | 6 |
| 영향 받은 verify-* 스킬 | 3 |
| 제안된 액션 | 7 |
| 그중 사용자 승인 필요 | 2 |

### 검사된 verify-* 스킬

| # | 스킬 | 설명 |
|---|------|------|
| 1 | `verify-api-contract` | 프론트↔백 API 계약 일치 검증 |
| 2 | `verify-i18n` | i18n 키 누락/미사용 검증 |
| 3 | `verify-auth-security` | 인증 로직 보안 검증 |
| 4 | `verify-payment-rules` | 결제 도메인 규칙 검증 |
| 5 | `verify-frontend` | 프론트엔드 lint/typecheck/build |
| 6 | `verify-backend` | 백엔드 spotless/build/test |

### 변경 상세

#### ✅ UPDATE-COVER (4건) — 이미 커버됨, 변경 불필요

| 파일 | 매칭 스킬 | 매칭 신뢰도 |
|------|---------|-----------|
| `mobidoc-front/src/api/auth.ts` | verify-api-contract | 1.0 |
| `mobidoc-server/api-doctor/src/.../AuthController.java` | verify-api-contract | 1.0 |
| `mobidoc-front/src/i18n/locales/ko/auth.json` | verify-i18n | 1.0 |
| `mobidoc-front/src/i18n/locales/en/auth.json` | verify-i18n | 1.0 |

#### ⚠ UPDATE-ADD (1건) — 자동 추가, 사용자 1번 일괄 승인

| 파일 | 대상 스킬 | 액션 |
|------|---------|------|
| `mobidoc-server/.../RefundPolicy.java` | verify-payment-rules | Related Files 에 명시 경로 추가 |

#### ❗ CREATE (1건) — 사용자 승인 필요

```
변경 파일 3개가 모두 새 도메인 (`mobidoc-server/api-doctor/src/.../queue/`):
- queue/MessageProducer.java
- queue/MessageConsumer.java
- queue/DeadLetterHandler.java

기존 어떤 verify-* 도 메시지 큐 도메인 검증 안 함.

제안: 새 verify-queue-conventions 스킬 생성
- consumer/producer 명명 규칙 검증
- dead-letter 핸들러 존재 검증
- 메시지 schema 일치성 검증

승인하시겠습니까? (y/n/modify)
```

#### ⚠ INVALID_REFERENCE (1건)

| 스킬 | 잘못된 참조 |
|------|-----------|
| `verify-frontend` | `mobidoc-front/src/legacy/` (디렉토리 삭제됨) |

→ 자동 stale 제거 (사용자 일괄 승인)

### 영향 없는 스킬

- `verify-auth-security` — 변경된 인증 코드 모두 기존 검사 패턴 안에 있음
- `verify-backend` — 빌드/테스트 검사 스킬 (특정 파일 매핑 없음)

### 면제된 변경 (5건)

- `package-lock.json` — Lock file
- `mobidoc-front/dist/**` (3 files) — Generated
- `.github/workflows/ci.yml` — CI 별도 정책

### 커버되지 않은 변경 (0건)

이번 세션의 모든 변경이 분류됨.

---

## 다음 단계

```
1. UPDATE-ADD 1건 승인 → Mode 2 자동 적용
2. CREATE 1건 (verify-queue-conventions) 승인 후 신규 생성 → Mode 2 자동 적용
3. INVALID_REFERENCE 1건 stale 제거 → Mode 2 자동 적용

위 3건 일괄 진행하시겠습니까? (`/manage-skills repair --auto-confirm-update --create-skip`)
```

---

## 보고서 작성 원칙

- **수치 우선** — "변경됐다" 대신 "23건 중 18건 커버됨"
- **사용자 승인 필요 항목 명확 분리** — UPDATE-ADD vs CREATE
- **면제는 카운트만** — 면제된 5건 일일이 나열 X (필요 시 펼침)
- **다음 단계 제안** — 단순 요약이 아니라 어느 명령으로 다음에 갈지

---

## 보고서를 보고 사용자가 결정해야 할 것

1. **CREATE 후보 승인 여부** — 새 스킬 만들지/말지
2. **모호한 매칭 귀속 (있을 때)** — verify-A vs verify-B
3. **stale 제거 의도 확인** — 정말 삭제 의도였는지
4. **다음 단계** — Mode 2 진행 / 일부만 / 보류
