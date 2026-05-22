---
name: decision-dashboard
description: When 3+ pending decisions block PO/team progress, capture them in a printable HTML artifact so the team can decide in 5 minutes instead of long Slack threads. Replaces "decision fatigue scattered across messages" with "one page, all options, traceable choice + memo + downloadable JSON for downstream skills". 카드 본문에 이슈 번호·클래스명 같은 식별자가 새어들어가는 것은 create-document 스키마가 구조적으로 차단한다.
when_to_use: 3+ decisions pile up in a review (architecture / DDL / UX / consistency), the user says "make a decision dashboard" / "lay out the choices", or chat explanations are too long to inline. Skip for 1-2 decisions (just ask in chat).
argument-hint: [issue-id] [output-dir?] [mode?]
allowed-tools: Bash(cp *) Bash(open *) Bash(date *) Bash(git branch*) Bash(mkdir *) Bash(rm claudedocs/*) Bash(python3 *) Edit Read Write
---

# Decision Dashboard Generator

When 3+ decisions pile up and the decision-maker (PO / team lead) cannot read every chat thread to the bottom, this skill captures the decisions as a **single printable HTML artifact** so the team can pick A/B/C in 5 minutes. The decisions are then persisted as JSON for downstream skills.

---

## Where this fits in the workflow

```
brainstorm → design → ▶ DECISION-DASHBOARD ◀ → implement → review → ship
                          (artifact-forcing
                           moment for taste)
```

- **Upstream skills** (brainstorm / design / review) surface the decisions.
- **This skill** turns those decisions into a printable HTML page and persists them as JSON.
- **Downstream skills** (implement / ship) read `decisions/{ISSUE}-final.json` to know "what was decided and why" as context.

이 스킬은 **콘텐츠 조립**(채팅 맥락에서 카드 후보 정리 → JSON 작성)을 담당하고, **JSON → HTML 치환·검증**은 자매 스킬 `create-document`에 위임한다.

---

## What's automated vs what needs your taste

| Claude decides automatically | User decides |
|------------------------------|--------------|
| Card numbering (c1, c2, …) | Per-card option choice (A/B/C/D) |
| P0/P1/P2 priority classification | Whether each option's definition is right |
| Option label rewrite (impl-term → outcome-term) | When to use "Other (custom input)" |
| LANGUAGE GATE filtering (block internal identifiers) | Defer / push a decision to a later session |
| Background's 3-sentence skeleton applied | Propose new options when offered ones don't fit |

automation이 잘못 작동하면 사용자가 메모로 수정한다. `D (Other)` 선택 + 메모 비어있는 카드는 publish 차단.

---

## Modes

`generate` (default) — 카드 만들어 HTML 산출.
`finalize` — 사용자가 선택을 마친 결과 JSON을 받아서 영구 저장 + disposable HTML 정리.

---

## Auto-invoke vs explicit

**Auto-invoke**:
- 3+ decisions awaiting user confirmation
- One decision's explanation is too long to inline in chat
- Review output (consistency / architecture / DDL / UX) surfaces multiple decisions

**Explicit invocation**:
- `/elian-store:decision-dashboard`
- "make a decision dashboard", "lay out the choices"

**Do NOT invoke when**:
- 1-2 decisions → just ask in chat (AskUserQuestion or short Markdown)
- Simple yes/no confirmation → just ask
- One-way choice on an implementation suggestion → short answer

---

## Output location

Default path:
```
{output-dir}/{ISSUE_ID}/decisions-{YYYY-MM-DD-HHmm}.html
```

`{output-dir}` precedence:
1. `$ARGUMENTS[1]` (explicit override)
2. `DECISIONS_DIR` env var
3. `claudedocs` (default)

Filenames include hour-minute (HHmm) so multiple runs in one day on one issue don't collide.

---

## Card-body authoring rules

(These rules apply to every card always; they are standing instructions, not procedure. create-document 의 `decision-dashboard.schema.json` 이 이 규칙을 강제한다 — 위반 시 publish 차단.)

A decision document is **not a conversation**. The decision-maker (PO / team lead / future-self) doesn't read code. They have 5 minutes to pick A or B. So the card body (title / background / judgment axis / option labels) describes **product-perspective real situations** only.

### Forbidden in card body (스키마가 차단)

| Forbidden category | Examples | 패턴 |
|--------------------|----------|------|
| Class / method names | `OrderRefundScheduler`, `isNightTime()` | `[A-Z][a-zA-Z]*\.class`, `[A-Z][a-zA-Z]*Entity` |
| Table / column names | `user_lock`, `next_compute_dtm` | `[a-z]+_[a-z]+(?:_[a-z]+)+` |
| File paths / commit SHAs | `overview.md §4`, `59623a8e7` | (수동 검사) |
| Internal acronyms | `BULK`, `AUTO_RULE`, `send_source` | (수동 검사) |
| Requirement / decision IDs | `R3`, `R6`, `#38`, `#A4`, `decision #44` | `#[0-9]+`, `\bR[0-9]{1,2}\b` |
| Stack-specific names | `ShedLock`, `cron`, `@SchedulerLock` | (LANGUAGE GATE) |
| Environment names | `stag`, `prod` | (LANGUAGE GATE) |

`detail-panel`(개발자 근거 영역)은 예외 — 거기엔 클래스명·테이블명을 적어도 됨.

### Background — 3-sentence skeleton

JSON 데이터에서 `background.situation` / `background.pain` / `background.divergence` 세 필드로 분리되어 있다. 각 필드의 의미:

1. **situation** — 제품에서 지금 일어나는 한 장면. 구체적 사용자/관리자 시점.
2. **pain** — 결정 없이 두면 발생하는 비용. **숫자 또는 '놓치/실패/지연' 같은 구체 표현 필수**(스키마 `mustMatch`).
3. **divergence** — 두 선택지에 따라 사용자가 무엇을 다르게 경험하는지.

### Option-label rules

End with **"what becomes different"**, not **"what we do"**.

| Bad (impl jargon) | Good (outcome) |
|-------------------|----------------|
| A. Generalize — `OrderRefundScheduler` handles source-agnostic | A. Both refunded together — auto-send failures recover immediately |
| A. Add upfront — pull in distributed-lock dep | A. Add now — multi-server rollout post-launch processes each request once |
| A. Replace with polling — expiry polling | A. Switch to immediate — admin condition changes apply right away |

### Judgment-question rule

Use a **decision question**, not an "axis". A 1-sentence question the decision-maker must answer (스키마 `endsWith: "?"` 강제). Avoid abstractions like "trade A for B"; use concrete situational questions: "When the admin changes the condition, should it apply right away, or is next-day acceptable?"

### "Other — custom input" option is mandatory

D(Other) 옵션은 `create-document` 의 템플릿이 자동 주입한다. JSON에 적을 필요 없음. A/B/C 만 데이터에 포함하면 된다.

> Worked example: [`references/example-good-card.md`](references/example-good-card.md) — BEFORE / AFTER comparison.
> JSON 예시: [`../create-document/references/example-decision-card.json`](../create-document/references/example-decision-card.json)

---

## Priority colors

| Class | Color | Meaning |
|-------|-------|---------|
| `pip-p0` / `pri-tag-p0` | Red | Blocks startup (decide now) |
| `pip-p1` / `pri-tag-p1` | Yellow | Implementation blocker |
| `pip-p2` / `pri-tag-p2` | Blue | Decidable after build starts |

JSON의 `priority` 필드는 lowercase `p0` / `p1` / `p2` (CSS class에 직접 들어감). 표시 텍스트(`P0 — 착수 차단` 등)는 `label` 필드에 별도.

---

## Mode 1 procedure: `generate`

```bash
# 1. Set variables
ISSUE="${1:-$(git branch --show-current | grep -oE '[A-Z]+-[0-9]+' || echo decision)}"
OUT_DIR="${2:-${DECISIONS_DIR:-claudedocs}}"
DATE=$(date +%Y-%m-%d-%H%M)
TARGET_DIR="${OUT_DIR}/${ISSUE}"
FILE="${TARGET_DIR}/decisions-${DATE}.html"
JSON="${TARGET_DIR}/decisions.json"

mkdir -p "${TARGET_DIR}"
```

다음:

**2. 채팅 맥락에서 결정 후보를 수집해 `${JSON}` 작성** (Write tool)

JSON 구조 — `schemas/decision-dashboard.schema.json` 참고. 한 카드 = 약 20 LOC:

```json
{
  "issue": "PROJ-123",
  "branch": "feat/...",
  "date": "2026-05-22-1430",
  "title": "결정 대시보드",
  "subtitle": "검토 후 A/B/C 선택",
  "priority_groups": [
    {
      "priority": "p0",
      "label": "P0 — 착수 차단",
      "cards": [
        {
          "card_id": "c1",
          "num": 1,
          "open_class": " open",
          "title": "카드 제목 (식별자 금지)",
          "background": {
            "situation": "제품에서 일어나는 한 장면 (20자 이상)",
            "pain": "결정 없이 두면 발생하는 비용 — 숫자/실패/지연 필수",
            "divergence": "두 선택지의 사용자 경험 차이"
          },
          "judgment_question": "한 줄 결정 질문?",
          "options": [
            {"key": "A", "label": "결과 중심 라벨", "rec_badge": "<span class=\"rec-badge\">권고</span>"},
            {"key": "B", "label": "..."},
            {"key": "C", "label": "..."}
          ]
        }
      ]
    }
  ]
}
```

**3. create-document 호출 — 자동 스키마 검증 + HTML 생성**

```bash
CD="${CLAUDE_PLUGIN_ROOT}/skills/create-document"
python3 "${CD}/scripts/render.py" \
  --template decision-dashboard \
  --data "${JSON}" \
  --out "${FILE}"
```

검증 실패 시 stderr에 `필드: 무엇이 잘못` 형식으로 출력되고 HTML은 생성되지 않는다. JSON을 고쳐 재시도.

**4. 4 gates 추가 검증 (template-level 안전망)**

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}"
```

- create-document는 input JSON을 검증한다.
- validate-dashboard.py는 출력된 HTML 자체를 검증한다 (placeholder 누락, nested comment, nav-link 매치, LANGUAGE GATE).
- 두 단계 모두 통과해야 publish.

**5. 브라우저로 열기**

```bash
open "${FILE}"
```

**6. 사용자에게 안내**: "옵션 선택 → JSON/MD 다운로드 → 경로 알려주면 finalize 진행"

> `${CLAUDE_PLUGIN_ROOT}`는 Claude Code가 plugin 설치 경로로 자동 치환한다.

---

## Mode 2 procedure: `finalize`

User finished picking on the dashboard and downloaded the JSON / MD. They say "apply these".

```bash
# 1. Parse args
ISSUE="$1"
USER_JSON="$2"   # 사용자가 다운로드한 export JSON
OUT_DIR="${DECISIONS_DIR:-claudedocs}"
TARGET_DIR="${OUT_DIR}/${ISSUE}"
ORIGINAL_JSON="${TARGET_DIR}/decisions.json"     # generate 단계에서 만들었던 입력 JSON
FINAL_JSON="${TARGET_DIR}/decisions-final.json"
```

**2. Claude가 inline 변환** — 두 JSON을 머지하여 final 작성:

- 사용자 export의 `decisions[]` 를 순회
- 각 항목에 원본 데이터의 `judgment_question`, 권고 옵션, rejected_alternatives 머지
- `summary` 계산 (total, by_priority, other_chosen, recommended_match_rate)

`decisions-final.json` schema:
```json
{
  "issue": "PROJ-123",
  "branch": "feat/...",
  "decided_at": "2026-05-22T05:31:53.970Z",
  "decisions": [
    {
      "card_id": "c1",
      "priority": "P0",
      "title": "...",
      "judgment_question": "...",
      "choice": "A",
      "choice_label": "...",
      "memo": "",
      "recommended_was": "A",
      "rejected_alternatives": [{"key": "B", "label": "..."}, ...]
    }
  ],
  "summary": {
    "total": 5,
    "by_priority": {"P0": 2, "P1": 2, "P2": 1},
    "other_chosen": 0,
    "recommended_match_rate": "4/5"
  }
}
```

**3. Disposable HTML 정리**:
```bash
rm "${TARGET_DIR}"/decisions-*.html
```

`decisions.json` (generate 단계 입력)도 정리하려면 남겨두는 게 안전 — 다음 finalize 호출에서 머지에 필요.

**4. End-of-skill reflection (아래 섹션 참고)**

---

## End-of-skill reflection (Mode 2 close)

**Don't praise. Observe patterns.**

JSON persistence 직후, 사용자에게 다음 형식으로 보고:

```
N decisions persisted. Patterns I noticed:

- 권고 매치율 X/N → 권고가 잘 calibrated 됐거나, 사용자가 시간 압박 받았다. 다음에는 권고 라벨 없이 한 번 비교해볼 가치.
- P0 picks가 모두 "immediacy > load" 방향 → 이 사용자/제품은 즉시성 선호 경향. 다음 결정에서 axis 기본값으로 잡아도 OK.
- Memo 0개 → 옵션이 잘 맞았거나, memo 작성이 부담. D(Other) 선택률 0%면 후자 가능.

Persisted at: {FINAL_JSON_PATH}
HTML cleaned up.
```

3 items, each = 1-sentence observation + 1-sentence hypothesis. Hedge with "may be" / "worth comparing" so guesses don't read as facts.

---

## Forbidden

- ❌ Edit tool로 HTML 카드 블록 작성 — 이제 JSON 만 작성한다.
- ❌ 외부 CDN / 라이브러리 추가 (Google Fonts는 템플릿 내장 예외).
- ❌ create-document/templates/decision-dashboard.html 직접 수정 — 디자인 변경은 별도 PR.
- ❌ Separate review / version files (`decisions-{date}-v2.html`, etc.).
- ❌ Disposable HTML을 finalize 전에 삭제 (사용자가 아직 결정 안 했을 수 있음).
- ❌ Publishing a card with `D (Other)` selected and an empty memo — request memo input first.

---

## Pitfall / Known issues

### Pitfall 1: `${CLAUDE_PLUGIN_ROOT}` vs `${CLAUDE_SKILL_DIR}`

- 자기 스킬의 자산(scripts, references) → `${CLAUDE_SKILL_DIR}`
- 다른 스킬(create-document) 호출 → `${CLAUDE_PLUGIN_ROOT}/skills/create-document`

### Pitfall 2: JSON 작성 시 식별자가 새어들어감

스키마가 차단하지만, 차단 메시지를 무시하지 말 것. 차단되면 카드 텍스트를 product-perspective로 다시 쓰라는 신호다. "약간만 우회"는 금지.

### Pitfall 3: `open_class` 누락으로 모든 카드가 닫힌 채 출력

첫 카드에만 `"open_class": " open"` (공백 + open). 나머지는 빈 문자열 또는 생략.

### Pitfall 4: 권고 옵션의 rec_badge

권고 옵션에만 `"rec_badge": "<span class=\"rec-badge\">권고</span>"`. 다른 옵션은 생략. 모든 옵션에 권고 badge를 달면 의미가 사라짐.

---

## Auto-validation

두 단계.

### Stage 1 — input JSON 검증 (create-document)

`render.py`가 자동 수행. `decision-dashboard.schema.json`에 정의된 모든 규칙(필수 필드, 길이, 패턴, forbid, mustMatch, endsWith) 검사.

### Stage 2 — output HTML 검증 (4 gates)

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}"
```

Chainable JSON output:
```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}" --json
```

Gates:
1. **placeholders** — 0 unresolved `{{...}}`.
2. **nested_comments** — 0 nested HTML comments.
3. **navlink_card_match** — every nav-link `data-id` matches an actual card `id`.
4. **language_gate** — 0 internal-identifier exposure in card body (`info-box`, `card-title`, `.opt`). The `.detail-panel` is exempt.

> 두 단계 검증은 보완 관계. Stage 1은 input JSON을 catch (식별자가 처음부터 못 들어감), Stage 2는 template 자체의 구조적 문제를 catch (placeholder 누락 등).

---

## Supporting files

| File | Role |
|------|------|
| [`scripts/validate-dashboard.py`](scripts/validate-dashboard.py) | Stage 2 — 출력 HTML 4-gate 검증 |
| [`references/example-good-card.md`](references/example-good-card.md) | BEFORE / AFTER card comparison — 규칙 위반 vs 통과 |
| [`references/example-card-snippet.html`](references/example-card-snippet.html) | (legacy) 단일 카드 HTML 조각 — 디자인 reference 용 |
| [`../create-document/templates/decision-dashboard.html`](../create-document/templates/decision-dashboard.html) | 마스터 HTML 템플릿 (FOREACH 블록) |
| [`../create-document/schemas/decision-dashboard.schema.json`](../create-document/schemas/decision-dashboard.schema.json) | Stage 1 — input JSON 스키마 |
| [`../create-document/references/example-decision-card.json`](../create-document/references/example-decision-card.json) | 좋은 JSON 데이터 예시 |

---

## Self-check before publishing

JSON 작성 후 publish 전 검증:

- [ ] Stage 1 (create-document/render.py) 통과 — `✓ schema valid` 메시지
- [ ] Stage 2 (validate-dashboard.py) 4 gates 모두 PASS
- [ ] 결정-maker(PO / team lead)가 모든 카드 본문을 코드/DB 모름 상태에서 이해할 수 있음
- [ ] 모든 카드 background.pain에 구체적 숫자 또는 시나리오가 있음 (스키마 강제)
- [ ] 모든 판단 질문이 즉답 가능한 형태
- [ ] 모든 옵션 라벨이 "what becomes different" 로 끝남
- [ ] 첫 카드만 `open_class: " open"`, 나머지 닫힘
- [ ] Priority(P0/P1/P2) 분류가 합리적
- [ ] (Mode 2) `decisions-final.json` 에 모든 결정 + rejected_alternatives 기록
