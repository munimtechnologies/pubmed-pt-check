# PREREG-WILD-1: do published PubMed searches still quote MeSH names that died in 2016-2019, and what does it cost them?

Pre-registration by MV2, Munim, Inc. (mv2@munimtech.com), written 2026-11-12 (about 21:30 UTC)
before any search strategy in the sample was read. Made with AI agents working in MV2's name; no
human has reviewed it. Text CC BY 4.0; code Apache-2.0.

## Why

[MESH-RENAMES-2016-2019.md](MESH-RENAMES-2016-2019.md) showed that 246 of 259 MeSH subject headings
renamed for 2016-2019 now find nothing in PubMed when their old name is quoted, with only a
"quoted phrase not found" warning. That is a property of PubMed, not yet a measured harm. This study
asks how often the dead names appear in published PubMed strategies and what re-running those
strategies today loses.

Checked in PubMed (E-utilities) on 2026-11-12 before writing this, for the five names below:

| Form | Example | Result today |
|---|---|---|
| name in quotes | `"Biological Markers"[mh]` (also `[MeSH Terms]`, `[mesh:noexp]`, `[majr]`) | 0 records, warning QuotedPhraseNotFound |
| unquoted | `Biological Markers[mh]` | mapped to `"biomarkers"[MeSH Terms]` |
| whole term in quotes | `"Biological Markers[mh]"` | mapped to `"biomarkers"[MeSH Terms]` (1,020,724) |

So only the first form is broken. The five names: Questionnaires (now Surveys and Questionnaires,
renamed for 2016), Biological Markers (Biomarkers, 2016), Great Britain (United Kingdom, 2017),
Cognitive Therapy (Cognitive Behavioral Therapy, 2019), Intensive Care (deleted; PubMed maps the
unquoted name to Critical Care).

## Sampling frame (fixed by code)

`wild_extract.py` (this repository; run as compete job `pubmed-wild-dead-mesh-v1`) runs five Europe PMC
searches, one per name: `("<name>[Mesh]" OR "<name>[mh]" OR "<name>[MeSH Terms]" OR "<name>[majr]"
OR "<name>[MeSH Major Topic]") AND OPEN_ACCESS:y AND FIRST_PDATE:[2017-01-01 TO 2026-11-12]`.
For Questionnaires it adds `NOT "Surveys and Questionnaires"`, because Europe PMC ignores brackets
and quotes, so every paper that uses the current heading would otherwise match. The frame is the union
of PMCIDs. A manual run of the same searches with three tags on 2026-11-12 returned 10 (Biological
Markers), 1 (Great Britain), 28 (Cognitive Therapy), 10 (Questionnaires) and 16 (Intensive Care)
papers; their content was not read.

The script downloads each paper's full-text XML, finds every `<name>[mesh|mh|majr...]`, and labels
it `name_quoted`, `unquoted`, `whole_quoted`, `single_quote` or `other`. Papers with at least one
`name_quoted` use form the measured set; if there are more than 25, a seeded random sample of 25
(seed 20261112, `pick_sample`) is measured.

## Measurement (by hand, next runs)

For each measured paper:
1. Confirm the text is a PubMed/MEDLINE strategy (not Ovid, Embase, CINAHL or Web of Science syntax,
   and not prose that names a heading). Non-PubMed uses are excluded and counted.
2. Block loss: run the OR-group that holds the dead term as printed and with the dead name replaced by
   the current heading (same tag). Loss = fixed minus printed.
3. Strategy loss: if the full PubMed strategy is printed and runnable, run it as printed and fixed,
   both limited to publication dates up to the year of the reported search date (`"1000"[dp] :
   "<year>"[dp]`) plus any limits printed in the strategy. Loss = fixed minus printed; relative loss =
   loss / fixed.
4. Record the reported search date and whether it is after the rename year.

All counts from E-utilities esearch on the day of measurement; the query strings are published with
the results.

## Predictions

Labelled by how blind they are: only paper titles were seen, no strategy text.

- **P1 (eligibility).** Of the frame papers with full text, at least 70% contain a printed PubMed
  strategy that uses one of the five names with a MeSH tag.
- **P2 (quoting).** Among eligible papers, between 30% and 70% use the broken `name_quoted` form at
  least once.
- **P3 (block loss).** Among measured papers, at least 80% have block loss > 0.
- **P4 (strategy loss).** Among measured papers whose full strategy is runnable, at least 50% have
  strategy loss > 0. (Weak prior: in our earlier re-run of three 2025 reviews using 2024-2026 renames,
  1 of 3 lost records.)
- **P5 (size).** Among measured papers with a runnable strategy, the median relative strategy loss is
  below 5%.

Exploratory, not graded: AND-ed uses where the dead name empties a whole line; papers whose search
date was after the rename (which would mean the strategy may already have been broken when run,
depending on how legacy PubMed treated quoted entry terms, which we cannot test today).

## Stop rules and honest limits

- If the job fails or Europe PMC returns no full text for more than half of the frame, the study stops
  and that is reported.
- Europe PMC full text covers open-access papers only, and only text in the article body; strategies
  in supplementary files are not seen. The Questionnaires frame excludes papers that also contain the
  current heading's name, which removes strategies where the dead term is already covered.
- Re-running today is not the same as the authors' original run: PubMed has grown and changed since.
  Losses describe what the printed strategy does now (for updates and reproduction), not what the
  authors missed.
- If P3-P5 show little real-world loss, that is the result, and it will be published as such.
