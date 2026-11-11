# pubmed-pt-check

Finds PubMed publication types in your searches that PubMed no longer recognizes.

NLM renamed three publication types (MeSH 2025; PubMed filters updated March 2026): "Retraction
of Publication" is now "Retraction Notice", "Congress" is now "Conference Proceedings", and
"Consensus Development Conference" is now "Consensus Statement". **In a `[pt]` search, the old
names now match nothing, and PubMed does not stop the search.** We checked with E-utilities on
2026-11-11:

- `"Retraction of Publication"[pt]` gives 0 records, so any AND clause that uses it gives 0;
- `NOT "Retraction of Publication"[pt]` excludes nothing, so retraction notices stay in your
  results;
- `"Retraction of Publication"[pt] OR "Retracted Publication"[pt]` returns only the retracted
  papers and drops every notice, with no error.

Evidence, exact queries and counts: [FINDINGS.md](FINDINGS.md).

## Use

Python 3.8+, standard library only. No install, no API key.

```
python pubmed_pt_check.py '"Cochrane Database Syst Rev"[ta] NOT "Retraction of Publication"[pt]'
python pubmed_pt_check.py my_search_strategy.txt scripts/*.py
python pubmed_pt_check.py --live my_search_strategy.txt      # ask PubMed about every [pt] term
python pubmed_pt_check.py --fix '("Retraction of Publication"[pt] OR "Retracted Publication"[pt])'
```

Example output:

```
<query>: "Retraction of Publication"[pt] -> renamed to "Retraction Notice". Joined by NOT.
    PubMed drops this term, so this NOT excludes nothing; records typed "Retraction Notice" stay in the results.
    NLM's own Retraction filter now runs 'hasretractionof OR retraction notice[pt]'.
checked 1 publication-type term(s): 1 renamed or unrecognized, 0 discontinued.
```

- Reads query strings, files (search strategies, R/Python/SQL code, notes) or `-` for stdin. In
  files it also reads escaped quotes (`\"...\"[pt]`) and URL-encoded PubMed links
  (`%22...%22%5Bpt%5D`).
- Knows the tags `[pt]`, `[ptyp]` and `[Publication Type]`, quoted or unquoted.
- Flags the 3 renamed types (exit code 1) and lists the 17 discontinued ones as information.
  Discontinued types still match older citations only.
- `--live` runs one `esearch` per distinct type and reports any type PubMed does not recognize
  today, including renames this script does not know about yet. It makes about 2-3 requests a
  second, read-only.
- `--fix` prints the input with renamed types replaced by the new names.
- `--json` gives machine-readable output; `--all` also lists current types.

Exit codes: 0 = nothing renamed or unrecognized; 1 = at least one; 2 = bad input or a failed
`--live` lookup.

## Limits

It checks one line at a time and finds the Boolean operator next to each term, not the full query
tree. It does not detect implicit AND between bare words. Always read PubMed's own translation
(Search Details, or `querytranslation` in E-utilities). It checks publication types only, not
MeSH headings. The counts in FINDINGS.md are from one day.

## For coding agents

[SKILL.md](SKILL.md) tells an agent when and how to run the checker.

## Licence and disclosure

Code: Apache-2.0 (see LICENSE). FINDINGS.md text: CC BY 4.0. Made with AI agents working in the
name of MV2, Munim, Inc. (mv2@munimtech.com). Not affiliated with or endorsed by NLM or NCBI.
Issues and corrections welcome.
