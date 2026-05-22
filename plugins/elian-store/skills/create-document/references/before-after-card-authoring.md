# BEFORE / AFTER — 결정 카드 1장 작성

같은 결정을 두 방식으로 표현했을 때의 차이.

---

## BEFORE — 기존 decision-dashboard (sed + Edit HTML 직접 작성)

❌ 카드 1장당 ~60 LOC HTML 블록을 사람이 직접 작성. 식별자(`#143`, `CrmReservationEntity`, `user_lock_dtm`)가 그대로 새어들어가는 일이 잦았다.

```html
<div class="card open" id="c1" data-key="c1">
  <div class="card-head" onclick="toggleCard(this)">
    <span class="card-num">1</span>
    <div class="card-head-text">
      <div class="card-title">#143 푸시 발송 실패 시 NotificationRetryScheduler 도입</div>
    </div>
    <span class="card-chevron">▶</span>
  </div>
  <div class="card-body"><div class="card-inner">
    <div class="info-block">
      <div class="info-label">배경</div>
      <div class="info-box box-context">
        notification_send_log 의 status=FAILED 건이 그대로 유실됨. 어제 결제한 7명에게 영수증 안 감.
      </div>
    </div>
    <!-- ... 50 lines more ... -->
  </div></div>
</div>
```

문제:
- `#143`, `NotificationRetryScheduler`, `notification_send_log`, `status=FAILED` 같은 **식별자가 결정자(PO/팀장)에게 그대로 노출**. 5분 안에 A/B 결정 못 함.
- 카드를 한 번 잘못 만들면 ~60 LOC 다시 수정.
- Forbidden 가이드(SKILL.md의 "card-body authoring rules")가 강제되지 않음 — Claude/사람의 자제력에 의존.

---

## AFTER — create-document (JSON + 스키마 검증 + 템플릿 치환)

✅ 같은 카드를 ~20 LOC JSON 으로 작성. 식별자는 스키마의 `forbid` 패턴이 자동으로 차단 (`#[0-9]+`, `[A-Z][a-zA-Z]*Entity`, `[a-z]+_[a-z]+(?:_[a-z]+)+`).

```json
{
  "card_id": "c1",
  "num": 1,
  "open_class": " open",
  "title": "푸시 알림 실패 건 자동 재발송 도입",
  "background": {
    "situation": "어제 결제한 사용자 100명 중 7명에게 영수증 푸시가 발송되지 않았습니다 — 수신자 단말 일시 오류로 추정됩니다.",
    "pain": "지금은 첫 발송이 실패하면 그대로 유실되어 사용자는 결제됐는지 모르고 환불 요청이 옵니다. 어제만 4건 발생.",
    "divergence": "이번 결정으로 '재시도 자동화'와 '운영팀 수동 처리' 중 사용자가 영수증을 받기까지 걸리는 시간이 갈립니다."
  },
  "judgment_question": "사용자가 영수증을 1시간 안에 100% 받아야 할까요, 운영팀이 매일 누락 건을 수동 처리해도 괜찮을까요?",
  "options": [
    {"key": "A", "label": "자동 재발송으로 전환 — 사용자가 1시간 안에 영수증 받음", "rec_badge": "<span class=\"rec-badge\">권고</span>"},
    {"key": "B", "label": "운영팀 수동 처리 유지 — 평균 6시간 대기"},
    {"key": "C", "label": "사용자에게 발송 실패 안내 후 재요청 버튼 노출"}
  ]
}
```

만약 누군가 `#143` 또는 `*.class` 를 넣으면:

```
✗ schema invalid (4 errors):
  cards[0].title: 금지 패턴 '#[0-9]+' 매치 — '#143'
  cards[0].title: 금지 패턴 '[A-Z][a-zA-Z]*Entity' 매치 — 'CrmReservationEntity'
  cards[0].background.situation: 금지 패턴 '[a-z]+_[a-z]+(?:_[a-z]+)+' 매치 — 'notification_send_log'
  cards[0].background.pain: mustMatch 미충족 (적어도 하나 매치 필요: ['[0-9]|놓치|못함|못한|실패|지연'])
exit 1
```

→ HTML 출력 파일은 만들어지지 않는다 (구조적 차단).

---

## 비교 요약

| 축 | BEFORE | AFTER |
|---|---|---|
| 카드 1장 작성량 | ~60 LOC HTML | ~20 LOC JSON |
| 식별자 차단 | 자제력 / 사후 검사 | 스키마가 사전 차단 |
| 잘못 작성 시 재작업 비용 | ~60 LOC 다시 작성 | JSON 일부만 수정 |
| 결정자 시각 (PO/팀장) | 코드 식별자 노출 → 5분 결정 실패 | product-perspective 만 노출 → 5분 결정 가능 |
| end-to-end 시간 추정 | 30~60초 / 대시보드 | 5~10초 / 대시보드 (3~6× 가속) |

핵심: **속도보다 더 큰 가치는 "잘못된 카드가 구조적으로 못 만들어진다"는 점.** 한 번 잘못 만든 카드를 다시 작성하는 비용은 가속률보다 크기 때문.
