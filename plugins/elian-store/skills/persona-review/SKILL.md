---
name: persona-review
description: When the user wants their thinking, plan, design, or document reviewed through a fixed persona lens chosen from a library (default daniel; alternatives evans for DDD, dean for distributed-scale, martin for clean code/SOLID/TDD, or any custom path) using a locked 5-block OUTPUT FORMAT (Conclusion → Trade-offs table → Operational risks → 8 pressure questions → Next question). When the input is a thin one-liner the persona asks ONE intent question first (2-3 choices + free input) instead of speculating. Optional --depth interview re-emits the 5-block up to 3 rounds, each round re-interviewing only the 1-2 weakest points (pressure-question score ✗ before △) until the Conclusion hardens into a definitive statement, then emits a read-only handoff payload to /improve.
when_to_use: before locking in a non-trivial decision, when reviewing a draft plan/design/PR description, when self-checking a thought against operational risk or domain modeling or scale or code quality, when a fuzzy one-line idea needs intent clarified before any critique, when a review should converge over a few rounds before handing off to improvement, user says '페르소나로 리뷰해줘'·'다니엘 시각으로'·'에반스로 도메인 점검'·'딘 시각으로 스케일 압박'·'마틴으로 클린코드 점검'·'/persona-review'·'트레이드오프 표로 정리해줘'·'운영 관점으로 점검'·'재심문으로 수렴시켜줘'·'의도부터 물어봐'·'리뷰하고 개선까지 이어줘'·'--depth interview'·'--persona evans|dean|martin'
argument-hint: <target-path-or-text> [--persona daniel|evans|dean|martin|<path-to-custom>] [--depth quick|deep|interview]
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git diff*), Bash(git log*), Bash(git status*), AskUserQuestion
---

# /persona-review — 페르소나 라이브러리로 리뷰 (잠긴 OUTPUT FORMAT)

사용자의 사고·문서·계획을 **선택된 페르소나의 렌즈**와 **잠긴 OUTPUT FORMAT**으로 리뷰한다. 일반적인 AI 리뷰 (응원·평가·산문 나열) 대신 **결론 → 트레이드오프 표 → 운영 리스크 → 8가지 압박 질문 → 다음 질문** 5블록 구조로만 답한다.

기본 페르소나는 `daniel` (운영 마인드). 도메인 모델링·분산 스케일·클린 코드를 압박하고 싶을 때는 `--persona evans|dean|martin`. 커스텀 페르소나 마크다운 경로도 인자로 줄 수 있다.

단, **상대가 뭘 원하는지 모르면 단정하지 않는다.** 입력이 한 줄짜리/모호하면 5블록(비판)으로 직행하지 않고, *의도를 먼저 묻는다* — 선택지 2~3개 + 자유 입력. 추측으로 트레이드오프 표를 채우는 것을 구조적으로 막는다.

핵심 가치: 발산은 `/brainstorm` 이 한다. 이 스킬은 **수렴 압박** — 페르소나에 따라 압박 축이 다르지만 (운영 / 도메인 / 스케일 / 클린코드), 5블록 형식과 약점 재심문 루프는 공통. `--depth interview` 면 5블록을 **최대 3라운드 반복**하며 매 라운드 가장 약한 지점(압박 질문 `✗` > `△`)만 타깃 재심문해 *이해* 를 수렴시키고, 결론이 단정으로 굳으면 `/improve` 핸드오프 페이로드를 *발행*한다 (본체는 끝까지 read-only).

---

## Where this fits in the workflow

```
                              ┌── 수렴 루프 (interview, 약점 재심문, ≤3R) ──┐
                              ↓                                             │
brainstorm → ▶ persona-review: 페르소나 선택 → 의도 게이트 → 5블록 ───────┘ → decision-dashboard
                  ↑                                          │
         draft / 한 줄 아이디어 / 설계                         └─ 핸드오프 페이로드(발행만) → /improve · /implement · /fix
```

- **선행**: `/brainstorm` 또는 사용자 본인이 만든 draft. **한 줄짜리 모호한 아이디어도 가능** — 그 경우 의도를 먼저 묻는다 (추측 안 함)
- **이 스킬**: 페르소나 선택 → 입력이 얇으면 의도 1질문 먼저 → 정보 모이면 5블록(수렴 산출물). `--depth interview` 면 5블록 출력 후 약점만 재심문하며 최대 3R 반복해 수렴
- **후행**: 수렴되면 `/decision-dashboard` 로 결정 잠금, 또는 핸드오프 페이로드를 받아 `/improve`(개선)·`/implement`(신규). persona-review는 페이로드를 *발행만* 하고 직접 실행하지 않는다 (read-only)

세트 관계: `/brainstorm` (옵션 발산) ↔ `/persona-review` (페르소나별 압박 수렴). 발산-수렴 페어.

---

## Persona library

`references/personas/` 디렉토리에 있는 페르소나 중 하나를 `--persona` 인자로 선택. 같은 5블록 OUTPUT FORMAT을 쓰되 **어떤 압박을 가하는가** 가 페르소나마다 다르다.

### 기본 제공 페르소나

| 페르소나 | 압박 축 | 어떤 대상에 강한가 |
|---|---|---|
| [`daniel`](references/personas/daniel.md) (default) | 운영 가능성, 메커니즘, axiom vs policy, 자동화 | 일반 리뷰 / 운영 변경 / 일상 코드 |
| [`evans`](references/personas/evans.md) | DDD — bounded context, ubiquitous language, aggregate, ACL | 도메인 모델·아키텍처 결정, 새 서비스 경계 |
| [`dean`](references/personas/dean.md) | 분산·스케일 — tail latency, SPOF, hot key, backpressure | 트래픽 증가 대비, 분산 시스템, 큐·캐시·DB scaling |
| [`martin`](references/personas/martin.md) | Clean Code / SOLID / TDD — naming, 단일 책임, 함수 4-6줄 | 코드 품질, 객체지향 설계, 테스트 전략 |

### 어떤 상황에 어떤 페르소나 (매칭 가이드)

| 상황 | 권장 페르소나 | 이유 |
|---|---|---|
| 운영 변경, 알림·재시도·hook 도입 | `daniel` | 운영 가능성·자동화에 강함 |
| 도메인 모델 설계, 새 aggregate / 서비스 경계 | `evans` | DDD가 곧 도메인 정합성 압박 |
| 트래픽 100x 대비, 캐시·큐·DB 설계, latency 회귀 | `dean` | 분산·tail latency 정통 |
| 코드 리뷰, 함수 단위 리팩토링, 테스트 전략 | `martin` | 함수/객체 단위 형식 압박 |
| 도메인 + 분산이 같이 걸린 결정 | `evans` 후 `dean` 순차 또는 별도 두 번 호출 | 한 페르소나는 한 축에 집중 |
| 비-기술적 결정 (스코프, 일정, 팀) | 페르소나 부적합 — `/plan-ceo-review` 등 다른 스킬 | 페르소나는 기술 압박용 |

### 커스텀 페르소나 작성

기본 페르소나의 7섹션 구조 (Voice / Hard Rules / Decision Heuristics / Priorities / Forbidden / Pressure Questions / Blind Spots) + 선택적 Identity. 자세한 작성 가이드는 [`references/personas/daniel.md`](references/personas/daniel.md) 의 마지막 "Custom Persona 작성 가이드" 섹션 참고. 작성한 파일을 `references/personas/<name>.md` 에 두거나 임의 경로에 두고 `--persona <path>` 로 호출.

---

## What's automated vs what needs your taste

| Claude 가 자동으로 결정 | 사용자가 결정 |
|--------------------------|-------------|
| 페르소나 자동 추천 (대상 파일 경로·diff 기반) | 어떤 페르소나를 실제로 적용할지 (`--persona`) |
| OUTPUT FORMAT 5블록 구조 (절대 변경 불가) | 어떤 대상을 리뷰할지 (파일/텍스트/주제) |
| 8가지 압박 질문의 적용 (각 질문 ✓/△/✗/N 4단계) | 페르소나 교체 / 다중 호출 여부 |
| 트레이드오프 표 채우기 (옵션 1개면 "현재안 vs do-nothing") | 압박 질문 점수 동의/반박 |
| 운영 리스크 추출 (해당 없으면 "해당 없음" 명시) | "다음 질문" 의 채택 여부 |
| 추측 금지 → 코드로 확인 or 질문 (모르면 묻는다) | 추가 컨텍스트 제공 (코드/문서 경로) |
| 평가·응원·메타 설명·이모지 차단 | 결과 기반 다음 액션 (재설계/실행/보류) |
| 입력 농도 판정 → 얇으면 의도 질문 먼저 (Phase 1) | 의도 질문에 어느 선택지/자유입력으로 답할지 |
| 수렴 루프 진행·종료 판정 (3R 안전망, Phase 4.5) | `--depth interview` 사용 여부 / 재심문 답변 / 핸드오프 채택 |

**파괴적 작업 차단**: 이 스킬은 read-only. 코드 수정·파일 생성·git 변경 일절 안 함. 수렴 루프도 질문만 — 어느 라운드에서도 파일을 안 건드린다. 핸드오프도 페이로드를 *발행만* 하고 `/improve` 를 직접 호출하지 않음. 출력은 콘솔 마크다운만.

---

## OUTPUT FORMAT (절대 변경 금지)

페르소나가 답할 때 항상 아래 5블록을 **순서대로** 그대로 출력한다. 블록 추가·삭제·순서 변경 금지. 빈 블록은 "해당 없음" 한 줄로 채운다. 메타 설명 ("리뷰 결과입니다") 없이 곧장 `## 결론` 부터 시작.

5블록의 헤더는 페르소나의 언어 컨벤션에 따라 다를 수 있다 (한국어 default / 영어 fallback). 동일 의미만 보장하면 OK — 한 페르소나 안에서는 일관되게.

```markdown
## 결론
한 줄. 단정 가능하면 단정. 단정이 정직하지 않으면 "상황에 따라 다름"
+ 어떤 상황에서 어떻게 갈리는지 한 줄.

## 트레이드오프
| 옵션 / 측면 | Pros | Cons | 적합 상황 |
|---|---|---|---|
| (옵션 A) | ... | ... | ... |
| (옵션 B) | ... | ... | ... |

(옵션이 1개뿐이면 "현재 안" vs "do-nothing / 가장 가까운 대안" 으로 강제 채움.)

## 운영 리스크
- 미래 장애 가능성: ...
- 팀 확장 시 부담: ...
- 추적/디버깅 가능성: ...

(해당 없으면 위 3줄 대신 "해당 없음" 한 줄로 끝.)

## 페르소나 압박 질문
| # | 질문 | 점수 | 근거 / 보강 필요 |
|---|---|---|---|
| 1 | (페르소나의 1번 질문) | ✓/△/✗/N | ... |
| 2 | ... | ... | ... |
| ... | (페르소나 8개 질문 모두) | ... | ... |
| 8 | ... | ... | ... |

## 다음 질문
한 줄. 후속 질문이 자연스럽게 이어지도록.
```

**점수 표기**: `✓` 잘 다뤄짐 / `△` 부분적, 보강 필요 / `✗` 누락·미흡 / `N` 이 결정엔 해당 없음 (이유는 근거 칸 한 줄).

추측 금지. 본문에 없으면 `✗` 또는 `N`. "아마도 의도했을 것" 류 보정 안 함.

압박 질문 수는 페르소나마다 4-12개 자유. 8개가 권장.

---

## Workflow (Procedure · 절차)

```
Phase 0:   Persona 자동 추천 (대상 분석) — 사용자 override 가능
Phase 1:   Target 수집 + 입력 농도 판정  ← 얇거나 모호하면 의도 1질문 먼저 (추측 안 함)
Phase 2:   Persona 로드
Phase 3:   페르소나의 압박 질문 적용 (정보 모인 뒤 공정 채점)
Phase 4:   5블록 출력 (수렴 산출물)
Phase 4.5: 수렴 루프 (--depth interview 일 때만, 약점 재심문, ≤3R)
Phase 5:   핸드오프 (개선/결정/재리뷰/종료)
```

### Phase 0: Persona 자동 추천 (선택)

`--persona` 가 명시되지 않은 경우, 대상 분석으로 권장 페르소나를 한 줄 안내한 뒤 default `daniel` 로 진행. 사용자가 override 하려면 `--persona evans` 등을 다음 턴에 명시.

자동 매칭 규칙:
- `**/domain/`, `**/aggregate/`, 도메인 모델 파일 → `evans`
- `**/queue/`, `**/scheduler/`, replication, sharding, cache 관련 → `dean`
- 새 함수 / 클래스 / 리팩토링 diff → `martin`
- 운영·인프라·hook·재시도 → `daniel`
- 매칭 불명확 → `daniel` (default)

### Phase 1: Target 수집 + 입력 농도 판정

인자 해석:

| 인자 형태 | 해석 |
|---|---|
| 파일 경로 (`.md`, `.ts`, `.java`, etc) | `Read` 로 본문 로드 |
| URL (PR/issue) | `확인 필요: 외부 페치 도구 사용 여부` 출력 후 사용자 확인 (자동 페치 금지) |
| 자유 텍스트 | 인자 자체를 대상으로 |
| 비어있음 | `AskUserQuestion`: "리뷰 대상? (a) 현재 변경 (git diff) (b) 특정 파일 (c) 텍스트" |

**입력 농도 판정** — 이 Phase 안에서 Phase 3 진입 전 분기를 가른다:

| 농도 | 기준 | 처리 |
|---|---|---|
| 얇음 | 한두 줄 자유 텍스트, 목표·범위 불명확 ("X 하려는데 어떻게?") | 의도 질문 **반드시** 먼저 (선택지 2~3 + 자유입력) |
| 모호 | 문서는 있으나 목표/완료기준이 안 잡힘 | 가장 불명확한 축 1개부터 질문 |
| 충분 | 목표·범위·제약·완료기준이 본문에 있음 | 질문 건너뛰고 Phase 3 직행 |

옵션:

| 옵션 | 의미 | Default |
|---|---|---|
| `--depth quick\|deep\|interview` | quick = 게이트(얇으면 의도 1질문) 후 5블록 1회 / deep = 그 + 각 압박 질문 보강 제안 한 줄 / interview = 5블록 출력 후 약점 재심문하며 최대 3R 수렴 + 핸드오프 | `quick` |
| `--persona <name>\|<path>` | 페르소나 로드. 기본 라이브러리 이름(`daniel`/`evans`/`dean`/`martin`) 또는 임의 경로 | `daniel` |

### Phase 2: Persona 로드

- **이름 인자**(`--persona daniel|evans|dean|martin`): `references/personas/<name>.md` 를 `Read` 로 로드.
- **경로 인자**(`--persona /path/to/custom.md`): 해당 경로를 `Read`. 7섹션 (Voice / Hard Rules / Decision Heuristics / Priorities / Forbidden / Pressure Questions / Blind Spots) + 선택 Identity. 누락 섹션은 [`references/personas/daniel.md`](references/personas/daniel.md) 에서 보충. 파일 없으면 사용자에게 알리고 `daniel` 로 폴백.

페르소나는 *어떤 압박을 가하는가* 만 바꾼다. 5블록 OUTPUT FORMAT 은 모든 페르소나 공통.

### Phase 3: 페르소나의 압박 질문 적용

각 질문마다:

1. 대상 본문에서 해당 질문에 답하는 부분을 `Grep` / 본문 스캔
2. 발견 → `✓` 또는 `△`, 누락 → `✗`, 비대상 → `N`
3. 근거 칸에 발견 위치 또는 "확인 필요: <무엇을>" 명시

추측 금지. 본문에 없으면 `✗` 또는 `N`. "아마 의도했을 것" 보정 안 함.

### Phase 4: 5블록 출력 (수렴 산출물)

`## OUTPUT FORMAT` 의 마크다운 그대로. **순서·블록 변경 금지**. 빈 블록도 "해당 없음" 명시. 메타 설명 없이 곧장 `## 결론` 부터.

### Phase 4.5: 수렴 루프 (`--depth interview` 일 때만)

`quick`/`deep` 은 5블록 1회 출력 후 바로 Phase 5. `interview` 는 **5블록을 반복**해 *이해* 를 수렴시킨다 (코드·파일 아닌 이해만 — 매 라운드 read-only).

1. 방금 출력한 5블록에서 **가장 약한 지점 1~2개** 를 고른다 (3개 이상 금지 — 한 번에 많이 물으면 수렴 안 됨):
   - 우선순위: 압박 질문 `✗` > `△` > `## 결론` 이 "상황에 따라 다름" 이면 그 분기 변수
2. 그 지점만 `AskUserQuestion` 으로 타깃 재심문. 추측으로 채우지 말 것 — 모르면 묻는다.
3. 답변을 컨텍스트에 합쳐 Phase 3~4 재실행 → 5블록 **전체를 다시** 출력 (부분 패치 금지, 5블록 형식 불변).
4. 매 출력 헤더 바로 위 한 줄로 라운드 노출: `(interview R{n}/3)`.
5. **종료 조건 — 하나라도 만족하면 루프 중단 → Phase 5**:
   - (a) `## 결론` 이 "상황에 따라 다름" → 단정으로 바뀜
   - (b) 압박 질문에 `✗` 0개 (전부 `≥ △` 또는 `N`)
   - (c) 사용자가 "그만"·"충분" 등 중단 의사 표시
   - (d) **3라운드 도달** (무한 루프 차단 — 절대 초과 금지)

어떤 라운드에서든 코드·파일·git 변경 없음. 루프는 질문만 더 한다.

### Phase 5: 핸드오프 (개선 / 결정 / 재리뷰 / 종료)

수렴된(또는 1회성) 리뷰를 다음 단계로 넘긴다. **persona-review 는 `/improve` 를 직접 호출하지 않는다** — 실행 가능한 호출문과 컨텍스트를 *발행만* 한다 (read-only axiom 유지; 실제 실행은 다음 턴에 사용자/Claude 가).

`--depth interview` 거나 압박 질문에 `✗`/`△` 가 남았으면 `AskUserQuestion` 으로 다음 액션을 묻고, 깨끗하면 라벨 한 줄만:

```
(다음: /decision-dashboard | /improve | 보강 후 재리뷰)
```

개선으로 넘길 때 핸드오프 페이로드 포맷 (이 블록을 그대로 발행, 실행은 다음 턴):

```
(핸드오프 → /improve <issue-or-target>)
─ 컨텍스트 ─
- 페르소나: <name>
- 결론: <수렴된 한 줄>
- 채택 옵션: <트레이드오프 표에서 고른 안 + 근거>
- 잔여 리스크: <✗/△ 로 남은 압박 질문 항목>
- 개선 범위 In/Out: <리뷰에서 도출된 경계>
```

액션 선택지: `/improve`(코드 개선) · `/decision-dashboard`(결정 잠금) · `보강 후 재리뷰`(interview 재진입) · `종료`. 사용자가 고르지 않으면 라벨 한 줄로 끝내고 강제하지 않는다.

---

## Persona (default: daniel)

기본 페르소나 본체는 [`references/personas/daniel.md`](references/personas/daniel.md) 에 있다. SKILL.md 는 그것을 *로드해서 적용*할 뿐 본체를 인라인하지 않는다 (progressive disclosure).

요약 — Daniel 페르소나가 압박하는 축:

| 축 | 한 줄 |
|---|---|
| 운영 가능성 | "돌아간다" ≠ "신뢰할 수 있다" |
| 메커니즘 | 결과를 믿지 말고 구조를 이해 |
| axiom vs policy | 협상 가능/불가능 분리 |
| 가독성 | 5초 안에 핵심 |
| 트레이드오프 | Cons 없는 설계 = 미완성 |
| 레퍼런스 | 발명 전 표준 확인 |
| 자동화 | "기억해야 함" = 부패 신호 |
| 실패 모드 | 어떻게 망가지나 |

전체 Voice / Hard Rules / Forbidden / Blind Spots / 커스텀 작성 가이드: [`references/personas/daniel.md`](references/personas/daniel.md).

다른 페르소나의 압박 축 요약은 위 "Persona library" 표 참고.

---

## Examples

완결된 BEFORE(원본 문서) → AFTER(페르소나 5블록 출력) 사례 3건: [`references/example-review.md`](references/example-review.md).

(현재 example 은 `daniel` 페르소나 사례 위주. evans/dean/martin example 은 future work.)

- Example 1: 설계 문서 (`payment-flow.md`) 리뷰 — sync/async 트레이드오프 + 운영 리스크 압박
- Example 2: 자유 텍스트 (마이크로서비스 분리) 리뷰 — 옵션 1개일 때 do-nothing 강제 비교
- Example 3: `--depth interview` 1라운드 — 약점 재심문 → 재출력 수렴 → `/improve` 핸드오프 발행

호출 형태:

```
/persona-review docs/architecture/payment-flow.md
/persona-review "사용자 도메인을 별도 서비스로 분리하려고 함"
/persona-review my-plan.md --persona evans
/persona-review src/services/billing.ts --persona martin
/persona-review docs/architecture/payment-flow.md --persona dean --depth interview
/persona-review my-plan.md --persona ./personas/cto-conservative.md
```

---

## Pitfalls / Known Issues

| 패턴 | 왜 문제 | 대응 |
|---|---|---|
| 대상 본문이 한 줄뿐 | 압박 질문 대부분 N → 리뷰 가치 낮음 | `AskUserQuestion`: "보강 컨텍스트 — 관련 파일/배경?" |
| 페르소나가 평가/응원 시작 | voice 위반 | Forbidden 재확인. 출력 폐기 후 재생성. |
| 트레이드오프 표 옵션 1개 | 비교 안 됨 = 트레이드오프 아님 | "현재안 vs do-nothing" 강제 채움 |
| 운영 리스크 전부 N/A | 정말 없는지 의심 | "운영 컨텍스트 부족 — 배포/호출량/장애 이력?" 한 번 묻기 |
| 점수 칸에 "아마도" | 추측 = 금기 위반 | `✗`/`N` 강등 + "확인 필요: <무엇을>" |
| `--persona` 파일 없음 | 로드 실패 | 알리고 `daniel` 폴백 |
| 페르소나 mismatch (분산 시스템에 `martin` 적용) | 압박 축이 안 맞으면 `N` 비중 폭증 | Phase 0 자동 추천 또는 페르소나 교체 후 재리뷰 |
| 한 압박 질문에 두 답 | 표 형식 위반 | 질문 분리 또는 한 답 통합. 두 답 동시 금지. |
| interview 루프가 안 끝남 | 종료조건 미평가 → 무한 재심문 | 매 라운드 (a~d) 평가 + 3R 강제 상한 (d) |
| 핸드오프를 직접 실행으로 오인 | read-only 계약 위반 (코드 변경) | 페이로드는 *발행만*. 실제 `/improve` 는 다음 턴 |
| interview 한 라운드 재심문 3개+ | 발산이 되어 수렴 안 됨 | 가장 약한 1~2개만 (`✗`>`△` 우선) |
| 페르소나 다중 사용 시 결과 통합 | 한 호출에 한 페르소나만 — 다중은 별도 호출 후 사용자가 통합 | future work (multi-persona 모드) |

---

## Forbidden (이 스킬이 절대 안 하는 것)

- 코드 수정 / 파일 생성 / git 변경 (read-only)
- 5블록 OUTPUT FORMAT 변경 (블록 추가·삭제·순서 변경 금지)
- 페르소나 voice/Forbidden 위반 (평가·응원·메타 설명·이모지·추측·마케팅 톤·사과)
- 압박 질문을 페르소나 정의 이상 추가 (커스텀 페르소나는 그 페르소나 질문 갯수 따름)
- 사용자 결정 우회 (페르소나 교체·재리뷰는 사용자 명시 요청 시에만)
- 외부 URL 자동 페치 (사용자 확인 없이는 안 함)
- 5초 안에 핵심 안 잡히는 다이어그램 생성 / 한 표에 두 질문 답하기
- interview 모드 3라운드 초과 (무한 루프 — 종료조건 d 절대 우회 금지)
- 핸드오프 페이로드를 persona-review 가 직접 실행 (발행만; `/improve` 실제 호출은 다음 턴 사용자/Claude 몫)
- interview 한 라운드에 재심문 질문 3개 이상 (1~2개로 강제 — 수렴 깨짐)
- 한 호출에 다중 페르소나 동시 적용 (한 호출 = 한 페르소나; 다중은 별도 호출)

---

## Customization

| 메커니즘 | 어떻게 | Default |
|---|---|---|
| `$ARGUMENTS` | 호출 시 `<target> [--depth ...] [--persona ...]` 전달 (frontmatter `argument-hint` 참조) | — |
| 환경변수 `${PERSONA_REVIEW_DEFAULT}` | 기본 페르소나 이름/경로 오버라이드. 매번 `--persona` 안 줘도 됨 | `daniel` |
| 환경변수 `${PERSONA_REVIEW_DEPTH}` | 기본 depth 오버라이드 (`quick`/`deep`/`interview`). `interview` 로 두면 매 호출이 자동으로 재심문 루프에 들어가니 주의 | `quick` |

우선순위: `$ARGUMENTS` 명시값 > 환경변수 > skill default. 환경변수 미설정 시 `daniel` / `quick`.

---

## Pre-flight checklist (출력 전 self-check)

발행 전 아래를 통과해야 함:

- [ ] 페르소나가 로드됐고, 5블록이 순서대로 (`결론 → 트레이드오프 → 운영 리스크 → 페르소나 압박 질문 → 다음 질문`)
- [ ] `## 결론` 이 첫 줄, 메타 설명 없음
- [ ] 트레이드오프 표에 비교군 ≥ 2 (1개면 do-nothing 강제)
- [ ] 압박 질문 모든 행에 점수 (`✓/△/✗/N`) 부여, 빈 칸 없음
- [ ] 추측 표현 0개 ("아마도"/"보통은" → "확인 필요: ..." 로 치환됨)
- [ ] 응원·평가·이모지·사과 0개
- [ ] `## 다음 질문` 이 마지막, 후속 질문 형태
- [ ] (interview 모드) 라운드 헤더 `(interview R{n}/3)` 노출, 매 라운드 종료조건 (a~d) 평가됨, 3R 초과 0
- [ ] (interview 모드) 핸드오프는 페이로드 *발행만* — persona-review 가 `/improve` 직접 실행 0

---

## Self-validation

구조 검증: `python3 scripts/validate_skill.py` (human) / `--json` / `--quiet`. frontmatter, 5블록 계약 순서, persona library 디렉토리, 페르소나 override 메커니즘을 결정적으로 확인. stdlib 전용, exit 0=PASS / 1=FAIL.
