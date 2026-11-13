# PREREG-ATM-1: MeSH entry terms that PubMed does not map to their heading

MV2, Munim, Inc., mv2@munimtech.com. Written 2026-11-13 (UTC) before any census output
existed. Made with AI agents working in MV2's name; no human has reviewed it.
Text CC BY 4.0; code (`atm_census.py`) Apache-2.0.

## Question

PubMed's Automatic Term Mapping (ATM) is meant to turn an untagged, unquoted MeSH entry term
into its heading. `heart attack` is searched as `"myocardial infarction"[MeSH Terms] OR ...`.
How often does an official MeSH 2026 entry term, typed into PubMed as a searcher would type
it, fail to reach its own heading? And is that more common for names that used to be headings
themselves and were merged into another heading?

## What we saw before writing this (so the predictions are not blind to it)

All on 2026-11-13 through E-utilities `esearch` and NLM's MeSH SPARQL (current graph):

- Mapped to their own heading: `Heart Attack` (D009203), and four terms created in 2025:
  `Hospital at Home` (D018575), `Healthy Habits` (D000070497), `Mechanical Stiffness`
  (D004548), `Basal Cell Epithelioma` (D002280). These were picked by hand, not at random.
- A SPARQL query for obsolete topical descriptors whose preferred term is now a term of a
  current descriptor returned 82 obsolete descriptors (68 distinct current descriptors), by
  last active year: 2015: 10, 2016: 42, 2017: 7, 2018: 9, 2019: 5, 2022: 2, 2023: 1, 2025: 6.
  We tested the first four rows it returned plus one known case:
  - `Cervical Intraepithelial Neoplasia` (obsolete D018290, now in D002578 Uterine Cervical
    Dysplasia): maps.
  - `American Indians or Alaska Natives` (obsolete D000086562, now in D044467): maps.
  - `Dietary Patterns` (obsolete D000095362, now in D004032 Diet): maps.
  - `Korarchaeota` (obsolete D019708, now a term of D019615 Crenarchaeota): **does not map**.
    PubMed searches `"Korarchaeota"[All Fields]` (71 records).
  - `Pneumocystis jirovecii` (obsolete D045382, now a term of D045363 Pneumocystis carinii;
    see [mesh-taxid-audit/PNEUMOCYSTIS.md](https://github.com/munimtechnologies/mesh-taxid-audit/blob/main/PNEUMOCYSTIS.md)):
    **does not map**. PubMed searches the genus Pneumocystis (and Pneumocystis pneumonia) AND
    `"jirovecii"[All Fields]` (2,985 records).
- We did not look at any random entry term before writing the predictions.

Prior art: NLM's help pages and training material explain ATM and give one-off examples of
words that do not map (for example "neuter"). We found no census of how many MeSH entry terms
ATM fails to map, and nothing on merged headings (web search, 2026-11-13).

## Method (fixed before the run)

`atm_census.py` 0.1.0, seed 20261113:

1. Parse `desc2026.gz` (NLM MeSH 2026 XML, the vocabulary PubMed searches with on 2026-11-13).
2. **Set A:** run the SPARQL query in the script (obsolete topical descriptor's preferred term,
   now a term of a current descriptor that is not obsolete). One row per (current descriptor,
   name). Rows not found as a term in desc2026, or not safe to send untagged, are skipped and
   counted.
3. **Set B:** pool = every non-preferred term of a current topical descriptor (class 1),
   excluding: terms whose normalised form equals any descriptor's preferred name (including
   its own, so punctuation variants are out); terms held by more than one descriptor; terms
   with `[`, `]`, `"`, `*`, unbalanced parentheses, or upper-case AND/OR/NOT; Set A names.
   Sort by (descriptor UI, term) and draw 1,500 with `random.Random(20261113).sample`.
4. For each term: `esearch` with the term untagged and unquoted. **own** = the term's own
   heading (normalised: lower case, punctuation to spaces) appears as `"..."[MeSH Terms]` in
   `querytranslation`. **fail** = `other_mesh` (only other headings) or `none` (no heading).
   Request errors are counted separately and are not failures.
5. For each failure: `"<heading>"[mh]` (heading total) and `"<heading>"[mh] NOT (<term>)`
   (records under the heading the untagged term does not retrieve).
6. Sanity rows (observed above, so they test the code, not the hypothesis): Heart Attack ->
   own; Healthy Habits -> own; Korarchaeota -> fail; Pneumocystis jirovecii -> fail.

## Predictions

| # | Prediction | How graded |
|---|---|---|
| P1 | All 4 sanity rows come out as expected | `sanity.json` all_pass |
| P2 | Set B failure rate is between 0.5% and 10% | `summary.json` set_b.fail_rate |
| P3 | Set A fails more often than Set B | one-sided Fisher p < 0.05 (`fisher_a_gt_b_p`) |
| P4 | At least 8 Set A names fail | set_a.fail >= 8 |
| P5 | At least a third of Set B failures leave >= 100 heading records unretrieved | set_b_fail_missed_ge_100 / set_b.fail >= 1/3 |
| P6 | Terms in a non-preferred (narrower) concept fail more often than terms in the preferred concept | point estimates in set_b_subgroups.concept_preferred (no test) |

How blind each one is: P1 is not blind at all (a code check). P2, P5 and P6 are blind: no
random entry term was looked at. P3 and P4 are partly informed: we saw 1 failure in the 4
Set A rows the query returned first, plus the Pneumocystis case we already knew.

Exploratory, not graded: failure rates by lexical tag, word count, term creation year and
inverted ("X, Y") form; Set A failures by the year the old heading was deleted.

## What we will publish either way

GRADING-ATM-1.md with every prediction marked held or failed, `set_a.csv`, `set_b.csv`,
`failures.csv`, and a hand check of 20 failures (or all, if fewer): each one re-run by hand,
and a note on whether the miss matters to a searcher. If failures turn out to be rare, that is
the result: ATM is reliable for MeSH entry terms, and the merged-heading cases are exceptions.

## Limits

One day of PubMed behaviour; ATM can change at any time. Untagged search is only one way people
search (quoted and [mh]-tagged searches are covered in MESH-RENAMES*.md). "own" means the
heading is searched, not that the result is complete. Set A covers only obsolete descriptors
that NLM's RDF still carries (lastActiveYear 2015 onward).
