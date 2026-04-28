---
name: decision-dashboard
description: Generate an interactive HTML decision dashboard when multiple issues need to be reviewed and decided at once. Radio selections + memos + MD/JSON download + JSON clipboard copy. Runs standalone via file://.
when_to_use: 3+ pending decisions, review results (architecture/DDL/UX/consistency) requiring multiple choices, user says "결정 대시보드 만들어줘", "선택지 정리해줘", "make decision dashboard"
argument-hint: [issue-id]
allowed-tools: Bash(cp *) Bash(sed *) Bash(grep *) Bash(awk *) Bash(diff *) Bash(open *) Bash(date *) Bash(git branch*) Bash(mkdir *) Bash(rm *) Bash(python3 *) Edit Read
---

# Decision Dashboard Generator

여러 사안을 한 번에 결정해야 할 때, 라디오 선택 + 메모 + 다운로드를 지원하는 단일 HTML 결정 대시보드를 생성한다. 외부 의존 없이 `file://`로 실행된다.

## When to invoke

**Auto-invoke** (사용자 명시 요청 없이):
- 3+ 결정 사안이 사용자 확인을 기다림
- 한 결정의 설명이 채팅에 인라인으로 읽기엔 너무 김
- 리뷰 결과(consistency / architecture / DDL / UX)에서 여러 결정 사안이 노출됨

**Explicit invocation**:
- `/decision-dashboard:decision-dashboard`, "결정 대시보드 만들어줘", "선택지 정리해줘"

**Do NOT invoke when**:
- 1~2개 결정 → 채팅으로 직접 물어보기 (AskUserQuestion 또는 짧은 Markdown)
- 단순 yes/no 확인 → 그냥 묻기
- 구현 제안에 대한 단방향 선택 → 짧은 답변

## Output location

기본 경로:
```
claudedocs/{ISSUE_ID}/decisions-{YYYY-MM-DD-HHmm}.html
```

이슈 ID 가 없으면:
```
claudedocs/decisions/{descriptive-name}-{YYYY-MM-DD-HHmm}.html
```

파일명에 시분(HHmm)을 포함해 같은 이슈에서 하루 여러 번 생성할 때 이름 충돌을 방지한다.

**경로 커스터마이즈**: 프로젝트가 `claudedocs/` 컨벤션을 쓰지 않으면 `$ARGUMENTS` 두 번째 인자로 전체 경로를 넘기거나, 환경변수 `DECISIONS_DIR` 로 베이스 디렉토리를 바꿀 수 있다.

## Template

`template.html` — 완성본. 아래 placeholder 만 치환하면 그대로 동작한다.

| Placeholder | Content |
|-------------|---------|
| `{{ISSUE_ID}}` | 예: `PROJ-123` — JS export 파일명에도 동일 사용 |
| `{{BRANCH}}` | 현재 브랜치 (`git branch --show-current`) |
| `{{DATE}}` | `YYYY-MM-DD-HHmm` — 파일명 충돌 방지 시분 포함 (예: `2026-04-16-1430`) |
| `{{DASHBOARD_TITLE}}` | 예: `결정 대시보드` (짧게, 팀 언어로) |
| `{{DASHBOARD_SUBTITLE}}` | 한 문장 인트로 (팀 언어) |
| `{{NAV_GROUPS}}` | 사이드바. 우선순위별 `<div class="nav-group">` 블록 (template 주석 참조) |
| `{{DECISION_SECTIONS}}` | 본문. 우선순위별 `<section class="pri-section">` 블록 (template 주석 참조) |

**Note**: 카드 본문(제목/배경/옵션/메모)은 결정자가 읽는 영역이다. **팀 언어로 작성한다**.

## Card design principles

각 결정 카드는 다음을 포함한다:

1. **Background** (`info-box box-context`) — 왜 지금 결정해야 하는가. 결정하지 않을 때의 비용.
2. **Judgment axis** (`info-box box-judge`) — 한 문장 판단 기준.
3. **(Optional) Comparison table** (`detail-trigger` + `detail-panel` + `table.cmp`) — 2×2 이상일 때만.
4. **Options** (`.opt-list`) — 각 `button.opt` 는 `A/B/C` + 한 줄 요약. 권고는 `.rec-badge` 표시.
5. **"기타 (자유 입력)" 옵션 필수** — 마지막 버튼은 항상 `직접 입력`. 제시된 옵션이 맞지 않을 때 메모에 자유 기입. 예: `<span><span class="key">D.</span> 기타 — 아래 메모에 직접 입력</span>`
6. **Memo textarea** — 자유 텍스트 ("기타" 선택 시 필수, 그 외 선택).

**감정적으로 어려운 결정은 배경의 고통(왜)을 구체화한다.** 사용자가 5분 안에 결정할 수 있어야 한다.

## 언어 규칙 (HARD RULE)

결정 문서는 **대화가 아니다**. 결정자(PO/팀장/미래의 나)는 코드를 안 본다. 5분 안에 A/B 중 하나를 골라야 한다. 따라서 카드 본문(title / background / judgment axis / option labels)은 **제품 관점의 실제 상황** 만 서술한다.

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

> 위 예시 토큰은 일반적인 패턴 예시. 본인 프로젝트의 클래스명/스택을 같은 기준으로 카드 본문에서 배제한다.

### 허용 위치

위 금지 토큰은 **접이식 상세 패널**(`detail-trigger` + `detail-panel`) 내부에서만 허용. 개발자 검증용 근거 영역. 결정자는 펼치지 않아도 되고, 개발자는 펼쳐서 클래스/DDL 출처 확인.

### 배경 서술 골격 (3문장)

1. **지금 제품에서 무엇이 일어나는가** — 사용자/관리자 시점의 구체 장면 1개.
2. **결정하지 않으면 어떤 고통이 발생하는가** — 구체적 숫자 1개 또는 시나리오 1개. ("결제 금액이 9,800 대신 9,750만 차감" 같은 식.)
3. **두 선택지의 결과가 어떻게 다른가** — 사용자 체감 차이.

### 옵션 라벨 규칙

**"무엇을 한다"** 가 아니라 **"무엇이 달라진다"** 로 끝낸다.

| 나쁨 (구현 용어) | 좋음 (결과) |
|------|------|
| A. 일반화 — `OrderRefundScheduler` 로 source 무관 처리 | A. 한 번에 둘 다 환급되게 만든다 — 자동 발송 실패 건도 바로 복구 |
| A. 선행 도입 — 분산락 의존성 추가 | A. 이번에 같이 도입 — 출시 직후 서버 여러 대 띄워도 중복 처리 없음 |
| A. 폴링으로 교체 — 만기 폴링 | A. 즉시 반영으로 바꾼다 — 관리자가 조건 수정하면 바로 반영 |

### 판단 질문 규칙

"축" 이라는 단어 대신 **"결정 질문"** 으로 쓴다. 결정자가 답해야 할 질문 1문장. "X 를 확보할 것인가, Y 를 수용할 것인가" 같은 추상어 금지 — "관리자가 조건을 바꿨을 때 즉시 반영돼야 할까요, 다음날 반영돼도 괜찮을까요?" 처럼 구체적 상황 질문.

## Priority color rules

| Class | Color | Meaning |
|-------|-------|---------|
| `pip-p0` / `pri-tag-p0` | Red | 착수 차단 (지금 결정) |
| `pip-p1` / `pri-tag-p1` | Yellow | 구현 중 블로커 |
| `pip-p2` / `pri-tag-p2` | Blue | 착수 후 결정 가능 |

카드 번호(cN)는 모든 우선순위에 걸쳐 단일 시퀀스. `data-key` / `id` / `data-group` / `data-memo` 가 모두 일치해야 한다.

## Generation procedure

```bash
# 1. 변수 설정 — 실제 셸 변수 사용
ISSUE="${1:-$(git branch --show-current | grep -oE '[A-Z]+-[0-9]+' || echo decision)}"
DATE=$(date +%Y-%m-%d-%H%M)
OUT_DIR="${DECISIONS_DIR:-claudedocs}/${ISSUE}"
FILE="${OUT_DIR}/decisions-${DATE}.html"

# 2. 출력 디렉토리 생성 + 템플릿 복사
mkdir -p "${OUT_DIR}"
cp "${CLAUDE_PLUGIN_ROOT}/skills/decision-dashboard/template.html" "${FILE}"

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
4. 대화 컨텍스트나 결정 노트로부터 결정 항목 정리.
5. 각 항목을 P0 / P1 / P2 로 분류.
6. `{{NAV_GROUPS}}` / `{{DECISION_SECTIONS}}` 는 큰 구조이므로 **Edit 툴**로 치환 (sed 가 줄바꿈 처리에 약함).
7. **검증 후 브라우저 열기**: `grep -n "{{" "${FILE}"` 결과 0줄 + `open "${FILE}"`.
8. 사용자가 선택 → JSON / MD 다운로드 → "이거 반영해줘" → 후속 작업 진행.
9. 반영 완료 직후 대시보드 HTML 삭제 (아래 "Cleanup" 참조).

> **`${CLAUDE_PLUGIN_ROOT}`** 는 Claude Code 가 플러그인 설치 경로로 자동 치환하는 환경변수. 플러그인은 cache 디렉토리에 복사되므로 절대 경로 하드코딩 금지.

## Post-generation behavior

대시보드를 연 직후 사용자에게 (한국어):
- "브라우저에서 선택 → 우측 하단 버튼으로 MD/JSON 다운로드 → 다운로드 경로를 알려주시면 그에 맞춰 후속 작업(설계 문서 / 커밋)을 진행하겠습니다"
- 사용자가 JSON 경로를 주면 읽어서 결정을 후속 작업에 적용.
- 적용 후 대시보드 HTML 삭제.

## Cleanup after decision (HARD RULE)

결정 응답(JSON / MD)을 받아 후속 작업에 반영을 **마친 직후**, 생성한 대시보드 HTML 을 반드시 삭제한다. 대시보드는 일회성 의사결정 도구이며, 결정이 완료된 순간부터는 최신 상태가 아니다. 오래된 대시보드가 저장소에 쌓이면 다음에 사람이 열었을 때 이미 반영된 과거 결정을 현재 결정으로 오인한다.

### When to delete

다음 조건이 모두 충족된 순간:
1. 사용자로부터 JSON/MD 결과 또는 "반영해줘" 지시를 받음
2. 해당 결정을 설계 문서 / 커밋 메시지 / 후속 작업에 실제로 반영 완료
3. 사용자에게 반영 결과를 보고 완료

### How to delete

```bash
rm "${FILE}"
```

다운로드된 JSON/MD 파일은 사용자 소유물이므로 임의 삭제 금지. 필요 없는지 사용자에게 확인 후 안내만.

### What to keep

- 결정 근거를 담은 **커밋 메시지** (영구 보존, git log 로 회고 가능)
- 변경된 **설계 / 코드** 자체

회고 시 "왜 B 가 아니라 A 를 골랐나" 추적이 필요하면 커밋 메시지에 한 줄 남기는 것을 권장:
```
[scope][TICKET] feat: ... (decision: A 채택, 사유 — ...)
```

### 예외 (삭제하지 않는 경우)

- 사용자가 "대시보드 남겨둬" / "아직 결정 안 끝났어" 라고 명시
- 일부 카드만 결정되고 나머지는 pending — 파일 유지, 다음 세션에서 계속 사용
- 반영에 실패/보류하여 재검토가 필요함

## Minimal example

2개 결정: 1 P0 + 1 P1.

```html
<!-- {{NAV_GROUPS}} -->
<div class="nav-group">
  <div class="nav-group-label">P0 착수 차단</div>
  <a class="nav-link" href="#c1" data-id="c1">
    <span class="pip pip-p0">1</span><span>사안 A 짧은라벨</span>
    <span class="check-indicator" id="ci-c1"></span>
  </a>
</div>
<div class="nav-group">
  <div class="nav-group-label">P1 블로커</div>
  <a class="nav-link" href="#c2" data-id="c2">
    <span class="pip pip-p1">2</span><span>사안 B 짧은라벨</span>
    <span class="check-indicator" id="ci-c2"></span>
  </a>
</div>

<!-- {{DECISION_SECTIONS}} -->
<section class="pri-section">
  <div class="pri-header"><span class="pri-tag pri-tag-p0">P0 — 착수 차단</span><span class="pri-line"></span></div>
  <div class="card open" id="c1" data-key="c1">
    <div class="card-head" onclick="toggleCard(this)">
      <span class="card-num">1</span>
      <div class="card-head-text"><div class="card-title">사안 A 전체 제목</div></div>
      <span class="card-chevron">▶</span>
    </div>
    <div class="card-body"><div class="card-inner">
      <div class="info-block"><div class="info-label">배경</div>
        <div class="info-box box-context">왜 지금? 방치 비용?</div></div>
      <div class="info-block"><div class="info-label">판단 축</div>
        <div class="info-box box-judge">X 가 중요한가 Y 가 중요한가?</div></div>
      <div class="choices">
        <div class="choices-label"><span class="req-dot"></span> 결정</div>
        <div class="opt-list" data-group="c1">
          <button class="opt" data-val="A" onclick="pick(this)">
            <span class="circle"></span>
            <span><span class="key">A.</span> 선택지 요약.</span>
            <span class="rec-badge">권고</span>
          </button>
          <button class="opt" data-val="B" onclick="pick(this)">
            <span class="circle"></span>
            <span><span class="key">B.</span> 대안.</span>
          </button>
        </div>
        <div class="memo"><textarea placeholder="메모 (선택)" data-memo="c1"></textarea></div>
      </div>
    </div></div>
  </div>
</section>
<section class="pri-section">
  <div class="pri-header"><span class="pri-tag pri-tag-p1">P1 — 블로커</span><span class="pri-line"></span></div>
  (c2 카드 ...)
</section>
```

## Forbidden

- 외부 CDN / 라이브러리 추가 금지 (Google Fonts 는 template 에 이미 포함, 예외)
- 단일 HTML 외 별도 산출물 금지 (분리된 js/css 파일 금지)
- template CSS 변수 수정 금지 (시각 일관성)
- 별도 review/version 파일 금지 (`decisions-{date}-v2.html` 같은 것)
- **중첩 HTML 주석 금지** (`<!-- ... <!-- ... --> ... -->`). HTML 스펙상 첫 `-->` 가 외부 주석을 닫아 이후 코드가 노출됨. 인라인 주석은 괄호 평문으로.

## Known pitfalls (regression prevention)

과거 버그 — 새 카드/주석 추가 시 재확인.

### Pitfall 1: Nested HTML comment leak

**Symptom**: 주석으로 가린 예시 카드/HTML 이 본문 영역 상단에 노출됨.

**Cause**: `<!-- DECISION_SECTIONS:START guide -->` 같은 외부 주석 안에 `<!-- recommended only -->` 내부 주석을 넣으면 첫 `-->` 에서 외부 주석이 종료됨.

**Prevention**: template body 의 모든 중첩 `<!-- -->` 제거. 새 카드 추가 시 인라인 노트는 평문만.

### Pitfall 2: Awkward scroll to collapsed cards

**Symptom**: 사이드바 링크 클릭 시 작은 헤드만 뷰포트 상단 살짝 아래에 표시됨. 사용자가 다시 클릭해야 펼쳐짐.

**Cause**: 카드 body 가 `max-height:0` 으로 접혀 있어 기본 `<a href="#cN">` 앵커가 헤드 상단으로 스크롤됨.

**Prevention**: template JS 가 nav-link 클릭 시 카드 자동 펼침 + 부드러운 스크롤(`scrollTo({top: rect.top - 24})`) 처리. 새 nav-link 추가 시 `data-id="cN"` 매칭 정확히 확인.

## Auto-validation checklist (after generation)

```bash
FILE="${1:?usage: validate.sh <html-file>}"

# 1. 미해결 placeholder 0 개
grep -n "{{" "$FILE"

# 2. 중첩 주석 0 개
awk '/<!--.*<!--/' "$FILE"

# 3. 모든 nav-link 의 data-id 가 실제 카드 id 와 매칭
diff <(grep -oE 'data-id="c[0-9]+"' "$FILE" | grep -oE 'c[0-9]+' | sort -u) \
     <(grep -oE ' id="c[0-9]+"' "$FILE" | grep -oE 'c[0-9]+' | sort -u)

# 4. LANGUAGE GATE — 카드 본문(info-box, card-title, .opt 내부)에 내부 식별자 노출 금지
#    detail-panel 내부는 제외 (개발자 근거 영역으로 허용)
python3 - "$FILE" <<'PYEOF'
import re, sys
path = sys.argv[1]
html = open(path, encoding='utf-8').read()
# detail-panel 제거
html_stripped = re.sub(r'<div class="detail-panel[^"]*"[^>]*>.*?</div>\s*</div>', '', html, flags=re.DOTALL)
# 카드 본문만 추출 (info-box, card-title, opt 내부)
scopes = re.findall(r'<div class="info-box[^"]*"[^>]*>(.*?)</div>', html_stripped, re.DOTALL)
scopes += re.findall(r'<div class="card-title"[^>]*>(.*?)</div>', html_stripped, re.DOTALL)
scopes += re.findall(r'<button class="opt"[^>]*>(.*?)</button>', html_stripped, re.DOTALL)
body = '\n'.join(scopes)

patterns = {
    'ClassName (Camel 3+)': r'\b[A-Z][a-z]+(?:[A-Z][a-z]+){2,}\b',
    'snake_case_table': r'\b[a-z]+_[a-z]+(?:_[a-z]+)+\b',
    '내부 결정번호': r'(?:결정\s*)?#[A-Z]?[0-9]{2,}',
    '요구사항 번호': r'\bR[0-9]{1,2}\b',
    '기술 스택': r'\b(?:ShedLock|cron|@\w+|polling|@Scheduled)\b',
    '환경명': r'\b(?:stag|prod)\b',
}
hits = []
for name, pat in patterns.items():
    for m in re.finditer(pat, body):
        hits.append(f"[{name}] {m.group()}")
if hits:
    print("LANGUAGE GATE FAILED — 카드 본문에 내부 식별자 노출:")
    for h in sorted(set(hits)): print("  " + h)
    sys.exit(1)
print("language gate pass")
PYEOF
```

1~3 빈 출력 + 4 exit 0 이어야 통과.

> 위 LANGUAGE GATE 의 패턴 리스트는 일반적인 예시. 본인 프로젝트에 맞게 추가/조정 가능 (예: 사내 약어, 프레임워크 어노테이션).
