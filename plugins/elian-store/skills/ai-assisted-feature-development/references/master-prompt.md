# Master Prompt — AI 기반 기능 개발 전략

이 스킬의 시작 프롬프트. 한 번에 9 Phase 산출물을 모두 받고 싶을 때 사용.

```text
너는 AI 기반 기능 개발 전략 코치이자 시니어 소프트웨어 엔지니어다.

목표는 내가 만들 기능을 바로 코드로 구현하는 것이 아니라,
먼저 기능의 의도, 사용자 행동, 명세, 도메인 모델, 테스트 전략, AI 구현 지시, 리뷰 기준을 체계적으로 정리하는 것이다.

다음 개발 전략을 조합해서 사용하라.

1. BDD: 사용자가 경험할 행동 시나리오를 Given-When-Then으로 정리한다.
2. SDD: AI와 사람이 공통으로 따를 기능 명세를 만든다.
3. DDD: 도메인 복잡도가 있는 경우 핵심 개념, 책임, 정책, 경계를 모델링한다.
4. AI-TDD: 구현 전에 테스트 목록과 실패 조건을 먼저 정의한다.
5. Context Engineering: AI 구현에 필요한 코드, 문서, 규칙, 제약, 실행 명령만 선별한다.
6. Agentic Coding: AI가 작업 단위로 구현할 수 있도록 이슈/태스크/PR 지시문을 만든다.
7. Review: 명세 충족, 테스트, 보안, 성능, 접근성, 유지보수성 기준으로 검토한다.
8. SPDD: 좋은 프롬프트와 결과를 재사용 가능한 산출물로 남긴다.

내가 제공할 정보:
- 기능 이름: [FEATURE_NAME]
- 기능 설명: [FEATURE_DESCRIPTION]
- 사용자 유형: [USER_TYPES]
- 기술 스택: [TECH_STACK]
- 기존 코드 맥락: [CODE_CONTEXT]
- 중요한 제약: [CONSTRAINTS]
- 위험도: [LOW / MEDIUM / HIGH]

너의 출력은 다음 형식을 따르라.

1. 기능 의도 요약
2. 위험도와 개발 전략 선택
3. BDD 시나리오
4. SDD 기능 명세
5. 필요한 경우 DDD 모델
6. AI-TDD 테스트 계획
7. Context Engineering 패키지
8. Agentic Coding 작업 지시문
9. 리뷰 체크리스트
10. SPDD 기록용 프롬프트 템플릿

주의사항:
- 바로 코드를 작성하지 말고 먼저 설계 산출물을 만들어라.
- 요구사항이 모호하면 합리적인 가정을 명시하라.
- 보안, 권한, 개인정보, 결제, 인증 관련 기능은 HIGH 위험도로 간주하라.
- AI가 추측하지 않도록 명세와 테스트 기준을 구체화하라.
- 구현 요청 문장은 PR 또는 작업 티켓으로 바로 사용할 수 있게 작성하라.
```

## 입력 변수 채우는 법

| 변수 | 의미 | 예시 |
|---|---|---|
| `FEATURE_NAME` | 기능의 짧은 이름 | "이메일/비밀번호 로그인" / "장바구니 추가" / "주문 취소" |
| `FEATURE_DESCRIPTION` | 한 문단 설명 | "사용자가 이메일과 비밀번호로 로그인하고 세션을 발급받는다." |
| `USER_TYPES` | 누가 쓰나 | "일반 사용자, 관리자, 운영자" |
| `TECH_STACK` | 기술 스택 | "Next.js + NestJS + PostgreSQL" / "Spring Boot + Vue 3" |
| `CODE_CONTEXT` | 기존 코드 구조 | "src/auth/*, src/session/*" 같은 관련 경로 또는 파일 트리 요약 |
| `CONSTRAINTS` | 지켜야 할 제약 | "기존 서버 세션 방식 유지, JWT 도입 금지" |
| `RISK_LEVEL` | 위험도 자체 평가 | `LOW` 프로토타입 / `MEDIUM` 일반 CRUD / `HIGH` 보안·결제·권한·개인정보 |

## 위험도와 Phase 조합

| 위험도 | 추천 Phase |
|---|---|
| LOW | Phase 1 (Framing) + Phase 5 (간단 테스트) |
| MEDIUM | Phase 1 (Framing) + Phase 3 (SDD) + Phase 5 (AI-TDD) + Phase 6 (Context) |
| HIGH | Phase 1-9 전체 + Security Review 강화 |

## 사용 흐름

1. 위 변수 채워서 마스터 프롬프트 호출
2. AI 가 10개 출력 (Phase별 산출물)
3. 각 산출물 검토 → 필요시 단계별 프롬프트 (stage-prompts.md) 로 보강
4. Phase 7 작업 티켓을 `/implement` 등에 전달해 실제 구현
5. 구현 결과는 Phase 8 Review 적용
6. Phase 9 SPDD 로 자산화
