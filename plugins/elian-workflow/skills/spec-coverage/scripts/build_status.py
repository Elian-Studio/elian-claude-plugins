#!/usr/bin/env python3
"""Build claudedocs/<label>/spec-coverage.json from a seed + test results.

Usage:
  python3 build_status.py <label> --seed <seed.json> [--tests <collect.json>]
                          [--root DIR] [--out FILE]

Seed format (written by the model from the design docs -- plain JSON, never
executable code):

  {
    "label": "MPT-9125",
    "title": "Order placement",
    "names": {"C2": "Acceptance Criteria"},          # optional overrides
    "C1": [ {"id": "SC-01", "title": "...", "ac": ["R1-AC1"],
             "source": "qa-checklist.md", "where": {"fe": "", "be": ""},
             "steps": ["...", "..."], "note": "", "expected": ""} ],
    "C2": [ ... ], "C3": [ ... ], "C4": [ ... ], "C5": [ ... ], "C6": [ ... ]
  }

Only `id` and `title` are required per item. For C2 the item id IS the AC ID,
so `ac` defaults to [id] when the id looks like one.

Truth source per category -- this drives the merge, and the HTML says so out
loud so nobody mistakes a human assertion for a machine check:

  C1 / C2 / C3  test          tests decide, always
  C4            test-or-manual tests decide when present, else manual evidence
  C5 / C6       manual        never decided by tests

Merge rules (existing spec-coverage.json is never blindly overwritten):
  * manual status / evidence / blocker / note / where are always carried over
  * on a `test` category a test verdict overwrites an earlier human status --
    a test result is fresher evidence than a note somebody typed last week
  * EXCEPT `skipped`: a human marking an item skipped means "deliberately not
    applicable", so it survives a passing or skipped run -- but NOT a currently
    failing one. A stale waiver must never hide a test that is red right now
  * on a `test` category with no verdict the item falls back to `unchecked`
    -- that is the whole product: a requirement nobody proved

Exit codes: 0 ok, 1 bad usage, 2 seed missing/invalid, 3 seed does not cover
every AC in --prd (a missing seed entry silently shrinks the denominator).
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

TODAY = date.today().isoformat()
AC_ID = re.compile(r"^R[0-9]+-AC[0-9]+$")
CATEGORY_IDS = ["C1", "C2", "C3", "C4", "C5", "C6"]

DEFAULT_NAMES = {
    "C1": "Scenarios",
    "C2": "Acceptance Criteria",
    "C3": "API endpoints",
    "C4": "State transitions",
    "C5": "Schema / DB verification",
    "C6": "Open decisions",
}

TRUTH_SOURCE = {
    "C1": "test",
    "C2": "test",
    "C3": "test",
    "C4": "test-or-manual",
    "C5": "manual",
    "C6": "manual",
}

STATUSES = ["pass", "partial", "fail", "unchecked", "skipped"]


def make_item(raw: dict, cat_id: str) -> dict:
    item_id = str(raw["id"])
    ac = raw.get("ac")
    if ac is None:
        ac = [item_id] if AC_ID.match(item_id) else []
    steps = [
        {"id": f"{item_id}-{i}", "desc": desc, "status": "unchecked", "evidence": ""}
        for i, desc in enumerate(raw.get("steps", []), start=1)
    ]
    return {
        "id": item_id,
        "title": raw["title"],
        "type": raw.get("type", cat_id.lower()),
        "ac": list(ac),
        "source_doc": raw.get("source", ""),
        "what": raw.get("what", raw["title"]),
        "where": dict(raw.get("where", {})),
        "expected": raw.get("expected", ""),
        "how_to_verify": raw.get("how_to_verify", []),
        "status": "unchecked",
        "decided_by": "",
        "tests": [],
        "last_checked": "",
        "steps": steps,
        "blocker": "",
        "note": raw.get("note", ""),
    }


def check_prd_coverage(seed: dict, prd_paths: list) -> None:
    """Fail when the seed does not name every AC ID found in the PRD.

    Without this the denominator is whatever the seed happened to contain: miss
    two of twelve ACs and the report reads a confident "10/10" instead of 10/12.
    A silently shrinking denominator is the most dangerous bug this tool can
    have, because the number still looks like an answer.
    """
    prd_ids = set()
    for path in prd_paths:
        p = Path(path)
        if not p.exists():
            print(f"ERROR: --prd file not found: {p}", file=sys.stderr)
            sys.exit(3)
        prd_ids |= set(re.findall(r"\bR[0-9]+-AC[0-9]+\b", p.read_text(encoding="utf-8")))
    if not prd_ids:
        print(f"ERROR: no R#-AC# IDs found in {', '.join(map(str, prd_paths))}", file=sys.stderr)
        print("  Either the PRD has no AC table yet, or its IDs do not follow the "
              "R<n>-AC<n> convention this skill binds on.", file=sys.stderr)
        sys.exit(3)

    seed_ids = {str(raw["id"]) for raw in seed.get("C2", [])}
    missing = sorted(prd_ids - seed_ids)
    extra = sorted(seed_ids - prd_ids)
    if missing or extra:
        print("ERROR: seed C2 does not match the PRD acceptance criteria.", file=sys.stderr)
        if missing:
            print(f"  missing from seed ({len(missing)}): {', '.join(missing)}", file=sys.stderr)
            print("  These requirements would never appear in the report at all.", file=sys.stderr)
        if extra:
            print(f"  in seed but not in the PRD ({len(extra)}): {', '.join(extra)}", file=sys.stderr)
        sys.exit(3)
    print(f"PRD coverage OK — all {len(prd_ids)} AC ID(s) present in the seed.", file=sys.stderr)


def build(seed: dict) -> dict:
    names = dict(DEFAULT_NAMES)
    names.update(seed.get("names", {}))
    categories = []
    for cid in CATEGORY_IDS:
        items = [make_item(raw, cid) for raw in seed.get(cid, [])]
        categories.append({
            "id": cid,
            "name": names[cid],
            "truth_source": TRUTH_SOURCE[cid],
            "leaf_count": 0,
            "items": items,
        })
    return {
        "label": seed["label"],
        "title": seed.get("title", f"{seed['label']} — requirement coverage"),
        "last_checked": TODAY,
        "summary": {},
        "categories": categories,
    }


def merge_existing(new_data: dict, existing_path: Path) -> dict:
    """Preserve human-entered status / evidence / notes from a previous run.

    Ported from the original generate.py. Overwriting what a person typed is a
    hard no: the file is a living document, not a build artifact.
    """
    if not existing_path.exists():
        return new_data
    try:
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return new_data

    old = {}
    for cat in existing.get("categories", []):
        for it in cat.get("items", []):
            old[it["id"]] = {
                "status": it.get("status", "unchecked"),
                "decided_by": it.get("decided_by", "manual"),
                "last_checked": it.get("last_checked", ""),
                "blocker": it.get("blocker", ""),
                "note": it.get("note", ""),
                "where": it.get("where", {}),
                "steps": {
                    s["id"]: {"status": s.get("status", "unchecked"),
                              "evidence": s.get("evidence", "")}
                    for s in it.get("steps", [])
                },
            }

    for cat in new_data["categories"]:
        for it in cat["items"]:
            prev = old.get(it["id"])
            if not prev:
                continue
            it["status"] = prev["status"]
            it["decided_by"] = prev["decided_by"]
            it["last_checked"] = prev["last_checked"]
            it["blocker"] = prev["blocker"]
            if prev["note"]:
                it["note"] = prev["note"]
            for k, v in prev["where"].items():
                if v and not it["where"].get(k):
                    it["where"][k] = v
            for step in it["steps"]:
                old_step = prev["steps"].get(step["id"])
                if old_step:
                    step["status"] = old_step["status"]
                    step["evidence"] = old_step["evidence"]
    return new_data


def apply_tests(data: dict, verdicts: dict, have_tests: bool) -> dict:
    """Overlay collected test verdicts onto the merged items."""
    for cat in data["categories"]:
        source = cat["truth_source"]
        if source == "manual":
            continue
        for it in cat["items"]:
            if not it["ac"]:
                continue
            hits = [verdicts[a] for a in it["ac"] if a in verdicts]
            if hits:
                statuses = {h["status"] for h in hits}
                # A human "skipped" means deliberately not applicable, and a
                # passing or skipped run does not override that judgement. A
                # currently FAILING test does: a stale waiver must never hide a
                # test that is red right now, or the report shows "skipped"
                # for something actually broken.
                if (it["status"] == "skipped" and it["decided_by"] == "manual"
                        and "fail" not in statuses):
                    continue
                if "fail" in statuses:
                    verdict = "fail"
                elif "pass" in statuses and len(statuses) == 1:
                    verdict = "pass"
                elif "pass" in statuses:
                    verdict = "partial"
                else:
                    verdict = "skipped"
                it["status"] = verdict
                it["decided_by"] = "test"
                it["tests"] = sorted({t for h in hits for t in h["tests"]})
                it["last_checked"] = TODAY
            elif source == "test" and have_tests:
                # No test carries this AC ID. This is the signal the skill exists
                # for -- do not let an earlier manual claim mask it.
                if it["status"] == "skipped" and it["decided_by"] == "manual":
                    continue
                it["status"] = "unchecked"
                it["decided_by"] = ""
                it["tests"] = []
    return data


def count_leaves(item: dict) -> int:
    # Steps are a manual breakdown; once a test decides the item the test is
    # the leaf, not the human's sub-checklist.
    return len(item["steps"]) if item["steps"] and item["decided_by"] != "test" else 1


def leaf_statuses(item: dict) -> list:
    if item["steps"] and item["decided_by"] != "test":
        return [s["status"] for s in item["steps"]]
    return [item["status"]]


def recount(data: dict) -> dict:
    counts = {s: 0 for s in STATUSES}
    by_category = {}
    by_category_items = {}
    decided_by = {"test": 0, "manual": 0, "": 0}

    for cat in data["categories"]:
        cat_leaves = 0
        for it in cat["items"]:
            cat_leaves += count_leaves(it)
            for st in leaf_statuses(it):
                counts[st] = counts.get(st, 0) + 1
            decided_by[it["decided_by"]] = decided_by.get(it["decided_by"], 0) + 1
        cat["leaf_count"] = cat_leaves
        by_category[cat["id"]] = cat_leaves
        by_category_items[cat["id"]] = len(cat["items"])

    # An AC counts as proven only when every item bound to it passed AND a test
    # is what decided it. The headline this feeds is labelled "AC proven by
    # tests" — so a human writing {"status": "pass"} through apply.py must NOT
    # move it. Counting manual claims here would let a patch fabricate
    # "AC proven: 1/1" for an AC that no test touches, which is precisely the
    # lie this skill exists to prevent (and is already in its Forbidden list).
    # Manual evidence still shows on the item itself, tagged decided_by=manual.
    ac_bound = {}
    for cat in data["categories"]:
        for it in cat["items"]:
            for a in it["ac"]:
                ac_bound.setdefault(a, []).append((it["status"], it["decided_by"]))

    data["summary"] = {
        "total_leaf": sum(by_category.values()),
        "by_category": by_category,
        "by_category_items": by_category_items,
        "status_counts": counts,
        "decided_by_counts": {"test": decided_by["test"],
                              "manual": decided_by["manual"],
                              "undecided": decided_by[""]},
        "ac_total": len(ac_bound),
        "ac_proven": sum(1 for pairs in ac_bound.values()
                         if pairs and all(st == "pass" and by == "test"
                                          for st, by in pairs)),
        # ACs a human asserted passing without a test behind them. Reported
        # separately so the evidence is visible but never counted as proof.
        "ac_claimed_manual": sum(1 for pairs in ac_bound.values()
                                 if pairs and all(st == "pass" for st, _ in pairs)
                                 and any(by != "test" for _, by in pairs)),
    }
    return data


def main():
    ap = argparse.ArgumentParser(description="Build spec-coverage.json.")
    ap.add_argument("label")
    ap.add_argument("--seed", required=True, help="seed JSON extracted from the design docs")
    ap.add_argument("--tests", help="collect_tests.py output JSON")
    ap.add_argument("--root", default=".", help="project root (default: cwd)")
    ap.add_argument("--out", help="override output path")
    ap.add_argument("--prd", action="append", default=[],
                    help="prd.md / tech-spec.md to verify the seed covers every "
                         "AC ID in (repeatable). Strongly recommended: without it "
                         "a seed that misses ACs silently shrinks the denominator.")
    args = ap.parse_args()

    seed_path = Path(args.seed)
    if not seed_path.exists():
        print(f"ERROR: seed not found: {seed_path}", file=sys.stderr)
        sys.exit(2)
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    seed.setdefault("label", args.label)

    if args.prd:
        check_prd_coverage(seed, args.prd)
    else:
        print("WARNING: no --prd given; the AC denominator is whatever the seed "
              "contains and is NOT verified against the PRD.", file=sys.stderr)

    verdicts = {}
    have_tests = False
    if args.tests:
        tests_path = Path(args.tests)
        if not tests_path.exists():
            print(f"ERROR: test results not found: {tests_path}", file=sys.stderr)
            sys.exit(2)
        verdicts = json.loads(tests_path.read_text(encoding="utf-8"))
        have_tests = True

    out_path = (Path(args.out) if args.out
                else Path(args.root) / "claudedocs" / args.label / "spec-coverage.json")

    data = build(seed)
    data = merge_existing(data, out_path)
    data = apply_tests(data, verdicts, have_tests)
    data = recount(data)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")

    s = data["summary"]
    print(f"OK {out_path}")
    print(f"  AC proven: {s['ac_proven']}/{s['ac_total']}")
    print(f"  Total leaf: {s['total_leaf']}  {s['status_counts']}")
    print(f"  Decided by: {s['decided_by_counts']}")
    if not have_tests:
        print("  NOTE: no --tests given; every test-backed item stayed as-is "
              "(run collect_tests.py to get real verdicts).")


if __name__ == "__main__":
    main()
