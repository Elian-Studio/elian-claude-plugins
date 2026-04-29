# Changelog

이 마켓플레이스에 포함된 모든 플러그인의 주요 변경 사항을 기록합니다.

포맷은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 를 따르고, 버전 체계는 [Semantic Versioning](https://semver.org/spec/v2.0.0.html) 을 따릅니다.

> 마켓플레이스 자체와 각 플러그인은 **독립적인 버전**을 갖습니다. 마켓플레이스 버전은 카탈로그 구조 변경(플러그인 추가/제거/메타데이터)을 추적하고, 플러그인 버전은 해당 플러그인의 기능 변경을 추적합니다.

---

## 마켓플레이스 (`elian`)

### [2.1.0] — 2026-04-29

#### Added
- **`/generate-teammate` 스킬 추가** — Agent Team / Subagent / 직접 실행을 Phase 별로 독립 판정해 최적 전략을 결정하는 팀 생성기. Phase 분해 → 접근법 판정 (★ 적합 / 가능 / 부적합) → 단일 또는 하이브리드 전략 선택 → 팀 / 작업 설계 → 사용자 확인 → 실행 흐름. 공식 문서(Sub-agents, Agent Teams) 의 핵심 판별 질문 ("작업자 간 소통이 필요한가?") 을 1차 기준으로 사용.
- **14 개 도메인 전문 에이전트 정의 번들** — `plugins/elian-store/agents/` 에 self-contained (외부 스킬 의존 0) 로 배포:
  - 엔지니어링 8 개: `frontend-architect` (React / Vue / Angular / Svelte / Solid 멀티 프레임워크), `backend-architect` (Spring Boot / Express / NestJS / Django / FastAPI / Rails / Go / .NET 멀티 스택), `system-architect` (ADR · 도메인 모델), `security-engineer` (OWASP + AI · 클라우드), `performance-engineer` (측정 우선), `quality-engineer` (테스트 피라미드), `devops-architect` (Docker · K8s · Terraform · CI / CD), `requirements-analyst` (PRD · 인수기준)
  - 디자인 / 리서치 / 전략 6 개: `ui-ux-designer` (디자인 토큰 · 컴포넌트 · a11y), `technical-writer` (Diátaxis), `ux-researcher` (인터뷰 · 페르소나 · 저니맵), `marketing-strategist` (포지셔닝 · GTM), `business-analyst` (단위 경제 · ROI · 의사결정 프레임), `devil-advocate` (사전 부검 · 가정 발굴 · 윤리 lens)
- **references/ 디렉토리** — 입력 → Phase 분해 → 판정 → 팀 구성 → spawn prompt 까지 전체 trace 4 개 시나리오 (풀스택 신기능, 가설 경쟁 디버깅, 다관점 PR 리뷰, 비-개발 런치 전략).
- **Documentation Team / Strategy Team 패턴 추가** — Design Team 은 기술 / UX 두 변형으로 확장. 단일 도메인 (스킬 빌더 · 분석가) 위주에서 풀 도메인 카탈로그로.
- 모든 스킬 내부 문서 영어 통일 (마켓플레이스 사용자가 다국적임을 고려).

#### Changed
- 마켓플레이스 / 플러그인 description 업데이트하여 새 스킬 + 에이전트 카탈로그 반영.
- `plugin.json` keywords 에 `agent-team`, `subagent` 추가.

#### Notes
- Agent Teams 는 실험적 기능. 사용 전 `settings.json` 또는 환경 변수에 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 필요. Claude Code v2.1.32 이상.
- 14 에이전트는 `skills:` frontmatter 의존성 없음 — 본 플러그인 단독 설치만으로 동작.

---

### [2.0.1] — 2026-04-28

#### Fixed
- **Skill Quality Gate detection 누수** — 기존 워크플로우의 `git diff --diff-filter=AM` 가 git rename(R) 을 누락. 디렉토리 이동 PR 에서 SKILL.md 변경 0개로 감지되어 평가/코멘트가 모두 스킵되던 문제 (PR #3 사례). `--no-renames` 추가로 rename 을 add+delete 로 분해해 새 경로가 A 로 잡히도록 수정. 향후 경로+콘텐츠 동시 변경 시에도 게이트가 정상 작동.

---

### [2.0.0] — 2026-04-28 ⚠ BREAKING

#### Changed (BREAKING for users)
- **단일 번들 플러그인 모델로 전환** — 기존 `decision-dashboard` 단일 스킬 플러그인을 `elian-store` 번들 플러그인으로 재배치. 다수 스킬을 한 번의 설치로 받고, 새 스킬은 `/plugin update elian-store@elian` 로 자동 반영
- 마이그레이션:
  ```shell
  /plugin uninstall decision-dashboard@elian
  /plugin install elian-store@elian
  ```
- 호출 형식 변경: `/decision-dashboard:decision-dashboard` → `/elian-store:decision-dashboard` (자연어 호출 "결정 대시보드 만들어줘" 는 변동 없음)
- `decision-dashboard` 스킬 자체의 콘텐츠는 변경 없음 — 위치만 `plugins/elian-store/skills/decision-dashboard/` 로 이동

#### 마이그레이션 동기

기존 구조(플러그인=스킬 1:1) 는 새 스킬 추가 시 매번 별도 plugin.json + 마켓플레이스 entry + 사용자 별도 install 을 요구. 단일 번들로 전환하여:

- 사용자 입장: 한 번 설치 → 모든 스킬 자동
- 메인테이너 입장: 새 스킬 = 디렉토리 하나 추가 + plugin.json version bump

향후 추가 예정 스킬: `manage-skills`, `brainstorm`, `commit` 등

---

### [1.2.0] — 2026-04-28

#### Changed (BREAKING for maintainers)
- **Skill Quality Gate 를 LLM 기반에서 stdlib 휴리스틱으로 전환** — `ANTHROPIC_API_KEY` Secret 셋업이 더 이상 필요 없음. 결정적 채점, 비용 0, 외부 의존성 0
- 채점 신호는 결정적 패턴 매칭 (섹션 존재, 길이, 키워드, 디렉토리 구조). 의미적 품질(글의 매끄러움) 은 평가하지 못하지만, 잘 만들어진 스킬은 구조가 갖춰져 있으므로 90점 게이트로는 충분
- 자가 검증: 개선 전 SKILL.md = 54점 (FAIL), 개선 후 SKILL.md = 97점 (PASS) — 게이트가 의도대로 작동

#### Added
- `scripts/score_skill.py` — Python stdlib 휴리스틱 채점기. argparse, `--help`, `--json` 지원. 다중 SKILL.md 동시 채점

#### Removed
- `scripts/evaluate_skill.py` — Anthropic SDK 기반 LLM 평가 스크립트 (휴리스틱으로 대체)
- `scripts/static_checks.sh` — score_skill.py 가 정적 검증을 흡수
- `ANTHROPIC_API_KEY` Secret 의존성 — 워크플로우/README/PR 템플릿에서 모두 제거

#### 향후 LLM 보강 (선택, 미구현)
- 휴리스틱 80~89점 구간에서만 LLM 추가 평가하는 hybrid 모델 가능. 비용 절약 + 의미적 품질 평가 동시 충족. 필요 시 별도 PR

---

### [1.1.0] — 2026-04-28

#### Added
- **PR 기반 워크플로우 + Skill Quality Gate** — 모든 SKILL.md 변경은 PR 을 통과해야 main 에 반영. GitHub Actions 가 자동 실행하고 90점 미만이면 머지 차단
- `scripts/rubric.md` — 100점 만점 평가 루브릭. 공식 Claude Code 가이드 + [garrytan/gstack](https://github.com/garrytan/gstack/blob/main/docs/skills.md) + [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) 의 베스트 프랙티스 종합
- `.github/workflows/skill-quality-gate.yml` — PR 트리거, 변경 SKILL.md 만 평가, 결과 PR 코멘트 자동 게시
- `.github/pull_request_template.md` — 변경 유형/체크리스트 표준화
- `README.md` 의 Contributing 섹션

### [1.0.0] — 2026-04-28

#### Added
- `decision-dashboard` 플러그인 v1.0.0 등록
- 마켓플레이스 메타데이터 (`metadata.pluginRoot = ./plugins`)

---

## elian-store (번들)

### [2.0.0] — 2026-04-28 ⚠ BREAKING

#### Changed
- 신규 번들 플러그인 — `decision-dashboard` 플러그인(v1.0.0) 을 흡수하여 첫 번째 스킬로 포함
- 향후 추가 스킬은 `plugins/elian-store/skills/<name>/` 디렉토리 추가만으로 사용자에게 자동 도달

#### Migration from decision-dashboard@1.0.0
- `/plugin uninstall decision-dashboard@elian` → `/plugin install elian-store@elian`
- 호출: `/decision-dashboard:decision-dashboard` → `/elian-store:decision-dashboard`

---

## decision-dashboard (legacy plugin, 1.0.0 only — superseded by elian-store@2.0.0)

### [1.0.0] — 2026-04-28

첫 공개 릴리즈. 개인 사용 중이던 `~/.claude/skills/decision-dashboard/` 를 플러그인으로 패키징하면서, 마켓플레이스 배포 적합성을 위해 [garrytan/gstack](https://github.com/garrytan/gstack/blob/main/docs/skills.md) + [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) 의 베스트 프랙티스를 종합 적용.

#### Added — 핵심 기능
- 단일 HTML 결정 대시보드 생성 (라디오 선택 + 메모 + MD/JSON 다운로드 + JSON 클립보드 복사)
- 우선순위 색상(P0/P1/P2) + 사이드바 카드 네비게이션
- 카드 본문 LANGUAGE GATE — 카드 본문에 클래스명/테이블명/내부 약어 노출 차단 (개발자 근거는 접이식 상세 패널에 격리)
- "기타 — 직접 입력" 옵션 표준화 — 모든 카드의 마지막 옵션

#### Added — 베스트 프랙티스 적용 (gstack + alirezarezvani)
- **Outcome-focused description** — "When 3+ pending decisions block PO/team progress, capture them in a printable HTML artifact so the team can decide in 5 minutes" (process 가 아닌 outcome 우선). gstack 의 *"Lead with the concrete problem the skill solves, not aspirational framing"*
- **Mode differentiation** — `generate` (첫 생성) / `finalize` (결정 영구화 + 정리) 2개 명시 모드. gstack 의 `/plan-ceo-review` 4모드 패턴 차용
- **Skill sequencing** — "Where this fits in the workflow" 섹션. `brainstorm → design → DECISION-DASHBOARD → implement → review → ship` 의 어느 단계인지 명시
- **Manual decision gating** — "What's automated vs what needs your taste" 표. Claude 자동 결정(우선순위 분류, 라벨 변환, GATE 검사) vs 사용자 결정(A/B/C 선택, 옵션 정의 검토) 명시
- **Persistent artifact for downstream** — `decisions-final.json` 영구 저장 (issue, decisions[], summary, rejected_alternatives 포함). 후행 스킬(`/implement`, `/ship`) 이 컨텍스트로 소비
- **End-of-skill reflection** — finalize 종료 시 결정 패턴 관찰 보고 (3개 항목, hedge 사용). gstack 의 *"specific callbacks, not generic praise"*
- **Three-file minimum** — `references/` 디렉토리 추가:
  - `references/example-good-card.md` — BEFORE/AFTER 카드 비교 + 셀프 체크리스트
  - `references/example-card-snippet.html` — 좋은 카드 1개 HTML fragment (그대로 복사 가능)
- **`scripts/validate-dashboard.py`** — inline bash 검증을 분리. argparse 기반 `--help` + `--json` 출력 지원 (다른 스킬 chaining). stdlib only (zero pip installs). alirezarezvani 의 *"All CLI tools tested with --help and --json flag support"* 표준
- **`argument-hint`** 두 번째/세 번째 인자(output-dir, mode) 반영
- **`${CLAUDE_SKILL_DIR}`** 사용 (플러그인 루트가 아닌 스킬 자신의 경로)
- **Standing Instructions 섹션 격리** — 카드 작성 규칙(LANGUAGE GATE, 배경 3문장, 옵션 라벨, 판단 질문) 을 모드 절차와 분리해 standing instructions 로

#### Changed (개인 버전 대비)
- **출력 경로 일반화** — 기본 `claudedocs/{ISSUE}/decisions-{DATE}.html`. 환경변수 `DECISIONS_DIR` 또는 `$ARGUMENTS` 두 번째 인자로 override 가능
- **이슈 ID 자동 추출** — `git branch --show-current` 에서 `[A-Z]+-[0-9]+` 패턴 매칭 (회사별 이슈 prefix 자동 인식)

#### Fixed (개인 버전 대비)
- **Auto-validation 셸 변수 버그** — 기존 `FILE=claudedocs/{ISSUE}/...` 가 placeholder 를 변수처럼 쓰고 있어 검증이 항상 깨지던 문제 → 실제 셸 변수 + 별도 Python 스크립트로 교체
- **Python heredoc 변수 미치환** — `<<'EOF'` (인용된 heredoc) 안에서 `$FILE` 이 빈 값으로 들어가 LANGUAGE GATE 가 항상 실패하던 문제 → 별도 스크립트 + argparse 로 해결

#### Removed (개인 버전 대비)
- **PENDING.md 아카이브 플로우 전체 제거** — 개인 워크플로우(claudedocs/{ISSUE}/PENDING.md 6블록 결정 카드)에 강하게 결합되어 일반 공유에 부적합. 결정 근거는 `decisions-final.json` 영구 저장 + 커밋 메시지로 대체
- mobidoc 프로젝트 고유 예시(MPT-####, ShedLock 환급 시나리오 등) — 일반 예시(PROJ-123, 푸시 알림 재발송 시나리오) 로 교체

---

## 버전 관리 정책

- **변경 시 반드시 `version` 필드를 bump** 합니다. `plugin.json` 의 `version` 이 그대로면 Claude Code 가 캐시된 사본을 그대로 사용해 사용자에게 업데이트가 도달하지 않습니다.
- 마켓플레이스 카탈로그 구조만 바뀌면 `marketplace.json` 의 `metadata.version` 만 bump.
- 플러그인 내용이 바뀌면 해당 플러그인의 `plugin.json.version` + 마켓플레이스 엔트리의 `version` 을 함께 bump (단, [공식 문서](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels)에 따라 `plugin.json` 값이 우선 — 두 곳에 동시에 두는 것보다 `plugin.json` 만 관리하는 편이 안전).

### SemVer 적용 가이드

| 변경 유형 | 예시 | bump |
|----------|------|------|
| MAJOR (breaking) | placeholder 이름 변경, 출력 디렉토리 디폴트 변경, allowed-tools 축소 | `1.0.0 → 2.0.0` |
| MINOR (feature) | 새 검증 규칙, 새 옵션, 새 카드 타입 | `1.0.0 → 1.1.0` |
| PATCH (fix/docs) | 버그 수정, 문서 보강, 예시 추가 | `1.0.0 → 1.0.1` |
