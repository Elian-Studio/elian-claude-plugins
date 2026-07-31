from __future__ import annotations

import io
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from _spec_coverage_loader import SPEC_COVERAGE, load

ct = load("spec_coverage_collect_tests", SPEC_COVERAGE / "collect_tests.py")


def _tc(xml: str) -> ET.Element:
    return ET.fromstring(xml)


class ClassifyTests(unittest.TestCase):
    def test_failure_is_fail(self) -> None:
        self.assertEqual(ct.classify(_tc('<testcase name="x"><failure/></testcase>')), "fail")

    def test_error_is_fail(self) -> None:
        self.assertEqual(ct.classify(_tc('<testcase name="x"><error/></testcase>')), "fail")

    def test_skipped_is_skipped(self) -> None:
        self.assertEqual(ct.classify(_tc('<testcase name="x"><skipped/></testcase>')), "skipped")

    def test_bare_testcase_is_pass(self) -> None:
        self.assertEqual(ct.classify(_tc('<testcase name="x"/>')), "pass")


class CollectTests(unittest.TestCase):
    def _write(self, tmp: Path, name: str, body: str) -> Path:
        p = tmp / name
        p.write_text(f'<testsuite name="s">{body}</testsuite>', encoding="utf-8")
        return p

    def test_binds_ac_id_from_display_name_only(self) -> None:
        with TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            p = self._write(
                tmp,
                "a.xml",
                '<testcase name="R1-AC1 order created" classname="OrderTest"/>'
                '<testcase name="unrelated smoke" classname="R9-AC9Tests"/>',
            )
            result = ct.collect([p])
        self.assertIn("R1-AC1", result)
        # The AC id living only in the classname must not bind.
        self.assertNotIn("R9-AC9", result)
        self.assertEqual(result["R1-AC1"]["status"], "pass")
        self.assertEqual(result["R1-AC1"]["tests"], ["OrderTest#R1-AC1 order created"])

    def test_label_without_classname_is_just_the_name(self) -> None:
        with TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            p = self._write(tmp, "a.xml", '<testcase name="R2-AC1 x"/>')
            result = ct.collect([p])
        self.assertEqual(result["R2-AC1"]["tests"], ["R2-AC1 x"])

    def test_fail_beats_pass_for_the_same_ac(self) -> None:
        with TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            p = self._write(
                tmp,
                "a.xml",
                '<testcase name="R1-AC1 a"/>'
                '<testcase name="R1-AC1 b"><failure/></testcase>',
            )
            result = ct.collect([p])
        self.assertEqual(result["R1-AC1"]["status"], "fail")
        self.assertEqual(len(result["R1-AC1"]["tests"]), 2)

    def test_only_skipped_yields_skipped(self) -> None:
        with TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            p = self._write(tmp, "a.xml", '<testcase name="R1-AC1 a"><skipped/></testcase>')
            result = ct.collect([p])
        self.assertEqual(result["R1-AC1"]["status"], "skipped")

    def test_one_test_can_bind_multiple_acs(self) -> None:
        with TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            p = self._write(tmp, "a.xml", '<testcase name="R1-AC1 and R1-AC2 both"/>')
            result = ct.collect([p])
        self.assertEqual(sorted(result), ["R1-AC1", "R1-AC2"])

    def test_unparseable_xml_exits_2(self) -> None:
        with TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            p = tmp / "bad.xml"
            p.write_text('<testsuite><testcase name="R7-AC1 x"/>', encoding="utf-8")
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
                ct.collect([p])
        self.assertEqual(ctx.exception.code, 2)


class FindXmlTests(unittest.TestCase):
    def test_finds_default_gradle_and_maven_layouts(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            gradle = root / "build" / "test-results" / "test"
            surefire = root / "target" / "surefire-reports"
            gradle.mkdir(parents=True)
            surefire.mkdir(parents=True)
            (gradle / "TEST-a.xml").write_text("<testsuite/>", encoding="utf-8")
            (surefire / "TEST-b.xml").write_text("<testsuite/>", encoding="utf-8")
            found = ct.find_xml(root, ct.DEFAULT_GLOBS)
        names = sorted(p.name for p in found)
        self.assertEqual(names, ["TEST-a.xml", "TEST-b.xml"])

    def test_prunes_node_modules_and_dedupes(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            pruned = root / "node_modules" / "build" / "test-results" / "test"
            pruned.mkdir(parents=True)
            (pruned / "TEST-x.xml").write_text("<testsuite/>", encoding="utf-8")
            found = ct.find_xml(root, ct.DEFAULT_GLOBS)
        self.assertEqual(found, [])

    def test_extra_relative_glob_is_matched(self) -> None:
        with TemporaryDirectory() as tmpname:
            root = Path(tmpname)
            (root / "reports").mkdir()
            (root / "reports" / "results.xml").write_text("<testsuite/>", encoding="utf-8")
            found = ct.find_xml(root, ["reports/*.xml"])
        self.assertEqual([p.name for p in found], ["results.xml"])


class MainTests(unittest.TestCase):
    def test_no_xml_found_exits_2(self) -> None:
        with TemporaryDirectory() as tmpname, redirect_stderr(io.StringIO()):
            argv = ["collect_tests.py", "--root", tmpname, "--json"]
            import sys

            old = sys.argv
            sys.argv = argv
            try:
                with self.assertRaises(SystemExit) as ctx:
                    ct.main()
            finally:
                sys.argv = old
        self.assertEqual(ctx.exception.code, 2)

    def test_writes_out_file_and_prints_json(self) -> None:
        import json
        import sys

        with TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            results = tmp / "reports"
            results.mkdir()
            (results / "TEST-a.xml").write_text(
                '<testsuite name="s"><testcase name="R1-AC1 x"/></testsuite>', encoding="utf-8"
            )
            out = tmp / "out.json"
            argv = [
                "collect_tests.py", "--root", str(tmp), "--results", "reports/*.xml",
                "--out", str(out), "--json",
            ]
            old = sys.argv
            sys.argv = argv
            buf = io.StringIO()
            try:
                with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                    ct.main()
            finally:
                sys.argv = old
            written = json.loads(out.read_text(encoding="utf-8"))
        self.assertIn("R1-AC1", written)
        self.assertIn("R1-AC1", json.loads(buf.getvalue()))


if __name__ == "__main__":
    unittest.main()
