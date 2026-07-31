from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from _spec_coverage_loader import SPEC_COVERAGE, load

# apply.py does `from build_status import ...`; the loader puts its directory on
# sys.path while executing so that sibling import resolves.
apply = load("spec_coverage_apply", SPEC_COVERAGE / "apply.py")
bs = load("build_status", SPEC_COVERAGE / "build_status.py")


def _seed_coverage(root: Path, label: str, seed: dict) -> Path:
    data = bs.recount(bs.build(seed))
    out = root / "claudedocs" / label / "spec-coverage.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data), encoding="utf-8")
    return out


def _run_apply(label: str, patches: dict, root: Path):
    patches_path = root / "patches.json"
    patches_path.write_text(json.dumps(patches), encoding="utf-8")
    argv = ["apply.py", label, str(patches_path), str(root)]
    old = sys.argv
    sys.argv = argv
    out_buf, err_buf = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            apply.main()
    finally:
        sys.argv = old
    return out_buf.getvalue(), err_buf.getvalue()


def _items(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {it["id"]: it for cat in data["categories"] for it in cat["items"]}


SEED = {
    "label": "L",
    "C5": [{"id": "SQL-01", "title": "index exists", "steps": ["run query", "check count"]}],
    "C6": [{"id": "DEC-01", "title": "decision"}],
}


class ApplyMainTests(unittest.TestCase):
    def test_records_manual_status_and_metadata(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            out = _seed_coverage(root, "L", SEED)
            _run_apply("L", {"SQL-01": {"status": "pass", "note": "verified", "blocker": ""}}, root)
            item = _items(out)["SQL-01"]
        self.assertEqual(item["status"], "pass")
        self.assertEqual(item["decided_by"], "manual")
        self.assertEqual(item["note"], "verified")
        self.assertEqual(item["last_checked"], apply.TODAY)

    def test_applies_step_overrides(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            out = _seed_coverage(root, "L", SEED)
            _run_apply(
                "L",
                {"SQL-01": {"steps": {"SQL-01-1": {"status": "pass", "evidence": "count=10"}}}},
                root,
            )
            item = _items(out)["SQL-01"]
        step = {s["id"]: s for s in item["steps"]}["SQL-01-1"]
        self.assertEqual((step["status"], step["evidence"]), ("pass", "count=10"))
        self.assertEqual(item["decided_by"], "manual")

    def test_where_is_merged_not_replaced(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            out = _seed_coverage(root, "L", {"label": "L", "C5": [{"id": "SQL-01", "title": "x", "where": {"be": "orig"}}]})
            _run_apply("L", {"SQL-01": {"where": {"fe": "added"}}}, root)
            item = _items(out)["SQL-01"]
        self.assertEqual(item["where"], {"be": "orig", "fe": "added"})

    def test_invalid_status_exits_2_and_writes_nothing(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            out = _seed_coverage(root, "L", SEED)
            before = out.read_text(encoding="utf-8")
            with self.assertRaises(SystemExit) as ctx:
                _run_apply("L", {"SQL-01": {"status": "passed"}}, root)
            after = out.read_text(encoding="utf-8")
        self.assertEqual(ctx.exception.code, 2)
        self.assertEqual(before, after)

    def test_invalid_step_status_exits_2(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            _seed_coverage(root, "L", SEED)
            with self.assertRaises(SystemExit) as ctx:
                _run_apply("L", {"SQL-01": {"steps": {"SQL-01-1": {"status": "nope"}}}}, root)
        self.assertEqual(ctx.exception.code, 2)

    def test_unknown_item_id_is_warned_not_fatal(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            _seed_coverage(root, "L", SEED)
            _, err = _run_apply("L", {"NOPE-99": {"status": "pass"}}, root)
        self.assertIn("NOPE-99", err)

    def test_missing_coverage_json_exits_2(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
                _run_apply("L", {"SQL-01": {"status": "pass"}}, root)
        self.assertEqual(ctx.exception.code, 2)

    def test_missing_patches_exits_3(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            _seed_coverage(root, "L", SEED)
            argv = ["apply.py", "L", str(root / "nope.json"), str(root)]
            old = sys.argv
            sys.argv = argv
            try:
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
                    apply.main()
            finally:
                sys.argv = old
        self.assertEqual(ctx.exception.code, 3)

    def test_too_few_args_exits_1(self) -> None:
        old = sys.argv
        sys.argv = ["apply.py", "only-label"]
        try:
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
                apply.main()
        finally:
            sys.argv = old
        self.assertEqual(ctx.exception.code, 1)

    def test_manual_pass_does_not_forge_ac_proven(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            out = _seed_coverage(root, "F", {"label": "F", "C2": [{"id": "R9-AC1", "title": "no test"}]})
            _run_apply("F", {"R9-AC1": {"status": "pass", "note": "trust me"}}, root)
            summary = json.loads(out.read_text(encoding="utf-8"))["summary"]
        self.assertEqual(summary["ac_proven"], 0)
        self.assertEqual(summary["ac_claimed_manual"], 1)


if __name__ == "__main__":
    unittest.main()
