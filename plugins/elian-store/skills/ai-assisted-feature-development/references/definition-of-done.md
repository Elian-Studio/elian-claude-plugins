# Definition of Done + 병합 차단 조건

이 스킬을 통해 만든 기능이 통과해야 할 기준과 PR 머지 차단 조건.

---

## Definition of Done

기능이 "완료" 라고 선언되려면 아래 11 항목 모두 통과해야 한다.

```text
[ ] 기능의 의도와 성공 기준이 명확하다.
[ ] BDD 시나리오가 작성되어 있다.
[ ] 기능 명세가 작성되어 있다.
[ ] 도메인 복잡도에 따라 DDD 적용 여부가 판단되어 있다.
[ ] 테스트 계획이 구현 전에 작성되어 있다.
[ ] AI에게 제공할 컨텍스트가 선별되어 있다.
[ ] AI 구현 지시문이 작업 티켓 또는 PR 단위로 작성되어 있다.
[ ] 구현 결과가 명세와 비교되어 리뷰되었다.
[ ] 보안, 권한, 개인정보, 성능, 접근성 위험이 검토되었다.
[ ] 테스트가 통과했다.
[ ] 사용한 프롬프트와 판단 근거가 기록되었다.
```

위험도(LOW/MEDIUM/HIGH)에 따라 일부 항목은 *간소화* 가능:

| 항목 | LOW | MEDIUM | HIGH |
|---|---|---|---|
| 의도·성공 기준 | 필수 | 필수 | 필수 |
| BDD 시나리오 | 생략 가능 | 권장 | 필수 |
| 기능 명세 | 간단 (1 페이지) | 필수 | 필수 (full SDD) |
| DDD 판단 | "skip" 으로 명시 | 판단 후 결정 | 필수 적용 |
| 테스트 계획 (구현 전) | 권장 | 필수 | 필수 |
| 컨텍스트 패키지 | 권장 | 필수 | 필수 |
| AI 작업 티켓 | 권장 | 필수 | 필수 |
| 명세 대비 리뷰 | 권장 | 필수 | 필수 |
| 보안/권한/개인정보/성능/접근성 검토 | 해당 항목만 | 해당 항목 + 보안 | 전체 + Security Review |
| 테스트 통과 | 필수 | 필수 | 필수 |
| 프롬프트 기록 (SPDD) | 권장 | 필수 | 필수 |

---

## 병합 차단 조건

아래 조건 중 *하나라도* 발견되면 PR 을 머지하지 않는다.

```text
[ ] 명세와 다른 동작이 있다.
[ ] 핵심 BDD 시나리오를 만족하지 않는다.
[ ] 실패 케이스 테스트가 없다.
[ ] AI가 테스트를 약화하거나 삭제했다.
[ ] 보안 또는 권한 정책이 불명확하다.
[ ] 개인정보가 로그에 노출될 가능성이 있다.
[ ] 기존 아키텍처를 불필요하게 깨뜨렸다.
[ ] 기능 범위를 벗어난 변경이 많다.
[ ] 리뷰어가 이해하기 어려운 대규모 변경이 있다.
[ ] 성능 또는 접근성 영향이 검토되지 않았다.
```

### 차단 조건 상세

| 조건 | 무엇을 본다 | 어떻게 catch |
|---|---|---|
| 명세 ↔ 동작 불일치 | spec.md vs 실제 응답/상태 | Phase 8 Review 1번 항목 |
| BDD 미충족 | bdd-scenarios.feature vs E2E 테스트 결과 | Phase 8 Review 2번 항목 |
| 실패 케이스 테스트 부재 | test-plan.md vs 실제 테스트 파일 | Phase 5 AI-TDD 매트릭스 카운트 |
| AI 가 테스트 약화 | test-plan.md 의 *보호 규칙* 위반 | git diff 검사 + Phase 5 보호 규칙 자동 점검 |
| 보안/권한 정책 불명확 | spec.md "Security Requirements" 섹션 부재 | Phase 3 SDD validator |
| 개인정보 로그 노출 | 로그에 비밀번호·세션 ID·토큰·OTP 검색 | Phase 8 Review 6번 항목 + grep |
| 아키텍처 파괴 | context-package.md 의 "변경 금지 사항" 위반 | Phase 6 Context vs diff |
| 범위 초과 | agent-task.md 의 "Out of Scope" 위반 | Phase 7 vs diff 파일 목록 |
| 리뷰 불가능한 큰 PR | PR diff size, 영향받는 파일 수 | Phase 7 단위로 PR 작게 |
| 성능/접근성 미검토 | Phase 8 Review 7-8번 항목 누락 | Review 체크리스트 |

---

## 차단 발견 시 액션

1. **PR comment 로 차단 사유 명시** — 어느 조건, 어떤 증거.
2. **사용자가 수정** — 다음 중 하나:
   - 명세를 갱신 (변경 의도였다면)
   - 코드를 명세에 맞춤 (코드가 명세 위반이면)
   - DoD 항목을 보강 (테스트 추가, 검토 수행)
3. **재리뷰** — Phase 8 Review 다시 실행.
4. **반복 차단되면 Phase 1 (Framing) 으로 회귀** — 의도 자체가 흔들리고 있다는 신호.

---

## "예외 통과" 정책

DoD 항목을 *의도적으로* skip 하려면:

```text
SPDD 기록 (prompt-record.md) 에 다음을 적는다:
- 어느 DoD 항목을 skip 했는가
- 왜 (위험도 / 시간 / 리소스 / 기존 정책)
- 어떤 후속 조치를 약속하는가 (다음 PR 에서 추가, 별도 TODO 등)
```

이 기록 없이 skip 하면 다음 기능 개발에서 같은 패턴이 반복된다 — 그게 안티패턴.

---

## 빠른 self-check

머지 직전 한 줄로 검증:

```bash
# 1. 명세 존재
[ -f docs/features/<feature>/spec.md ]

# 2. 테스트 계획이 구현 commit 이전
git log --diff-filter=A --name-only docs/features/<feature>/test-plan.md  # 추가 commit
git log --diff-filter=A --name-only src/<feature-impl>/...                 # 구현 commit
# test-plan commit time < impl commit time 인지 확인

# 3. SPDD 기록 존재
[ -f docs/features/<feature>/prompt-record.md ]
```

세 조건 모두 ✓ 면 *최소* DoD 충족.
