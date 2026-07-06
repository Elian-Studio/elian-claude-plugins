# Functional Spec Guide

Reference for `/functional-spec` Phase 6 per-screen `.md`. Read after
`component-design-template.md` (the shared catalog is designed first, in Phase 2).

A functional spec is **not** a design spec. `design-spec.md` (from `/design-feature`)
describes screens in design language and deliberately bans code terms. A functional
spec does the opposite: it binds every wireframe element to code — components to
reuse (from the **shared catalog** or an existing file), new screen-specific
components, and the endpoint/field behind each element. It is the contract
`/implement` builds from.

**Grounding mode.** On an existing codebase, cite a real `file:line` for every
reuse and data source. On a **greenfield** product (no code yet), cite a
**designed** endpoint/entity from `api-spec.md` / `ddl.sql` / `design.md` instead —
every component is new (designed in the Phase 2 catalog). Never fabricate: a
mockup's hardcoded value (price, %, name) with no data source is an open question,
not a spec value.

**Shared components are NOT re-declared here.** §③ references the Phase 2
`component-design.md` catalog for anything used on ≥2 screens; this file only adds
components genuinely unique to this screen.

---

## Mandatory 5-section structure

```markdown
# <Screen Name> V2 — 기능명세

- 이슈: <label> (context, parent if any)
- 근거 목업: <path to the wireframe/mockup this spec is derived from>
- plan: <path to the plan/roadmap task if one exists>
- 목적: fix "what each element does + component contract" BEFORE code. This is a spec, not code.

## ① 화면 개요
What the screen does, who uses it, the IA anchor (real menu/route), and the single
most important grounding fact (e.g. "표시 필드 6종 중 1종만 신규 BE, 나머지는 이미 VO에 존재. 신규 테이블 0개.").

## ② 기능 분해 표
One numbered row per wireframe element. The number is the connected-view anchor.

| # | 요소 | 기능(동작) | 데이터 소스·BE 의존 | 상태(빈/로딩/에러/선택/비활성) | 상호작용·연동 | 완료 판정 |
|---|------|-----------|--------------------|------------------------------|--------------|----------|

- 데이터 소스: a **real** endpoint + field (`GET /patient` `VO.Simple.hpNo`) or `UI-only` with reason.
- 완료 판정: a real-server-round-trip condition — "실 API에 keyword 전달되어 서버 필터된 rows 반환(클라 필터 아님)", never "테이블이 렌더된다".

## ③ 컴포넌트 계약
Front-end rules first (e.g. "기존 view 미수정, 신규 view로 분리, base 컴포넌트 미수정").

### 재사용 (catalog / existing)
| 컴포넌트 | 출처 | 이 화면 사용(props/variant) |
Shared components from `component-design.md` (name + "catalog"), or on a codebase
an existing component at its exact `file:line`. Do NOT re-design a shared component here.

### 신규 (this screen only)
| 컴포넌트/파일 | 배치(신규) | 역할 | props | emit/노출 | 상태 |
Only components unique to this screen. If one turns out to recur, promote it to the
Phase 2 catalog instead of duplicating.

### 데이터 흐름
A short tree: view → composable → service → endpoint → selection/handoff. Include
the downstream handoff contract (object shape passed on) and the minimal change to enable it.

## ④ BE 의존 / 신규 필요
### 신규 (plan iN)
The real change: VO field, mapper/query (file + line range), table. Honesty line
("신규 테이블 0개, 신규 집계 1건"). Smallest change that satisfies the wireframe.
### 기존 (BE 무변경)
Fields already provided + their source.
### UI-only 정당성
Why selection/label mapping needs no server round-trip.

## ⑤ 미결 질문
Numbered. Every unverified Phase-1 assumption + every real open decision. Each is a
gate before /implement. Tag `[BE]` / `[UX]` / `[정합]` as useful.
```

---

## Golden example (trimmed — real output shape)

From a real issue (`MPT-9457` 환자 목록 V2). Note how every claim is grounded:

**② 기능 분해 표 (excerpt)**

| # | 요소 | 기능 | 데이터·완료 판정 | 구분 |
|---|------|------|-----------------|------|
| 1 | 키워드 검색 | 이름·연락처·차트번호로 서버 재조회(debounce, page=1) | `GET /patient` `search.keyword` → 서버 필터 rows 반환(클라필터 아님) | 기존 |
| 11 | 방문 횟수 | 완료 진료 건수 표시 | **신규**: `consult_v2` COUNT(status∈CON-END/COM, type≠REC) → `visitCount:int`. 실 API 카운트 반환(껍데기 금지) | 신규 BE |
| 13 | 발송 아이콘(행) | 해당 환자 1명 단건 발송 창 | `childWindowService.createCrmSendWindow({name,hpNo})` | 기존 |

> Of 15 elements, exactly **one** is new BE (#11). The rest are existing-data display
> or client state. "Build the screen" really = assemble a new view + one aggregate.

**③ 재사용 (excerpt)** — reuse is grounded in real paths:

| 컴포넌트 | 경로 | 사용 계약 |
|---------|------|----------|
| `MTable` | `src/components/base/MTable.vue` | 골격만. built-in select-mode는 페이징과 안 맞음 → `selectable=false` + 체크박스 컬럼 slot |
| `MPagination` | `src/components/base/MPagination.vue` | `v-model="search.page"` `:totalRowCnt` `@change="movePage"` |
| `ModalPatientDetail` | `src/components/modal/ModalPatientDetail.vue` | `showPatientDetail(seq)` 호출로 오픈 |

**⑤ 미결 질문 (excerpt)**

1. **[정합]** plan은 `GET /hospital/patient/search`라 적었으나 목업 리치 테이블을 실제 반환하는 건 `GET /patient` — 라벨 정정 필요.
2. **[BE]** 방문유형 드롭다운을 서버 파라미터로 거를지 vs 표시만 — 현 `IHospitalPatientSearch`에 visit 필터 부재.

---

## Checklist

Before handing off to `/implement`:

- [ ] Every ② row has a data source: codebase → `file:line`; greenfield → a designed endpoint+field; or a justified `UI-only`.
- [ ] Every ② 완료 판정 is a real-server condition, not "renders".
- [ ] No fabricated value: any mockup hardcode (price/%/name) with no source is in ⑤, not treated as real.
- [ ] Every ③ 재사용 entry names a catalog component or an existing `file:line` — shared components are NOT re-declared here.
- [ ] Every ③ 신규 component is genuinely screen-specific (recurring ones live in the catalog).
- [ ] ④ counts new tables/endpoints honestly.
- [ ] ⑤ lists every unpinned assumption — none silently promoted to fact.
- [ ] The connected view includes the §③ component section, its table survives the wireframe's linked CSS (`.fs-*` + scoped reset), and `data-n` matches ② rows one-to-one.
