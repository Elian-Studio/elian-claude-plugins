# Stage Prompts — Phase별 하위 프롬프트 9개

마스터 프롬프트 한 번에 처리하기 어렵거나 한 Phase 만 다듬고 싶을 때 사용. Phase 순서대로 호출하면 각 산출물이 다음 Phase 입력이 된다.

---

## Phase 1: Feature Framing 프롬프트

```text
다음 기능을 개발하기 전에 Feature Framing을 해줘.

기능 이름: [FEATURE_NAME]
기능 설명: [FEATURE_DESCRIPTION]
사용자 유형: [USER_TYPES]
비즈니스 목적: [BUSINESS_GOAL]
기술 스택: [TECH_STACK]
기존 제약: [CONSTRAINTS]

다음 항목으로 정리해줘.

1. 이 기능의 핵심 의도
2. 주요 사용자와 사용 상황
3. 성공 기준
4. 실패하면 안 되는 조건
5. 예상되는 엣지 케이스
6. 보안/권한/개인정보/성능/접근성 위험도
7. 이 기능에 적합한 개발 전략 조합
8. 구현 전에 반드시 확인해야 할 질문
```

---

## Phase 2: BDD 프롬프트

```text
다음 기능에 대해 BDD 시나리오를 작성해줘.

기능 이름: [FEATURE_NAME]
기능 설명: [FEATURE_DESCRIPTION]
사용자 유형: [USER_TYPES]
정책 또는 제약: [POLICIES]

요구사항:
- Given-When-Then 형식으로 작성한다.
- 정상 흐름, 실패 흐름, 예외 흐름을 모두 포함한다.
- 기획자, QA, 개발자가 함께 읽고 합의할 수 있는 문장으로 작성한다.
- 구현 세부사항보다 사용자 행동과 결과에 집중한다.
- 모호한 정책은 질문 또는 가정으로 분리한다.

출력 형식:
1. Feature 설명
2. Scenario 목록
3. 아직 합의가 필요한 정책 질문
```

---

## Phase 3: SDD 프롬프트

```text
다음 기능에 대해 Spec-Driven Development용 기능 명세서를 작성해줘.

기능 이름: [FEATURE_NAME]
기능 설명: [FEATURE_DESCRIPTION]
BDD 시나리오: [BDD_SCENARIOS]
기술 스택: [TECH_STACK]
기존 코드 제약: [CODE_CONSTRAINTS]

명세서에는 다음을 포함해줘.

1. 기능 목적
2. 범위와 비범위
3. 사용자 역할과 권한
4. 입력값
5. 출력값
6. API 명세 또는 UI 동작 명세
7. 상태 변화
8. 에러 정책
9. 엣지 케이스
10. 보안 요구사항
11. 성능 요구사항
12. 접근성 요구사항
13. 로깅/모니터링 요구사항
14. 테스트해야 할 항목
15. 완료 기준

주의사항:
- AI가 임의로 추측할 만한 부분을 명시적으로 적어라.
- 구현하지 말아야 할 범위도 Out of Scope로 분리하라.
- 리뷰자가 명세와 구현을 비교할 수 있게 작성하라.
```

---

## Phase 4: DDD 프롬프트

```text
다음 기능에 DDD가 필요한지 판단하고, 필요하다면 도메인 모델을 제안해줘.

기능 이름: [FEATURE_NAME]
기능 설명: [FEATURE_DESCRIPTION]
비즈니스 규칙: [BUSINESS_RULES]
기능 명세: [SPEC]

출력 형식:
1. DDD 적용 필요성 판단
2. 핵심 도메인인지, 지원 도메인인지, 일반 하위 도메인인지 판단
3. 주요 도메인 개념
4. Entity, Value Object, Domain Service, Repository 후보
5. Bounded Context 후보
6. 도메인 이벤트 후보
7. 피해야 할 설계 과잉
8. 간단한 코드 구조 예시

주의사항:
- 단순 CRUD라면 DDD를 과하게 적용하지 말라고 말해라.
- 복잡한 정책이 있는 경우 정책 객체나 도메인 서비스를 제안해라.
```

---

## Phase 5: AI-TDD 프롬프트

```text
다음 기능을 구현하기 전에 AI-TDD 방식으로 테스트 계획을 작성해줘.

기능 이름: [FEATURE_NAME]
기능 명세: [SPEC]
도메인 모델: [DOMAIN_MODEL]
기술 스택: [TECH_STACK]

요구사항:
- 구현보다 테스트를 먼저 설계한다.
- 정상 케이스, 실패 케이스, 엣지 케이스, 회귀 테스트를 포함한다.
- 보안/권한/개인정보 관련 기능이면 악용 시나리오도 포함한다.
- 각 테스트가 검증하는 요구사항을 명시한다.
- AI가 테스트를 약화하거나 삭제하지 못하도록 보호 규칙을 적는다.

출력 형식:
1. 테스트 전략 요약
2. 테스트 매트릭스
3. 우선순위가 높은 테스트
4. 단위 테스트 후보
5. 통합 테스트 후보
6. E2E 테스트 후보
7. 보안 또는 권한 테스트 후보
8. 회귀 테스트 후보
9. AI 구현 시 테스트 변경 금지 규칙
```

---

## Phase 6: Context Engineering 프롬프트

```text
다음 기능을 AI에게 구현시키기 전에 Context Engineering 패키지를 만들어줘.

기능 이름: [FEATURE_NAME]
기능 명세: [SPEC]
기술 스택: [TECH_STACK]
저장소 구조 또는 관련 파일 목록: [REPOSITORY_CONTEXT]
코딩 규칙: [CODING_RULES]
테스트 명령: [TEST_COMMANDS]
제약사항: [CONSTRAINTS]

다음 항목으로 정리해줘.

1. AI가 반드시 읽어야 할 문서
2. AI가 반드시 참고해야 할 코드 파일
3. AI가 참고하지 않아도 되는 파일
4. 기존 아키텍처 규칙
5. 구현 시 반드시 지켜야 할 제약
6. 금지되는 변경
7. 테스트와 검증 명령
8. AI에게 전달할 최종 컨텍스트 요약

주의사항:
- 관련 없는 파일을 많이 주지 마라.
- AI가 기존 구조를 깨지 않도록 현재 프로젝트의 규칙을 강조하라.
- "더 많은 정보"가 아니라 "필요한 정보"를 선별하라.
```

---

## Phase 7: Agentic Coding 프롬프트

```text
다음 기능을 AI 에이전트에게 작업 티켓 또는 PR 단위로 위임할 수 있도록 구현 지시문을 작성해줘.

기능 이름: [FEATURE_NAME]
기능 명세: [SPEC]
테스트 계획: [TEST_PLAN]
컨텍스트 패키지: [CONTEXT_PACKAGE]
위험도: [RISK_LEVEL]

출력은 다음 형식을 따른다.

# Task: [FEATURE_NAME]

## Goal
이 작업의 목표를 설명한다.

## Scope
구현해야 할 범위를 나열한다.

## Out of Scope
이번 작업에서 제외할 범위를 나열한다.

## Acceptance Criteria
완료 조건을 구체적으로 나열한다.

## Required Context
AI가 참고해야 할 문서와 파일을 나열한다.

## Constraints
변경 금지 사항과 아키텍처 제약을 적는다.

## Test Requirements
반드시 추가하거나 통과해야 할 테스트를 적는다.

## Review Notes
리뷰어가 특히 확인해야 할 위험 요소를 적는다.

주의사항:
- AI가 범위를 넓히지 않도록 Out of Scope를 명확히 적어라.
- PR 설명에 포함해야 할 테스트 결과와 변경 요약도 요구하라.
```

---

## Phase 8: Review 프롬프트

```text
다음 기능 구현 결과를 리뷰해줘.

기능 명세: [SPEC]
테스트 계획: [TEST_PLAN]
구현 요약 또는 diff: [IMPLEMENTATION_DIFF]
테스트 결과: [TEST_RESULTS]
위험도: [RISK_LEVEL]

다음 관점에서 리뷰해줘.

1. 명세 충족 여부
2. BDD 시나리오 충족 여부
3. 테스트 충분성
4. 도메인 모델 적합성
5. 보안 위험
6. 권한/개인정보 위험
7. 성능 위험
8. 접근성 위험
9. 유지보수성
10. 불필요한 변경 여부
11. 병합 차단 이슈
12. 개선 제안

출력 형식:
- 요약 판단: Merge 가능 / 수정 후 Merge / Merge 금지
- 주요 문제
- 세부 리뷰
- 추가 테스트 제안
- 최종 권고
```

---

## Phase 9: SPDD Archive 프롬프트

```text
이번 기능 개발에 사용한 프롬프트와 산출물을 SPDD 기록으로 정리해줘.

기능 이름: [FEATURE_NAME]
사용한 프롬프트: [PROMPTS]
명세: [SPEC]
테스트 계획: [TEST_PLAN]
구현 요약: [IMPLEMENTATION_SUMMARY]
리뷰 결과: [REVIEW_RESULT]
최종 결정: [FINAL_DECISION]

다음 형식으로 정리해줘.

1. 기능 개요
2. 사용한 개발 전략 조합
3. 핵심 프롬프트
4. 중요한 가정
5. 생성된 산출물
6. 테스트 결과
7. 리뷰에서 발견된 문제
8. 다음에 재사용할 수 있는 프롬프트 패턴
9. 다음에는 피해야 할 안티패턴
```
