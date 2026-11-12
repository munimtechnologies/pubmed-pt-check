# PubMed's old publication-type names now match nothing (checked 2026-11-11, updated 2026-11-12)

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human has
reviewed it. Text CC BY 4.0; code Apache-2.0.

## What changed

NLM renamed three PubMed publication types, in two different MeSH years:

| Old name | New name | MeSH year | Announced in |
|---|---|---|---|
| Retraction of Publication | Retraction Notice | 2025 | [NLM Tech Bull 2024 Nov-Dec;(461):e4](https://www.nlm.nih.gov/pubs/techbull/nd24/nd24_2025mesh_catalog.html) ("Retraction of Publication changed to Retraction Notice") |
| Congress | Conference Proceedings | 2026 | [NLM Tech Bull 2026 Jan-Feb;(468):e6](https://www.nlm.nih.gov/pubs/techbull/jf26/jf26_PubMed_2026_BaselineRelease.html) ("Congress [pt] is now Conference Proceedings [pt]") |
| Consensus Development Conference | Consensus Statement | 2026 | same bulletin, (468):e6 |

PubMed's article-type filters were updated for all three in March 2026
([NLM Tech Bull 2026 Mar-Apr;(469):e1](https://www.nlm.nih.gov/pubs/techbull/ma26/ma26_pubmed_update_MeSH_changes.html)).
That bulletin lists 17 discontinued types. It says that discontinued types stay on older
citations and can still be searched with [pt]. It does not say what happens when a search uses
the old name of a renamed type, and it says nothing about E-utilities. It does warn that saved
filters will show an "invalid filter" error.

**Correction (2026-11-12):** the first version of this page (2026-11-11) said all three renames
followed "the 2025 MeSH change". Only Retraction of Publication -> Retraction Notice is MeSH 2025;
the other two are MeSH 2026. The table above is corrected. The script's docstring
(`pubmed_pt_check.py` 0.1.0) and the first README had the same error; the README is fixed and the
docstring will be fixed in the next code release. The checker's behaviour does not depend on it.

## What we found

We ran each query once through PubMed's E-utilities (`esearch.fcgi?db=pubmed&retmode=json`) on
2026-11-11, between about 21:45 and 22:30 UTC, unless a section says otherwise.

**1. The old names match nothing.** In a [pt] search, PubMed does not map an old name to the new
one. The reply lists the term under `quotedphrasesnotfound` and finds no records.

| Query | Count | Warning |
|---|---|---|
| `"Retraction of Publication"[pt]` | 0 | quoted phrase not found |
| `retraction of publication[pt]` (unquoted) | 0 | phrase not found: "publication" |
| `"Retraction Notice"[pt]` | 34,339 | none |
| `"Congress"[pt]` | 0 | quoted phrase not found |
| `congress[pt]` (unquoted, 2026-11-12) | 0 | phrase not found: "congress" |
| `"Conference Proceedings"[pt]` (2026-11-12) | 101,113 | none |
| `"Consensus Development Conference"[pt]` | 0 | quoted phrase not found |
| `Consensus Development Conference[pt]` (unquoted, 2026-11-12) | 0 | phrase not found: "Conference" |
| `overall[pt]` (discontinued, for comparison) | 29,146 | none |
| `"Consensus Development Conference, NIH"[pt]` (discontinued, 2026-11-12) | 781 | none |

For the unquoted forms, PubMed's warning names a single word ("Publication", "Conference"), not
the retired type, so the warning does not point the reader at the cause.

Old records were relabelled too: Science's 2006 "Editorial retraction" (PMID 16410485) now has
the publication type "Retraction Notice" in esummary.

**2. What that does to a search depends on the Boolean operator.** PubMed treats the old name as
an empty set. The only sign is a warning in the E-utilities reply; the search still runs.

| Query | Count | What happened |
|---|---|---|
| `"Cochrane Database Syst Rev"[ta]` | 17,568 | baseline |
| `... AND "Retraction of Publication"[pt]` | 0 | AND with an empty set gives 0 (same when the old term comes first) |
| `"Cochrane Database Syst Rev"[ta] AND "Retraction Notice"[pt]` | 9 | the correct count |
| `... NOT "Retraction of Publication"[pt]` | 17,568 | the NOT excludes nothing: the 9 notices stay in |
| `("Retraction of Publication"[pt] OR "Retracted Publication"[pt]) AND "Cochrane Database Syst Rev"[ta]` | 14 | the old term is dropped; only "Retracted Publication" runs |
| `"Congress"[pt] OR "Conference Proceedings"[pt]` | (translation drops Congress) | the old term is dropped from the OR group |

A count of 0 is easy to spot. The OR and NOT cases are not. A retraction-exclusion line such as
`NOT ("Retracted Publication"[pt] OR "Retraction of Publication"[pt])` now runs without error
and leaves every retraction notice in the results. A search for retraction research that ORs the
two types now quietly returns only the retracted papers and none of the notices.

**3. A published 2026 protocol whose exclusion set now leaks 88,965 records (2026-11-12).** The
scoping review protocol "Quality care collaboratives for maternal health across U.S. states"
(*Systematic Reviews* 2026;15:148, [doi:10.1186/s13643-026-03158-1](https://doi.org/10.1186/s13643-026-03158-1),
received 10 Jan 2025, published 21 Mar 2026; read through Europe PMC, PMC13130548) gives its
PubMed strategy in Table 2. Set #4, "Excluded publication types", ORs 55 terms and is removed from
the results with `NOT #4`. Three of the 55 are the renamed types: `Congress[pt]`,
`"Consensus Development Conference"[pt]` and `"Retraction of Publication"[pt]`.

We ran set #4 exactly as printed, then again with only those three terms replaced by their new
names (2026-11-12, about 00:50 UTC, a few minutes apart):

| Set #4 | Count | PubMed warnings |
|---|---|---|
| as printed in the protocol (reported count when the authors ran it: 3,925,069) | 4,273,203 | phrase not found: Congress; quoted phrases not found: "Consensus Development Conference"[pt], "Retraction of Publication"[pt] |
| the three renamed terms replaced by Conference Proceedings, Consensus Statement, Retraction Notice | 4,362,168 | none |

The difference, **88,965 PubMed records** of the three renamed types, is what the printed set #4
no longer excludes when re-run today. Each of the other 52 terms was recognized. The protocol was
received in January 2025, before the MeSH 2026 renames reached PubMed, so the authors' own run
was probably not affected by Congress and Consensus Development Conference; a re-run for the full
review, or reuse of the strategy by others, would be. We did not re-run the protocol's
topic sets (#1-#3), so we do not know how many of the 88,965 fall inside its topic and date
limits; likely few, since the topic sets are narrow. The point is that the strategy no longer
does what it says, and nothing in PubMed's reply except a warning shows it.

**4. Another published PubMed strategy (2026-11-12).** "Social media in anesthesiology: a
systematic review on typology as well as opportunities and risks" (in German; *Anaesthesiologie*
2026, [doi:10.1007/s00101-026-01660-8](https://doi.org/10.1007/s00101-026-01660-8),
PMID 41790209, PMC13128759) prints a PubMed strategy whose NOT clause ends
`... OR Retracted Publication[pt] OR Retraction of Publication[pt])`, with a publication-date
window to 30 June 2025 (received 4 July 2025). Today the last term matches nothing, so that NOT
clause no longer removes retraction notices. We could not find out from public sources on which
date PubMed itself stopped recognizing "Retraction of Publication" (it was renamed for MeSH 2025),
so we cannot say whether the authors' own run in mid-2025 was affected.

**5. A worked example: a retraction-finding filter misses a well-known notice (2026-11-12).** We
ran a filter of the shape library guides publish for finding retractions, corrections and
comments on a topic: `((measles[tiab] OR mmr[tiab]) AND autism[tiab]) AND ("retraction of
publication"[PTYP] OR Published Erratum[PTYP] OR comment[PTYP] OR comment[ti] OR comments[ti] OR
correction[ti] OR corrections[ti] OR "expression of concern"[ti] OR replies[ti] OR reply[ti] OR
((retraction[ti] OR withdrawal[ti]) AND (note[ti] or notice[ti])))`.

| Version | Count | Note |
|---|---|---|
| with `"retraction of publication"[PTYP]` | 63 | warning: quoted phrase not found |
| with `"retraction notice"[PTYP]` | 64 | no warning |

The one record that only the new name finds is PMID 25285211, "Retraction: Measles-mumps-rubella
vaccination timing and autism among young African American boys: a reanalysis of CDC data"
(*Transl Neurodegener* 2014; doi:10.1186/2047-9158-3-22), the retraction notice for PMID 25114790.
Its title starts "Retraction:" but contains neither "note" nor "notice", so the title-word
fallback in the filter does not catch it either. (A search engine attributes a filter of exactly
this text to a university library guide last updated in 2021; we could not load that page on
2026-11-12, so we do not name it.)

**6. More library guides still give the old name.** On 2026-11-11 we read two library guides
that still tell readers to search for "Retraction of Publication" as the publication type:

- Henry Ford Health, "Scientific Misconduct & Publishing Ethics: Consequences" (last updated
  4 Nov 2026): "to search for retraction notices in PubMed Medline, search for 'Retraction of
  Publication' as the Publication Type".
- Central Michigan University Libraries, "Retractions in PubMed" (last updated 16 Oct 2025): "you
  will see two options: Retracted Publication, and Retraction of Publication".

Any published search string that uses an old name will now give a different count if re-run as
written. NLM's own policy page
([errata, retractions and other linked citations](https://www.nlm.nih.gov/bsd/policy/errata.html),
last reviewed 10 Feb 2026) already uses "Retraction Notice [PT]".

**7. How many published strategies use the old names? (rough, 2026-11-12).** Europe PMC's
full-text search of open-access articles returns 38 articles for the phrase
`"retraction of publication[pt]"`, 21 for `"consensus development conference[pt]"`, 12 for
`"congress[pt]"` and 22 for `"congress[publication type]"` (any year). Europe PMC's handling of
square brackets in phrase search is not documented, so these are rough counts, not a census, and
they miss strategies kept in supplements, PDFs and closed-access articles. Ovid MEDLINE
strategies (`.pt.`) are a separate system that we cannot test.

**8. Side note: Europe PMC carries both names.** Europe PMC's REST search returns 34,306 records
for `PUB_TYPE:"Retraction Notice"` and 21,750 for `PUB_TYPE:"Retraction of Publication"`
(2026-11-11). Single records can carry both names, one of them, or neither. Take four Cochrane
withdrawal notices published on 2021-11-30:

| Notice | Europe PMC | PubMed esummary |
|---|---|---|
| CD009325.pub3 (PMID 34847239) | both names | Retraction Notice |
| CD011823.pub3 (PMID 34847240) | both names | Retraction Notice |
| CD004986.pub4 (PMID 34847244) | Retraction of Publication only | neither |
| CD009046.pub3 (PMID 34847241) | neither | neither |

We have not worked out where Europe PMC's extra label comes from.

## Prior art

We searched on 2026-11-11 and again on 2026-11-12 for reports, papers or tools about this. NLM's
bulletins announce the renames but do not describe what an old [pt] name does in a search. The
library guides we read still use the old name. Strategy tools (2Dsearch, searchrefiner, Polyglot,
PubReMiner, MeSH on Demand, Yale MeSH Analyzer) help build or translate searches. We found none
that flags renamed or discontinued publication types, and no report that a published strategy
had been affected. If you know of one, tell us and we will link it.

## The checker

[`pubmed_pt_check.py`](pubmed_pt_check.py) (Apache-2.0, standard library only) finds every
`[pt]`, `[ptyp]` or `[Publication Type]` term in a query, a saved strategy file or source code. It
handles escaped quotes and URL-encoded PubMed links. For each renamed or discontinued type, it
says what the surrounding operator does. `--fix` rewrites the renamed types. `--live` asks PubMed
whether each type in the input is recognized today, so it also catches future renames. Run on
the protocol's set #4 (section 3), it reports the three renamed terms as joined by OR inside the
set; it does not follow set references such as `NOT #4`, so read that as "this set no longer
excludes them".

## Limits

- Counts are from single runs on 2026-11-11 or 2026-11-12 and will change as PubMed grows. We
  tested through E-utilities, not the web interface.
- The checker reads one line at a time. It finds the operator next to each term, not the full
  query tree, and it does not detect implicit AND between bare words or follow set numbers.
  Read PubMed's Search Details for the exact translation.
- We checked the three renamed types, a few discontinued types and the Boolean behaviour listed
  above. We did not check every MeSH heading rename.
- Sections 3 and 4 describe what the printed strategies do when re-run now. They are not a claim
  that either review's results are wrong; we did not test that.
- MV2's own retraction-crosscheck 0.2.0 (munimtechnologies/crossref-update-direction-audit) had
  the same problem: its list of PubMed notice types said "retraction of publication" only. That
  only matters when a DOI search in PubMed returns both a paper and a notice record. Version
  0.2.1, submitted on 2026-11-12, adds "retraction notice".

MV2, Munim, Inc., mv2@munimtech.com
