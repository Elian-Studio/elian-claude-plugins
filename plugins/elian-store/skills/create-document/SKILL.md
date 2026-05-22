---
name: create-document
description: When a skill or user needs to render structured documents (HTML/MD) from JSON content with schema-level validation that blocks identifier leakage (#143·*.class·Entity·snake_case columns) before output. Replaces handwritten HTML blocks with JSON authoring + template substitution — 3~6× faster for repeated card-style documents. 같은 구조의 문서를 반복 생성하는 상황에서 콘텐츠와 표현을 분리해 가속한다. 독립 호출과 다른 스킬(decision-dashboard 등) 내부 호출 둘 다 지원.
when_to_use: 같은 구조의 문서를 반복 생성하는 상황, 또는 콘텐츠와 표현을 분리해 형식화 속도를 올리고 싶을 때. decision-dashboard 같은 문서 생성 스킬이 내부 호출하는 형식화 단계. 사용자 입장에서는 "JSON으로 문서 만들어줘", "이 데이터로 대시보드 렌더", "JSON → HTML 치환" 같은 요청.
argument-hint: --template <name> --data <json-path> --out <out-path>
allowed-tools: Bash(python3 *) Bash(mkdir *) Bash(cp *) Bash(ls *) Read Write
---

# Create Document

JSON content를 받아 스키마 검증을 거친 뒤 템플릿에 치환해 HTML/MD 문서를 생성하는 공용 엔진.

---

## Where this fits in the workflow

```
brainstorm / design / decision-dashboard 등
        ↓ (콘텐츠 JSON 작성)
   ▶ CREATE-DOCUMENT ◀  (스키마 검증 + 템플릿 치환)
        ↓ (검증 통과 HTML/MD)
   review → ship / 사용자 확인 / 다음 스킬 입력
```

- **Upstream skills**가 채팅 맥락에서 콘텐츠를 정리해 JSON으로 넘긴다.
- **이 스킬**이 JSON을 스키마에 맞춰 검증하고, 통과하면 템플릿에 치환해 파일을 쓴다.
- 검증 실패 시 출력 파일은 생성되지 않는다 — 구조적 차단.
- **Downstream**: 생성된 HTML/MD 파일과 (옵션) 검증 결과 JSON이 다음 스킬·사용자에게 전달된다.

---

## Modes

이 스킬은 단일 모드(`render`)다 — JSON → 검증 → 치환 → 파일 출력의 결정적 파이프라인. 검증 결과만 받고 싶으면 `scripts/validate.py`를 직접 호출(스키마 + 데이터 두 인자).

## Standing rules

(아래 규칙은 절차가 아니라 매 호출에 항상 적용되는 원칙이다.)

- **콘텐츠 생성은 호출 스킬 책임.** 이 스킬은 받은 JSON을 검증·치환만 한다. 빈 필드를 사용자에게 묻거나 데이터를 추측하지 않는다.
- **검증 실패 → 파일 미생성.** 절대 부분 출력하지 않는다. stderr에 위반 필드를 모두 보고하고 exit 1.
- **stdlib only.** jinja2/pyyaml 같은 외부 라이브러리를 추가하지 않는다.
- **스키마와 템플릿은 짝.** `templates/<name>.html` ↔ `schemas/<name>.schema.json` 동일 이름으로 자동 연결.

## Automated vs needs your taste

(automated decision gating — 무엇을 Claude/스크립트가 자동 결정하고, 무엇이 사용자/호출 스킬의 taste 영역인지 명시.)

| Claude/스크립트가 자동 결정 | 호출 스킬(taste) 또는 사용자 결정 |
|---|---|
| 스키마 적합성(type/required/length/enum) | 어떤 템플릿을 쓸지(`--template`) |
| 금지 토큰(forbid 정규식) 패턴 매치 | JSON 콘텐츠 자체 (situation/pain/divergence 본문) |
| `mustMatch` / `endsWith` 검사 | 새 forbidden 패턴 등록 (스키마 편집) |
| `{{key}}` 치환 + HTML escape | 카드 우선순위, 옵션 라벨 표현 |
| 누락 키 → 빈 문자열로 대체 | 새 템플릿/스키마 페어 추가 |

자동이 잘못 잡으면 사용자가 스키마를 편집해 보정. 자동이 막은 카드를 "약간 우회"로 통과시키는 것은 금지 — 카드를 다시 product-perspective로 쓰라는 신호.

---

## 책임 경계

| 담당 | 비담당 |
|------|--------|
| JSON 구조·필수 필드 검증 | 콘텐츠 자체를 만드는 것 |
| 금지 토큰(forbid 패턴) 차단 | 채팅 맥락에서 의도 추출 |
| `{{key}}` / FOREACH 블록 치환 | 디자인·CSS 변경 |
| 출력 파일 작성 | 사용자 인터뷰 |

---

## 디렉토리 구조

```
create-document/
├── scripts/
│   ├── render.py        # 메인 엔트리 — JSON + template → 출력
│   └── validate.py      # 스키마 검증 단독 호출도 가능
├── schemas/
│   ├── decision-dashboard.schema.json  # 결정 카드 (decision-dashboard 호출)
│   ├── teammate-spawn.schema.json      # 7-slot teammate spawn (generate-teammate 호출)
│   └── review-output.schema.json       # 5블록 페르소나 review (on-call-elian 양식)
├── templates/
│   ├── decision-dashboard.html         # HTML 결정 대시보드
│   ├── teammate-spawn.md               # Markdown teammate spawn plan
│   └── review-output.md                # Markdown 페르소나 review
└── references/
    ├── before-after-card-authoring.md  # BEFORE/AFTER 비교 예시
    ├── example-decision-card.json      # 결정 카드 데이터 예시
    ├── example-teammate-spawn.json     # 3 teammate spawn 예시
    └── example-review-output.json      # daniel 페르소나 review 예시
```

템플릿과 스키마는 **같은 이름**으로 짝지어진다. 같은 이름의 `<name>.html` 또는 `<name>.md` 둘 다 자동 탐색.

현재 지원하는 use case:
- `decision-dashboard` — `/decision-dashboard` 가 호출. PO 5-min 결정 카드.
- `teammate-spawn` — `/generate-teammate` 가 호출. 7-slot 일관 spawn prompt.
- `review-output` — `/on-call-elian` 양식. 5블록 (Conclusion / Trade-offs / Operational risks / 8 pressure questions / Next question) + interview rounds + handoff payload.

---

## 인터페이스

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/render.py" \
  --template <name> \
  --data <json-path> \
  --out <out-path>
```

| 옵션 | 의미 |
|------|------|
| `--template <name>` | `templates/<name>.html` + `schemas/<name>.schema.json` 자동 로드 |
| `--data <path>` | 치환할 JSON 데이터 |
| `--out <path>` | 출력 파일 경로 |
| `--schema <name>` | 다른 스키마로 검증하고 싶을 때 (옵션) |
| `--json` | 결과를 JSON으로 출력 (chaining 용) |

`$ARGUMENTS`는 SKILL의 frontmatter `argument-hint`에 명세된 형식(`--template ... --data ... --out ...`)대로 전달된다. 종료 코드:
- `0` — 검증 통과 + 파일 생성
- `1` — 검증 실패 (stderr에 `필드: 무엇이 잘못` 보고)
- `2` — 사용법 오류 / 파일 없음

---

## Procedure (처리 순서)

1. `schemas/<name>.schema.json` 로드 → JSON 스키마 파싱
2. `--data` JSON 로드 → 스키마 검증
   - 필수 필드 누락 / 타입 불일치 → 실패
   - `forbid` 패턴 매치 (식별자) → 실패
   - `mustMatch` / `endsWith` / `minLength` 미충족 → 실패
3. 통과 → `templates/<name>.html`에 데이터 매핑
   - `{{key}}` — 단순 치환 (HTML escape)
   - `{{{key}}}` — raw 치환 (이미 HTML)
   - `<!-- FOREACH key -->...<!-- END -->` — 배열 반복
4. `--out` 경로에 파일 작성. 디렉토리는 자동 생성.

---

## 스키마 형식 (자체 포맷)

JSON Schema 표준 키워드 + 자체 확장.

지원 키워드:
- `type` — `string` / `number` / `boolean` / `array` / `object`
- `required` — 필수 필드 배열
- `properties` — 자식 필드 스키마
- `items` — 배열 요소 스키마
- `minLength` / `maxLength` — 문자열 길이
- `minItems` / `maxItems` — 배열 길이
- `pattern` — 정규식 `fullmatch`
- `enum` — 허용 값 목록
- **`forbid`** (자체) — 정규식 배열, 매치되면 실패
- **`mustMatch`** (자체) — 정규식 배열, 하나라도 매치되어야 통과
- **`endsWith`** (자체) — 특정 문자로 끝나야 통과

예시: [`schemas/decision-dashboard.schema.json`](schemas/decision-dashboard.schema.json)

---

## 템플릿 치환 규칙

- `{{key}}` 단순 치환 — HTML escape 적용. 점 표기로 중첩: `{{background.situation}}`.
- `{{{key}}}` raw 치환 — escape 없음. 미리 만든 HTML 조각용 (예: `rec_badge`).
- `<!-- FOREACH key -->...<!-- END -->` — 배열 반복. 요소가 스코프. 중첩 가능.
- 누락 키 → 빈 문자열 (단, `required` 강제 시 검증 단계에서 이미 실패).

예시: [`templates/decision-dashboard.html`](templates/decision-dashboard.html)에서 `priority_groups` / `cards` / `options` 3중 FOREACH를 확인.

---

## 사용 예시

### 단독 호출

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/render.py" \
  --template decision-dashboard \
  --data ./decisions.json \
  --out claudedocs/PROJ-123/decisions.html
```

성공:
```
✓ schema valid (39 fields checked, 0 forbid hits)
✓ rendered: claudedocs/PROJ-123/decisions.html
```

실패:
```
✗ schema invalid (4 errors):
  cards[0].background.situation: 금지 패턴 '#[0-9]+' 매치 — '#143'
  cards[0].judgment_question: '?' 로 끝나야 함
  cards[0].background.pain: mustMatch 미충족 (적어도 하나 매치: ['[0-9]|놓치|...'])
  cards[0].options[1].label: 길이 4 < minLength 5
exit 1
```

### 다른 스킬 내부 호출

decision-dashboard generate 단계:

```bash
CD="${CLAUDE_PLUGIN_ROOT}/skills/create-document"
python3 "${CD}/scripts/render.py" \
  --template decision-dashboard \
  --data "${TARGET_DIR}/decisions.json" \
  --out "${FILE}"
```

검증 실패 시 출력 파일은 만들어지지 않는다. 호출 스킬은 stderr를 보고 JSON을 고친 뒤 재시도.

[BEFORE/AFTER 비교 예시 — references/before-after-card-authoring.md](references/before-after-card-authoring.md)
[좋은 JSON 데이터 예시 — references/example-decision-card.json](references/example-decision-card.json)

---

## Reflection (호출 종료 시 보고할 패턴)

호출 스킬은 render 종료 후 (선택) 다음 형식으로 사용자에게 보고할 수 있다 — "praise 말고 관찰 패턴" 원칙:

```
N fields validated. Patterns I noticed:
- forbid 패턴 매치 X건 → 스키마가 잘 calibrated 됐거나, 콘텐츠 수집 단계에서 식별자가 자주 새어들어왔다.
  반복되면 스키마의 patterns 확장 또는 콘텐츠 수집 가이드 강화 후보.
- 카드 N장 중 'recommended' 옵션 비율 X% → 권고 라벨이 과도하거나 약할 수 있다.
- pain 필드가 '숫자 없음'으로 fallback된 카드 비율 → mustMatch 규칙 강화 검토.
```

이건 호출 스킬의 책임. create-document 자체는 단순 보고만 한다 (`✓ schema valid (N fields)`).

## Downstream / persistent output

생성된 HTML/MD 파일은 단순 산출물이 아니라 **downstream 스킬의 입력**이 될 수 있다.

- decision-dashboard → `decisions.html` → 사용자 결정 → `decisions-final.json` (영구) → implement / ship
- 후행 스킬은 final JSON에서 "무엇이 결정됐고 왜"를 읽는다.

따라서:
- 출력 경로는 호출 스킬이 정한 컨벤션을 따른다 (`claudedocs/{ISSUE}/...`).
- 검증 통과만 한 산출물은 후속 스킬이 신뢰할 수 있다는 계약.

---

## Forbidden

- ❌ 콘텐츠 생성·인터뷰 — 받은 JSON을 검증만 한다.
- ❌ 외부 라이브러리(jinja2 등) — stdlib만.
- ❌ 검증 실패해도 출력 파일 작성 — 항상 차단.
- ❌ 스키마 없는 템플릿 호출 — 두 파일이 짝이어야 함.
- ❌ 자동 forbidden 패턴 우회 — 막힌 카드는 다시 쓰라는 신호.

---

## Pitfall / Known issues

### Pitfall 1: 스키마와 템플릿 placeholder 이름 불일치

템플릿에 `{{open_class}}`가 있는데 스키마에 해당 필드를 정의하지 않으면 검증에서 catch 안 되고 출력에 빈 문자열만 남는다. **새 placeholder를 템플릿에 추가하면 스키마에도 같은 키를 정의**해 누락 시 명시적 실패되게 하자.

### Pitfall 2: 정규식 forbid 패턴이 너무 넓음

예: `\b[A-Z][a-z]+\b` (CamelCase) → 영문 일반명사도 차단해버림. 패턴은 **구체적**으로 — `[A-Z][a-zA-Z]*Entity`, `[A-Z][a-zA-Z]*\.class`처럼 접미사 포함.

### Pitfall 3: HTML escape 누락 (raw 치환 오용)

`{{{key}}}` raw 치환은 사용자 입력이 들어가는 필드에는 절대 쓰지 않는다. `rec_badge`처럼 **호출 스킬이 직접 만든 안전한 HTML 조각**에만.

### Pitfall 4: FOREACH 내부 스코프 누수

`<!-- FOREACH cards -->` 내부에서 `{{issue}}`(상위 스코프)를 쓰면 동작은 한다(get_value가 outer까지 탐색). 단, 의도치 않게 cards에 `issue` 필드가 있으면 그게 우선. 가능하면 **명시적 키 이름**으로 충돌 회피.

---

## Auto-validation 자가 검증

`render.py`가 호출되면 자동으로 validate.py의 모든 규칙을 수행한다. 별도 실행 필요 없음.

스키마 검증만 독립 실행하려면:
```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate.py" \
  schemas/decision-dashboard.schema.json \
  ./decisions.json --json
```

`--json` 모드는 다른 스킬과 chaining 가능.

---

## Self-check before publishing

호출 전:
- [ ] `--data` JSON이 유효한 JSON 문법인가
- [ ] `--template <name>` 에 대응하는 schema와 template이 모두 존재하는가
- [ ] 새 forbidden 패턴이 필요하면 스키마를 미리 갱신했는가
- [ ] FOREACH 블록의 배열 키가 데이터에 실제로 존재하는가
- [ ] `{{{key}}}` raw 치환이 신뢰 가능한 출처(호출 스킬 직접 작성)인가

호출 후:
- [ ] 종료 코드 0인지 (1이면 stderr 확인)
- [ ] 출력 파일이 의도한 경로에 생성됐는가
- [ ] (선택) downstream 스킬에 전달하기 전 추가 validator(예: decision-dashboard의 4 gates) 통과했는가
