# Contributing

이 마켓플레이스에 기여하거나 본인의 변경을 머지할 때 참고하는 가이드입니다.

## 워크플로우

```
1. 브랜치 생성 → feature/<scope> 또는 fix/<scope>
2. SKILL.md / plugin.json / marketplace.json 변경
3. (선택) 로컬 채점으로 사전 점검
4. PR 생성
5. Skill Quality Gate (Actions) 자동 실행 — 90점 이상이어야 통과
6. 리뷰 + 머지
7. 필요 시 GitHub Release 발행
```

main 브랜치는 직접 푸시 차단. 모든 변경은 PR 을 거쳐야 합니다.

---

## 로컬 검증

휴리스틱 채점 — Python stdlib 만 사용. **외부 API 키 / 의존성 / 비용 모두 0**. 같은 입력은 같은 점수.

```bash
# 텍스트 출력
python3 scripts/score_skill.py plugins/elian-store/skills/decision-dashboard/SKILL.md

# JSON 출력 (다른 스킬과 chaining 가능)
python3 scripts/score_skill.py plugins/elian-store/skills/decision-dashboard/SKILL.md --json

# 여러 SKILL.md 동시 채점
python3 scripts/score_skill.py plugins/elian-store/skills/*/SKILL.md

# 실제 YAML parser smoke test (frontmatter가 Claude/GitHub에서 깨지는지 확인)
ruby -EUTF-8 -ryaml -e 'Dir["plugins/elian-store/skills/*/SKILL.md"].sort.each { |p| s=File.read(p, encoding: "UTF-8"); YAML.safe_load(s.split(/^---\s*$/,3)[1] || "", permitted_classes: [], aliases: false); puts "OK #{p}" }'
```

종료 코드: 모든 입력이 90점 이상이면 `0`, 하나라도 미만이면 `1`.

---

## 평가 기준 (90점 게이트)

PR 의 SKILL.md 변경은 [`scripts/rubric.md`](scripts/rubric.md) 의 100점 만점 루브릭으로 평가됩니다.

10개 축 × 각 10점:

1. Frontmatter 규약 준수
2. Description 자동 호출 신뢰성
3. Progressive Disclosure (토큰 효율)
4. Standing Instructions
5. 예시 완결성
6. Anti-pattern / Failure-mode 핸들링
7. Validation 자가 검증
8. 보안 / 권한 (`allowed-tools`)
9. 일반화 / 휴대성
10. 의사결정·산출물 설계

루브릭은 다음 레퍼런스를 종합합니다:

- [Claude Code 공식 Skills 가이드](https://code.claude.com/docs/en/skills)
- [Claude Code 공식 Plugins / Marketplace 가이드](https://code.claude.com/docs/en/plugins)
- [garrytan/gstack — docs/skills.md](https://github.com/garrytan/gstack/blob/main/docs/skills.md) (실전 운영 사례)
- [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (대형 스킬 마켓플레이스 운영 패턴)

### Portfolio review checklist (non-blocking)

90점 게이트는 개별 `SKILL.md` 품질을 본다. 포트폴리오 운영 모델은 [`docs/plugin-portfolio-hybrid-model.md`](docs/plugin-portfolio-hybrid-model.md)를 기준으로 하고, gstack식 lifecycle gap은 별도 체크리스트로 운영한다. 새 스킬을 추가하거나 큰 리팩터링을 할 때 [`docs/gstack-skill-review.md`](docs/gstack-skill-review.md)도 같이 확인한다.

- lifecycle coverage: product/spec → design → implement/fix/improve → review → browser QA → ship/release → learning
- role clarity: 각 skill은 하나의 specialist 역할과 하나의 명확한 job을 가진다.
- artifact continuity: 출력물이 downstream skill의 입력으로 이어진다.
- human decision gate: 취향/릴리즈/파괴적 변경은 사용자가 결정한다.
- browser-visible QA: UI/배포 검증은 가능한 한 실제 화면, 스크린샷, 재현 경로를 남긴다.
- release readiness: 구현 완료와 release/PR 생성은 별도 책임으로 분리한다.
- learning capture: 반복되는 선호, 실패 모드, 프로젝트 규칙은 후속 세션에서 재사용 가능해야 한다.

### Claude skill/plugin 운영 규칙

이 저장소의 기준은 **Claude Code 공식 문서가 하한선**, `alirezarezvani/claude-skills`가 **운영 패턴 참고자료**입니다. 외부 레퍼런스끼리 충돌하면 공식 문서와 이 저장소의 로컬 게이트를 우선합니다.

- `SKILL.md` frontmatter: `description`은 공식 권장 필드입니다. 이 저장소는 추가로 `name`, `argument-hint`, `allowed-tools`를 요구하고, 자동 호출 트리거가 길면 `when_to_use`로 분리합니다.
- `description`, `when_to_use`, `argument-hint` 값에 `: `, `[`/`]`, 따옴표, 긴 trigger list가 들어가면 YAML 문자열로 quote합니다. 특히 `Trigger phrases:` 같은 문장은 unquoted plain scalar로 두면 Claude/GitHub YAML 파서가 실패합니다.
- `description + when_to_use`는 공식 skill listing cap인 1,536자 안에 유지합니다. 핵심 use case를 앞에 두고, 긴 절차 설명은 본문이나 `references/`로 내립니다.
- side-effect가 있는 workflow는 `disable-model-invocation: true`를 기본값으로 둡니다. 자동 호출 가능한 skill은 읽기/문서 생성 등 영향 범위가 낮아야 합니다.
- `SKILL.md`는 공식 기준 500줄 이하를 지키고, 운영 목표는 10KB 안쪽입니다. 긴 예시, 체크리스트, 도메인 지식은 `references/`, 반복 출력 양식은 `templates/`, 결정적 검증은 `scripts/`로 분리합니다.
- plugin 구조: `.claude-plugin/` 안에는 `plugin.json`만 둡니다. `skills/`, `agents/`, `hooks/`, `.mcp.json`, `.lsp.json` 등 컴포넌트는 plugin root에 둡니다.
- marketplace 구조: root `.claude-plugin/marketplace.json`이 catalog이고, plugin 본문은 `plugins/elian-store/` 아래에 둡니다.
- version 규칙: `plugin.json.version`이 있으면 marketplace entry의 `version`보다 우선하고 update cache key가 됩니다. plugin 내부 문서나 skill 동작을 바꾸면 `plugin.json`, root `marketplace.json`, `README.md`, `CHANGELOG.md`를 함께 갱신합니다.

---

## 단일 번들 플러그인 모델

이 마켓플레이스는 **단일 번들 플러그인**(`elian-store`) 안에 다수 스킬을 묶어 배포합니다. 사용자는 한 번의 설치로 모든 스킬을 받고, 새 스킬 추가는 `/plugin update elian-store@elian` 로 자동 반영됩니다.

```
plugins/elian-store/
├── .claude-plugin/
│   └── plugin.json                    # 번들 메타데이터 (name: "elian-store", version: ...)
└── skills/
    ├── decision-dashboard/            # 스킬 1
    │   ├── SKILL.md
    │   ├── scripts/                   # 스킬 자체 도구 (검증 등). --help/--json 지원
    │   ├── references/                # 예시, 체크리스트
    │   └── (스킬별 추가 자산)
    ├── manage-skills/                 # 스킬 2 (예정)
    │   └── SKILL.md
    └── ...
```

## 새 스킬 추가하기

1. `plugins/elian-store/skills/<new-skill>/SKILL.md` 작성 — 루브릭 90점 기준 충족 (구조: SKILL.md + 가능하면 scripts/ + references/)
2. `plugins/elian-store/.claude-plugin/plugin.json` 의 `version` bump (MINOR — 신규 스킬 추가)
3. `.claude-plugin/marketplace.json` 의 elian-store entry 의 `version` 도 동시 bump
4. `README.md` 의 스킬 표에 신규 row 추가 (상태: ✅ 또는 적절히)
5. `CHANGELOG.md` 의 `elian-store` 섹션에 신규 버전 항목 작성 (Added: 새 스킬 X)
6. PR 생성 → 게이트(SKILL.md 90점) 통과 확인 → 머지
7. (메인테이너) GitHub Release 발행

> 마켓플레이스에 새 플러그인을 통째로 추가하려는 경우(이를테면 `elian-pro` 같은 별도 번들), 별도 PR + 별도 가이드. 현재 정책은 **단일 번들** 권장.

---

## Claude vs Codex — 어디를 수정하나

이 repo 는 두 도구용 설정을 **독립 2-트리**로 관리합니다. 단일 진실원이 **없습니다** (의식적 결정 — `/persona-review` 리뷰에서 trade-off 인지 후 채택).

| | Claude Code | Codex CLI |
|---|---|---|
| 트리 | `plugins/elian-store/skills/*/SKILL.md` | `codex/prompts/*.md` |
| 진입 포맷 | YAML frontmatter + 마크다운 | 순수 마크다운 (파일명 = `/명령`), `$ARGUMENTS` |
| 프로젝트 지침 | `CLAUDE.md` / `.claude/` | `codex/AGENTS.md` / `~/.codex/config.toml` |
| 권한 모델 | frontmatter `allowed-tools` | `config.toml` `approval_policy`/`sandbox_mode` |
| 품질 게이트 | `scripts/score_skill.py` + `rubric.md` (10축) | `scripts/score_codex_prompt.py` + `rubric-codex.md` (8축) |
| CI | `.github/workflows/skill-quality-gate.yml` | `.github/workflows/codex-config-gate.yml` |

**핵심 규칙 (드리프트 책임):**

1. 한 도구의 로직을 바꾸면 다른 트리 동기화는 **PR 작성자 수동 책임**. 게이트가 자동 동기화해 주지 않는다.
2. 같은 스킬이 양쪽에 있으면 **PR 에서 두 파일 diff 를 함께** 확인. (v2.5.0 에서 잡은 "산문↔절차 drift" 의 트리-레벨 버전이 정확히 이 위험.)
3. Codex 게이트의 축 1·3·5(command identity·workflow 정합·카운터파트 상호참조)가 이 드리프트를 결정적으로 검사한다 — 우회하지 말 것.
4. 새 스킬을 Codex 로도 포팅할 때: `codex/prompts/<skill>.md` 작성 → `python3 scripts/score_codex_prompt.py codex/prompts/<skill>.md` 90점 확인 → `codex/README.md` 포팅 목록 갱신.
5. `codex/` 추가는 elian-store **플러그인 버전과 무관** (마켓플레이스 플러그인이 아닌 sibling 배포 트리). `plugin.json`/`marketplace.json` version bump 대상 아님.
6. Claude/Codex catalog parity 는 [`docs/claude-codex-skill-parity.md`](docs/claude-codex-skill-parity.md) 를 기준으로 점검한다. 새 Claude skill 은 같은 PR 에 Codex prompt 또는 예외 사유를 남긴다.
7. plugin portfolio 운영 모델은 [`docs/plugin-portfolio-hybrid-model.md`](docs/plugin-portfolio-hybrid-model.md) 를 기준으로 한다. gstack lifecycle gaps 는 [`docs/gstack-skill-review.md`](docs/gstack-skill-review.md) 에서 관리한다. gap이 있다고 바로 skill을 추가하지 말고, 먼저 local workflow와 검증 산출물이 있는지 확인한다.

---

## 메인테이너용 — 1회 셋업 (저장소 운영)

게이트는 stdlib 만 사용하는 휴리스틱이라 **API 키 / Secret 셋업 불필요**. 브랜치 보호 규칙만 적용하면 즉시 작동.

### 브랜치 보호 규칙 (`main` 보호)

직접 푸시 차단 + 게이트 통과 필수.

GitHub UI:
```
Settings → Branches → Add branch ruleset
- Branch name pattern: main
- Require a pull request before merging: ✅
- Require status checks to pass before merging: ✅
  - Status check: "Evaluate skills (90+ required)"
  - Require branches to be up to date before merging: ✅
- Block force pushes: ✅
- Require linear history: (선택)
```

`gh` CLI:
```bash
gh api -X PUT repos/Elian-Studio/elian-claude-plugins/branches/main/protection \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["Evaluate skills (90+ required)"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

> `enforce_admins: false` 는 메인테이너가 긴급 시 우회할 수 있도록 둔 설정. 엄격히 하려면 `true`.
> README/CHANGELOG/docs-only PR도 required check가 생성되도록 `skill-quality-gate.yml`의 `paths`에 문서 경로를 포함한다.

---

## 릴리즈 절차 (변경 머지 → 배포)

1. **PR 머지** (게이트 통과 후)
2. **`plugin.json.version`** 이 bump 됐다면 사용자 자동 업데이트 도달 (`plugin.json.version` 이 marketplace entry `version` 보다 우선)
3. **GitHub Release 발행** — 사용자 안내용:
   ```bash
   gh release create vX.Y.Z \
     --target main \
     --title "vX.Y.Z — <한 줄 요약>" \
     --notes "$(cat <<'NOTES'
   ## 변경 요약
   ...
   ## 포함된 플러그인 변경
   - plugin-name `vX.Y.Z` — ...
   ## 마켓플레이스 인프라 변경 (있을 시)
   ...
   NOTES
   )"
   ```

> 공식 가이드: *"If `plugin.json` declares `"version": "1.0.0"`, pushing new commits without changing that string does nothing for existing users, because Claude Code sees the same version and keeps the cached copy."* 반드시 bump.

---

## 디렉토리 구조

```
elian-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json          # 마켓플레이스 카탈로그 (단일 elian-store entry)
├── .github/
│   ├── workflows/
│   │   ├── skill-quality-gate.yml  # Claude SKILL.md PR 자동 평가
│   │   └── codex-config-gate.yml   # Codex prompt PR 자동 평가 (독립)
│   └── pull_request_template.md
├── plugins/                       # ── Claude Code 트리 ──
│   └── elian-store/              # 단일 번들 플러그인
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           ├── decision-dashboard/
│           │   ├── SKILL.md
│           │   ├── scripts/
│           │   └── references/
│           ├── create-document/
│           │   ├── SKILL.md
│           │   ├── scripts/
│           │   ├── schemas/
│           │   └── templates/
│           └── (추가 스킬은 같은 skills/ 하위에)
├── codex/                         # ── Codex CLI 트리 (plugins/ 와 독립) ──
│   ├── README.md                 # 정체성 + 설치 + drift 경고
│   ├── AGENTS.md                 # Codex 프로젝트 지침 템플릿
│   ├── prompts/
│   │   └── persona-review.md      # 레퍼런스 포팅 (~/.codex/prompts/ 드롭인)
│   └── config.toml.example       # ~/.codex/config.toml 샘플
├── scripts/                       # 마켓플레이스 레벨 도구
│   ├── rubric.md                 # Claude 평가 루브릭 (100점)
│   ├── score_skill.py            # Claude SKILL.md 채점 (stdlib only)
│   ├── rubric-codex.md           # Codex 평가 루브릭 (100점, 독립)
│   └── score_codex_prompt.py     # Codex prompt 채점 (stdlib only)
├── docs/
│   ├── claude-codex-skill-parity.md
│   ├── claude-skill-plugin-audit.md
│   └── screenshots/              # README 용 시각 자료
├── CHANGELOG.md
├── CONTRIBUTING.md               # 이 파일
├── README.md
└── .gitignore
```

---

## 라이선스

MIT (각 플러그인의 `plugin.json.license` 필드 참조)
