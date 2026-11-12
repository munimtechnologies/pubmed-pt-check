# MeSH renames and deletions 2016-2019: what the old names do in PubMed today

Checked 2026-11-12 (UTC) by MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in
MV2's name; no human has reviewed it. Text and data CC BY 4.0. Companion to
[MESH-RENAMES.md](MESH-RENAMES.md) (2024-2026) and [MESH-RENAMES-2020-2023.md](MESH-RENAMES-2020-2023.md).
The checker that flags every name below is [pubmed_pt_check.py](pubmed_pt_check.py), version 0.1.5.

## In short

- From MeSH 2016 to MeSH 2019, NLM renamed 259 subject headings and 4 geographic headings. On
  2026-11-12, **246 of the 259 old subject-heading names and 3 of the 4 geographic names found
  nothing in PubMed when quoted** (`"Old Name"[mh]`). PubMed only adds a "quoted phrase not
  found" warning. Inside an OR group the term is silently dropped; joined by AND, the clause finds 0.
- Some of these are among the most used headings in MEDLINE:
  - `"Questionnaires"[Mesh]` (renamed Surveys and Questionnaires, MeSH 2016) finds 0. The new
    heading holds 1,418,051 records; 761,965 of them do not have questionnaire* or survey* in
    the title or abstract.
  - `"Biological Markers"[Mesh]` (now Biomarkers, 2016) finds 0. Biomarkers holds 1,020,680
    records; 761,002 of them have neither "biological markers" nor biomarker* in the title or
    abstract.
  - `"Great Britain"[Mesh]` (now United Kingdom, 2017) finds 0. United Kingdom holds 418,425
    records; 295,590 (70.6%) of them have none of great britain, britain, british, uk or
    "united kingdom" in the title or abstract, and 225,025 (53.8%) also lack england, english,
    scotland, scottish, wales, welsh, "northern ireland", london and nhs.
- NLM also deleted 68 subject headings in these years. 58 of the deleted names now give 0 when
  quoted but map to a replacement when unquoted, for example `"Intensive Care"[mh]` (unquoted it maps
  to Critical Care), `"Food Habits"[mh]` (Feeding Behavior) and `"Receptor, Epidermal Growth
  Factor"[mh]` (ErbB Receptors, deleted for 2019). Seven deleted names map to nothing even
  unquoted, among them Intervention Studies and Pneumocystis jirovecii. Three (Lotus, Rhamnus,
  Salicaceae) are valid names again because later headings took them over.
- For MeSH 2019 NLM turned publication types from plural to singular. Twelve that PubMed uses
  give 0 under the plural, for example `"Congresses"[pt]` (Congress in 2019, Conference
  Proceedings since 2026), `"Personal Narratives"[pt]`, `"Portraits"[pt]` and `"Lectures"[pt]`.
- Names that still work: 11 renames that changed only letter case or a hyphen, and 2 old names
  (Eugenia and Pharmacological Phenomena) that NLM later gave to new, different headings. A quoted
  search for these finds records, but not the same set the old heading meant (see below).

pubmed-pt-check 0.1.5 knows every name in this file. `--fix` rewrites renamed names to the current
heading (also across later renames, for example Gypsies -> Roma (2016) -> Romani People (2026)).

## How we checked

1. **Renames.** NLM publishes each MeSH year as an RDF graph (`http://id.nlm.nih.gov/mesh/2015` ...
   `/2026`) at https://id.nlm.nih.gov/mesh/sparql. For each pair of years we joined descriptors on
   `meshv:identifier` and listed those whose English `rdfs:label` changed: 2016: 56, 2017: 34,
   2018: 105, 2019: 64 subject headings (TopicalDescriptor), plus geographic headings and
   publication types.
2. **Validation against NLM's own lists.** NLM's "Changed and Deleted MeSH Headings" pages list
   35 changed headings for 2017
   (https://www.nlm.nih.gov/pubs/techbull/nd16/nd16_mesh_headings_replaced.html), 106 for 2018
   (https://www.nlm.nih.gov/pubs/techbull/nd17/nd17_mesh_headings_replaced.html) and 64 for 2019
   (https://www.nlm.nih.gov/pubs/techbull/nd18/nd18_mesh_replaced_headings_2019.html). Our lists
   match them name for name: 2017 = our 34 + Great Britain; 2018 = our 105 + Cape Verde; 2019 =
   our 64. For 2016 we found no itemized NLM list (the 2016 MeSH bulletin gives only counts: 17
   descriptor terms replaced and 9 deleted). Our 2016 rows come from the RDF alone, and each was
   tested in PubMed one by one.
3. **Deletions.** The 2017 and 2018 pages list 42 and 7 deleted headings with their replacements.
   For 2016 and 2019 we listed subject headings present in one year's RDF and absent the next:
   10 for 2016 and 12 for 2019. Three of the 2019 ones became publication types, which leaves 9,
   matching NLM's 2019 count of 73 changed or deleted headings (64 + 9). Two of those 9 (Rhamnus,
   Salicaceae) had their names taken over by renamed headings, so the names still work.
4. **PubMed.** Every old name was searched quoted with `[mh]` (or `[pt]`) through E-utilities
   `esearch`, about 20 names per request joined by OR with `"Bacillota"[mh]` as a control, and we
   read `warninglist.quotedphrasesnotfound`. Deleted names were also searched unquoted to read
   PubMed's mapping in `translationset`. Current names were spot-checked (60) and all were
   recognized.
5. **Losses.** For the largest headings we counted records under the current heading that lack
   the words of the old name (and close variants) in title or abstract. That is what a
   strategy written as `("Old Name"[Mesh] OR old words[tiab])` loses today compared with the
   same strategy using the new heading. It is an upper bound for any real strategy that has
   other terms in the same block; we have not yet measured published strategies for 2016-2019.

## Losses for the largest headings (PubMed, 2026-11-12)

| Quoted old name (MeSH year it stopped) | Current heading | Records under current heading | Of those, without these title/abstract words | Words |
|---|---|---|---|---|
| Questionnaires (2016) | Surveys and Questionnaires | 1,418,051 | 761,965 | questionnaire*, survey* |
| Biological Markers (2016) | Biomarkers | 1,020,680 | 761,002 | "biological markers", biomarker* |
| Great Britain (2017) | United Kingdom | 418,425 | 295,590 | "great britain", britain, british, uk, "united kingdom" |
| Anoxia (2017) | Hypoxia | 97,588 | not counted | |
| Receptor, Epidermal Growth Factor (deleted 2019) | ErbB Receptors | 85,666 | 32,692 | egfr, "epidermal growth factor receptor*" |
| Bias (Epidemiology) (2018) | Bias | 81,473 | 57,858 | bias* |
| Intensive Care (deleted 2016) | Critical Care | 72,190 | 38,246 | "intensive care" |
| Cognitive Therapy (2019) | Cognitive Behavioral Therapy | 45,308 | 18,804 | cognitive AND (therap* OR treatment*) |
| Metabolic Syndrome X (2018) | Metabolic Syndrome | 44,508 | 6,246 | "metabolic syndrome", "syndrome x" |
| Individualized Medicine (2016) | Precision Medicine | 42,543 | 42,265 | "individualized medicine" |
| Cell Aging (2018) | Cellular Senescence | 34,025 | 31,651 | "cell aging", "cellular aging", "cell ageing", "cellular ageing" |
| Health Manpower (2019) | Health Workforce | 15,479 | 10,616 | manpower, workforce |

Example query for one row: `"United Kingdom"[mh] NOT ("great britain"[tiab] OR britain[tiab] OR
british[tiab] OR uk[tiab] OR "united kingdom"[tiab])` = 295,590. `Great Britain[mh]` unquoted maps
to "united kingdom"[MeSH Terms] (418,425); `"Great Britain"[Mesh]` and `"Great Britain"[MeSH
Terms]` are "quoted phrase not found".

On Great Britain: Ayiku et al. (Health Info Libr J 2017, doi:10.1111/hir.12187) noted that their
MEDLINE UK filter, validated in 2016 with `exp Great Britain/`, needed the new heading and that
the change did not alter the filter's performance. That was in Ovid. In PubMed the quoted old
form finds nothing. We found no earlier measurement of what quoted 2016-2019 heading names do in
PubMed (web searches on 2026-11-12).

## The lists

Old name -> current name. "Dead" means the quoted old name gave "quoted phrase not found" on
2026-11-12. Where a heading was renamed again later, the arrow points to today's name.

### 2016: 47 dead subject-heading renames (of 56)

Adenylate Cyclase -> Adenylyl Cyclases; Anesthesia, Intratracheal -> Anesthesia, Endotracheal;
Eating Disorders -> Feeding and Eating Disorders; Axis -> Axis, Cervical Vertebra; Biogenesis ->
Organelle Biogenesis; Cereals -> Edible Grain; Day Care -> Day Care, Medical; Diabetic Diet ->
Diet, Diabetic; Gypsies -> Romani People (Roma 2016-2025); Impulse Control Disorders -> Disruptive,
Impulse Control, and Conduct Disorders; Newspapers -> Newspapers as Topic; Nondirective Therapy ->
Person-Centered Psychotherapy (Person-Centered Therapy 2016-2018); Paraphilias -> Paraphilic
Disorders; Arachis hypogaea -> Arachis; Physician's Practice Patterns -> Practice Patterns,
Physicians'; Questionnaires -> Surveys and Questionnaires; Oryza sativa -> Oryza; Round Ligament ->
Round Ligament of Uterus; Secale cereale -> Secale; Sleep Disorders -> Sleep Wake Disorders; Space
Maintenance -> Space Maintenance, Orthodontic; Tumor Markers, Biological -> Biomarkers, Tumor; War ->
Warfare; Wing -> Wings, Animal; Biological Markers -> Biomarkers; Trimethoprim-Sulfamethoxazole
Combination -> Trimethoprim, Sulfamethoxazole Drug Combination; Klatskin's Tumor -> Klatskin Tumor;
Avena sativa -> Avena; Dentist's Practice Patterns -> Practice Patterns, Dentists'; Delirium,
Dementia, Amnestic, Cognitive Disorders -> Neurocognitive Disorders; Schizophrenia and Disorders
with Psychotic Features -> Schizophrenia Spectrum and Other Psychotic Disorders; Raloxifene ->
Raloxifene Hydrochloride; Adhatoda -> Justicia; Laser Therapy, Low-Level -> Low-Level Light
Therapy; Seedling -> Seedlings; Polygonum cuspidatum -> Fallopia japonica; Anellovirus ->
Anelloviridae; Hu Paraneoplastic Encephalomyelitis Antigens -> ELAV Proteins; Volar Plate ->
Palmar Plate; Nurse's Practice Patterns -> Practice Patterns, Nurses'; Individualized Medicine ->
Precision Medicine; Support Vector Machines -> Support Vector Machine; Health Services for
Transgendered Persons -> Health Services for Transgender Persons; Transgendered Persons ->
Transgender Persons; Dexmethylphenidate -> Dexmethylphenidate Hydrochloride; Ethnic Conflict ->
Ethnic Violence; Observational Study as Topic -> Observational Studies as Topic.

Still work: 7 case-only virus renames (for example Avian leukosis virus -> Avian Leukosis Virus).
**Reused names:** Eugenia -> Syzygium, and Pharmacological Phenomena -> Pharmacological and
Toxicological Phenomena and Processes (2016) -> Pharmacological and Toxicological Phenomena
(2018). Both old names were later given to new
headings (Eugenia, D000068856; Pharmacological Phenomena, D000069437; IDs from the 2026 RDF). A
pre-2016 search for `"Eugenia"[Mesh]` meant the heading now called Syzygium (cloves, for example,
were Eugenia caryophyllata); today it finds the new, narrower Eugenia heading instead.
`"Pharmacological Phenomena"[mh:noexp]` finds 167 records today.

Geographic: East Timor -> Timor-Leste (dead); Bosnia-Herzegovina -> Bosnia and Herzegovina
(still works).

### 2017: 34 dead subject-heading renames (all), plus Great Britain

Anoxia -> Hypoxia; B-Cell-Specific Activator Protein -> PAX5 Transcription Factor; Bicyclo
Compounds -> Bridged Bicyclo Compounds; Bicyclo Compounds, Heterocyclic -> Bridged Bicyclo
Compounds, Heterocyclic; Blueberry Plant -> Blueberry Plants; Body, Physical Appearance ->
Physical Appearance, Body; Bridged Compounds -> Bridged-Ring Compounds; Camels -> Camelus;
Chitinase -> Chitinases; Consumer Participation -> Community Participation; Dislocations -> Joint
Dislocations; Drug-Induced Liver Injury -> Chemical and Drug Induced Liver Injury; G0 Phase ->
Resting Phase, Cell Cycle; Gizzard -> Gizzard, Avian; Guanylate Kinase -> Guanylate Kinases;
Heterocyclic Compounds with 4 or More Rings -> Heterocyclic Compounds, 4 or More Rings; Institute of
Medicine (U.S.) -> National Academies of Science, Engineering, and Medicine, U.S., Health and
Medicine Division (via "(U.S.) Health and Medicine Division", 2017-2019); Lecithin Acyltransferase
Deficiency -> Lecithin Cholesterol Acyltransferase Deficiency; Microfilaria -> Microfilariae; Mild
Cognitive Impairment -> Cognitive Dysfunction; Obsessive Hoarding -> Hoarding; Odors -> Odorants;
Organic Anion Transport Polypeptide C -> Liver-Specific Organic Anion Transporter 1 (via Solute
Carrier Organic Anion Transporter Family Member 1b1, 2017-2018); Pharmacists' Aides -> Pharmacy
Technicians; Pneumocytes -> Alveolar Epithelial Cells; Polycyclic Hydrocarbons, Aromatic ->
Polycyclic Aromatic Hydrocarbons; Prostitution -> Sex Work; Psilocybine -> Psilocybin; Renal
Osteodystrophy -> Chronic Kidney Disease-Mineral and Bone Disorder; RNA Recognition Motif (RRM)
Proteins -> RNA Recognition Motif Proteins; Smilacina -> Maianthemum; Tooth Movement -> Tooth
Movement Techniques; Twist Transcription Factor -> Twist-Related Protein 1; Urginea -> Drimia.
Geographic: **Great Britain -> United Kingdom** (dead).

### 2018: 105 dead subject-heading renames (all), plus Cape Verde

Non-CD headings: 6-Mercaptopurine -> Mercaptopurine; Advanced Glycosylation End Product-Specific
Receptor -> Receptor for Advanced Glycation End Products; Alismatidae -> Alismatales; Angiosperms ->
Magnoliopsida; Antigen Peptide Transporter-1 / -2 -> ATP Binding Cassette Transporter, Subfamily
B, Member 2 / 3; Antigens, Thy-1 -> Thy-1 Antigens; Architecture as Topic -> Architecture; Beetles
-> Coleoptera; Bias (Epidemiology) -> Bias; Cell Aging -> Cellular Senescence; Cell Phones -> Cell
Phone; Comoviridae -> Secoviridae; Cycadophyta -> Cycadopsida; Dictionaries, Classical / Dental /
Pharmaceutic -> ... as Topic; Dictionaries, Polyglot -> (a catalog publication type since 2019);
Dissertations, Academic as Topic -> Academic Dissertations as Topic; DNA (Cytosine-5-)-
Methyltransferase -> DNA (Cytosine-5-)-Methyltransferases; Drug-Induced Liver Injury, Chronic ->
Chemical and Drug Induced Liver Injury, Chronic; Electronic Cigarettes -> Electronic Nicotine
Delivery Systems; Epidemiologic Study Characteristics as Topic -> Epidemiologic Study
Characteristics; Fluticasone Propionate, Salmeterol Xinafoate Drug Combination ->
Fluticasone-Salmeterol Drug Combination; Formularies, Dental -> Formularies, Dental as Topic; Giant
Lymph Node Hyperplasia -> Castleman Disease; Glycosylation End Products, Advanced -> Glycation End
Products, Advanced; Hemocyanin -> Hemocyanins; Hemoglobin A, Glycosylated -> Glycated Hemoglobin
(Glycated Hemoglobin A 2018-2022); Heterozygote Detection -> Genetic Carrier Screening; Human
Engineering -> Ergonomics; Hydrogel -> Hydrogel, Polyethylene Glycol Dimethacrylate; Insects ->
Insecta; Ketogenic Diet -> Diet, Ketogenic; Manuscripts, Medical -> Manuscripts, Medical as Topic;
Medicine in Art -> Medicine in the Arts; Metabolic Syndrome X -> Metabolic Syndrome; Metrizoate ->
Metrizoic Acid; Motion Pictures as Topic -> Motion Pictures; NADPH Oxidase -> NADPH Oxidases;
National Institute of Neurological Disorders and Stroke -> ... (U.S.); P-Glycoprotein -> ATP
Binding Cassette Transporter, Subfamily B, Member 1; P-Glycoproteins -> ATP Binding Cassette
Transporter, Subfamily B; Pharmacological and Toxicological Phenomena and Processes ->
Pharmacological and Toxicological Phenomena; Pinnipedia -> Caniformia; Psychological Phenomena and
Processes -> Psychological Phenomena; Sexual Minorities -> Sexual and Gender Minorities;
Sodium-Hydrogen Antiporter -> Sodium-Hydrogen Exchangers; Sphincterotomy, Transhepatic ->
Sphincterotomy, Transduodenal; Sublimation -> Sublimation, Psychological; Theales -> Ericales;
Tracheobionta -> Tracheophyta; Vetiveria -> Chrysopogon.

52 "Antigens, CD..." headings: Antigens, CD4 -> CD4 Antigens; CD8 -> CD8 Antigens; CD3 -> CD3
Complex; CD45 -> Leukocyte Common Antigens; CD14 -> Lipopolysaccharide Receptors; CD44 -> Hyaluronan
Receptors; CD95 -> fas Receptor; CD29 -> Integrin beta1; CD31 -> Platelet Endothelial Cell Adhesion
Molecule-1; CD38 -> ADP-ribosyl Cyclase 1; CD274 -> B7-H1 Antigen; CD80 / CD86 -> B7-1 / B7-2
Antigen; CD9 / CD53 / CD63 / CD81 / CD151 -> Tetraspanin 29 / 25 / 30 / 28 / 24; CD147 -> Basigin;
CD27 / CD137 -> Tumor Necrosis Factor Receptor Superfamily, Member 7 / 9; CD70 -> CD27 Ligand; CD30
-> Ki-1 Antigen; CD15 -> Lewis X Antigen; CD99 -> 12E7 Antigen; CD46 -> Membrane Cofactor Protein;
CD43 -> Leukosialin; CD82 -> Kangai-1 Protein; CD164 -> Endolyn; CD98 (and Heavy Chain, Light
Chains) -> Fusion Regulatory Protein-1 (1, Heavy Chain; 1, Light Chains); and "Antigens, CDn" ->
"CDn Antigen(s)" for CD2, CD5, CD11, CD11a, CD11b, CD11c, CD13, CD18, CD24, CD28, CD36, CD40, CD47,
CD55, CD56, CD57, CD58, CD59, CD79, CD146. The full table is in pubmed_pt_check.py.

Geographic: Cape Verde -> Cabo Verde (dead).

### 2019: 60 dead subject-heading renames (of 64)

46, XY Disorders of Sex Development -> Disorder of Sex Development, 46,XY; Arteritis Virus,
Equine -> Equartevirus; Astragalus membranaceus -> Astragalus propinquus; Atorvastatin Calcium ->
Atorvastatin; 13 ATP-binding cassette names with "Sub-Family" -> "Subfamily" (for example ATP
Binding Cassette Transporter, Sub-Family B -> ATP Binding Cassette Transporter, Subfamily B: the
hyphen-to-one-word change is enough to break the quoted name); ATP Binding Cassette Subfamily B
Member 11 -> ATP Binding Cassette Transporter, Subfamily B, Member 11; Automatic Data Processing ->
Electronic Data Processing; Canola Oil -> Rapeseed Oil; Catalogs, Commercial / Drug / Union -> ...
as Topic; Cinacalcet Hydrochloride -> Cinacalcet; **Cognitive Therapy -> Cognitive Behavioral
Therapy**; Dictionaries, Chemical / Medical -> ... as Topic; Dispensatories -> Dispensatories as
Topic; Dose Fractionation -> Dose Fractionation, Radiation; Dose Hypofractionation -> Radiation
Dose Hypofractionation; Flacourtiaceae -> Salicaceae; Formularies, Homeopathic / Hospital -> ... as
Topic; Frangula -> Rhamnus; **Health Manpower -> Health Workforce**; Lindane ->
Hexachlorocyclohexane; Loteae -> Lotus; Medical Missions, Official -> Medical Missions;
**Mesenchymal Stromal Cells -> Mesenchymal Stem Cells**; Multiple Personality Disorder ->
Dissociative Identity Disorder; Myristica fragrans -> Myristica; Nurses' Aides -> Nursing
Assistants; Person-Centered Therapy -> Person-Centered Psychotherapy; Pharmacopoeias, Homeopathic ->
... as Topic; Polyacetylenes -> Polyynes; Records as Topic -> Records; Risedronate Sodium ->
Risedronic Acid; Scopolamine Hydrobromide -> Scopolamine; **Sedentary Lifestyle -> Sedentary
Behavior**; Slavery -> Enslavement; Slaves -> Enslaved Persons; Solute Carrier Organic Anion
Transporter Family Member 1b1 -> Liver-Specific Organic Anion Transporter 1; Tissue Conditioning
(Dental) -> Tissue Conditioning, Dental; Tobacco Use Cessation Products -> Tobacco Use Cessation
Devices; Universal Coverage -> Universal Health Insurance; Value-Based Insurance -> Value-Based
Health Insurance; Vegetable Proteins -> Plant Proteins, Dietary. Also dead, but now catalog
publication types rather than headings: Catalogs, Booksellers'; Catalogs, Publishers';
Dictionaries, Polyglot as Topic (not in the checker).

Still work: Classical swine fever virus (case only), Salt-Tolerance, Tetraspanin-25,
Tetraspanin-29 (hyphen dropped).

### Deleted headings

Quoted, every deleted name below gives "quoted phrase not found". Unquoted, PubMed maps it to the
heading after the arrow (checked one by one in `translationset`).

- 2016: Intensive Care -> Critical Care; Mental Disorders Diagnosed in Childhood ->
  Neurodevelopmental Disorders; Black Pepper -> Piper nigrum; Asclepiadaceae -> Apocynaceae;
  Acanthopanax -> Eleutherococcus; Pharmacological Processes -> Pharmacological Phenomena.
- 2017 (NLM list of 42): Food Habits -> Feeding Behavior; Metabolic Phenomena -> Metabolism;
  Tetrachlorodibenzodioxin -> Polychlorinated Dibenzodioxins; Agavaceae -> Asparagaceae;
  Physicochemical Phenomena and Physicochemical Processes -> Chemical Phenomena; and 34 "...
  Processes" headings -> "... Phenomena" (for example Physiological Processes -> Physiological
  Phenomena; Nutrition Processes -> Nutritional Physiological Phenomena; Digestive System
  Processes -> Digestive System Physiological Phenomena). Lotus was deleted for 2017 and is a
  heading again since 2019 (Loteae -> Lotus), so it works.
- 2018 (NLM list of 7): Anopheles gambiae -> Anopheles; Cecropiaceae -> Urticaceae; Cobra Venoms ->
  Elapid Venoms; Endamoeba histolytica -> Entamoeba histolytica; Gymnosperms -> Cycadopsida;
  Pseudocholinesterase -> Butyrylcholinesterase; Secernentea -> Nematoda.
- 2019: **Receptor, Epidermal Growth Factor -> ErbB Receptors**; Apium graveolens -> Apium;
  Myrsinaceae -> Primulaceae; Sterculiaceae -> Malvaceae; Immunochromatography -> Chromatography,
  Affinity; Pteridophyta -> Tracheophyta. (Rhamnus and Salicaceae were deleted too, but renamed
  headings took over their names, so they work.)

Deleted names that PubMed maps to nothing, quoted or not: Vertebrate Viruses, Intervention
Studies, Health Food, Pygeum (2016); Functional Behavior, Psychology (2017; NLM names Behavior as
the replacement); Pneumocystis jirovecii (2017; NLM's 2017 list gives Pneumocystis carinii as the
replacement; `Pneumocystis jirovecii[mh]` unquoted gives 0 with "jirovecii" not found, and
`"Pneumocystis carinii"[mh]` finds 2,300 records); Emergency Police Dispatcher (2019).

### Publication types, MeSH 2019 (plural to singular)

Dead plural -> current singular, for the 12 that PubMed recognizes in the singular: Addresses ->
Address; Congresses -> Congress -> Conference Proceedings (2026); Government Publications ->
Government Document -> Government Publication (2020; discontinued); Lectures -> Lecture; Legal
Cases -> Legal Case (discontinued); Personal Narratives -> Personal Narrative; Portraits ->
Portrait (discontinued); Collected Works -> Collected Work; Popular Works -> Popular Work;
Manuscripts -> Manuscript; Pictorial Works -> Pictorial Work; Photographs -> Photograph. NLM's
"MEDLINE Data Changes - 2019" names the first seven as the types used for MEDLINE indexing. The
other plural types renamed for 2019 (Book Reviews, Meeting Abstracts, Periodicals, Patents,
Diaries, Academic Dissertations, Humor -> Wit and Humor, and about 40 catalog-only types) give 0
under both names in PubMed.

## Limits

- One day of PubMed checks. PubMed can change its phrase index; rerun with `pubmed_pt_check.py
  --live`.
- The loss column counts records that lack certain words in title or abstract. It is not a
  measure of any particular published search. A strategy that also has other synonyms, or
  explodes a broader heading, loses less.
- 2016 rows rest on the RDF comparison and the PubMed test, not on an NLM list. NLM's 2016 count
  (17 replaced) is far below our 56; we have not found out how NLM counted.
- We did not check the 7 case-only 2016 virus renames one by one (one was tested and works).
- The reused-name rows (Eugenia, Pharmacological Phenomena) are not flagged by the checker,
  because the names are valid today.

Reproduce: the queries in this file are plain E-utilities `esearch` calls
(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=0&term=...`)
and SPARQL queries against https://id.nlm.nih.gov/mesh/sparql as described above.
