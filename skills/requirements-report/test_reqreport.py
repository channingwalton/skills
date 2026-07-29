import unittest

import reqreport


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
