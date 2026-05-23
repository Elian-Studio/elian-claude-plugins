# Other Feature Examples — 로그인 외 적용 사례

같은 9 Phase 흐름을 다른 기능에 적용할 때의 위험도 / 추천 Phase / 중점 검토 항목 가이드.

---

## 1. 파일 업로드 기능

**위험도**: MEDIUM 또는 HIGH (악성 파일 / 권한 / 저장소 비용에 따라)

**중점 검토**:
- 파일 크기 제한
- 확장자 + MIME 타입 검증 (두 가지 모두, 한 가지만으로는 우회 가능)
- 악성 파일 처리 (svg XSS, zip bomb, polyglot 등)
- 저장 위치 (public/private bucket, path traversal 방지)
- 접근 권한 (업로더 vs 다운로더)
- 업로드 실패 / 부분 업로드 처리
- 다운로드 권한 (signed URL, 만료)
- 바이러스 스캔 필요 여부 (HIGH 위험이면 필수)

**추천 전략**:
```
Phase 1 (Framing, 위험도 결정)
+ Phase 3 (SDD — 확장자/MIME/크기/위치/권한 명시)
+ Phase 5 (AI-TDD — 악성 파일 시나리오 포함)
+ Phase 6 (Context — 기존 스토리지 헬퍼·signed URL 헬퍼)
+ Phase 8 (보안 리뷰)
```

DDD 는 보통 skip (도메인 정책 단순).

---

## 2. 주문 취소 기능

**위험도**: HIGH

**중점 검토**:
- 취소 가능 상태 (결제완료 / 배송준비 / 배송중 / 배송완료 어디까지?)
- 결제 취소 (PG 환불 호출, 부분 환불, 환불 실패 처리)
- 재고 복구 (취소 시점에 재고가 다시 잠겨야 하는가)
- 쿠폰 복원 (사용된 쿠폰을 다시 사용 가능하게 할지)
- 배송 상태 (이미 출고된 경우 운송장 회수 정책)
- 환불 정책 (전액 / 부분 / 위약금)
- 관리자 강제 취소 (사용자 동의 없이 가능한가, 감사 로그)
- 이벤트 발행 (OrderCancelled → 다른 도메인이 구독)

**추천 전략**:
```
Phase 1 (Framing — 정책 복잡도 HIGH)
+ Phase 2 (BDD — 각 상태별 시나리오)
+ Phase 3 (SDD — 환불·재고·쿠폰 정책)
+ Phase 4 (DDD — OrderCancellation 도메인 서비스, RefundPolicy 객체)
+ Phase 5 (AI-TDD — 상태 전환 + 외부 호출 실패 시나리오)
+ Phase 6 (Context — 결제 PG 어댑터, 재고 서비스, 이벤트 버스)
+ Phase 7 (Agentic Task)
+ Phase 8 (Review — 트랜잭션 일관성·이벤트 순서 검증)
+ Phase 9 (SPDD)
```

전체 9 Phase 권장.

---

## 3. 게시글 작성 기능

**위험도**: LOW 또는 MEDIUM

**중점 검토**:
- 입력 검증 (제목·본문 길이, HTML 허용 여부)
- 권한 (로그인 사용자만? 익명 가능?)
- 임시 저장 (draft, 자동 저장 주기)
- 첨부파일 (별도 파일 업로드 기능 호출)
- 금칙어 (정규식 vs 모델 기반)
- XSS 방지 (sanitize 라이브러리, 허용 태그 화이트리스트)
- 공개 범위 (public / followers / private)

**추천 전략**:
```
Phase 3 (SDD — 입력·출력·권한 명세)
+ Phase 5 (AI-TDD — XSS·금칙어·권한 테스트)
+ Phase 6 (Context — sanitize 헬퍼·권한 미들웨어)
```

LOW 위험이면 Phase 1·2·4·9 는 생략 가능. MEDIUM (XSS 가능성 + 권한 분기 복잡) 이면 Phase 2 BDD 추가.

---

## 4. 검색 필터 기능

**위험도**: LOW 또는 MEDIUM

**중점 검토**:
- 검색 인덱싱 (DB FTS vs Elasticsearch vs Algolia)
- 필터 조합 (AND / OR, 다중 선택)
- 페이지네이션 (offset vs cursor)
- N+1 쿼리 방지 (관련 데이터 join 또는 batch load)
- 결과 정렬 (관련도 vs 최신순)
- 빈 결과 UX
- 검색 로그 (개인정보·키워드 마스킹)
- 검색 결과 캐시 정책

**추천 전략**:
```
Phase 3 (SDD — 쿼리 파라미터·응답·정렬)
+ Phase 5 (AI-TDD — N+1, 페이지네이션 경계 케이스)
+ Phase 6 (Context — 검색 인덱스 헬퍼, 캐시 레이어)
```

---

## 5. 알림 발송 기능

**위험도**: MEDIUM (사용자 동의·발송 비용·반복 트리거 위험)

**중점 검토**:
- 발송 채널 (push / SMS / email / in-app)
- 발송 동의 (opt-in / opt-out, 채널별 별도)
- 발송 시점 (즉시 / 예약 / 큐 처리)
- 실패 처리 (재시도, dead letter queue)
- 발송 비용 (SMS 비용 통제)
- Rate limiting (사용자당 / 채널당)
- 템플릿 관리 (i18n, 변수 치환, A/B 테스트)
- 발송 이력·감사 로그
- 비밀값 마스킹 (OTP 등은 로그에 안 남김)

**추천 전략**:
```
Phase 1 (Framing — 채널·동의 정책 명확화)
+ Phase 3 (SDD — 발송 정책·재시도)
+ Phase 4 (DDD — NotificationPolicy, Channel, Template)
+ Phase 5 (AI-TDD — 동의 안 된 사용자 차단, retry idempotency)
+ Phase 6 (Context — 큐·채널 어댑터)
+ Phase 7 (Agentic Task)
+ Phase 8 (Review — 비용·로깅·rate limit)
```

---

## 6. 관리자 권한 관리 기능

**위험도**: HIGH

**중점 검토**:
- 권한 모델 (RBAC / ABAC / ReBAC 중 선택)
- 권한 부여·회수 흐름
- 권한 변경 감사 로그 (필수)
- 권한 위임·임시 권한
- 권한 캐시·만료
- 관리자 본인 권한 회수 방지 (lock-out)
- API 게이트웨이 인가 vs 서비스 내부 인가
- 권한 매트릭스 문서

**추천 전략**:
```
Phase 1-9 전체 + 보안 검토 강화
+ 권한 매트릭스를 Phase 3 SDD 산출물로 명문화
+ Phase 5 AI-TDD 에서 권한 우회 시도 시나리오 필수
```

---

## 7. 회원가입 기능

**위험도**: HIGH (개인정보 수집·인증 흐름)

**중점 검토**:
- 입력 검증 (이메일 형식·중복·비밀번호 정책)
- 비밀번호 저장 (Argon2id / scrypt / bcrypt)
- 이메일 인증 (인증 토큰 만료·재발송 제한)
- 약관 동의 (필수·선택·버전 추적)
- 프로필 정보 (수집 최소화 원칙)
- 가입 직후 자동 로그인 vs 별도 로그인
- 가입 실패 메시지 (사용자 열거 방지)
- 봇 차단 (CAPTCHA, rate limit)

**추천 전략**: Phase 1-9 전체. 로그인과 묶어서 같은 SPDD 자산화 권장.

---

## 패턴 요약

| 기능 종류 | 일반 위험도 | 권장 Phase |
|---|---|---|
| 인증·결제·권한·개인정보 | HIGH | Phase 1-9 전체 |
| 복잡 정책 (주문 / 알림 / 권한) | MEDIUM-HIGH | Phase 1-9 전체 |
| 일반 CRUD (게시글 / 검색) | LOW-MEDIUM | Phase 3 + 5 + 6 |
| 프로토타입·데모 | LOW | Phase 1 + 5 (간단 테스트) |

**판단 기준**:
- 외부 시스템 (결제·이메일·SMS) 호출 있나? → 위험도 ↑
- 비밀번호·세션·토큰·OTP 다루나? → HIGH 고정
- 정책이 여러 도메인에 걸치나? (주문 ↔ 결제 ↔ 재고) → DDD 권장
- 5분 안에 정책 설명 가능한가? → Yes 면 LOW-MEDIUM, No 면 MEDIUM-HIGH
