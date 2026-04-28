---
name: decision-dashboard
description: When 3+ pending decisions block PO/team progress, capture them in a printable HTML artifact so the team can decide in 5 minutes instead of long Slack threads. Replaces "decision fatigue scattered across messages" with "one page, all options, traceable choice + memo + downloadable JSON for downstream skills".
when_to_use: 3+ decisions pile up in a review (architecture/DDL/UX/consistency), user says "결정 대시보드 만들어줘"·"선택지 정리해줘"·"make decision dashboard", or chat explanations are too long to inline. Skip for 1~2 decisions (ask in chat).
argument-hint: [issue-id] [output-dir?] [mode?]
allowed-tools: Bash(cp *) Bash(sed *) Bash(grep *) Bash(awk *) Bash(diff *) Bash(open *) Bash(date *) Bash(git branch*) Bash(mkdir *) Bash(rm claudedocs/*) Bash(python3 *) Edit Read Write
---

# Decision Dashboard Generator

3개 이상의 결정이 쌓여서 의사결정자(PO/팀장)가 채팅을 끝까지 읽기 어려운 순간, 그 결정들을 **한 장의 인쇄 가능한 HTML 산출물**로 캡처해 5분 안에 A/B/C 를 고를 수 있게 만든다. 결정 결과는 다른 스킬이 소비할 수 있는 JSON 으로 영구 저장된다.

---

## Where this fits in the workflow

```
brainstorm → design → ▶ DECISION-DASHBOARD ◀ → implement → review → ship
                          (artifact-forcing
                           moment for taste)
```

- **선행 스킬** (brainstorm/design/review) 이 결정 사안을 표면화한다.
- **이 스킬** 이 그 결정들을 인쇄 가능한 HTML 로 만들고, JSON 으로 영구화한다.
- **후행 스킬** (implement/ship) 이 `decisions/{ISSUE}-final.json` 을 읽어 "무엇을, 왜 그렇게 결정했나" 컨텍스트로 사용한다.

---

## What's automated vs what needs your taste

(gstack 의 "What can the model safely decide alone, and what needs human taste?" 원칙 적용)

| Claude 가 자동으로 결정 | 사용자가 결정 |
|--------------------------|-------------|
| 카드 번호 (c1, c2, …) | 각 카드의 옵션 선택 (A/B/C/D) |
| P0/P1/P2 우선순위 분류 | 옵션 자체의 정의가 맞는지 |
| 옵션 라벨 변환 (구현 용어 → 결과 용어) | "기타 (직접 입력)" 사용 시점 |
| LANGUAGE GATE 검사 (내부 식별자 차단) | 결정 보류 / 다음 세션으로 미룸 |
| 카드 본문의 배경 3문장 골격 적용 | 선택지가 부적합할 때 새 옵션 제안 |

자동 부분이 잘못되면 사용자가 메모로 교정. 메모가 빈 상태로 D(기타) 선택 시 발행 차단.

---

## Modes

이 스킬은 2개의 명시적 모드를 지원한다. 첫 인자가 모드 키워드면 그 모드, 아니면 `generate` 기본.

### Mode 1: `generate` (기본)

3+ 결정 사안을 카드로 만들고 HTML 대시보드를 생성한다.

**언제**: 결정 사안 첫 캡처. 새 이슈에 대한 결정이 쌓였을 때.

**산출물**: `{OUT_DIR}/{ISSUE}/decisions-{DATE}.html`

### Mode 2: `finalize`

JSON/MD 결과를 받아 결정을 영구화하고 일회용 HTML 을 정리한다.

**언제**: 사용자가 대시보드에서 선택을 마치고 "이거 반영해줘" 라고 했을 때.

**산출물**:
- `{OUT_DIR}/{ISSUE}/decisions-final.json` — **영구 보존**. 후행 스킬이 소비
- `{OUT_DIR}/{ISSUE}/decisions-{DATE}.html` — **삭제** (일회용 UI 레이어)

---

## Auto-invoke vs explicit

**Auto-invoke**:
- 3+ 결정 사안이 사용자 확인을 기다림
- 한 결정의 설명이 채팅에 인라인으로 읽기엔 너무 김
- 리뷰 결과(consistency / architecture / DDL / UX) 에서 여러 결정 사안이 노출됨

**Explicit invocation**:
- `/decision-dashboard:decision-dashboard`
- "결정 대시보드 만들어줘", "선택지 정리해줘"

**Do NOT invoke when**:
- 1~2개 결정 → 채팅에서 직접 묻기 (AskUserQuestion 또는 짧은 Markdown)
- 단순 yes/no 확인 → 그냥 묻기
- 구현 제안에 대한 단방향 선택 → 짧은 답변

---

## Output location

기본 경로:
```
{output-dir}/{ISSUE_ID}/decisions-{YYYY-MM-DD-HHmm}.html
```

이슈 ID 가 없으면:
```
{output-dir}/decisions/{descriptive-name}-{YYYY-MM-DD-HHmm}.html
```

`{output-dir}` 우선순위:
1. `$ARGUMENTS` 두 번째 인자 (명시적 override)
2. 환경변수 `DECISIONS_DIR`
3. `claudedocs` (기본)

파일명에 시분(HHmm) 을 포함해 같은 이슈에서 하루 여러 번 생성할 때 충돌 방지.

---

## Standing rules — 카드 본문 작성

(이 섹션의 규칙은 모든 카드에 항상 적용. 절차가 아니라 standing instructions.)

결정 문서는 **대화가 아니다**. 결정자(PO/팀장/미래의 나) 는 코드를 안 본다. 5분 안에 A/B 중 하나를 골라야 한다. 따라서 카드 본문(title / background / judgment axis / option labels) 은 **제품 관점의 실제 상황** 만 서술한다.

### 금지 (카드 본문에 쓰면 안 되는 것)

| 금지 범주 | 예시 |
|-----------|------|
| 클래스명/메소드명 | `OrderRefundScheduler`, `isNightTime()`, `UserCampaignTagSendScheduler` |
| DB 테이블명/컬럼명 | `user_lock`, `next_compute_dtm`, `send_dtm` |
| 파일 경로/커밋 해시 | `overview.md §4`, `architecture.html §04-2`, `59623a8e7` |
| 프로젝트 내부 약어 | `BULK`, `AUTO_RULE`, `send_source`, `FILTER_CRITERIA` |
| 요구사항/결정 번호 | `R3`, `R6`, `#38`, `#A4`, `결정 #44` |
| 기술 스택 고유명 | `ShedLock`, `cron`, `@SchedulerLock`, `polling`, `@Scheduled` |
| 환경명 | `stag`, `prod`, `PR` (풀어서 "운영 배포 전") |

> 위 예시 토큰은 일반 패턴. 본인 프로젝트의 클래스명/스택을 같은 기준으로 카드 본문에서 배제.

위 금지 토큰은 **접이식 상세 패널**(`detail-trigger` + `detail-panel`) 내부에서만 허용. 개발자 검증용 근거 영역.

### 배경 3문장 골격

1. **지금 제품에서 무엇이 일어나는가** — 사용자/관리자 시점의 구체 장면 1개.
2. **결정하지 않으면 어떤 고통이 발생하는가** — 구체 숫자 1개 또는 시나리오 1개. ("결제 금액이 9,800 대신 9,750만 차감")
3. **두 선택지의 결과가 어떻게 다른가** — 사용자 체감 차이.

### 옵션 라벨 규칙

**"무엇을 한다"** 가 아니라 **"무엇이 달라진다"** 로 끝낸다.

| 나쁨 (구현 용어) | 좋음 (결과) |
|------|------|
| A. 일반화 — `OrderRefundScheduler` 로 source 무관 처리 | A. 한 번에 둘 다 환급되게 만든다 — 자동 발송 실패 건도 바로 복구 |
| A. 선행 도입 — 분산락 의존성 추가 | A. 이번에 같이 도입 — 출시 직후 서버 여러 대 띄워도 중복 처리 없음 |
| A. 폴링으로 교체 — 만기 폴링 | A. 즉시 반영으로 바꾼다 — 관리자가 조건 수정하면 바로 반영 |

### 판단 질문 규칙

"축" 대신 **"결정 질문"**. 결정자가 답해야 할 1문장 질문. "X 를 확보할 것인가, Y 를 수용할 것인가" 같은 추상어 금지 — "관리자가 조건을 바꿨을 때 즉시 반영돼야 할까요, 다음날 반영돼도 괜찮을까요?" 처럼 구체적 상황 질문.

### "기타 — 직접 입력" 옵션 필수

모든 카드의 마지막 옵션은 항상 `D. 기타 — 아래 메모에 직접 입력`. 메모에 자유 텍스트 가능.

> 완성 카드 예시 1개: [`references/example-good-card.md`](references/example-good-card.md) — BEFORE/AFTER 비교
> HTML 스니펫: [`references/example-card-snippet.html`](references/example-card-snippet.html) — 그대로 복사 가능

---

## Priority colors

| Class | Color | Meaning |
|-------|-------|---------|
| `pip-p0` / `pri-tag-p0` | Red | 착수 차단 (지금 결정) |
| `pip-p1` / `pri-tag-p1` | Yellow | 구현 중 블로커 |
| `pip-p2` / `pri-tag-p2` | Blue | 착수 후 결정 가능 |

카드 번호 (cN) 는 모든 우선순위에 걸쳐 단일 시퀀스. `data-key` / `id` / `data-group` / `data-memo` 가 모두 일치해야 한다.

---

## Mode 1 procedure: `generate`

```bash
# 1. 변수 설정
ISSUE="${1:-$(git branch --show-current | grep -oE '[A-Z]+-[0-9]+' || echo decision)}"
OUT_DIR="${2:-${DECISIONS_DIR:-claudedocs}}"
DATE=$(date +%Y-%m-%d-%H%M)
TARGET_DIR="${OUT_DIR}/${ISSUE}"
FILE="${TARGET_DIR}/decisions-${DATE}.html"

# 2. 출력 디렉토리 + 템플릿 복사
mkdir -p "${TARGET_DIR}"
cp "${CLAUDE_SKILL_DIR}/template.html" "${FILE}"

# 3. 단순 placeholder 치환
BRANCH=$(git branch --show-current 2>/dev/null || echo main)
sed -i '' \
  -e "s|{{ISSUE_ID}}|${ISSUE}|g" \
  -e "s|{{BRANCH}}|${BRANCH}|g" \
  -e "s|{{DATE}}|${DATE}|g" \
  -e "s|{{DASHBOARD_TITLE}}|결정 대시보드|g" \
  -e "s|{{DASHBOARD_SUBTITLE}}|아래 사안들을 검토하고 선택해주세요|g" \
  "${FILE}"
```

이후:
4. 결정 항목 정리 (대화 컨텍스트 또는 결정 노트로부터)
5. 각 항목을 P0 / P1 / P2 로 분류
6. `{{NAV_GROUPS}}` / `{{DECISION_SECTIONS}}` 는 큰 구조 — **Edit 툴**로 치환 (sed 는 줄바꿈 처리 약함). 카드 작성 시 `references/example-card-snippet.html` 참조
7. **검증**: `python3 "${CLAUDE_SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}"` — 4개 게이트 모두 통과해야 발행
8. 브라우저 열기: `open "${FILE}"`
9. 사용자에게 안내: "브라우저에서 선택 → JSON/MD 다운로드 → 경로를 알려주시면 finalize 모드로 진행"

> `${CLAUDE_SKILL_DIR}` 은 Claude Code 가 스킬 설치 경로로 자동 치환. cache 디렉토리에 복사되므로 절대 경로 하드코딩 금지.

---

## Mode 2 procedure: `finalize`

사용자가 대시보드에서 결정 후 JSON/MD 다운로드. "이거 반영해줘" 시작.

```bash
# 1. 인자 파싱: <ISSUE> <user-downloaded-json-path>
ISSUE="$1"
USER_JSON="$2"
OUT_DIR="${DECISIONS_DIR:-claudedocs}"
TARGET_DIR="${OUT_DIR}/${ISSUE}"
FINAL_JSON="${TARGET_DIR}/decisions-final.json"

# 2. 사용자 JSON 을 영구 저장소로 복사 + 메타 추가
python3 "${CLAUDE_SKILL_DIR}/scripts/finalize.py" \
  --input "${USER_JSON}" \
  --output "${FINAL_JSON}" \
  --issue "${ISSUE}"

# (현재 finalize.py 미포함 — Claude 가 직접 JSON 변환:
#  사용자 JSON 의 각 카드에 {decided_at, source: dashboard} 메타 추가하여 FINAL_JSON 에 저장)

# 3. 일회용 HTML 정리
rm "${TARGET_DIR}"/decisions-*.html

# 4. 사용자에게 보고 (다음 섹션 "End-of-skill reflection" 참조)
```

`decisions-final.json` 스키마:
```json
{
  "issue": "PROJ-123",
  "decided_at": "2026-04-28T10:30:00+09:00",
  "decisions": [
    {
      "card_id": "c1",
      "title": "...",
      "priority": "P0",
      "choice": "A",
      "choice_label": "...",
      "memo": "",
      "rejected_alternatives": [
        {"key": "B", "label": "..."},
        {"key": "C", "label": "..."}
      ],
      "judgment_question": "..."
    }
  ],
  "summary": {
    "total": 5,
    "by_priority": {"P0": 2, "P1": 2, "P2": 1},
    "other_chosen": 0
  }
}
```

후행 스킬(`/implement`, `/ship` 등) 이 이 JSON 을 읽어 "무엇이 결정됐고 왜 그랬는지" 컨텍스트로 사용.

---

## End-of-skill reflection (Mode 2 종료 시)

**칭찬하지 말 것. 패턴을 관찰할 것.**
(gstack 의 *"After /office-hours, the model reflects on what it noticed about how you think — not generic praise, but specific callbacks"* 원칙)

JSON 영구화 직후, 사용자에게 다음 형식으로 보고:

```
결정 5건 반영 완료. 패턴 관찰:

- 5건 중 4건에서 "권고 옵션" 선택 → 권고 옵션의 신뢰도가 높거나, 사용자가 검토 시간이 부족했을 수 있음.
  다음 세션에서 권고 표시 없이 carded 한 후 같은 비율인지 비교해 볼 만함.
- P0 결정 2건이 모두 "즉시성 > 부하" 방향 → 사용자/제품이 latency 보다 immediacy 를 우선시하는 경향.
  같은 축의 다음 결정에서 디폴트로 가정 가능.
- 메모 입력 0건 → 제시된 옵션이 모두 적합했거나, 사용자가 메모 작성 부담을 느꼈을 수 있음.
  옵션 D(기타) 선택률이 0이면 후자일 가능성.

영구 저장: {FINAL_JSON_PATH}
HTML 정리됨.
```

3개 항목, 각 1문장 관찰 + 1문장 가설/제안. 추측이 사실로 표현되지 않게 "~일 수 있음" / "비교해 볼 만함" 같은 hedge 사용.

---

## Forbidden

- 외부 CDN / 라이브러리 추가 금지 (Google Fonts 는 template 에 이미 포함, 예외)
- 단일 HTML 외 별도 산출물 금지 — 단, finalize 모드의 `decisions-final.json` 은 예외 (영구 저장 의도)
- template CSS 변수 수정 금지 (시각 일관성)
- 별도 review/version 파일 금지 (`decisions-{date}-v2.html` 같은 것)
- **중첩 HTML 주석 금지** (`<!-- ... <!-- ... --> ... -->`). 첫 `-->` 가 외부 주석을 닫아 이후 코드 노출. 인라인 주석은 괄호 평문으로
- finalize 전 HTML 삭제 금지 (사용자 결정 안 끝났을 가능성)
- 메모 빈 상태로 D(기타) 선택된 카드 발행 금지 — 사용자에게 메모 입력 요청

---

## Known pitfalls (regression prevention)

### Pitfall 1: Nested HTML comment leak

**Symptom**: 주석으로 가린 예시 카드/HTML 이 본문 영역 상단에 노출.

**Cause**: `<!-- DECISION_SECTIONS:START guide -->` 같은 외부 주석 안에 `<!-- recommended only -->` 내부 주석을 넣으면 첫 `-->` 에서 외부 주석이 종료.

**Prevention**: template body 의 모든 중첩 `<!-- -->` 제거. 새 카드 추가 시 인라인 노트는 평문만.

### Pitfall 2: Awkward scroll to collapsed cards

**Symptom**: 사이드바 링크 클릭 시 작은 헤드만 뷰포트 상단 살짝 아래에 표시.

**Cause**: 카드 body 가 `max-height:0` 으로 접혀 있어 기본 `<a href="#cN">` 앵커가 헤드 상단으로 스크롤.

**Prevention**: template JS 가 nav-link 클릭 시 카드 자동 펼침 + 부드러운 스크롤(`scrollTo({top: rect.top - 24})`) 처리. 새 nav-link 추가 시 `data-id="cN"` 매칭 정확히 확인.

### Pitfall 3: `${CLAUDE_PLUGIN_ROOT}` vs `${CLAUDE_SKILL_DIR}` 혼동

**Symptom**: `cp ${CLAUDE_PLUGIN_ROOT}/skills/decision-dashboard/template.html ...` 처럼 PLUGIN_ROOT 를 쓰면 cache 경로에서 실패할 수 있음.

**Cause**: 플러그인 SKILL.md 안에서 같은 스킬의 자산을 참조할 때는 `CLAUDE_SKILL_DIR` 이 안전한 변수.

**Prevention**: 항상 `${CLAUDE_SKILL_DIR}/template.html`, `${CLAUDE_SKILL_DIR}/scripts/...`, `${CLAUDE_SKILL_DIR}/references/...` 사용.

---

## Auto-validation

생성한 HTML 의 4개 게이트를 검증한다. 게이트 실패 시 발행 차단.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}"
```

JSON 출력으로 다른 스킬과 chaining 가능:
```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}" --json
```

게이트:
1. **placeholders** — 미해결 `{{...}}` 0개
2. **nested_comments** — 중첩 HTML 주석 0개
3. **navlink_card_match** — 모든 nav-link 의 `data-id` 가 실제 카드 `id` 와 일치
4. **language_gate** — 카드 본문(`info-box`, `card-title`, `.opt`) 에 내부 식별자 노출 0건. `.detail-panel` 내부는 제외 (개발자 근거 영역)

> LANGUAGE GATE 의 패턴 리스트는 `scripts/validate-dashboard.py` 의 `LANGUAGE_GATE_PATTERNS` 에서 직접 편집 가능. 본인 프로젝트의 사내 약어/프레임워크 어노테이션을 추가하라.

---

## Supporting files

| 파일 | 용도 |
|------|------|
| [`template.html`](template.html) | 마스터 HTML 템플릿. `{{...}}` placeholder 포함. 그대로 복사 후 치환 |
| [`scripts/validate-dashboard.py`](scripts/validate-dashboard.py) | 4-gate 검증. `--json` 으로 chaining 가능. stdlib only |
| [`references/example-good-card.md`](references/example-good-card.md) | BEFORE/AFTER 카드 비교 — 자체 규칙 위반 vs 통과 |
| [`references/example-card-snippet.html`](references/example-card-snippet.html) | 좋은 카드 1개 HTML fragment — `{{DECISION_SECTIONS}}` 영역에 그대로 삽입 가능 |

---

## Self-check before publishing (사람용)

발행 전 다음 8개 항목 모두 ✓ 확인:

- [ ] `validate-dashboard.py` 4-gate 모두 PASS
- [ ] 결정자(PO/팀장) 가 코드/DB 를 안 보고 모든 카드 본문 이해 가능
- [ ] 각 카드 배경에 구체 숫자 또는 시나리오 1개 이상
- [ ] 각 카드 판단 질문에 결정자가 즉답 가능한 형식
- [ ] 모든 옵션 라벨이 "무엇이 달라진다" 로 끝남
- [ ] 모든 카드 마지막에 "기타 — 직접 입력" 옵션 존재
- [ ] 우선순위(P0/P1/P2) 분류가 합리적
- [ ] (Mode 2) `decisions-final.json` 에 모든 결정과 거부된 대안이 기록됨
