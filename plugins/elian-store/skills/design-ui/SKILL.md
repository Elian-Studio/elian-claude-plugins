---
name: design-ui
description: When a user needs to design a UI/UX from scratch — drives Interview → Reference → Wireframe → (Gate) → Visual → Deliver in one skill. Phase 1 is an iterative interview until the problem brief is signed off; Phase 2 collects 2~3 competitor/reference patterns; Phase 3 produces a grayscale wireframe where every section carries an "UX intent" annotation and an explicit reading-order number; Phase 4 applies tokens to produce visual HTML + DESIGN.md. Enforces readability heuristics, empty/loading/error trio, and blocks "AI slop" defaults (Inter/Roboto/Arial fallback, purple-on-white gradients). 와이어프레임을 먼저 합의한 뒤에야 비주얼로 진입하는 게이트로, "색부터 정하고 본다"는 편향을 차단한다.
when_to_use: 새 화면/플로우의 UI/UX 디자인이 필요할 때. "와이어프레임 만들어줘", "이 기능 UI 어떻게 짤지", "디자인 시안 잡아줘", "UX 개선해줘", "사용자 경험 좋게 다시" 같은 요청. 이미 디자인 시스템이 있고 컴포넌트 한두 개만 손보는 경우는 frontend-design / design-html 직접 사용이 더 빠르다. 요구사항이 흐릿하면 먼저 /brainstorm을 돌리고 결과를 입력으로 넘긴다.
argument-hint: <feature-name> [--out <dir>] [--skip-gate] [--from-brief <path>] [--refs <url,url,...>]
allowed-tools: Read, Write, Edit, Bash(mkdir *), Bash(ls *), Bash(open *), Glob, Grep, AskUserQuestion, WebFetch
disable-model-invocation: false
---

# /design-ui — Wireframe → Visual 2단계 UI/UX 설계

새 기능/플로우의 디자인을 **페이지 단위**로 설계한다. 한 기능은 보통 1~5개 페이지로 나뉜다(예: 메인 리스트 + 상세 + 일괄 확인 + 결과 요약). **회색 와이어프레임으로 레이아웃·정보구조·페이지 간 흐름을 먼저 합의**한 뒤에야 **타이포·색·여백을 입혀 비주얼**로 진입한다. 게이트 하나 사이에 두는 것만으로 "색·폰트부터 정하고 본다"는 편향이 사라지고, 사용자가 정말 봐야 할 것(정보 위계, 사용자 경험, 페이지 간 동선)에 집중하게 된다.

---

## Where this fits in the workflow

```
   /brainstorm (선택)            ← 요구사항이 흐릿하면 먼저 수행
        ↓
   ▶ /design-ui  ◀
        ↓
   Phase 1: Interview            (반복 — brief + 페이지 목록 합의)
        ↓
   Phase 2: Reference            (2~3개 경쟁사/유사 제품 — 페이지 분할 패턴 포함)
        ↓
   Phase 3: Wireframe            (flow.html 사이트맵 + wireframe.html 다중 페이지 스택)
        ↓
   ★ Gate: 페이지 + 와이어프레임 OK? ★    ← --skip-gate로 끌 수 있음
        ↓
   Phase 4: Visual               (타이포·색·여백·모션 + 페이지 간 인터랙티브 이동)
        ↓
   Phase 5: Deliver              (flow + wireframe + visual + DESIGN.md + references.md)
        ↓
   frontend-design / 실구현      ← 다음 스킬
```

- **Upstream**: 요구사항 (`/brainstorm` 결과 / 이슈 본문 / 한 줄 요청).
- **이 스킬**: Interview → Reference → Wireframe → (Gate) → Visual → Deliver의 결정적 파이프라인.
- **Downstream**: `frontend-design`이나 직접 구현에 산출 HTML과 DESIGN.md를 입력으로 넘긴다.

---

## Parameters

`$ARGUMENTS`는 frontmatter `argument-hint`에 명세된 형식으로 전달된다. 우선순위: `$ARGUMENTS` 명시값 > 환경변수 > skill default.

| Option | Meaning | Default |
|---|---|---|
| `<feature-name>` | 디자인할 기능/화면 이름 (필수) | — |
| `--out <dir>` | 산출물 출력 디렉토리 | `claudedocs/design/<feature>/` |
| `--skip-gate` | Phase 3/4 사이 게이트를 생략 (자동화 환경용) | off |
| `--from-brief <path>` | brainstorm/PRD 파일 경로를 Phase 1 입력으로 사용 | — |
| `--refs <urls>` | 콤마 구분 URL — Phase 2 자동 수집 대상 (없으면 인터뷰에서 묻는다) | — |

### Environment overrides

| Env var | Meaning | Default |
|---|---|---|
| `${DESIGN_UI_OUT}` | 기본 출력 디렉토리 오버라이드 (`--out` 미지정 시 사용) | `claudedocs/design/<feature>/` |
| `${CLAUDE_PLUGIN_ROOT}` | plugin 설치 루트. 다른 스킬 호출 시 참조 | (Claude Code 자동 주입) |
| `${CLAUDE_SKILL_DIR}` | 본 스킬의 자산(`templates/`, `references/`, `scripts/`) 경로 | (자동 주입) |

---

## Workflow

```
Phase 1: Interview      (반복 — brief 합의될 때까지)
Phase 2: Reference      (2~3개 패턴 수집·정리)
Phase 3: Wireframe      (회색 + UX 의도 + 읽기 순서)
★ Gate: 와이어프레임 검토 ★
Phase 4: Visual         (토큰 → 적용)
Phase 5: Deliver        (파일 + 다음 단계)
```

### Phase 1: Interview — brief가 합의될 때까지 반복

**일괄 4문항 묶음 금지.** 한 번에 1~2개씩 묻고, 답을 들은 뒤 다음 질문을 정하는 반복 인터뷰. brief 한 단락이 사용자 동의로 확정될 때까지 빠져나오지 않는다.

#### 인터뷰 루프

```
loop:
  1) 지금 가장 흐릿한 한 가지를 골라서 묻는다 (AskUserQuestion 1~2문항).
  2) 답을 받으면 brief 초안을 그 자리에서 갱신한다.
  3) brief를 사용자에게 보여주고 "여기 맞나요? 누락된 거 없나요?" 확인.
  4) 사용자가 "맞다" 할 때까지 1~3 반복.
```

#### 흐림이 큰 순서로 묻는다 (예시 — 상황 따라 순서·문구 조정)

| 순번 | 질문 (예시) | 듣고 싶은 것 |
|---|---|---|
| 1 | **문제** — "지금 사용자가 못 하는 게 정확히 뭐예요?" | 한 줄 problem statement |
| 2 | **주 사용자** — "이 화면을 가장 자주 쓸 한 명을 묘사해주세요(역할·맥락·기기)." | 페르소나 1명 |
| 3 | **핵심 작업** — "이 화면에서 무조건 끝낼 수 있어야 하는 작업 1~3개는?" | 동사 형태 작업 목록 |
| 4 | **사용 상황** — "언제, 어디서, 어떤 마음 상태에서 이 화면에 오나요?" | 트리거·맥락·감정 |
| 5 | **성공 상태** — "이 화면을 잘 썼다면 사용자는 어떤 상태가 돼 있어야 하나요?" | success criteria |
| 6 | **금기·제약** — "절대 하면 안 되는 것 / 기술·정책 제약은?" | guardrails |
| 7 | **페이지 분할** — "이 기능이 몇 개의 페이지/뷰로 나뉠 것 같나요? 각 페이지의 한 줄 목적은?" | 페이지 목록 1~5개 (이름 + 목적) |

**페이지 자동 추론 가이드** (사용자가 7번에 "잘 모르겠다" 답할 때):
- task가 1개고 단순 조회/입력이면 → 1페이지
- task에 "검토 → 확정" 같은 2단계 의사결정이 있으면 → 메인 + 확인 페이지
- task에 "여러 항목 일괄 처리"가 있으면 → 메인 + 선택 확인 페이지
- task에 "결과 공유/리포트"가 있으면 → 결과 요약 페이지 추가
- 항상 사용자에게 "이렇게 N개 페이지로 보면 될까요?" 확인받음. 자의로 결정 금지.

#### 자동 컨텍스트 수집 (질문 줄이기)

- `--from-brief`가 있으면 먼저 `Read`해 brief 초안 작성 → 빈 칸만 묻는다.
- `Glob`로 기존 디자인 시스템 신호 탐지: `**/DESIGN.md`, `**/design-tokens.*`, `**/tokens.scss`, `**/tailwind.config.*`, `**/_variables.scss`. 있으면 Phase 4에서 재사용.
- `Glob`로 같은 기능의 기존 화면 탐지: `**/{feature}*.{vue,tsx,html}`. 있으면 사용자에게 "이게 현재 상태인가요?" 한 번에 확인.

#### Phase 1 산출 — Problem Brief (사용자 사인오프 필수)

```
Feature:  <name>
Problem:  <한 단락 — 무엇이, 왜 문제인가>
User:     <페르소나 한 줄>
Tasks:    1) … 2) … 3) …
Context:  <언제·어디서·어떤 마음>
Success:  <한 줄>
Guard:    <금기·제약 bullet>
System:   <탐지된 디자인 시스템 / 없으면 "신규 토큰 생성">
Pages:
  - page-1 (<short-slug>): <한 줄 목적>
  - page-2 (<short-slug>): <한 줄 목적>
  - ...
```

`page-N`은 Phase 3 이후 모든 산출물에서 동일한 slug로 참조된다 (flow.html, wireframe.html `<section id="page-N">`, visual.html hash `#page-N`).

이 brief에 사용자가 "OK"라고 답하기 전에는 Phase 2로 절대 진입하지 않는다.

---

### Phase 2: Reference — 경쟁사·유사 제품에서 무엇을 가져올지

좋은 디자인은 진공에서 나오지 않는다. **이 단계의 목적은 베끼는 게 아니라, 도메인에서 이미 검증된 UX 패턴을 의식적으로 선택·거절하는 것.**

#### 레퍼런스 후보 확보

1. `--refs`로 URL이 들어왔으면 그대로 사용.
2. 없으면 `AskUserQuestion`으로 한 번 묻는다:
   - "같은 기능을 잘 한다고 느낀 제품 2~3개 알려주세요 (URL이나 이름)"
   - 사용자가 "모르겠다"면 Claude가 도메인 추론(예: 예약 화면 → Calendly/Booking.com/Toss)으로 후보 3개를 제시하고 사용자가 1~2개 고른다.

#### 각 레퍼런스 분석 (WebFetch 사용)

URL당 다음 4개 슬롯만 추출 (장황한 설명 금지):

| 슬롯 | 내용 |
|---|---|
| **Steal** | 우리가 가져올 패턴 1개 (구체적으로 — "primary CTA를 첫 스크롤 안에 단독 배치") |
| **Adapt** | 변형해서 쓸 패턴 1개 ("좌측 필터 + 우측 결과지만, 모바일은 필터를 sheet로") |
| **Reject** | 의식적으로 거절할 패턴 1개 + 이유 ("3-step wizard — 우리 사용자는 1회성 작업이라 과함") |
| **Why this ref** | 우리 문제와 어디서 겹치는지 한 줄 |

#### Phase 2 산출 — `references.md` (2~3개 카드)

이 문서는 Phase 3 와이어프레임의 모든 배치 결정의 근거가 된다. 와이어프레임 주석에서 "Why ref-1 Steal" 같이 역참조할 수 있어야 한다.

WebFetch 실패 / 사용자가 URL 제공 거부 시: 사용자가 "skip"이라고 명시했을 때만 Phase 2를 건너뛴다. 그 경우 references.md에 "사용자 요청으로 생략 — Phase 3 결정은 일반 UX 휴리스틱에 의존"이라고 명시.

---

### Phase 3: Wireframe — 페이지 단위 사이트맵 + 다중 페이지 와이어프레임

**와이어프레임은 박스 배치가 아니다. "사용자가 어느 페이지에서 시작해, 어떤 트리거로, 어느 페이지로 이동하며, 어떤 감정으로 임무를 끝내는가"의 시각화다.**

#### 3-A. Sitemap — `flow.html` 먼저

`templates/flow.html`을 베이스로 페이지 박스와 화살표(전이 트리거)를 그린다:

```
   [page-1: Watchlist]  ──[행 클릭]──▶  [page-2: Patient Detail]
         │                                      │
         │ [batch 버튼]                          │ [닫기]
         ▼                                      └──▶ page-1 복귀
   [page-3: Batch SMS Confirm]
         │ [전송] → toast → page-1
         │ [취소] → page-1
```

각 화살표는 **트리거(클릭 대상)** + **결과 페이지**를 명시. 막다른 길이 없어야 한다 (사용자가 항상 page-1로 돌아갈 길이 있어야 함). 첫 진입 페이지(entry)를 분명히 표시.

#### 3-B. Wireframe — `wireframe.html` 다중 페이지 스택

한 파일 안에 모든 페이지를 세로로 쌓는다. 각 페이지는 `<section class="wf-page" id="page-N">`로 감싸고, 페이지 사이에는 flow.html의 화살표를 그대로 옮겨 적은 transition strip을 둔다.

#### 모든 박스가 가져야 하는 4개 슬롯 (페이지 내부, 변경 없음)

`templates/wireframe.html`의 `.wf-section` 패턴. 각 박스는 다음을 반드시 표시:

| 슬롯 | 무엇 | 예시 |
|---|---|---|
| **Order** | 의도된 읽기 순서 번호 (1, 2, 3 …) — **페이지마다 1부터 다시 시작** | `1` |
| **Label** | 박스 이름 | `[ResultList]` |
| **Intent** | 이 자리에서 사용자가 느껴야 할 것 | "탐색 중 안심 — 결과가 얼마나 있는지 즉시 보임" |
| **Why here** | 이 위치인 이유 (refs 역참조 또는 휴리스틱) | "ref-2 Steal: above-fold에 결과 수 노출" |

#### 페이지 단위 결정 원칙

1. **모든 페이지의 entry/exit를 명시.** 이 페이지로 어떻게 들어오는가, 어떻게 나가는가.
2. **각 페이지에 독립적인 above-the-fold가 있다.** 페이지마다 자기만의 fold 마커.
3. **페이지 간 데이터 의존성.** page-2는 page-1의 어느 정보를 받아오는지 명시.
4. **돌아갈 길 보장.** 모든 페이지에서 entry로 복귀하는 경로가 있어야 한다. 막다른 사이드 페이지 금지.

#### 페이지 내부 배치 순서 결정 원칙 (변경 없음)

1. 읽기 순서 번호를 먼저 정하고 박스를 그린다.
2. F-pattern / Z-pattern을 의식한다.
3. Primary action은 단독 배치.
4. Above the fold에 핵심 작업 1개만.
5. 모바일에서 순서가 바뀌면 그 변경도 번호로 표시.

#### 회색 규칙 (변경 없음)

- 색·폰트·아이콘 금지. 회색 박스 + 라벨 + 4개 슬롯만.
- 데이터 영역은 `default | empty | loading | error` 4상태 변종 자리 모두 표시.
- 반응형: 360 / 768 / 1280에서 어떻게 재배치되는지 명시.

산출: `flow.html` + `wireframe.html` 두 파일 (둘 다 브라우저에서 더블클릭으로 열림).

---

### ★ Gate: Wireframe approval ★

`--skip-gate`가 아니면 `AskUserQuestion`으로 반드시 묻는다:

- **이 와이어프레임으로 비주얼 단계 진입할까요?**
  - "OK, 비주얼 가자" — Phase 4로
  - "수정 필요" — 어디를(읽기 순서 / Intent / 배치 / 누락 섹션 / refs 반영 부족)? 그 부분만 다시 Phase 3 반복
  - "되돌아가기" — Phase 1 또는 Phase 2로 (brief 또는 refs가 잘못 잡혔던 경우)

게이트의 목적은 "색을 입히기 전에 **경험과 배치가** 맞는지" 확인하는 것. 이 단계에서 잡히는 UX 오류는 비주얼 적용 후 잡을 때보다 10× 싸다.

---

### Phase 4: Visual — 타이포·색·여백·모션 + **클릭 가능한 프로토타입**

1. **토큰 결정**(기존 시스템 있으면 그대로 사용, 없으면 신규):
   - **Typography**: display font + body font 페어. **Inter/Roboto/Arial/system-ui fallback 금지**. 본문 ≥16px, line-height 1.5, 본문 line-length 45~75ch.
   - **Color**: 1 dominant + 1~2 accent + neutral scale (5단계 이상). 본문/배경 대비 ≥4.5:1 (WCAG AA).
   - **Spacing**: 4 또는 8 base scale.
   - **Motion**: 100~200ms ease-out 중심. `prefers-reduced-motion` 대응 토큰 포함.
2. **Aesthetic direction** 한 줄 선언 (예: "차분한 에디토리얼", "도구적·산업적", "절제된 미니멀"). 흐릿한 "modern clean" 같은 표현 금지. **이 한 줄은 Phase 2의 refs Steal/Reject 결정과 일관되어야 한다.**
3. `templates/visual.html`을 베이스로 와이어프레임의 박스를 실제 컴포넌트로 채움. **모든 페이지의 읽기 순서와 Intent를 보존**해야 한다 — 시각 디자인이 와이어프레임 의도를 뒤집으면 안 됨.
4. **다중 페이지 → 하나의 visual.html에 hash 라우팅으로 묶는다.**
   - 모든 페이지는 한 파일 안에 `<section class="page-mock" id="page-N">`로 stack.
   - 한 번에 하나만 `display:block`, 나머지는 `display:none`. 현재 페이지는 `location.hash`로 결정.
   - 페이지 전이 트리거(버튼/링크/행 클릭)는 `location.hash = '#page-N'`으로 이동. flow.html의 화살표가 visual.html에서 실제 동작.
   - 상단 banner에 페이지 점프 셀렉터(`<select>` 또는 chip 그룹) 추가 — 리뷰어가 임의 페이지로 즉시 점프.
5. **클릭 가능한 프로토타입으로 만든다** — 정적 렌더 금지. 아래를 vanilla JS(외부 의존 없음)로 wire:
   - **brief.md의 모든 primary task마다 시연 경로 1개** — 클릭하면 시각 피드백(상태 변경 / toast / 다음 페이지로 hash 이동). 시연 못 하면 그 task의 디자인은 아직 끝나지 않은 것.
   - **상태 스위처** — 상단 banner에 `default | empty | loading | error` 즉시 전환. 페이지별로 상태가 다르면 페이지마다 독립.
   - **시간/카운트다운/타이머** — `setInterval`로 실제 tick. 정지된 숫자는 작동 환경의 압박감을 전달 못 함.
   - **모든 토글 (마스킹·필터·체크박스)** — 실제로 토글 동작.
   - **페이지 간 상태 전달** — page-1에서 선택한 N명이 page-2(확인 화면)에 실제 N명으로 보여야 함. 글로벌 `state` 객체로 페이지 간 공유.
   - **모의 데이터 명시** — 상단 "프로토타입 모드" 배너 + 현재 페이지 이름.
6. 산출 직전 **UX 체크리스트 통과 확인** — `references/ux-checklist.md`의 항목을 모두 점검. 신규 항목 16~21 (시연 경로 / 상태 스위처 / 라이브 토글 / 사이트맵 일관 / 페이지 간 상태 / 돌아갈 길) 통과 필수.

### Phase 5: Deliver

`<out>/` 디렉토리에 다음 파일 작성:

```
<out>/
├── brief.md            # Phase 1 사인오프된 brief (페이지 목록 포함)
├── references.md       # Phase 2 레퍼런스 카드 (Steal/Adapt/Reject)
├── flow.html           # Phase 3-A 사이트맵 (페이지 박스 + 화살표)
├── wireframe.html      # Phase 3-B 다중 페이지 와이어프레임 (페이지 세로 스택)
├── visual.html         # Phase 4 결과 (hash 라우팅 + 페이지 간 상태 공유)
└── DESIGN.md           # 토큰·근거·페이지별 Order 보존표·체크리스트·다음 단계
```

마지막에 한 줄 안내:
```
✅ Design ready at <out>/. Open visual.html in browser. Next: /frontend-design or implement directly.
```

`open <out>/visual.html`은 사용자 확인 후에만 실행.

---

## Standing rules

(아래 규칙은 절차가 아니라 매 호출에 항상 적용되는 원칙이다.)

- **Brief 사인오프 없이 Phase 2 진입 금지.** 인터뷰는 일괄 질문 4개가 아니라, 흐릿한 것 1~2개씩 묻고 brief를 갱신하며 사용자가 "OK" 할 때까지 반복하는 루프다.
- **레퍼런스는 베끼는 게 아니라 의식적으로 선택·거절하기.** 각 ref마다 Steal / Adapt / Reject 한 개씩. "Reject + 이유"가 빠지면 그 ref는 미완.
- **와이어프레임은 박스가 아니라 경험.** 모든 박스가 4개 슬롯(Order / Label / Intent / Why here)을 가져야 한다. Intent와 Order가 비면 박스를 그리지 않는다.
- **읽기 순서를 박스보다 먼저 정한다.** "1번이 뭔지" 모르면 와이어프레임을 그리기 시작하지 않는다. 모바일에서 순서가 바뀌면 그 변경도 번호로 표시.
- **Wireframe first.** Phase 3 산출에는 색·폰트·아이콘이 들어가지 않는다. 회색조 + 라벨 + 4슬롯 주석만. 사용자가 "그냥 컬러로 바로 해줘"라고 해도 이유를 한 줄 설명하고 게이트로 간다 (`--skip-gate`로 자동화 환경만 우회).
- **재사용 우선.** 프로젝트에 디자인 시스템이 있으면 새 토큰을 만들지 않는다. CLAUDE.md의 "Frontend Aesthetics" 규칙과도 일치한다.
- **AI slop 금지.** Inter / Roboto / Arial / system-ui를 fallback으로 쓰지 않는다. 흰 배경에 보라 그라데이션 금지. cream/serif house style을 무관한 맥락에 쓰지 않는다. 박스 그리드 카드 + 보라 CTA의 "그 디자인" 금지.
- **세 가지 상태.** 데이터를 보여주는 모든 영역은 `default + empty + loading + error` 네 변종이 정의되어야 한다. 와이어프레임에 주석으로, 비주얼에 실제 마크업으로.
- **접근성 하한선.** 본문 ≥16px / line-height 1.5 / contrast ≥4.5:1 / 터치 타깃 ≥44×44px / focus state 가시. 이건 양보 안 함.
- **stdlib only HTML.** 산출 HTML은 외부 CSS·JS·폰트 호스팅 없이 한 파일에서 열린다(폰트는 `<link rel="stylesheet">` 한 줄 허용). 사용자가 미리보기 환경 없이도 더블클릭해서 본다.
- **시안이 아니라 프로토타입.** Phase 4 산출 visual.html은 클릭하면 동작해야 한다. 그래야 사용자가 "이 흐름이 진짜 손에 맞나"를 5분 안에 검증 가능. 정적 렌더만 주면 리뷰가 "이거 색 좋다 나쁘다"로 빠지고 정작 task ②/③ 같은 핵심 흐름 결함은 구현 단계까지 발견 안 된다.
- **페이지 단위로 설계한다.** 1~5개 페이지. 한 페이지에 다 욱여넣지 않는다 — 사용자가 "검토 → 확정"이나 "선택 → 일괄 확인" 같은 2단계 의사결정을 하면 페이지를 나누는 게 정직하다. 반대로 페이지를 과하게 쪼개도 동선이 길어진다. Phase 1에서 페이지 수를 명시적으로 합의한다.
- **flow.html ⇆ wireframe.html ⇆ visual.html 페이지 ID 일관.** 세 파일은 같은 `page-N` slug를 공유한다. flow의 화살표가 wireframe의 transition strip, visual의 hash 라우팅과 1:1 대응해야 함. 일관성이 깨지면 리뷰어가 무엇이 정본인지 모름.
- **모든 페이지는 돌아갈 길이 있다.** 막다른 사이드 페이지 금지. 사용자가 의도치 않게 빠져나갈 수 없는 페이지에 갇히는 게 가장 흔한 UX 사고.

---

## Automated vs needs your taste

(automated decision gating — 무엇을 Claude/스크립트가 자동 결정하고, 무엇이 사용자 taste 영역인지 명시.)

| Claude가 자동 결정 | 사용자(taste) 결정 |
|---|---|
| 인터뷰 다음 질문 선택 (현재 brief에서 가장 흐릿한 슬롯 골라 묻기) | brief 사인오프 여부 |
| 레퍼런스 후보 추론 (사용자가 모르겠다 할 때만) | 어떤 ref를 채택할지, Steal/Adapt/Reject 판정 |
| 와이어프레임 레이아웃 그리드 (12/8/단일) | 페이지의 정서적 톤 ("차분한 / 도구적 / 표현적") |
| 박스별 4슬롯(Order/Label/Intent/Why here) 자리 잡기 | Intent 문구의 정확성 — "이게 진짜 사용자가 느낄 것인가" |
| 읽기 순서 번호의 형식적 배치 (F-pattern 적용) | 순서 자체가 맞는지 판단 |
| 기존 디자인 시스템 탐지 + 재사용 결정 | 새 토큰을 만들 때 폰트 페어 후보 1차 픽 |
| 본문 ≥16px / contrast ≥4.5:1 / 터치 ≥44px 강제 | "이 컬러 매칭이 우리 브랜드와 맞나" 판단 |
| empty / loading / error 변종 자리 잡기 | 그 상태에서 보여줄 메시지 톤 |
| UX 체크리스트 자동 점검 | 게이트 통과 여부 |

자동이 잘못 잡으면 사용자가 Phase 2/3을 다시 돈다. 자동이 막은 결정을 "약간 우회"로 통과시키지 않는다 — 와이어프레임을 다시 그리는 게 정답.

---

## 책임 경계

| 담당 | 비담당 |
|---|---|
| 와이어프레임 HTML + 비주얼 HTML + DESIGN.md 산출 | 실구현 코드 (Vue/React 컴포넌트) |
| 디자인 시스템 탐지 및 재사용 결정 | 디자인 시스템 자체를 만드는 것 (필요하면 `design-consultation`) |
| UX 체크리스트 자동 점검 | QA·E2E·시각 회귀 테스트 |
| 빈/로딩/오류 상태 자리 표시 | 그 상태의 카피라이팅 |
| 색/폰트/여백 토큰 기록 | 브랜드 가이드라인 작성 |

---

## Templates and references

| File | Purpose |
|---|---|
| [templates/brief.md](templates/brief.md) | Phase 1 산출 — 사용자 사인오프된 problem brief (페이지 목록 포함) |
| [templates/references.md](templates/references.md) | Phase 2 산출 — Steal/Adapt/Reject 카드 2~3개 |
| [templates/flow.html](templates/flow.html) | Phase 3-A 사이트맵 — 페이지 박스 + 전이 화살표 |
| [templates/wireframe.html](templates/wireframe.html) | Phase 3-B 다중 페이지 와이어프레임 — `.wf-page` 스택 + 페이지 내부 `.wf-section` 4슬롯 |
| [templates/visual.html](templates/visual.html) | Phase 4 비주얼 베이스 — `.page-mock` 스택 + hash 라우팅 + 페이지 간 state 공유 |
| [templates/DESIGN.md](templates/DESIGN.md) | Phase 5 산출 — 토큰 표, refs 요약, 페이지별 Order 보존표, UX 체크 결과 |
| [references/ux-checklist.md](references/ux-checklist.md) | Phase 4 직전 강제 점검 항목 (21개) |
| [scripts/validate_skill.py](scripts/validate_skill.py) | 스킬 자가 검증 (frontmatter, 5 Phases, templates, references, override) |

---

## Pitfall / Failure modes — 이렇게 하면 안 된다

- ❌ Phase 1을 일괄 4문항으로 처리하고 사인오프 없이 진행 → brief가 흐릿한 채 와이어프레임이 굳어버림
- ❌ Phase 2를 건너뛰기 (사용자가 명시적으로 skip하지 않았는데) → Phase 3 배치 결정의 근거가 "내 추측"이 됨
- ❌ 와이어프레임 박스에 Intent/Order 슬롯을 빈 채로 두기 → 게이트가 의례가 되고 색 토론으로 빠짐
- ❌ Phase 3에 색을 입혀버리기 → 게이트가 무의미해지고 토론이 "이 색이 좋다 나쁘다"로 빠짐
- ❌ Primary CTA를 다른 CTA와 나란히 배치 → 선택의 마비
- ❌ 기존 DESIGN.md를 무시하고 새 토큰 만들기 → 디자인 시스템 파편화
- ❌ "loading 상태는 나중에" 미루기 → 실구현 단계에서 다시 디자인
- ❌ "modern, clean, minimal" 같은 흐릿한 톤 선언 → Phase 4에서 결정이 안 내려짐
- ❌ 한 페이지에 모든 task 욱여넣기 → 의사결정이 흐려지고 above-the-fold 경쟁
- ❌ 페이지를 6개 이상 쪼개기 → 동선 과다, 사용자가 길을 잃음. 의심스러우면 3개로 시작
- ❌ flow.html과 wireframe.html에서 페이지 이름/slug 불일치 → 리뷰어가 정본을 모름
- ❌ visual.html에서 페이지 전이를 새 탭/페이지 이동으로 처리 → 프로토타입성 깨짐. hash 라우팅으로 한 파일에 유지
- ❌ 막다른 페이지 (돌아갈 길 없음) → 사용자 갇힘. 모든 페이지에 entry로 복귀 경로 명시

---

## Pre-flight checklist

각 Phase 전환 전 self-check:

- [ ] Phase 1 → 2: brief에 사용자 "OK" 사인오프 완료
- [ ] Phase 2 → 3: refs 2~3개 각각 Steal/Adapt/Reject 슬롯 채워짐
- [ ] Phase 3 → Gate: 모든 박스가 Order/Label/Intent/Why here 4슬롯 보유, empty/loading/error 변종 표시
- [ ] Gate 통과: 사용자 명시 "OK, 비주얼 가자" 또는 `--skip-gate`
- [ ] Phase 4 → 5: ux-checklist.md 12개 항목 모두 통과, AI slop 토큰 0건
- [ ] Phase 5 발행: out 디렉토리에 brief / references / wireframe / visual / DESIGN 5개 파일 모두 존재
- [ ] scripts/validate_skill.py 통과 (frontmatter, phases, templates, references, override)
