# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# Licensed under the Apache License, Version 2.0 (Apache-2.0). See LICENSE.
# Made with AI agents working in MV2's name.
import io
import unittest
from xml.sax.saxutils import escape

import mesh_year_diff as m


def rec(ui, name, terms=(), cls="1", trees=("C01",)):
    t = "".join("<Term><String>%s</String></Term>" % escape(x) for x in (name,) + tuple(terms))
    name = escape(name)
    tr = "".join("<TreeNumber>%s</TreeNumber>" % x for x in trees)
    return ('<DescriptorRecord DescriptorClass="%s"><DescriptorUI>%s</DescriptorUI>'
            '<DescriptorName><String>%s</String></DescriptorName>'
            '<PharmacologicalActionList><PharmacologicalAction><DescriptorReferredTo>'
            '<DescriptorUI>D999999</DescriptorUI><DescriptorName><String>Other</String>'
            '</DescriptorName></DescriptorReferredTo></PharmacologicalAction>'
            '</PharmacologicalActionList>'
            '<TreeNumberList>%s</TreeNumberList>'
            '<ConceptList><Concept PreferredConceptYN="Y"><TermList>%s</TermList></Concept>'
            '</ConceptList></DescriptorRecord>' % (cls, ui, name, tr, t))


def xml(*records):
    return io.BytesIO(('<?xml version="1.0"?>\n<DescriptorRecordSet LanguageCode = "eng">'
                       + "".join(records) + "</DescriptorRecordSet>").encode("utf-8"))


OLD = xml(rec("D1", "Pregnant Women"),
          rec("D2", "Tinea cruris"),
          rec("D3", "Gone Heading"),
          rec("D4", "Same Name", ("Alias",)),
          rec("D5", "Congress", cls="2", trees=("V02.300",)),
          rec("D6", "Merged Away"))
NEW = xml(rec("D1", "Pregnant People", ("Pregnant Women",)),
          rec("D2", "Tinea Cruris"),
          rec("D4", "Same Name", ("Alias",)),
          rec("D5", "Conference Proceedings", cls="2", trees=("V02.300",)),
          rec("D7", "Survivor", ("Merged Away",)),
          rec("D8", "Brand New"))


class TestNorm(unittest.TestCase):
    def test_case_and_punctuation(self):
        self.assertEqual(m.norm("Health Disparate, Minority and Vulnerable Populations"),
                         m.norm("Health Disparate Minority and Vulnerable Populations"))
        self.assertEqual(m.norm("Tinea cruris"), "tinea cruris")
        self.assertEqual(m.norm("Meta-Research"), "meta research")
        self.assertNotEqual(m.norm("Pregnant Women"), m.norm("Pregnant People"))
        self.assertEqual(m.norm(None), "")


class TestParse(unittest.TestCase):
    def test_records(self):
        r = m.parse_records(xml(rec("D1", "A & B", ("Alt",))), "desc")
        self.assertEqual(list(r), ["D1"])
        self.assertEqual(r["D1"]["name"], "A & B")
        self.assertEqual(r["D1"]["terms"], {"A & B", "Alt"})
        self.assertEqual(r["D1"]["trees"], ["C01"])
        self.assertEqual(r["D1"]["cls"], "1")

    def test_nested_ui_ignored(self):
        r = m.parse_records(xml(rec("D1", "X"), rec("D2", "Y")), "desc")
        self.assertEqual(sorted(r), ["D1", "D2"])
        self.assertNotIn("D999999", r)

    def test_qualifiers(self):
        q = io.BytesIO(b'<?xml version="1.0"?><QualifierRecordSet LanguageCode = "eng">'
                       b'<QualifierRecord><QualifierUI>Q000002</QualifierUI><QualifierName>'
                       b'<String>abnormalities</String></QualifierName><TreeNumberList>'
                       b'<TreeNumber>Y02.030.010</TreeNumber></TreeNumberList><ConceptList>'
                       b'<Concept><TermList><Term><String>abnormalities</String></Term><Term>'
                       b'<String>anomalies</String></Term></TermList></Concept></ConceptList>'
                       b'</QualifierRecord></QualifierRecordSet>')
        r = m.parse_records(q, "qual")
        self.assertEqual(r["Q000002"]["name"], "abnormalities")
        self.assertEqual(r["Q000002"]["terms"], {"abnormalities", "anomalies"})
        self.assertEqual(r["Q000002"]["cls"], "")


class TestDiff(unittest.TestCase):
    def setUp(self):
        OLD.seek(0)
        NEW.seek(0)
        self.d = m.diff(m.parse_records(OLD, "desc"), m.parse_records(NEW, "desc"))

    def test_renamed(self):
        ren = {r["ui"]: r for r in self.d["renamed"]}
        self.assertEqual(sorted(ren), ["D1", "D2", "D5"])
        self.assertEqual(ren["D1"]["new"], "Pregnant People")
        self.assertEqual(ren["D1"]["change"], "words")
        self.assertTrue(ren["D1"]["old_kept_as_entry"])
        self.assertEqual(ren["D2"]["change"], "case_or_punctuation")
        # a case-only rename still matches its old spelling, so it counts as kept
        self.assertTrue(ren["D2"]["old_kept_as_entry"])
        self.assertEqual(ren["D5"]["tag"], "pt")
        self.assertEqual(ren["D5"]["class"], "publication type")
        self.assertEqual(ren["D1"]["tag"], "mesh")
        self.assertEqual(ren["D1"]["old_name_now_in"], "")

    def test_deleted(self):
        dele = {r["ui"]: r for r in self.d["deleted"]}
        self.assertEqual(sorted(dele), ["D3", "D6"])
        self.assertEqual(dele["D3"]["now_entry_of"], "")
        self.assertEqual(dele["D6"]["now_entry_of"], "D7")
        self.assertEqual(dele["D6"]["now_entry_of_names"], "Survivor")

    def test_added(self):
        self.assertEqual([r["ui"] for r in self.d["added"]], ["D7", "D8"])
        self.assertEqual(self.d["added"][1]["new"], "Brand New")


class TestPubmed(unittest.TestCase):
    def test_parse_esearch(self):
        self.assertEqual(m.parse_esearch({"esearchresult": {"count": "17946"}}),
                         {"count": 17946, "recognized": True, "not_found": ""})
        r = m.parse_esearch({"esearchresult": {"count": "0", "warninglist": {
            "quotedphrasesnotfound": ['"pregnant women"[mh]']}}})
        self.assertEqual(r["count"], 0)
        self.assertFalse(r["recognized"])
        self.assertEqual(r["not_found"], '"pregnant women"[mh]')
        self.assertIsNone(m.parse_esearch({})["recognized"])

    def test_url(self):
        u = m.esearch_url('Pregnant "Women"', "mesh")
        self.assertIn("term=%22Pregnant+Women%22%5Bmh%5D", u)
        self.assertIn("tool=mesh-year-diff", u)
        self.assertIn("%5Bpt%5D", m.esearch_url("Congress", "pt"))

    def test_checks(self):
        seen = []

        def fetch(url):
            seen.append(url)
            if "People" in url:
                return {"esearchresult": {"count": "0", "warninglist": {
                    "quotedphrasesnotfound": ['"pregnant people"[mh]']}}}
            if "Boom" in url:
                raise OSError("down")
            return {"esearchresult": {"count": "5"}}

        rows = [{"ui": "D1", "old": "Pregnant Women", "new": "Pregnant People", "tag": "mesh"},
                {"ui": "D3", "old": "Gone Heading", "new": "", "tag": "mesh"},
                {"ui": "D9", "old": "Boom", "tag": "pt"}]
        out = m.pubmed_checks(rows, fetch, pause=0, today="2026-11-12")
        self.assertEqual([(o["ui"], o["which"]) for o in out],
                         [("D1", "old"), ("D1", "new"), ("D3", "old"), ("D9", "old")])
        self.assertEqual(out[0]["count"], 5)
        self.assertTrue(out[0]["recognized"])
        self.assertFalse(out[1]["recognized"])
        self.assertEqual(out[1]["query"], '"Pregnant People"[mh]')
        self.assertEqual(out[3]["query"], '"Boom"[pt]')
        self.assertIn("OSError", out[3]["error"])
        self.assertIsNone(out[3]["count"])
        self.assertEqual(out[0]["checked"], "2026-11-12")
        self.assertEqual(len(seen), 6)


class TestReport(unittest.TestCase):
    def test_report(self):
        OLD.seek(0)
        NEW.seek(0)
        d = m.diff(m.parse_records(OLD, "desc"), m.parse_records(NEW, "desc"))
        txt = m.report_md(d, {"renamed": [], "deleted": [], "added": []},
                          [{"ui": "D1", "which": "old", "count": 5, "recognized": True}],
                          {"desc_new": {"url": "u", "bytes": 1, "sha256": "x"}}, 6, 6)
        self.assertIn("Renamed (words): 2; case/punctuation only: 1; deleted: 2; added: 2.", txt)
        self.assertIn("| D1 | Pregnant Women | Pregnant People | topical | yes | 5 |  |", txt)
        self.assertIn("| D6 | Merged Away | topical | Survivor |  |", txt)


if __name__ == "__main__":
    unittest.main()
