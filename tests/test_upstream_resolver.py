"""Unit tests for the pure logic of tools/upstream_resolver.py — no
network, bodies are fixtures. Run: python3 -m unittest discover -s tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from upstream_resolver import (  # noqa: E402
    first_version_tag, json_field, normalize, parse_commit)


class Normalize(unittest.TestCase):
    def test_strips_leading_v(self):
        self.assertEqual(normalize("v1.2.3"), "1.2.3")

    def test_unprefixes_component_tags(self):
        # openai/codex's rust-v0.163.0 -> 0.163.0
        self.assertEqual(normalize("rust-v0.163.0"), "0.163.0")
        self.assertEqual(normalize("vscode-v1.0.0"), "1.0.0")

    def test_plain_component_tag_untouched(self):
        self.assertEqual(normalize("2026.09.10"), "2026.09.10")


class FirstVersionTag(unittest.TestCase):
    def test_strict_pass_wins_over_component_tags(self):
        # anomalyco/opencode shape: component tag sorts first, plain wins
        self.assertEqual(
            first_version_tag(["vscode-v1.0.0", "2.2.7", "2.2.6"]), "2.2.7")

    def test_prefix_pass_used_only_without_plain_tags(self):
        # openai/codex shape: only component tags exist
        self.assertEqual(
            first_version_tag(["rust-v0.163.0", "cli-v0.9.0"]), "0.163.0")

    def test_nonversion_shapes_rejected(self):
        # jethrokuan/z's '<2.7.0' must never resolve (red: warned every
        # run while it had an upstream file)
        self.assertEqual(first_version_tag(["<2.7.0"]), "")

    def test_leading_v_kept_in_strict_pass(self):
        self.assertEqual(first_version_tag(["v1.2.3", "v1.2.2"]), "1.2.3")


class JsonField(unittest.TestCase):
    def test_compact_body(self):
        self.assertEqual(
            json_field('{"tag_name": "v5.9.0","other": 1}',
                       r'"tag_name": ?"([^"]*)"'), "v5.9.0")

    def test_loose_spacing(self):
        self.assertEqual(json_field('{"name":"2026.09.10"}',
                                    r'"name": ?"([^"]*)"'), "2026.09.10")

    def test_missing(self):
        self.assertEqual(json_field("{}", r'"tag_name": ?"([^"]*)"'), "")


class ParseCommit(unittest.TestCase):
    def test_full_payload(self):
        body = ('{"sha": "f130b55ee3eaf099eccf588e2a62e5447068d120", '
                '"commit": {"committer": {"date": "2026-02-23T10:00:00Z"}}}')
        self.assertEqual(parse_commit(body),
                         ("f130b55ee3eaf099eccf588e2a62e5447068d120",
                          "2026.02.23"))

    def test_empty_body(self):
        self.assertEqual(parse_commit("404 not found"), ("", ""))


if __name__ == "__main__":
    unittest.main()
