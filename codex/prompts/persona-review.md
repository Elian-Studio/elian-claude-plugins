# /persona-review — Persona Code Review (Codex 포팅)

> `~/.codex/prompts/persona-review.md` 로 설치하면 Codex TUI에서 `/persona-review <target> [--persona evans|dean|martin|fowler|beck|all|comma-list|<path>] [--depth quick|deep|interview] [--apply]` 로 호출된다. 인자는 `$ARGUMENTS` 로 들어온다.
>
> 이 파일은 `plugins/elian-store/skills/persona-review/SKILL.md` 의 Codex 네이티브 포팅이지만, `codex/` 독립 트리라서 Claude skill 변경 시 수동 동기화가 필요하다. Claude `Agent`/`AskUserQuestion` 도구가 Codex에는 없으므로, subagent dispatch는 prompt 안에서 5개 렌즈를 직접 적용하고, 질문 단계는 평문으로 질문한 뒤 그 턴에서 멈춘다. Codex 권한, sandbox, approval 기본값은 `~/.codex/config.toml` 책임이다.

`$ARGUMENTS` = `<target-path-or-text> [--persona evans|dean|martin|fowler|beck|all|comma-list|<path>] [--depth quick|deep|interview] [--apply]`

---

## 무엇을 하는가

코드, 설계, 아키텍처, PR, 리팩터링 계획, 도메인 모델링, 테스트 전략을 여러 소프트웨어 품질 관점으로 검토한다. 유명 개발자 이름을 흉내 내는 것이 아니라 각 인물이 대표하는 품질 관점을 리뷰 렌즈로 사용한다.

기본은 review-only다. 사용자가 명시적으로 "수정해줘", "반영해줘", "패치해줘", "리팩터링해줘" 또는 `--apply`를 요청하지 않으면 파일을 변경하지 않는다. 수정 요청이 명확하면 리뷰 결과 중 가장 중요하고 안전한 변경부터 작은 단위로 반영한다.

## 렌즈

| Persona | Lens | Strong for |
|---|---|---|
| `evans` | Domain-Driven Design | 도메인 모델, bounded context, aggregate, invariant |
| `dean` | 대규모 시스템 / 성능 / 신뢰성 | latency, throughput, memory, I/O, concurrency, observability |
| `martin` | Clean Code / SOLID / 가독성 | 책임 분리, 이름, 의존성 방향, 테스트 가능성 |
| `fowler` | 리팩터링 / 엔터프라이즈 아키텍처 / 진화 가능성 | code smell, module boundary, incremental refactoring |
| `beck` | TDD / XP / 단순 설계 / 빠른 피드백 | test-first, small steps, YAGNI, behavior tests |

## 절차

```
Phase 0: Scope 파악
Phase 1: Target 수집 + 관련 근거 확인
Phase 2: Persona lens 선택
Phase 3: 5개 관점 또는 지정 관점으로 리뷰
Phase 4: 고정 출력 포맷 작성
Phase 4.5: interview 수렴 루프 (--depth interview)
Phase 5: 명시적 수정 요청이 있을 때만 작은 패치 적용
```

### Phase 0 — Scope 파악

요청이 코드 리뷰, PR 리뷰, 설계 리뷰, 아키텍처 리뷰, DDD/클린코드/리팩터링/TDD/성능/확장성 검토인지 확인한다.

리뷰할 파일이 명확하지 않으면 다음 우선순위로 범위를 정한다.

1. 현재 변경된 파일
2. 사용자가 언급한 파일
3. PR diff 또는 `git diff`
4. 관련 테스트 파일
5. 관련 도메인/서비스/컨트롤러/인프라 파일

### Phase 1 — Target 수집

관련 파일, 변경사항, 테스트, README, 설계 문서, 타입 정의, API 경계, 설정 파일을 확인한다. 가능하면 `git status`, `git diff`, 관련 테스트/lint/build 설정을 확인한다.

URL이나 원격 PR이 필요한 경우 외부 페치해도 되는지 묻고 멈춘다.

### Phase 2 — Persona 선택

`--persona`가 없거나 `all`이면 5개 렌즈를 모두 사용한다. `evans,dean` 같은 comma-list면 지정된 렌즈만 적용한다. 경로면 custom persona 파일을 읽는다.

### Phase 3 — 리뷰 원칙

- 근거 없는 추측 금지. 코드에서 확인한 사실과 추론을 구분한다.
- persona별 점수화를 하지 않는다.
- 먼저 리뷰를 작성한다.
- 사용자가 명시하지 않은 파일 수정은 하지 않는다.
- 수정 요청이 명확하면 P0/P1 중 가장 작고 안전한 변경부터 적용한다.

### Phase 4.5 — 수렴 루프 (`--depth interview`)

입력 의도, 변경 범위, 성공 기준이 모호하면 결론을 가르는 질문 1개만 묻고 멈춘다. 최대 3라운드까지 반복한다.

### Phase 5 — 수정

`--apply` 또는 명시적 수정 요청이 있을 때만 수정한다. 수정한 경우 변경 요약, 검증 결과, 남은 리스크를 보고한다.

## 출력 포맷

항상 아래 구조로 답한다. 해당 관점에서 발견 사항이 없으면 "특이 사항 없음"이라고 쓴다.

```text
# Persona Code Review

## 1. 전체 평가

- 결론:
- 가장 큰 리스크:
- 가장 먼저 고칠 것:
- 수정 여부:
  - 리뷰만 수행했는지
  - 패치를 적용했는지
  - 패치를 적용하지 않았다면 이유

## 2. 핵심 발견 사항

| 우선순위 | 관점 | 문제 | 영향 | 추천 조치 |
|---|---|---|---|---|
| P0/P1/P2/P3 | evans/dean/martin/fowler/beck | ... | ... | ... |

우선순위 기준:

- P0: 즉시 수정해야 하는 correctness, security, data loss, production outage 위험
- P1: 릴리스 전 수정해야 하는 설계, 성능, 안정성, 테스트 리스크
- P2: 유지보수성, 리팩터링, 가독성 개선
- P3: 선택적 개선 또는 장기 개선

## 3. 페르소나별 리뷰

### `evans` — DDD/도메인 모델

- 좋은 점:
- 문제:
- 개선 제안:
- 확인하면 좋은 질문:

### `dean` — 성능/확장성/신뢰성

- 좋은 점:
- 문제:
- 개선 제안:
- 확인하면 좋은 질문:

### `martin` — Clean Code/SOLID

- 좋은 점:
- 문제:
- 개선 제안:
- 확인하면 좋은 질문:

### `fowler` — 리팩터링/아키텍처 진화

- 좋은 점:
- 문제:
- 개선 제안:
- 확인하면 좋은 질문:

### `beck` — TDD/단순 설계/피드백

- 좋은 점:
- 문제:
- 개선 제안:
- 확인하면 좋은 질문:

## 4. 관점 간 충돌과 조정

- 충돌:
- 현실적인 절충안:

## 5. 추천 액션 플랜

- 목표:
- 이유:
- 예상 변경 범위:
- 검증 방법:
- 리스크:

## 6. 테스트 및 검증 제안

- 추가해야 할 테스트:
- 수정해야 할 테스트:
- 실행하면 좋은 명령:
- 수동 검증 포인트:

## 7. 최종 요약

- 지금 반드시 고칠 것:
- 나중에 개선해도 되는 것:
- 설계적으로 가장 중요한 판단:
```

## 금지

- 사용자 요청 없이 파일 수정
- 근거 없는 추측을 사실처럼 말하기
- persona 이름만 빌리고 실제 품질 관점은 적용하지 않기
- 한 관점의 결론을 다른 관점의 결론으로 덮어쓰기
- P0/P1 리스크를 P2/P3 스타일 이슈 뒤에 숨기기
- 수정 후 검증 결과 생략
