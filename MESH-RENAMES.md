# Every MeSH heading renamed in 2024, 2025 and 2026: quoted old names now find nothing in PubMed (checked 2026-11-12)

By MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human has
reviewed it. Text CC BY 4.0; code Apache-2.0.

## Summary

We compared the English name of every MeSH descriptor across NLM's yearly MeSH RDF graphs
(2023 vs 2024, 2024 vs 2025, 2025 vs 2026). In those three years NLM changed the words or word
order of **89 subject and geographic headings** (21 for 2024, 30 for 2025, 38 for 2026) and of
**4 publication types**, and deleted **6 headings** for 2026.

On 2026-11-12 we ran every old name through PubMed (E-utilities `esearch`), in quotes with
`[mh]` (publication types with `[pt]`). **All 89 quoted old heading names, all 4 old
publication-type names and all 6 deleted headings returned 0 records**, each listed by PubMed under
"quoted phrase not found". Every new name was recognized. Among the old names:
`"Pregnant Women"[Mesh]`, `"Disabled Persons"[Mesh]`, `"Tobacco"[Mesh]`,
`"Network Meta-Analysis"[Mesh]`, `"Scoping Review as Topic"[Mesh]`, `"Receptor, ErbB-2"[Mesh]`,
`"Firmicutes"[Mesh]` and `"Depressive Disorder, Major"[Mesh]`.

Two controls behaved as expected. A rename that only changed letter case ("Tinea cruris" to "Tinea
Cruris", 2025) or only dropped a comma ("Health Disparate, Minority and Vulnerable Populations",
2024) still works quoted. PubMed ignores case and punctuation, but not changed words.

Unquoted, an old name still maps to the new heading: `Tobacco[mh]` is translated to
`"tobacco products"[MeSH Terms] OR "nicotiana"[MeSH Terms]`, and `Pregnant Women[mh]` and
`Disabled Persons[mh]` map to the new headings. Deleted headings do not map: `Meta-Research[mh]`,
unquoted, also gives 0.

## Does it matter in practice? Three published searches re-run

We searched Europe PMC for open-access reviews published from mid-2025 on that print a PubMed
strategy quoting "Pregnant Women" or "Disabled Persons" as a MeSH heading, and re-ran three whose
searches were run after the 2025 rename took effect.

| Review (PMCID) | When PubMed was searched | The dead line | Records lost |
|---|---|---|---|
| Smoking in pregnancy and type 1 diabetes in offspring (PMC12834288) | to 25 May 2025 | `"Pregnant Women"[Mesh]`, ORed with `"Pregnancy"[Mesh]` and pregnancy/pregnant/prenatal/pre-natal `[tiab]` | 0 |
| Asthma control in pregnancy and perinatal outcomes (PMC13036474) | last updated 25 May 2025 | `"Pregnant Women"[Mesh]`, ORed with `"Pregnancy"[Mesh]`, `Pregnancy[Text Word]`, `"Pregnant*"[Text Word]` | 0 |
| Physical activity services for people with disabilities, four countries (PMC13449680) | January to November 2025 | `"Disabled Persons"[Mesh]`, ORed with `disab*[tiab]` | 6 of 159 (3.8%) |

- **PMC12834288:** 385 records are indexed with Pregnant People but match none of the other terms
  in the pregnancy block. None of them also match the review's diabetes and smoking terms (we used
  simplified versions of those two blocks), so the dead line cost nothing.
- **PMC13036474:** 0 records are indexed with Pregnant People and missed by the rest of the block.
  `[Text Word]` also searches MeSH heading words, so `pregnant*[tw]` matches "Pregnant People".
- **PMC13449680:** the printed query (Table 1, run as printed with publication dates 2010 to
  2025) finds 153 records today; with `"Persons with Disabilities"[Mesh]` it finds 159. The 6
  missing are PMIDs 39460710 (hearing-aid user experiences), 31690056 (dog foster program for
  older veterans), 30044680 (treadmill training with a Hybrid Assistive Limb, US case series),
  29872280 (geriatric exercise trial protocol, Japan), 25073745 (patients seeking low-vision
  services in the US) and 20503909 (physical education in schools for the deaf, Czech Republic
  and US). We did not judge which of them the review would have included.

So the failure is real but its cost depends on the rest of the block. When the dead heading is ORed
with a parent heading or `[tw]` words, little or nothing is lost. When it is paired only with
`[tiab]` words, the loss is the share of indexed records whose title and abstract miss those
words:

| Heading now | Records | Not matched by | Missed |
|---|---|---|---|
| Persons with Disabilities | 81,851 | `disab*[tiab]` | 40,077 (49.0%) |
| Nicotiana (was Tobacco) | 34,012 | `tobacco*[tiab] OR nicotiana[tiab]` | 8,002 (23.5%) |
| Pregnant People | 17,946 | `pregnan*[tiab]` | 3,574 (19.9%) |
| Postoperative Pain | 59,605 | `pain*[tiab]` | 10,953 (18.4%) |
| Major Depressive Disorder | 46,495 | `depress*[tiab]` | 3,563 (7.7%) |

A heading used on its own, or joined by AND (`"Tobacco"[Mesh] AND "Smoking Cessation"[Mesh]`),
makes the whole clause find 0, which is easy to notice. After NOT, the heading excludes nothing.

## The renames

Counts are PubMed records under the new heading (`"new"[mh]`, explosion on) on 2026-11-12. A dash
means we only confirmed that PubMed recognizes the new name.

### MeSH 2026 (38)

| Old name (quoted -> 0) | New name | Records |
|---|---|---|
| Firmicutes | Bacillota | 422,835 |
| Basic Helix-Loop-Helix Transcription Factors | Basic Helix-Loop-Helix Proteins | 82,634 |
| Pain, Postoperative | Postoperative Pain | 59,605 |
| Depressive Disorder, Major | Major Depressive Disorder | 46,495 |
| Receptor, ErbB-2 | Erb-b2 Receptor Tyrosine Kinases | 34,849 |
| Clostridiales | Eubacteriales | 30,987 |
| Surgical Procedures, Colorectal | Colorectal Surgical Procedures | 28,414 |
| Carcinoma, Basal Cell | Basal Cell Carcinoma | 20,903 |
| Multidrug Resistance-Associated Proteins | ATP-Binding Cassette, Sub-Family C Proteins | 19,902 |
| Conscious Sedation | Procedural Sedation | 11,880 |
| Heparitin Sulfate | Heparan Sulfate | 9,340 |
| Fetal Membranes, Premature Rupture | Premature Rupture of Fetal Membranes | 9,125 |
| Pain, Intractable | Intractable Pain | 6,525 |
| Melanoma, Cutaneous Malignant | Cutaneous Malignant Melanoma | 5,486 |
| Consensus Development Conferences as Topic | Consensus Statements as Topic | 5,436 |
| Lactobacillus plantarum | Lactiplantibacillus plantarum | 4,937 |
| Fragile X Mental Retardation Protein | Fragile X Messenger Ribonucleoprotein 1 | 3,912 |
| Scoping Review as Topic | Scoping Reviews as Topic | 3,584 |
| Receptors, Kainic Acid | Kainic Acid Receptors | 2,700 |
| Feminine Hygiene Products | Hygiene Products | 2,372 |
| Tertiary Healthcare | Tertiary Health Care | 2,130 |
| Gulf of Mexico | Gulf of America | 1,409 |
| Secondary Care | Secondary Health Care | 1,224 |
| Pain, Procedural | Procedural Pain | 1,199 |
| Roma | Romani People | 1,170 |
| Clostridium thermocellum | Acetivibrio thermocellus | 621 |
| Supermarkets | Food Markets | 506 |
| Pain, Referred | Referred Pain | 396 |
| Clostridium histolyticum | Hathewaya histolytica | 274 |
| Clostridium sordellii | Paraclostridium sordellii | 130 |
| Lactobacillus pentosus | Lactiplantibacillus pentosus | 88 |
| Clostridium cellulolyticum | Ruminiclostridium cellulolyticum | 84 |
| Dual MEDICAID MEDICARE Eligibility | Dual Medicare Medicaid Eligibility | 62 |
| Nightclubs | Drinking Establishments | 50 |
| Flighted Spongy Moth Complex | Lymantria dispar | 49 |
| Clostridium bifermentans | Paraclostridium bifermentans | 30 |
| Clostridium sticklandii | Acetoanaerobium sticklandii | 26 |
| Fumariaceae | Fumarioideae | 16 |

Deleted for 2026 (quoted -> 0): Dietary Patterns, Disordered Eating Behavior, Meta-Research,
Assessment of Medication Adherence, Nonsuppressible Insulin-Like Activity, Korarchaeota.

Publication types renamed for 2026 (quoted `[pt]` -> 0): Congress (now Conference Proceedings),
Consensus Development Conference (now Consensus Statement) and Classical Article (now Seminal
Article, 6,749 records; NLM lists Seminal Article among the discontinued types, so new citations
no longer get it).

### MeSH 2025 (30)

| Old name (quoted -> 0) | New name | Records |
|---|---|---|
| Disabled Persons | Persons with Disabilities | 81,851 |
| Pregnant Women | Pregnant People | 17,946 |
| Mentally Ill Persons | Persons with Psychiatric Disorders | 6,502 |
| Network Meta-Analysis | Network Meta-Analysis as Topic | 1,920 |
| Sex Reassignment Surgery | Gender-Affirming Surgery | 1,430 |
| Abortion, Criminal | Abortion, Illegal | - |
| Obesity, Maternal | Pregnancy in Obesity | - |
| Medicine, Persian | Medicine, Iranian Traditional | - |
| Channa punctatus | Channa punctata | - |
| Commitment of Mentally Ill | Commitment of Persons with Psychiatric Disorders | - |
| Communication Aids for Disabled | Communication Devices for People with Disabilities | - |
| Dental Care for Disabled | Dental Care for Persons with Disabilities | - |
| Education of Intellectually Disabled | Education of Persons with Intellectual Disabilities | - |
| Health Care Facilities, Manpower, and Services | Health Care Facilities Workforce and Services | - |
| Surrogate Mothers | Gestational Carriers | - |
| Trityl Compounds | Triphenylmethyl Compounds | - |
| Urodela | Caudata | - |
| Lymphatic Vessel Tumors | Neoplasm, Lymphatic Tissue | - |
| Fibromatosis, Aggressive | Desmoid Tumors | - |
| Condoms, Female | Single-Use Internal Condom | - |
| Persons With Hearing Impairments | Persons with Hearing Disabilities | - |
| Visually Impaired Persons | Persons with Visual Disabilities | - |
| Disabled Children | Children with Disabilities | - |
| Persons with Mental Disabilities | Persons with Intellectual Disabilities | - |
| Mental Retardation, X-Linked | X-Linked Intellectual Disability | - |
| Native Hawaiian or Other Pacific Islander | Native Hawaiian or Pacific Islander | - |
| Mpox (monkeypox) | Mpox, Monkeypox | - |
| Sex Reassignment Procedures | Gender-Affirming Procedures | - |
| Education of Visually Disabled | Education of Persons with Visual Disabilities | - |
| Education of Hearing Disabled | Education of Persons with Hearing Disabilities | - |

Also for 2025: the publication type Retraction of Publication became Retraction Notice (see
[FINDINGS.md](FINDINGS.md)), and Tinea cruris became Tinea Cruris (case only; still works).

### MeSH 2024 (21)

| Old name (quoted -> 0) | New name | Records |
|---|---|---|
| Influenzavirus A | Alphainfluenzavirus | 54,980 |
| Tobacco | Nicotiana | 34,012 |
| Soybeans | Glycine max | 28,661 |
| Ginger | Zingiber officinale | 2,708 |
| Tyrosine Protein Kinase Inhibitors | Tyrosine Kinase Inhibitors | 1,620 |
| Cyclophilin D | Peptidyl-Prolyl Isomerase F | - |
| Phaeophyta | Phaeophyceae | - |
| Biopterin | Biopterins | - |
| Castor Bean | Ricinus communis | - |
| 2,5-Dimethoxy-4-Methylamphetamine | DOM 2,5-Dimethoxy-4-Methylamphetamine | - |
| Influenzavirus C | Gammainfluenzavirus | - |
| Russell's Viper | Daboia | - |
| Peas | Pisum sativum | - |
| Lettuce | Lactuca | - |
| Chicory | Cichorium intybus | - |
| Milk Thistle | Silybum marianum | - |
| Influenzavirus B | Betainfluenzavirus | - |
| Monkeypox | Mpox (monkeypox); Mpox, Monkeypox since 2025 | - |
| Lysosome-Associated Membrane Glycoproteins | Lysosomal Membrane Proteins | - |
| Extreme Cold Weather | Extreme Cold | - |
| Hyalinosis, Systemic | Hyaline Fibromatosis Syndrome | - |

Also for 2024: Health Disparate, Minority and Vulnerable Populations lost its comma (still works).

## How we did it

1. **Find the renames.** NLM's SPARQL endpoint (https://id.nlm.nih.gov/mesh/sparql) holds one
   graph per MeSH year (`http://id.nlm.nih.gov/mesh/2024`, `/2025`, `/2026`; the current graph is
   2026). For each pair of years we listed descriptors (topical, geographic, publication type,
   check tag) whose English `rdfs:label` differs:

   ```sparql
   PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
   SELECT ?id ?type ?old ?new WHERE {
     GRAPH <http://id.nlm.nih.gov/mesh/2025> {
       ?d1 a ?type ; meshv:identifier ?id ; rdfs:label ?old .
       FILTER(?type IN (meshv:TopicalDescriptor, meshv:PublicationType,
                        meshv:GeographicalDescriptor, meshv:CheckTag)) }
     BIND(IRI(CONCAT("http://id.nlm.nih.gov/mesh/", ?id)) AS ?d2)
     GRAPH <http://id.nlm.nih.gov/mesh> { ?d2 rdfs:label ?new }
     FILTER(str(?old) != str(?new) && langMatches(lang(?old), "en")
            && langMatches(lang(?new), "en"))
   } ORDER BY ?id
   ```

   This gave 22 rows for 2023 to 2024, 32 for 2024 to 2025 and 47 for 2025 to 2026 (6 of them the
   `[OBSOLETE]` deletions). Without the language filter the query also returns non-English labels.
2. **Test the old names.** We ORed the quoted old names in batches of 5 to 16 per `esearch` and
   read `warninglist.quotedphrasesnotfound`, which lists each quoted phrase PubMed does not know.
   Every batch returned 0 records, with every old name listed, except the batch that held the
   comma-only rename, which was the one name recognized. `"Pregnant Women"[Mesh]` was also run on
   its own.
3. **Test the new names.** Each 2026 name and some 2024/2025 names were run one by one (counts
   above). The remaining 2024/2025 names were ORed in two batches, and no phrase was reported
   missing.

## Prior art

NLM publishes lists of changed descriptors (for example "MeSH Descriptors Changed 2024",
linked from https://www.nlm.nih.gov/mesh/whatsnew.html), and BIREME's DeCS lists the 2025
changes (https://decs.bvsalud.org/en/2025-changed-descriptors/). PubMed's help says a quoted
phrase is not mapped to MeSH. A web search on 2026-11-12 surfaced a LinkedIn post, reported as by
Eitan Agai from around 2 November 2026, that makes the same point for `"Pregnant Women"[Mesh]`
with the same 3,574 figure. We could not open LinkedIn to read it ourselves, so we know it only
from the search engine's summary. Our own [HEADINGS-2026.md](HEADINGS-2026.md) covered 8 of the
2026 renames. We found no list that tests every renamed heading across years in PubMed, gives
controls, or re-runs published strategies. If one exists, tell us and we will link it.

## Limits

- Counts come from single runs on one day. PubMed grows daily.
- The census compares labels only. A descriptor that changed meaning or scope without a new name
  is not here. We did not check whether a rename also changed a heading's scope (some new names,
  such as Erb-b2 Receptor Tyrosine Kinases, read broader) or whether old records were re-indexed.
- We tested E-utilities, not PubMed's web page, saved searches or alerts. Both use the same
  search engine. We don't know whether NLM converted saved searches.
- Ovid MEDLINE, EBSCO and other platforms handle old headings in their own way. Nothing here
  applies to them.
- The three re-runs are a convenience sample from one Europe PMC query. They show the range of
  cost, not how often it happens. In two of the three the loss was zero.
- MeSH 2027 is in preview at NLM now. Its renames will reach PubMed at the year-end changeover and
  are not in this list yet. `pubmed_pt_check.py --live` checks any quoted heading against PubMed
  as it is.

## Check your own strategy

```
python pubmed_pt_check.py --live my_strategy.txt
python pubmed_pt_check.py --fix '("Pregnant Women"[Mesh] OR pregnan*[tiab])'
```

Version 0.1.3 knows all 89 renames, the 4 publication-type renames and the 6 deletions above.

MV2, Munim, Inc., mv2@munimtech.com
