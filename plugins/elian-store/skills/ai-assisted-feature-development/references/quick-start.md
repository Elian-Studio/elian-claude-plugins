# Quick Start — 빠른 사용법

상황별 시작 패턴 4가지. 마스터 프롬프트 ([master-prompt.md](master-prompt.md)) 와 단계별 프롬프트 ([stage-prompts.md](stage-prompts.md)) 의 *진입점*.

---

## 1. 처음 사용할 때 (Full Mode)

9 Phase 전체 적용. 신규 기능·HIGH 위험·정책 복잡한 경우 권장.

```text
다음 기능에 AI 기반 기능 개발 전략 스킬을 적용해줘.

기능 이름: [FEATURE_NAME]
기능 설명: [FEATURE_DESCRIPTION]
사용자 유형: [USER_TYPES]
기술 스택: [TECH_STACK]
기존 코드 맥락: [CODE_CONTEXT]
제약사항: [CONSTRAINTS]
위험도: [LOW / MEDIUM / HIGH]

출력:
1. Feature Framing
2. BDD
3. SDD
4. DDD 적용 여부
5. AI-TDD 테스트 계획
6. Context Engineering 패키지
7. Agentic Coding 작업 지시문
8. 리뷰 체크리스트
9. SPDD 기록 템플릿
```

호출 예시:

```
/ai-assisted-feature-development "이메일/비밀번호 로그인" --risk high --depth full
```

소요 시간 추정: **30분-2시간** (위험도와 정책 복잡도에 따라).

---

## 2. 설계만 필요할 때 (Design-Only Mode)

명세는 만들지만 구현은 다른 PR / 다른 시점. Phase 1-5 만 산출.

```text
다음 기능을 구현하지 말고 설계 산출물만 만들어줘.

- BDD 시나리오
- SDD 명세
- DDD 적용 판단
- 테스트 계획
- 리뷰 체크리스트

기능: [FEATURE_DESCRIPTION]
```

호출 예시:

```
/ai-assisted-feature-development "장바구니 추가" --risk medium --depth design-only
```

언제 쓰나:
- 다음 sprint 에서 구현할 기능을 *미리* 설계.
- 다른 팀이 구현할 기능을 *명세서로* 넘기기.
- AI 가 아닌 본인이 구현할 거지만 명세는 정리하고 싶을 때.

---

## 3. AI 에이전트에게 구현을 맡길 때 (Task-Only Mode)

명세가 *이미 잠긴* 상태에서 Phase 6 + 7 만 실행 (Context Package + Agent Task).

```text
다음 명세와 테스트 계획을 바탕으로 AI 에이전트용 작업 티켓을 작성해줘.

명세: [SPEC]
테스트 계획: [TEST_PLAN]
관련 파일: [RELATED_FILES]
제약사항: [CONSTRAINTS]

PR 단위로 구현할 수 있게 Goal, Scope, Out of Scope, Acceptance Criteria, Required Context, Test Requirements, Review Notes를 포함해줘.
```

호출 예시:

```
/ai-assisted-feature-development "주문 취소 구현" --depth task-only
```

언제 쓰나:
- 이미 docs/features/<feature>/spec.md 가 있고 AI 에이전트에게 넘기기만 하면 될 때.
- 명세가 별도 회의에서 합의됐고 *AI 작업 정의* 만 필요할 때.

---

## 4. 구현 결과 리뷰할 때 (Review-Only Mode)

AI 가 만든 PR / diff 를 명세·테스트 계획 대비 검증. Phase 8 만 실행.

```text
다음 구현 결과를 기능 명세와 테스트 계획 기준으로 리뷰해줘.

기능 명세: [SPEC]
테스트 계획: [TEST_PLAN]
구현 diff 또는 요약: [DIFF]
테스트 결과: [TEST_RESULTS]

Merge 가능 / 수정 후 Merge / Merge 금지 중 하나로 판단하고,
병합 차단 이슈와 추가 테스트 제안을 알려줘.
```

호출 예시:

```
/ai-assisted-feature-development "로그인 PR #123" --depth review-only
```

언제 쓰나:
- AI 가 만든 PR 머지 직전 *체크리스트 검증*.
- 외부 컨트리뷰터 PR 의 명세 충족 여부 점검.
- 리뷰어가 *놓칠 수 있는* 12 관점 자동 적용.

---

## 5. 환경변수로 default 조절

매번 `--risk` / `--depth` 안 적으려면:

```bash
export AAFD_DEFAULT_RISK=medium       # default risk
export AAFD_DEFAULT_DEPTH=full         # default depth
export AAFD_ARTIFACT_DIR=docs/features # 산출물 저장 위치
```

우선순위: `$ARGUMENTS` 명시값 > 환경변수 > skill default.

---

## 6. 예시 카탈로그 호출

기능 종류별 *완성된 예시* 를 보고 시작:

```
/ai-assisted-feature-development --example login
/ai-assisted-feature-development --example upload
/ai-assisted-feature-development --example order-cancel
/ai-assisted-feature-development --example post-create
```

`--example` 은 [login-example.md](login-example.md) 또는 [other-feature-examples.md](other-feature-examples.md) 의 *해당 예시를 자동 로드* — 사용자가 본인 기능과 비교하면서 시작 가능.

---

## 7. 다른 스킬과 조합

| 시나리오 | 흐름 |
|---|---|
| 모호한 아이디어 → 명세화 → 구현 | `/brainstorm` → `/ai-assisted-feature-development` → `/implement` |
| 명세 → 페르소나 압박 리뷰 → 구현 | `/ai-assisted-feature-development --depth design-only` → `/persona-review --persona evans` → `/implement` |
| 큰 결정 → 결정 잠금 → 명세 → 구현 | `/decision-dashboard` → `/ai-assisted-feature-development` → `/implement` |
| 명세 → 작업 티켓 → AI 팀 동시 구현 | `/ai-assisted-feature-development --depth task-only` → `/generate-teammate` |
| 명세 → 와이어프레임 → 구현 | `/ai-assisted-feature-development` → `/design-ui` → `/implement` |
| AI 가 만든 PR 검증 | `/ai-assisted-feature-development --depth review-only` |

`$ARGUMENTS` 와 환경변수가 표준이라 다른 스킬과 데이터 교환 쉬움.

---

## 8. 자주 묻는 사용 패턴

### Q. 위험도를 LOW 로 했는데 보안 위험이 있는 것 같다

→ Phase 1 Feature Framing 다시 실행 (`--depth design-only` + risk 재평가). 의심 들면 HIGH 로 올리고 Phase 4 + 8 추가.

### Q. AI 가 명세를 무시하고 코드를 짠다

→ Phase 6 Context Engineering 의 "AI 가 반드시 읽어야 할 문서" 에 명세 경로 명시. Phase 7 Agent Task 의 Constraints 강화.

### Q. 테스트가 매번 happy path 만이다

→ Phase 5 AI-TDD 매트릭스에 *실패·엣지·보안* 카테고리 별도 항목 명시. 보호 규칙 강화.

### Q. PR 이 너무 크다

→ Phase 7 Out-of-Scope 명확화. PR 을 *기능 단위* 가 아닌 *Phase 단위* 로 나누기 (예: PR 1 = 명세 + 테스트 / PR 2 = 구현 / PR 3 = 모니터링).

### Q. 같은 기능을 두 번째 만드는데 처음부터 다시

→ 첫 번째 작업의 Phase 9 SPDD 기록 (`prompt-record.md`) 를 *Phase 1 입력* 으로 사용. 재사용 패턴을 활용.
