#!/usr/bin/env python3
"""verify-implementation dry-run — 현재 디렉토리의 verify-* 스킬 동적 탐색.

verify-implementation 이 실제로 무엇을 실행할지 미리 확인하는 도구.
다른 스킬과 chaining 가능하도록 --json 출력 지원.

stdlib 만 사용 (zero pip installs).

사용법:
    python3 check-skill-discovery.py <skills-dir>
    python3 check-skill-discovery.py .claude/skills/ --json
    python3 check-skill-discovery.py --help

출력:
- 발견된 verify-* 스킬 목록 (name, description, manual-only 여부)
- 자기 자신(verify-implementation) 제외 표시
- frontmatter 누락/parse 실패 경고
- "수동 실행 전용" 표식 경고

종료 코드:
  0 — 1개 이상 verify-* 스킬 발견
  1 — verify-* 스킬 0개
  2 — 사용법 오류 / 디렉토리 없음
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def parse_frontmatter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end == -1:
        return None
    fm: dict[str, str] = {}
    for ln in lines[1:end]:
        m = re.match(r"^([a-zA-Z_-][a-zA-Z0-9_-]*)\s*:\s*(.*)$", ln)
        if m:
            key, value = m.group(1), m.group(2).strip()
            value = re.sub(r'^"|"$', "", value)
            value = re.sub(r"^'|'$", "", value)
            fm[key] = value
    return fm


def is_manual_only(text: str) -> bool:
    return bool(re.search(r"수동\s*실행\s*전용|수동\s*실행", text))


def has_section(text: str, name: str) -> bool:
    pattern = rf"^#{{1,4}}\s+.*\b{re.escape(name)}\b"
    return bool(re.search(pattern, text, re.MULTILINE | re.IGNORECASE))


def discover(skills_dir: Path) -> dict[str, Any]:
    if not skills_dir.exists() or not skills_dir.is_dir():
        return {
            "skills_dir": str(skills_dir),
            "error": "directory not found",
            "verify_skills": [],
            "skipped": [],
            "warnings": [],
        }

    verify_skills: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    warnings: list[str] = []

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if not skill_dir.name.startswith("verify-"):
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            warnings.append(f"{skill_dir.name}: SKILL.md missing")
            continue

        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)

        if fm is None:
            warnings.append(f"{skill_dir.name}: frontmatter parse failed")
            continue

        name = fm.get("name", skill_dir.name)
        description = fm.get("description", "")
        manual_only = is_manual_only(text)
        has_workflow = has_section(text, "Workflow")
        has_exceptions = has_section(text, "Exceptions")

        skill_info = {
            "name": name,
            "directory": str(skill_dir),
            "description": description,
            "manual_only": manual_only,
            "has_workflow": has_workflow,
            "has_exceptions": has_exceptions,
        }

        if name == "verify-implementation":
            skipped.append({**skill_info, "reason": "self (orchestrator)"})
        elif manual_only:
            skipped.append({**skill_info, "reason": "manual-only flag"})
            verify_skills.append(skill_info)  # 명시 호출 가능하므로 목록에는 포함
        else:
            verify_skills.append(skill_info)

        if not has_workflow:
            warnings.append(f"{name}: Workflow 섹션 부재 — 실행 시 SKIP")
        if not has_exceptions:
            warnings.append(f"{name}: Exceptions 섹션 부재 — false positive 위험")

    return {
        "skills_dir": str(skills_dir),
        "verify_skills": verify_skills,
        "skipped": skipped,
        "warnings": warnings,
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [f"=== {report['skills_dir']} ==="]
    if report.get("error"):
        lines.append(f"❌ {report['error']}")
        return "\n".join(lines)

    skills = report["verify_skills"]
    auto_runnable = [s for s in skills if not s["manual_only"] and s["name"] != "verify-implementation"]

    lines.append(f"\n발견된 verify-* 스킬: {len(skills)}개")
    lines.append(f"  자동 실행 대상: {len(auto_runnable)}개")
    lines.append(f"  SKIP (manual-only / self): {len(report['skipped'])}개")
    lines.append("")

    if skills:
        lines.append("| # | 스킬 | 설명 | manual? | Workflow | Exceptions |")
        lines.append("|---|------|------|---------|----------|------------|")
        for i, s in enumerate(skills, 1):
            desc = (s["description"] or "")[:50]
            manual = "Y" if s["manual_only"] else ""
            wf = "✓" if s["has_workflow"] else "✗"
            ex = "✓" if s["has_exceptions"] else "✗"
            lines.append(f"| {i} | {s['name']} | {desc} | {manual} | {wf} | {ex} |")

    if report["skipped"]:
        lines.append("")
        lines.append("SKIP 처리:")
        for s in report["skipped"]:
            lines.append(f"  - {s['name']} ({s['reason']})")

    if report["warnings"]:
        lines.append("")
        lines.append("경고:")
        for w in report["warnings"]:
            lines.append(f"  ⚠ {w}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check-skill-discovery.py",
        description="verify-implementation dry-run — verify-* 스킬 동적 탐색 + frontmatter 검증. stdlib only.",
    )
    parser.add_argument("skills_dir", help="검사할 스킬 디렉토리 (예: .claude/skills/)")
    parser.add_argument("--json", dest="as_json", action="store_true", help="JSON 출력")
    args = parser.parse_args(argv)

    skills_dir = Path(args.skills_dir)
    report = discover(skills_dir)

    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))

    if report.get("error"):
        return 2
    return 0 if report["verify_skills"] else 1


if __name__ == "__main__":
    sys.exit(main())
