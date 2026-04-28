# Skill Quality Rubric (100점 만점)

이 루브릭은 다음 세 레퍼런스를 종합한다:
1. [Claude Code 공식 Skills 가이드](https://code.claude.com/docs/en/skills)
2. [garrytan/gstack — docs/skills.md](https://github.com/garrytan/gstack/blob/main/docs/skills.md) (실전 운영 사례)
3. [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (235 스킬 마켓플레이스 패턴)

마켓플레이스 병합 게이트는 **총점 90점 이상**을 요구한다. 10개 축 × 각 10점.
평가자(LLM)는 각 축마다 0~10 정수 점수와 한 줄 사유, 구체적 개선 제안을 출력해야 한다.

---

## 1. Frontmatter 규약 준수 (10점)

YAML frontmatter 가 공식 스키마를 따르는가.

- `name` — kebab-case, 64자 이내, 디렉토리명과 일치
- `description` — 권장. 없으면 첫 단락 사용됨
- `argument-hint` — 인자 받는 스킬은 명시
- `allowed-tools` — 필요한 툴만 명시 (와일드카드 남발 금지)
- 옵션 필드(`when_to_use`, `disable-model-invocation`, `paths`, `model`, `effort`)는 용도에 맞으면 가점

**감점 예시**: `name` kebab-case 위반 (-2), 64자 초과 (-2), 존재하지 않는 필드 (-1).

## 2. Description 품질 — 자동 호출 신뢰성 (10점)

`description` + `when_to_use` 가 Claude 의 auto-invocation 을 신뢰성 있게 유도하는가.

**공식 가이드**: "Front-load the key use case — the combined description and when_to_use text is truncated at 1,536 characters."

**gstack 인용**: *"Descriptions must be specific enough to auto-invoke reliably. Avoid generic introductory text. Lead with the concrete problem the skill solves, not aspirational framing."*

**alirezarezvani 인용**: *"Descriptions are outcome-focused rather than process-focused."* — "무엇을 만들지" 가 아니라 **"사용자가 무엇을 얻는지"** 로 서술.

평가 기준:
- ❌ Bad: "Generate an interactive HTML decision dashboard..." (출력물 중심)
- ✅ Good: "When 3+ pending decisions block progress, help PO/team decide in 5 minutes via..." (상황+성과 중심)
- 트리거 문구가 `when_to_use` 에 포함 (사용자가 자연스럽게 말할 표현)
- 1,536자 캡 안에서 핵심 키워드 선두 배치
- 좁은 범위 (narrow scope) — gstack: *"Skills should have narrow, defensible scope. /plan-ceo-review explicitly rejects sprawling ideation."*
- 명시 호출 의도면 `disable-model-invocation: true` 와 일관성

**감점 예시**: 출력 형식 중심 서술 (-2), 트리거 문구 부재 (-3), "wouldn't it be cool" 식 일반화 (-2), 1,536자 초과 위험 (-2).

## 3. 토큰 효율성 / Progressive Disclosure (10점)

**공식**: "Keep SKILL.md under 500 lines. Move detailed reference material to separate files."

**alirezarezvani 표준**: *"Three-file minimum: SKILL.md + scripts/ + references/"* — 자주 안 읽히는 reference (validation script, 큰 예시, API 명세) 는 분리.

평가 기준:
- SKILL.md 본문 500줄 이하 (400~500줄은 경고)
- 큰 예시(>50줄), 검증 스크립트, 템플릿은 같은 디렉토리의 별도 파일로 분리
- SKILL.md 에서 reference 파일을 명시적으로 링크 ("see [reference.md]")
- `references/` / `scripts/` 서브디렉토리 활용

**감점 예시**: 500줄 초과 (-3), 큰 reference 인라인 (-3), reference 파일 링크 부재 (-1).

## 4. Standing Instructions vs One-time Steps (10점)

**공식**: *"skill content enters the conversation as a single message and stays there for the rest of the session. Claude Code does not re-read the skill file on later turns, so write guidance that should apply throughout a task as standing instructions rather than one-time steps."*

평가 기준:
- 세션 전반에 적용될 규칙은 **현재형 standing 문장** ("X 일 때 Y 한다")
- 절차는 별도 섹션으로 격리
- "이번에만" 또는 "먼저 X, 그다음 Y" 식 one-time 지시 최소화
- **gstack 의 mode differentiation**: 컨텍스트가 크게 다르면 명시적 모드(예: 4모드 `/plan-ceo-review`)로 분리

**감점 예시**: 본문 전체가 절차형 (-3), standing 규칙과 절차 혼재 (-2), 다른 컨텍스트가 한 흐름에 섞여 있음 (-2).

## 5. 예시 완결성 — 시연성 (10점)

스킬이 만들어내는 산출물 또는 적용된 결과의 **완성된 예시**가 있는가.

평가 기준:
- "잘 작성된" 예시 1개 이상 — 스킬의 모든 원칙을 동시에 시연
- placeholder 가 아닌 **실제 통과 가능한 완성본** (스킬의 LANGUAGE GATE / Forbidden / Pitfall 모두 통과)
- "나쁜 예 vs 좋은 예" 비교 (`Before vs After`) — alirezarezvani 의 변환 표 패턴
- **gstack 인용**: *"diagrams force hidden assumptions into the open. They make hand-wavy planning much harder."* — 시각 산출물 시연이 적합한 스킬은 도식/스크린샷도 포함

**감점 예시**: 완성 예시 부재 (-4), placeholder 만 있음 (-3), 자체 규칙 위반하는 예시 (-3).

## 6. Anti-pattern / Failure-mode 핸들링 (10점)

피해야 할 것 + 실패 시 복구가 명시되어 있는가.

평가 기준:
- `Forbidden` / `금지` 섹션 — 구체 예시 포함
- `Pitfalls` / `Known issues` — 과거 버그 + 재발 방지 메커니즘
- **gstack 인용**: *"Skills touching production or destructive operations must handle failure modes explicitly. /land-and-deploy doesn't assume success — it 'verifies production health' and tells you whether to rollback."*
- 파괴적 액션(rm, push, deploy)은 **사후 검증 + 복구 경로** 명시
- **자동 vs 수동 게이팅**: gstack 의 *"What can the model safely decide alone, and what needs human taste?"* — 기계적 결정은 자동, 취향 결정은 사용자에게 surface

**감점 예시**: forbidden 섹션 부재 (-3), 파괴적 액션 후 검증 부재 (-3), 자동/수동 경계 모호 (-2).

## 7. Validation / 자가 검증 (10점)

스킬 사용 후 결과의 올바름을 자동/반자동으로 확인하는 메커니즘이 있는가.

평가 기준:
- 산출물 생성 후 실행 가능한 체크리스트/스크립트
- 명확한 통과 기준 ("X 가 0 이어야 통과")
- **alirezarezvani 표준**: *"All CLI tools are tested with --help and --json flag support, enabling programmatic output parsing."* — 도구는 `--help` + 구조화 출력(`--json`) 지원
- 검증 스크립트 자체에 버그 없음 (셸 변수 치환, 인자 전달, 인용 heredoc 같은 함정)
- 의존성 최소화 — alirezarezvani: *"All Python CLI tools use the standard library only — zero pip installs required"*

**감점 예시**: validation 부재 (-4), 통과 기준 모호 (-2), 스크립트 버그 (-3), `--help`/`--json` 미지원 (-1), 외부 의존성 추가 (-1).

## 8. 보안 / 권한 설계 (`allowed-tools`) (10점)

평가 기준:
- `allowed-tools` 가 최소 권한 원칙
- 와일드카드 사용 시 합리적 범위 제한 (`Bash(rm *)` 같은 무제한 위험)
- 외부 영향 액션(push, send, deploy)은 `disable-model-invocation: true` 또는 명시 권한 게이트
- **gstack 의 careful 패턴**: *"PreToolUse hooks for checking destructive commands... Whitelisting common safe operations to avoid false alarms... Override capability"*
- **alirezarezvani 의 skill-security-auditor 패턴**: *"Scans for: command injection, code execution, data exfiltration, prompt injection, dependency supply chain risks"*

**감점 예시**: `Bash(*)` 무제한 (-5), `rm *` 와일드카드 (-2), 외부 영향 자동 호출 가능 (-3), 명령 주입 가능 입력 (-3).

## 9. 일반화 / 공유 적합성 / 휴대성 (10점)

마켓플레이스 배포 대상이므로 특정 프로젝트에 강결합되지 않아야 한다.

평가 기준:
- 출력 경로, 이슈 ID 포맷, 회사 약어 등이 **하드코딩되지 않고** override 가능 (`$ARGUMENTS`, 환경변수)
- 예시가 일반적 (회사 고유 클래스명/테이블명/약어 미사용)
- README 또는 SKILL.md 에 커스터마이즈 방법 안내
- 언어 강제 시 그 사유 명시
- **alirezarezvani 인용**: *"Tool-agnostic distribution: A single skill definition converts across 12 platforms... skills must be format-agnostic."* — 절대 경로, OS 가정(macOS sed) 같은 lock-in 회피
- **stdlib-only / 의존성 명시** — 외부 패키지를 묵시적으로 요구하지 않음

**감점 예시**: 회사 고유 경로 하드코딩 (-3), 회사 클래스명/약어 예시 (-2), 커스터마이즈 안내 부재 (-2), OS 특정 명령 (-1, 예: GNU/BSD sed 차이 미고려).

## 10. 의사결정·산출물 설계 (10점)

스킬이 사용자/시스템 상호작용을 어떻게 설계하는가. (이 축은 gstack/alirezarezvani 의 운영 통찰을 통합한 메타 축)

평가 기준:
- **artifact-forcing**: gstack — *"force hidden assumptions into the open through artifacts."* 추상 텍스트가 아닌 도식/표/HTML/JSON 등 검증 가능한 산출물 생성
- **persistent artifacts**: gstack — *"reviews save to ~/.gstack/projects/ for downstream skills to consume."* 후속 스킬이 소비 가능한 형태로 저장하거나, 이번 세션에서 일회용이면 명시
- **manual decision gating**: gstack — *"What can the model safely decide alone, and what needs human taste?"* 자동 결정 가능한 부분과 사용자 결정 필요한 부분의 경계 명시
- **skill sequencing**: gstack — *"office-hours → plan → implement → review → QA → ship → retro"* 이 스킬이 어떤 워크플로우의 어느 단계인지 명시 (전/후 스킬 관계)
- **end-of-skill reflection**: gstack — *"After /office-hours, the model reflects on what it noticed about how you think — not generic praise, but specific callbacks."* 적절한 경우 종료 시 관찰/체크 제공
- **mode differentiation**: gstack — 컨텍스트가 크게 다르면 명시 모드 분리

**감점 예시**: 추상 텍스트만 생성 (-3), 자동/수동 경계 부재 (-2), skill sequencing 미언급 (-2), 모드 분리 필요한데 단일 흐름 (-2).

---

## 통과 기준

- **총점 ≥ 90**: PASS — 병합 가능
- **총점 < 90**: FAIL — 개선 후 재제출
- **블로킹 이슈** (정적 검증 단계): YAML 파싱 실패, 필수 필드 누락, 500줄 hard cap 초과 등 — 점수 무관 자동 FAIL

## 평가 출력 포맷 (LLM 강제)

```json
{
  "axes": [
    {"id": 1, "name": "Frontmatter", "score": 9, "max": 10, "reason": "...", "improvements": ["..."]},
    ...
  ],
  "total": 84,
  "verdict": "FAIL",
  "blocking_issues": [],
  "top_improvements": ["..."],
  "summary": "한 문장 총평"
}
```

## 평가자 행동 원칙

1. 각 축은 본문에서 **실제 확인 가능한 사실**만 인용해 채점. 추측 금지.
2. 90점 게이트가 있으므로 의심스러우면 **보수적으로** 채점.
3. 개선 제안은 실행 가능한 수준 — "더 좋게 하라" 같은 모호한 표현 금지.
4. 일반화/휴대성 축은 **다른 팀이 다른 스택에서 쓴다**는 전제로 평가.
5. gstack/alirezarezvani 인용한 기준 위반은 점수 -1 ~ -3 사이 차등 적용.
