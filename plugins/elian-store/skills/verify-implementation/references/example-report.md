# 예시: Mode 1 통합 보고서

verify-implementation 가 모든 verify-* 스킬 실행 후 출력하는 통합 보고서 본보기.

---

## 구현 검증

현재 프로젝트에서 5개의 검증 스킬을 발견했습니다:

| # | 스킬 | 설명 |
|---|------|------|
| 1 | verify-api-contract | 프론트↔백 API 계약 (path, method, DTO) 일치 검증 |
| 2 | verify-i18n | i18n 키 누락/미사용/upload.json 무결성 검증 |
| 3 | verify-frontend | Vue 3/TypeScript lint, typecheck, build 검증 |
| 4 | verify-backend | Java/Spring spotless, build, test 검증 |
| 5 | verify-business-rules | 도메인 비즈니스 규칙 검증 |

검증 시작...

---

## 진행 상황

### verify-api-contract 검증 완료

- 검사 항목: 8개
- 통과: 8개
- 이슈: 0개
- 면제: 0개

### verify-i18n 검증 완료

- 검사 항목: 4개
- 통과: 0개
- 이슈: 4개
- 면제: 12개 (`__fixtures__/**`, deprecated keys)

### verify-frontend 검증 완료

- 검사 항목: 3개 (lint / typecheck / build)
- 통과: 2개
- 이슈: 1개 (lint)
- 면제: 0개

### verify-backend 검증 완료

- 검사 항목: 3개 (spotless / build / test)
- 통과: 3개
- 이슈: 0개
- 면제: 0개

### verify-business-rules 검증 완료

- 검사 항목: 6개
- 통과: 4개
- 이슈: 2개
- 면제: 1개 (legacy migration)

---

## 구현 검증 보고서

### 요약

| 검증 스킬 | 상태 | 이슈 수 | 상세 |
|-----------|------|---------|------|
| verify-api-contract | ✅ PASS | 0 | 모든 endpoint 매칭 |
| verify-i18n | ❌ FAIL | 4 | 키 누락 3, 미사용 1 |
| verify-frontend | ❌ FAIL | 1 | lint 위반 1 |
| verify-backend | ✅ PASS | 0 | 모든 검사 통과 |
| verify-business-rules | ❌ FAIL | 2 | 도메인 규칙 위반 2 |

**발견된 총 이슈: 7개**

---

### 발견된 이슈

| # | 스킬 | 파일 | 문제 | 수정 방법 |
|---|------|------|------|-----------|
| 1 | verify-i18n | `front/src/views/Order/OrderList.vue:42` | i18n 키 `order.list.empty` 미존재 | `upload.json` 에 `order.list.empty: "주문 내역이 없습니다"` 추가 |
| 2 | verify-i18n | `front/src/views/Order/OrderDetail.vue:18` | i18n 키 `order.detail.title` 미존재 | 추가 |
| 3 | verify-i18n | `front/src/components/RefundModal.vue:25` | i18n 키 `refund.modal.confirm` 미존재 | 추가 |
| 4 | verify-i18n | `front/src/legacy/oldOrder.vue:12` | i18n 키 `legacy.unused` 미사용 | upload.json 에서 제거 또는 주석 처리 |
| 5 | verify-frontend | `front/src/api/order.ts:55` | ESLint `no-unused-vars` — `tempVar` 미사용 | 제거 |
| 6 | verify-business-rules | `server/.../OrderService.java:88` | 환불 정책 위반 — 7일 초과 주문 환불 가능 | `@RefundPolicy(maxDays=7)` 어노테이션 추가 |
| 7 | verify-business-rules | `server/.../PaymentService.java:120` | 결제 실패 시 사용자 알림 누락 | `notifyUser` 호출 추가 후 catch 블록 검토 |

---

### 수정 옵션

**7개 이슈가 발견되었습니다. 어떻게 진행할까요?**

1. **전체 수정** - 모든 권장 수정사항을 자동으로 적용
2. **개별 수정** - 각 수정사항을 하나씩 검토 후 적용
3. **건너뛰기** - 변경 없이 종료

> [사용자가 "1. 전체 수정" 선택]

---

## 수정 적용 중...

- [1/7] verify-i18n: `upload.json` 에 3개 키 추가
- [2/7] verify-i18n: `legacy.unused` 키 제거
- [3/7] verify-frontend: `front/src/api/order.ts` 의 `tempVar` 제거
- [4/7] verify-business-rules: `OrderService.java` 에 `@RefundPolicy` 추가
- [5/7] verify-business-rules: **자동 수정 불가 — 도메인 로직 영향. 사용자 검토 필요**

5건 자동 수정 / 2건 잔여.

---

## 수정 후 재검증

이슈가 있었던 스킬을 다시 실행합니다...

| 검증 스킬 | 수정 전 | 수정 후 |
|-----------|---------|---------|
| verify-i18n | 4개 이슈 | ✅ PASS |
| verify-frontend | 1개 이슈 | ✅ PASS |
| verify-business-rules | 2개 이슈 | 1개 잔여 |

5개 자동 수정 → 모두 PASS. 1개 잔여 이슈 (도메인 로직) 는 수동 해결 필요.

---

### 잔여 이슈 (수동 해결 필요)

| # | 스킬 | 파일 | 문제 |
|---|------|------|------|
| 1 | verify-business-rules | `server/.../PaymentService.java:120` | 결제 실패 시 사용자 알림 누락 — 자동 수정 불가, 도메인 로직 영향 |

수동으로 해결한 후 `/elian-store:verify-implementation verify-business-rules` 를 다시 실행하세요.

---

## End-of-skill reflection

검증 5개 스킬, 7개 이슈 발견 → 자동 수정 5개 + 잔여 2개 → 최종 1개 수동. 패턴 관찰:

- 7개 중 4개가 verify-i18n (i18n 키 누락) → 새 기능 구현 시 번역 키를 자주 누락하는 경향. /implement 의 i18n 단계가 약할 수 있음. verify-i18n 의 Workflow 가 새 키 자동 생성까지 확장될 수 있는지 검토 가능.
- verify-api-contract 와 verify-backend 는 PASS — 백엔드 안정. 프론트엔드 변경 영향이 더 크게 나오는 패턴.
- 잔여 1개 (도메인 로직) 는 수동 해결 필요. 결제 실패 알림은 코드보다 정책 결정 영역이라 자동 수정 부적합. /brainstorm 으로 정책 확정 후 코드 반영 권장.

다음 권장: 잔여 1개 해결 후 PR 생성
