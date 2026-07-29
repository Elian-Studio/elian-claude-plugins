#!/usr/bin/env python3
"""create-document 의 스키마 검증 모듈.

JSON Schema 표준 키워드 일부 + 자체 확장 키워드(forbid, mustMatch, endsWith)를 지원한다.
stdlib 만 사용.

지원 키워드:
  - type: string | number | boolean | array | object
  - required: list of field names
  - properties: dict of field -> sub-schema
  - items: sub-schema (array element)
  - minLength / maxLength
  - minItems / maxItems
  - pattern: 정규식 fullmatch
  - enum: 허용 값 목록
  - forbid (자체): 정규식 배열, search match 시 실패
  - mustMatch (자체): 정규식 배열, 하나라도 search match 해야 통과
  - endsWith (자체): 특정 접미사로 끝나야 통과

CLI (단독):
  python3 validate.py <schema.json> <data.json>
  python3 validate.py <schema.json> <data.json> --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def validate(schema: dict, data, path: str = "") -> list[str]:
    """schema 에 맞춰 data 를 검증. 위반 사항을 사람 읽을 수 있는 메시지 리스트로 반환."""
    errors: list[str] = []

    expected_type = schema.get("type")
    if expected_type and not _type_matches(expected_type, data):
        errors.append(f"{path or '(root)'}: type 불일치 — 기대 '{expected_type}', 실제 '{_actual_type(data)}'")
        return errors

    if expected_type == "object":
        if not isinstance(data, dict):
            return errors  # 위에서 이미 잡힘
        for req in schema.get("required", []):
            if req not in data:
                errors.append(f"{_join(path, req)}: 필수 필드 누락")
        for key, sub_schema in (schema.get("properties") or {}).items():
            if key in data:
                errors.extend(validate(sub_schema, data[key], _join(path, key)))

    elif expected_type == "array":
        if not isinstance(data, list):
            return errors
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        if min_items is not None and len(data) < min_items:
            errors.append(f"{path or '(root)'}: 배열 길이 {len(data)} < minItems {min_items}")
        if max_items is not None and len(data) > max_items:
            errors.append(f"{path or '(root)'}: 배열 길이 {len(data)} > maxItems {max_items}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(data):
                errors.extend(validate(item_schema, item, f"{path}[{i}]"))

    elif expected_type == "string":
        if not isinstance(data, str):
            return errors
        min_len = schema.get("minLength")
        max_len = schema.get("maxLength")
        if min_len is not None and len(data) < min_len:
            errors.append(f"{path or '(root)'}: 길이 {len(data)} < minLength {min_len}")
        if max_len is not None and len(data) > max_len:
            errors.append(f"{path or '(root)'}: 길이 {len(data)} > maxLength {max_len}")

        pattern = schema.get("pattern")
        if pattern and not re.fullmatch(pattern, data):
            errors.append(f"{path or '(root)'}: pattern '{pattern}' 불일치 — '{_truncate(data)}'")

        enum = schema.get("enum")
        if enum and data not in enum:
            errors.append(f"{path or '(root)'}: enum {enum} 에 없음 — '{_truncate(data)}'")

        ends = schema.get("endsWith")
        if ends and not data.endswith(ends):
            errors.append(f"{path or '(root)'}: '{ends}' 로 끝나야 함 — '{_truncate(data)}'")

        for pat in schema.get("forbid", []) or []:
            m = re.search(pat, data)
            if m:
                errors.append(f"{path or '(root)'}: 금지 패턴 '{pat}' 매치 — '{m.group()}'")

        must = schema.get("mustMatch") or []
        if must:
            if not any(re.search(pat, data) for pat in must):
                errors.append(
                    f"{path or '(root)'}: mustMatch 미충족 (적어도 하나 매치 필요: {must})"
                )

    elif expected_type == "number":
        if not isinstance(data, (int, float)) or isinstance(data, bool):
            return errors
        # 숫자 제약은 현재 없음 (필요 시 minimum/maximum 추가)

    elif expected_type == "boolean":
        return errors  # 별도 제약 없음

    return errors


def _type_matches(expected: str, value) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return True  # 알 수 없는 타입은 통과


def _actual_type(value) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    return type(value).__name__


def _join(path: str, key: str) -> str:
    return f"{path}.{key}" if path else key


def _truncate(s: str, limit: int = 60) -> str:
    return s if len(s) <= limit else s[:limit] + "…"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate.py",
        description="JSON Schema(+forbid/mustMatch/endsWith) 검증",
    )
    parser.add_argument("schema_file")
    parser.add_argument("data_file")
    parser.add_argument("--json", dest="json_output", action="store_true")
    args = parser.parse_args(argv)

    schema_path = Path(args.schema_file)
    data_path = Path(args.data_file)
    if not schema_path.exists():
        print(f"::error::schema 파일 없음: {schema_path}", file=sys.stderr)
        return 2
    if not data_path.exists():
        print(f"::error::data 파일 없음: {data_path}", file=sys.stderr)
        return 2

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    data = json.loads(data_path.read_text(encoding="utf-8"))
    errors = validate(schema, data)

    if args.json_output:
        print(json.dumps({"verdict": "PASS" if not errors else "FAIL", "errors": errors}, ensure_ascii=False, indent=2))
    else:
        if errors:
            print(f"✗ schema invalid ({len(errors)} errors):", file=sys.stderr)
            for e in errors:
                print(f"  {e}", file=sys.stderr)
        else:
            print("✓ schema valid")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
