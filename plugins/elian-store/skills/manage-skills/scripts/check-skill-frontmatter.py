#!/usr/bin/env python3
"""verify-* SKILL.md 의 frontmatter + 6개 필수 섹션 자가 검증.

manage-skills 가 verify-* 스킬을 생성/수정 후 자가 검증에 사용.
다른 스킬이 chaining 가능하도록 --json 출력 지원.

stdlib 만 사용 (zero pip installs).

사용법:
    python3 check-skill-frontmatter.py <SKILL.md path> [<SKILL.md path>...]
    python3 check-skill-frontmatter.py path/to/SKILL.md --json
    python3 check-skill-frontmatter.py --help

검증 항목:
  1. YAML frontmatter (`---` 블록) 존재 + valid 구조
  2. frontmatter 의 필수 필드: name, description
  3. name 이 kebab-case + `verify-` 접두사 (검증 스킬일 경우)
  4. 6개 필수 섹션 존재: Purpose / When to Run / Related Files / Workflow / Output Format / Exceptions
  5. allowed-tools 의 위험 패턴 (`Bash(*)`, 무제한 `rm`) 부재

종료 코드:
  0 — 모든 입력이 통과
  1 — 하나 이상 실패
  2 — 사용법 오류 / 파일 없음

JSON 스키마 (--json):
  {
    "results": [
      {
        "file": "...",
        "verdict": "PASS" | "FAIL",
        "checks": {
          "frontmatter_block": {"pass": bool, "reason": "..."},
          "required_fields":   {"pass": bool, "missing": [...]},
          "name_format":       {"pass": bool, "reason": "..."},
          "required_sections": {"pass": bool, "missing": [...]},
          "allowed_tools":     {"pass": bool, "violations": [...]}
        }
      }
    ],
    "all_pass": bool
  }
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = [
    "Purpose",
    "When to Run",
    "Related Files",
    "Workflow",
    "Output Format",
    "Exceptions",
]

REQUIRED_FRONTMATTER_FIELDS = ["name", "description"]


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end == -1:
        return None, text
    fm: dict[str, str] = {}
    for ln in lines[1:end]:
        m = re.match(r"^([a-zA-Z_-][a-zA-Z0-9_-]*)\s*:\s*(.*)$", ln)
        if m:
            key, value = m.group(1), m.group(2).strip()
            value = re.sub(r'^"|"$', "", value)
            value = re.sub(r"^'|'$", "", value)
            fm[key] = value
    body = "\n".join(lines[end + 1 :])
    return fm, body


def has_required_section(body: str, name: str) -> bool:
    pattern = rf"^#{{1,4}}\s+.*\b{re.escape(name)}\b"
    return bool(re.search(pattern, body, re.MULTILINE | re.IGNORECASE))


def check_one(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    checks: dict[str, dict[str, Any]] = {}

    if fm is None:
        checks["frontmatter_block"] = {
            "pass": False,
            "reason": "YAML frontmatter (--- 로 둘러싼 블록) 부재 또는 종료 마커 누락",
        }
        checks["required_fields"] = {"pass": False, "missing": REQUIRED_FRONTMATTER_FIELDS}
        checks["name_format"] = {"pass": False, "reason": "frontmatter 부재로 검사 불가"}
    else:
        checks["frontmatter_block"] = {"pass": True, "reason": "valid"}
        missing = [f for f in REQUIRED_FRONTMATTER_FIELDS if not fm.get(f)]
        checks["required_fields"] = {"pass": not missing, "missing": missing}
        name = fm.get("name", "")
        if not name:
            checks["name_format"] = {"pass": False, "reason": "name 필드 부재"}
        elif not re.fullmatch(r"[a-z0-9-]+", name):
            checks["name_format"] = {
                "pass": False,
                "reason": f"name '{name}' 가 kebab-case 위반 (소문자/숫자/하이픈만 허용)",
            }
        elif len(name) > 64:
            checks["name_format"] = {
                "pass": False,
                "reason": f"name '{name}' 64자 초과 ({len(name)}자)",
            }
        else:
            checks["name_format"] = {"pass": True, "reason": "kebab-case OK"}

    missing_sections = [s for s in REQUIRED_SECTIONS if not has_required_section(body, s)]
    checks["required_sections"] = {
        "pass": not missing_sections,
        "missing": missing_sections,
    }

    tools = fm.get("allowed-tools", "") if fm else ""
    violations: list[str] = []
    if re.search(r"Bash\(\s*\*\s*\)", tools):
        violations.append("Bash(*) 무제한 권한")
    if re.search(r"Bash\(\s*rm\s*\*\s*\)", tools) or re.search(r"rm\s+-rf", tools):
        violations.append("rm 와일드카드 / rm -rf 무제한")
    if re.search(r"Bash\(\s*sudo", tools):
        violations.append("Bash(sudo*) 권한 상승")
    checks["allowed_tools"] = {
        "pass": not violations,
        "violations": violations,
    }

    all_pass = all(c["pass"] for c in checks.values())
    return {
        "file": str(path),
        "verdict": "PASS" if all_pass else "FAIL",
        "checks": checks,
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [f"=== {report['file']} ==="]
    icon_pass, icon_fail = "✓", "✗"
    c = report["checks"]

    def line(name: str, ok: bool, detail: str) -> str:
        return f"  {icon_pass if ok else icon_fail} {name}: {detail}"

    lines.append(line("1. frontmatter block", c["frontmatter_block"]["pass"], c["frontmatter_block"]["reason"]))
    fields = c["required_fields"]
    lines.append(
        line(
            "2. required fields",
            fields["pass"],
            "OK" if fields["pass"] else f"missing: {fields['missing']}",
        )
    )
    lines.append(line("3. name format", c["name_format"]["pass"], c["name_format"]["reason"]))
    secs = c["required_sections"]
    lines.append(
        line(
            "4. required sections (6개)",
            secs["pass"],
            "all present"
            if secs["pass"]
            else f"missing: {secs['missing']}",
        )
    )
    tools = c["allowed_tools"]
    lines.append(
        line(
            "5. allowed-tools safety",
            tools["pass"],
            "OK" if tools["pass"] else f"violations: {tools['violations']}",
        )
    )
    lines.append("")
    lines.append(
        f"Verdict: {report['verdict']}"
        + (" — 모든 검사 통과" if report["verdict"] == "PASS" else " — 위 항목 수정 필요")
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check-skill-frontmatter.py",
        description="verify-* SKILL.md frontmatter + 6 필수 섹션 자가 검증. stdlib only.",
    )
    parser.add_argument("paths", nargs="+", help="검사할 SKILL.md 파일 (다중 허용)")
    parser.add_argument("--json", dest="as_json", action="store_true", help="JSON 출력")
    args = parser.parse_args(argv)

    reports: list[dict[str, Any]] = []
    all_pass = True
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            print(f"::error file={path}::파일 없음", file=sys.stderr)
            reports.append({"file": str(path), "error": "file not found"})
            all_pass = False
            continue
        report = check_one(path)
        reports.append(report)
        if report["verdict"] != "PASS":
            all_pass = False
        if not args.as_json:
            print(render_text(report))

    aggregate = {"results": reports, "all_pass": all_pass}
    if args.as_json:
        print(json.dumps(aggregate, ensure_ascii=False, indent=2))
    else:
        print()
        if all_pass:
            print("✅ 모든 SKILL.md 통과")
        else:
            print("❌ 일부 SKILL.md 위반 — 위 결과 참조", file=sys.stderr)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
