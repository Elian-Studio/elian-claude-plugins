# elian-claude-plugins

Daniel(Elian-Studio) 의 개인 Claude Code 플러그인 마켓플레이스. 결정 대시보드 등 개인 워크플로우 도구를 동료들과 공유하기 위해 패키징한 곳.

## 포함된 플러그인

| 이름 | 버전 | 설명 |
|------|------|------|
| [decision-dashboard](plugins/decision-dashboard/) | 1.0.0 | 여러 사안을 한 번에 결정할 때 사용하는 인터랙티브 HTML 대시보드 생성기. 라디오 선택 + 메모 + MD/JSON 다운로드. |

상세 변경 이력은 [CHANGELOG.md](CHANGELOG.md) 참조.

---

## 설치 (사용자)

### 1. 마켓플레이스 등록

```shell
/plugin marketplace add Elian-Studio/elian-claude-plugins
```

또는 git URL 직접:

```shell
/plugin marketplace add https://github.com/Elian-Studio/elian-claude-plugins.git
```

### 2. 플러그인 설치

```shell
/plugin install decision-dashboard@elian
```

### 3. 사용

`/decision-dashboard:decision-dashboard` 로 명시 호출하거나, "결정 대시보드 만들어줘" 같은 자연어로 말하면 Claude 가 자동 호출.

자세한 사용법은 [`plugins/decision-dashboard/skills/decision-dashboard/SKILL.md`](plugins/decision-dashboard/skills/decision-dashboard/SKILL.md) 참조.

### 업데이트

```shell
/plugin marketplace update elian
/plugin update decision-dashboard@elian
```

---

## Contributing (기여 / 자체 수정)

이 마켓플레이스는 **PR 기반 워크플로우**로 운영된다. 모든 변경은 PR 을 통과해야 main 에 반영된다.

### 워크플로우

```
1. 브랜치 생성 → feature/<scope> 또는 fix/<scope>
2. SKILL.md / plugin.json / marketplace.json 변경
3. 로컬 검증 (선택)
4. PR 생성
5. Skill Quality Gate (Actions) 자동 실행 — 90점 이상 통과
6. 리뷰 + 머지
```

### 로컬 검증

```bash
# 정적 검증 (무료, 빠름)
bash scripts/static_checks.sh plugins/decision-dashboard/skills/decision-dashboard/SKILL.md

# LLM 평가 (Anthropic API 호출, 1회 약 $0.02)
export ANTHROPIC_API_KEY=sk-ant-...
pip install 'anthropic>=0.40.0'
python scripts/evaluate_skill.py plugins/decision-dashboard/skills/decision-dashboard/SKILL.md
```

### 평가 기준

PR 의 SKILL.md 변경은 [scripts/rubric.md](scripts/rubric.md) 의 100점 만점 루브릭으로 평가된다.

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

루브릭은 다음 세 레퍼런스를 종합한다:
- [Claude Code 공식 Skills 가이드](https://code.claude.com/docs/en/skills)
- [garrytan/gstack — docs/skills.md](https://github.com/garrytan/gstack/blob/main/docs/skills.md) (실전 운영 사례)
- [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (235 스킬 마켓플레이스 패턴)

---

## 저장소 운영 (메인테이너)

### 1회 셋업

#### Anthropic API 키 등록

PR 게이트가 LLM 평가를 위해 API 키를 사용한다.

GitHub UI:
```
Settings → Secrets and variables → Actions → New repository secret
Name: ANTHROPIC_API_KEY
Value: sk-ant-...
```

`gh` CLI:
```bash
gh secret set ANTHROPIC_API_KEY --body "sk-ant-..." --repo Elian-Studio/elian-claude-plugins
```

#### 브랜치 보호 규칙 (main 보호)

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

`gh` CLI (간이):
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

> `enforce_admins: false` 는 메인테이너(=daniel) 가 긴급 시 우회할 수 있도록 둔 설정. 엄격히 하려면 `true`.

### 릴리즈 절차 (변경 머지 → 배포)

1. PR 머지 (게이트 통과 후)
2. **`plugin.json.version`** 또는 **마켓플레이스 메타데이터 버전** 이 bump 되었으면 사용자에게 자동 업데이트 도달
3. 명시 태그 권장 (선택):
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

> 공식 가이드: *"If `plugin.json` declares `"version": "1.0.0"`, pushing new commits without changing that string does nothing for existing users, because Claude Code sees the same version and keeps the cached copy."* 반드시 bump.

---

## 디렉토리 구조

```
elian-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json          # 마켓플레이스 카탈로그
├── .github/
│   ├── workflows/
│   │   └── skill-quality-gate.yml  # PR 자동 평가
│   └── pull_request_template.md
├── plugins/
│   └── decision-dashboard/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── decision-dashboard/
│               ├── SKILL.md
│               └── template.html
├── scripts/
│   ├── rubric.md                 # 평가 루브릭 (100점)
│   ├── static_checks.sh          # 정적 검증 (frontmatter, 길이 등)
│   └── evaluate_skill.py         # LLM 평가
├── CHANGELOG.md
├── README.md
└── .gitignore
```

---

## 라이선스

MIT (각 플러그인의 `plugin.json.license` 참조)
