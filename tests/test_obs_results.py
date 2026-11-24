"""Regression for tools/watch-build.sh: a stale (dirty) OBS result must
never be counted as a fresh failure, but must stay pending until OBS
dispatches the rebuild. Run: python3 -m unittest discover -s tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from obs_results import classify  # noqa: E402


def result(code="failed", dirty=None, package="effectcraft",
           repo="opensuse_tumbleweed", arch="x86_64"):
    attrs = f' repository="{repo}" arch="{arch}" state="{code}"'
    if dirty:
        attrs += ' dirty="true"'
    return (f"<result{attrs}>"
            f'<status package="{package}" code="{code}"/>'
            "</result>")


def doc(*results):
    return "<resultlist>" + "".join(results) + "</resultlist>"


class WatchResults(unittest.TestCase):
    def test_stale_failure_is_pending_not_failed(self):
        rows = classify(doc(result(dirty="true")))
        self.assertEqual(rows, [("PENDING", "effectcraft",
                                 "opensuse_tumbleweed/x86_64",
                                 "outdated (was: failed)")])

    def test_fresh_failure_is_bad(self):
        self.assertEqual(classify(doc(result())),
                         [("BAD", "effectcraft",
                           "opensuse_tumbleweed/x86_64", "failed")])

    def test_inflight_is_pending(self):
        self.assertEqual(classify(doc(result(code="building"))),
                         [("PENDING", "effectcraft",
                           "opensuse_tumbleweed/x86_64", "building")])

    def test_stale_success_still_waits_for_rebuild(self):
        rows = classify(doc(result(code="succeeded", dirty="true")))
        self.assertEqual(rows[0][0], "PENDING")

    def test_success_and_empty_produce_no_rows(self):
        self.assertEqual(classify(doc(result(code="succeeded"))), [])
        self.assertEqual(classify("<resultlist/>"), [])

    def test_stale_repo_without_status_is_pending(self):
        rows = classify('<resultlist><result repository="r" arch="a" '
                        'state="failed" dirty="true"/></resultlist>')
        self.assertEqual(rows, [("PENDING", "*", "r/a", "outdated")])


if __name__ == "__main__":
    unittest.main()
