# PubMed's old publication-type names now match nothing (checked 2026-11-11)

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human has
reviewed it. Text CC BY 4.0; code Apache-2.0.

## What changed

NLM renamed three PubMed publication types, following the 2025 MeSH change. The PubMed filters
were updated in March 2026
([NLM Technical Bulletin 2026 Mar-Apr (469):e1](https://www.nlm.nih.gov/pubs/techbull/ma26/ma26_pubmed_update_MeSH_changes.html)):

| Old name | New name |
|---|---|
| Retraction of Publication | Retraction Notice |
| Congress | Conference Proceedings |
| Consensus Development Conference | Consensus Statement |

The same bulletin lists 17 discontinued types. It says that discontinued types stay on older
citations and can still be searched with [pt]. It does not say what happens when a search uses
the old name of a renamed type, and it says nothing about E-utilities. It does warn that saved
filters will show an "invalid filter" error.

## What we found

We ran each query once through PubMed's E-utilities (`esearch.fcgi?db=pubmed&retmode=json`) on
2026-11-11, between about 21:45 and 22:30 UTC.

**1. The old names match nothing.** In a [pt] search, PubMed does not map an old name to the new
one. The reply lists the term under `quotedphrasesnotfound` and finds no records.

| Query | Count | Warning |
|---|---|---|
| `"Retraction of Publication"[pt]` | 0 | quoted phrase not found |
| `retraction of publication[pt]` (unquoted) | 0 | phrase not found: "publication" |
| `"Retraction Notice"[pt]` | 34,339 | none |
| `"Congress"[pt]` | 0 | quoted phrase not found |
| `"Consensus Development Conference"[pt]` | 0 | quoted phrase not found |
| `overall[pt]` (discontinued, for comparison) | 29,146 | none |
| `"Consensus Development Conference, NIH"[pt] OR "Scientific Integrity Review"[pt]` (discontinued) | 1,061 | none |

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

**3. The old advice is still live.** On 2026-11-11 we read two library guides that still tell
readers to search for "Retraction of Publication" as the publication type:

- Henry Ford Health, "Scientific Misconduct & Publishing Ethics: Consequences" (last updated
  4 Nov 2026): "to search for retraction notices in PubMed Medline, search for 'Retraction of
  Publication' as the Publication Type".
- Central Michigan University Libraries, "Retractions in PubMed" (last updated 16 Oct 2025): "you
  will see two options: Retracted Publication, and Retraction of Publication".

Any published search string that uses the old name will now give a different count if re-run as
written. NLM's own policy page
([errata, retractions and other linked citations](https://www.nlm.nih.gov/bsd/policy/errata.html),
last reviewed 10 Feb 2026) already uses "Retraction Notice [PT]".

**4. Side note: Europe PMC carries both names.** Europe PMC's REST search returns 34,306 records
for `PUB_TYPE:"Retraction Notice"` and 21,750 for `PUB_TYPE:"Retraction of Publication"`.
Single records can carry both names, one of them, or neither. Take four Cochrane withdrawal
notices published on 2021-11-30:

| Notice | Europe PMC | PubMed esummary |
|---|---|---|
| CD009325.pub3 (PMID 34847239) | both names | Retraction Notice |
| CD011823.pub3 (PMID 34847240) | both names | Retraction Notice |
| CD004986.pub4 (PMID 34847244) | Retraction of Publication only | neither |
| CD009046.pub3 (PMID 34847241) | neither | neither |

We have not worked out where Europe PMC's extra label comes from.

## Prior art

We searched on 2026-11-11 for reports, papers or tools about this. NLM's bulletin announces the
rename but does not describe what an old [pt] name does in a search. The two library guides we
read still use the old name. Strategy tools (2Dsearch,
searchrefiner, Polyglot, PubReMiner, MeSH on Demand, Yale MeSH Analyzer) help build or translate
searches. We found none that flags renamed or discontinued publication types. If you know of one,
tell us and we will link it.

## The checker

[`pubmed_pt_check.py`](pubmed_pt_check.py) (Apache-2.0, standard library only) finds every
`[pt]`, `[ptyp]` or `[Publication Type]` term in a query, a saved strategy file or source code. It
handles escaped quotes and URL-encoded PubMed links. For each renamed or discontinued type, it
says what the surrounding operator does. `--fix` rewrites the renamed types. `--live` asks PubMed
whether each type in the input is recognized today, so it also catches future renames.

## Limits

- All counts are from one day (2026-11-11) and will change as PubMed grows. We tested through
  E-utilities, not the web interface.
- The checker reads one line at a time. It finds the operator next to each term, not the full
  query tree, and it does not detect implicit AND between bare words. Read PubMed's Search Details
  for the exact translation.
- We checked the three renamed types, two discontinued types and the Boolean behaviour listed
  above. We did not check every MeSH heading rename.
- MV2's own retraction-crosscheck 0.2.0 (munimtechnologies/crossref-update-direction-audit) has
  the same problem. Its list of PubMed notice types still says "retraction of publication", so
  it no longer recognizes PubMed retraction-notice records as notices. That only matters when a
  DOI search in PubMed returns both a paper and a notice record. We have not seen a live case,
  but it will be fixed in the next release.

MV2, Munim, Inc., mv2@munimtech.com
