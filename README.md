# pubmed-pt-check

Finds PubMed publication types and quoted MeSH headings in your searches that PubMed no longer
recognizes.

NLM renamed three publication types: "Retraction of Publication" is now "Retraction Notice"
(MeSH 2025), "Congress" is now "Conference Proceedings" and "Consensus Development Conference" is
now "Consensus Statement" (both MeSH 2026); PubMed's filters were updated in March 2026. MeSH 2026
also renamed the heading "Consensus Development Conferences as Topic" to "Consensus Statements as
Topic". **In a search, a quoted old name now matches nothing, and PubMed does not stop the
search.** We checked with E-utilities on 2026-11-11 and 2026-11-12:

- `"Retraction of Publication"[pt]` gives 0 records, so any AND clause that uses it gives 0;
- `NOT "Retraction of Publication"[pt]` excludes nothing, so retraction notices stay in your
  results;
- `"Retraction of Publication"[pt] OR "Retracted Publication"[pt]` returns only the retracted
  papers and drops every notice, with no error;
- a published 2026 scoping-review protocol's exclusion set, re-run as printed, no longer excludes
  88,965 PubMed records because three of its 55 terms are the old names;
- three published PubMed guideline search filters now miss 4,459, 6,555 and 23,426 records
  (0.2%, 3.3% and 25.2% of what they would find with the new names), mostly consensus statements
  and society position papers.

Evidence, exact queries and counts: [FINDINGS.md](FINDINGS.md) (publication types, the protocol)
and [FILTERS.md](FILTERS.md) (guideline filters, MeSH headings).

## Use

Python 3.8+, standard library only. No install, no API key.

```
python pubmed_pt_check.py '"Cochrane Database Syst Rev"[ta] NOT "Retraction of Publication"[pt]'
python pubmed_pt_check.py my_search_strategy.txt scripts/*.py
python pubmed_pt_check.py --live my_search_strategy.txt      # ask PubMed about every [pt] and quoted [mh] term
python pubmed_pt_check.py --fix '("Retraction of Publication"[pt] OR "Retracted Publication"[pt])'
```

Example output:

```
<query>: "Retraction of Publication"[pt] -> renamed to "Retraction Notice" (MeSH 2025). Joined by NOT.
    PubMed drops this term, so this NOT excludes nothing; records typed "Retraction Notice" stay in the results.
    NLM's own Retraction filter now runs 'hasretractionof OR retraction notice[pt]'.
checked 1 publication-type term(s) and 0 MeSH term(s): 1 renamed or unrecognized, 0 discontinued.
```

- Reads query strings, files (search strategies, R/Python/SQL code, notes) or `-` for stdin. In
  files it also reads escaped quotes (`\"...\"[pt]`) and URL-encoded PubMed links
  (`%22...%22%5Bpt%5D`).
- Knows the tags `[pt]`, `[ptyp]` and `[Publication Type]`, and (since 0.1.1) `[mh]`, `[mesh]`,
  `[majr]`, `[MeSH Terms]` and `[MeSH Major Topic]`, each with or without `:noexp`.
- Flags the 3 renamed publication types and the renamed MeSH heading (exit code 1), and lists the
  17 discontinued publication types as information. Discontinued types still match older
  citations only. An unquoted old MeSH heading name is reported but not flagged, because PubMed
  maps it to the new heading.
- `--live` runs one `esearch` per distinct publication type and per distinct quoted MeSH heading,
  and reports any that PubMed does not recognize today, including renames this script does not
  know about yet. It makes about 2-3 requests a second, read-only.
- `--fix` prints the input with renamed names replaced by the new ones.
- `--json` gives machine-readable output (with the MeSH year of each rename); `--all` also lists
  current terms.

Exit codes: 0 = nothing renamed or unrecognized; 1 = at least one; 2 = bad input or a failed
`--live` lookup.

## Limits

It checks one line at a time and finds the Boolean operator next to each term, not the full query
tree. It does not detect implicit AND between bare words, and it does not follow set numbers
such as `NOT #4`. Always read PubMed's own translation (Search Details, or `querytranslation` in
E-utilities). Its offline table holds only renames we checked by hand (one MeSH heading so far);
use `--live` to catch other renamed headings. The counts in FINDINGS.md and FILTERS.md are from
single runs on one or two days.

Correction (2026-11-12): the first README said all three publication-type renames were MeSH 2025.
Only the Retraction Notice rename is; the other two are MeSH 2026. Version 0.1.1 also fixes the
same error in the script's description.

## For coding agents

[SKILL.md](SKILL.md) tells an agent when and how to run the checker.

## Licence and disclosure

Code: Apache-2.0 (see LICENSE). FINDINGS.md and FILTERS.md text: CC BY 4.0. Made with AI agents
working in the name of MV2, Munim, Inc. (mv2@munimtech.com). Not affiliated with or endorsed by
NLM or NCBI. Issues and corrections welcome.
