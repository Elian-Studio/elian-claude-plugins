# Artifact Structure — 산출물 저장 디렉토리

9 Phase 의 산출물을 일관되게 저장하는 구조. 다음 기능에 재사용하기 쉽도록 *기능별* 디렉토리 + *프롬프트별* 디렉토리로 분리.

---

## 권장 구조

```
docs/
  features/
    <feature-name>/
      feature-framing.md          # Phase 1 산출
      bdd-scenarios.feature        # Phase 2 산출 (Gherkin)
      spec.md                      # Phase 3 산출 (SDD)
      domain-model.md              # Phase 4 산출 (필요 시)
      test-plan.md                 # Phase 5 산출 (AI-TDD)
      context-package.md           # Phase 6 산출
      agent-task.md                # Phase 7 산출 (작업 티켓)
      review-checklist.md          # Phase 8 체크리스트
      prompt-record.md             # Phase 9 SPDD 기록

prompts/
  feature-development/
    master.prompt.md               # 마스터 프롬프트 (이 스킬의 references/master-prompt.md)
    bdd.prompt.md
    sdd.prompt.md
    ddd.prompt.md
    ai-tdd.prompt.md
    context-engineering.prompt.md
    agentic-coding.prompt.md
    review.prompt.md
    spdd-record.prompt.md
```

---

## 파일별 책임

| 파일 | 무엇이 들어가나 | 누가 읽는가 |
|---|---|---|
| `feature-framing.md` | 의도·성공 기준·위험도·예상 엣지 케이스 | PO, 개발자, QA, 보안 담당자 |
| `bdd-scenarios.feature` | Gherkin Given-When-Then | 기획자, QA, 개발자 |
| `spec.md` | API·UI·정책·완료 기준 (SoT) | 개발자, AI, 리뷰어 |
| `domain-model.md` | 도메인 객체·책임·이벤트 | 개발자, 아키텍트 |
| `test-plan.md` | 테스트 매트릭스 + 보호 규칙 | 개발자, AI, QA |
| `context-package.md` | AI 가 봐야 할 파일·규칙·금지 사항 | AI 에이전트 |
| `agent-task.md` | Goal / Scope / OoS / AC / Constraints / Tests | AI 에이전트, 리뷰어 |
| `review-checklist.md` | 리뷰 12 관점 결과 | 리뷰어, 머지 결정자 |
| `prompt-record.md` | 사용 프롬프트 + 가정 + 판단 근거 | 다음 기능 개발자 (자산) |

---

## 환경변수 오버라이드

기본 디렉토리는 `docs/features/<feature>/` 와 `prompts/feature-development/`. 환경변수로 변경:

```bash
export AAFD_ARTIFACT_DIR="docs/specs/<feature>/"           # 산출물 디렉토리
export AAFD_PROMPT_DIR="prompts/aaf/"                       # 프롬프트 디렉토리
```

또는 `--artifact-dir` 인자로 호출 시 1회 오버라이드.

---

## 명명 규칙

- `<feature-name>` 은 **kebab-case** (예: `email-password-login`, `order-cancel`, `file-upload`).
- 한국어 기능명은 영문 슬러그로 변환: `이메일 로그인` → `email-login`.
- Phase 0 (Feature Framing) 단계에서 슬러그를 확정하고 이후 일관 사용.

---

## 다중 기능 동시 작업 시

작은 기능들을 같이 작업하면 디렉토리는 분리하되 SPDD 기록을 합치는 게 유용:

```
docs/features/
  login/
    ... (9 산출물)
  signup/
    ... (9 산출물)
  password-reset/
    ... (9 산출물)

docs/features/_auth-bundle/
  combined-prompt-record.md     # 세 기능 통합 SPDD (재사용 패턴)
```

---

## 자산화 원칙

- **명세는 git tracked**: `docs/features/**` 는 commit.
- **프롬프트도 git tracked**: `prompts/**` 는 commit. 다음 작업자가 재사용 가능.
- **민감 정보 절대 금지**: 비밀번호·실제 사용자 데이터·내부 키 등은 산출물에 안 들어감.
- **변경 이력**: 명세 변경은 별도 commit으로 추적, PR 에서 명세 ↔ 코드 diff 비교.

---

## 다른 스킬과의 연계

- `/persona-review` 는 `docs/features/<feature>/spec.md` 를 입력으로 받아 5블록 압박 리뷰 가능.
- `/decision-dashboard` 는 `feature-framing.md` 의 결정 항목을 카드로 변환 가능.
- `/implement` / `/fix` / `/improve` 는 `agent-task.md` 를 입력으로 받아 실제 구현.
- `/document-release` 는 SPDD 기록을 release notes 입력으로 활용.
