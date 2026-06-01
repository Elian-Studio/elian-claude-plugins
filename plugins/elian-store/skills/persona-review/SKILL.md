---
name: persona-review
description: "When a user asks for code, PR, design, architecture, refactoring, domain model, or test strategy review through expert software quality lenses, inspect the relevant artifacts and report findings through Evans, Dean, Martin, Fowler, and Beck perspectives before making changes."
when_to_use: "Use for code review, PR review, design review, architecture review, DDD review, Clean Code/SOLID review, refactoring review, TDD/test strategy review, performance/scalability/reliability review, or requests such as '다양한 관점에서 봐줘', '페르소나 리뷰해줘', 'evans/dean/martin/fowler/beck 관점으로 리뷰해줘'."
argument-hint: "<target-path-or-text> [--persona evans|dean|martin|fowler|beck|all|comma-list|<path-to-custom>] [--depth quick|deep|interview] [--apply]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git diff*), Bash(git log*), Bash(git status*), Bash(git show*), Bash(git branch*), Agent, AskUserQuestion
---

# /persona-review — Persona Code Review

코드, 설계, 아키텍처, PR, 리팩터링 계획, 도메인 모델링, 테스트 전략을 여러 소프트웨어 품질 관점으로 검토한다. 유명 개발자 이름을 흉내 내는 스킬이 아니라, 각 인물이 대표하는 품질 관점을 **리뷰 렌즈**로 사용한다.

기본은 read-only 리뷰다. 사용자가 명시적으로 "수정해줘", "반영해줘", "패치해줘", "리팩터링해줘"라고 요청하지 않으면 파일을 변경하지 않는다. 수정 요청이 명확하면 리뷰 결과 중 가장 중요하고 안전한 변경부터 작은 단위로 반영한다.

핵심 계약:

- 먼저 리뷰를 작성한다. 수정은 사용자가 명시했거나 수정 의도가 분명할 때만 한다.
- 근거 없는 추측을 하지 않는다. 코드에서 확인한 사실과 추론을 구분한다.
- persona별 점수화를 하지 않는다. `Lens Questions`는 내부 검토 렌즈이고, 출력은 아래 고정 리뷰 리포트 구조를 따른다.
- 모든 built-in persona는 대응 subagent로 실행한다. 메인 스킬이 대신 리뷰하지 않는다.
- 수정한 경우 변경 요약, 검증 결과, 남은 리스크를 보고한다.

## Review Lenses

| Persona | subagent_type | Lens | Strong for |
|---|---|---|---|
| `evans` | `persona-evans-reviewer` | Domain-Driven Design | 도메인 모델, bounded context, aggregate, invariant |
| `dean` | `persona-dean-reviewer` | 대규모 시스템 / 성능 / 신뢰성 | latency, throughput, memory, I/O, concurrency, observability |
| `martin` | `persona-martin-reviewer` | Clean Code / SOLID / 가독성 | 책임 분리, 이름, 의존성 방향, 테스트 가능성 |
| `fowler` | `persona-fowler-reviewer` | 리팩터링 / 엔터프라이즈 아키텍처 / 진화 가능성 | code smell, module boundary, incremental refactoring |
| `beck` | `persona-beck-reviewer` | TDD / XP / 단순 설계 / 빠른 피드백 | test-first, small steps, YAGNI, behavior tests |
| custom path | `persona-custom-reviewer` | custom persona file 기준 | 사용자가 정의한 렌즈 |

Reference files:

- [references/personas/evans.md](references/personas/evans.md)
- [references/personas/dean.md](references/personas/dean.md)
- [references/personas/martin.md](references/personas/martin.md)
- [references/personas/fowler.md](references/personas/fowler.md)
- [references/personas/beck.md](references/personas/beck.md)
- [references/example-review.md](references/example-review.md)

### Lens Questions

`evans`:
- 이 코드는 비즈니스 개념을 정확히 표현하는가?
- 도메인 규칙이 코드의 중심에 있는가, 주변부에 흩어져 있는가?
- 잘못된 bounded context 결합이 있는가?
- 모델 이름과 행위 이름이 실제 도메인 언어와 맞는가?

`dean`:
- 이 코드는 트래픽이 늘어도 견딜 수 있는가?
- latency, throughput, memory, I/O 측면의 위험은 없는가?
- 실패, 재시도, timeout, 중복 처리, race condition을 고려했는가?
- 로그, 메트릭, tracing으로 문제를 추적할 수 있는가?
- 불필요한 동기 처리나 반복 쿼리가 있는가?

`martin`:
- 코드를 읽는 사람이 의도를 바로 이해할 수 있는가?
- 함수나 클래스가 너무 많은 일을 하지 않는가?
- 의존성 방향이 안정적인 정책을 향하는가?
- 구현 세부사항이 핵심 정책을 오염시키지 않는가?
- 테스트하기 어려운 구조가 아닌가?

`fowler`:
- 이 구조는 앞으로 바뀌기 쉬운가?
- 리팩터링을 작은 단계로 안전하게 진행할 수 있는가?
- 패턴을 문제 해결에 쓰는가, 패턴을 위한 패턴인가?
- 변경이 특정 모듈 안에 갇히는가, 여러 계층으로 퍼지는가?
- 지금 가장 먼저 제거해야 할 code smell은 무엇인가?

`beck`:
- 이 코드는 테스트로 행위를 설명할 수 있는가?
- 실패하는 테스트 -> 통과하는 코드 -> 리팩터링 흐름이 가능한가?
- 가장 단순한 설계인가?
- 테스트가 내부 구현이 아니라 관찰 가능한 행위를 검증하는가?
- 변경을 작은 단계로 나누어 안전하게 배포할 수 있는가?

## Modes

| Mode | What it does | Use when |
|---|---|---|
| `quick` (default) | 핵심 파일/diff 기반으로 5개 렌즈 리뷰 | 일반 코드/PR/설계 리뷰 |
| `deep` | 관련 테스트, 타입, API 경계, 설정, README/설계 문서까지 더 넓게 확인 | 아키텍처, 도메인 모델, 성능/신뢰성 리스크가 큰 변경 |
| `interview` | 리뷰 전에 결론을 가르는 질문을 최대 3라운드까지 묻고 재검토 | 목표, 제약, 변경 범위가 불명확한 설계/리팩터링 |

`--persona`는 특정 렌즈만 보고 싶을 때 사용한다. 생략하면 built-in 5개 렌즈를 모두 사용한다. `--apply` 또는 명시적 수정 요청이 있을 때만 패치를 적용한다.

## Standing Rules

- `$ARGUMENTS` 또는 사용자 본문에서 target, `--persona`, `--depth`, `--apply` 의도를 해석한다.
- 환경변수 override는 필요하지 않다. 리뷰 범위는 사용자 요청, 현재 diff, 명시된 파일 경로를 우선한다.
- 자동 결정은 읽기 범위 수집, persona 선택 기본값, 우선순위 정렬까지만 허용한다.
- 사용자 결정은 파일 수정, 광범위한 리팩터링, 공개 API 변경, schema 변경, release 판단에 필요하다.
- evidence가 부족하면 단정하지 말고 "확인 필요"로 남긴다.
- built-in persona 결과를 합칠 때 한 관점의 결론으로 다른 관점의 리스크를 지우지 않는다.

## Manual Decision Gating

| Decision | 자동 처리 | 사용자 확인 필요 |
|---|---|---|
| Review scope | current diff, 언급 파일, 관련 테스트 확인 | 범위가 너무 넓거나 서로 다른 PR 단위가 섞인 경우 |
| Persona selection | `--persona` 없으면 5개 built-in lens 사용 | custom persona 파일 해석이 모호한 경우 |
| Patch application | `--apply` 또는 명시적 수정 요청이 있을 때만 작은 변경 | 수정 요청이 없거나 public API/schema 변경이 필요한 경우 |
| Verification | 가능한 read-only 명령과 관련 테스트 제안 | 느리거나 파괴적이거나 외부 시스템이 필요한 검증 |
| Release judgment | release note에 필요한 영향 정리 | version bump, breaking change, merge 여부 |

## Procedure

`Workflow` 섹션의 순서를 절차로 따른다. `quick`은 핵심 diff 중심, `deep`은 관련 테스트/설정/문서까지 확장, `interview`는 결론을 가르는 질문을 먼저 묻고 멈춘다.

## Workflow

1. 사용자 요청 범위를 파악한다.
2. 관련 파일, 변경사항, 테스트, README, 설계 문서, 타입 정의, API 경계, 설정 파일을 확인한다.
3. 가능하면 `git status`, `git diff`, 관련 테스트/lint/build 설정을 확인한다.
4. 리뷰할 파일이 명확하지 않으면 범위를 다음 순서로 정한다:
   - 현재 변경된 파일
   - 사용자가 언급한 파일
   - PR diff 또는 `git diff`
   - 관련 테스트 파일
   - 관련 도메인/서비스/컨트롤러/인프라 파일
5. 사용자가 명시하지 않은 파일 수정은 하지 않는다.
6. 먼저 고정 출력 포맷으로 리뷰를 작성한다.
7. 사용자가 수정을 요청했거나 요청에 수정 의도가 명확하면, 가장 중요하고 안전한 변경부터 작은 단위로 제안하거나 적용한다.
8. 수정한 경우 변경 요약, 검증 결과, 남은 리스크를 보고한다.

## Subagent Execution Contract

메인 스킬은 lead/router다. built-in persona 요청은 반드시 대응 subagent로 실행한다.

| persona arg | subagent_type |
|---|---|
| `evans` | `persona-evans-reviewer` |
| `dean` | `persona-dean-reviewer` |
| `martin` | `persona-martin-reviewer` |
| `fowler` | `persona-fowler-reviewer` |
| `beck` | `persona-beck-reviewer` |
| 생략 또는 `all` | 위 5개를 실행 |
| `evans,dean` 같은 comma-list | 지정된 subagent만 실행 |
| custom file path | `persona-custom-reviewer`에 custom persona 본문을 포함해 실행 |

각 subagent prompt에는 사용자 의도, target, depth, evidence, 수정 가능 여부를 포함한다. subagent도 read-only로 리뷰해야 하며, 패치 적용 판단은 lead가 한다.

## Output Format

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

## Conflict Handling

다음 충돌이 있으면 명시하고 현실적인 절충안을 제시한다.

- `dean`의 성능 최적화 vs `beck`의 단순 설계
- `martin`의 분리 원칙 vs `fowler`의 과한 추상화 경계
- `evans`의 도메인 순수성 vs 실제 운영/인프라 제약
- `beck`의 작은 단계 접근 vs 대규모 구조 개선 필요성

## Modification Rules

- 기본은 review-only다.
- 수정 요청이 없으면 파일을 변경하지 않는다.
- 수정 요청이 있으면 P0/P1 중 가장 작고 안전한 변경부터 적용한다.
- 수정 전후로 변경 범위와 검증 방법을 분리해서 보고한다.
- 광범위한 리팩터링, 공개 API 변경, schema 변경은 먼저 계획과 리스크를 제시한다.

## Pitfall / Known Issues

- persona 이름만 붙인 일반 리뷰는 실패다. 각 관점의 품질 기준이 실제 finding에 드러나야 한다.
- performance claim은 측정이나 코드 경로 없이 단정하지 않는다.
- DDD claim은 실제 도메인 언어와 경계 근거 없이 단정하지 않는다.
- refactoring 제안은 작은 단계와 검증 방법 없이 rewrite 제안으로 만들지 않는다.
- `--apply`가 있어도 모든 finding을 한 번에 고치지 않는다. 가장 중요한 안전한 변경부터 처리한다.

## BEFORE/AFTER Examples

완성된 BEFORE/AFTER 예시는 [references/example-review.md](references/example-review.md)를 본다. 예시는 출력 템플릿을 그대로 복사하라는 뜻이 아니라, evidence 수집 → persona lens → priority finding → conflict 조정 → verification 제안의 흐름을 보여준다.

## Self-Check

- [ ] target, diff, 관련 테스트/설정/문서를 확인했다.
- [ ] 수정 요청이 없을 때 파일을 변경하지 않았다.
- [ ] 각 persona finding이 실제 evidence 또는 명시적 추론에 기반한다.
- [ ] P0/P1 리스크가 P2/P3 개선 뒤에 묻히지 않았다.
- [ ] 관점 충돌과 검증 제안을 포함했다.

## Where This Fits

이 스킬은 implementation 전 설계 리뷰, PR 리뷰, merge 전 risk review, 리팩터링 계획 검토에 위치한다. 후행 작업은 사용자가 요청할 때만 `implement`, `fix`, `improve`, 또는 직접 패치로 이어진다.

## Reflection

리뷰 후 반복되는 blind spot이 보이면 다음 리뷰에서 먼저 확인할 패턴으로 남긴다. 단, 메모리나 장기 문서 갱신은 사용자가 명시적으로 요청할 때만 수행한다.

## Forbidden

- 사용자 요청 없이 파일 수정
- 근거 없는 추측을 사실처럼 말하기
- persona 이름만 빌리고 실제 품질 관점은 적용하지 않기
- 한 관점의 결론을 다른 관점의 결론으로 덮어쓰기
- P0/P1 리스크를 P2/P3 스타일 이슈 뒤에 숨기기
- 수정 후 검증 결과를 생략하기

## Validation

```bash
python3 plugins/elian-store/skills/persona-review/scripts/validate_skill.py
python3 scripts/score_skill.py plugins/elian-store/skills/persona-review/SKILL.md
```
