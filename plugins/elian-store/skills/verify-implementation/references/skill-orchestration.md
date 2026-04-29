# Skill Orchestration — 동적 탐색 + Workflow 파싱 + Exceptions 매칭

verify-implementation 의 핵심 로직. SKILL.md 의 Mode 1 Step 1-2 를 상세히 풀어둔 reference.

---

## Step 1: 동적 탐색

```
Glob pattern=".claude/skills/verify-*/SKILL.md"
```

또는 Bash:
```bash
find .claude/skills -maxdepth 2 -type d -name 'verify-*' | xargs -I {} test -f {}/SKILL.md && echo {}
```

각 발견된 SKILL.md 의 frontmatter 에서:
- `name` — 실행 대상 이름
- `description` — 사용자에게 보여줄 표

자기 자신 제외:
```
filtered = [s for s in skills if s.name != "verify-implementation"]
```

`manage-skills` 는 `verify-` 접두사가 아니므로 자동 제외됨.

---

## "수동 실행 전용" 표식 검사

각 SKILL.md 본문에서:

```python
content = read_skill_md(skill)
manual_only = bool(re.search(r'수동 실행 전용|수동 실행', content))
```

`manual_only=True` 인 스킬은 Mode 1 (run-all) 에서 SKIP. 표시:

```markdown
### verify-{name} SKIP (수동 실행 전용)
이 스킬은 파괴적 작업을 포함할 수 있습니다.
실행하려면: `/elian-store:verify-implementation verify-{name}`
```

Mode 2 (run-specific) 로 명시 호출 시는 정상 실행.

---

## Workflow 섹션 파싱

각 SKILL.md 의 `## Workflow` 섹션에서 검사 항목별로:

1. **항목 제목** — `### N. {제목}` 또는 `#### N. {제목}`
2. **탐지 명령어** — 코드블록 안의 Grep / Glob / Bash 명령
3. **PASS 기준** — "PASS 기준:" 또는 "✓" 가 들어간 줄
4. **FAIL 시 동작** — "FAIL 시:" 또는 보고 형식 정의

### 명령어 추출 예시

SKILL.md:
````markdown
### 1. Controller 명명 규칙

**탐지**:
```bash
grep -rE 'class\s+\w+Controller' src/main/java/
```

**PASS 기준**: 모든 controller 가 `*Controller` 접미사
````

추출:
```python
{
    "id": 1,
    "title": "Controller 명명 규칙",
    "command_type": "bash",
    "command": "grep -rE 'class\\s+\\w+Controller' src/main/java/",
    "pass_criteria": "모든 controller 가 *Controller 접미사",
}
```

---

## Exceptions 섹션 파싱

`## Exceptions` 섹션에서 면제 패턴 추출:

````markdown
## Exceptions

다음은 위반이 아닙니다:

1. **테스트 파일** (`**/__tests__/**`, `*.spec.ts`) — 명명 규칙 면제
2. **legacy migration** (`src/legacy/**`) — 일시 면제
````

추출:
```python
[
    {"category": "테스트 파일", "patterns": ["**/__tests__/**", "*.spec.ts"]},
    {"category": "legacy migration", "patterns": ["src/legacy/**"]},
]
```

매칭 시:
```python
def is_exempted(file, exceptions):
    for ex in exceptions:
        if any(fnmatch.fnmatch(file, p) for p in ex.patterns):
            return True, ex.category
    return False, None
```

---

## 실행 흐름

```
for skill in filtered_skills:
    if manual_only(skill):
        emit SKIP(skill); continue
    workflow = parse_workflow(skill)
    exceptions = parse_exceptions(skill)
    issues = []
    exempted = []
    for check in workflow:
        result = execute(check.command)
        for hit in result:
            if is_exempted(hit, exceptions):
                exempted.append(hit)
                continue
            if not matches_pass_criteria(hit, check):
                issues.append(Issue(skill, check, hit))
    emit SkillResult(skill, issues, exempted)
```

---

## 자동 수정 (Step 4-5)

각 issue 에 `fix_suggestion` 이 있으면 자동 수정 가능. 없으면 수동 표시.

`fix_suggestion` 결정 로직:
- SKILL.md 의 검사 항목에 "수정 권장:" 또는 "FAIL 시:" 코드 예시가 있으면 → 자동 수정 가능
- 코드 예시가 모호하거나 도메인 로직 영향이면 → 수동

자동 수정 적용 후 **이슈 있던 스킬만** 재실행 (cross-check 는 사용자 선택).

---

## Output Format 통일

각 verify-* 가 자체 Output Format 을 가지지만, verify-implementation 의 통합 보고서는 일관된 형식으로 모음:

```markdown
| 검증 스킬 | 상태 | 이슈 수 | 상세 |
|-----------|------|---------|------|
| verify-X | PASS / FAIL | N | 요약 |
```

상세는 항목별 "발견된 이슈" 표 (스킬 / 파일 / 문제 / 수정 방법) 로.

---

## 에지 케이스

### 1. SKILL.md frontmatter parse 실패

frontmatter 가 valid YAML 이 아니면 → 해당 스킬 SKIP + 경고:
```
verify-{name} SKILL.md 파싱 실패 — frontmatter YAML 오류
/elian-store:manage-skills 로 SKILL.md 보강 권장
```

### 2. Workflow 섹션 부재

`## Workflow` 가 없으면 → SKIP + 경고:
```
verify-{name} 에 Workflow 섹션 부재 — 검사 명령어 정의 필요
```

### 3. 실행 명령어 자체 실패 (timeout, syntax error)

해당 검사만 FAIL 처리 + 명령어 출력 그대로 표시. 다른 검사는 계속.

### 4. 동일 파일에 다중 위반

같은 파일이 여러 검사에서 위반 → 검사별로 별도 row 로 보고. 중복 제거 안 함 (각 검사가 다른 이유로 FAIL).

---

## verify-* 스킬에서 expected 한 SKILL.md 구조

verify-implementation 가 정상 동작하려면 각 verify-* SKILL.md 에 다음 섹션이 필요:

| 섹션 | 용도 | 필수? |
|------|------|------|
| `Purpose` | 사용자 안내 | 권장 |
| `When to Run` | 사용자 안내 | 권장 |
| `Related Files` | 검사 대상 힌트 (orchestrator 에는 미사용) | 권장 |
| `Workflow` | 검사 항목 + 명령어 + PASS 기준 | **필수** |
| `Output Format` | 결과 표시 형식 (orchestrator 에는 미사용) | 권장 |
| `Exceptions` | 면제 패턴 | **필수** (없으면 면제 처리 불가) |

manage-skills 의 `check-skill-frontmatter.py` 가 이 6개 섹션 모두 검사.
