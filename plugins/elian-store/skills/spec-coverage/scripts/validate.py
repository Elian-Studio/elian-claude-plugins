#!/usr/bin/env python3
"""Self-check for the spec-coverage scripts, driven by fixtures/.

Usage:  python3 validate.py
Exit codes: 0 all checks passed, 1 at least one check failed.

Checks:
  1. collect_tests.py on the fixture reproduces fixtures/expected-collect.json
     (pass / fail / skipped verdicts + testcases with no AC ID ignored)
  2. collect_tests.py exits non-zero when no JUnit XML exists -- "tests were not
     run" must never be silently reported as "no test covers this"
  3. build_status.py turns a seeded AC with zero matching tests into `unchecked`
     and reports ac_proven / ac_total honestly
  4. a manual waiver survives a passing test but NOT a currently failing one
  5. render.py produces HTML carrying the ac_proven headline
  6. a manual `pass` cannot forge the "proven by tests" headline number
  7. an AC ID that appears only in a testcase's classname does not bind
  8. build_status.py refuses a seed that misses an AC present in the PRD
  9. unparseable JUnit XML is a hard error, not a silent partial result

Checks 6-9 are regressions for defects found by adversarial review before the
skill first shipped; each one produced a confidently wrong number.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE.parent / "fixtures"
PY = sys.executable or "python3"

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'} — {name}")
    if not ok and detail:
        print(f"       {detail}")


def run(args, **kw):
    return subprocess.run([PY] + args, capture_output=True, text=True, **kw)


def check_collect_matches_fixture():
    proc = run([str(HERE / "collect_tests.py"), "--root", str(FIXTURES),
                "--results", "sample-junit.xml", "--json"])
    if proc.returncode != 0:
        check("collect_tests.py on fixture", False, proc.stderr.strip())
        return
    expected = json.loads((FIXTURES / "expected-collect.json").read_text(encoding="utf-8"))
    actual = json.loads(proc.stdout)
    if actual == expected:
        check("collect_tests.py on fixture matches expected-collect.json", True)
    else:
        diff = f"expected {json.dumps(expected, sort_keys=True)}\n       actual   {json.dumps(actual, sort_keys=True)}"
        check("collect_tests.py on fixture matches expected-collect.json", False, diff)


def check_no_xml_fails():
    with tempfile.TemporaryDirectory() as tmp:
        proc = run([str(HERE / "collect_tests.py"), "--root", tmp, "--json"])
    ok = proc.returncode != 0 and proc.stdout.strip() in ("", "{}")
    check("collect_tests.py exits non-zero with no JUnit XML", ok,
          f"returncode={proc.returncode} stdout={proc.stdout.strip()!r}")


SEED = {
    "label": "SC-DEMO",
    "title": "spec-coverage self-check",
    "C2": [
        {"id": "R1-AC1", "title": "an order is created", "source": "tech-spec.md §2"},
        {"id": "R1-AC2", "title": "quantity 0 is rejected", "source": "tech-spec.md §2"},
        {"id": "R1-AC3", "title": "a coupon is applied", "source": "tech-spec.md §2"},
        {"id": "R2-AC1", "title": "the button is disabled at 0 stock", "source": "prd.md §6"},
        {"id": "R2-AC2", "title": "stock is released on cancel", "source": "prd.md §6"},
        {"id": "R9-AC9", "title": "refunds are issued within 24h", "source": "prd.md §6"},
    ],
    "C5": [
        {"id": "SQL-01", "title": "order table has the idempotency key unique index",
         "source": "ddl.sql", "expected": "1 index"},
    ],
}


def build(tmp: Path, tests_json: Path = None):
    seed_path = tmp / "seed.json"
    seed_path.write_text(json.dumps(SEED), encoding="utf-8")
    args = [str(HERE / "build_status.py"), "SC-DEMO", "--seed", str(seed_path),
            "--root", str(tmp)]
    if tests_json:
        args += ["--tests", str(tests_json)]
    proc = run(args)
    out = tmp / "claudedocs" / "SC-DEMO" / "spec-coverage.json"
    return proc, out


def items_of(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, {it["id"]: it for cat in data["categories"] for it in cat["items"]}


def check_build_status(tmp: Path, tests_json: Path):
    proc, out = build(tmp, tests_json)
    if proc.returncode != 0 or not out.exists():
        check("build_status.py produces spec-coverage.json", False, proc.stderr.strip())
        return None
    data, items = items_of(out)

    expected_status = {
        "R1-AC1": ("pass", "test"),
        "R1-AC2": ("fail", "test"),
        "R1-AC3": ("skipped", "test"),
        "R2-AC1": ("fail", "test"),
        "R2-AC2": ("fail", "test"),
        "R9-AC9": ("unchecked", ""),   # no test carries this ID — the whole point
        "SQL-01": ("unchecked", ""),   # manual category, never touched by tests
    }
    bad = [f"{k}: got ({items[k]['status']},{items[k]['decided_by']}) want {v}"
           for k, v in expected_status.items()
           if (items[k]["status"], items[k]["decided_by"]) != v]
    check("build_status.py verdicts (incl. AC with zero tests -> unchecked)",
          not bad, "; ".join(bad))

    s = data["summary"]
    ac_ok = s["ac_total"] == 6 and s["ac_proven"] == 1
    check("build_status.py summary reports ac_proven/ac_total", ac_ok,
          f"ac_proven={s['ac_proven']} ac_total={s['ac_total']} (want 1/6)")
    return out


def check_manual_skip_survives(tmp: Path, out: Path, tests_json: Path):
    """A human marking an item skipped means 'deliberately not applicable'."""
    patches = tmp / "patches.json"
    patches.write_text(json.dumps({"R1-AC2": {"status": "skipped",
                                              "note": "out of scope this release"}}),
                       encoding="utf-8")
    proc = run([str(HERE / "apply.py"), "SC-DEMO", str(patches), str(tmp)])
    if proc.returncode != 0:
        check("apply.py records manual evidence", False, proc.stderr.strip())
        return
    _, items = items_of(out)
    ok = items["R1-AC2"]["status"] == "skipped" and items["R1-AC2"]["decided_by"] == "manual"
    check("apply.py sets decided_by=manual", ok,
          f"got ({items['R1-AC2']['status']},{items['R1-AC2']['decided_by']})")

    # R1-AC2's fixture test FAILS. A waiver must not outrank a test that is red
    # right now, or the report shows "deliberately skipped" for something broken.
    build(tmp, tests_json)
    _, items = items_of(out)
    ok = items["R1-AC2"]["status"] == "fail" and items["R1-AC2"]["decided_by"] == "test"
    check("a failing test overrides a stale manual waiver", ok,
          f"got ({items['R1-AC2']['status']},{items['R1-AC2']['decided_by']})")

    # The other direction: R1-AC1's fixture test PASSES, so the waiver stands —
    # "deliberately not applicable" is a judgement a green run cannot contradict.
    patches.write_text(json.dumps({"R1-AC1": {"status": "skipped",
                                              "note": "out of scope this release"}}),
                       encoding="utf-8")
    run([str(HERE / "apply.py"), "SC-DEMO", str(patches), str(tmp)])
    build(tmp, tests_json)
    _, items = items_of(out)
    ok = items["R1-AC1"]["status"] == "skipped" and items["R1-AC1"]["decided_by"] == "manual"
    check("a manual waiver survives a passing test", ok,
          f"got ({items['R1-AC1']['status']},{items['R1-AC1']['decided_by']})")


def check_manual_cannot_forge_proof(tmp: Path):
    """A hand-written `pass` must not move the "AC proven by tests" headline."""
    root = tmp / "forge"
    (root / "claudedocs" / "F").mkdir(parents=True)
    seed = root / "seed.json"
    seed.write_text(json.dumps({"label": "F", "title": "f",
                                "C2": [{"id": "R9-AC1", "title": "no test exists"}]}),
                    encoding="utf-8")
    run([str(HERE / "build_status.py"), "F", "--seed", str(seed), "--root", str(root)])
    patches = root / "p.json"
    patches.write_text(json.dumps({"R9-AC1": {"status": "pass", "evidence": "trust me"}}),
                       encoding="utf-8")
    run([str(HERE / "apply.py"), "F", str(patches), str(root)])
    summary = json.loads((root / "claudedocs" / "F" / "spec-coverage.json")
                         .read_text(encoding="utf-8"))["summary"]
    ok = summary["ac_proven"] == 0 and summary["ac_claimed_manual"] == 1
    check("a manual 'pass' cannot forge the proven-by-tests count", ok,
          f"got ac_proven={summary['ac_proven']} ac_claimed_manual={summary.get('ac_claimed_manual')}")


def check_classname_does_not_bind(tmp: Path):
    """An AC ID in the class name must not let unrelated tests prove the AC."""
    xml = tmp / "cls.xml"
    xml.write_text('<testsuite name="s"><testcase name="unrelated smoke" '
                   'classname="R9-AC2Tests"/></testsuite>', encoding="utf-8")
    proc = run([str(HERE / "collect_tests.py"), "--results", str(xml), "--json"])
    ok = proc.returncode == 0 and json.loads(proc.stdout or "{}") == {}
    check("an AC ID only in classname does not bind", ok,
          f"rc={proc.returncode} out={proc.stdout.strip()[:80]}")


def check_seed_must_cover_prd(tmp: Path):
    """A seed missing an AC would silently shrink the denominator."""
    root = tmp / "prdcheck"
    root.mkdir(parents=True)
    prd = root / "prd.md"
    prd.write_text("| R8-AC1 | g | w | t |\n| R8-AC2 | g | w | t |\n", encoding="utf-8")
    seed = root / "seed.json"
    seed.write_text(json.dumps({"label": "P", "title": "p",
                                "C2": [{"id": "R8-AC1", "title": "only one"}]}),
                    encoding="utf-8")
    proc = run([str(HERE / "build_status.py"), "P", "--seed", str(seed),
                "--prd", str(prd), "--root", str(root)])
    ok = proc.returncode == 3 and "R8-AC2" in proc.stderr
    check("build_status.py rejects a seed that misses a PRD AC", ok,
          f"rc={proc.returncode} err={proc.stderr.strip()[:120]}")


def check_malformed_xml_is_fatal(tmp: Path):
    """Truncated results next to older ones must not yield stale verdicts."""
    xml = tmp / "bad.xml"
    xml.write_text('<testsuite><testcase name="R7-AC1 x"/>', encoding="utf-8")
    proc = run([str(HERE / "collect_tests.py"), "--results", str(xml), "--json"])
    ok = proc.returncode != 0 and proc.stdout.strip() in ("", "{}")
    check("unparseable JUnit XML is a hard error", ok,
          f"rc={proc.returncode} out={proc.stdout.strip()[:80]}")


def check_render(tmp: Path):
    proc = run([str(HERE / "render.py"), "SC-DEMO", str(tmp), "--lang", "ko"])
    html = tmp / "claudedocs" / "SC-DEMO" / "spec-coverage.html"
    ok = proc.returncode == 0 and html.exists() and "headline-num" in html.read_text(encoding="utf-8")
    check("render.py writes spec-coverage.html with the AC headline", ok,
          proc.stderr.strip())


def main():
    check_collect_matches_fixture()
    check_no_xml_fails()

    with tempfile.TemporaryDirectory() as tmpname:
        tmp = Path(tmpname)
        tests_json = tmp / "tests.json"
        proc = run([str(HERE / "collect_tests.py"), "--root", str(FIXTURES),
                    "--results", "sample-junit.xml", "--out", str(tests_json)])
        if proc.returncode != 0:
            check("collect_tests.py --out", False, proc.stderr.strip())
        else:
            out = check_build_status(tmp, tests_json)
            if out:
                check_manual_skip_survives(tmp, out, tests_json)
                check_render(tmp)
        check_manual_cannot_forge_proof(tmp)
        check_classname_does_not_bind(tmp)
        check_seed_must_cover_prd(tmp)
        check_malformed_xml_is_fatal(tmp)

    failed = [n for n, ok, _ in results if not ok]
    print()
    if failed:
        print(f"FAIL — {len(failed)}/{len(results)} check(s) failed")
        sys.exit(1)
    print(f"PASS — all {len(results)} checks passed")


if __name__ == "__main__":
    main()
