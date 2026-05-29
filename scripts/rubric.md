# Skill Quality Rubric (100점 만점, 휴리스틱)

이 루브릭은 다음 세 레퍼런스를 종합한다:
1. [Claude Code 공식 Skills 가이드](https://code.claude.com/docs/en/skills)
2. [Claude Code 공식 Plugins / Marketplace 가이드](https://code.claude.com/docs/en/plugins)
3. [garrytan/gstack — docs/skills.md](https://github.com/garrytan/gstack/blob/main/docs/skills.md) (실전 운영 사례)
4. [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (대형 스킬 마켓플레이스 운영 패턴)

공식 문서와 외부 레퍼런스가 충돌하면 공식 문서와 이 저장소의 로컬 게이트를 우선한다. 예: Claude Code 공식 문서는 `when_to_use`, `argument-hint`, `allowed-tools`, `disable-model-invocation` 같은 optional frontmatter를 지원하므로, "frontmatter는 name/description만" 같은 더 좁은 외부 규칙은 이 저장소에 그대로 적용하지 않는다.

마켓플레이스 병합 게이트는 **총점 90점 이상**을 요구한다. 10개 축 × 각 10점.

**채점 방식**: `scripts/score_skill.py` 가 Python stdlib 만 사용해 결정적 신호로 점수화한다. LLM 호출 없음, 외부 API 키 불필요, 빠르고 비용 0. 같은 입력은 항상 같은 점수를 받는다.

> **휴리스틱의 한계**: 글의 매끄러움/품질 같은 의미적 판단은 평가하지 못한다. 구조적 요소(섹션 존재, 길이, 키워드, 패턴) 만 점수화한다. 따라서 "구조는 갖췄으나 글이 거친" 스킬도 통과할 수 있다. 운영해보고 부족하면 LLM 보강 가능.

---

## 1. Frontmatter 규약 준수 (10점)

| 신호 | 점수 |
|------|------|
| YAML `---` 블록 존재 | +2 |
| `name` kebab-case + 64자 이내 | +2 |
| `name` 이 디렉토리명과 일치 | +1 |
| `description` 존재 | +2 |
| `when_to_use` 존재 또는 description ≥150자 | +1 |
| `argument-hint` 존재 | +1 |
| `allowed-tools` 존재 | +1 |

> 공식 가이드: *"All fields are optional. Only `description` is recommended so Claude knows when to use the skill."*
> repo policy: `name`, `argument-hint`, `allowed-tools` 는 이 저장소의 품질 게이트에서 요구하는 운영 필드다.

## 2. Description 자동 호출 신뢰성 (10점)

| 신호 | 점수 |
|------|------|
| description + when_to_use 합산 ≤1536자 (공식 캡) | +3 |
| description 이 "When " 으로 시작 | +3 |
| description 본문에 "when" 또는 "상황" 포함 | +2 (위와 OR) |
| description 첫 단어가 process 동사 ("Generate"/"Create"/"Make"/"Build") 가 아님 | +2 |
| description 또는 when_to_use 에 따옴표로 둘러싼 트리거 문구 존재 | +2 |

> gstack: *"Lead with the concrete problem the skill solves, not aspirational framing."*
> alirezarezvani: *"Descriptions are outcome-focused rather than process-focused."*

## 3. Progressive Disclosure (10점)

| 신호 | 점수 |
|------|------|
| 본문 ≤400줄 | +5 |
| 본문 ≤500줄 | +4 (위와 OR) |
| `references/` + `scripts/` 디렉토리 둘 다 존재 | +3 |
| 한쪽만 존재 | +2 (위와 OR) |
| SKILL.md 가 references/ 또는 scripts/ 의 파일을 markdown 링크로 참조 | +2 |

> 공식: *"Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files."*
> alirezarezvani 운영 패턴: SKILL.md 는 workflow/navigation 에 집중하고, 깊은 지식은 references/, 결정적 작업은 scripts/ 로 분리한다. 운영 목표는 SKILL.md 10KB 안쪽이다.

## 4. Standing Instructions vs One-time Steps (10점)

| 신호 | 점수 |
|------|------|
| "Modes" 또는 "모드" 섹션 존재 | +4 |
| "Standing rules" 또는 "원칙" 섹션 존재 | +3 (위와 OR) |
| "Procedure" 또는 "절차" 섹션 분리 존재 | +3 |
| 절차 마커(`Step N:` / `1. ` 시작 줄) 밀도 < 5% | +3 |
| 5~10% | +2 |
| 10% 이상 | +1 |

> 공식: *"skill content enters the conversation as a single message and stays there for the rest of the session... write guidance that should apply throughout a task as standing instructions rather than one-time steps."*

## 5. 예시 완결성 (10점)

| 신호 | 점수 |
|------|------|
| `references/` 에 .md 또는 .html 파일 존재 | +5 |
| 본문에 "BEFORE/AFTER" / "나쁨/좋음" / "❌/✅" 비교 패턴 존재 | +3 |
| 본문 또는 references/ 에 체크리스트(`[ ]`) 5개 이상 | +2 |

> alirezarezvani: 잘 만들어진 스킬은 references/ 에 템플릿/체크리스트/예시를 분리. 본문은 그 파일을 링크하고 핵심만 요약.

## 6. Anti-pattern / Failure-mode (10점)

| 신호 | 점수 |
|------|------|
| "Forbidden" / "금지" / "Don't" 섹션 | +3 |
| "Pitfall" / "Known issue" 섹션 | +3 |
| 본문에 "verify"/"검증"/"rollback"/"fail" 키워드 존재 (failure-mode 핸들링) | +2 |
| "automated.*taste" / "자동.*사용자" / "auto vs" / "gating" — 자동 vs 사용자 결정 경계 명시 | +2 |

> gstack: *"Skills touching production or destructive operations must handle failure modes explicitly."* + *"What can the model safely decide alone, and what needs human taste?"*

## 7. Validation 자가 검증 (10점)

| 신호 | 점수 |
|------|------|
| `scripts/` 안에 이름에 "valid" 또는 "check" 포함된 도구 존재 | +4 |
| `scripts/` 에 도구는 있으나 이름이 모호 | +2 (위와 OR) |
| 검증 도구가 argparse 또는 getopts 사용 (`--help` 지원) | +3 |
| 검증 도구가 `--json` 출력 지원 | +3 |

> alirezarezvani 표준: *"All CLI tools are tested with --help and --json flag support, enabling programmatic output parsing."*

## 8. 보안 / 권한 설계 (10점)

| 신호 | 점수 |
|------|------|
| `allowed-tools` 정의됨 | +3 |
| `Bash(*)` 무제한 패턴 없음 | +3 |
| `Bash(rm *)` 무제한 또는 `rm -rf` 패턴 없음 | +2 |
| `disable-model-invocation: true` 또는 외부 영향 액션(push/deploy/send/delete) 자동 호출 가능 표현 없음 | +2 |

> 공식: *"`allowed-tools` grants permission for the listed tools while the skill is active... It does not restrict which tools are available... your permission settings still govern tools that are not listed."*
> side-effect 가 있는 workflow 는 `disable-model-invocation: true` 를 기본값으로 둔다.

## 9. 일반화 / 휴대성 (10점)

| 신호 | 점수 |
|------|------|
| 회사 고유 이슈 prefix(`MPT-####`, `ACME-####` 등) 본문에 없음 | +3 |
| 환경변수(`$VAR` / `${VAR}`) 와 `$ARGUMENTS`/`argument-hint` 둘 다 사용 | +4 |
| 한쪽만 사용 | +2 (위와 OR) |
| `sed -i ''` (BSD sed 의존) 패턴 없음 — Linux 호환 | +3 |

> alirezarezvani: *"Tool-agnostic distribution: A single skill definition converts across 12 platforms... skills must be format-agnostic."*

## 10. 의사결정·산출물 설계 (10점)

| 신호 | 점수 |
|------|------|
| "Where this fits" / "workflow" / "sequencing" 섹션 (skill sequencing) | +3 |
| "automated vs taste" / "자동 vs 사용자" / "gating" 표현 (manual decision gating) | +3 |
| "Reflection" / "관찰" / "패턴" 섹션 (end-of-skill reflection) | +2 |
| "persistent" / "영구" / "downstream" / "후행" (persistent artifact for downstream) | +1 |
| "Modes" / "모드" 섹션 (mode differentiation) | +1 |

> gstack 의 운영 통찰 종합: artifact-forcing, persistent artifacts for downstream, manual decision gating, skill sequencing, end-of-skill reflection, mode differentiation.

---

## 통과 기준

- **총점 ≥ 90**: PASS — 병합 가능
- **총점 < 90**: FAIL — 개선 후 재제출

## 평가 출력

`scripts/score_skill.py <SKILL.md path> [--json]` 실행 시 다음 구조로 결과 산출:

```json
{
  "pass_score": 90,
  "all_pass": true,
  "results": [
    {
      "path": "...",
      "axes": [
        {"id": 1, "name": "Frontmatter 규약 준수", "score": 10, "max": 10, "reason": "...", "improvements": []},
        ...
      ],
      "total": 97,
      "verdict": "PASS",
      "blocking_issues": [],
      "top_improvements": ["..."],
      "summary": "한 문장 총평"
    }
  ]
}
```

## 향후 LLM 보강 (선택)

휴리스틱이 놓치는 의미적 품질을 평가하고 싶다면, 아래 hybrid 모델로 확장 가능:

1. 휴리스틱 점수가 90+ → 자동 PASS
2. 휴리스틱 점수가 80~89 → ANTHROPIC_API_KEY 가 있으면 LLM 추가 평가, 둘 합산하여 90+면 PASS
3. 휴리스틱 점수가 80 미만 → 자동 FAIL (LLM 호출 안 함, 비용 절약)

이 hybrid 는 현재 미구현. 필요 시 별도 PR 로 추가.
