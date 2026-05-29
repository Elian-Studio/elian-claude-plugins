#!/usr/bin/env python3
"""SKILL.md 휴리스틱 채점 (100점 만점, 90 미만 → exit 1).

LLM 호출 없이 결정적 신호로 10축 × 10점을 채점한다.
각 축의 채점 신호는 scripts/rubric.md 와 일치한다.

사용법:
    python3 scripts/score_skill.py <SKILL.md path> [<SKILL.md path>...]
    python3 scripts/score_skill.py <SKILL.md path> --json
    python3 scripts/score_skill.py --help

환경변수:
    SKILL_EVAL_PASS_SCORE  통과 점수 (기본: 90)
    SKILL_EVAL_OUTPUT      JSON 결과 저장 경로 (기본: evaluation-results.json)

종료 코드:
    0  모든 입력이 90점 이상
    1  하나 이상 90점 미만
    2  사용법 오류 / 파일 없음
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


PASS_SCORE = int(os.environ.get("SKILL_EVAL_PASS_SCORE", "90"))
OUTPUT_PATH = os.environ.get("SKILL_EVAL_OUTPUT", "evaluation-results.json")


# ---------- frontmatter 파싱 (YAML 의존 없이) ----------


def decode_frontmatter_value(value: str) -> str:
    """Decode the simple quoted scalar forms this repository uses."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        inner = value[1:-1]
        if value[0] == "'":
            return inner.replace("''", "'")
        return inner.replace(r"\"", '"').replace(r"\\", "\\")
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, str], int, str]:
    """frontmatter 의 단순 키:값 추출. 본문과 frontmatter 라인 끝 위치 반환.

    YAML 라이브러리에 의존하지 않기 위해 단순 라인 파싱. 멀티라인 / 중첩은 무시.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ({}, 0, text)
    fm: dict[str, str] = {}
    end = 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        m = re.match(r"^([a-zA-Z_-][a-zA-Z0-9_-]*)\s*:\s*(.*)$", lines[i])
        if m:
            key, value = m.group(1), m.group(2).strip()
            fm[key] = decode_frontmatter_value(value)
    body = "\n".join(lines[end + 1 :]) if end else text
    return (fm, end, body)


def frontmatter_yaml_syntax_issues(text: str) -> list[str]:
    """Catch YAML-unsafe metadata patterns without adding a YAML dependency.

    The production loader is a YAML parser, while this scorer intentionally stays
    stdlib-only. These checks target the high-risk plain-scalar cases that break
    real YAML parsing or coerce string metadata into YAML collections.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ["missing YAML frontmatter opening delimiter"]

    issues: list[str] = []
    closed = False
    for i in range(1, len(lines)):
        raw = lines[i]
        line = raw.strip()
        if line == "---":
            closed = True
            break
        if not line or line.startswith("#"):
            continue
        if raw.startswith((" ", "\t")):
            continue
        m = re.match(r"^([a-zA-Z_-][a-zA-Z0-9_-]*)\s*:\s*(.*)$", raw)
        if not m:
            issues.append(f"line {i + 1}: not a simple YAML key/value pair")
            continue
        key, value = m.group(1), m.group(2).strip()
        if not value:
            continue
        if value in {"|", ">", "|-", ">-", "|+", ">+"}:
            continue
        if value[0] in {"'", '"'}:
            if len(value) < 2 or value[-1] != value[0]:
                issues.append(f"line {i + 1}: {key} has an unterminated quoted scalar")
            continue
        if value[0] in {"[", "{"}:
            issues.append(
                f"line {i + 1}: {key} starts with a YAML collection marker; quote it if it is text"
            )
        if ": " in value:
            issues.append(
                f"line {i + 1}: {key} contains ': ' in an unquoted scalar; quote it"
            )

    if not closed:
        issues.append("missing YAML frontmatter closing delimiter")
    return issues


# ---------- 보조 함수 ----------


def has_section(body: str, *patterns: str) -> bool:
    """헤딩(##/###) 또는 굵은 텍스트로 패턴이 나타나는지 확인."""
    for pat in patterns:
        if re.search(rf"^#+\s+.*{pat}", body, re.MULTILINE | re.IGNORECASE):
            return True
        if re.search(rf"\*\*[^*]*{pat}[^*]*\*\*", body, re.IGNORECASE):
            return True
    return False


def file_exists_in_skill_dir(skill_dir: Path, *names: str) -> bool:
    return any((skill_dir / n).exists() for n in names)


def find_in_subdir(skill_dir: Path, subdir: str, *exts: str) -> list[Path]:
    target = skill_dir / subdir
    if not target.exists():
        return []
    out: list[Path] = []
    for p in target.rglob("*"):
        if p.is_file() and (not exts or p.suffix in exts):
            out.append(p)
    return out


# ---------- 10개 축 채점 ----------


def axis1_frontmatter(
    fm: dict[str, str], path: Path, yaml_issues: list[str]
) -> tuple[int, str, list[str]]:
    score = 0
    why: list[str] = []
    improvements: list[str] = []
    if yaml_issues:
        improvements.extend(f"YAML frontmatter issue: {issue}" for issue in yaml_issues)

    if fm:
        score += 2
    else:
        improvements.append("YAML frontmatter 블록(---)이 없음")

    name = fm.get("name", "")
    if name:
        if re.fullmatch(r"[a-z0-9-]+", name) and len(name) <= 64:
            score += 2
            # 디렉토리명 일치 (가산점)
            dir_name = path.parent.name
            if name == dir_name:
                score += 1
            else:
                improvements.append(
                    f"name '{name}' 가 디렉토리명 '{dir_name}' 와 다름"
                )
        else:
            improvements.append(
                f"name '{name}' kebab-case 위반 또는 64자 초과"
            )
    else:
        improvements.append("name 필드 누락 (디렉토리명 자동 사용 가능하지만 명시 권장)")

    if fm.get("description"):
        score += 2
    else:
        improvements.append("description 필드 누락")

    if fm.get("when_to_use"):
        score += 1
    elif len(fm.get("description", "")) >= 150:
        score += 1  # description 자체가 충분히 자세하면 가산
    else:
        improvements.append("when_to_use 필드 또는 충분한 description 필요")

    if fm.get("argument-hint"):
        score += 1

    if fm.get("allowed-tools"):
        score += 1

    score = min(score, 10)
    if yaml_issues:
        score = 0
    why.append(
        f"필드 충족: name={'O' if name else 'X'}, "
        f"description={'O' if fm.get('description') else 'X'}, "
        f"when_to_use={'O' if fm.get('when_to_use') else 'X'}, "
        f"argument-hint={'O' if fm.get('argument-hint') else 'X'}, "
        f"allowed-tools={'O' if fm.get('allowed-tools') else 'X'}"
    )
    return (score, "; ".join(why), improvements)


def axis2_description(fm: dict[str, str]) -> tuple[int, str, list[str]]:
    score = 0
    improvements: list[str] = []
    desc = fm.get("description", "")
    when = fm.get("when_to_use", "")
    combined_len = len(desc) + len(when)

    if 0 < combined_len <= 1536:
        score += 3
    elif combined_len > 1536:
        improvements.append(
            f"description+when_to_use 합산 {combined_len}자 (1536 초과 — 자동 호출 매칭 불안정)"
        )

    # outcome-focused 감지: "When ..." / "when ..." 으로 시작하거나 포함
    desc_lower = desc.lower()
    if desc_lower.startswith("when "):
        score += 3
    elif " when " in desc_lower or "상황" in desc:
        score += 2
    else:
        improvements.append(
            "description 이 상황(When ...)으로 시작하지 않음 — 자동 호출 신뢰성 약화"
        )

    # process-focused 단어 첫 단어 회피 가산
    first_word = desc.strip().split(" ", 1)[0].lower() if desc else ""
    if first_word in {"generate", "create", "make", "build"}:
        improvements.append(
            f"description 첫 단어 '{first_word}' — outcome 보다 process 중심. 'When 3+ ...' 같은 상황 우선 권장"
        )
    else:
        score += 2

    # 트리거 문구 신호 (when_to_use 또는 description 안에 따옴표/예시 포함)
    if re.search(r'["\'].*?["\']', when) or re.search(r'["\'].*?["\']', desc):
        score += 2

    score = min(score, 10)
    return (
        score,
        f"합산 {combined_len}자, outcome-focused 감지: "
        + ("Y" if "when" in desc_lower or "상황" in desc else "N"),
        improvements,
    )


def axis3_progressive_disclosure(
    body: str, skill_dir: Path
) -> tuple[int, str, list[str]]:
    score = 0
    improvements: list[str] = []
    body_lines = len(body.splitlines())

    if body_lines <= 400:
        score += 5
    elif body_lines <= 500:
        score += 4
    else:
        score += 1
        improvements.append(f"본문 {body_lines}줄 (500줄 초과)")

    refs = find_in_subdir(skill_dir, "references", ".md", ".html", ".txt")
    scripts = find_in_subdir(skill_dir, "scripts", ".py", ".sh")
    if refs and scripts:
        score += 3
    elif refs or scripts:
        score += 2
        improvements.append(
            "references/ + scripts/ 둘 다 있을 때 만점 (현재 한쪽만 있음)"
        )
    else:
        improvements.append(
            "references/ 또는 scripts/ 디렉토리 부재 — 큰 reference 분리 권장"
        )

    # SKILL.md 가 reference 파일을 링크하는지
    if re.search(r"\[[^\]]+\]\(\s*(references|scripts)/", body):
        score += 2
    else:
        improvements.append(
            "SKILL.md 가 references/ 또는 scripts/ 의 파일을 명시적으로 링크하지 않음"
        )

    score = min(score, 10)
    return (
        score,
        f"본문 {body_lines}줄, references={len(refs)}개, scripts={len(scripts)}개",
        improvements,
    )


def axis4_standing_instructions(body: str) -> tuple[int, str, list[str]]:
    score = 0
    improvements: list[str] = []

    has_modes = has_section(body, "Modes?", "모드")
    has_standing = has_section(body, "Standing", "standing rule", "원칙")
    has_procedure = has_section(body, "Procedure", "절차", "Generation procedure")

    if has_modes:
        score += 4
    elif has_standing:
        score += 3
    else:
        improvements.append(
            "Modes 또는 Standing rules 섹션 부재 — 컨텍스트별 흐름 분리 권장"
        )

    if has_procedure:
        score += 3

    # 절차 동사 밀도: "1. " "Step N:" 마커 카운트 vs 전체 줄 수
    proc_markers = len(re.findall(r"^(?:Step\s+\d+|[0-9]+\.)\s", body, re.MULTILINE))
    body_lines = max(1, len(body.splitlines()))
    density = proc_markers / body_lines
    if density < 0.05:
        score += 3
    elif density < 0.10:
        score += 2
    else:
        score += 1
        improvements.append(
            f"절차 동사 밀도 높음 ({density:.1%}) — standing 문장 비중 늘리기"
        )

    score = min(score, 10)
    return (
        score,
        f"modes={has_modes}, standing={has_standing}, procedure={has_procedure}, 절차밀도={density:.1%}",
        improvements,
    )


def axis5_examples(body: str, skill_dir: Path) -> tuple[int, str, list[str]]:
    score = 0
    improvements: list[str] = []

    refs = find_in_subdir(skill_dir, "references", ".md", ".html")
    if refs:
        score += 5
        # 줄 수 합이 50줄 이상이면 충분한 예시 간주
        total_lines = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in refs)
        if total_lines >= 50:
            pass  # 이미 가산됨
        else:
            improvements.append(
                f"references/ 의 예시 합산 {total_lines}줄 — 좀 더 풍부한 예시 권장"
            )
    else:
        improvements.append("references/ 부재 — 완성된 예시 1개 이상 필요")

    # BEFORE/AFTER 또는 비교 표 신호
    if re.search(r"BEFORE|AFTER|나쁨|좋음|❌|✅", body):
        score += 3

    # 셀프 체크리스트 신호: "[ ]" 가 5개 이상
    if len(re.findall(r"\[\s\]", body)) >= 5:
        score += 2
    elif refs:
        # references 안의 체크리스트도 인정
        for p in refs:
            txt = p.read_text(encoding="utf-8")
            if len(re.findall(r"\[\s\]", txt)) >= 5:
                score += 2
                break
        else:
            improvements.append("체크리스트 부재 — 발행 전 self-check 권장")

    score = min(score, 10)
    return (score, f"references={len(refs)}개, BEFORE/AFTER 패턴={'O' if 'BEFORE' in body or '나쁨' in body else 'X'}", improvements)


def axis6_anti_patterns(body: str) -> tuple[int, str, list[str]]:
    score = 0
    improvements: list[str] = []

    if has_section(body, "Forbidden", "금지", "Don't"):
        score += 3
    else:
        improvements.append("Forbidden / 금지 섹션 부재")

    if has_section(body, "Pitfall", "Known issue", "Known pitfall"):
        score += 3
    else:
        improvements.append("Pitfall / Known issue 섹션 부재")

    # failure-mode handling 신호: rm 후 검증 / verify 키워드
    if re.search(r"verify|검증|확인|rollback|fail", body, re.IGNORECASE):
        score += 2

    # auto vs taste / 자동 vs 사용자 결정 명시
    if re.search(r"automated.*taste|자동.*사용자|auto vs|taste|gating", body, re.IGNORECASE):
        score += 2
    else:
        improvements.append(
            "자동 결정 vs 사용자 결정 경계 명시 부재 (manual decision gating)"
        )

    score = min(score, 10)
    return (score, "anti-pattern 섹션 + failure-mode 핸들링", improvements)


def axis7_validation(body: str, skill_dir: Path) -> tuple[int, str, list[str]]:
    score = 0
    improvements: list[str] = []

    scripts = find_in_subdir(skill_dir, "scripts", ".py", ".sh")
    validators = [p for p in scripts if "valid" in p.name.lower() or "check" in p.name.lower()]
    if validators:
        score += 4
    elif scripts:
        score += 2
        improvements.append("scripts/ 안에 검증 도구 이름이 분명하지 않음 (validate-*.py 권장)")
    else:
        improvements.append("검증 스크립트 부재")

    # argparse / --help 지원 검사
    has_argparse = False
    has_json_flag = False
    for v in validators:
        txt = v.read_text(encoding="utf-8")
        if "argparse" in txt or 'getopts' in txt:
            has_argparse = True
        if re.search(r'--json', txt):
            has_json_flag = True
    if has_argparse:
        score += 3
    else:
        improvements.append("검증 스크립트가 argparse/--help 미지원 (사용자/CI 친화성 부족)")
    if has_json_flag:
        score += 3
    else:
        improvements.append("--json 출력 미지원 (다른 스킬과 chaining 불가)")

    score = min(score, 10)
    return (
        score,
        f"validators={len(validators)}, argparse={has_argparse}, --json={has_json_flag}",
        improvements,
    )


def axis8_security(fm: dict[str, str]) -> tuple[int, str, list[str]]:
    score = 0
    improvements: list[str] = []
    tools = fm.get("allowed-tools", "")

    if tools:
        score += 3
    else:
        improvements.append("allowed-tools 미정의 — 명시 권장 (보안/투명성)")

    if re.search(r"Bash\(\s*\*\s*\)", tools):
        improvements.append("Bash(*) 무제한 권한 — 위험")
    else:
        score += 3

    if re.search(r"Bash\(\s*rm\s*\*\s*\)", tools) or re.search(r"rm\s+-rf", tools):
        improvements.append("rm 와일드카드 — 범위 제한 필요 (예: Bash(rm claudedocs/*))")
    else:
        score += 2

    # disable-model-invocation 또는 명시 안전성 (외부 영향 액션 없음)
    if fm.get("disable-model-invocation") == "true":
        score += 2
    elif not re.search(r"push|deploy|publish|send|delete", tools, re.IGNORECASE):
        score += 2
    else:
        improvements.append(
            "외부 영향 액션(push/deploy/send) 자동 호출 가능 — disable-model-invocation: true 또는 권한 게이트 권장"
        )

    score = min(score, 10)
    return (score, f"allowed-tools 정의={'O' if tools else 'X'}", improvements)


def axis9_generalization(body: str, fm: dict[str, str]) -> tuple[int, str, list[str]]:
    score = 0
    improvements: list[str] = []

    # 회사 고유 이슈 prefix 감지 (MPT-, JIRA 특정 prefix 등은 PROJ-/TICKET- 으로 일반화 권장)
    # MPT- 같은 회사 prefix 가 본문에 박혀 있으면 감점
    prefix_hits = re.findall(r"\bMPT-\d+\b|\bACME-\d+\b", body)
    if not prefix_hits:
        score += 3
    else:
        improvements.append(
            f"회사 고유 이슈 prefix 노출: {set(prefix_hits)} — 일반화 (PROJ-### 등)"
        )

    # override 메커니즘 (env var, $ARGUMENTS, ${CLAUDE_SKILL_DIR})
    has_env = re.search(r"\$\{?[A-Z_]+\}?|환경변수", body)
    has_args = re.search(r"\$ARGUMENTS|argument-hint", body)
    if has_env and has_args:
        score += 4
    elif has_env or has_args:
        score += 2
        improvements.append(
            "override 메커니즘 한쪽만 (환경변수 + $ARGUMENTS 둘 다 권장)"
        )
    else:
        improvements.append("커스터마이즈 메커니즘 부재 — 환경변수 또는 $ARGUMENTS 사용 권장")

    # 절대 경로 / OS 특정 (macOS 특정 sed -i '' 패턴)
    if re.search(r"sed -i ''", body):
        improvements.append(
            "macOS BSD sed 의존 (`sed -i ''`) — Linux 와 호환 안 됨, GNU/BSD 분기 권장"
        )
    else:
        score += 3

    score = min(score, 10)
    return (
        score,
        f"override mechanism: env={'O' if has_env else 'X'}, args={'O' if has_args else 'X'}",
        improvements,
    )


def axis10_decision_design(body: str) -> tuple[int, str, list[str]]:
    score = 0
    improvements: list[str] = []

    if has_section(body, "Where this fits", "workflow", "sequencing", "어디에 위치"):
        score += 3
    else:
        improvements.append("Skill sequencing / 'Where this fits' 섹션 부재")

    if re.search(r"automated.*taste|자동.*사용자|auto vs|gating", body, re.IGNORECASE):
        score += 3
    else:
        improvements.append("Manual decision gating (자동 vs 사용자 결정) 표 부재")

    if has_section(body, "Reflection", "reflection", "관찰", "패턴 관찰"):
        score += 2

    if has_section(body, "persistent", "영구", "downstream", "후행"):
        score += 1

    if has_section(body, "Modes?", "모드"):
        score += 1

    score = min(score, 10)
    return (score, "decision design 섹션 커버리지", improvements)


# ---------- 통합 ----------


AXES = [
    ("Frontmatter 규약 준수", axis1_frontmatter),
    ("Description 자동 호출 신뢰성", axis2_description),
    ("Progressive Disclosure", axis3_progressive_disclosure),
    ("Standing Instructions", axis4_standing_instructions),
    ("예시 완결성", axis5_examples),
    ("Anti-pattern / Failure-mode", axis6_anti_patterns),
    ("Validation 자가 검증", axis7_validation),
    ("보안 / 권한 설계", axis8_security),
    ("일반화 / 휴대성", axis9_generalization),
    ("의사결정·산출물 설계", axis10_decision_design),
]


def score_skill(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    fm, _, body = parse_frontmatter(text)
    yaml_issues = frontmatter_yaml_syntax_issues(text)
    skill_dir = path.parent

    axis_results = []
    total = 0
    all_improvements: list[str] = []

    for idx, (name, fn) in enumerate(AXES, start=1):
        # 각 축 함수의 인자가 다르므로 분기
        if fn is axis1_frontmatter:
            score, reason, imps = fn(fm, path, yaml_issues)
        elif fn is axis2_description:
            score, reason, imps = fn(fm)
        elif fn is axis8_security:
            score, reason, imps = fn(fm)
        elif fn is axis9_generalization:
            score, reason, imps = fn(body, fm)
        elif fn is axis3_progressive_disclosure or fn is axis5_examples:
            score, reason, imps = fn(body, skill_dir)
        elif fn is axis7_validation:
            score, reason, imps = fn(body, skill_dir)
        else:
            score, reason, imps = fn(body)

        axis_results.append(
            {
                "id": idx,
                "name": name,
                "score": score,
                "max": 10,
                "reason": reason,
                "improvements": imps,
            }
        )
        total += score
        all_improvements.extend(imps)

    verdict = "PASS" if total >= PASS_SCORE and not yaml_issues else "FAIL"
    return {
        "path": str(path),
        "axes": axis_results,
        "total": total,
        "verdict": verdict,
        "pass_score": PASS_SCORE,
        "blocking_issues": yaml_issues,
        "top_improvements": all_improvements[:5],
        "summary": f"{total}/100 ({verdict}). 강점/약점은 axes 항목 참조.",
    }


def render_text(report: dict[str, Any]) -> str:
    lines: list[str] = []
    icon = "✅" if report["verdict"] == "PASS" else "❌"
    lines.append(
        f"\n{icon} {report['path']}  →  {report['total']}/100  ({report['verdict']}, 통과 기준 {report['pass_score']})"
    )
    lines.append("")
    lines.append("| # | 축 | 점수 | 사유 |")
    lines.append("|---|---|---|---|")
    for ax in report["axes"]:
        reason = ax["reason"].replace("|", "\\|")
        lines.append(f"| {ax['id']} | {ax['name']} | {ax['score']}/{ax['max']} | {reason} |")
    if report["top_improvements"]:
        lines.append("")
        lines.append("**점수 상승 포인트**:")
        for imp in report["top_improvements"]:
            lines.append(f"- {imp}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="score_skill.py",
        description="SKILL.md 휴리스틱 채점 (100점, 90점 게이트). LLM 호출 없음. stdlib only.",
    )
    parser.add_argument("paths", nargs="+", help="SKILL.md 파일 경로 (다중 허용)")
    parser.add_argument("--json", dest="as_json", action="store_true", help="JSON 출력")
    parser.add_argument(
        "--output",
        default=OUTPUT_PATH,
        help=f"JSON 결과 저장 경로 (기본: {OUTPUT_PATH})",
    )
    args = parser.parse_args(argv)

    reports: list[dict[str, Any]] = []
    all_pass = True
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            print(f"::error file={path}::파일 없음", file=sys.stderr)
            reports.append({"path": str(path), "error": "file not found"})
            all_pass = False
            continue
        report = score_skill(path)
        reports.append(report)
        if report["verdict"] != "PASS":
            all_pass = False
        if args.as_json:
            pass  # 마지막에 통합 출력
        else:
            print(render_text(report))

    aggregate = {
        "pass_score": PASS_SCORE,
        "all_pass": all_pass,
        "results": reports,
    }
    Path(args.output).write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if args.as_json:
        print(json.dumps(aggregate, ensure_ascii=False, indent=2))
    else:
        print(f"\n결과 저장: {args.output}")
        if all_pass:
            print(f"✅ 모든 스킬 {PASS_SCORE}점 이상")
        else:
            print(f"❌ 일부 스킬 {PASS_SCORE}점 미만 — 머지 차단", file=sys.stderr)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
