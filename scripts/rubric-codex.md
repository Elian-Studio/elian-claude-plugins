# Codex Prompt Quality Rubric (100점 만점, 휴리스틱)

`codex/prompts/*.md` 채점 기준. `scripts/score_codex_prompt.py` 의 신호와 1:1 일치.
Claude `scripts/rubric.md` (SKILL.md 용) 와 **독립** — Codex 프롬프트는 frontmatter/`allowed-tools` 가 없고 권한이 `~/.codex/config.toml` 책임이므로 축이 다르다.

LLM 호출 없음. stdlib only. 결정적. 통과 = 90/100, 미달 = 머지 차단.

| # | 축 | 배점 | 신호 |
|---|---|---|---|
| 1 | 5블록 잠금 계약 | 20 | `결론·트레이드오프·운영 리스크·압박 질문·다음 질문` 5개 모두 등장(비례 배점) + **등장 순서가 잠금 순서와 일치** (순서 어긋나면 10점 상한) |
| 2 | Phase 절차 정합 | 15 | `Phase 1~5` 모두 명시 (+10). 본문에 `Phase 6` 미등장 (+5) — Phase 6 언급은 절차 본문↔목록 불일치(drift) 신호 (v2.5.0 PR 에서 잡은 버그 클래스) |
| 3 | Standing 규칙 | 15 | `Forbidden` 섹션 (+8), `Pre-flight`/self-check 섹션 (+7) |
| 4 | Read-only 계약 | 15 | read-only/읽기 전용 명시 (+10), 파괴적 명령 문자열(`rm -rf`/`git push --force`/`git reset --hard`/`DROP TABLE`) 미포함 (+5) |
| 5 | 독립 트리 drift 가드 | 15 | 독립 트리/수동 동기화/drift 경고 (+8), Claude `SKILL.md` 카운터파트 상호참조 (+7) |
| 6 | 인자 규약 | 8 | `$ARGUMENTS` 또는 `$1`/`$2` Codex 인자 규약 사용 |
| 7 | 출력 템플릿 | 7 | 펜스된(```markdown```) 출력 템플릿 + `## 결론` 포함 |
| 8 | 라인 예산 | 5 | 자기완결 프롬프트 ≤320줄 (초과 시 2점) |

## 설계 의도

- **축 1·2·5 가 drift 방어의 핵심.** `/on-call-elian` v2.5.0 리뷰에서 잡은 결함은 "산문 스펙 ↔ 절차 본문 번호 불일치" 였다. 독립 2-트리는 그 위험을 트리 레벨로 키우므로(단일 진실원 없음), 게이트가 5블록 순서·Phase 정합·카운터파트 상호참조를 결정적으로 검사한다.
- **권한 축 없음.** Codex 는 `allowed-tools` 가 아니라 `config.toml` 의 `sandbox_mode`/`approval_policy` 로 통제. 프롬프트는 read-only 를 *지시문*으로 명시하는지만 본다(축 4).
- **로컬 검증**: `python3 scripts/score_codex_prompt.py codex/prompts/on-call-elian.md` / `--json` / `--output <path>`.
