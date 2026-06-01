# Example: /persona-review 자유 형식 사례

이 파일은 출력 고정 템플릿이 아니다. 같은 대상을 보더라도 페르소나마다 무엇을 먼저 보고, 어떤 형식으로 압박하는지가 달라야 한다.

금지되는 방향:

- 모든 페르소나가 같은 5개 섹션으로 답함
- `Pressure Questions`를 전부 표로 펼쳐 점수화함
- 확인되지 않은 내용을 추측으로 채움

권장되는 방향:

- 페르소나가 가장 중요하게 보는 판단부터 시작
- 필요한 경우에만 표·목록·다이어그램 사용
- 마지막에 다음 질문 또는 다음 액션 1개를 남김

---

## Example 1 — Daniel: 운영 가능성 리뷰

### BEFORE

```markdown
# 결제 플로우

사용자가 결제 버튼을 누르면 백엔드가 PG사 API를 호출한다.
PG사가 200을 주면 주문 상태를 PAID로 바꾸고 알림톡을 보낸다.

## Sequence
1. FE: POST /orders/{id}/pay
2. BE: PG사 결제 요청 (sync)
3. PG사: 결제 승인
4. BE: order.status = PAID
5. BE: 알림톡 발송
6. FE: 완료 화면

운영자는 매일 아침 결제 실패 로그를 확인한다.
```

### 호출

```bash
/persona-review docs/architecture/payment-flow.md --persona daniel
```

### AFTER

```markdown
이 문서는 성공 경로 설명이지 운영 설계가 아님.

가장 먼저 잠글 건 sync/async가 아니라 "실패를 어떤 상태로 남길 것인가"야. 지금은 PG timeout, 승인 성공 후 DB update 실패, 알림톡 실패가 모두 같은 빈칸으로 남아 있음. "운영자가 매일 아침 로그 확인"도 시스템 설계가 아니라 기억 의존 프로세스라 부패한다.

운영 관점에서 바로 깨지는 지점:

| 지점 | 지금 문서 | 필요한 결정 |
|---|---|---|
| PG timeout | 없음 | 결제 요청 상태를 `REQUESTED`/`UNKNOWN`으로 남길지, 즉시 실패 처리할지 |
| 승인 후 DB 실패 | 없음 | PG 승인 조회 reconciliation이 있는지 |
| 알림톡 실패 | 결제 플로우 안에 섞임 | 결제 성공과 알림 발송을 같은 성공 조건으로 볼지 |
| 로그 확인 | 사람이 매일 확인 | 실패 상태 dashboard/alert로 자동화 |

이 설계는 "돌아간다" 수준에서는 충분할 수 있지만 "신뢰할 수 있다" 수준은 아님. 실패 상태 모델과 재처리 경로가 없으면 장애 때 주문/결제 상태를 수동 추측하게 된다.

다음 질문: PG 승인 성공 후 우리 DB 업데이트가 실패하면, 고객에게는 결제가 된 상태인데 주문은 어떤 상태로 남겨야 해?
```

---

## Example 2 — Evans: 도메인 모델 리뷰

### BEFORE

```markdown
UserService가 User, Patient, Reservation 정보를 모두 받아 NoShowScore를 계산한다.
점수가 높으면 CRM 메시지 대상자로 분류한다.
```

### 호출

```bash
/persona-review "UserService가 User, Patient, Reservation 정보를 모두 받아 NoShowScore를 계산한다..." --persona evans
```

### AFTER

```markdown
여기서 제일 이상한 이름은 `UserService`야. 도메인 이야기는 "노쇼 위험 환자 선별"인데 모델 이름은 generic user로 시작한다. 이건 코드가 도메인 언어를 따라가지 못하고 있다는 신호다.

모델을 이렇게 다시 물어봐야 함:

```text
CRM Context
  Patient
  ReservationHistory
  NoShowRiskAssessment
  CampaignAudienceCandidate
```

`NoShowScore`가 값인지, 평가 행위인지, 캠페인 대상 선정의 중간 결과인지도 아직 섞여 있다. 도메인 전문가가 "점수"라고 말하는지 "위험도"라고 말하는지 확인해야 한다. 두 말이 다르면 코드 이름도 달라져야 한다.

bounded context 경계도 불명확하다. 예약 이력은 Reservation context의 사실이고, CRM은 그 사실을 가져와 대상자를 선별한다. CRM이 Reservation 내부 모델을 직접 들고 계산하면 context leak이다. 필요한 건 `ReservationHistorySnapshot` 같은 anti-corruption layer일 가능성이 높다.

다음 질문: 도메인 전문가가 실제로 쓰는 말은 "노쇼 점수"야, "노쇼 위험도"야, 아니면 "재방문 유도 대상"이야?
```

---

## Example 3 — Dean: 분산·스케일 리뷰

### BEFORE

```markdown
예약 리마인더 배치는 매일 09:00에 모든 예약자를 조회하고,
대상자마다 알림톡 API를 동기로 호출한다.
실패하면 즉시 3번 재시도한다.
```

### 호출

```bash
/persona-review docs/reminder-batch.md --persona dean --depth deep
```

### AFTER

```markdown
이 설계의 병목은 DB 조회가 아니라 동기 외부 호출 fan-out이다.

대상자가 10만 명이고 알림톡 API p99가 800ms면, 단일 worker가 순차 호출하는 순간 배치 시간은 시간 단위로 늘어난다. 병렬화해도 즉시 3회 retry가 붙으면 실패 시점에 외부 API와 우리 worker를 같이 두들긴다. retry budget과 backpressure가 먼저 필요하다.

fault model:

| Failure | 지금 설계의 반응 | 필요한 완충 |
|---|---|---|
| 알림톡 API 5xx | 즉시 3회 재시도 | exponential backoff + jitter |
| API latency 상승 | worker thread 점유 | queue + concurrency limit |
| 특정 병원 예약자 폭증 | hot partition 가능 | hospital/date 단위 shard 또는 rate limit |
| 일부 발송 성공 후 배치 중단 | 중복 발송 위험 | idempotency key |

측정 없이 "매일 09:00 전체 조회"를 정하면 09:00 정각의 트래픽 스파이크가 설계에 박힌다. 분산해서 보내도 되는 메시지라면 scheduling jitter를 넣는 게 더 자연스럽다.

다음 질문: 발송 지연 허용치는 몇 분이야? 09:00 정각 보장이 axiom인지, 09:00~09:30 안에 도착하면 되는 policy인지가 설계를 가른다.
```

---

## Example 4 — Martin: 코드 품질 리뷰

### BEFORE

```ts
function saveUser(data, force, notify, retryCount) {
  validate(data)
  if (force) {
    // ...
  }
  save(data)
  if (notify) sendNotification(data)
  if (retryCount > 0) retry(data, retryCount)
}
```

### 호출

```bash
/persona-review src/user/saveUser.ts --persona martin
```

### AFTER

```markdown
`saveUser`는 이름보다 많은 일을 한다.

문제는 줄 수가 아니라 변경 이유다. validation, forced save policy, persistence, notification, retry가 한 함수에 묶여 있다. `force`, `notify`, `retryCount`도 호출자가 함수 내부 시나리오를 알아야 한다는 냄새다.

먼저 쪼갤 경계:

```ts
saveUser(command)
saveUserIgnoringConflicts(command)
notifyUserSaved(user)
retrySaveUser(command, policy)
```

`force`와 `notify`는 boolean parameter라서 함수 의미를 숨긴다. 테스트도 조합 폭발이 난다. `force=true, notify=false, retryCount=3`이 실제 비즈니스 케이스인지, 우연히 생긴 플래그 조합인지 알 수 없다.

테스트 관점에서 첫 실패 테스트는 "notify 실패가 save 성공을 되돌리지 않는다" 같은 정책이어야 한다. 그 정책이 없다면 이 함수는 구현보다 요구사항이 먼저 더럽다.

다음 질문: notification 실패는 사용자 저장 실패로 취급해야 해, 아니면 별도 후속 작업으로 남겨야 해?
```

---

## Example 5 — `--depth interview`

### BEFORE

```markdown
백오피스 STAFF에게 정산 메뉴를 숨긴다. 프론트에서 역할에 따라 메뉴/버튼을 조건부 렌더링한다.
```

### 호출

```bash
/persona-review docs/backoffice-auth.md --persona daniel --depth interview
```

### R1

```markdown
(interview R1/3)

이건 UI 표시 제어인지 권한 시행인지 먼저 갈라야 함.

프론트에서 메뉴를 숨기는 건 UX고, 보안 경계가 아니다. 정산 API가 서버에서 STAFF를 막는다면 이 문서는 "화면 노출 정책" 문서로 보강하면 된다. 서버 인가가 없다면 이건 권한 설계 결함이다.

결론을 가르는 질문 하나: 정산 같은 민감 엔드포인트에 백엔드 역할 검증이 이미 있어?
```

사용자 답변:

```text
없음. 프론트 숨김만 있음.
```

### R2

```markdown
(interview R2/3)

현재안은 보안 결함이다.

STAFF가 메뉴를 못 보는 것과 `GET /settlements`를 직접 호출하지 못하는 건 다른 문제다. 지금 답변 기준으로는 후자가 막혀 있지 않다. 정산은 민감 데이터라서 "프론트 숨김만"은 policy가 아니라 금지해야 할 상태다.

이번 결정에서 협상 불가능한 것:

- 민감 엔드포인트는 백엔드에서 role을 검증한다.
- 인가 실패는 서버 로그에 남긴다.
- 프론트 메뉴 숨김은 UX 보조로만 둔다.

개선 handoff:

```markdown
(handoff → fix docs/backoffice-auth.md)
- persona: daniel
- judgment: FE-only role hiding is not authorization.
- change intent: add backend authorization requirement for settlement endpoints.
- evidence: user confirmed no server-side role check exists.
- risks to preserve: direct API access, audit logging, endpoint coverage.
- out of scope: redesigning the whole RBAC model.
```
```
