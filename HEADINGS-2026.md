# Seven common MeSH headings renamed for 2026: quoted old names now find nothing in PubMed (checked 2026-11-12)

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human has
reviewed it. Text CC BY 4.0; code Apache-2.0.

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

`pubmed_pt_check.py` 0.1.2 knows all eight heading renames above and the three publication-type
renames. `--fix` rewrites them, and `--live` asks PubMed about every quoted heading and
publication type in a strategy, so it also catches the 2026 renames we have not listed:

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
term mapping. We did not find anyone pointing out that quoted 2025 names of these headings now
return nothing, or measuring the loss. If such a report exists, tell us and we will link it.

## Limits

- All counts come from single runs on one day and will change as PubMed grows.
- We checked only the 8 heading renames NLM lists on the Classification page, not all 42 changed
  descriptors. `--live` covers the rest one strategy at a time.
- We did not test PubMed's web interface, My NCBI saved searches or email alerts directly. We
  queried E-utilities, which uses the same search engine. We don't know whether NLM converted
  saved searches when it renamed the headings.
- The "how much a strategy loses" numbers use simple one-word text searches. A real strategy with
  many synonyms will lose less.

MV2, Munim, Inc., mv2@munimtech.com
