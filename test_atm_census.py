# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# Tests for atm_census.py (no network). Made with AI agents working in MV2's name.
import io
import unittest

import atm_census as ac

XML = b"""<?xml version="1.0"?>
<DescriptorRecordSet LanguageCode="eng">
<DescriptorRecord DescriptorClass="1">
 <DescriptorUI>D009203</DescriptorUI>
 <DescriptorName><String>Myocardial Infarction</String></DescriptorName>
 <ConceptList>
  <Concept PreferredConceptYN="Y"><TermList>
   <Term ConceptPreferredTermYN="Y" LexicalTag="NON" RecordPreferredTermYN="Y">
    <String>Myocardial Infarction</String></Term>
   <Term ConceptPreferredTermYN="N" LexicalTag="NON" RecordPreferredTermYN="N">
    <DateCreated><Year>2014</Year></DateCreated><String>Heart Attack</String></Term>
   <Term ConceptPreferredTermYN="N" LexicalTag="NON" RecordPreferredTermYN="N">
    <String>Infarction, Myocardial</String></Term>
   <Term ConceptPreferredTermYN="N" LexicalTag="NON" RecordPreferredTermYN="N">
    <String>Myocardial-Infarction</String></Term>
  </TermList></Concept>
  <Concept PreferredConceptYN="N"><TermList>
   <Term ConceptPreferredTermYN="Y" LexicalTag="ABB" RecordPreferredTermYN="N">
    <String>MI</String></Term>
  </TermList></Concept>
 </ConceptList>
</DescriptorRecord>
<DescriptorRecord DescriptorClass="1">
 <DescriptorUI>D000001</DescriptorUI>
 <DescriptorName><String>Calcimycin</String></DescriptorName>
 <ConceptList>
  <Concept PreferredConceptYN="Y"><TermList>
   <Term ConceptPreferredTermYN="Y" LexicalTag="NON" RecordPreferredTermYN="Y">
    <String>Calcimycin</String></Term>
   <Term ConceptPreferredTermYN="N" LexicalTag="NON" RecordPreferredTermYN="N">
    <String>MI</String></Term>
   <Term ConceptPreferredTermYN="N" LexicalTag="NON" RecordPreferredTermYN="N">
    <String>A23187 [antibiotic]</String></Term>
   <Term ConceptPreferredTermYN="N" LexicalTag="NON" RecordPreferredTermYN="N">
    <String>Myocardial Infarction</String></Term>
  </TermList></Concept>
 </ConceptList>
</DescriptorRecord>
<DescriptorRecord DescriptorClass="2">
 <DescriptorUI>D016428</DescriptorUI>
 <DescriptorName><String>Journal Article</String></DescriptorName>
 <ConceptList>
  <Concept PreferredConceptYN="Y"><TermList>
   <Term ConceptPreferredTermYN="N" LexicalTag="NON" RecordPreferredTermYN="N">
    <String>Article, Journal</String></Term>
  </TermList></Concept>
 </ConceptList>
</DescriptorRecord>
</DescriptorRecordSet>
"""

# Translations as E-utilities returned them on 2026-11-13 (backslash escapes removed).
QT_HEART = ('"myocardial infarction"[MeSH Terms] OR ("myocardial"[All Fields] AND '
            '"infarction"[All Fields]) OR "myocardial infarction"[All Fields] OR '
            '("heart"[All Fields] AND "attack"[All Fields]) OR "heart attack"[All Fields]')
QT_KOR = '"Korarchaeota"[All Fields]'
QT_PJ = ('("pneumocystis"[MeSH Terms] OR "pneumocystis"[All Fields] OR "pneumocysti"[All Fields] '
         'OR "pneumonia, pneumocystis"[MeSH Terms] OR ("pneumonia"[All Fields] AND '
         '"pneumocystis"[All Fields]) OR "pneumocystis pneumonia"[All Fields]) AND '
         '"jirovecii"[All Fields]')
QT_HOME = ('"home care services, hospital based"[MeSH Terms] OR ("home"[All Fields] AND '
           '"care"[All Fields]) OR "hospital at home"[All Fields]')


class TestClassify(unittest.TestCase):
    def test_norm(self):
        self.assertEqual(ac.norm("Home Care Services, Hospital-Based"),
                         "home care services hospital based")
        self.assertEqual(ac.norm("Bowen's Disease"), "bowen s disease")

    def test_phrases(self):
        self.assertEqual(ac.mesh_phrases(QT_PJ), ["pneumocystis", "pneumonia pneumocystis"])
        self.assertEqual(ac.mesh_phrases(QT_KOR), [])
        self.assertEqual(ac.mesh_phrases('"x y"[MeSH Terms:noexp]'), ["x y"])

    def test_classify(self):
        self.assertEqual(ac.classify_translation(QT_HEART, "Myocardial Infarction"), "own")
        self.assertEqual(ac.classify_translation(QT_HOME, "Home Care Services, Hospital-Based"),
                         "own")
        self.assertEqual(ac.classify_translation(QT_PJ, "Pneumocystis carinii"), "other_mesh")
        self.assertEqual(ac.classify_translation(QT_KOR, "Crenarchaeota"), "none")
        self.assertEqual(ac.classify_translation("", "Crenarchaeota"), "none")

    def test_usable(self):
        self.assertTrue(ac.usable("Polycystic Breakpoint (PBP) Protein"))
        self.assertTrue(ac.usable("American Indians or Alaska Natives"))
        self.assertFalse(ac.usable("A23187 [antibiotic]"))
        self.assertFalse(ac.usable("Smith AND Jones"))
        self.assertFalse(ac.usable("Unbalanced (paren"))
        self.assertFalse(ac.usable(""))


class TestParsePool(unittest.TestCase):
    def setUp(self):
        self.recs = ac.parse_desc(io.BytesIO(XML))

    def test_parse(self):
        self.assertEqual(sorted(self.recs), ["D000001", "D009203", "D016428"])
        mi = self.recs["D009203"]
        self.assertEqual(mi["cls"], "1")
        self.assertEqual(len(mi["terms"]), 5)
        ha = mi["terms"][1]
        self.assertEqual((ha["string"], ha["year"], ha["concept_preferred"],
                          ha["record_preferred"]), ("Heart Attack", "2014", True, False))
        self.assertEqual(mi["terms"][4]["lexical_tag"], "ABB")
        self.assertFalse(mi["terms"][4]["concept_preferred"])

    def test_pool(self):
        pool = ac.build_pool(self.recs)
        # D009203: preferred name out; Myocardial-Infarction has the heading's key; MI is
        # held by two records. D000001: MI ambiguous; bracket term unusable; "Myocardial
        # Infarction" is another record's preferred name. D016428 is a publication type.
        self.assertEqual([(p["ui"], p["string"]) for p in pool],
                         [("D009203", "Heart Attack"), ("D009203", "Infarction, Myocardial")])
        self.assertEqual(pool[0]["heading"], "Myocardial Infarction")


class TestStats(unittest.TestCase):
    def test_wilson(self):
        self.assertEqual(ac.wilson(0, 0), (0.0, 0.0))
        lo, hi = ac.wilson(5, 10)
        self.assertAlmostEqual(lo, 0.2366, places=3)
        self.assertAlmostEqual(hi, 0.7634, places=3)

    def test_fisher(self):
        # a=2,b=0,c=0,d=2: N=4, K=2, n1=2: P(X>=2) = C(2,2)C(2,0)/C(4,2) = 1/6
        self.assertAlmostEqual(ac.fisher_greater(2, 0, 0, 2), 1 / 6)
        # a=0: P(X>=0) = 1
        self.assertAlmostEqual(ac.fisher_greater(0, 3, 1, 2), 1.0)
        # a=1,b=1,c=1,d=1: N=4,K=2,n1=2: P(X>=1) = 1 - C(2,0)C(2,2)/6 = 5/6
        self.assertAlmostEqual(ac.fisher_greater(1, 1, 1, 1), 5 / 6)

    def test_buckets_subgroups_tally(self):
        self.assertEqual(ac.word_bucket("MI"), "1")
        self.assertEqual(ac.word_bucket("Heart Attack"), "2")
        self.assertEqual(ac.word_bucket("a b c d"), "3+")
        self.assertEqual(ac.year_bucket("1999"), "<2000")
        self.assertEqual(ac.year_bucket("2019"), "2000-2019")
        self.assertEqual(ac.year_bucket("2020"), "2020+")
        self.assertEqual(ac.year_bucket(""), "unknown")
        rows = [{"string": "Heart Attack", "result": "own", "concept_preferred": True,
                 "year": "2014", "lexical_tag": "NON"},
                {"string": "MI", "result": "none", "concept_preferred": False,
                 "year": "", "lexical_tag": "ABB"},
                {"string": "x", "result": "error"}]
        sg = ac.subgroups(rows)
        self.assertEqual(sg["concept_preferred"], {"N": {"fail": 1, "n": 1},
                                                   "Y": {"fail": 0, "n": 1}})
        self.assertEqual(sg["words"]["1"], {"fail": 1, "n": 1})
        t = ac.tally(rows)
        self.assertEqual((t["n"], t["fail"], t["none"], t["errors"]), (2, 1, 1, 1))
        self.assertAlmostEqual(t["fail_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
