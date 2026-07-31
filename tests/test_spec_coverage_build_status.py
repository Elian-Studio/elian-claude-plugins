from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory

from _spec_coverage_loader import SPEC_COVERAGE, load

bs = load("spec_coverage_build_status", SPEC_COVERAGE / "build_status.py")


class MakeItemTests(unittest.TestCase):
    def test_minimal_item_gets_defaults(self) -> None:
        item = bs.make_item({"id": "SC-01", "title": "a scenario"}, "C1")
        self.assertEqual(item["id"], "SC-01")
        self.assertEqual(item["title"], "a scenario")
        self.assertEqual(item["type"], "c1")
        self.assertEqual(item["status"], "unchecked")
        self.assertEqual(item["decided_by"], "")
        self.assertEqual(item["ac"], [])
        self.assertEqual(item["steps"], [])
        self.assertEqual(item["what"], "a scenario")

    def test_ac_defaults_to_id_only_for_ac_shaped_ids(self) -> None:
        # In C2 the item id IS the AC id, so a bare AC-shaped id becomes its own ac.
        self.assertEqual(bs.make_item({"id": "R1-AC1", "title": "x"}, "C2")["ac"], ["R1-AC1"])
        # A non-AC-shaped id gets no implicit ac binding.
        self.assertEqual(bs.make_item({"id": "SC-01", "title": "x"}, "C1")["ac"], [])

    def test_explicit_ac_overrides_default(self) -> None:
        item = bs.make_item({"id": "R1-AC1", "title": "x", "ac": ["R1-AC1", "R1-AC2"]}, "C2")
        self.assertEqual(item["ac"], ["R1-AC1", "R1-AC2"])

    def test_steps_are_numbered_and_seeded_unchecked(self) -> None:
        item = bs.make_item({"id": "SC-01", "title": "x", "steps": ["first", "second"]}, "C1")
        self.assertEqual([s["id"] for s in item["steps"]], ["SC-01-1", "SC-01-2"])
        self.assertEqual([s["desc"] for s in item["steps"]], ["first", "second"])
        self.assertTrue(all(s["status"] == "unchecked" and s["evidence"] == "" for s in item["steps"]))

    def test_non_string_id_is_coerced(self) -> None:
        self.assertEqual(bs.make_item({"id": 12, "title": "x"}, "C1")["id"], "12")


class BuildTests(unittest.TestCase):
    def test_builds_all_six_categories_with_default_names(self) -> None:
        data = bs.build({"label": "L", "C2": [{"id": "R1-AC1", "title": "t"}]})
        self.assertEqual(data["label"], "L")
        self.assertEqual(data["title"], "L — requirement coverage")
        ids = [c["id"] for c in data["categories"]]
        self.assertEqual(ids, bs.CATEGORY_IDS)
        names = {c["id"]: c["name"] for c in data["categories"]}
        self.assertEqual(names["C1"], "Scenarios")
        self.assertEqual(names["C6"], "Open decisions")
        truth = {c["id"]: c["truth_source"] for c in data["categories"]}
        self.assertEqual(truth["C2"], "test")
        self.assertEqual(truth["C5"], "manual")
        self.assertEqual(truth["C4"], "test-or-manual")

    def test_name_overrides_and_explicit_title(self) -> None:
        data = bs.build({"label": "L", "title": "Order placement", "names": {"C2": "ACs"}})
        self.assertEqual(data["title"], "Order placement")
        names = {c["id"]: c["name"] for c in data["categories"]}
        self.assertEqual(names["C2"], "ACs")

    def test_last_checked_uses_today(self) -> None:
        data = bs.build({"label": "L"})
        self.assertEqual(data["last_checked"], bs.TODAY)


def _seed_data():
    return bs.build(
        {
            "label": "L",
            "C2": [
                {"id": "R1-AC1", "title": "one"},
                {"id": "R1-AC2", "title": "two"},
            ],
            "C5": [{"id": "SQL-01", "title": "index exists"}],
        }
    )


class ApplyTestsTests(unittest.TestCase):
    def test_passing_verdict_is_recorded_as_test_decided(self) -> None:
        data = _seed_data()
        verdicts = {"R1-AC1": {"status": "pass", "tests": ["T#a"]}}
        data = bs.apply_tests(data, verdicts, have_tests=True)
        items = _items(data)
        self.assertEqual((items["R1-AC1"]["status"], items["R1-AC1"]["decided_by"]), ("pass", "test"))
        self.assertEqual(items["R1-AC1"]["tests"], ["T#a"])
        self.assertEqual(items["R1-AC1"]["last_checked"], bs.TODAY)

    def test_ac_with_no_matching_test_falls_back_to_unchecked(self) -> None:
        data = _seed_data()
        data = bs.apply_tests(data, {"R1-AC1": {"status": "pass", "tests": []}}, have_tests=True)
        items = _items(data)
        self.assertEqual((items["R1-AC2"]["status"], items["R1-AC2"]["decided_by"]), ("unchecked", ""))

    def test_mixed_pass_and_skip_is_partial(self) -> None:
        data = _seed_data()
        verdicts = {"R1-AC1": {"status": "pass", "tests": ["a"]}}
        # Simulate two AC bindings by giving one item two ACs with different verdicts.
        for cat in data["categories"]:
            for it in cat["items"]:
                if it["id"] == "R1-AC1":
                    it["ac"] = ["R1-AC1", "R1-AC2"]
        verdicts["R1-AC2"] = {"status": "skipped", "tests": ["b"]}
        data = bs.apply_tests(data, verdicts, have_tests=True)
        self.assertEqual(_items(data)["R1-AC1"]["status"], "partial")

    def test_failing_test_wins_over_pass(self) -> None:
        data = _seed_data()
        for cat in data["categories"]:
            for it in cat["items"]:
                if it["id"] == "R1-AC1":
                    it["ac"] = ["R1-AC1", "R1-AC2"]
        verdicts = {
            "R1-AC1": {"status": "pass", "tests": ["a"]},
            "R1-AC2": {"status": "fail", "tests": ["b"]},
        }
        data = bs.apply_tests(data, verdicts, have_tests=True)
        item = _items(data)["R1-AC1"]
        self.assertEqual(item["status"], "fail")
        self.assertEqual(item["tests"], ["a", "b"])

    def test_manual_skip_survives_a_passing_run(self) -> None:
        data = _seed_data()
        item = _items(data)["R1-AC1"]
        item["status"], item["decided_by"] = "skipped", "manual"
        data = bs.apply_tests(data, {"R1-AC1": {"status": "pass", "tests": ["a"]}}, have_tests=True)
        again = _items(data)["R1-AC1"]
        self.assertEqual((again["status"], again["decided_by"]), ("skipped", "manual"))

    def test_manual_skip_yields_to_a_failing_run(self) -> None:
        data = _seed_data()
        item = _items(data)["R1-AC1"]
        item["status"], item["decided_by"] = "skipped", "manual"
        data = bs.apply_tests(data, {"R1-AC1": {"status": "fail", "tests": ["a"]}}, have_tests=True)
        again = _items(data)["R1-AC1"]
        self.assertEqual((again["status"], again["decided_by"]), ("fail", "test"))

    def test_manual_category_is_never_touched_by_tests(self) -> None:
        data = _seed_data()
        data = bs.apply_tests(data, {"SQL-01": {"status": "pass", "tests": ["a"]}}, have_tests=True)
        item = _items(data)["SQL-01"]
        self.assertEqual((item["status"], item["decided_by"]), ("unchecked", ""))

    def test_no_test_run_leaves_items_as_is(self) -> None:
        # have_tests=False: a test-source item with no verdict stays untouched
        # rather than being reset to unchecked.
        data = _seed_data()
        item = _items(data)["R1-AC1"]
        item["status"], item["decided_by"] = "pass", "manual"
        data = bs.apply_tests(data, {}, have_tests=False)
        again = _items(data)["R1-AC1"]
        self.assertEqual((again["status"], again["decided_by"]), ("pass", "manual"))


class LeafAndRecountTests(unittest.TestCase):
    def test_count_leaves_uses_steps_unless_test_decided(self) -> None:
        item = bs.make_item({"id": "SC-01", "title": "x", "steps": ["a", "b", "c"]}, "C1")
        self.assertEqual(bs.count_leaves(item), 3)
        item["decided_by"] = "test"
        self.assertEqual(bs.count_leaves(item), 1)

    def test_count_leaves_is_one_without_steps(self) -> None:
        self.assertEqual(bs.count_leaves(bs.make_item({"id": "x", "title": "y"}, "C1")), 1)

    def test_leaf_statuses_reflects_steps_or_item(self) -> None:
        item = bs.make_item({"id": "SC-01", "title": "x", "steps": ["a", "b"]}, "C1")
        item["steps"][0]["status"] = "pass"
        self.assertEqual(bs.leaf_statuses(item), ["pass", "unchecked"])
        item["decided_by"] = "test"
        item["status"] = "fail"
        self.assertEqual(bs.leaf_statuses(item), ["fail"])

    def test_recount_ac_proven_requires_test_decided_pass(self) -> None:
        data = _seed_data()
        items = _items(data)
        items["R1-AC1"]["status"], items["R1-AC1"]["decided_by"] = "pass", "test"
        items["R1-AC2"]["status"], items["R1-AC2"]["decided_by"] = "pass", "manual"
        data = bs.recount(data)
        s = data["summary"]
        self.assertEqual(s["ac_total"], 2)
        self.assertEqual(s["ac_proven"], 1)
        self.assertEqual(s["ac_claimed_manual"], 1)

    def test_recount_status_and_decided_by_counts(self) -> None:
        data = _seed_data()
        items = _items(data)
        items["R1-AC1"]["status"], items["R1-AC1"]["decided_by"] = "pass", "test"
        items["R1-AC2"]["status"], items["R1-AC2"]["decided_by"] = "fail", "test"
        data = bs.recount(data)
        s = data["summary"]
        self.assertEqual(s["status_counts"]["pass"], 1)
        self.assertEqual(s["status_counts"]["fail"], 1)
        self.assertEqual(s["status_counts"]["unchecked"], 1)  # SQL-01 untouched
        self.assertEqual(s["decided_by_counts"]["test"], 2)
        self.assertEqual(s["decided_by_counts"]["undecided"], 1)
        self.assertEqual(s["by_category_items"]["C2"], 2)


class MergeExistingTests(unittest.TestCase):
    def _write(self, path: Path, data: dict) -> None:
        import json

        path.write_text(json.dumps(data), encoding="utf-8")

    def test_missing_existing_file_is_a_no_op(self) -> None:
        data = _seed_data()
        with TemporaryDirectory() as tmp:
            merged = bs.merge_existing(data, Path(tmp) / "nope.json")
        self.assertIs(merged, data)

    def test_unparseable_existing_file_is_ignored(self) -> None:
        data = _seed_data()
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "spec.json"
            p.write_text("not json", encoding="utf-8")
            merged = bs.merge_existing(data, p)
        self.assertIs(merged, data)

    def test_carries_over_human_status_note_and_steps(self) -> None:
        import json

        existing = bs.build({"label": "L", "C2": [{"id": "R1-AC1", "title": "one", "steps": ["s"]}]})
        item = _items(existing)["R1-AC1"]
        item["status"], item["decided_by"] = "skipped", "manual"
        item["note"], item["blocker"] = "out of scope", "waiting"
        item["last_checked"] = "2020-01-01"
        item["steps"][0]["status"], item["steps"][0]["evidence"] = "pass", "ran it"

        fresh = bs.build({"label": "L", "C2": [{"id": "R1-AC1", "title": "one", "steps": ["s"]}]})
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "spec.json"
            p.write_text(json.dumps(existing), encoding="utf-8")
            merged = bs.merge_existing(fresh, p)
        got = _items(merged)["R1-AC1"]
        self.assertEqual((got["status"], got["decided_by"], got["note"], got["blocker"]), ("skipped", "manual", "out of scope", "waiting"))
        self.assertEqual((got["steps"][0]["status"], got["steps"][0]["evidence"]), ("pass", "ran it"))


class CheckPrdCoverageTests(unittest.TestCase):
    def _prd(self, tmp: Path, text: str) -> Path:
        p = tmp / "prd.md"
        p.write_text(text, encoding="utf-8")
        return p

    def test_passes_when_seed_matches_prd(self) -> None:
        seed = {"C2": [{"id": "R1-AC1"}, {"id": "R1-AC2"}]}
        with TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            prd = self._prd(tmp, "R1-AC1 and R1-AC2 are covered")
            with redirect_stderr(io.StringIO()):
                bs.check_prd_coverage(seed, [prd])  # no SystemExit == pass

    def test_exits_when_seed_misses_a_prd_ac(self) -> None:
        seed = {"C2": [{"id": "R1-AC1"}]}
        with TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            prd = self._prd(tmp, "R1-AC1 R1-AC2")
            with redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit) as ctx:
                bs.check_prd_coverage(seed, [prd])
        self.assertEqual(ctx.exception.code, 3)
        self.assertIn("R1-AC2", err.getvalue())

    def test_exits_when_prd_has_no_ac_ids(self) -> None:
        with TemporaryDirectory() as tmpname:
            prd = self._prd(Path(tmpname), "no ids here")
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
                bs.check_prd_coverage({"C2": []}, [prd])
        self.assertEqual(ctx.exception.code, 3)

    def test_exits_when_prd_file_missing(self) -> None:
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
            bs.check_prd_coverage({"C2": []}, ["/no/such/prd.md"])
        self.assertEqual(ctx.exception.code, 3)


def _items(data: dict) -> dict:
    return {it["id"]: it for cat in data["categories"] for it in cat["items"]}


if __name__ == "__main__":
    unittest.main()
