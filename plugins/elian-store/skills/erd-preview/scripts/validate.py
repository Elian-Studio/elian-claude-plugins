#!/usr/bin/env python3
"""ERD 계보 추적기 HTML 검증기.

생성된 계보 추적기 HTML 에서 SCHEMA / RELS / DATA / LAYERS / KLABEL 를 뽑아 검사한다:
  1. RELS 의 from/to 컬럼이 SCHEMA 에 실제로 존재
  2. 카디널리티 라벨 ∈ {1:1, 1:N, N:1}
  3. 참조 무결성 — DATA 의 모든 FK 셀 값이 참조 테이블의 대상 컬럼 값 집합에 존재
     (소프트 참조도 동일 검사. to 가 PK 아닐 수 있음. 매칭 0건이면 경고 — 계보가 안 그려짐)
  4. 행 수 — 테이블당 최소 1행, 15행 초과면 가독성 경고
  5. LAYERS 커버리지 — SCHEMA 의 모든 테이블이 LAYERS 에 정확히 1회 등장
  6. 레이어 순서 — 하드 FK 각 관계에서 부모(to) 레이어 ≤ 자식(from) 레이어 (좌→우 흐름)
  7. KLABEL — 각 테이블에 한글 라벨 존재(없으면 경고)

다섯 구조는 JS 리터럴(따옴표 없는 키·홑따옴표)이라 Node 로 파싱한다.
Node 가 없으면 명확히 알리고 실패한다(추정 파싱으로 잘못된 PASS 를 내지 않기 위해).

사용:  python3 validate.py <erd.html>
종료코드 0 = 통과, 1 = 실패.

# ponytail: Node 로 파싱 — JS 리터럴 정규식 변환은 홑따옴표 안 콤마('2,500,000')에서 깨진다.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

# const 선언 블록은 이 마커 앞에서 끝난다(템플릿 고정 구조).
RENDER_MARKER = "Render engine"


def extract_models(html: str) -> dict:
    start = html.find("const SCHEMA")
    if start < 0:
        fail("HTML 에서 'const SCHEMA' 선언을 찾지 못했습니다.")
    mpos = html.find(RENDER_MARKER, start)
    if mpos < 0:
        mpos = html.find("const esc", start)
    if mpos < 0:
        mpos = html.find("class ERD", start)
    if mpos < 0:
        fail("SCHEMA/RELS/DATA/LAYERS/KLABEL 선언 블록의 끝을 찾지 못했습니다.")
    # 마커를 감싼 렌더 섹션 주석의 여는 '//' 또는 '/*' 앞까지만 잘라 주석이 잘리지 않게 한다.
    end = html.rfind("//", start, mpos)
    cend = html.rfind("/*", start, mpos)
    end = max(end, cend)
    if end < 0:
        end = mpos
    decls = html[start:end]
    js = decls + (
        "\nprocess.stdout.write(JSON.stringify("
        "{SCHEMA:SCHEMA,RELS:RELS,DATA:DATA,LAYERS:LAYERS,KLABEL:KLABEL}));"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as f:
        f.write(js)
        tmp = f.name
    try:
        out = subprocess.run(["node", tmp], capture_output=True, text=True, timeout=15)
    except FileNotFoundError:
        fail("node 실행 파일을 찾지 못했습니다. Node 설치 후 다시 검증하세요.")
    finally:
        Path(tmp).unlink(missing_ok=True)
    if out.returncode != 0:
        fail("JS 리터럴 파싱 실패:\n" + out.stderr.strip())
    return json.loads(out.stdout)


def fail(msg: str):
    print(f"❌ FAIL: {msg}")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("usage: python3 validate.py <erd.html>")
        sys.exit(2)
    html = Path(sys.argv[1]).read_text(encoding="utf-8")
    m = extract_models(html)
    schema, rels = m["SCHEMA"], m["RELS"]
    data, layers, klabel = m["DATA"], m["LAYERS"], m["KLABEL"]

    errors, warnings = [], []

    # 테이블 → {컬럼명: 컬럼def}
    cols_of = {}
    for t in schema:
        cols_of[t["name"]] = {c["c"]: c for c in t["cols"]}
    table_names = [t["name"] for t in schema]

    # 1) RELS 컬럼 존재 + 2) 카디널리티 라벨
    valid_cards = {"1:1", "1:N", "N:1"}
    for r in rels:
        (ft, fc), (tt, tc) = r["from"], r["to"]
        if ft not in cols_of or fc not in cols_of.get(ft, {}):
            errors.append(f"RELS from {ft}.{fc} 컬럼이 SCHEMA 에 없음")
        if tt not in cols_of or tc not in cols_of.get(tt, {}):
            errors.append(f"RELS to {tt}.{tc} 컬럼이 SCHEMA 에 없음")
        if r.get("card") not in valid_cards:
            errors.append(f"RELS {ft}.{fc}→{tt}.{tc} 카디널리티 '{r.get('card')}' 가 {valid_cards} 밖")

    def col_values(table, col):
        d = data.get(table)
        if not d or col not in d["cols"]:
            return None
        i = d["cols"].index(col)
        return {str(row[i]) for row in d["rows"]}

    # 3) 참조 무결성 (하드 + 소프트)
    for r in rels:
        (ft, fc), (tt, tc) = r["from"], r["to"]
        soft = bool(r.get("soft"))
        tag = "소프트참조" if soft else "FK"
        if ft not in data:
            warnings.append(f"{ft} 에 데이터(DATA) 없음 — {tag} 참조 무결성 검사 스킵")
            continue
        target_vals = col_values(tt, tc)
        if target_vals is None:
            warnings.append(f"{tt}.{tc} 에 데이터 없음 — {ft}.{fc} {tag} 검사 스킵")
            continue
        src = data[ft]
        if fc not in src["cols"]:
            errors.append(f"{ft} 데이터에 {tag} 컬럼 {fc} 없음")
            continue
        idx = src["cols"].index(fc)
        matched = 0
        for row in src["rows"]:
            v = row[idx]
            if v in (None, "", "null"):
                continue
            if str(v) in target_vals:
                matched += 1
            else:
                errors.append(
                    f"참조 무결성 위반: {ft}.{fc}={v} 이 {tt}.{tc} 값 {sorted(target_vals)} 에 없음"
                )
        if matched == 0:
            warnings.append(
                f"{ft}.{fc} → {tt}.{tc} ({tag}) 매칭 0건 — 이 관계는 계보에 안 그려짐"
            )

    # 4) 행 수 — 최소 1, 15 초과 경고
    for name, d in data.items():
        n = len(d["rows"])
        if n < 1:
            errors.append(f"{name} 데이터 0행 (최소 1행 필요)")
        elif n > 15:
            warnings.append(f"{name} 데이터 {n}행 — 15행 초과, 가독성 위해 스코프 축소 권장")

    # 5) LAYERS 커버리지 — 모든 테이블이 정확히 1회
    flat = [t for layer in layers for t in layer]
    seen = {}
    for t in flat:
        seen[t] = seen.get(t, 0) + 1
    for name in table_names:
        c = seen.get(name, 0)
        if c == 0:
            errors.append(f"LAYERS 에 {name} 없음 (모든 테이블이 레이어에 배치돼야 함)")
        elif c > 1:
            errors.append(f"LAYERS 에 {name} 가 {c}번 중복 등장")
    for t in flat:
        if t not in cols_of:
            errors.append(f"LAYERS 의 {t} 가 SCHEMA 에 없는 테이블")

    # 6) 레이어 순서 — 하드 FK 는 부모(to) 레이어 ≤ 자식(from) 레이어
    def layer_index(name):
        for i, layer in enumerate(layers):
            if name in layer:
                return i
        return None

    for r in rels:
        if r.get("soft"):
            continue
        fl, tl = layer_index(r["from"][0]), layer_index(r["to"][0])
        if fl is None or tl is None:
            continue
        if tl > fl:
            errors.append(
                f"레이어 순서 역전: {r['to'][0]}(부모, L{tl}) 가 "
                f"{r['from'][0]}(자식, L{fl}) 보다 오른쪽 — 좌→우 흐름 위해 부모를 앞 레이어로"
            )

    # 7) KLABEL — each table has a human-readable label
    for name in table_names:
        if name not in klabel or not klabel[name]:
            warnings.append(f"KLABEL has no label for {name}; the summary panel will use the table name")

    # FK 플래그인데 대응 RELS 없으면 경고
    rel_from = {(r["from"][0], r["from"][1]) for r in rels}
    for t in schema:
        for c in t["cols"]:
            if c.get("fk") and (t["name"], c["c"]) not in rel_from:
                warnings.append(f"{t['name']}.{c['c']} 는 FK 플래그지만 대응 RELS 없음")

    for w in warnings:
        print(f"⚠️  {w}")
    if errors:
        for e in errors:
            print(f"❌ {e}")
        print(f"\nFAIL — {len(errors)}건 오류")
        sys.exit(1)
    hard = sum(1 for r in rels if not r.get("soft"))
    soft = sum(1 for r in rels if r.get("soft"))
    print(
        f"✅ PASS — 테이블 {len(schema)} · 하드FK {hard} · 소프트참조 {soft} · "
        f"레이어 {len(layers)} · 참조 무결성 OK"
    )


if __name__ == "__main__":
    main()
