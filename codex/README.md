# codex/ — OpenAI Codex CLI 설정 트리

이 트리는 `plugins/` (Claude Code 마켓플레이스) 와 **완전히 독립**된, Codex CLI 용 배포 가능 설정 묶음이다.

| | Claude Code | Codex CLI |
|---|---|---|
| 진입점 | `plugins/elian-store/skills/*/SKILL.md` (YAML frontmatter) | `codex/prompts/*.md` (순수 마크다운, 파일명 = `/명령`) |
| 프로젝트 지침 | `CLAUDE.md` + `.claude/` | `AGENTS.md` + `~/.codex/config.toml` |
| 권한 모델 | frontmatter `allowed-tools` | `config.toml` 의 `approval_policy` / `sandbox_mode` |
| 배포 | marketplace.json 으로 install | 사용자가 파일을 `~/.codex/` 로 복사/심볼릭 |
| 품질 게이트 | `scripts/score_skill.py` (10축×10점) | `scripts/score_codex_prompt.py` (경량 구조 검사) |

## ⚠️ Drift 경고 (의도된 트레이드오프)

이 repo 는 **독립 2-트리** 모델을 택했다. **단일 진실원이 없다.** `codex/prompts/persona-review.md` 와 `plugins/elian-store/skills/persona-review/SKILL.md` 는 *별개 파일* 이고, 한쪽 로직을 바꾸면 다른 쪽 동기화는 **작성자 수동 책임**이다.

> 한쪽만 고치고 다른 쪽을 잊으면 두 도구의 동작이 갈린다. 이게 정확히 v2.5.0 에서 잡았던 "산문↔절차 drift" 버그의 트리-레벨 버전이다. PR 시 두 파일 diff 를 같이 확인하라.

## 설치

```bash
# 1) 커스텀 프롬프트 (스킬 analog) — /persona-review 로 호출 가능해짐
mkdir -p ~/.codex/prompts
rm -f ~/.codex/prompts/on-call-elian.md  # legacy command cleanup
cp codex/prompts/*.md ~/.codex/prompts/

# 2) 프로젝트 지침 (선택) — 작업 repo 루트에 두거나 ~/.codex/AGENTS.md 로
cp codex/AGENTS.md ~/.codex/AGENTS.md

# 3) 전역 설정 (선택) — 모델/승인/샌드박스 기본값
cp codex/config.toml.example ~/.codex/config.toml   # 그 후 직접 편집
```

설치 후 Codex TUI 에서 `/persona-review <target> [--persona daniel|evans|dean|martin|<path>] [--depth quick|deep|interview]` 로 사용.

## 구조

```
codex/
  README.md            ← 이 파일
  AGENTS.md            ← Codex 프로젝트 지침 템플릿 (Daniel standing rules)
  prompts/
    persona-review.md  ← /persona-review 의 Codex 네이티브 포팅 (레퍼런스)
  config.toml.example  ← ~/.codex/config.toml 샘플 (read-only 리뷰 안전 기본값)
```

스킬 포팅 범위: 현재 `persona-review` 1개만 (레퍼런스). 나머지 elian-store 스킬은 패턴 검증 후 점진 추가.

Claude/Codex catalog parity 현황과 포팅 순서는 [`../docs/claude-codex-skill-parity.md`](../docs/claude-codex-skill-parity.md) 를 기준으로 관리한다.
