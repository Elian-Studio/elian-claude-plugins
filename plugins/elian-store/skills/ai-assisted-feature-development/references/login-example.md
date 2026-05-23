# Example — 로그인 기능에 9 Phase 적용

> 로그인은 이 스킬을 *어떤 기능에 적용하는지* 보여주는 샘플. 결제·주문·업로드·게시글에도 같은 방식으로 적용 가능 (`other-feature-examples.md` 참조).

---

## Phase 1: Feature Framing

입력:

```text
기능 이름: 이메일/비밀번호 로그인
기능 설명: 사용자가 이메일과 비밀번호로 로그인하고 세션을 발급받는다.
사용자 유형: 일반 사용자, 관리자
비즈니스 목적: 인증된 사용자에게 개인화된 기능을 제공한다.
기술 스택: React, Node.js, Express, PostgreSQL
위험도: HIGH
```

산출:

```text
핵심 의도:
사용자가 안전하게 본인 계정에 접근하도록 한다.

성공 기준:
- 올바른 자격 증명으로 로그인하면 세션이 발급된다.
- 잘못된 자격 증명으로는 세션이 발급되지 않는다.
- 실패 메시지는 사용자 존재 여부를 노출하지 않는다.
- 반복 실패는 제한된다.
- 로그아웃하면 세션이 무효화된다.

위험도:
HIGH. 인증, 세션, 개인정보 접근과 연결되므로 보안 검토가 필요하다.

추천 Phase 조합:
Phase 1-9 전체 + Security Review 강화
```

---

## Phase 2: BDD

```gherkin
Feature: 로그인

  Scenario: 올바른 이메일과 비밀번호로 로그인한다
    Given 가입된 사용자가 존재한다
    When 사용자가 올바른 이메일과 비밀번호로 로그인한다
    Then 사용자는 로그인 상태가 된다
    And 서버는 세션을 발급한다

  Scenario: 잘못된 비밀번호로 로그인에 실패한다
    Given 가입된 사용자가 존재한다
    When 사용자가 잘못된 비밀번호로 로그인한다
    Then 로그인은 실패한다
    And 서버는 세션을 발급하지 않는다
    And 사용자는 공통 실패 메시지를 본다

  Scenario: 존재하지 않는 이메일로 로그인한다
    Given 가입된 사용자가 존재하지 않는다
    When 사용자가 존재하지 않는 이메일로 로그인한다
    Then 로그인은 실패한다
    And 사용자는 공통 실패 메시지를 본다

  Scenario: 로그인 실패가 반복된다
    Given 사용자가 여러 번 로그인에 실패했다
    When 사용자가 다시 로그인을 시도한다
    Then 시스템은 추가 시도를 일시적으로 제한한다
```

---

## Phase 3: SDD

```md
# Login Feature Spec

## Goal
사용자가 이메일과 비밀번호로 인증하고 세션을 발급받을 수 있게 한다.

## Scope
- POST /auth/login
- POST /auth/logout
- 세션 쿠키 발급
- 로그인 실패 제한
- 로그인 성공/실패 로그

## Out of Scope
- 소셜 로그인
- 비밀번호 재설정
- MFA 등록
- 관리자 대리 로그인

## Request
POST /auth/login

{
  "email": "string",
  "password": "string"
}

## Success Response
Status: 200

{
  "user": {
    "id": "string",
    "email": "string"
  }
}

## Failure Response
Status: 401

{
  "message": "이메일 또는 비밀번호가 올바르지 않습니다."
}

## Security Requirements
- 비밀번호는 평문으로 저장하거나 로그에 남기지 않는다.
- 존재하지 않는 이메일과 잘못된 비밀번호는 동일한 실패 메시지를 반환한다.
- 세션 쿠키는 HttpOnly, Secure, SameSite 속성을 사용한다.
- 로그아웃 시 서버 측 세션을 무효화한다.
- 반복 실패를 제한한다.

## Test Requirements
- 정상 로그인
- 잘못된 비밀번호
- 존재하지 않는 이메일
- 반복 실패 제한
- 로그아웃 후 세션 재사용 불가
- 세션 쿠키 보안 속성 확인
```

---

## Phase 4: DDD (필요 시)

```text
DDD 적용 판단:
로그인은 단순 기능처럼 보이지만, 실패 제한·세션 정책·관리자 MFA·휴면 계정·위험 기반 인증 등이 포함되면 도메인 모델링이 유용하다.

주요 개념:
- Account
- Credential
- Session
- AuthenticationAttempt
- LoginPolicy
- RiskSignal

도메인 서비스 후보:
- AuthenticationService
- LoginPolicyService
- SessionIssuer

도메인 이벤트 후보:
- LoginSucceeded
- LoginFailed
- SessionRevoked
```

---

## Phase 5: AI-TDD

| 테스트 | 목적 | 우선순위 |
|---|---|---|
| 올바른 이메일과 비밀번호면 세션 발급 | 정상 흐름 검증 | 높음 |
| 잘못된 비밀번호면 401 | 실패 흐름 검증 | 높음 |
| 존재하지 않는 이메일도 동일한 401 | 사용자 열거 방지 | 높음 |
| 5회 실패 후 제한 | 공격 완화 | 높음 |
| 로그아웃 후 세션 재사용 불가 | 세션 무효화 검증 | 높음 |
| 세션 쿠키 보안 속성 검증 | 보안 기준 검증 | 높음 |

AI 구현 지시 보호 규칙:

```text
- 테스트를 삭제하지 마라.
- 테스트의 기대값을 약화하지 마라.
- 보안 관련 테스트는 구현 편의를 위해 변경하지 마라.
- 테스트 변경이 필요하면 그 이유를 먼저 설명하고 승인을 받아라.
```

---

## Phase 6: Context Engineering

```text
AI가 반드시 읽어야 할 문서:
- docs/login-spec.md
- docs/error-response-format.md
- docs/security-baseline.md

AI가 참고해야 할 코드:
- src/routes/auth.ts
- src/services/sessionService.ts
- src/repositories/userRepository.ts
- src/middleware/errorHandler.ts
- src/tests/helpers/createUser.ts

지켜야 할 규칙:
- JWT를 새로 도입하지 않는다.
- 기존 서버 세션 방식을 사용한다.
- 컨트롤러에서 직접 DB에 접근하지 않는다.
- 평문 비밀번호를 로그에 남기지 않는다.

실행 명령:
- npm test
- npm run lint
```

---

## Phase 7: Agentic Coding Task

```md
# Task: Implement Email and Password Login

## Goal
이메일과 비밀번호 기반 로그인을 구현한다.

## Scope
- POST /auth/login
- POST /auth/logout
- 세션 발급
- 로그인 실패 제한
- 성공/실패 감사 로그
- 테스트 추가

## Out of Scope
- 소셜 로그인
- 비밀번호 재설정
- MFA 등록

## Acceptance Criteria
- 올바른 자격 증명으로 로그인하면 세션이 발급된다.
- 잘못된 자격 증명으로 로그인하면 401을 반환한다.
- 존재하지 않는 이메일과 잘못된 비밀번호는 같은 실패 메시지를 반환한다.
- 반복 실패 시 일시적으로 제한된다.
- 로그아웃하면 세션이 무효화된다.
- 모든 테스트와 lint가 통과한다.

## Required Context
- docs/login-spec.md
- src/services/sessionService.ts
- src/middleware/errorHandler.ts

## Constraints
- JWT를 도입하지 않는다.
- 기존 에러 응답 형식을 유지한다.
- 인증과 무관한 UI 또는 도메인 코드를 수정하지 않는다.

## Test Requirements
- login success
- login failure
- unknown email failure
- rate limit
- logout invalidation
- session cookie attributes

## Review Notes
리뷰어는 세션, 쿠키, 실패 메시지, rate limit, 로그 출력, 테스트 약화 여부를 집중 확인한다.
```

---

## Phase 8 + Phase 9 는 구현 결과를 받고 진행

구현 PR/diff 가 도착하면 [stage-prompts.md](stage-prompts.md) 의 Phase 8 Review 프롬프트로 점검, 통과 후 Phase 9 SPDD 프롬프트로 자산화.
