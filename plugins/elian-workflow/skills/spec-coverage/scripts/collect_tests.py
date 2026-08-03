#!/usr/bin/env python3
"""Collect JUnit XML results and bind them to acceptance-criteria (AC) IDs.

Usage:
  python3 collect_tests.py [--root DIR] [--results GLOB]... [--out FILE] [--json]

An AC ID (`R<n>-AC<n>`) is bound to a test by appearing in the test's display
NAME -- that is the only binding mechanism, no manifest. The class name is
deliberately NOT scanned: that would bind every testcase in the class to the AC,
letting an unrelated passing helper stand in as the proof.

    @DisplayName("R1-AC1 an order over the limit is rejected")
    it('R1-AC2 the order button is disabled when stock is 0', () => {})

Output shape:
  {"R1-AC1": {"status": "pass", "tests": ["com.example.OrderTest#..."]}}

Verdict per AC ID:
  any failing/erroring test -> fail
  else any passing test     -> pass
  else (only skipped tests) -> skipped
  no test at all            -> the AC ID never appears here; build_status.py
                               turns that absence into `unchecked`.

Exit codes: 0 ok, 1 bad usage, 2 no JUnit XML found / unparseable XML.
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

AC_ID = re.compile(r"\bR[0-9]+-AC[0-9]+\b")

# Gradle writes build/test-results/<task>/TEST-*.xml, Maven writes
# target/surefire-reports/TEST-*.xml. The leading **/ covers multi-module
# layouts and still matches the single-module root (** matches zero dirs).
DEFAULT_GLOBS = [
    "**/build/test-results/**/TEST-*.xml",
    "**/target/surefire-reports/TEST-*.xml",
]

PRUNE = {"node_modules", ".git", ".gradle", "venv", ".venv"}


def find_xml(root: Path, globs: list) -> list:
    found = []
    for pattern in globs:
        # Path.glob rejects absolute patterns, but an absolute --results is a
        # normal input (CI artifact dir, out-of-tree build, another module).
        # Anchor those at the filesystem root instead of the project root.
        if os.path.isabs(pattern):
            base, rel = Path(pattern).anchor, os.path.relpath(pattern, Path(pattern).anchor)
            matches = Path(base).glob(rel)
        else:
            matches = root.glob(pattern)
        for path in matches:
            if PRUNE & set(path.parts):
                continue
            if path.is_file():
                found.append(path)
    return sorted(set(found))


def classify(testcase: ET.Element) -> str:
    if testcase.find("failure") is not None or testcase.find("error") is not None:
        return "fail"
    if testcase.find("skipped") is not None:
        return "skipped"
    return "pass"


def collect(paths: list) -> dict:
    """Return {ac_id: {"status": ..., "tests": [...]}}."""
    seen = {}  # ac_id -> {"statuses": set, "tests": set}
    for path in paths:
        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            # Do NOT skip-and-continue. A truncated report from the run you just
            # did, sitting next to an older parseable one, would silently yield
            # verdicts from stale evidence presented as current.
            print(f"ERROR: unparseable JUnit XML {path}: {exc}", file=sys.stderr)
            print("  Test evidence is unusable — fix or delete the file and re-run "
                  "the suite. Refusing to report partial results as current.",
                  file=sys.stderr)
            sys.exit(2)
        for tc in tree.getroot().iter("testcase"):
            name = tc.get("name", "")
            classname = tc.get("classname", "")
            # Bind from the display NAME only. Scanning classname too made every
            # testcase in a class whose name contains an AC ID bind to that AC —
            # so an unrelated passing helper in that class could stand in as the
            # proof after the real test was deleted. The documented convention
            # puts the ID in the display name; honour exactly that.
            ids = set(AC_ID.findall(name))
            if not ids:
                continue
            status = classify(tc)
            label = f"{classname}#{name}" if classname else name
            for ac in ids:
                entry = seen.setdefault(ac, {"statuses": set(), "tests": set()})
                entry["statuses"].add(status)
                entry["tests"].add(label)

    result = {}
    for ac in sorted(seen):
        statuses = seen[ac]["statuses"]
        if "fail" in statuses:
            verdict = "fail"
        elif "pass" in statuses:
            verdict = "pass"
        else:
            verdict = "skipped"
        result[ac] = {"status": verdict, "tests": sorted(seen[ac]["tests"])}
    return result


def main():
    ap = argparse.ArgumentParser(description="Bind JUnit XML results to AC IDs.")
    ap.add_argument("--root", default=".", help="project root to scan (default: cwd)")
    ap.add_argument("--results", action="append", default=[],
                    help="extra glob for JUnit XML, relative to --root (repeatable)")
    ap.add_argument("--out", help="write JSON to this path")
    ap.add_argument("--json", action="store_true", help="print JSON to stdout")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    globs = DEFAULT_GLOBS + args.results
    paths = find_xml(root, globs)

    # Hard failure, never an empty result: "the tests were not run" and "no test
    # covers this AC" are different facts. Returning {} here would silently mark
    # every AC `unchecked` and make the report claim a coverage gap that is
    # really just a missing test run -- that would destroy this skill's credibility.
    if not paths:
        print(f"ERROR: no JUnit XML found under {root}", file=sys.stderr)
        print(f"  searched: {', '.join(globs)}", file=sys.stderr)
        print("  Run the test suite first, or pass --results <glob> for a "
              "non-standard reporter output path.", file=sys.stderr)
        sys.exit(2)

    result = collect(paths)
    payload = json.dumps(result, ensure_ascii=False, indent=2)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
        print(f"OK {out} — {len(paths)} XML file(s), {len(result)} AC ID(s)", file=sys.stderr)
    if args.json or not args.out:
        print(payload)


if __name__ == "__main__":
    main()
