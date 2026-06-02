---
name: persona-review
description: "When a user wants a plan, design, document, PR description, or idea reviewed through Daniel, Evans, Dean, Martin, multiple persona reviewers, or a custom persona, route the target to selected read-only persona reviewer subagent(s) and return each persona's native judgment style without a shared scorecard or fixed output template."
when_to_use: "Use before locking in a non-trivial decision, when the user asks for a persona lens such as Daniel, Evans, Dean, Martin, multiple persona reviewers, or a custom persona, or when a fuzzy idea needs one clarification before critique. Trigger phrases: '페르소나로 리뷰해줘', '다니엘 시각으로', '에반스로 도메인 점검', '딘 시각으로 스케일 압박', '마틴으로 클린코드 점검', '/persona-review', '--depth interview'."
argument-hint: "<target-path-or-text> [--persona daniel|evans|dean|martin|all|<path-to-custom>|comma-list] [--depth quick|deep|interview]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git diff*), Bash(git log*), Bash(git status*), Agent, AskUserQuestion
---

# /persona-review — 페르소나 렌즈 리뷰

사용자의 사고·문서·계획을 **선택된 페르소나 reviewer subagent**에게 맡겨 리뷰한다. 이 스킬의 목적은 점수표를 채우는 것이 아니라, 페르소나별 사고 습관으로 약한 가정·숨은 비용·다음 질문을 드러내는 것이다.

메인 스킬은 리뷰어가 아니다. 메인 스킬은 대상 수집, 입력 농도 판정, subagent dispatch, 결과 종합만 담당한다. 실제 리뷰는 `persona-daniel-reviewer`, `persona-evans-reviewer`, `persona-dean-reviewer`, `persona-martin-reviewer`, 또는 `persona-custom-reviewer`가 수행한다.

단, **상대가 뭘 원하는지 모르면 단정하지 않는다.** 입력이 한 줄짜리거나 목표·범위가 모호하면 리뷰로 직행하지 말고 의도를 먼저 묻는다. 질문은 한 번에 하나만, 선택지 2~3개 + 자유 입력을 허용한다.

핵심 계약:

- 페르소나별 자유 형식. 공통 5블록, 공통 표, 공통 점수표를 강제하지 않는다.
- `Pressure Questions`는 내부 렌즈다. 모든 질문을 행으로 평가하지 않는다.
- 리뷰는 read-only다. 메인 스킬과 subagent 모두 코드 수정·파일 생성·git 변경을 하지 않는다.
- built-in persona는 반드시 대응 subagent로 실행한다. 메인 스킬이 대신 리뷰하지 않는다.
- 추측 금지. 본문·diff·파일에서 확인되지 않으면 "확인 필요: ..."로 남긴다.
- 끝에는 자연스러운 다음 질문이나 다음 액션을 남긴다.

---

## Standing Rules

- 메인 스킬은 lead/router다. built-in persona 리뷰를 직접 작성하지 않는다.
- subagent output은 가능한 그대로 보존한다. lead synthesis는 multi-persona일 때만 붙인다.
- `$ARGUMENTS` 명시값이 기본값이나 환경변수보다 우선한다.
- `${PERSONA_REVIEW_DEFAULT}`는 기본 persona를, `${PERSONA_REVIEW_DEPTH}`는 기본 depth를 바꿀 수 있다.
- 모든 단계는 read-only다. 실행이 필요하면 handoff payload만 발행한다.

## Modes

| Mode | What it does | Use when |
|---|---|---|
| `quick` (default) | 선택 persona subagent 1회 실행 | 빠른 판단, 문서/아이디어 1개 리뷰 |
| `deep` | 더 많은 파일·diff·참조를 subagent prompt에 포함하거나 subagent가 추가 read-only 탐색 | 설계·PR·운영 변경처럼 맥락이 중요한 대상 |
| `interview` | subagent 리뷰 후 lead가 가장 큰 불확실성 1개를 묻고 최대 3라운드 재실행 | 결론이 목표·제약·소유권 같은 답변에 따라 갈릴 때 |

`--persona`와 `--depth`는 독립이다. `--persona evans --depth deep`이면 Evans 방식으로 더 많은 근거를 읽고 리뷰한다.

## Where this fits in the workflow

```
brainstorm → persona-review lead → persona reviewer subagent(s) → lead aggregation → decision-dashboard
                                                                └─ handoff payload → improve / implement / fix
```

- **선행**: `/brainstorm` 또는 사용자가 작성한 draft, 설계, PR 설명, 한 줄 아이디어.
- **이 스킬**: 페르소나 선택 → 입력 농도 판정 → 필요 시 질문 → 대응 subagent 실행 → 결과 relay/aggregation.
- **후행**: 결정 잠금은 `/decision-dashboard`, 개선 실행은 `/improve`·`/implement`·`/fix`. 이 스킬은 실행하지 않고 필요한 경우 handoff payload만 발행한다.

## Persona library

`references/personas/` 디렉토리에 있는 페르소나 중 하나를 `--persona` 인자로 선택한다. 페르소나는 출력 양식이 아니라 **판단 방식**을 바꾼다.

### 기본 제공 페르소나

| 페르소나 | subagent_type | 압박 축 | 어떤 대상에 강한가 |
|---|---|---|---|
| [`daniel`](references/personas/daniel.md) (default) | `persona-daniel-reviewer` | 운영 가능성, 메커니즘, axiom vs policy, 자동화 | 일반 리뷰 / 운영 변경 / 일상 코드 |
| [`evans`](references/personas/evans.md) | `persona-evans-reviewer` | DDD, bounded context, ubiquitous language, aggregate, ACL | 도메인 모델·아키텍처 결정, 새 서비스 경계 |
| [`dean`](references/personas/dean.md) | `persona-dean-reviewer` | 분산·스케일, tail latency, SPOF, hot key, backpressure | 트래픽 증가 대비, 큐·캐시·DB scaling |
| [`martin`](references/personas/martin.md) | `persona-martin-reviewer` | Clean Code / SOLID / TDD, naming, SRP, testability | 코드 품질, 객체지향 설계, 테스트 전략 |
| custom path | `persona-custom-reviewer` | custom persona file 기준 | 사용자가 정의한 렌즈 |

### 어떤 상황에 어떤 페르소나

| 상황 | 권장 페르소나 | 이유 |
|---|---|---|
| 운영 변경, 알림·재시도·hook 도입 | `daniel` | 운영 가능성·자동화에 강함 |
| 도메인 모델 설계, 새 aggregate / 서비스 경계 | `evans` | DDD가 도메인 정합성을 압박 |
| 트래픽 100x 대비, 캐시·큐·DB 설계, latency 회귀 | `dean` | 분산·tail latency 시각이 필요 |
| 코드 리뷰, 함수 단위 리팩토링, 테스트 전략 | `martin` | 함수/객체 단위 품질 압박 |
| 도메인 + 분산이 같이 걸린 결정 | `evans` 후 `dean` 순차 리뷰 | 한 페르소나는 한 축에 집중 |
| 비-기술적 결정 (스코프, 일정, 팀) | 다른 스킬 권장 | 이 스킬은 기술 판단 렌즈에 최적화 |

### 커스텀 페르소나

커스텀 페르소나는 기본 페르소나와 같은 7섹션 구조를 권장한다.

```markdown
# Persona: <name>

## Voice
## Hard Rules
## Decision Heuristics
## Priorities
## Forbidden
## Pressure Questions
## Blind Spots
```

`Pressure Questions`는 체크리스트가 아니라 리뷰 때 떠올릴 질문 묶음이다. 커스텀 페르소나는 자기만의 출력 구조를 가질 수 있고, 공통 점수표를 만들 필요가 없다. 커스텀 경로는 메인 스킬이 파일을 읽어 `persona-custom-reviewer` prompt에 포함한다.

## What's automated vs what needs your taste

| Claude가 자동으로 결정 | 사용자가 결정 |
|---|---|
| 대상 파일/텍스트/diff 수집 | 리뷰 대상 |
| 입력이 너무 얇은지 판정 | 의도 질문에 대한 답 |
| 기본 페르소나 `daniel`과 대응 subagent 적용 | 다른 페르소나, `all`, comma-list, custom path |
| built-in/custom persona dispatch | 페르소나 판단에 동의/반박 |
| single result relay 또는 multi-persona conflict aggregation | 다음 액션 채택 여부 |
| 필요 시 handoff payload 발행 | 실제 개선/구현 실행 여부 |

## Common Review Contract

공통 계약은 아래가 전부다. 그 외 구조는 subagent에 맡긴다.

1. **Lead with the useful judgment.** 결론부터 말하되, 페르소나가 모델/다이어그램/숫자부터 시작하는 편이 더 정확하면 그렇게 한다.
2. **Use the persona's native shape.** Daniel은 운영 리스크와 결정 경계, Evans는 모델·언어·context map, Dean은 병목·분포·fault model, Martin은 코드 smell·함수 구조·테스트로 리뷰한다.
3. **No scorecard.** `Pressure Questions`를 전부 행으로 펼치거나 점수화하지 않는다. 필요한 질문만 본문에 녹인다.
4. **Evidence over vibe.** 파일·diff·본문 근거가 있으면 짧게 인용하거나 위치를 말한다. 없으면 추측하지 않는다.
5. **Expose trade-offs only when useful.** 표가 판단을 선명하게 만들 때만 쓴다. 표 자체를 의무화하지 않는다.
6. **End with one next move.** 자연스러운 다음 질문, 결정, 보강 요청, 또는 handoff payload 중 하나로 마무리한다.

## Subagent Execution Contract

메인 스킬은 lead/router다. built-in persona 요청은 반드시 대응 subagent로 실행한다.

| persona arg | subagent_type |
|---|---|
| `daniel` 또는 생략 | `persona-daniel-reviewer` |
| `evans` | `persona-evans-reviewer` |
| `dean` | `persona-dean-reviewer` |
| `martin` | `persona-martin-reviewer` |
| `all` | 위 4개를 병렬 실행 |
| `daniel,evans` 같은 comma-list | 지정된 subagent만 병렬 실행 |
| custom file path | `persona-custom-reviewer`에 custom persona 본문을 포함해 실행 |

### Agent prompt payload

각 subagent prompt에는 아래 정보를 넣는다.

```markdown
[ROLE]
Run a read-only persona review for /persona-review.

[USER INTENT]
<사용자가 원하는 리뷰 의도. 없으면 "not specified">

[TARGET]
<파일 경로, diff 요약, 또는 자유 텍스트>

[DEPTH]
quick | deep | interview

[EVIDENCE]
<메인 스킬이 이미 읽은 본문/diff/파일 경로>

[CONSTRAINTS]
- Do not edit files.
- Do not create files.
- Do not run destructive commands.
- Do not output a scorecard or fixed 5-block template.
- End with one next question/action/handoff.
```

### Result handling

- **single persona**: subagent 결과를 그대로 전달한다. 명백한 중복 헤더 제거 외에는 다시 쓰지 않는다.
- **multiple personas / `all`**: subagent 결과를 persona별로 보존하고, lead가 마지막에 `## Lead synthesis` 한 섹션만 추가한다. synthesis는 충돌점, 공통 리스크, 다음 결정 1개만 다룬다.
- **interview**: lead가 subagent 결과에서 결론을 가르는 질문 1개만 골라 사용자에게 묻고 멈춘다. 답변 후 같은 subagent들을 다시 실행한다.
- **custom persona**: custom file이 없거나 섹션이 부족하면 사용자에게 알리고 `daniel`로 폴백할지 묻는다.

## Workflow

```
Phase 0: Persona 선택 또는 추천
Phase 1: Target 수집 + 입력 농도 판정
Phase 2: Persona → subagent dispatch 결정
Phase 3: subagent prompt 구성 + Agent 실행
Phase 4: subagent 결과 relay/aggregation
Phase 4.5: interview 수렴 루프 (--depth interview)
Phase 5: handoff 또는 종료
```

### Procedure

1. `$ARGUMENTS`에서 target, `--persona`, `--depth`를 파싱한다.
2. persona가 없으면 `${PERSONA_REVIEW_DEFAULT}`를 보고, 없으면 `daniel`을 사용한다.
3. depth가 없으면 `${PERSONA_REVIEW_DEPTH}`를 보고, 없으면 `quick`을 사용한다.
4. target을 읽고 입력 농도를 판정한다.
5. persona arg를 subagent_type으로 매핑한다.
6. read-only evidence payload를 만들어 `Agent`로 실행한다.
7. single persona면 결과를 그대로 전달하고, multiple persona면 lead synthesis만 추가한다.
8. `interview`면 결론을 가르는 질문 1개만 묻고 멈춘다.

### Phase 0: Persona 선택 또는 추천

`--persona`가 명시되지 않은 경우 대상 분석으로 권장 페르소나를 한 줄 안내하되, 기본은 `daniel`로 진행한다.

- `**/domain/`, `**/aggregate/`, 도메인 모델 파일 → `evans`
- `**/queue/`, `**/scheduler/`, replication, sharding, cache 관련 → `dean`
- 새 함수 / 클래스 / 리팩토링 diff → `martin`
- 운영·인프라·hook·재시도 → `daniel`
- 매칭 불명확 → `daniel`

### Phase 1: Target 수집 + 입력 농도 판정

| 인자 형태 | 해석 |
|---|---|
| 파일 경로 (`.md`, `.ts`, `.java`, etc) | `Read`로 본문 로드 |
| URL (PR/issue) | 외부 페치가 필요한지 사용자에게 확인 |
| 자유 텍스트 | 인자 자체를 대상으로 사용 |
| 비어있음 | `AskUserQuestion`: "리뷰 대상? (a) 현재 변경 git diff (b) 특정 파일 (c) 텍스트" |

입력이 얇거나 모호하면 리뷰 전에 질문한다.

- **얇음**: 한두 줄 자유 텍스트, 목표·범위 불명확 → 의도 질문 1개
- **모호**: 문서는 있으나 목표/완료기준 불명확 → 가장 불명확한 축 1개
- **충분**: 목표·범위·제약·완료기준이 있음 → 질문 없이 리뷰

### Phase 2: Persona → subagent dispatch 결정

- 이름 인자: `Subagent Execution Contract`의 대응 `subagent_type` 선택
- `all` 또는 comma-list: 여러 subagent를 병렬 실행하도록 계획
- 경로 인자: 해당 파일을 `Read`로 읽고 `persona-custom-reviewer` 선택
- custom 파일이 없으면 사용자에게 알리고 `daniel` 폴백 여부를 질문

### Phase 3: subagent prompt 구성 + Agent 실행

메인 스킬은 필요한 본문/diff를 읽어 prompt payload에 담고 `Agent`를 호출한다. subagent가 추가 탐색을 해야 할 때도 read-only 범위에 머무르게 한다.

예시:

```typescript
Agent({
  subagent_type: 'persona-evans-reviewer',
  prompt: '<payload>'
})
```

### Phase 4: subagent 결과 relay/aggregation

single persona면 결과를 그대로 전달한다. multiple persona면 각 결과를 아래처럼 구분하고, 마지막에 lead synthesis만 붙인다.

```markdown
## daniel
<persona-daniel-reviewer output>

## dean
<persona-dean-reviewer output>

## Lead synthesis
- 공통 리스크: ...
- 충돌점: ...
- 다음 결정: ...
```

BEFORE/AFTER 예시는 [`references/example-review.md`](references/example-review.md)를 참고한다. 예시는 출력 고정 형식이 아니라 방향성 샘플이다.

### Phase 4.5: 수렴 루프 (`--depth interview`)

`quick`/`deep`은 subagent 실행 1회 후 종료한다. `interview`는 최대 3라운드까지 반복한다.

1. 방금 subagent 결과에서 결론을 가르는 가장 큰 불확실성 1개를 고른다.
2. `AskUserQuestion`으로 그 지점만 묻는다. 한 번에 2개 이상 묻지 않는다.
3. 답변을 반영해 같은 subagent를 다시 실행한다.
4. 각 라운드 앞에 `(interview R{n}/3)`만 붙인다.
5. 결론이 충분히 단정되거나, 사용자가 중단하거나, 3라운드에 도달하면 멈춘다.

### Phase 5: handoff 또는 종료

리뷰가 실행으로 이어져야 하면 handoff payload를 발행만 한다. 이 스킬이 `/improve`, `/implement`, `/fix`를 직접 실행하지 않는다.

```markdown
(handoff → improve/implement/fix <target>)
- persona: <name>
- judgment: <수렴된 판단 한 줄>
- change intent: <무엇을 바꿀지>
- evidence: <핵심 근거>
- risks to preserve: <놓치면 안 되는 리스크>
- out of scope: <이번에 하지 않을 것>
```

## Pitfalls

| Pitfall | Avoidance |
|---|---|
| 페르소나 리뷰를 체점표로 바꿈 | 질문 목록은 내부 렌즈로만 사용하고, 출력은 페르소나 방식으로 작성 |
| 모든 페르소나가 같은 구조로 답함 | persona file의 `Voice`와 `Forbidden`을 먼저 적용 |
| 메인 스킬이 직접 리뷰를 써버림 | built-in persona는 반드시 대응 subagent에 맡김 |
| multi-persona 결과를 한 문체로 재작성 | 각 subagent output은 보존하고 lead synthesis만 추가 |
| 한 줄 아이디어에 과도한 비판을 쏟음 | 먼저 의도·성공 기준을 한 질문으로 확인 |
| 추측으로 빈칸을 채움 | "확인 필요: ..."로 남기고 다음 질문으로 연결 |
| 리뷰가 실행으로 넘어감 | handoff만 발행, 파일 변경은 하지 않음 |

## Forbidden

- 코드 수정 / 파일 생성 / git 변경
- 공통 5블록 출력 강제
- 점수표·등급표·전수 체크리스트 출력
- `Pressure Questions` 전체를 기계적으로 평가
- built-in persona 리뷰를 메인 스킬이 직접 작성
- subagent 결과를 임의로 고쳐 한 문체로 평탄화
- 평가·응원·마케팅 톤·이모지
- 확인되지 않은 가정으로 결론 채우기
- 외부 URL 자동 페치
- interview 모드 3라운드 초과
- handoff payload를 이 스킬이 직접 실행

## Validation

```bash
python3 plugins/elian-store/skills/persona-review/scripts/validate_skill.py
```

자가 검증은 다음을 확인한다.

- frontmatter와 read-only guard
- `Agent` tool과 persona reviewer agent 파일 존재
- persona reference와 example link
- 공통 5블록/점수표 강제 문구가 없는지
- persona override와 interview mode 문서화

## Pre-flight

- [ ] 대상과 페르소나가 명확한가
- [ ] 입력이 얇으면 리뷰 전에 질문했는가
- [ ] built-in persona는 대응 subagent로 실행했는가
- [ ] subagent prompt에 사용자 의도, target, depth, evidence, constraints가 들어갔는가
- [ ] 점수표나 공통 템플릿을 만들지 않았는가
- [ ] 확인된 근거와 확인 필요 사항을 분리했는가
- [ ] 마지막에 다음 질문 또는 다음 액션이 있는가
