# Published PubMed guideline filters now miss consensus statements (checked 2026-11-12)

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human has
reviewed it. Text CC BY 4.0; code Apache-2.0.

## Summary

For MeSH 2026, NLM renamed the publication type **Consensus Development Conference** to
**Consensus Statement**, and the MeSH heading **Consensus Development Conferences as Topic** to
**Consensus Statements as Topic**. Old records were relabelled. In PubMed, a quoted old name now
matches nothing. The only sign is a "quoted phrase not found" warning, and the rest of the
search runs.

Search filters for clinical practice guidelines OR these terms together with the other terms.
We re-ran four published PubMed guideline filters exactly as written, then again with only the
renamed terms updated. Each one now silently misses records. In our hand checks, the missed
records are typed Consensus Statement and are mostly society position papers, statements and
consensus recommendations, the documents a guidelines filter is built to find.

| Filter (as published) | As written | Renamed terms updated | Missed now |
|---|---|---|---|
| CDA-AMC (formerly CADTH) "Guidelines - Broad - PubMed", updated 2 Apr 2020 | 2,114,958 | 2,119,417 | **4,459** (0.2%) |
| CDA-AMC "Guidelines - Standard - PubMed", updated 13 Aug 2020 | 366,853 | 372,372 | **5,519** (1.5%) |
| "PubMed - Guidelines Filter - 2017" (MD Anderson Research Medical Library) | 191,266 | 197,821 | **6,555** (3.3%) |
| "Search Builder for Guidelines: Controlled Vocabulary, PubMed" (Carrie Price, updated 26 May 2022) | 69,436 | 92,862 | **23,426** (25.2%) |

All counts are single E-utilities `esearch` runs on 2026-11-12: the MD Anderson and Carrie Price
filters between about 02:50 and 03:40 UTC, the two CDA-AMC filters in a run that started at
05:20 UTC. They will change as PubMed grows.

How much a filter loses depends on what else it contains. The CDA-AMC Broad filter also searches
`consensus*[tiab]` and `"Consensus"[MESH]`, so most consensus statements still come in that way.
The 4,459 it misses are mostly position papers and statements whose title and abstract do not say
"consensus". The CDA-AMC Standard filter has no MeSH headings and searches title words rather
than abstracts, which is probably why it misses more.
The two-line builder has nothing to catch them, so a quarter of what it should find is gone.

The same MeSH year also renamed seven common subject headings, such as Depressive Disorder, Major
(now Major Depressive Disorder). Quoted old names of those also find nothing: see
[HEADINGS-2026.md](HEADINGS-2026.md).

## What PubMed does with the old names

| Query (2026-11-12) | Count | PubMed's reply |
|---|---|---|
| `"consensus statement"[pt]` | 30,251 | no warning |
| `"consensus development conference"[pt]` | 0 | quoted phrase not found (see [FINDINGS.md](FINDINGS.md)) |
| `"consensus development conference, NIH"[pt]` | 781 | no warning (a discontinued type; not renamed) |
| `"consensus statements as topic"[mh]` | 5,436 | no warning |
| `"consensus development conferences as topic"[mh]` (quoted) | 0 | quoted phrase not found |
| `consensus development conferences as topic[mh]` (not quoted) | 5,436 | mapped to "consensus statements as topic"[MeSH Terms] |

The MeSH record (D003245) still lists "Consensus Development Conferences as Topic" as an entry
term. PubMed maps an entry term to its heading only when the term is not in quotes. This is not
new to 2026: `"mental retardation"[mh]`, the old name of the heading now called Intellectual
Disability, also gives 0 when quoted. Published filters quote their headings, so every MeSH
rename can break them this way. The publication-type names do not map even unquoted.

## The filters, and how we ran them

**1. CDA-AMC "Guidelines - Broad - PubMed"** (last updated 2 April 2020). Our first run used the
strategy behind the PubMed "Launch" link on the
[ISSG Search Filters Resource guidelines page](https://sites.google.com/a/york.ac.uk/issg-search-filters-resource/home/guidelines).
For the second run, the strategy was copied from CDA-AMC's own page
(searchfilters.cda-amc.ca/link/75, which our fetcher cannot read) in a browser. Two of its terms
are renamed: `"Consensus development conferences as topic"[MESH]` and
`"consensus development conference"[pt]`. As a single URL, the strategy is too long for our
tools. We ran it in two parts through E-utilities search history (`usehistory=y`): part 1 is
every term outside the four `( ... AND ( ... ))` groups, and part 2 is part 1 ORed with those four
groups.

| Step | As written | Updated |
|---|---|---|
| part 1 (CDA-AMC page text) | 955,274 (warning lists both old names) | |
| whole filter (CDA-AMC page text) | 2,114,958 | 2,119,417 |
| whole filter (ISSG link, earlier the same day) | 2,114,812 | 2,119,271 |

Both versions miss the same 4,459 records. Through the publication type alone, the filter misses
3,540 records: `"consensus statement"[pt] NOT (every other term of the filter)`, again the same
number in both runs. The other 919 are records indexed with the renamed heading that no other
term catches. All of the ten most recent of the 3,540 are typed Consensus Statement. Six titles
call themselves position papers. The other four are a classification proposal from a society, a
numbered guidance document and two whose titles were cut off when we read them. Examples:

- PMID 42969776, "Classification of tracheal and crico-tracheal resection and anastomosis: a
  proposal from the European Laryngological Society" (*Acta Otorhinolaryngol Ital* 2026)
- PMID 42781907, "Walking for Chronic Pain: ... A Position Paper From the European Pain
  Federation" (*Eur J Pain* 2026)
- PMID 42744303, "Genetic testing and reporting: what the endocrinologists should know and can
  expect (joint position paper of the ENDO-ERN)" (*Eur J Endocrinol* 2026)
- PMID 42758313, national lung cancer screening in Austria: position paper of the Austrian
  Radiological Society (*Wien Klin Wochenschr* 2026)

The other six are PMIDs 42921172, 42880097, 42831711, 42799440, 42782533 and 42742688. All are
typed Consensus Statement in PubMed.

**2. CDA-AMC "Guidelines - Standard - PubMed"** (last updated 13 August 2020;
searchfilters.cda-amc.ca/link/77, copied in a browser). It searches four publication types plus
title, corporate-author and other-term words, and systematic reviews that mention guidelines. One
term is renamed: `"consensus development conference"[pt]`. Its
`"consensus development conference, NIH"[pt]` still works (781 records). PubMed also reports
`chemotreatment*` as not found in the `[ot]` part, because no other-term entry starts with it;
that changes nothing. We ran it in two parts through search history (the publication-type and
`[ti]`/`[cn]` terms, then the `[ot]` terms with the systematic-review group) and ORed them:

| Step | Count |
|---|---|
| as written | 366,853 |
| as written OR `"consensus statement"[pt]` | 372,372 |
| `"consensus statement"[pt]` NOT (as written) | **5,519** |

5,519 is exactly the difference between the first two rows. We read the 12 missed records with
the latest publication dates (PMIDs 42367168, 42549820, 42469146, 42334988, 41966983, 42600706,
42785804, 42880097, 42838857, 42710617, 42704015, 42695957). All 12 are typed Consensus Statement.
Five titles call themselves a position paper, two a statement and two an expert opinion. One is a
Delphi validation study, and two name only their topic (procalcitonin in paediatric emergency
care; the regulatory landscape of tuberculosis research platforms). Three titles were cut off when
we read them. Examples:

- PMID 42695957, "2026 HRS/PACES scientific statement on the use of antiarrhythmic drugs in
  understudied clinical scenarios" (*Heart Rhythm* 2026)
- PMID 42704015, "FIGO statement on emergency contraception" (*Int J Gynaecol Obstet* 2026)
- PMID 42367168, "European society of gynecology (ESG) position paper on the proposed terminology
  change from PCOS to PMOS" (*Gynecol Endocrinol* 2026)

The filter's title words do not catch these: "statement" is searched only as part of "position
statement*" and "policy statement*", and "position paper" not at all.

**3. "PubMed - Guidelines Filter - 2017"** ([MD Anderson Research Medical Library](https://mdanderson.libguides.com/ld.php?content_id=34393248),
read 2026-11-12). It has 17 terms joined by OR, including
`"Consensus Development Conference" [Publication Type]`. We ran the 17 terms as one flat OR
list. The original nests them in parentheses and writes two of the ORs in lower case; for a
filter that only uses OR, flattening it does not change the set of records it returns. Updated:
`"Consensus Statement" [Publication Type]`.

**4. "Search Builder for Guidelines: Controlled Vocabulary, PubMed"** ([Carrie Price's search
filter guide](https://carrieprice78.github.io/guides/search-filters/methodological-filters/),
updated 26 May 2022), run exactly as written:
`"guideline"[pt] OR "practice guideline"[pt] OR "consensus"[mesh] OR "consensus development
conference, nih"[mesh] OR "consensus development conference"[pt] OR "delphi technique"[mesh]`.
PubMed warns about two of these terms. `"consensus development conference"[pt]` is the renamed
type. `"consensus development conference, nih"[mesh]` names a publication type with a MeSH tag.
We could not tell whether it ever matched, so we did not change it. The updated run replaces only
the renamed type with `"consensus statement"[pt]`.

We also queried the missed set directly:
`"consensus statement"[pt] NOT ("guideline"[pt] OR "practice guideline"[pt] OR "consensus"[mesh]
OR "delphi technique"[mesh])`. It returns exactly 23,426 records, and 9,736 of them were
published in 2020-2026. The 12 most recent (PMIDs 42927910, 42762875, 43006798, 42647144,
42367168, 42810452, 42771181, 42734653, 42720753, 42704670, 42681552, 42549820) are all typed
Consensus Statement. Eight titles call themselves a consensus, a recommendation, guidance or a
position paper or statement. Three titles were cut off when we read them. One (PMID 42762875,
on refining the Young Mania Rating Scale) names only its topic. Examples: international
consensus guidance on screening for islet autoantibodies (*Diabetologia* 2026), an international
position statement on inpatient continuous glucose monitoring (*Diabetologia* 2026), and a
Swedish consensus recommendation for follow-up after an ICU stay (*Acta Anaesthesiol Scand*
2027).

**Not measured.** The University of Pittsburgh HSLS PubMed practice-guidelines filter (listed by
ISSG, dated 9 September 2024) was not public on 2026-11-12. Its page
(hsls.libguides.com/PubMed-search-filters/practice-guidelines) shows "The requested page is not
currently available due to visibility settings", so we have not read it. The UIC and Ohio
University evidence-based-medicine guides list `Consensus Development Conference [pt]` in a
"Questions of Harm" term table (pages updated 22 Oct 2026 and 23 Sep 2026). These are lists of
terms to add, not a single search string, so there is nothing to count. Ovid MEDLINE filters
(`.pt.`, `/`) run on a different system, and we cannot test them.

## How to fix a filter

Replace, or OR in, the new names:

- `"Consensus Development Conference"[pt]` -> `"Consensus Statement"[pt]`
- `"Consensus Development Conferences as Topic"[mh]` -> `"Consensus Statements as Topic"[mh]`
  (or leave the old name unquoted)
- the other two renamed publication types: `Congress` -> `"Conference Proceedings"[pt]`;
  `"Retraction of Publication"` -> `"Retraction Notice"[pt]` (see [FINDINGS.md](FINDINGS.md))
- renamed subject headings, such as `"Depressive Disorder, Major"[mh]` ->
  `"Major Depressive Disorder"[mh]` (see [HEADINGS-2026.md](HEADINGS-2026.md))

`pubmed_pt_check.py` (0.1.2) flags all of these, and `--fix` rewrites them. With `--live`, it
also asks PubMed about every publication type and every quoted MeSH heading in a strategy, so it
catches renames it does not know about:

```
python pubmed_pt_check.py --live my_guideline_filter.txt
```

## Prior art

On 2026-11-12 we searched for reports of search filters affected by the MeSH 2026 renames. We
found NLM's bulletins (Tech Bull 2026 Jan-Feb;(468):e6 and Mar-Apr;(469):e1), the MeSH records,
and the ISSG resource's general advice to check older filters for changes in subject indexing.
We found no measurement of what the renames do to a published filter, and no updated version of
these four filters. If one exists, tell us and we will link it.

## Limits

- Each count is from a single run. "Missed now" counts records that the filter would return
  with the new names and does not return as written. It is not a count of guidelines missed by
  any particular review: a topic search combined with the filter would miss far fewer records.
- We hand-checked 34 of the missed records: the most recent 10 from the CDA-AMC Broad filter, the
  12 with the latest publication dates from the CDA-AMC Standard filter and the most recent 12
  from the Carrie Price builder. We read titles and publication types only. All 34 are typed
  Consensus Statement. These are the newest records, not a random sample, and we did not judge
  relevance across the whole set.
- The CDA-AMC strategies were copied from CDA-AMC's own pages in a browser. Its page for the
  Broad filter gives the same missed count as ISSG's link to it.
- We did not check whether any of these filters has an updated version elsewhere.

MV2, Munim, Inc., mv2@munimtech.com
