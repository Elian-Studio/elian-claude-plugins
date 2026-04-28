<!--
PR 작성 가이드:
- SKILL.md 변경 시 자동으로 Skill Quality Gate (90점) 가 작동합니다.
- 정적 검증 + LLM 평가 (claude-sonnet-4-6 기준) 가 PR 코멘트로 결과를 게시합니다.
- 점수가 90 미만이면 머지가 차단됩니다 (브랜치 보호 규칙).
- 평가 루브릭은 scripts/rubric.md 참조.
-->

## 변경 요약

<!-- 한 줄로 무엇을 바꿨는지 -->

## 변경 유형

- [ ] 신규 플러그인 추가 (`plugins/<name>/` 디렉토리)
- [ ] 기존 플러그인 기능 추가 (MINOR — `1.0.0 → 1.1.0`)
- [ ] 기존 플러그인 버그 수정 (PATCH — `1.0.0 → 1.0.1`)
- [ ] 기존 플러그인 호환성 깨짐 (MAJOR — `1.0.0 → 2.0.0`)
- [ ] 마켓플레이스 메타데이터 변경 (스킬 자체 변경 없음)
- [ ] 인프라/문서/CI 변경 (스킬 자체 변경 없음)

## 체크리스트

### 항상

- [ ] `feature/*` 또는 `fix/*` 브랜치에서 작업 (직접 main 푸시 금지)
- [ ] PR 단일 책임 (한 플러그인의 한 가지 변경)

### SKILL.md 변경 시

- [ ] `plugin.json` 의 `version` bump 완료
- [ ] `marketplace.json` 의 해당 플러그인 `version` bump 완료 (둘 다 bump 권장)
- [ ] `CHANGELOG.md` 에 변경사항 기록 (Added / Changed / Fixed / Removed)
- [ ] 로컬에서 정적 검증 통과 — `bash scripts/static_checks.sh <SKILL.md>`
- [ ] (선택) 로컬에서 LLM 평가 통과 — `ANTHROPIC_API_KEY=... python scripts/evaluate_skill.py <SKILL.md>`

### 신규 플러그인 추가 시

- [ ] `plugins/<name>/.claude-plugin/plugin.json` 작성
- [ ] `marketplace.json` 의 `plugins[]` 에 신규 엔트리 추가
- [ ] `README.md` 의 플러그인 목록 업데이트
- [ ] LICENSE 명시 (`plugin.json.license`)

## Skill Quality Gate 점수 (수동 사전 점검)

PR 생성 후 자동 평가가 게시됩니다. 사전에 어떤 축에서 점수 손실이 예상되는지 자가 점검:

- [ ] 1. Frontmatter 규약 (10/10 예상)
- [ ] 2. Description 자동 호출 신뢰성 (10/10 예상)
- [ ] 3. Progressive Disclosure (10/10 예상)
- [ ] 4. Standing Instructions (10/10 예상)
- [ ] 5. 예시 완결성 (10/10 예상)
- [ ] 6. Anti-pattern / Failure-mode (10/10 예상)
- [ ] 7. Validation 자가 검증 (10/10 예상)
- [ ] 8. 보안 / 권한 (10/10 예상)
- [ ] 9. 일반화 / 휴대성 (10/10 예상)
- [ ] 10. 의사결정·산출물 설계 (10/10 예상)

**예상 총점**: ___ / 100 (90 이상 필요)

## 관련 이슈 / 컨텍스트

<!-- Closes #N, Refs #M, 또는 결정 배경 -->
