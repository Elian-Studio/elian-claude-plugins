#!/usr/bin/env python3
"""Apply manual verification results to claudedocs/<label>/spec-coverage.json.

Usage:
  python3 apply.py <label> <patches.json> [project_root]

This is the human-evidence path, for the categories no test can decide:
C5 (schema / DB verification) and C6 (open decisions), plus C4 when no test
carries the transition. Everything written here is recorded as
`decided_by: "manual"` so the HTML can keep it visually separate from
machine-verified items -- a person's claim must never look like a test result.

patches.json format:

  {
    "SQL-A1": {
      "status": "pass",
      "blocker": "",
      "note": "",
      "where": {"verify_sql": "verify.sql §A.1"},
      "steps": {"SQL-A1-1": {"status": "pass", "evidence": "count=10"}}
    },
    "DEC-02": {"status": "fail", "blocker": "migration not started"}
  }

Exit codes: 0 ok, 1 bad usage, 2 coverage JSON missing, 3 patches missing.
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_status import STATUSES, recount  # noqa: E402  (sibling script, same directory)

TODAY = date.today().isoformat()


def main():
    if len(sys.argv) < 3:
        print("Usage: apply.py <label> <patches.json> [project_root]", file=sys.stderr)
        sys.exit(1)

    label = sys.argv[1]
    patches_path = Path(sys.argv[2])
    project_root = Path(sys.argv[3]) if len(sys.argv) > 3 else Path.cwd()
    json_path = project_root / "claudedocs" / label / "spec-coverage.json"

    if not json_path.exists():
        print(f"ERROR: no spec-coverage.json at {json_path}", file=sys.stderr)
        sys.exit(2)
    if not patches_path.exists():
        print(f"ERROR: patches not found: {patches_path}", file=sys.stderr)
        sys.exit(3)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    patches = json.loads(patches_path.read_text(encoding="utf-8"))

    applied = 0
    unknown = sorted(set(patches) - {it["id"] for c in data["categories"] for it in c["items"]})

    # Reject unknown status values before writing anything. recount() tallies with
    # {s: 0 for s in STATUSES}, so a typo like "passed" would not raise — it would
    # drop out of the counts entirely and under-report ac_proven/ac_total. A wrong
    # number here is worse than a crash: the whole point of this skill is a status
    # you can trust.
    bad = []
    for iid, patch in patches.items():
        if "status" in patch and patch["status"] not in STATUSES:
            bad.append(f"{iid}: {patch['status']!r}")
        for sid, sp in (patch.get("steps") or {}).items():
            if "status" in sp and sp["status"] not in STATUSES:
                bad.append(f"{iid}.{sid}: {sp['status']!r}")
    if bad:
        print(f"ERROR: invalid status value(s); allowed: {', '.join(STATUSES)}", file=sys.stderr)
        for b in bad:
            print(f"  {b}", file=sys.stderr)
        sys.exit(2)

    for cat in data["categories"]:
        for it in cat["items"]:
            patch = patches.get(it["id"])
            if not patch:
                continue
            if "status" in patch:
                it["status"] = patch["status"]
                it["decided_by"] = "manual"
                it["last_checked"] = TODAY
            if "blocker" in patch:
                it["blocker"] = patch["blocker"]
            if "note" in patch:
                it["note"] = patch["note"]
            if "where" in patch:
                it["where"].update(patch["where"])

            step_overrides = patch.get("steps", {})
            if step_overrides and it["steps"]:
                step_map = {s["id"]: s for s in it["steps"]}
                for sid, sp in step_overrides.items():
                    if sid not in step_map:
                        continue
                    if "status" in sp:
                        step_map[sid]["status"] = sp["status"]
                    if "evidence" in sp:
                        step_map[sid]["evidence"] = sp["evidence"]
                it["decided_by"] = "manual"
                it["last_checked"] = TODAY
            applied += 1

    data = recount(data)
    data["last_checked"] = TODAY

    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    s = data["summary"]
    print(f"OK applied {applied} patch(es) to {json_path}")
    print(f"  AC proven: {s['ac_proven']}/{s['ac_total']}")
    print(f"  Status: {s['status_counts']}")
    if unknown:
        print(f"  WARNING: unknown item id(s) ignored: {', '.join(unknown)}", file=sys.stderr)


if __name__ == "__main__":
    main()
