# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# Licensed under the Apache License, Version 2.0 (Apache-2.0). See LICENSE.
# Made with AI agents working in MV2's name.
"""Offline tests for pubmed_pt_check.py (no network: --live uses a fake fetch).

The esearch replies below copy the shape and numbers of real E-utilities replies read on
2026-11-11 (see FINDINGS.md). The MeSH tests (0.1.1) follow replies read on 2026-11-12:
'"consensus development conferences as topic"[mh]' -> 0 with quotedphrasesnotfound; the same
words unquoted -> mapped to "consensus statements as topic"[MeSH Terms], 5,436 records.
The 0.1.2 tests follow replies read on 2026-11-12: '"Depressive Disorder, Major"[Mesh]' -> 0
with quotedphrasesnotfound; 'Depressive Disorder, Major[mh]' unquoted -> "major depressive
disorder"[MeSH Terms], 46,495 records (see HEADINGS-2026.md)."""
import io
import json
import os
import tempfile
import unittest

import pubmed_pt_check as p

# Real replies, 2026-11-11 (trimmed to the fields the script reads).
OLD_REPLY = {"esearchresult": {"count": "0", "retmax": "0", "retstart": "0", "idlist": [],
                               "translationset": [],
                               "querytranslation": "\"Retraction of Publication\"[pt]",
                               "warninglist": {"phrasesignored": [],
                                               "quotedphrasesnotfound": [
                                                   "\"Retraction of Publication\"[pt]"],
                                               "outputmessages": ["No items found."]}}}
NEW_REPLY = {"esearchresult": {"count": "34339", "retmax": "0", "retstart": "0", "idlist": [],
                               "querytranslation": "\"Retraction Notice\"[Publication Type]"}}
RETRACTED_REPLY = {"esearchresult": {"count": "35579", "idlist": [],
                                     "querytranslation": "\"Retracted Publication\"[Publication Type]"}}
# 2026-11-12: a quoted old MeSH heading name.
OLD_MESH_REPLY = {"esearchresult": {"count": "0", "idlist": [],
                                    "querytranslation": "\"consensus development conferences as topic\"[mh]",
                                    "warninglist": {"phrasesignored": [],
                                                    "quotedphrasesnotfound": [
                                                        "\"consensus development conferences as topic\"[mh]"],
                                                    "outputmessages": ["No items found."]}}}

CDA_SNIPPET = ('"Clinical protocols"[MESH] OR "Consensus"[MESH] OR "Consensus development '
               'conferences as topic"[MESH] OR "Guidelines as topic" [Mesh:NoExp] OR '
               '"guideline"[pt] OR "practice guideline"[pt] OR "consensus development '
               'conference"[pt] OR "consensus development conference, NIH"[pt]')

# MeSH 2026 heading renames added in 0.1.2 (classification.nlm.nih.gov/scope; each quoted old
# name checked in PubMed on 2026-11-12: 0 records, "quoted phrase not found").
RENAMES_2026 = [
    ("Depressive Disorder, Major", "Major Depressive Disorder"),
    ("Pain, Postoperative", "Postoperative Pain"),
    ("Carcinoma, Basal Cell", "Basal Cell Carcinoma"),
    ("Conscious Sedation", "Procedural Sedation"),
    ("Pain, Intractable", "Intractable Pain"),
    ("Receptors, Kainic Acid", "Kainic Acid Receptors"),
    ("Surgical Procedures, Colorectal", "Colorectal Surgical Procedures"),
]


def fake_fetch(url):
    if "Retraction+of+Publication" in url or "Retraction%20of%20Publication" in url:
        return OLD_REPLY
    if "Made+Up+Type" in url:
        return {"esearchresult": {"count": "0", "idlist": [],
                                  "warninglist": {"quotedphrasesnotfound": ["\"Made Up Type\"[pt]"]}}}
    if "Retracted+Publication" in url:
        return RETRACTED_REPLY
    return NEW_REPLY


def broken_fetch(url):
    raise OSError("network down")


class TestParsing(unittest.TestCase):
    def test_quoted_term(self):
        t = p.find_terms('"Retraction of Publication"[pt]')
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0]["term"], "Retraction of Publication")
        self.assertEqual(t[0]["start"], 0)

    def test_unquoted_term_after_operator(self):
        t = p.find_terms("cancer[ti] AND retraction of publication[pt]")
        self.assertEqual([x["term"] for x in t], ["retraction of publication"])

    def test_tag_variants_and_case(self):
        for q in ("Congress[PTYP]", "congress[publication type]", '"Congress" [pt]',
                  "Congress[ Publication Type ]"):
            t = p.find_terms(q)
            self.assertEqual(len(t), 1, q)
            self.assertEqual(p.key(t[0]["term"]), "congress", q)

    def test_other_fields_ignored(self):
        self.assertEqual(p.find_terms('retraction of publication[ti] OR "x"[tiab]'), [])

    def test_classify(self):
        self.assertEqual(p.classify("Retraction of Publication"), ("renamed", "Retraction Notice"))
        self.assertEqual(p.classify("congress"), ("renamed", "Conference Proceedings"))
        self.assertEqual(p.classify("Consensus Development Conference"),
                         ("renamed", "Consensus Statement"))
        self.assertEqual(p.classify("Consensus Development Conference, N.I.H."),
                         ("discontinued", None))
        self.assertEqual(p.classify("Consensus Development Conference, NIH"),
                         ("discontinued", None))
        self.assertEqual(p.classify("Overall"), ("discontinued", None))
        self.assertEqual(p.classify("Retracted Publication"), ("ok", None))
        self.assertEqual(p.classify("Retraction Notice"), ("ok", None))

    def test_seventeen_discontinued(self):
        self.assertEqual(len(p.DISCONTINUED), 17)
        self.assertEqual(len(p.RENAMED), 3)
        self.assertEqual(len(p.MESH_RENAMED), 8)

    def test_rename_years(self):
        # NLM Tech Bull 2024 Nov-Dec (461):e4 and 2026 Jan-Feb (468):e6.
        self.assertEqual(p.RENAMED_YEAR[p.key("Retraction of Publication")], 2025)
        self.assertEqual(p.RENAMED_YEAR[p.key("Congress")], 2026)
        self.assertEqual(p.RENAMED_YEAR[p.key("Consensus Development Conference")], 2026)
        self.assertEqual(set(p.RENAMED_YEAR), set(p.RENAMED))
        self.assertEqual(set(p.MESH_RENAMED_YEAR), set(p.MESH_RENAMED))

    def test_version(self):
        self.assertEqual(p.VERSION, "0.1.2")
        self.assertNotIn("following the 2025 MeSH change", p.__doc__)


class TestMesh(unittest.TestCase):
    def test_mesh_tags_found(self):
        for q in ('"Guidelines as topic" [Mesh:NoExp]', '"Consensus"[MESH]', 'consensus[mh]',
                  '"Consensus"[MeSH Terms]', '"Consensus"[majr]', '"Consensus"[mh:noexp]'):
            t = p.find_terms(q)
            self.assertEqual(len(t), 1, q)
            self.assertEqual(t[0]["field"], "mesh", q)
        t = p.find_terms('"Guidelines as topic" [Mesh:NoExp]')[0]
        self.assertEqual(t["term"], "Guidelines as topic")
        self.assertTrue(t["quoted"])
        self.assertFalse(p.find_terms("consensus[mh]")[0]["quoted"])

    def test_classify_mesh(self):
        self.assertEqual(p.classify("Consensus Development Conferences as Topic", "mesh", True),
                         ("renamed", "Consensus Statements as Topic"))
        self.assertEqual(p.classify("consensus development conferences as topic", "mesh", False),
                         ("renamed_mapped", "Consensus Statements as Topic"))
        self.assertEqual(p.classify("Consensus", "mesh", True), ("ok", None))
        # a publication-type name tagged as MeSH is not a publication-type finding
        self.assertEqual(p.classify("Congress", "mesh", True), ("ok", None))

    def test_quoted_old_heading_in_or_group(self):
        f = [x for x in p.check_text('"Consensus"[MESH] OR "Consensus development conferences '
                                     'as topic"[MESH]') if x["status"] != "ok"]
        self.assertEqual(len(f), 1)
        self.assertEqual((f[0]["field"], f[0]["status"]), ("mesh", "renamed"))
        self.assertEqual((f[0]["operator"], f[0]["side"]), ("OR", "before"))
        self.assertIn('records indexed with "Consensus Statements as Topic"', f[0]["effect"])
        self.assertEqual(f[0]["mesh_year"], 2026)
        self.assertTrue(p.is_problem(f[0]))

    def test_unquoted_old_heading_is_mapped_not_a_problem(self):
        out = io.StringIO()
        code = p.main(["consensus development conferences as topic[mh]"], out=out)
        self.assertEqual(code, 0)
        self.assertIn("mapped because unquoted", out.getvalue())

    def test_cda_style_filter(self):
        f = [x for x in p.check_text(CDA_SNIPPET) if x["status"] != "ok"]
        self.assertEqual([(x["field"], x["status"]) for x in f],
                         [("mesh", "renamed"), ("pt", "renamed"), ("pt", "discontinued")])
        self.assertEqual(sum(1 for x in f if p.is_problem(x)), 2)
        self.assertEqual(p.main([CDA_SNIPPET], out=io.StringIO()), 1)

    def test_fix_mesh_and_pt(self):
        self.assertEqual(
            p.fix_text('"Consensus development conferences as topic"[MESH] OR '
                       '"consensus development conference"[pt]'),
            '"Consensus Statements as Topic"[MESH] OR "Consensus Statement"[pt]')

    def test_live_checks_quoted_mesh_only(self):
        urls = []

        def fetch(url):
            urls.append(url)
            return OLD_MESH_REPLY

        findings, errors = p.run(['"Made Up Heading"[mh] OR cancer[mh]'], live=True,
                                 fetch=fetch, pause=0)
        self.assertEqual(errors, [])
        self.assertEqual(len(urls), 1)
        self.assertIn("%22Made+Up+Heading%22%5Bmh%5D", urls[0])
        made = [x for x in findings if x["term"] == "Made Up Heading"][0]
        self.assertEqual(made["status"], "not_recognized")
        self.assertIn("silently misses", made["effect"])
        cancer = [x for x in findings if x["term"] == "cancer"][0]
        self.assertEqual(cancer["status"], "ok")
        self.assertNotIn("live", cancer)

    def test_describe_mesh_unrecognized(self):
        out = io.StringIO()
        code = p.main(["--live", '"Made Up Heading"[mh]'], fetch=lambda u: OLD_MESH_REPLY,
                      out=out)
        self.assertEqual(code, 1)
        self.assertIn("does not recognize this MeSH heading", out.getvalue())


class TestMesh2026Headings(unittest.TestCase):
    def test_seven_more_renames(self):
        for old, new in RENAMES_2026:
            self.assertEqual(p.classify(old, "mesh", True), ("renamed", new), old)
            self.assertEqual(p.classify(old.upper(), "mesh", False), ("renamed_mapped", new), old)
            self.assertEqual(p.MESH_RENAMED_YEAR[p.key(old)], 2026, old)
            self.assertEqual(p.classify(new, "mesh", True), ("ok", None), new)
            # as a publication type these names mean nothing special
            self.assertEqual(p.classify(old, "pt", True), ("ok", None), old)

    def test_depression_strategy_line(self):
        q = '("Depressive Disorder, Major"[Mesh] OR depress*[tiab]) AND "Ketamine"[Mesh]'
        f = [x for x in p.check_text(q) if x["status"] != "ok"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["term"], "Depressive Disorder, Major")
        self.assertEqual((f[0]["operator"], f[0]["side"]), ("OR", "after"))
        self.assertIn('records indexed with "Major Depressive Disorder"', f[0]["effect"])
        self.assertEqual(f[0]["mesh_year"], 2026)
        self.assertTrue(p.is_problem(f[0]))
        self.assertEqual(p.main([q], out=io.StringIO()), 1)

    def test_fix_comma_headings(self):
        self.assertEqual(
            p.fix_text('"Pain, Postoperative"[Mesh] OR "Depressive Disorder, Major"[mh:noexp]'),
            '"Postoperative Pain"[Mesh] OR "Major Depressive Disorder"[mh:noexp]')

    def test_unquoted_comma_heading_is_mapped(self):
        out = io.StringIO()
        code = p.main(["ketamine AND depressive disorder, major[mh]"], out=out)
        self.assertEqual(code, 0)
        self.assertIn('renamed to "Major Depressive Disorder" (MeSH 2026); mapped because '
                      'unquoted.', out.getvalue())

    def test_url_encoded_link_in_file(self):
        text = ("https://pubmed.ncbi.nlm.nih.gov/?term=%22Conscious+Sedation%22%5BMesh%5D"
                "+AND+endoscopy%5Btiab%5D\n")
        f = [x for x in p.scan_lines(text, "links.txt") if x["status"] != "ok"]
        self.assertEqual(len(f), 1)
        self.assertEqual((f[0]["new_name"], f[0]["operator"]), ("Procedural Sedation", "AND"))
        self.assertIn("0 records", f[0]["effect"])


class TestOperators(unittest.TestCase):
    def one(self, q):
        f = [x for x in p.check_text(q) if x["status"] != "ok"]
        self.assertEqual(len(f), 1, q)
        return f[0]

    def test_or_first(self):
        f = self.one('("Retraction of Publication"[pt] OR "Retracted Publication"[pt])')
        self.assertEqual((f["operator"], f["side"]), ("OR", "after"))
        self.assertIn("silently misses", f["effect"])
        self.assertIn('"Retraction Notice"', f["effect"])

    def test_or_second(self):
        f = self.one('"Retracted Publication"[pt] OR "Retraction of Publication"[pt]')
        self.assertEqual((f["operator"], f["side"]), ("OR", "before"))
        self.assertIn("drops", f["effect"])

    def test_and(self):
        f = self.one('"Cochrane Database Syst Rev"[ta] AND "Retraction of Publication"[pt]')
        self.assertEqual((f["operator"], f["side"]), ("AND", "before"))
        self.assertIn("0 records", f["effect"])

    def test_and_inside_parentheses(self):
        f = self.one('cancer[ti] AND (Retraction of Publication[pt])')
        self.assertEqual(f["operator"], "AND")

    def test_not_excludes_nothing(self):
        f = self.one('"Cochrane Database Syst Rev"[ta] NOT "Retraction of Publication"[pt]')
        self.assertEqual((f["operator"], f["side"]), ("NOT", "before"))
        self.assertIn("excludes nothing", f["effect"])

    def test_not_with_term_first_is_zero(self):
        f = self.one('"Retraction of Publication"[pt] NOT "Cochrane Database Syst Rev"[ta]')
        self.assertEqual((f["operator"], f["side"]), ("NOT", "after"))
        self.assertIn("0 records", f["effect"])

    def test_alone(self):
        f = self.one('"Retraction of Publication"[pt]')
        self.assertEqual((f["operator"], f["side"]), (None, None))
        self.assertIn("0 records", f["effect"])

    def test_word_containing_or_is_not_operator(self):
        f = self.one('cancer FOR "Congress"[pt]')
        self.assertEqual(f["operator"], None)

    def test_discontinued_effect(self):
        f = self.one('cancer AND overall[pt]')
        self.assertEqual(f["status"], "discontinued")
        self.assertIn("older citations", f["effect"])

    def test_retraction_note(self):
        f = self.one('"Retraction of Publication"[pt]')
        self.assertIn("hasretractionof", f["note"])


class TestFix(unittest.TestCase):
    def test_fix_quoted(self):
        self.assertEqual(p.fix_text('("Retraction of Publication"[pt] OR "Retracted Publication"[pt])'),
                         '("Retraction Notice"[pt] OR "Retracted Publication"[pt])')

    def test_fix_unquoted_keeps_space_and_tag(self):
        self.assertEqual(p.fix_text("cancer AND retraction of publication [pt]"),
                         'cancer AND "Retraction Notice" [pt]')

    def test_fix_several(self):
        self.assertEqual(p.fix_text('Congress[pt] OR "Consensus Development Conference"[ptyp]'),
                         '"Conference Proceedings"[pt] OR "Consensus Statement"[ptyp]')

    def test_fix_leaves_discontinued(self):
        q = '"Consensus Development Conference, NIH"[pt] OR overall[pt]'
        self.assertEqual(p.fix_text(q), q)


class TestFiles(unittest.TestCase):
    def test_scan_code_and_urls(self):
        text = "\n".join([
            "# saved search",
            'q = "\\"Retraction of Publication\\"[pt] OR \\"Retracted Publication\\"[pt]"',
            "term <- 'retraction of publication[pt]'",
            "https://pubmed.ncbi.nlm.nih.gov/?term=cancer+AND+%22Retraction+of+Publication%22%5Bpt%5D",
            'nothing here "Retraction Notice"[pt]',
        ])
        f = [x for x in p.scan_lines(text, "s.txt") if x["status"] != "ok"]
        self.assertEqual([x["line"] for x in f], [2, 3, 4])
        self.assertEqual(f[0]["operator"], "OR")
        self.assertEqual(f[2]["operator"], "AND")

    def test_run_on_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "strategy.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write('#1 exercise[tiab]\n#2 #1 NOT "Retraction of Publication"[pt]\n')
            findings, errors = p.run([path])
            self.assertEqual(errors, [])
            bad = [x for x in findings if x["status"] == "renamed"]
            self.assertEqual(len(bad), 1)
            self.assertEqual(bad[0]["line"], 2)
            self.assertEqual(bad[0]["operator"], "NOT")


class TestLive(unittest.TestCase):
    def test_parse_esearch(self):
        self.assertEqual(p.parse_esearch(OLD_REPLY)["recognized"], False)
        r = p.parse_esearch(NEW_REPLY)
        self.assertEqual((r["count"], r["recognized"]), (34339, True))
        self.assertEqual(p.parse_esearch({})["recognized"], None)

    def test_parse_esearch_errorlist(self):
        obj = {"esearchresult": {"count": "0", "errorlist": {"phrasesnotfound": ["publication"]}}}
        self.assertEqual(p.parse_esearch(obj)["recognized"], False)

    def test_url(self):
        u = p.esearch_url("Retraction Notice")
        self.assertIn("esearch.fcgi?", u)
        self.assertIn("%22Retraction+Notice%22%5Bpt%5D", u)
        self.assertIn("tool=pubmed-pt-check", u)
        self.assertIn("%22Consensus%22%5Bmh%5D", p.esearch_url("Consensus", "mesh"))

    def test_unknown_type_flagged_live(self):
        out = io.StringIO()
        code = p.main(["--live", '"Made Up Type"[pt] OR "Retracted Publication"[pt]'],
                      fetch=fake_fetch, out=out)
        self.assertEqual(code, 1)
        self.assertIn("does not recognize", out.getvalue())

    def test_renamed_confirmed_live(self):
        findings, errors = p.run(['"Retraction of Publication"[pt]'], live=True, fetch=fake_fetch,
                                 pause=0)
        self.assertEqual(errors, [])
        self.assertEqual(findings[0]["live"]["recognized"], False)
        self.assertTrue(p.is_problem(findings[0]))

    def test_renamed_but_recognized_is_not_a_problem(self):
        findings, _ = p.run(['"Retraction of Publication"[pt]'], live=True,
                            fetch=lambda u: NEW_REPLY, pause=0)
        self.assertFalse(p.is_problem(findings[0]))
        self.assertIn("still renamed", findings[0]["effect"])

    def test_live_failure_exit_2(self):
        out = io.StringIO()
        code = p.main(["--live", '"Retraction Notice"[pt]'], fetch=broken_fetch, out=out)
        self.assertEqual(code, 2)
        self.assertIn("live lookup failed", out.getvalue())


class TestMain(unittest.TestCase):
    def test_clean_query_exit_0(self):
        out = io.StringIO()
        self.assertEqual(p.main(['"Retracted Publication"[pt] OR "Retraction Notice"[pt]'], out=out), 0)
        self.assertIn("0 renamed", out.getvalue())

    def test_renamed_exit_1_and_text(self):
        out = io.StringIO()
        code = p.main(['"Cochrane Database Syst Rev"[ta] NOT "Retraction of Publication"[pt]'], out=out)
        self.assertEqual(code, 1)
        self.assertIn('renamed to "Retraction Notice"', out.getvalue())
        self.assertIn("(MeSH 2025)", out.getvalue())

    def test_rename_year_2026_in_text(self):
        out = io.StringIO()
        p.main(['"Consensus Development Conference"[pt]'], out=out)
        self.assertIn('renamed to "Consensus Statement" (MeSH 2026)', out.getvalue())

    def test_discontinued_only_exit_0(self):
        self.assertEqual(p.main(["overall[pt]"], out=io.StringIO()), 0)

    def test_json(self):
        out = io.StringIO()
        p.main(["--json", "Congress[pt] AND cancer"], out=out)
        obj = json.loads(out.getvalue())
        self.assertEqual(obj["findings"][0]["new_name"], "Conference Proceedings")
        self.assertEqual(obj["findings"][0]["operator"], "AND")
        self.assertEqual(obj["findings"][0]["mesh_year"], 2026)
        self.assertEqual(obj["version"], p.VERSION)

    def test_fix_cli(self):
        out = io.StringIO()
        self.assertEqual(p.main(["--fix", "Congress[pt]"], out=out), 0)
        self.assertEqual(out.getvalue(), '"Conference Proceedings"[pt]\n')

    def test_stdin(self):
        out = io.StringIO()
        code = p.main(["-"], out=out, stdin=io.StringIO('"Retraction of Publication"[pt]'))
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
