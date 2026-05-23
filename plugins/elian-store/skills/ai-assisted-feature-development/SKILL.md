---
name: ai-assisted-feature-development
description: When a user is about to build a new feature, improve an existing one, refactor legacy code, or hand work to an AI agent, drive the work through a disciplined 9-phase flow — Feature Framing → BDD → SDD → DDD(필요 시) → AI-TDD → Context Engineering → Agentic Coding → Review → SPDD Archive — instead of vibe-coding it directly. The skill forces intent, spec, tests, and review boundaries to exist before AI writes code, scales depth by feature risk (low/medium/high), and produces archivable prompts so each feature compounds into team assets. Any feature qualifies (login, payment, file upload, search, permissions, notifications, ...) — login is just one example.
when_to_use: 신규 기능 개발 / 기존 기능 개선 / 레거시 리팩터링 / API 설계 / UI 동작 구현 / 도메인 정책이 포함된 기능 / AI 에이전트에게 작업 위임 전 작업 정의 / PR 리뷰 전 품질 점검. 사용자가 '기능 만들기 시작', '이 기능 어떻게 짤까', 'AI에게 맡기기 전에 정리', '명세부터 짜자', 'BDD부터 짜줘', 'AI 코딩 절차 적용', '/ai-assisted-feature-development' 같은 표현을 쓸 때. 단순 오타·1-line 설정 변경·이미 명세가 잠긴 작은 fix에는 사용하지 않는다.
argument-hint: <feature-name> [--risk low|medium|high] [--depth full|design-only|task-only|review-only] [--example login|payment|upload|search]
disable-model-invocation: false
allowed-tools: Read, Glob, Grep, Write, Bash(git diff*), Bash(git log*), Bash(git status*), AskUserQuestion
---

# /ai-assisted-feature-development — AI 기반 기능 개발 전략

AI 시대의 개발은 "코드를 빠르게 생성" 이 아니라 **의도 → 행동 → 명세 → 모델 → 테스트 → 컨텍스트 → 구현 지시 → 리뷰 → 기록** 의 흐름을 만드는 것이다. 이 스킬은 그 흐름을 9 Phase 로 정형화해서, 어떤 기능이든 AI가 추측 없이 작업할 수 있게 한다.

핵심 원칙:

```
AI에게 바로 구현을 맡기지 말고,
먼저 의도 → 행동 → 명세 → 모델 → 테스트 → 컨텍스트 → 구현 지시 → 리뷰 → 기록의 흐름을 만든다.
```

로그인은 [references/login-example.md](references/login-example.md) 의 예시. 결제·주문 취소·파일 업로드·게시글 작성 등 다른 기능 예시는 [references/other-feature-examples.md](references/other-feature-examples.md).

---

## Where this fits in the workflow

```
/brainstorm (옵션 발산, 모호한 아이디어)
      ↓
▶ /ai-assisted-feature-development  ◀  (의도·명세·테스트·맥락·리뷰까지 정리)
      ↓
   Phase 1  Feature Framing       (의도·성공기준·위험도)
   Phase 2  BDD                   (사용자 행동 시나리오)
   Phase 3  SDD                   (API·UI·정책·완료 기준)
   Phase 4  DDD (필요 시)          (도메인 모델·책임 분리)
   Phase 5  AI-TDD                (구현 전 실패 테스트)
   Phase 6  Context Engineering   (AI에게 줄 최소 패키지)
   Phase 7  Agentic Coding        (작업 티켓 / PR 단위 지시)
   Phase 8  Review                (명세·테스트·보안·성능·접근성)
   Phase 9  SPDD Archive          (프롬프트·결정·테스트 결과 보존)
      ↓
/implement · /fix · /improve (실제 구현은 다른 스킬)
      ↓
/persona-review (페르소나 압박 리뷰) · /decision-dashboard (결정 잠금)
```

- **Upstream**: 모호하면 `/brainstorm`. 모호하지 않으면 바로 이 스킬.
- **이 스킬**: 9 Phase 산출물을 *문서·티켓·체크리스트*로 만든다. **구현 코드는 만들지 않는다** (Phase 7 에서 작업 티켓을 *발행* 하고, 실제 코드는 `/implement` 등이 받아 실행).
- **Downstream**: 산출물을 `/implement` / `/fix` / `/improve` 에 전달. 결과는 `/persona-review` 로 압박 리뷰, `/decision-dashboard` 로 결정 잠금.

---

## Standing rules

(아래 규칙은 절차가 아니라 매 호출에 항상 적용되는 원칙이다.)

- **AI 에게 바로 구현 시키지 않는다.** "X 만들어줘" 는 거부 — Phase 1-5 산출물이 먼저.
- **코드보다 의도·명세·테스트가 먼저다.** 요구사항이 모호하면 AI 는 빈칸을 추측으로 채운다.
- **위험도에 따라 깊이를 조절한다.** 프로토타입에 9 Phase 전체는 과잉, 결제·인증·권한은 모두 필수.
- **컨텍스트는 *bounded*.** 전체 저장소를 AI 에게 던지지 말고, 필요한 파일만 선별.
- **AI drafts, human owns.** 정책·보안·아키텍처 결정은 사람.
- **테스트는 계약이다.** AI 가 테스트를 약화하거나 삭제하면 회귀 방지가 무너진다 — AI-TDD Phase 의 보호 규칙으로 차단.
- **명세 없는 새 인증·새 패턴 도입 금지.** 기존 아키텍처와 충돌하는 임의 변경은 Forbidden.
- **인증과 무관한 대규모 리팩터링 금지.** PR 단위는 작고 리뷰 가능한 크기.
- **모든 Phase 는 *재사용 가능한 산출물* 을 남긴다.** SPDD Phase 가 그것을 보존.

자세한 마스터 프롬프트: [references/master-prompt.md](references/master-prompt.md).

---

## Modes

Skill 호출 시 `--depth` 로 조절:

| Mode | 무엇 | 언제 |
|---|---|---|
| `full` (default) | Phase 1-9 전체 흐름 | 신규 기능·HIGH 위험·정책 복잡 |
| `design-only` | Phase 1-5 만 (산출물 = framing/BDD/SDD/DDD/test-plan) | 설계만 필요, 구현은 다른 PR |
| `task-only` | Phase 6-7 만 (context + agentic task ticket) | 명세 이미 있고 AI 위임만 |
| `review-only` | Phase 8 만 | 구현 끝나고 리뷰 기준 점검 |

`--risk` 는 깊이 가이드:

| Risk | 추천 Phase 조합 |
|---|---|
| `low` (프로토타입/데모) | Phase 1, 2, 5 (간단 테스트) |
| `medium` (일반 CRUD) | Phase 1, 3, 5, 6 |
| `high` (보안·결제·권한·개인정보) | Phase 1-9 전체 + Security Review |

`--example login|payment|upload|search` 는 references 에서 해당 예시를 자동 로드.

---

## Automated vs needs your taste

| Claude/스크립트 자동 결정 | 사용자/팀(taste) 결정 |
|---|---|
| Phase 진행 순서, 각 Phase 산출물 형식 | 기능의 위험도 (LOW/MEDIUM/HIGH) |
| 보안·권한·개인정보 기능을 HIGH 로 분류 | 비즈니스 정책 (실패 메시지 톤, 락아웃 임계) |
| BDD/SDD/DDD 템플릿 채우기 (입력값 기반) | 사용자 시나리오의 우선순위·완료 기준 |
| Context Engineering 패키지 자동 추천 (파일·문서·제약) | AI 가 *반드시* 봐야 할 파일 vs 부수 파일 |
| AI-TDD 테스트 매트릭스 자동 생성 | 어느 테스트가 회귀 방지로 *보호 대상* 인지 |
| Agentic Task 티켓의 Goal/Scope/Constraints 채움 | Out-of-Scope 경계 (어디까지 AI 가 손대도 되는지) |
| 리뷰 체크리스트 자동 적용 | Merge / Block 최종 판단 |
| SPDD 산출물 자동 형식화 | 다음 작업에 재사용할 프롬프트 패턴 선별 |

자동이 잘못 잡으면 사용자가 수정 — Phase 마다 산출물 검토 게이트가 있음.

---

## Procedure (9 Phase Workflow)

각 Phase 의 *세부 프롬프트* 는 [references/stage-prompts.md](references/stage-prompts.md) 에 있음. 마스터 프롬프트 한 번에 모두 수행하려면 [references/master-prompt.md](references/master-prompt.md).

### Phase 1: Feature Framing (의도·성공 기준·위험도)

입력 변수 정리:
- `FEATURE_NAME`, `FEATURE_DESCRIPTION`, `USER_TYPES`, `TECH_STACK`, `CONSTRAINTS`, `RISK_LEVEL`

산출물:
1. 기능 핵심 의도 (한 문장)
2. 주요 사용자·사용 상황
3. 성공 기준
4. 실패하면 안 되는 조건
5. 예상 엣지 케이스
6. 보안/권한/개인정보/성능/접근성 위험도
7. 추천 Phase 조합 (위험도 기반)
8. 구현 전 반드시 확인할 질문

### Phase 2: BDD (사용자 행동 시나리오)

Given-When-Then 형식. 정상·실패·예외 흐름 모두 포함. 모호한 정책은 *질문/가정* 으로 분리.

산출:
- Feature 설명
- Scenario 목록 (Gherkin)
- 아직 합의가 필요한 정책 질문

### Phase 3: SDD (명세)

명세에 포함:
1. 기능 목적
2. Scope / Out of Scope
3. 사용자 역할·권한
4. 입력값·출력값
5. API 또는 UI 동작
6. 상태 변화
7. 에러 정책
8. 엣지 케이스
9. 보안/성능/접근성 요구사항
10. 로깅/모니터링
11. 테스트 항목
12. 완료 기준 (Acceptance Criteria)

명세는 `docs/features/<feature>/spec.md` 같은 위치에 저장 (저장 구조 [references/artifact-structure.md](references/artifact-structure.md)).

### Phase 4: DDD (필요 시)

DDD 적용 *판단* 부터. 단순 CRUD 에는 과잉.

복잡 정책 있는 경우 산출:
- 핵심 도메인 / 지원 / 일반 분류
- Entity, Value Object, Domain Service, Repository 후보
- Bounded Context, 도메인 이벤트
- 피해야 할 anemic / 과잉 설계

### Phase 5: AI-TDD (구현 전 테스트)

구현 *전에* 테스트 매트릭스 + 실패 테스트 작성.

매트릭스:
- Unit / Integration / E2E / 보안 / 권한 / 회귀
- 각 테스트의 검증 요구사항 명시
- **AI 구현 시 테스트 변경 금지 규칙** 명시 (assertion 약화·삭제 차단)

### Phase 6: Context Engineering

AI 에게 줄 *최소* 패키지:
1. 반드시 읽어야 할 문서
2. 참고할 코드 파일
3. 참고 안 해도 되는 파일
4. 기존 아키텍처 규칙
5. 변경 금지 사항
6. 테스트·검증 명령
7. 최종 컨텍스트 요약

원칙: "더 많은 정보" 가 아니라 "필요한 정보" 만.

### Phase 7: Agentic Coding (작업 티켓 발행)

PR 또는 작업 티켓 형식:

```
# Task: <FEATURE_NAME>
## Goal / Scope / Out of Scope / Acceptance Criteria
## Required Context / Constraints / Test Requirements
## Review Notes
```

**이 스킬은 티켓을 *발행만* 한다 — 실제 코드 구현은 `/implement` / `/fix` / `/improve` 가 받아 실행.**

### Phase 8: Review (리뷰)

리뷰 관점 12 가지:
1. 명세 충족 · 2. BDD 시나리오 충족 · 3. 테스트 충분성 · 4. 도메인 모델 적합성 · 5. 보안 · 6. 권한/개인정보 · 7. 성능 · 8. 접근성 · 9. 유지보수성 · 10. 불필요한 변경 · 11. 병합 차단 이슈 · 12. 개선 제안

최종 판단: `Merge 가능` / `수정 후 Merge` / `Merge 금지`

### Phase 9: SPDD Archive (재사용 자산화)

저장:
- 기능 개요 · 사용한 전략 조합 · 핵심 프롬프트 · 가정 · 산출물 · 테스트 결과 · 리뷰 발견 · 재사용 패턴 · 안티패턴

저장 위치 예시: `prompts/feature-development/<feature>/spdd-record.md`.

---

## Forbidden (이 스킬이 절대 안 하는 것)

- ❌ AI 에게 "기능 만들어줘" 만 시키는 것 — Phase 1-5 산출물 없이 구현 호출 금지
- ❌ 테스트를 구현 후에 *변명처럼* 붙이기 — AI-TDD 가 깨짐
- ❌ AI 가 보안·권한·개인정보 정책을 자체적으로 *추측* 하게 두기 — Phase 3 명세에 명시 강제
- ❌ 전체 저장소를 AI 에게 던지기 — Phase 6 Context Engineering 강제
- ❌ 인증과 무관한 대규모 리팩터링 묶기 — PR 작아야 리뷰 가능
- ❌ 명세 없는 새 패턴 (JWT, 새 ORM, 새 큐 등) 임의 도입
- ❌ 테스트를 AI 가 *삭제·약화* 하도록 허용 — AI-TDD 보호 규칙으로 차단
- ❌ Phase 7 작업 티켓을 이 스킬이 *직접 실행* — 발행만, 실행은 `/implement` 등
- ❌ Out-of-Scope 정의 없이 Phase 7 진행 — AI 범위 폭주 위험
- ❌ SPDD 단계 skip — 같은 패턴이 다음 기능에 재사용 안 됨

---

## Pitfall / 안티패턴

자세히는 [references/anti-patterns.md](references/anti-patterns.md).

| 패턴 | 왜 문제 | 대응 |
|---|---|---|
| "로그인 기능 만들어줘" | 의도·정책·테스트가 추측됨 | Phase 1-5 산출물 강제 |
| "대충 테스트도 추가해줘" | 테스트가 통과용 형식만 | AI-TDD 매트릭스 + 보호 규칙 |
| "전체 코드 보고 알아서 고쳐줘" | 컨텍스트 폭증·기존 아키텍처 깨짐 | Phase 6 bounded context |
| "좋은 방식으로 해줘" | 기준 부재 → 매번 다른 결과 | SPDD 로 패턴 자산화 |
| Phase 7 만 잘 적고 Phase 1-5 skip | AI 가 명세 추측 → 회귀 | full mode 권장 |
| HIGH 위험 기능에 Phase 4(DDD) skip | 정책 책임이 컨트롤러에 몰림 | risk=high 면 자동 포함 |
| AI 가 구현 후 테스트 assertion 약화 | 회귀 방지 무너짐 | AI-TDD 보호 규칙 + Review Phase 8 항목 12 |

## 병합 차단 조건

[references/definition-of-done.md](references/definition-of-done.md) 의 12 조건 중 하나라도 위반이면 Merge 안 함.

핵심 5 조건:
- 명세와 다른 동작
- 핵심 BDD 시나리오 불만족
- 실패 케이스 테스트 부재
- AI 가 테스트 약화/삭제
- 보안·권한·개인정보 정책 불명확

---

## Examples

- 로그인 기능에 9 Phase 적용: [references/login-example.md](references/login-example.md) — Feature Framing → BDD → SDD → DDD → AI-TDD → Context → Agentic Task 까지 완성된 산출물 8 개.
- 다른 기능 (파일 업로드 / 주문 취소 / 게시글 작성): [references/other-feature-examples.md](references/other-feature-examples.md) — 각 기능의 위험도 + 추천 Phase 조합 + 중점 검토 항목.

호출 형태:

```
/ai-assisted-feature-development "이메일/비밀번호 로그인" --risk high
/ai-assisted-feature-development "장바구니 추가" --risk medium --depth design-only
/ai-assisted-feature-development "파일 업로드" --risk medium --example upload
/ai-assisted-feature-development "주문 취소" --risk high --depth full
/ai-assisted-feature-development "게시글 작성" --risk low --depth task-only
```

---

## Customization

| 메커니즘 | 어떻게 | Default |
|---|---|---|
| `$ARGUMENTS` | `<feature-name> [--risk ...] [--depth ...] [--example ...]` | — |
| 환경변수 `${AAFD_DEFAULT_RISK}` | 기본 risk 오버라이드 | `medium` |
| 환경변수 `${AAFD_DEFAULT_DEPTH}` | 기본 depth 오버라이드 | `full` |
| 환경변수 `${AAFD_ARTIFACT_DIR}` | 산출물 저장 디렉토리 | `docs/features/<feature>/` |

우선순위: `$ARGUMENTS` > 환경변수 > skill default.

---

## Quick-start templates

빠르게 시작할 수 있는 4 가지 패턴 ([references/quick-start.md](references/quick-start.md)):

1. **처음 사용할 때** — 9 Phase 모두 적용 (full mode)
2. **설계만 필요할 때** — design-only mode (Phase 1-5)
3. **AI 에이전트에게 위임할 때** — task-only mode (Phase 6-7)
4. **구현 결과 리뷰할 때** — review-only mode (Phase 8)

---

## Definition of Done

전체 12 조건은 [references/definition-of-done.md](references/definition-of-done.md). 핵심 요약:

- [ ] 의도·성공 기준 명확
- [ ] BDD 시나리오 작성됨
- [ ] 기능 명세 작성됨
- [ ] 도메인 복잡도에 따른 DDD 판단됨
- [ ] 테스트 계획이 구현 *전* 작성됨
- [ ] AI 컨텍스트 패키지 선별됨
- [ ] AI 작업 티켓 작성됨
- [ ] 구현 결과 명세 대비 리뷰됨
- [ ] 보안/권한/개인정보/성능/접근성 검토됨
- [ ] 테스트 통과
- [ ] 사용한 프롬프트·판단 근거 기록됨

---

## Artifact structure

산출물 디렉토리 구조: [references/artifact-structure.md](references/artifact-structure.md).

```
docs/features/<feature-name>/
  feature-framing.md
  bdd-scenarios.feature
  spec.md
  domain-model.md
  test-plan.md
  context-package.md
  agent-task.md
  review-checklist.md
  prompt-record.md

prompts/feature-development/
  master.prompt.md
  bdd.prompt.md
  sdd.prompt.md
  ddd.prompt.md
  ai-tdd.prompt.md
  context-engineering.prompt.md
  agentic-coding.prompt.md
  review.prompt.md
  spdd-record.prompt.md
```

---

## Self-validation

구조 검증: `python3 scripts/validate_skill.py` (human) / `--json` / `--quiet`. frontmatter, 9 Phase 명시, references 필수 파일, Standing rules·Forbidden·Pitfall·Where this fits·DoD 섹션 존재를 결정적으로 확인. stdlib 전용.

핵심 문장으로 마무리:

```
AI에게 바로 구현을 맡기지 말고,
먼저 의도 → 행동 → 명세 → 모델 → 테스트 → 컨텍스트 → 구현 지시 → 리뷰 → 기록의 흐름을 만든다.
```
