# Roadmap Task Writing Guide

Reference for `design-feature` Phase 5. Read this before writing task objects
in `roadmap.json`.

---

## Core Principle

**Behaviour first. Class and method names are secondary.**

Developers forget class names. They do not forget "what becomes possible when
this task is done." Class names can be found by opening the codebase. "Why does
this code exist" cannot be recovered without documentation.

---

## The Three Section Roles

| Section | Question it answers | Audience |
|---------|---------------------|----------|
| `desc` | What does this slice do and why? | PM, BE, FE |
| `criteria` | Done conditions — what must be true for this to count as done? | Reviewer, QA |
| `subs` | What implementation steps are needed, in order? | Implementer |

Use all three when a task is large enough to warrant them. For a small,
well-understood task a `title` + one `criteria` item may be enough — do not
pad sections just to fill the template.

---

## desc — Three-Part Summary

Format: user/operations outcome → one-line BE/FE summary → MVP scope and
current state.

**Bad — implementation identifiers first:**

```json
"desc": [
  "Duplicate notifyUpdateSubscriptionToAdmin → create notifyAlimtalkRequestToAdmin, add signal type NOTIFY_ADMIN_ALIMTALK_REQUEST. payload 5 fields: type·hospitalSeq·hospitalName·requestKind(CHANNEL|TEMPLATE)·requestSeq. Trigger point: requestChannel and requestTemplate in HospitalAlimTalkRequestFacadeService, immediately after save succeeds."
]
```

This tells you nothing about *why* the task exists or what changes for the user.

**Good — behaviour first:**

```json
"desc": [
  "When a hospital submits an alimtalk channel/template request, an alert appears immediately on the operations screen.",
  "Reuses the existing STOMP admin topic (/topic/a/all) — no new infrastructure.",
  "",
  "BE: add signal type + send method → call after save. FE: add handler to existing topic subscription.",
  "",
  "MVP scope: new channel + template requests only (A1, A2). Current state: 0 implemented (not started)."
]
```

---

## criteria — Behaviour Headline + Implementation Hint

Format: `[what becomes possible / what fact is guaranteed]`
then optionally `→ [how — minimal implementation hint]`

The headline must read like a test scenario title. Everything after `→` is a
hint for the implementer — write it without class names.

**Bad — class name as headline:**

```json
"criteria": [
  { "text": "SignalMessageType gets NOTIFY_ADMIN_ALIMTALK_REQUEST (SignalMessageType.java:49, 'admin' group) + SignalMessageBroker.notifyAlimtalkRequestToAdmin(...) created — destination=TOPIC_AUTH_ADMIN_ALL...", "done": false }
]
```

**Good — behaviour as headline:**

```json
"criteria": [
  { "text": "An alimtalk request signal can be sent to the admin topic → add signal type enum + send method, payload includes hospitalSeq/hospitalName/requestKind/requestSeq", "done": false },
  { "text": "The signal fires the moment channel/template registration is saved → wire send call immediately after save; resolve hospitalName lookup path", "done": false },
  { "text": "The operations screen shows a new-request alert and navigates to the review drawer on confirm → socket receive → sticky notification stack (bottom-right) + auto-refresh review list", "done": false },
  { "text": "Signal send failure does not block hospital request submission → async processing separates send from transaction", "done": false }
]
```

---

## subs — One Action Per Item, Starting with a Verb

Format: `[verb] + [object] — what this step does`
then optionally `→ [technical detail — only when not obvious]`

Each sub item is one action. Do not bundle multiple changes into one item.

**Bad — class names and file paths leading:**

```json
"subs": [
  { "text": "api-common SignalMessageType.java: add NOTIFY_ADMIN_ALIMTALK_REQUEST("NOTIFY_ADMIN_ALIMTALK_REQUEST") enum constant near UPDATE_ADMIN_HOSPITAL_SUBSCRIPTION:49 in 'admin' group", "done": false },
  { "text": "Create SignalMessageBroker.notifyAlimtalkRequestToAdmin(...) — TOPIC_AUTH_ADMIN_ALL destination, SignalBrokerMessage.builder with hospitalSeq/hospitalName/requestKind/requestSeq; extend to 4-arg to carry requestSeq", "done": false }
]
```

**Good — action as the leading phrase:**

```json
"subs": [
  { "text": "Add a dedicated signal type for alimtalk requests → new constant in the admin signal group", "done": false },
  { "text": "Add a send method that emits an alimtalk request signal to the admin topic → payload: 5 fields; resolve arg-count mismatch between design docs", "done": false },
  { "text": "Wire the send call immediately after channel/template registration is saved → inject send service; resolve hospitalName lookup", "done": false },
  { "text": "Add a socket handler on the operations screen to display the alert → sticky notification (bottom-right) + auto-refresh review list", "done": false }
]
```

---

## features — Capability Checklist (Reviewer/QA)

`features[]` is a **product-facing** checklist, separate from `criteria`/`subs`.
It answers one question: "is this screen functionally complete?" The audience is
a PM or QA skimming a screen, not an implementer. Each `t` must read as a
capability the reader can verify at a glance — never an implementation task.
`sub[]` bullets are the concrete, enumerable behaviours of that capability.

Do not pad. `features[]` is for screens/tasks complex enough to warrant a
functional breakdown; skip it for small, well-understood tasks (same rule as
`criteria`/`subs` — do not fill the template just because it exists).

**Bad — implementation tasks disguised as features:**

```json
"features": [
  { "name": "LoginController", "items": [
    { "t": "POST /api/login 핸들러 추가", "done": true, "sub": ["@Valid 적용", "JWT 발급"] }
  ]}
]
```

This is a `subs` list wearing a `features` costume — it names endpoints and
annotations, not what a user can do.

**Good — capabilities a reviewer can verify:**

```json
"features": [
  { "name": "로그인", "items": [
    { "t": "이메일과 비밀번호로 로그인할 수 있다", "done": true, "sub": ["형식 오류 시 인라인 메시지 표시", "5회 실패 시 잠금"] },
    { "t": "비밀번호 재설정 링크를 이메일로 받는다", "done": false }
  ]},
  { "name": "세션", "items": [
    { "t": "자동 로그인이 유지된다", "done": false, "sub": ["30일 만료", "로그아웃 시 즉시 해제"] }
  ]}
]
```

**Why:** a reviewer opening the drawer sees ✓/◐ per capability and knows
exactly what still fails, without reading code or the implementer's `subs`.

---

## dropped + reason — Recording a Descope Decision

Set `status: "dropped"` when there is an **explicit decision not to build** a
task/screen — not merely "not started yet." A `todo` task looks unstarted; a
`dropped` task reads as "decided against," excluded from the progress %.

Always pair it with `reason`, naming the decision date/source when known:

```json
{ "title": "SSO 연동", "status": "dropped", "reason": "2026-07-03 점검 결정: 3rd-party 우선순위 낮음, 구현 제외" }
```

Use `hold` (not `dropped`) when the work is merely paused and expected to
resume.

---

## title Checklist

If any of the following appear in a task `title`, rewrite it:

- Class suffixes: `Service`, `Repository`, `Handler`, `Controller`, `Facade`
- Implementation identifiers: `XxxImpl`, `AbstractXxx`, `@Async`, `@Mock`
- File paths or line numbers: `SignalMessageType.java:49`, `api-common/...`
- Constant / signal names: `NOTIFY_ADMIN_ALIMTALK_REQUEST`, `TOPIC_AUTH_ADMIN_ALL`
- Verb-free noun phrases (no action stated)
- Vague verbs alone: "처리", "수행", "진행", "handle", "process"

**Examples:**

| Bad | Good |
|-----|------|
| `SignalMessageType + notifyAlimtalkRequestToAdmin 추가` | `알림톡 요청 신호를 관리자 토픽으로 발송한다` |
| `HospitalAlimTalkRequestFacadeService 발송 배선` | `채널/템플릿 저장 직후 신호를 발송하도록 연결한다` |
| `useSocket.onAdmin NOTIFY_ADMIN_ALIMTALK_REQUEST 핸들러` | `운영팀 화면에 신규 요청 알림을 표시한다` |

---

## Mermaid Diagrams in desc

Use a `sequenceDiagram` in `desc` to show flows that cross the BE/FE boundary
or involve async handoffs. Embed it as a fenced mermaid block string:

```json
"desc": [
  "When a hospital submits a request, an alert fires on the operations screen.",
  "```mermaid\nsequenceDiagram\n  actor 병원 as 병원(front-doctor)\n  participant BE as api-admin FacadeService\n  participant Broker as Signal Broker (STOMP)\n  actor 운영팀 as 운영팀(front-admin)\n  병원->>BE: channel/template registration request\n  BE->>BE: DB save succeeds\n  BE-->>Broker: send alert signal\n  Note right of BE: async — send failure does not roll back the save\n  Broker-->>운영팀: signal received\n  운영팀->>운영팀: show sticky notification (bottom-right)\n  운영팀-->>BE: confirm → review drawer\n```"
]
```

**Role naming rules:**

| Element | Use | Avoid |
|---------|-----|-------|
| `actor` | External users: `병원(front-doctor)`, `운영팀(front-admin)` | User IDs, login names |
| `participant` | Internal systems: `api-admin FacadeService`, `Signal Broker (STOMP)` | `HospitalAlimTalkRequestFacadeService`, `SignalMessageBroker` |
| Labels | Role or service purpose | Class names, constant names |

Use `-->>` for async arrows and `->>` for sync. Add `Note right of X` to
highlight guarantees or exceptional behaviour.

---

## Summary Table

| Question | Where to put it |
|----------|-----------------|
| Why does this task exist? | `desc[0]` — one sentence, user/ops outcome |
| How does it work? | `desc` — Mermaid `sequenceDiagram` |
| What counts as done? | `criteria` — behaviour headline + `→` hint |
| What are the implementation steps? | `subs` — verb + object, one per item |
| What can a user actually do here? | `features` — grouped capability checklist (reviewer/QA) |
| What does this block or depend on? | `deps` |
| Related documents? | `links` |
| Decided against building this? | `status: "dropped"` + `reason` |
