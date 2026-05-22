# Problem Brief — {{FEATURE_NAME}}

Signed off by user on {{TODAY}}.

---

## Problem

{{PROBLEM_PARAGRAPH}}

(한 단락. "사용자가 X를 못 한다" 또는 "Y가 너무 비효율적이다" 같이 구체적.)

## Primary user

{{USER_PERSONA}}

(역할 · 맥락 · 기기. 추상명사 금지 — "관리자" ❌, "월 200건 예약을 처리하는 동네의원 데스크 직원, 데스크탑 크롬" ✅)

## Core tasks (1~3)

1. {{TASK_1}}
2. {{TASK_2}}
3. {{TASK_3}}

(동사로 시작. "보기" ❌, "오늘 예약된 환자 중 노쇼 가능성 높은 사람 찾기" ✅)

## Context — 언제 / 어디서 / 어떤 마음

- **When**: {{WHEN}}
- **Where**: {{WHERE}}
- **Mood**: {{MOOD}}

## Success state

{{SUCCESS}}

(이 화면을 잘 썼다면 사용자는 어떤 상태에 도달해 있어야 하는가)

## Guardrails — 금기 / 제약

- {{GUARD_1}}
- {{GUARD_2}}

(기술·정책 제약, 또는 "절대 하지 말 것")

## Design system source

{{SYSTEM_SOURCE}}

(`reused: <path>` 또는 `newly created`)

## Pages — 페이지 단위 분할 (1~5개)

| slug | 페이지 이름 | 한 줄 목적 | Entry (어떻게 들어오나) | Exit (어디로 나가나) |
|---|---|---|---|---|
| page-1 | {{PAGE_1_NAME}} | {{PAGE_1_PURPOSE}} | {{PAGE_1_ENTRY}} | {{PAGE_1_EXIT}} |
| page-2 | {{PAGE_2_NAME}} | {{PAGE_2_PURPOSE}} | {{PAGE_2_ENTRY}} | {{PAGE_2_EXIT}} |
| page-3 | {{PAGE_3_NAME}} | {{PAGE_3_PURPOSE}} | {{PAGE_3_ENTRY}} | {{PAGE_3_EXIT}} |

> **Entry page**: page-1 (사용자가 가장 자주 시작하는 페이지)
> 모든 페이지는 entry로 돌아갈 길이 있어야 함.

---

## Sign-off log

| When | Field changed | By |
|---|---|---|
| {{T1}} | initial draft | claude |
| {{T2}} | tasks revised | user |
| {{T3}} | signed off | user |
