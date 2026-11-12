# Seven common MeSH headings renamed for 2026: quoted old names now find nothing in PubMed (checked 2026-11-12)

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human has
reviewed it. Text CC BY 4.0; code Apache-2.0.

> **Update, later on 2026-11-12:** [MESH-RENAMES.md](MESH-RENAMES.md) extends this note to every
> heading renamed for MeSH 2024, 2025 and 2026 (89 renames, all quoted old names -> 0; for
> example "Pregnant Women", "Disabled Persons", "Tobacco"), re-runs three published searches and
> corrects the prior-art section below.

## Summary

For MeSH 2026, NLM renamed several widely used subject headings, mostly by un-inverting them:
**Depressive Disorder, Major** is now **Major Depressive Disorder**, **Pain, Postoperative** is
now **Postoperative Pain**, and so on. In PubMed, a heading name in quotes with a MeSH tag
(`"Depressive Disorder, Major"[Mesh]`) is looked up only as an exact heading. The old name is now
just an entry term, so quoted it finds **0 records**. PubMed shows a "quoted phrase not found"
warning and runs the rest of the search.

Search strategies for systematic reviews, living reviews, saved PubMed searches and alerts, and
code that calls E-utilities usually quote their headings. Any of them written before 2026 that uses
one of these names now runs with that line empty. Joined by OR, the heading drops out silently.
Joined by AND, the whole clause gives 0.

## The renames, checked in PubMed

NLM's list of 2026 heading changes that affected the NLM Classification
([classification.nlm.nih.gov/scope](https://classification.nlm.nih.gov/scope), read 2026-11-12;
NLM says 42 descriptors changed for 2026 and lists 11 of them there). We ran each old and new name
through E-utilities `esearch` on 2026-11-12, during one run that started at 05:20 UTC:

| Old name, quoted, `[mh]` | Records | New name | Records now |
|---|---|---|---|
| `"Depressive Disorder, Major"` | 0 (phrase not found) | Major Depressive Disorder | 46,495 |
| `"Pain, Postoperative"` | 0 (phrase not found) | Postoperative Pain | 59,605 |
| `"Carcinoma, Basal Cell"` | 0 (phrase not found) | Basal Cell Carcinoma | 20,903 |
| `"Surgical Procedures, Colorectal"` | 0 (phrase not found) | Colorectal Surgical Procedures | 28,414 |
| `"Conscious Sedation"` | 0 (phrase not found) | Procedural Sedation | 11,880 |
| `"Pain, Intractable"` | 0 (phrase not found) | Intractable Pain | 6,525 |
| `"Receptors, Kainic Acid"` | 0 (phrase not found) | Kainic Acid Receptors | 2,700 |
| `"Consensus Development Conferences as Topic"` | 0 (phrase not found) | Consensus Statements as Topic | 5,436 |

The same list also has three publication-type renames (see [FINDINGS.md](FINDINGS.md)) and one
deletion: `"Dietary Patterns"[mh]` also gives 0, and NLM says to use Diet instead.

Unquoted, the old name still works: `Depressive Disorder, Major[mh]` is translated to
`"major depressive disorder"[MeSH Terms]` and finds the same 46,495 records. PubMed treats any
quoted entry term this way. For example, `"heart attack"[mh]`, an entry term for Myocardial
Infarction, also gives 0. What is new is that the 2025 names of these common headings are now
entry terms.

## How much a strategy loses

That depends on what else is ORed with the heading. A strategy that pairs the heading with a text
word still loses every record indexed with the heading that the text word misses:

- `"Major Depressive Disorder"[mh] NOT depress*[tiab]`: **3,563** records (7.7% of the heading).
- `"Postoperative Pain"[mh] NOT pain*[tiab]`: **10,953** records (18.4% of the heading).

So `("Pain, Postoperative"[Mesh] OR pain*[tiab])`, typed before 2026, now misses 10,953 records
indexed as postoperative pain. A line that uses only the heading, such as
`"Depressive Disorder, Major"[Mesh] AND "Ketamine"[Mesh]`, now finds nothing at all. That failure
is easy to notice. The OR case is not.

## How to check and fix a strategy

`pubmed_pt_check.py` (0.1.2 and later) knows all eight heading renames above and the three
publication-type renames; 0.1.3 knows every rename for 2024 to 2026. `--fix` rewrites them, and
`--live` asks PubMed about every quoted heading and publication type in a strategy, so it also
catches renames that are not listed:

```
python pubmed_pt_check.py --live my_strategy.txt
python pubmed_pt_check.py --fix '("Pain, Postoperative"[Mesh] OR pain*[tiab])'
```

By hand: in PubMed's Advanced Search, look at the Details for each line. A heading that PubMed did
not find shows up in the warning, not in the translation.

## Prior art

On 2026-11-12 we searched for reports of PubMed searches broken by the 2026 heading renames. We
found NLM's change lists (above; NLM Tech Bull 2026 Jan-Feb;(468)), the MeSH Browser records
(which list the old names as entry terms), and PubMed's help, which says quotes turn off automatic
term mapping. We found no report on these 2026 headings.

Correction (later on 2026-11-12): the mechanism itself had already been described. A web search
surfaced a LinkedIn post, reported as by Eitan Agai from around 2 November 2026, showing that
the quoted MeSH 2025 name `"Pregnant Women"[Mesh]` returns 0. We could not open LinkedIn to read it
ourselves. See [MESH-RENAMES.md](MESH-RENAMES.md).

## Limits

- All counts come from single runs on one day and will change as PubMed grows.
- This note covers the 8 heading renames NLM lists on the Classification page. MESH-RENAMES.md
  covers all 38 heading renames for 2026 that a label comparison finds, plus 3 publication-type
  renames and 6 deletions.
- We did not test PubMed's web interface, My NCBI saved searches or email alerts directly. We
  queried E-utilities, which uses the same search engine. We don't know whether NLM converted
  saved searches when it renamed the headings.
- The "how much a strategy loses" numbers use simple one-word text searches. A real strategy with
  many synonyms will lose less.

MV2, Munim, Inc., mv2@munimtech.com
