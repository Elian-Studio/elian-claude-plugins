---
name: manage-skills
description: When verify-* skills drift behind code changes (uncovered files / broken references / missing checks), auto-detect the drift and create or update verify-* skills so the project's verification stays current. Pairs with verify-implementation (orchestrator); this skill is the meta-tool that maintains the skill set.
when_to_use: "after introducing new patterns/rules, before PR to confirm coverage, when verification missed an expected issue, periodically to keep skills aligned with codebase, user says '스킬 드리프트 점검'·'verify 스킬 정리'·'/manage-skills'"
argument-hint: "[skill-name | focus-area | question]"
disable-model-invocation: true
allowed-tools: Bash(git diff*) Bash(git log*) Bash(grep*) Bash(awk*) Bash(find*) Bash(python3 *) Read Glob Grep Edit Write
---

# manage-skills — verify-* 스킬 드리프트 자동 유지

코드는 진화하고 검증 스킬은 뒤처진다. 이 스킬은 세션 변경사항과 프로젝트의 `verify-*` 스킬을 매핑해 **커버리지 갭을 찾고**, 필요하면 **새 verify-* 스킬을 자동 생성**하거나 **기존 스킬을 업데이트**해서 검증을 코드에 맞춘다.

---

## Where this fits in the workflow

```
implement / fix / improve  →  manage-skills (드리프트 점검 + 스킬 정정)  →  verify-implementation (실제 검증 실행)  →  ship
                                       ↑                                           ↓
                                       └────────── 매 PR 전 한 번 ──────────────┘
```

- **선행**: `/implement`, `/fix`, `/improve` 가 코드를 바꾼 직후 새 패턴/규칙이 도입됨
- **이 스킬**: 변경 ↔ 기존 verify-* 스킬 매핑 분석. 갭 있으면 스킬 생성/업데이트
- **후행**: `/verify-implementation` 이 정정된 verify-* 들을 실제로 실행해 통합 검증

세트 관계: `manage-skills` (메타-도구) ↔ `verify-implementation` (오케스트레이터). 본 elian-store 안에 함께 번들됨.

---

## What's automated vs what needs your taste

| Claude 가 자동으로 결정 | 사용자가 결정 |
|--------------------------|-------------|
| 스킬 동적 탐색 (`.claude/skills/verify-*/SKILL.md` Glob) | 새 스킬 생성 여부 (CREATE 제안 시 승인 게이트) |
| 변경 파일 ↔ 스킬 매핑 (Related Files / Workflow 패턴 매칭) | 매핑 모호 시 어느 스킬에 귀속시킬지 |
| Coverage Gap / Invalid Reference / Missing Check / Outdated Value 4종 분류 | 면제(EXEMPT) 처리할지 |
| CREATE vs UPDATE vs EXEMPT 1차 판정 | 판정 결과 채택 / 재작성 / 보류 |
| 기존 스킬의 Related Files 자동 추가/제거 | 검증 명령어(Grep/Glob 패턴) 의도 |

판정이 모호하면 사용자에게 묻는다. "스킬 자동 생성" 은 항상 사용자 승인 게이트 거침.

---

## Modes

### Mode 1: `analyze` (기본)

세션 변경 ↔ 기존 verify-* 스킬 드리프트만 분석하고 보고. 실제 수정 안 함. PR 전 점검에 적합.

**산출물**: 콘솔 보고서 (분석 요약 표 + 변경 상세 표 + 커버되지 않은 변경 목록)

### Mode 2: `repair`

`analyze` 결과를 받아 실제 스킬 수정/생성. 각 CREATE/UPDATE 항목마다 사용자 승인 게이트.

**산출물**:
- 수정된 `.claude/skills/verify-*/SKILL.md` 파일들
- (선택) 생성된 신규 `verify-{name}/SKILL.md`
- `verify-implementation` 동기화 (하드코딩 목록 사용 시)

### Mode 3: `sync-with-verify-implementation`

프로젝트의 `verify-implementation` SKILL.md 가 하드코딩된 verify-* 목록을 사용하는 경우, 그 목록을 현재 디렉토리 상태로 자동 갱신. (글로벌 elian-store 의 verify-implementation 은 동적 탐색 방식이라 이 단계 불필요)

---

## Standing rules — 새/수정된 verify-* 스킬 품질 기준

(생성/수정 시 모든 verify-* 스킬에 항상 적용. 절차 아닌 standing instructions.)

### 명명

- 검증 스킬: **`verify-`** 접두사 필수
- kebab-case 만 (소문자/숫자/하이픈)
- 도메인이 명확히 드러나는 이름 (예: `verify-i18n`, `verify-api-contract`)

### 필수 섹션 (만족 안 하면 발행 차단)

1. `Purpose` — 무엇을 검증하는가
2. `When to Run` — 언제 실행되는가
3. `Related Files` — 검사 대상 파일 패턴
4. `Workflow` — 단계별 검사 + 탐지 명령어 + PASS/FAIL 기준
5. `Output Format` — 결과 보고 포맷
6. `Exceptions` — 위반이 아닌 것

### 품질 기준

- 실제 존재하는 파일 경로
- 작동하는 탐지 명령어 (Grep/Glob/Bash)
- 명시적 PASS/FAIL 기준
- 현실적인 면제 조건 (false positive 회피)
- 일관된 포맷

### 검사 범위

**현재 작업 디렉토리의 `.claude/skills/` 만** 대상. 사용자 글로벌 (`~/.claude/skills/`) 은 건드리지 않는다. 프로젝트 격리 보장.

---

## Procedure — Mode 1 (analyze)

```bash
# 1. 스킬 동적 탐색
SKILLS=$(find .claude/skills -maxdepth 2 -name SKILL.md 2>/dev/null)
# 분류 (verify-* / manage-* / 기타) — references/example-skill-table.md 참조

# 2. 세션 변경 수집
git diff HEAD --name-only > /tmp/session-changes.txt
git log --oneline main..HEAD 2>/dev/null
git diff main...HEAD --name-only 2>/dev/null
sort -u /tmp/session-changes.txt > /tmp/changed-files.txt
```

이후 단계는 standing rules 와 references 참조:

3. **변경 ↔ 스킬 매핑** — 각 verify-* 의 Related Files / Workflow 패턴과 매칭. 상세는 [`references/drift-detection.md`](references/drift-detection.md)
4. **4종 갭 분류** — Coverage Gap / Invalid Reference / Missing Check / Outdated Value
5. **CREATE / UPDATE / EXEMPT 판정** — 판정 매트릭스: [`references/decision-matrix.md`](references/decision-matrix.md)
6. **보고서 생성** — 포맷: [`references/example-drift-report.md`](references/example-drift-report.md)

Mode 1 은 보고만 한다. 실제 수정은 Mode 2 (repair) 에서.

---

## Procedure — Mode 2 (repair)

Mode 1 의 보고서를 입력으로 받아 각 항목 실행:

| 판정 | 액션 | 사용자 승인 게이트? |
|------|------|------------------|
| UPDATE (Related Files 추가) | 해당 SKILL.md 의 Related Files 자동 추가 | 한 번 모아서 |
| UPDATE (탐지 명령어 갱신) | Workflow 섹션 자동 수정 | 항목별 |
| CREATE (신규 verify-* 스킬) | `verify-{name}/SKILL.md` 신규 생성 | **카드 단위로 반드시** |
| EXEMPT | 조치 없음 | 불필요 |

생성/수정 후 `scripts/check-skill-frontmatter.py` 로 자가 검증. 6개 필수 섹션 모두 존재하는지, frontmatter 가 valid 한지 확인.

---

## Procedure — Mode 3 (sync-with-verify-implementation)

프로젝트 `.claude/skills/verify-implementation/SKILL.md` 의 본문에 하드코딩된 verify-* 목록이 있으면 그것을 현재 디렉토리 실제 상태와 일치시킨다. 글로벌 elian-store 의 verify-implementation 은 동적 탐색 방식이므로 이 모드는 **프로젝트가 자체 verify-implementation 을 갖고 있는 경우만** 적용.

---

## Forbidden

- 사용자 글로벌 `~/.claude/skills/` 의 스킬을 수정/생성 — 본 스킬은 **현재 프로젝트 (.claude/skills/) 만** 대상
- `verify-` 접두사 없는 스킬을 검증 스킬로 분류
- 스킬 삭제 — 사용자 명시 동의 없이 절대 삭제 안 함 (추가/수정만)
- 6개 필수 섹션 (Purpose/When to Run/Related Files/Workflow/Output Format/Exceptions) 미충족 스킬 발행
- 비현실적 면제 조건 (모든 패턴을 면제 처리해 검증 무력화)

## Known pitfalls (regression prevention)

### Pitfall 1: 매핑 모호 시 자동 귀속

**Symptom**: 변경 파일 X 가 verify-A, verify-B 양쪽 패턴에 매칭. 자동으로 verify-A 에 추가됨. 나중에 verify-B 에서 누락 발견.

**Cause**: 매핑 알고리즘이 첫 번째 매치만 채택.

**Prevention**: 모호한 매칭은 사용자에게 질문 (`AskUserQuestion`). 자동 결정 금지.

### Pitfall 2: stale Related Files

**Symptom**: 삭제된 파일 경로가 Related Files 에 그대로 남음.

**Cause**: UPDATE 가 추가만 하고 제거 안 함.

**Prevention**: Mode 2 에서 UPDATE 시 항상 stale path 제거 단계 포함. 단, 제거는 사용자 승인 후.

---

## Validation

스킬 생성/수정 직후 다음 도구로 자가 검증:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check-skill-frontmatter.py" .claude/skills/verify-{name}/SKILL.md
```

JSON 출력으로 다른 스킬과 chaining 가능:
```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check-skill-frontmatter.py" .claude/skills/verify-*/SKILL.md --json
```

검증 항목:
1. YAML frontmatter valid + required fields 존재
2. 6개 필수 섹션 (Purpose/When to Run/Related Files/Workflow/Output Format/Exceptions) 모두 존재
3. Related Files 의 경로가 실제 존재 (또는 glob 패턴이 매칭)
4. allowed-tools 가 위험 패턴 (`Bash(*)`, 무제한 `rm`) 포함 안 함

---

## End-of-skill reflection

Mode 2 / Mode 3 종료 후 사용자에게 보고할 때, 칭찬하지 말고 패턴을 관찰한다 (3개 항목, hedge 사용):

```
드리프트 5건 정정 완료. 패턴 관찰:

- 5건 중 4건이 Coverage Gap (새 파일이 어떤 verify 에도 매핑 안 됨) → 새 도메인이 자주 추가되는 단계로 보임. verify-* 분할 단위가 너무 굵어서일 수 있음.
- Invalid Reference 1건 → 파일 이동 빈도가 낮은 편. 다음 점검 주기는 여유 가능.
- Missing Check 0건 → 기존 패턴 정확도는 양호. 다만 새 도메인 1건은 다음 PR 까지 사용자 정의 검증 필요.

다음 권장: /verify-implementation 으로 정정된 스킬들 통합 실행
```

---

## Supporting files

| 파일 | 용도 |
|------|------|
| [`references/drift-detection.md`](references/drift-detection.md) | 변경 ↔ 스킬 매핑 알고리즘 + 4종 갭 분류 기준 |
| [`references/decision-matrix.md`](references/decision-matrix.md) | CREATE / UPDATE / EXEMPT 판정 매트릭스 (BEFORE/AFTER 예시 포함) |
| [`references/example-drift-report.md`](references/example-drift-report.md) | Mode 1 산출물 예시 |
| [`references/example-verify-skill-template.md`](references/example-verify-skill-template.md) | 6개 필수 섹션 템플릿 (CREATE 시 채움) |
| [`scripts/check-skill-frontmatter.py`](scripts/check-skill-frontmatter.py) | verify-* 스킬 frontmatter + 필수 섹션 자가 검증. `--help` / `--json` 지원. stdlib only |

---

## Self-check before publishing changes (사람용)

새/수정된 verify-* 스킬을 발행 전 다음 7개 항목 모두 확인:

- [ ] `check-skill-frontmatter.py` 통과
- [ ] 6개 필수 섹션 모두 존재 (Purpose / When to Run / Related Files / Workflow / Output Format / Exceptions)
- [ ] Related Files 경로가 실제 존재 또는 glob 매칭
- [ ] Workflow 의 탐지 명령어 dry-run PASS
- [ ] PASS/FAIL 기준 명시적 (모호한 "잘 작동" 등 금지)
- [ ] Exceptions 가 현실적 (모든 케이스 면제하는 게으른 면제 금지)
- [ ] (Mode 3 인 경우) 프로젝트 verify-implementation 의 하드코딩 목록과 일치
