---
name: create-document
description: JSON content + template으로 HTML/MD 문서를 빠르게 생성하는 공용 엔진. 스키마 검증을 통해 금지 토큰(이슈 번호·클래스명·테이블명)이 본문에 새어들어가는 것을 구조적으로 차단한다. 단독 호출과 다른 스킬 내부 호출 둘 다 지원.
when_to_use: 같은 구조의 문서를 반복 생성하거나, 콘텐츠와 표현을 분리해 형식화 속도를 올리고 싶을 때. decision-dashboard 같은 문서 생성 스킬이 내부 호출하는 형식화 단계. JSON에 콘텐츠가 이미 정리되어 있어야 사용 가치가 있다 — 콘텐츠 자체를 만드는 단계가 아님.
argument-hint: --template <name> --data <json-path> --out <out-path>
allowed-tools: Bash(python3 *) Bash(mkdir *) Bash(cp *) Bash(ls *) Read Write
---

# Create Document

JSON content를 받아 스키마 검증을 거친 뒤 템플릿에 치환해 HTML/MD 문서를 생성하는 공용 엔진.

## 책임 경계

| 담당 | 비담당 |
|------|--------|
| JSON 구조·필수 필드 검증 | 콘텐츠 자체를 만드는 것 |
| 금지 토큰(forbid 패턴) 차단 | 채팅 맥락에서 의도 추출 |
| `{{key}}` / FOREACH 블록 치환 | 디자인·CSS 변경 |
| 출력 파일 작성 | 사용자 인터뷰 |

콘텐츠 생성·맥락 수집은 **호출 스킬(decision-dashboard 등) 또는 사용자의 책임**이다. create-document는 받은 JSON이 스키마에 맞는지만 검증한다.

---

## 디렉토리 구조

```
create-document/
├── scripts/
│   ├── render.py        # JSON + template → 출력
│   └── validate.py      # 스키마 + 금지 토큰 검사 (render.py가 내부 호출)
├── schemas/
│   └── decision-card.schema.json
├── templates/
│   └── decision-dashboard.html
└── references/
    └── example-decision-card.json
```

템플릿과 스키마는 **같은 이름**으로 짝지어진다 (`templates/<name>.html` ↔ `schemas/<name>.schema.json`). `<name>`을 인자로 넘기면 둘 다 자동 로드.

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
| `--strict-language` | LANGUAGE GATE 패턴(파일·외부 forbid 목록)도 강제 (기본 on) |
| `--json` | 결과를 JSON으로 출력 (chaining 용) |

종료 코드:
- `0` — 검증 통과 + 파일 생성 완료
- `1` — 검증 실패 (어떤 필드의 무엇이 잘못됐는지 stderr에 출력)
- `2` — 사용법 오류 / 파일 없음

---

## 처리 순서

1. `schemas/<name>.schema.json` 로드 → JSON 스키마 파싱
2. `--data` JSON 로드 → 스키마 검증
   - 필수 필드 누락 → 실패
   - 타입 불일치 → 실패
   - `forbid` 패턴 매치 → 실패 (식별자 차단)
   - `mustMatch` / `endsWith` / `minLength` 미충족 → 실패
3. 통과 → `templates/<name>.html`에 데이터 매핑
   - `{{key}}` — 단순 치환 (HTML escape)
   - `{{{key}}}` — raw 치환 (이미 HTML)
   - `<!-- FOREACH key -->...<!-- END -->` — 배열 반복 블록
4. `--out` 경로에 파일 작성

---

## 스키마 형식

자체 포맷 (JSON Schema의 단순화 버전). 예:

```json
{
  "type": "object",
  "required": ["issue", "cards"],
  "properties": {
    "issue":  { "type": "string", "minLength": 1 },
    "branch": { "type": "string" },
    "title":  { "type": "string" },
    "cards": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["card_id", "priority", "title", "background", "judgment_question", "options"],
        "properties": {
          "card_id":  { "type": "string", "pattern": "^c[0-9]+$" },
          "priority": { "type": "string", "enum": ["P0", "P1", "P2"] },
          "title":    { "type": "string", "minLength": 5, "forbid": ["#[0-9]+", "\\w+Entity", "\\w+\\.class"] },
          "background": {
            "type": "object",
            "required": ["situation", "pain", "divergence"],
            "properties": {
              "situation":  { "type": "string", "minLength": 20, "forbid": ["#[0-9]+", "\\w+Entity", "\\w+\\.class", "[a-z]+_(dtm|id|cd)"] },
              "pain":       { "type": "string", "mustMatch": ["[0-9]|놓치|하지\\s*못한|실패"] },
              "divergence": { "type": "string", "minLength": 10 }
            }
          },
          "judgment_question": { "type": "string", "endsWith": "?" },
          "options": {
            "type": "array",
            "minItems": 2,
            "maxItems": 3,
            "items": {
              "type": "object",
              "required": ["key", "label"],
              "properties": {
                "key":   { "type": "string", "enum": ["A", "B", "C"] },
                "label": { "type": "string", "minLength": 5 }
              }
            }
          }
        }
      }
    }
  }
}
```

지원하는 키워드 (JSON Schema 표준 + 자체 확장):
- `type` — `string` / `number` / `boolean` / `array` / `object`
- `required` — 필수 필드 배열
- `properties` — 자식 필드 스키마
- `items` — 배열 요소 스키마
- `minLength` / `maxLength` — 문자열 길이
- `minItems` / `maxItems` — 배열 길이
- `pattern` — 정규식 매치 (전체)
- `enum` — 허용 값 목록
- **`forbid`** (자체) — 정규식 배열, 매치되면 실패
- **`mustMatch`** (자체) — 정규식 배열, 하나라도 매치되어야 통과
- **`endsWith`** (자체) — 특정 문자로 끝나야 통과

---

## 템플릿 치환 규칙

### `{{key}}` 단순 치환

HTML escape 적용. 중첩 키는 점 표기: `{{card.title}}`.

### `{{{key}}}` raw 치환

HTML escape 없이 그대로 삽입. 의도적으로 HTML을 포함시킬 때만 사용.

### `<!-- FOREACH key -->...<!-- END -->` 반복 블록

`key`가 배열일 때, 요소마다 블록을 반복한다. 블록 내부에서 요소의 필드는 `{{key}}`로 접근 (요소가 스코프).

```html
<!-- FOREACH cards -->
<div class="card" id="{{card_id}}">
  <h3>{{title}}</h3>
  <p>{{background.situation}}</p>
</div>
<!-- END -->
```

중첩 FOREACH는 지원 (스코프 스택).

### 누락 키 동작

- 단순 치환 시 키 없음 → 빈 문자열 (silent)
- 단, 스키마에서 `required`로 강제했다면 검증 단계에서 이미 실패.

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
✓ schema valid (15 fields checked, 0 forbid hits)
✓ rendered: claudedocs/PROJ-123/decisions.html
```

실패:
```
✗ schema invalid:
  cards[0].background.situation: forbid pattern matched "#143"
  cards[0].judgment_question: must end with "?"
exit 1
```

### 다른 스킬 내부 호출

decision-dashboard SKILL.md의 generate 모드:

```bash
# 1. 채팅 맥락에서 결정 후보 수집 → JSON 작성 (Write tool)
# 2. create-document 호출
CD_SKILL="${CLAUDE_PLUGIN_ROOT}/skills/create-document"
python3 "${CD_SKILL}/scripts/render.py" \
  --template decision-dashboard \
  --data "${TARGET_DIR}/decisions.json" \
  --out "${FILE}"
```

검증이 실패하면 출력 파일은 만들어지지 않는다. 호출 스킬은 stderr를 보고 JSON을 고친 뒤 재시도.

---

## 추가 forbidden 패턴 확장

프로젝트별 금지 토큰을 추가하려면 스키마 파일에서 `forbid` 배열을 확장한다. 또는 별도 `schemas/<name>.forbidden.json`을 만들어 patterns 배열만 두고, 호출 시 자동 머지하는 형태도 가능 (현재 MVP는 스키마 내 inline만).

---

## Forbidden (이 스킬 자체의 규칙)

- ❌ 콘텐츠 생성·인터뷰 — 받은 JSON을 검증만 한다.
- ❌ 외부 라이브러리(jinja2 등) — stdlib만.
- ❌ 검증 실패해도 출력 파일 작성 — 항상 차단.
- ❌ 스키마 없는 템플릿 호출 — 두 파일이 짝이어야 함.

---

## 자기 검증 체크리스트

호출 전:
- [ ] `--data` JSON이 유효한 JSON 문법인지
- [ ] `--template <name>` 에 대응하는 schema와 template이 존재하는지

호출 후:
- [ ] 종료 코드 0인지 (1이면 stderr 확인)
- [ ] 출력 파일이 의도한 경로에 생성됐는지
