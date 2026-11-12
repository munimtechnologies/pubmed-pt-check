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
We re-ran three published PubMed guideline filters exactly as written, then again with only the
renamed terms updated. Each one now silently misses records. In our hand checks, the missed
records are typed Consensus Statement and are mostly society position papers and consensus
recommendations, the documents a guidelines filter is built to find.

| Filter (as published) | As written | Renamed terms updated | Missed now |
|---|---|---|---|
| CDA-AMC (formerly CADTH) "Guidelines - Broad - PubMed", updated 2 Apr 2020 | 2,114,812 | 2,119,271 | **4,459** (0.2%) |
| "PubMed - Guidelines Filter - 2017" (MD Anderson Research Medical Library) | 191,266 | 197,821 | **6,555** (3.3%) |
| "Search Builder for Guidelines: Controlled Vocabulary, PubMed" (Carrie Price, updated 26 May 2022) | 69,436 | 92,862 | **23,426** (25.2%) |

All counts are single E-utilities `esearch` runs on 2026-11-12, between about 02:50 and 03:40
UTC. They will change as PubMed grows.

How much a filter loses depends on what else it contains. The CDA-AMC filter also searches
`consensus*[tiab]` and `"Consensus"[MESH]`, so most consensus statements still come in that way.
The 4,459 it misses are mostly position papers and statements whose title and abstract do not say
"consensus". The two-line builder has nothing to catch them, so a quarter of what it should find
is gone.

## What PubMed does with the old names

| Query (2026-11-12) | Count | PubMed's reply |
|---|---|---|
| `"consensus statement"[pt]` | 30,251 | no warning |
| `"consensus development conference"[pt]` | 0 | quoted phrase not found (see [FINDINGS.md](FINDINGS.md)) |
| `"consensus statements as topic"[mh]` | 5,436 | no warning |
| `"consensus development conferences as topic"[mh]` (quoted) | 0 | quoted phrase not found |
| `consensus development conferences as topic[mh]` (not quoted) | 5,436 | mapped to "consensus statements as topic"[MeSH Terms] |

The MeSH record (D003245) still lists "Consensus Development Conferences as Topic" as an entry
term. PubMed maps an entry term to its heading only when the term is not in quotes. This is not
new to 2026: `"mental retardation"[mh]`, the old name of the heading now called Intellectual
Disability, also gives 0 when quoted. Published filters quote their headings, so every MeSH
rename can break them this way. The publication-type names do not map even unquoted.

## The filters, and how we ran them

**1. CDA-AMC "Guidelines - Broad - PubMed"** (last updated 2 April 2020). The CDA-AMC search
filters site refused our fetcher (HTTP 403), so we read the strategy from the PubMed "Launch" link
on the [ISSG Search Filters Resource guidelines page](https://sites.google.com/a/york.ac.uk/issg-search-filters-resource/home/guidelines)
(read 2026-11-12). It has 73 terms. Two are renamed: `"Consensus development conferences as
topic"[MESH]` and `"consensus development conference"[pt]`. As a single URL, the strategy is too
long for our tools. We ran it in two parts through E-utilities search history (`usehistory=y`):
part 1 is every term outside the four `( ... AND ( ... ))` groups, and part 2 is part 1 ORed with
those four groups.

| Step | As written | Updated |
|---|---|---|
| part 1 | 955,234 (warning lists both old names) | 960,008 (no warning) |
| part 1 OR the four AND groups (the whole filter) | 2,114,812 | 2,119,271 |

Through the publication type alone, the filter misses 3,540 records:
`"consensus statement"[pt] NOT (every other term of the filter)`. The other 919 are records
indexed with the renamed heading that no other term catches. All of the ten most recent of the
3,540 are typed Consensus Statement. Six titles call themselves position papers. The other four
are a classification proposal from a society, a numbered guidance document and two whose titles
were cut off when we read them. Examples:

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

**2. "PubMed - Guidelines Filter - 2017"** ([MD Anderson Research Medical Library](https://mdanderson.libguides.com/ld.php?content_id=34393248),
read 2026-11-12). It has 17 terms joined by OR, including
`"Consensus Development Conference" [Publication Type]`. We ran the 17 terms as one flat OR
list. The original nests them in parentheses and writes two of the ORs in lower case; for a
filter that only uses OR, flattening it does not change the set of records it returns. Updated:
`"Consensus Statement" [Publication Type]`.

**3. "Search Builder for Guidelines: Controlled Vocabulary, PubMed"** ([Carrie Price's search
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
consensus guidance
on screening for islet autoantibodies (*Diabetologia* 2026), an international position statement
on inpatient continuous glucose monitoring (*Diabetologia* 2026), and a Swedish consensus
recommendation for follow-up after an ICU stay (*Acta Anaesthesiol Scand* 2027).

**Not measured.** The CDA-AMC "Guidelines - Standard - PubMed" filter and the University of
Pittsburgh HSLS PubMed practice-guidelines filter (9 Sep 2024) are both listed by ISSG, but their
pages refused our fetcher, so we have not read them and do not report on them. The UIC and Ohio
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

`pubmed_pt_check.py` 0.1.1 flags all of these, and `--fix` rewrites them. With `--live`, it also
asks PubMed about every publication type and every quoted MeSH heading in a strategy, so it
catches renames it does not know about:

```
python pubmed_pt_check.py --live my_guideline_filter.txt
```

## Prior art

On 2026-11-12 we searched for reports of search filters affected by the MeSH 2026 renames. We
found NLM's bulletins (Tech Bull 2026 Jan-Feb;(468):e6 and Mar-Apr;(469):e1), the MeSH records,
and the ISSG resource's general advice to check older filters for changes in subject indexing.
We found no measurement of what the renames do to a published filter, and no updated version of
these three filters. If one exists, tell us and we will link it.

## Limits

- Each count is from a single run. "Missed now" counts records that the filter would return
  with the new names and does not return as written. It is not a count of guidelines missed by
  any particular review: a topic search combined with the filter would miss far fewer records.
- We hand-checked 22 of the missed records: the most recent 10 from filter 1 and the most
  recent 12 from filter 3. We read titles and publication types only. All 22 are typed
  Consensus Statement, and 14 titles say outright that they are a consensus, guidance,
  recommendation or position document. The most recent records are not a random sample, and we
  did not judge relevance across the whole set.
- We read the CDA-AMC strategy as ISSG's link to it; CDA-AMC's own page may differ.
- We did not check whether any of these filters has an updated version elsewhere.

MV2, Munim, Inc., mv2@munimtech.com
