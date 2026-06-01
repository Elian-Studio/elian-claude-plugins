# Codex Prompt Quality Rubric (100점 만점, 휴리스틱)

`codex/prompts/*.md` 채점 기준. `scripts/score_codex_prompt.py` 의 신호와 1:1 일치.
Codex 프롬프트는 frontmatter/`allowed-tools` 가 없고 권한이 `~/.codex/config.toml` 책임이므로, SKILL.md 와는 다른 축으로 채점한다. (Claude SKILL.md 쪽은 자동 채점 게이트 없이 수동 리뷰로 운영한다.)

LLM 호출 없음. stdlib only. 결정적. 통과 = 90/100, 미달 = 머지 차단.

| # | 축 | 배점 | 신호 |
|---|---|---|---|
| 1 | 명령·목적 계약 | 15 | H1 이 파일명 기반 slash command 를 명시 (+5), 목적/Purpose 섹션 (+5), `$ARGUMENTS` 계약 (+5) |
| 2 | 사용 범위·경계 | 15 | 사용 조건/trigger (+5), 비사용·금지 경계 (+5), 입력 범위·판정·폴백 기준 (+5) |
| 3 | Workflow 절차 정합 | 15 | Workflow/Procedure/절차 존재 (+10), Phase/Step 번호가 drift 없이 이어짐 (+5) |
| 4 | Safety / approval posture | 15 | read-only/approval/ask-and-stop 같은 안전 태도 (+6), Codex 권한 모델/config 언급 (+4), 파괴적 명령 문자열 없음 (+5) |
| 5 | 독립 트리 drift 가드 | 15 | 독립 트리/수동 동기화/drift 경고 (+8), Claude `SKILL.md` 카운터파트 상호참조 (+7) |
| 6 | 인자 규약 | 8 | `$ARGUMENTS` 또는 `$1`/`$2` Codex 인자 규약 사용 |
| 7 | 출력·산출물 계약 | 12 | fenced output/template 예시 (+4), OUTPUT FORMAT/산출물/handoff 계약 (+4), 5블록을 쓰는 prompt는 순서 보존 (+4) |
| 8 | 라인 예산 | 5 | 자기완결 프롬프트 ≤320줄 (초과 시 2점) |

## 설계 의도

- **축 1·3·5 가 drift 방어의 핵심.** 독립 2-트리는 산문 스펙 ↔ 절차 본문 ↔ Claude counterpart 불일치 위험을 키우므로, 게이트가 command identity·workflow 정합·카운터파트 상호참조를 결정적으로 검사한다.
- **권한 축 없음.** Codex 는 `allowed-tools` 가 아니라 `config.toml` 의 `sandbox_mode`/`approval_policy` 로 통제. 프롬프트는 read-only 를 *지시문*으로 명시하는지만 본다(축 4).
- **5블록은 persona-review 전용 계약.** 다른 Codex prompt 는 자기 목적에 맞는 출력·산출물 계약을 쓰면 된다.
- **로컬 검증**: `python3 scripts/score_codex_prompt.py codex/prompts/*.md` / `--json` / `--output <path>`.
