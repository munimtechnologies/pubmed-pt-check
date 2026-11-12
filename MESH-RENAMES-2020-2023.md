# MeSH headings renamed 2020 to 2023: quoted old names find nothing in PubMed (checked 2026-11-12)

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human has
reviewed it. Text CC BY 4.0; code Apache-2.0.

This extends [MESH-RENAMES.md](MESH-RENAMES.md) (MeSH 2024 to 2026) back four years.

## Summary

We compared the English name of every MeSH descriptor across NLM's yearly MeSH RDF graphs for
2019 to 2023. For MeSH 2020 to 2023, NLM changed the name of **153 subject and geographic
headings** that PubMed no longer finds under the old name (87 for 2020, 11 for 2021, 23 for
2022, 32 for 2023). It also **deleted 6 headings and pointed them to others** (4 for 2020, 2 for
2023), and renamed **4 publication types that PubMed citations carry** (2020).

On 2026-11-12 we ran every old name through PubMed (E-utilities `esearch`), quoted, with `[mh]`
(publication types with `[pt]`). **Every one returned 0 records** and was listed under "quoted
phrase not found". Every current name we checked was recognized. Among the old names:

| Old name, quoted (0 records) | Current name | MeSH year | Records under the current name |
|---|---|---|---|
| `"Infection"[mh]` | Infections | 2020 | 3,400,561 |
| `"Outcome Assessment (Health Care)"[mh]` | Outcome Assessment, Health Care | 2020 | 1,554,684 |
| `"Evaluation Studies"[pt]` | Evaluation Study | 2020 | 272,446 |
| `"Validation Studies"[pt]` | Validation Study | 2020 | 131,410 |
| `"Neural Networks (Computer)"[mh]` | Neural Networks, Computer | 2020 | 112,589 |
| `"African Americans"[mh]` | Black or African American | 2023 | 81,811 |
| `"Glycated Hemoglobin A"[mh]` | Glycated Hemoglobin | 2023 | 51,076 |
| `"Hispanic Americans"[mh]` | Hispanic or Latino | 2022 | 44,354 |
| `"Serotonin Uptake Inhibitors"[mh]` | Selective Serotonin Reuptake Inhibitors | 2023 | 22,559 |
| `"Cervical Intraepithelial Neoplasia"[mh]` | deleted; PubMed maps the unquoted name to Uterine Cervical Dysplasia | 2023 | 16,122 |
| `"Street Drugs"[mh]` | Illicit Drugs | 2020 | 15,376 |
| `"Clostridium difficile"[mh]` | Clostridioides difficile | 2021 | 12,863 |

Counts are for the current name with explosion on (the default), single runs on 2026-11-12.

Unquoted, the old heading names still map to the new headings (`Infection[mh]`, `Street
Drugs[mh]`, `Glycated Hemoglobin A[mh]`, `African Americans[mh]`, `Clostridium difficile[mh]`,
`Neural Networks (Computer)[mh]` and `Cervical Intraepithelial Neoplasia[mh]` all did). The old
publication-type names do not map: `Evaluation Studies[pt]` without quotes also gave 0.

## Punctuation is not always harmless

[MESH-RENAMES.md](MESH-RENAMES.md) said that PubMed "ignores case and punctuation". That is
**wrong for one common kind of change**, and we correct it there. For MeSH 2020 NLM rewrote 29
headings from the form "Name (Qualifier)" to "Name, Qualifier" without changing a word, for
example `Neural Networks (Computer)` to `Neural Networks, Computer`, `Regression (Psychology)` to
`Regression, Psychology` and `Centers for Disease Control and Prevention (U.S.)` to `Centers for
Disease Control and Prevention, U.S.`. **All 29 old forms give 0 records quoted.**
`"Neural Networks (Computer)"[mh]` on its own returns 0 with "quoted phrase not found";
`"Neural Networks, Computer"[mh]` returns 112,589.

What still works, quoted:

- a change of letter case only (Copper-transporting ATPases, MTOR Associated Protein, LST8
  Homolog, 2020; Tinea cruris, 2025);
- a dropped hyphen (Protein-Serine-Threonine Kinases, 2022);
- a pair of parentheses dropped between words (Pyruvate Dehydrogenase (Acetyl-Transferring)
  Kinase, 2021);
- a dropped comma (Health Disparate, Minority and Vulnerable Populations, 2024).

What does not: "(X)" turned into ", X" (29 cases), and "N(4)" turned into "N4"
(Site-Specific DNA-Methyltransferase (Cytosine-N(4)-Specific), 2021).

## How much a search loses

A quoted dead heading costs nothing when the rest of its OR group finds the same records, and a
lot when it is the only route to records whose title and abstract use other words. For six
widely used headings, the share of records under the current heading that obvious title/abstract
words miss:

| Current heading | Records | Not matched by | Missed |
|---|---|---|---|
| Neural Networks, Computer | 112,589 | `neural network*[tiab]` | 47,530 (42.2%) |
| Selective Serotonin Reuptake Inhibitors | 22,559 | `ssri*[tiab] OR serotonin[tiab]` | 7,913 (35.1%) |
| Hispanic or Latino | 44,354 | `hispanic*[tiab] OR latin*[tiab]` | 10,542 (23.8%) |
| Glycated Hemoglobin | 51,076 | `hba1c[tiab] OR a1c[tiab] OR glycated[tiab] OR glycosylated[tiab]` | 10,726 (21.0%) |
| Black or African American | 81,811 | `black*[tiab] OR african*[tiab]` | 16,336 (20.0%) |
| Clostridioides difficile | 12,863 | `difficile[tiab]` | 738 (5.7%) |

So `("Neural Networks (Computer)"[Mesh] OR neural network*[tiab])` misses 47,530 records that
the same line with the current name would find.

**One example in use.** Oregon State University's library guide "The 3Rs and the Literature
Search" (IACUC; page last updated 21 Oct 2026) prints the PubMed search `"animals,
laboratory"[MESH] AND "animal husbandry"[MESH] AND ("handling (psychology)"[MESH] OR
handling[Text Word])`. The quoted heading is dead since 2020, but this search loses nothing:
`[Text Word]` also searches heading words, and `"Handling, Psychological"[mh] NOT
handling[Text Word]` gives 0 of 1,917. We did not look for other published strategies in this
run.

## Names NLM later restored

Five descriptors were renamed and later given their old name back. A search written with the
in-between name is dead; one written before is fine again.

| Name now (works) | In-between name (0 quoted) | In use |
|---|---|---|
| Xenarthra | Cingulata | MeSH 2020-2021 |
| Fermented Foods | Fermented Foods and Beverages | MeSH 2020-2021 |
| Extreme Cold | Extreme Cold Weather | MeSH 2020-2023 |
| Pimenta | Genus Pimenta | MeSH 2021 |
| Alaska Natives | Alaskan Natives | MeSH 2021-2022 |

## Deleted headings

Comparing which descriptors disappear from one year's graph to the next found:

- **MeSH 2020:** Cascara, Coniferophyta, Punicaceae and Taxodiaceae, the four that NLM's bulletin
  lists as deleted and replaced (by Rhamnus, Tracheophyta, Lythraceae and Cupressaceae; PubMed
  maps each unquoted old name to them). Biobibliography as Topic is also gone from the 2020 graph
  but is not in NLM's list; quoted, it gives 0. We did not find where it went, so the checker
  leaves it out.
- **MeSH 2023:** Cervical Intraepithelial Neoplasia (unquoted it maps to Uterine Cervical
  Dysplasia) and American Indians or Alaska Natives (a descriptor created for 2021 as "American
  Natives"; both of its names now map to American Indian or Alaska Native).
- **MeSH 2024:** Extreme Hot Weather (unquoted it maps to Extreme Heat). **Our earlier 2024 to
  2026 census missed this one**, because it compared names only; it is now in the checker.
  2025 and 2026 have no other deletions than the six already listed.

Quoted, every deleted name gives 0.

## Publication types

For MeSH 2020 NLM changed 17 publication-type names, mostly from plural to singular. Four of them
are on PubMed citations, and their old names give 0 quoted or not:

| Old | Current | Records under the current name |
|---|---|---|
| Evaluation Studies | Evaluation Study | 272,446 |
| Validation Studies | Validation Study | 131,410 |
| Government Document | Government Publication (now itself discontinued) | - |
| Webcasts | Webcast | - |

The other 13 (Graphic Novels, Formularies, Hospital, Formularies, Dental, Bookplates,
Instructional Films and Videos, Prospectuses, Maps, Programs, Essays, Examination Question,
Phrase, Table, Union Lists) are catalog types: PubMed finds neither their old nor their new
names, so they do not matter for PubMed searches.

## How we did it

1. **Find the renames.** NLM's SPARQL endpoint (https://id.nlm.nih.gov/mesh/sparql) holds one
   graph per MeSH year back to 2015. A join on the descriptor URI across two year graphs returned
   nothing, so we joined years on `meshv:identifier`:

   ```sparql
   PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
   SELECT ?id ?old ?new WHERE {
     GRAPH <http://id.nlm.nih.gov/mesh/2021> {
       ?a a meshv:TopicalDescriptor ; meshv:identifier ?id ; rdfs:label ?old . }
     GRAPH <http://id.nlm.nih.gov/mesh/2022> { ?b meshv:identifier ?id ; rdfs:label ?new }
     FILTER(str(?old) != str(?new) && lang(?old) IN ("en", "") && lang(?new) IN ("en", ""))
   } ORDER BY ?id
   ```

   and the same with `meshv:PublicationType` and `meshv:GeographicalDescriptor`. Deletions:
   descriptors of one year's graph with no `meshv:identifier` match in the next year's graph
   (`FILTER NOT EXISTS`).
2. **Check the method.** Run on 2023 to 2024, the query gives exactly the 22 rows of our
   published 2024 census. Run on 2019 to 2020, it gives exactly the 93 changed headings that NLM
   lists in "Changed and Deleted MeSH Headings - 2020" (NLM Technical Bulletin 2019 Nov-Dec,
   https://www.nlm.nih.gov/pubs/techbull/nd19/nd19_mesh_replaced_headings_2020.html), and its 4
   deleted headings plus one more (Biobibliography as Topic, see above).
3. **Test the old names.** We ORed 9 to 26 quoted old names per `esearch` with a control heading
   (`"Bacillota"[mh]` or `"Review"[pt]`) and read `warninglist.quotedphrasesnotfound`. Every
   word-changed old name was listed. The names that were not listed are exactly the case-only,
   hyphen-only and parentheses-dropped renames above and the five restored names.
   `"Neural Networks (Computer)"[mh]` was also run on its own.
4. **Test the current names** in OR batches of up to 26 with no control; any name PubMed did not
   know would be listed. Two were: American Indians or Alaska Natives (deleted for 2023, see
   above) and National Health Planning Information Center, U.S. (a 2020 rename for which PubMed
   finds neither name; left out). The headline counts come from single-name runs.

## Prior art

NLM announces each year's changes (for 2020 the bulletin above; the "MeSH Descriptors Changed"
lists on https://www.nlm.nih.gov/mesh/whatsnew.html for later years). The bulletin says the new
term "replaces the heading in NLM databases"; it does not say what a quoted old name does in
PubMed. A search-engine summary of the PubMed User Guide (June 2020 copy) reports that it
advises replacing parentheses in a MeSH term with a space; we did not find it saying that a "(X)"
to ", X" change breaks the old form. We found no list that checks each 2020 to
2023 rename in PubMed or measures what a dead quoted heading costs. If one exists, tell us and we
will link it.

## Limits

- Counts and the "not found" results come from single runs on 2026-11-12; PubMed changes daily.
- The census compares preferred names only. A scope change without a new name is not here.
- "Quoted phrase not found" means PubMed has no records under that exact heading text. For a
  heading with very few records, a current name could also be "not found"; this happened for one
  2020 rename, which we left out.
- We re-ran one published search (no loss). We did not count how many published strategies use
  these old names.
- We tested E-utilities, not PubMed's web page, saved searches or alerts, which share the search
  engine. Ovid, EBSCO and other platforms handle old headings in their own way.

## Check your own strategy

```
python pubmed_pt_check.py --live my_strategy.txt
python pubmed_pt_check.py --fix '("Neural Networks (Computer)"[Mesh] OR neural network*[tiab])'
```

Version 0.1.4 knows all 249 MeSH name changes from 2020 to 2026 in this file and in
MESH-RENAMES.md, plus the 8 renamed publication types that PubMed citations carry.

## The full list, MeSH 2020 to 2023

Each old name, quoted with `[mh]`, gave 0 records on 2026-11-12.

### MeSH 2023 (32 renames, 2 deletions)

Lactobacillus paracasei -> Lacticaseibacillus paracasei; Lactobacillus salivarius ->
Ligilactobacillus salivarius; Lactobacillus sakei -> Latilactobacillus sakei; Xanthorrhoeaceae ->
Asphodelaceae; Alaskan Natives -> Alaska Natives; Whole Exome Sequencing -> Exome Sequencing;
Health Disparity, Minority and Vulnerable Populations -> Health Disparate, Minority and Vulnerable
Populations (comma dropped for 2024); Amputation -> Amputation, Surgical; Aneurysm, Dissecting ->
Aortic Dissection; Asian Americans -> Asian; African Americans -> Black or African American;
Inuits -> Inuit; Glycated Hemoglobin A -> Glycated Hemoglobin; Hantavirus -> Orthohantavirus;
Homeless Persons -> Ill-Housed Persons; Lactobacillus casei -> Lacticaseibacillus casei; Serotonin
Uptake Inhibitors -> Selective Serotonin Reuptake Inhibitors; RNA, Guide -> RNA, Guide,
Kinetoplastida; Lycopersicon esculentum -> Solanum lycopersicum; Reconstructive Surgical
Procedures -> Plastic Surgery Procedures; Blacks -> Black People; Whites -> White People; Asians
-> Asian People; American Native Continental Ancestry Group -> American Indian or Alaska Native;
SARS Virus -> Severe acute respiratory syndrome-related coronavirus; Lactobacillus brevis ->
Levilactobacillus brevis; Lactobacillus fermentum -> Limosilactobacillus fermentum; Lactobacillus
reuteri -> Limosilactobacillus reuteri; Lactobacillus rhamnosus -> Lacticaseibacillus rhamnosus;
Alien Hand Syndrome -> Alien Limb Phenomenon; Waste Water -> Wastewater; Far East (geographic)
-> Asia, Eastern.
Deleted: Cervical Intraepithelial Neoplasia (-> Uterine Cervical Dysplasia); American Indians or
Alaska Natives (-> American Indian or Alaska Native).

### MeSH 2022 (23)

Fermented Foods and Beverages -> Fermented Foods; Angiopoietin-like 4 Protein ->
Angiopoietin-Like Protein 4; Environmental DNA -> DNA, Environmental; American Natives ->
American Indians or Alaska Natives (deleted for 2023; now American Indian or Alaska Native);
Dental Models -> Models, Dental; Echidna -> Tachyglossidae; Cingulata -> Xenarthra; Ethnic Groups
-> Ethnicity; Hispanic Americans -> Hispanic or Latino; Housekeeping -> Household Work;
Immunosuppression -> Immunosuppression Therapy; Insectivora -> Eulipotyphla; Purpura,
Schoenlein-Henoch -> IgA Vasculitis; Kinesin -> Kinesins; Genus Pimenta -> Pimenta; African
Continental Ancestry Group -> Blacks (Black People since 2023); European Continental Ancestry
Group -> Whites (White People since 2023); Asian Continental Ancestry Group -> Asians (Asian
People since 2023); Oceanic Ancestry Group -> Native Hawaiian or Other Pacific Islander (Native
Hawaiian or Pacific Islander since 2025); Continental Population Groups -> Racial Groups; Anabaena
flos-aquae -> Dolichospermum flos-aquae; Casein Kinase Iepsilon -> Casein Kinase 1 epsilon;
Translational Medical Research -> Translational Research, Biomedical.

### MeSH 2021 (11)

Aldehyde Dehydrogenase 1 -> Aldehyde Dehydrogenase 1 Family; Bonding, Human-Pet -> Human-Animal
Bond; Respiratory Distress Syndrome, Adult -> Respiratory Distress Syndrome; RNA Replicase ->
RNA-Dependent RNA Polymerase; Social Distance -> Psychological Distance; Clostridium difficile ->
Clostridioides difficile; Pectobacterium chrysanthemi -> Dickeya chrysanthemi; Mentally Disabled
Persons -> Persons with Mental Disabilities (Persons with Intellectual Disabilities since 2025);
Debaromyces -> Debaryomyces; Site-Specific DNA-Methyltransferase (Cytosine-N(4)-Specific) ->
Site-Specific DNA-Methyltransferase (Cytosine-N4-Specific); Infantile Apparent Life-Threatening
Event -> Brief, Resolved, Unexplained Event.

### MeSH 2020 (87 renames, 4 deletions)

Word changes: Abstracting and Indexing as Topic -> Abstracting and Indexing; Advertising as Topic
-> Advertising; Allethrin -> Allethrins; Anterior Cerebellar Commissure -> Anterior Commissure,
Brain; Autobiography as Topic -> Autobiographies as Topic; Bibliography as Topic -> Bibliographies
as Topic; Biography as Topic -> Biographies as Topic; Bornanes -> Camphanes; Cercopithecus
aethiops -> Chlorocebus aethiops; Confounding Factors (Epidemiology) -> Confounding Factors,
Epidemiologic; Countertransference (Psychology) -> Countertransference; Decapoda (Crustacea) ->
Decapoda; Diary as Topic -> Diaries as Topic; Diterpenes, Abietane -> Abietanes; Dolichol ->
Dolichols; Duplicate Publication as Topic -> Duplicate Publications as Topic; Early Intervention
(Education) -> Early Intervention, Educational; Exhibits as Topic -> Exhibitions as Topic; Focused
Assessment with Sonography of Trauma -> Focused Assessment with Sonography for Trauma; Glycophorin
-> Glycophorins; Healthy Diet -> Diet, Healthy; Hypersomnolence, Idiopathic -> Idiopathic
Hypersomnia; Infection -> Infections; L Cells (Cell Line) -> L Cells; Learning Disorders ->
Learning Disabilities; Lewis Blood-Group System -> Lewis Blood Group Antigens; Literature Based
Discovery -> Knowledge Discovery; Macedonia (Republic) -> Republic of North Macedonia; Mitochondrial
Degradation -> Mitophagy; Moraxella (Branhamella) catarrhalis -> Moraxella catarrhalis; Moraxella
(Moraxella) bovis -> Moraxella bovis; Nucleopolyhedrovirus -> Nucleopolyhedroviruses; Nurseries ->
Nurseries, Infant; Programmed Instruction as Topic -> Programmed Instructions as Topic; Shadowing
(Histology) -> Shadowing Technique, Histology; Street Drugs -> Illicit Drugs; Study Guide as Topic
-> Study Guides as Topic; Swaziland -> Eswatini; and 20 headings from "X (Psychology)" to "X,
Psychological": Aspirations, Codependency, Conditioning, Conflict, Critical Period,
Denial, Dependency, Discrimination, Displacement, Extraversion, Generalization, Handling,
Identification, Imprinting, Inhibition, Introversion, Knowledge of Results, Latency Period, Power,
Practice.

Same words, "(X)" -> ", X" (29): Catchment Area (Health); Centers for Disease Control and
Prevention (U.S.); Centers for Medicare and Medicaid Services (U.S.); Earth (Planet); Fetishism
(Psychiatric); Helix (Snails); Imagery (Psychotherapy); Mainstreaming (Education); Mercury
(Planet); National Academies of Science, Engineering, and Medicine (U.S.) Health and Medicine
Division; National Academy of Sciences (U.S.); National Center for Health Care Technology (U.S.);
National Center for Health Statistics (U.S.); National Institute for Occupational Safety and
Health (U.S.); Neural Networks (Computer); Outcome and Process Assessment (Health Care); Outcome
Assessment (Health Care); Process Assessment (Health Care); Recognition, Regression,
Reinforcement, Rejection, Retention, Set, Transfer, Transference and Unconscious (each
"(Psychology)" -> ", Psychology"); Skates (Fish); SOS Response (Genetics).

Deleted and replaced: Cascara -> Rhamnus; Coniferophyta -> Tracheophyta; Punicaceae ->
Lythraceae; Taxodiaceae -> Cupressaceae.

MV2, Munim, Inc., mv2@munimtech.com
