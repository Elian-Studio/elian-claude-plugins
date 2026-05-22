#!/usr/bin/env python3
"""create-document 의 메인 엔트리.

JSON content + template → 스키마 검증 → 치환 → 파일 출력.
stdlib 만 사용.

치환 규칙:
  - {{key}}      : 단순 치환 (HTML escape 적용)
  - {{{key}}}    : raw 치환 (escape 없음)
  - {{key.sub}}  : 점 표기로 중첩 접근
  - <!-- FOREACH key --> ... <!-- END -->  : 배열 반복. 블록 내부에서 요소가 스코프.

종료 코드:
  0 — 검증 통과 + 파일 작성
  1 — 검증 실패 또는 치환 오류
  2 — 사용법 오류 / 파일 없음
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

# validate.py 가 같은 디렉토리에 있다.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from validate import validate  # noqa: E402

SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
SCHEMAS_DIR = SKILL_DIR / "schemas"


FOREACH_RE = re.compile(
    r"<!--\s*FOREACH\s+([\w.]+)\s*-->(.*?)<!--\s*END\s*-->",
    re.DOTALL,
)
PLACEHOLDER_RE = re.compile(r"\{\{\{?([\w.]+)\}?\}\}")


def get_value(scope_stack: list, key: str):
    """점 표기 키를 스코프 스택 위에서부터 차례로 탐색해 값을 얻는다.

    예: scope_stack = [{"cards": [...]}, {"card_id": "c1", "title": "..."}]
        key = "title" → 두 번째 스코프의 title
        key = "issue" → 첫 번째 스코프의 issue
    """
    parts = key.split(".")
    for scope in reversed(scope_stack):
        if not isinstance(scope, dict):
            continue
        cur = scope
        ok = True
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                ok = False
                break
        if ok:
            return cur
    return None


def render_template(template: str, data: dict) -> str:
    """템플릿 전체를 렌더. FOREACH 를 먼저 처리한 뒤 placeholder 를 치환."""
    return _render_with_scope(template, [data])


def _render_with_scope(template: str, scope_stack: list) -> str:
    # 1. FOREACH 블록을 가장 안쪽부터 풀려면, 단순 반복 매치(non-nested 우선) 사용
    #    중첩은 inner 가 outer 의 placeholder 형태로 남지 않도록 재귀로 처리한다.
    while True:
        m = _find_outermost_foreach(template)
        if not m:
            break
        key, body = m.group(1), m.group(2)
        items = get_value(scope_stack, key)
        if items is None:
            items = []
        if not isinstance(items, list):
            raise RuntimeError(f"FOREACH '{key}' — 배열이 아님 (실제: {type(items).__name__})")
        rendered_items = []
        for item in items:
            rendered_items.append(_render_with_scope(body, scope_stack + [item]))
        template = template[: m.start()] + "".join(rendered_items) + template[m.end() :]

    # 2. {{...}} / {{{...}}} placeholder 치환
    def sub(match: re.Match) -> str:
        token = match.group(0)
        key = match.group(1)
        is_raw = token.startswith("{{{") and token.endswith("}}}")
        value = get_value(scope_stack, key)
        if value is None:
            return ""
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)
        return value if is_raw else html.escape(value, quote=False)

    return PLACEHOLDER_RE.sub(sub, template)


def _find_outermost_foreach(template: str) -> re.Match | None:
    """가장 바깥쪽 FOREACH 블록을 찾는다 (중첩 시 outer 부터 처리)."""
    pos = 0
    while pos < len(template):
        # 다음 FOREACH 시작 위치
        start_m = re.search(r"<!--\s*FOREACH\s+([\w.]+)\s*-->", template[pos:])
        if not start_m:
            return None
        start = pos + start_m.start()
        # 짝이 맞는 END 를 depth 카운팅으로 찾는다
        depth = 1
        cursor = pos + start_m.end()
        while cursor < len(template):
            next_open = re.search(r"<!--\s*FOREACH\s+[\w.]+\s*-->", template[cursor:])
            next_close = re.search(r"<!--\s*END\s*-->", template[cursor:])
            if not next_close:
                raise RuntimeError("FOREACH 블록에 짝이 맞는 <!-- END --> 가 없음")
            close_at = cursor + next_close.start()
            open_at = cursor + next_open.start() if next_open else None
            if open_at is not None and open_at < close_at:
                depth += 1
                cursor = open_at + len(next_open.group())
            else:
                depth -= 1
                cursor = close_at + len(next_close.group())
                if depth == 0:
                    end = close_at + len(next_close.group())
                    block_body = template[pos + start_m.end() : close_at]
                    # 가짜 match 객체 만들기
                    return _Match(start, end, start_m.group(1), block_body)
        return None
    return None


class _Match:
    """re.Match 의 일부 인터페이스만 흉내내는 가벼운 어댑터."""

    def __init__(self, start: int, end: int, group1: str, group2: str):
        self._start, self._end, self._g1, self._g2 = start, end, group1, group2

    def start(self) -> int:
        return self._start

    def end(self) -> int:
        return self._end

    def group(self, n: int) -> str:
        return {1: self._g1, 2: self._g2}[n]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="render.py",
        description="JSON content + template → 스키마 검증 + 치환 → 파일 출력",
    )
    parser.add_argument("--template", required=True, help="templates/<name>.html (and schemas/<name>.schema.json) 의 <name>")
    parser.add_argument("--data", required=True, help="치환할 JSON 데이터 파일")
    parser.add_argument("--out", required=True, help="출력 파일 경로")
    parser.add_argument("--schema", help="다른 스키마 이름 (기본은 --template 와 동일)")
    parser.add_argument("--json", dest="json_output", action="store_true")
    args = parser.parse_args(argv)

    template_path = TEMPLATES_DIR / f"{args.template}.html"
    if not template_path.exists():
        # .md 도 지원
        template_path = TEMPLATES_DIR / f"{args.template}.md"
    if not template_path.exists():
        print(f"::error::template 없음: {TEMPLATES_DIR}/{args.template}.(html|md)", file=sys.stderr)
        return 2

    schema_name = args.schema or args.template
    schema_path = SCHEMAS_DIR / f"{schema_name}.schema.json"
    if not schema_path.exists():
        print(f"::error::schema 없음: {schema_path}", file=sys.stderr)
        return 2

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"::error::data 없음: {data_path}", file=sys.stderr)
        return 2

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    data = json.loads(data_path.read_text(encoding="utf-8"))

    errors = validate(schema, data)
    if errors:
        if args.json_output:
            print(json.dumps({"verdict": "FAIL", "errors": errors}, ensure_ascii=False, indent=2))
        else:
            print(f"✗ schema invalid ({len(errors)} errors):", file=sys.stderr)
            for e in errors:
                print(f"  {e}", file=sys.stderr)
        return 1

    template = template_path.read_text(encoding="utf-8")
    try:
        rendered = render_template(template, data)
    except RuntimeError as e:
        print(f"✗ render error: {e}", file=sys.stderr)
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")

    if args.json_output:
        print(json.dumps({"verdict": "PASS", "out": str(out_path)}, ensure_ascii=False, indent=2))
    else:
        field_count = _count_validated_fields(schema, data)
        print(f"✓ schema valid ({field_count} fields checked, 0 forbid hits)")
        print(f"✓ rendered: {out_path}")
    return 0


def _count_validated_fields(schema: dict, data, count: int = 0) -> int:
    """검증된 leaf 필드의 개략적 개수 (보고용)."""
    if isinstance(data, dict):
        for k in data:
            count = _count_validated_fields(
                (schema.get("properties") or {}).get(k, {}), data[k], count
            )
        return count
    if isinstance(data, list):
        for item in data:
            count = _count_validated_fields(schema.get("items") or {}, item, count)
        return count
    return count + 1


if __name__ == "__main__":
    sys.exit(main())
