#!/usr/bin/env bash
# 결정적 정적 검증. LLM 호출 전에 fail-fast.
# 사용법: bash scripts/static_checks.sh <SKILL.md path>
# Exit 0: pass / Exit 1: blocking fail

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <SKILL.md path>" >&2
  exit 2
fi

FILE="$1"
ERRORS=()
WARNINGS=()

if [[ ! -f "$FILE" ]]; then
  echo "::error file=$FILE::파일이 존재하지 않음"
  exit 1
fi

# 1. Frontmatter 추출 가능 확인 (--- ... --- 블록)
if ! head -n 1 "$FILE" | grep -qE '^---\s*$'; then
  ERRORS+=("$FILE:1: 파일 첫 줄이 '---' 가 아님 (YAML frontmatter 누락)")
fi

# 2. Frontmatter 종료 마커 존재
FM_END=$(awk '/^---\s*$/{c++; if(c==2){print NR; exit}}' "$FILE")
if [[ -z "$FM_END" ]]; then
  ERRORS+=("$FILE: YAML frontmatter 종료 마커(---) 없음")
fi

# 3. description 필드 존재 (권장이지만 강제)
if ! awk -v end="$FM_END" 'NR<end && /^description:/{found=1} END{exit !found}' "$FILE"; then
  ERRORS+=("$FILE: frontmatter 에 'description' 필드 누락 (권장 필드)")
fi

# 4. description + when_to_use 합산 1,536자 이내
COMBINED_LEN=$(awk -v end="$FM_END" '
  NR<end && /^description:/ { sub(/^description:[[:space:]]*/, ""); d=$0 }
  NR<end && /^when_to_use:/  { sub(/^when_to_use:[[:space:]]*/,  ""); w=$0 }
  END { print length(d) + length(w) }
' "$FILE")
if (( COMBINED_LEN > 1536 )); then
  ERRORS+=("$FILE: description + when_to_use 합산 ${COMBINED_LEN}자 (1,536 캡 초과 — 자동 호출 매칭 불안정)")
fi

# 5. 본문 줄 수 (전체 - frontmatter)
TOTAL_LINES=$(wc -l < "$FILE")
BODY_LINES=$(( TOTAL_LINES - FM_END ))
if (( BODY_LINES > 500 )); then
  ERRORS+=("$FILE: 본문 ${BODY_LINES}줄 (공식 권장 500줄 초과 — reference 분리 필요)")
elif (( BODY_LINES > 400 )); then
  WARNINGS+=("$FILE: 본문 ${BODY_LINES}줄 (500줄 한계 근접)")
fi

# 6. 중첩 HTML 주석 (template 누수 방지) — SKILL.md 동일 디렉토리의 .html 파일만 검사
SKILL_DIR=$(dirname "$FILE")
while IFS= read -r -d '' html; do
  if awk '/<!--.*<!--/' "$html" | grep -q .; then
    ERRORS+=("$html: 중첩 HTML 주석 발견 — 첫 --> 가 외부 주석 종료시킴")
  fi
done < <(find "$SKILL_DIR" -maxdepth 2 -name '*.html' -print0 2>/dev/null)

# 7. name 필드 kebab-case + 길이
NAME_VAL=$(awk -v end="$FM_END" 'NR<end && /^name:/ {sub(/^name:[[:space:]]*/,""); print; exit}' "$FILE")
if [[ -n "$NAME_VAL" ]]; then
  if [[ ${#NAME_VAL} -gt 64 ]]; then
    ERRORS+=("$FILE: name '$NAME_VAL' 64자 초과")
  fi
  if ! [[ "$NAME_VAL" =~ ^[a-z0-9-]+$ ]]; then
    ERRORS+=("$FILE: name '$NAME_VAL' kebab-case 위반 (소문자/숫자/하이픈만 허용)")
  fi
  # 디렉토리명과 일치 확인
  DIR_NAME=$(basename "$(dirname "$FILE")")
  if [[ "$NAME_VAL" != "$DIR_NAME" ]]; then
    WARNINGS+=("$FILE: name '$NAME_VAL' 가 디렉토리명 '$DIR_NAME' 와 다름")
  fi
fi

# 8. allowed-tools 위험 패턴
if awk -v end="$FM_END" 'NR<end && /^allowed-tools:/ {print; found=1} END{exit !found}' "$FILE" | grep -qE 'Bash\(\*\)|Bash\(rm \*\)$|Bash\(sudo'; then
  ERRORS+=("$FILE: allowed-tools 에 위험 패턴 발견 (Bash(*) / Bash(rm *) / Bash(sudo*))")
fi

# 결과 출력
echo "=== Static checks: $FILE ==="
if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo ""
  echo "Warnings:"
  for w in "${WARNINGS[@]}"; do
    echo "  ⚠ $w"
    echo "::warning::$w"
  done
fi

if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo ""
  echo "Errors (blocking):"
  for e in "${ERRORS[@]}"; do
    echo "  ✗ $e"
    echo "::error::$e"
  done
  echo ""
  echo "❌ STATIC CHECKS FAILED — LLM 평가 단계 진입 차단"
  exit 1
fi

echo ""
echo "✓ Static checks passed (lines=$BODY_LINES, desc+when_to_use=${COMBINED_LEN}자)"
exit 0
