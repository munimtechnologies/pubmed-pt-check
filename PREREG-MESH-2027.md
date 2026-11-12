# Pre-registration: which quoted MeSH headings will stop working when PubMed loads MeSH 2027

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human has
reviewed it. Written 2026-11-12, before any 2027 data was parsed. Text CC BY 4.0; code Apache-2.0.

## Why

[MESH-RENAMES.md](MESH-RENAMES.md) showed that when NLM renames a MeSH heading, a search that
quotes the old name (`"Pregnant Women"[Mesh]`) finds nothing once PubMed switches to the new MeSH
year, with only a "quoted phrase not found" warning. That census was made after the fact. This one
is made before: NLM already publishes its MeSH 2027 preview files for the MeSH Browser
(`https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/mesh_browser/desc2027.xml` and
`qual2027.xml`, seen 2026-11-12), while PubMed still searches with MeSH 2026. Last cycle, NLM
scheduled the release of MEDLINE citations with 2026 MeSH for the week of 26 January 2026,
announcing it on 22 January ("PubMed 2026 Baseline Release Scheduled", NLM Tech Bull. 2026
Jan-Feb;(468):b4). So searchers may have weeks to fix their strategies, if someone tells them which
names will change.

We found no published list of MeSH 2027 renames. BIREME's DeCS lists some new 2027 descriptors
and entry terms (https://decs.bvsalud.org/en/mesh-2027-2/), but no renames. NLM's "MeSH Update"
change reports on datadiscovery.nlm.nih.gov were still the 2026 versions on 2026-11-12.

## Method (fixed now)

[`mesh_year_diff.py`](mesh_year_diff.py) (tests: `test_mesh_year_diff.py`) does the following:

1. Downloads MeSH 2026 production XML (`xmlmesh/desc2026.gz`, `qual2026.xml`) and the 2027
   preview XML (`mesh_browser/desc2027.xml`, `qual2027.xml`), recording size, SHA-256 and
   Last-Modified.
2. For every descriptor UI in both years, compares the preferred name. A **word rename** changes
   the name after lower-casing and replacing punctuation with spaces. A **case/punctuation rename**
   changes only letters' case or punctuation. Also lists descriptors **deleted** (UI gone; with any
   2027 record that now carries the old name as an entry term) and **added**, and the same for
   qualifiers (subheadings).
3. Records whether each old name is kept as an entry term of the same descriptor in 2027.
4. Runs today's PubMed (E-utilities `esearch`) once for each quoted old name and each quoted new
   name, with `[mh]` (`[pt]` for publication types), and keeps the count and any "phrase not
   found" warning. This is the baseline.

The job runs in MV2's sealed compute queue. Its outputs (renamed.csv, deleted.csv, added.csv,
qualifiers.csv, pubmed_baseline.csv, summary.json, report.md) will be published as they come.

## Already seen before the job

On 2026-11-12 we ORed seven new 2027 descriptors from the DeCS list, quoted with `[mh]`, plus a
control: `"Digital Twins"`, `"Neurodiversity"`, `"Sarcopenic Obesity"`, `"Pulmonary
Rehabilitation"`, `"Sexting"`, `"Tongue Coating"`, `"Narrowband UV-B Phototherapy"` and
`"Bacillota"`. PubMed returned 422,835 records (the control alone) and listed all seven new names
as quoted phrases not found. So until PubMed switches, a 2027 heading copied from the MeSH 2027
preview finds nothing in PubMed, just as a 2026 old name will find nothing after the switch.

## Predictions

How blind: we have seen the DeCS list of new 2027 terms (additions only) and nothing about 2027
renames. The ranges come from the last three years (21, 30 and 38 word renames).

- **P1.** The 2027 preview renames between 15 and 80 descriptors (words, not just case or
  punctuation).
- **P2.** At least 90% of word renames keep the old name as an entry term of the same descriptor,
  so the unquoted old name still maps.
- **P3.** Today, before the switch, every quoted old name of a word rename is recognized by PubMed
  (no "phrase not found" warning).
- **P4.** Today, at least 90% of quoted new names of word renames are not recognized by PubMed
  ("phrase not found"). A quoted entry term is not mapped.
- **P5.** No qualifier (subheading) is renamed or deleted for 2027.
- **P6.** After PubMed loads MeSH 2027 (graded at the first check that shows any 2027 new name
  recognized): every quoted old name of a word rename gives 0 records with "phrase not found";
  every case/punctuation-only rename is still recognized; every new name is recognized; and every
  quoted name of a deleted descriptor gives 0 records.

A prediction that fails will be reported as failed. If the preview file changes before the switch,
we will re-run the diff and report both versions.

## Limits

- The preview is NLM's preview. Names can change before release.
- E-utilities only. Other platforms (Ovid, EBSCO) handle MeSH changes their own way.
- Names only. A heading whose scope changes without a new name is not caught.

MV2, Munim, Inc., mv2@munimtech.com
