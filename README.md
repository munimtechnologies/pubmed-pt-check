# pubmed-pt-check

Finds PubMed publication types and quoted MeSH headings in your searches that PubMed no longer
recognizes.

NLM renames MeSH headings every year. From 2020 to 2026 it changed 242 subject and geographic
headings that PubMed no longer finds under the old name. Among them: "Pregnant Women" (now
"Pregnant People"), "Disabled Persons" (now "Persons with Disabilities"), "Tobacco" (now
"Nicotiana"), "Depressive Disorder, Major" (now "Major Depressive Disorder"), "African Americans"
(now "Black or African American"), "Glycated Hemoglobin A" (now "Glycated Hemoglobin"),
"Clostridium difficile" (now "Clostridioides difficile"), "Infection" (now "Infections") and
"Neural Networks (Computer)" (now "Neural Networks, Computer"). It deleted 14 headings, 7 of them
pointed to a replacement (for example Cervical Intraepithelial Neoplasia, now Uterine Cervical
Dysplasia). It renamed eight publication types that PubMed citations carry: "Retraction of
Publication" is now "Retraction Notice" (MeSH 2025); "Congress", "Consensus Development
Conference" and "Classical Article" are now "Conference Proceedings", "Consensus Statement" and
"Seminal Article" (MeSH 2026); "Evaluation Studies", "Validation Studies", "Government Document"
and "Webcasts" lost their plural in 2020. **In a search, a quoted old name now matches nothing,
and PubMed does not stop the search.** We checked every one of them with E-utilities on
2026-11-11 and 2026-11-12:

- `"Retraction of Publication"[pt]` gives 0 records, so any AND clause that uses it gives 0;
- `NOT "Retraction of Publication"[pt]` excludes nothing, so retraction notices stay in your
  results;
- `"Retraction of Publication"[pt] OR "Retracted Publication"[pt]` returns only the retracted
  papers and drops every notice, with no error;
- a published 2026 scoping-review protocol's exclusion set, re-run as printed, no longer excludes
  88,965 PubMed records because three of its 55 terms are the old names;
- four published PubMed guideline search filters now miss 4,459, 5,519, 6,555 and 23,426
  records (0.2% to 25.2% of what they would find with the new names), mostly consensus
  statements and society position papers;
- every quoted old heading name gives 0. `"Disabled Persons"[Mesh] OR disab*[tiab]` misses the
  40,077 records under the new heading that `disab*[tiab]` does not find, and
  `"Neural Networks (Computer)"[Mesh] OR neural network*[tiab]` misses 47,530. A published 2025
  search that used the disability line found 153 records instead of 159. Three other published
  searches lost nothing, because other terms in the same block covered the heading.
- Punctuation can matter: 29 headings that NLM only changed from "Name (X)" to "Name, X" in 2020
  give 0 under the old form.

Evidence, exact queries and counts: [FINDINGS.md](FINDINGS.md) (publication types, the protocol),
[FILTERS.md](FILTERS.md) (guideline filters), [MESH-RENAMES.md](MESH-RENAMES.md) (every heading
rename 2024-2026, three published searches re-run),
[MESH-RENAMES-2020-2023.md](MESH-RENAMES-2020-2023.md) (2020-2023, punctuation, restored names,
deletions) and [HEADINGS-2026.md](HEADINGS-2026.md) (the first eight 2026 headings). MeSH 2027:
[PREREG-MESH-2027.md](PREREG-MESH-2027.md).

## Use

Python 3.8+, standard library only. No install, no API key.

```
python pubmed_pt_check.py '"Cochrane Database Syst Rev"[ta] NOT "Retraction of Publication"[pt]'
python pubmed_pt_check.py my_search_strategy.txt scripts/*.py
python pubmed_pt_check.py --live my_search_strategy.txt      # ask PubMed about every [pt] and quoted [mh] term
python pubmed_pt_check.py --fix '("Pregnant Women"[Mesh] OR pregnan*[tiab])'
```

Example output:

```
<query>: "Retraction of Publication"[pt] -> renamed to "Retraction Notice" (MeSH 2025). Joined by NOT.
    PubMed drops this term, so this NOT excludes nothing; records typed "Retraction Notice" stay in the results.
    NLM's own Retraction filter now runs 'hasretractionof OR retraction notice[pt]'.
checked 1 publication-type term(s) and 0 MeSH term(s): 1 renamed, deleted or unrecognized, 0 discontinued.
```

- Reads query strings, files (search strategies, R/Python/SQL code, notes) or `-` for stdin. In
  files it also reads escaped quotes (`\"...\"[pt]`) and URL-encoded PubMed links
  (`%22...%22%5Bpt%5D`).
- Knows the tags `[pt]`, `[ptyp]` and `[Publication Type]`, and (since 0.1.1) `[mh]`, `[mesh]`,
  `[majr]`, `[MeSH Terms]` and `[MeSH Major Topic]`, each with or without `:noexp`.
- Flags the 8 renamed publication types, 249 MeSH name changes from 2020 to 2026 (renamed
  headings, plus deleted headings that PubMed maps to a replacement, reported as "replaced by")
  and the 6 headings deleted for 2026 with no replacement (exit code 1). It lists the 17
  discontinued publication types as information; they still match older citations. An unquoted
  old heading name is reported but not flagged, because PubMed maps it to the new heading. A
  deleted heading with no replacement is flagged quoted or not.
- `--live` runs one `esearch` per distinct publication type and per distinct quoted MeSH heading,
  and reports any that PubMed does not recognize today, including renames this script does not
  know about yet (for example MeSH 2027, once PubMed switches). It makes about 2-3 requests a
  second, read-only.
- `--fix` prints the input with renamed names replaced by the current ones. Deleted headings with
  no replacement are left for you to replace.
- `--json` gives machine-readable output (with the MeSH year of each change); `--all` also lists
  current terms.

Exit codes: 0 = nothing renamed, deleted or unrecognized; 1 = at least one; 2 = bad input or a
failed `--live` lookup.

## Limits

It checks one line at a time and finds the Boolean operator next to each term, not the full query
tree. It does not detect implicit AND between bare words, and it does not follow set numbers
such as `NOT #4`. Always read PubMed's own translation (Search Details, or `querytranslation` in
E-utilities). Its offline table covers MeSH 2020 to 2026, found by comparing NLM's yearly MeSH
RDF; for older renames use `--live`. It is written for PubMed syntax; Ovid and other platforms
treat old headings their own way. The counts in the .md files are from single runs on one or two
days.

Corrections (2026-11-12): the first README said all three publication-type renames were MeSH
2025. Only the Retraction Notice rename is; the other two are MeSH 2026. Version 0.1.1 also fixes
the same error in the script's description. MESH-RENAMES.md said PubMed ignores punctuation; it
does not when "(X)" becomes ", X" (see MESH-RENAMES-2020-2023.md).

## Changes

- 0.1.4 (2026-11-12): MeSH 2020 (87), 2021 (11), 2022 (23) and 2023 (32) heading renames; 7
  deleted headings that PubMed maps to a replacement (2020, 2023, 2024; reported as "replaced
  by"); the publication types Evaluation Studies, Validation Studies, Government Document and
  Webcasts (MeSH 2020).
- 0.1.3 (2026-11-12): every MeSH heading renamed for 2024 (21), 2025 (30) and 2026 (38); the 6
  headings deleted for 2026 (new status `deleted`); the publication type Classical Article (now
  Seminal Article, MeSH 2026).
- 0.1.2 (2026-11-12): seven more MeSH 2026 heading renames (Depressive Disorder, Major; Pain,
  Postoperative; Carcinoma, Basal Cell; Conscious Sedation; Pain, Intractable; Receptors, Kainic
  Acid; Surgical Procedures, Colorectal).
- 0.1.1 (2026-11-12): MeSH headings ([mh], [mesh], [majr], :noexp); Consensus Statements as Topic.
- 0.1.0 (2026-11-11): publication types.

## For coding agents

[SKILL.md](SKILL.md) tells an agent when and how to run the checker.

## Licence and disclosure

Code: Apache-2.0 (see LICENSE). FINDINGS.md, FILTERS.md, HEADINGS-2026.md, MESH-RENAMES.md and
MESH-RENAMES-2020-2023.md text: CC BY 4.0. Made with AI agents working in the name of MV2, Munim,
Inc. (mv2@munimtech.com). Not affiliated with or endorsed by NLM or NCBI. Issues and corrections
welcome.
