# Changelog

이 마켓플레이스에 포함된 모든 플러그인의 주요 변경 사항을 기록합니다.

포맷은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 를 따르고, 버전 체계는 [Semantic Versioning](https://semver.org/spec/v2.0.0.html) 을 따릅니다.

> 마켓플레이스 자체와 각 플러그인은 **독립적인 버전**을 갖습니다. 마켓플레이스 버전은 카탈로그 구조 변경(플러그인 추가/제거/메타데이터)을 추적하고, 플러그인 버전은 해당 플러그인의 기능 변경을 추적합니다.

---

## 마켓플레이스 (`elian`)

### [1.1.0] — 2026-04-28

#### Added
- **PR 기반 워크플로우 + Skill Quality Gate** — 모든 SKILL.md 변경은 PR 을 통과해야 main 에 반영. GitHub Actions 가 정적 검증 + LLM 평가(claude-sonnet-4-6) 를 자동 실행하고 90점 미만이면 머지 차단
- `scripts/rubric.md` — 100점 만점 평가 루브릭. 공식 Claude Code 가이드 + [garrytan/gstack](https://github.com/garrytan/gstack/blob/main/docs/skills.md) + [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) 의 베스트 프랙티스 종합
- `scripts/static_checks.sh` — frontmatter, 길이, 중첩 주석, 위험 권한 패턴 등 결정적 정적 검증
- `scripts/evaluate_skill.py` — Anthropic SDK 기반 LLM 평가. tool_use 강제 JSON, 프롬프트 캐싱
- `.github/workflows/skill-quality-gate.yml` — PR 트리거, 변경 SKILL.md 만 평가, 결과 PR 코멘트 자동 게시
- `.github/pull_request_template.md` — 변경 유형/체크리스트 표준화
- `README.md` 의 Contributing 섹션 — 로컬 검증/브랜치 보호 설정 명령

### [1.0.0] — 2026-04-28

#### Added
- `decision-dashboard` 플러그인 v1.0.0 등록
- 마켓플레이스 메타데이터 (`metadata.pluginRoot = ./plugins`)

---

## decision-dashboard

### [1.0.0] — 2026-04-28

첫 공개 릴리즈. 개인 사용 중이던 `~/.claude/skills/decision-dashboard/` 를 플러그인으로 패키징.

#### Added
- 단일 HTML 결정 대시보드 생성 (라디오 선택 + 메모 + MD/JSON 다운로드 + JSON 클립보드 복사)
- 우선순위 색상(P0/P1/P2) + 사이드바 카드 네비게이션
- 카드 본문 LANGUAGE GATE — 카드 본문에 클래스명/테이블명/내부 약어 노출 차단 (개발자 근거는 접이식 상세 패널에 격리)
- 자동 검증 체크리스트 — 미해결 placeholder, 중첩 주석, nav-link/카드 ID 매칭, LANGUAGE GATE 통과 검사
- "기타 — 직접 입력" 옵션 표준화 — 모든 카드의 마지막 옵션
- 결정 반영 후 HTML 자동 정리 규칙 (Cleanup after decision)

#### Changed (개인 버전 대비)
- **출력 경로 일반화**: 기본 `claudedocs/{ISSUE}/decisions-{DATE}.html`. 환경변수 `DECISIONS_DIR` 또는 `$ARGUMENTS` 두 번째 인자로 override 가능
- **이슈 ID 자동 추출**: `git branch --show-current` 에서 `[A-Z]+-[0-9]+` 패턴 매칭 (회사별 이슈 prefix 자동 인식)
- **`${CLAUDE_PLUGIN_ROOT}` 사용**: template.html 경로를 플러그인 루트 환경변수로 참조 (cache 디렉토리 호환)

#### Fixed (개인 버전 대비)
- **Auto-validation 셸 변수 버그**: 기존 `FILE=claudedocs/{ISSUE}/...` 가 placeholder를 변수처럼 쓰고 있어 검증이 항상 깨지던 문제 → 실제 셸 변수로 교체
- **Python heredoc 변수 미치환**: `<<'EOF'` (인용된 heredoc) 안에서 `$FILE` 이 빈 값으로 들어가 LANGUAGE GATE 가 항상 실패하던 문제 → `python3 - "$FILE" <<'PYEOF'` 로 인자 전달 방식 변경

#### Removed (개인 버전 대비)
- **PENDING.md 아카이브 플로우 전체 제거** — 개인 워크플로우(claudedocs/{ISSUE}/PENDING.md 6블록 결정 카드)에 강하게 결합되어 일반 공유에 부적합. 결정 근거는 커밋 메시지에 한 줄 남기는 방식으로 대체
- mobidoc 프로젝트 고유 예시(MPT-####, ShedLock 환급 시나리오 등) — 일반 예시(PROJ-123, OrderRefundScheduler) 로 교체

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
