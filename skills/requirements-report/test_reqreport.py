import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import reqreport

HERE = Path(__file__).resolve().parent


class ConfigSourcesTest(unittest.TestCase):
    """A scalar "sources" must not be iterated per character.

    "src/test" as a bare string yields Path('s'), Path('r'), Path('c'), Path('/') …
    and Path('/') as a source root walks the entire filesystem instead of failing.
    """

    def run_in(self, sources):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "docs").mkdir()
            (d / "junit").mkdir()
            # A real marked requirement, so the run reaches the sources handling
            # instead of exiting 2 on "no requirements found".
            (d / "docs" / "req.md").write_text(
                "# Reqs\n\n- The service answers health checks `#health-ok`\n",
                encoding="utf-8")
            (d / "junit" / "results.xml").write_text(
                '<testsuite name="S" tests="1">'
                '<testcase classname="S" name="#health-ok answers 200"/>'
                "</testsuite>", encoding="utf-8")
            (d / ".reqreport.json").write_text(json.dumps(
                {"requirements": "docs", "junit": "junit",
                 "sources": sources, "out": "out"}), encoding="utf-8")
            # The timeout is load-bearing: unguarded, a scalar "sources" yields Path('/')
            # and the run walks the whole disk, so a regression shows up here as a
            # TimeoutExpired. A correct run finishes in well under a second.
            return subprocess.run(
                [sys.executable, str(HERE / "reqreport.py")],
                cwd=d, capture_output=True, text=True, timeout=20)

    def test_string_sources_is_treated_as_one_path(self):
        proc = self.run_in("src/test")
        self.assertNotIn("No such file or directory: '/'", proc.stderr)
        self.assertNotEqual(proc.returncode, 2, msg=proc.stderr)

    def test_non_string_non_list_sources_is_rejected(self):
        proc = self.run_in(7)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('"sources" must be a list of paths', proc.stderr)

    def test_list_sources_still_works(self):
        proc = self.run_in(["src/test"])
        self.assertNotEqual(proc.returncode, 2, msg=proc.stderr)


class TestsHtmlTest(unittest.TestCase):
    def test_failure_message_is_preformatted(self):
        case = reqreport.TestCase(
            name="#create-book",
            classname="LibrarySuite",
            failure=("line 1\n  <expected>\nline 3", "failure detail"),
            skipped=False,
            ids=["create-book"],
        )

        rendered = reqreport.tests_html("create-book", [case], {})

        self.assertIn(
            '<pre class="msg"><strong>'
            "line 1\n  &lt;expected&gt;\nline 3"
            "</strong></pre>",
            rendered,
        )
        self.assertNotIn('<div class="msg">', rendered)


if __name__ == "__main__":
    unittest.main()
