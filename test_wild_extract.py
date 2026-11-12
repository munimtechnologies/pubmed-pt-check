# SPDX-License-Identifier: Apache-2.0
# Tests for wild_extract.py (no network). MV2, Munim, Inc. Made with AI agents.
import unittest

import wild_extract as w


def one(text):
    ms = w.find_matches(text)
    assert len(ms) == 1, ms
    return ms[0]


class TestClassify(unittest.TestCase):
    def test_name_quoted(self):
        m = one('"Biological Markers"[Mesh] OR biomarker*[tiab]')
        self.assertEqual(m["name"], "Biological Markers")
        self.assertEqual(m["cls"], "name_quoted")
        self.assertEqual(m["tag"], "Mesh")

    def test_unquoted(self):
        self.assertEqual(one("#1 Biological Markers[mh] OR x").get("cls"), "unquoted")

    def test_whole_quoted(self):
        m = one('"Biological Markers[MeSH Terms]" OR x')
        self.assertEqual(m["cls"], "whole_quoted")
        self.assertEqual(m["tag"], "MeSH Terms")

    def test_curly_quotes(self):
        m = one("“Cognitive Therapy”[MeSH]")
        self.assertEqual(m["cls"], "name_quoted")

    def test_single_quotes(self):
        self.assertEqual(one("'Great Britain'[mh]")["cls"], "single_quote")

    def test_space_before_bracket_and_case(self):
        m = one('intensive care [mh:noexp]')
        self.assertEqual(m["cls"], "unquoted")
        self.assertEqual(m["tag"], "mh:noexp")

    def test_new_name_flagged(self):
        m = one('"Surveys and Questionnaires"[Mesh]')
        self.assertTrue(m["after_surveys_and"])
        self.assertEqual(m["cls"], "other")

    def test_longer_heading_not_matched(self):
        self.assertEqual(w.find_matches('"Intensive Care Units"[Mesh]'), [])
        self.assertEqual(w.find_matches('"Cognitive Behavioral Therapy"[Mesh]'), [])

    def test_inside_word_not_matched(self):
        self.assertEqual(w.find_matches("PreQuestionnaires[mh]"), [])

    def test_two_matches(self):
        ms = w.find_matches('"Questionnaires"[Mesh] AND "Great Britain"[Mesh]')
        self.assertEqual(sorted(m["name"] for m in ms), ["Great Britain", "Questionnaires"])


class TestQueryAndSample(unittest.TestCase):
    def test_query(self):
        q = w.build_query("Questionnaires")
        self.assertIn('"Questionnaires[MeSH Terms]"', q)
        self.assertIn('NOT "Surveys and Questionnaires"', q)
        self.assertIn("FIRST_PDATE:[2017-01-01 TO 2026-11-12]", q)
        self.assertNotIn("NOT", w.build_query("Great Britain"))

    def test_sample_small(self):
        self.assertEqual(w.pick_sample(["PMC2", "PMC1", "PMC2"]), ["PMC1", "PMC2"])

    def test_sample_deterministic(self):
        ids = ["PMC%d" % i for i in range(100)]
        a = w.pick_sample(ids)
        self.assertEqual(len(a), 25)
        self.assertEqual(a, w.pick_sample(list(reversed(ids))))


class TestXml(unittest.TestCase):
    XML = ('<article><body><p>See <italic>Table</italic> 1</p>'
           '<table-wrap><table><tr><td><p>#2 "Biological Markers"[Mesh] OR biomarker*[tiab]</p>'
           '</td></tr></table></table-wrap></body></article>')

    def test_leaf_blocks(self):
        blocks, full = w.leaf_blocks(self.XML)
        self.assertEqual(blocks, ["See Table 1", '#2 "Biological Markers"[Mesh] OR biomarker*[tiab]'])
        self.assertIn("Table 1", full)

    def test_process_doc(self):
        blocks, recs = w.process_doc(self.XML)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["block_index"], 1)
        self.assertEqual(recs[0]["cls"], "name_quoted")

    def test_bad_xml_fallback(self):
        blocks, recs = w.process_doc('<p>"Great Britain"[mh] <b>unclosed')
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["cls"], "name_quoted")


if __name__ == "__main__":
    unittest.main()
