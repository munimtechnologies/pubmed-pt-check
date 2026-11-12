#!/usr/bin/env python3
# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# Licensed under the Apache License, Version 2.0 (Apache-2.0). See LICENSE.
# Made with AI agents working in MV2's name.
"""pubmed-pt-check: find PubMed publication types and MeSH headings that PubMed no longer
recognizes under the name a search uses.

NLM renamed four PubMed publication types, in two MeSH years: "Retraction of Publication" is
now "Retraction Notice" (MeSH 2025, NLM Tech Bull 2024 Nov-Dec;(461):e4); "Congress" is now
"Conference Proceedings" and "Consensus Development Conference" is now "Consensus Statement"
(MeSH 2026, NLM Tech Bull 2026 Jan-Feb;(468):e6); "Classical Article" is now "Seminal Article"
(MeSH 2026, found by comparing NLM's MeSH 2025 and 2026 RDF). PubMed's article-type filters
followed in March 2026 (NLM Tech Bull 2026 Mar-Apr;(469):e1). Checked against E-utilities on
2026-11-11/12, the old names no longer match anything in a [pt] search: PubMed treats the term as
an empty set and only adds a "quoted phrase not found" warning. Since 0.1.4 the table also has
four MeSH 2020 renames of publication types that PubMed uses ("Evaluation Studies" is now
"Evaluation Study", "Validation Studies" is "Validation Study", "Government Document" is
"Government Publication", "Webcasts" is "Webcast"); their old names give 0 too, quoted or not.

- alone or joined with AND: the search (or AND clause) finds 0 records;
- joined with OR: the term is dropped and the rest of the OR group runs, so the result silently
  misses every record of the renamed type;
- after NOT: the term is dropped, so nothing is excluded.

Seventeen more types were discontinued: older citations keep them and they are still searchable,
but new citations no longer get them.

MeSH headings behave the same way. PubMed maps an old heading name to the new one only when the
term is not in quotes; a quoted old name ("..."[mh], [mesh], [majr], with or without :noexp)
finds nothing. 0.1.3 listed every heading NLM renamed in MeSH 2024, 2025 and 2026 (89). 0.1.4
adds MeSH 2020 to 2023 (found the same way, by comparing NLM's yearly MeSH RDF graphs at
id.nlm.nih.gov/mesh/sparql; the 2020 list matches NLM's own "Changed and Deleted MeSH
Headings - 2020" bulletin) and eight names of headings NLM deleted and replaced, where PubMed
maps the unquoted old name to the replacement (for example Cervical Intraepithelial Neoplasia, deleted for
2023: unquoted it maps to Uterine Cervical Dysplasia; quoted it finds nothing). On 2026-11-12
every quoted old name in the table gave 0 records in PubMed with "quoted phrase not found", and
every current name was recognized. Renames that only changed letter case, or dropped a comma,
a hyphen or a pair of parentheses between words, still work and are not listed. Turning "(X)" into ", X" is NOT harmless:
"Neural Networks (Computer)"[mh] and 28 more such 2020 names give 0. See MESH-RENAMES.md and
MESH-RENAMES-2020-2023.md.

This script reads search strings, saved strategies or source code, finds every term tagged [pt],
[ptyp], [Publication Type], [mh], [mesh], [majr] or [MeSH Terms], and reports renamed, deleted
and discontinued names with the effect that the surrounding Boolean operator has. --fix rewrites
renamed names; --live asks PubMed itself (E-utilities esearch) whether each publication type and
each quoted MeSH heading in the input is recognized today, which also catches renames this script
does not know about yet.

    python pubmed_pt_check.py '"Cochrane Database Syst Rev"[ta] NOT "Retraction of Publication"[pt]'
    python pubmed_pt_check.py --live search_strategy.txt
    python pubmed_pt_check.py --fix '("Pregnant Women"[Mesh] OR pregnan*[tiab])'

Exit codes: 0 = nothing renamed, deleted or unrecognized; 1 = at least one renamed or
unrecognized publication type or quoted MeSH heading, or a deleted heading; 2 = bad input or a
failed --live lookup. Python 3.8+, standard library only; --live makes read-only HTTPS GETs to
eutils.ncbi.nlm.nih.gov (no API key).
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

VERSION = "0.1.4"
MAILTO = "mv2@munimtech.com"
TOOL = "pubmed-pt-check"
UA = "pubmed-pt-check/%s (MV2, Munim, Inc.; mailto:%s)" % (VERSION, MAILTO)
ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
SOURCE = ("NLM Technical Bulletin 2019 Nov-Dec (Changed and Deleted MeSH Headings - 2020), "
          "2024 Nov-Dec (461):e4, 2026 Jan-Feb (468):e6 and 2026 Mar-Apr (469):e1, "
          "https://www.nlm.nih.gov/pubs/techbull/ma26/ma26_pubmed_update_MeSH_changes.html; "
          "MeSH RDF yearly graphs 2019-2026, https://id.nlm.nih.gov/mesh/sparql (compared "
          "2026-11-12)")


def key(name):
    """Comparison key for a publication type name: lower case, no dots, single spaces."""
    return " ".join(str(name or "").replace(".", "").lower().split())


RENAMED = {
    key("Retraction of Publication"): "Retraction Notice",
    key("Congress"): "Conference Proceedings",
    key("Consensus Development Conference"): "Consensus Statement",
    key("Classical Article"): "Seminal Article",
    # MeSH 2020 (MeSH RDF 2019 vs 2020). Only types that PubMed citations carry are listed: NLM
    # renamed 13 more catalog-only types for 2020 (Maps, Programs, Essays, ...), and neither
    # their old nor their new names match anything in PubMed.
    key("Evaluation Studies"): "Evaluation Study",
    key("Validation Studies"): "Validation Study",
    key("Government Document"): "Government Publication",
    key("Webcasts"): "Webcast",
}
# MeSH year of each rename (NLM Technical Bulletins 461:e4 and 468:e6; Classical Article from
# the MeSH 2025 vs 2026 RDF, D016419; the 2020 renames from the MeSH 2019 vs 2020 RDF).
RENAMED_YEAR = {
    key("Retraction of Publication"): 2025,
    key("Congress"): 2026,
    key("Consensus Development Conference"): 2026,
    key("Classical Article"): 2026,
    key("Evaluation Studies"): 2020,
    key("Validation Studies"): 2020,
    key("Government Document"): 2020,
    key("Webcasts"): 2020,
}
DISCONTINUED = {key(n) for n in (
    "Autobiography", "Bibliography", "Clinical Conference",
    "Consensus Development Conference, NIH", "Dictionary", "Directory",
    "Government Publication", "Interactive Tutorial", "Legal Case", "Legislation",
    "Newspaper Article", "Overall", "Periodical Index", "Portrait",
    "Scientific Integrity Review", "Seminal Article", "Technical Report")}

# Renamed MeSH headings (descriptors): (old name, current name, MeSH year of the rename).
# Found by comparing the English rdfs:label of every descriptor in NLM's yearly MeSH RDF graphs
# (2019 vs 2020 through 2025 vs 2026). On 2026-11-12 every quoted old name below gave 0 records
# in PubMed with "quoted phrase not found", and every current name was recognized.
# A descriptor renamed twice maps both old names to its current name. Names that NLM renamed
# and later restored (Xenarthra, Fermented Foods, Extreme Cold, Pimenta, Alaska Natives) are
# current again and are not listed; only the in-between names are.
MESH_RENAMES = [
    # MeSH 2020. NLM's bulletin lists 93 changed headings: the 87 below; 2 case-only renames
    # that still work (Copper-transporting ATPases; MTOR Associated Protein, LST8 Homolog); 3
    # names NLM restored later (Extreme Cold, Fermented Foods, Xenarthra); and National Health
    # Planning Information Center (U.S.), left out because PubMed finds neither name.
    ("Abstracting and Indexing as Topic", "Abstracting and Indexing", 2020),
    ("Advertising as Topic", "Advertising", 2020),
    ("Allethrin", "Allethrins", 2020),
    ("Anterior Cerebellar Commissure", "Anterior Commissure, Brain", 2020),
    ("Aspirations (Psychology)", "Aspirations, Psychological", 2020),
    ("Autobiography as Topic", "Autobiographies as Topic", 2020),
    ("Bibliography as Topic", "Bibliographies as Topic", 2020),
    ("Biography as Topic", "Biographies as Topic", 2020),
    ("Bornanes", "Camphanes", 2020),
    ("Catchment Area (Health)", "Catchment Area, Health", 2020),
    ("Centers for Disease Control and Prevention (U.S.)",
     "Centers for Disease Control and Prevention, U.S.", 2020),
    ("Centers for Medicare and Medicaid Services (U.S.)",
     "Centers for Medicare and Medicaid Services, U.S.", 2020),
    ("Cercopithecus aethiops", "Chlorocebus aethiops", 2020),
    ("Codependency (Psychology)", "Codependency, Psychological", 2020),
    ("Conditioning (Psychology)", "Conditioning, Psychological", 2020),
    ("Conflict (Psychology)", "Conflict, Psychological", 2020),
    ("Confounding Factors (Epidemiology)", "Confounding Factors, Epidemiologic", 2020),
    ("Countertransference (Psychology)", "Countertransference", 2020),
    ("Critical Period (Psychology)", "Critical Period, Psychological", 2020),
    ("Decapoda (Crustacea)", "Decapoda", 2020),
    ("Denial (Psychology)", "Denial, Psychological", 2020),
    ("Dependency (Psychology)", "Dependency, Psychological", 2020),
    ("Diary as Topic", "Diaries as Topic", 2020),
    ("Discrimination (Psychology)", "Discrimination, Psychological", 2020),
    ("Displacement (Psychology)", "Displacement, Psychological", 2020),
    ("Diterpenes, Abietane", "Abietanes", 2020),
    ("Dolichol", "Dolichols", 2020),
    ("Duplicate Publication as Topic", "Duplicate Publications as Topic", 2020),
    ("Early Intervention (Education)", "Early Intervention, Educational", 2020),
    ("Earth (Planet)", "Earth, Planet", 2020),
    ("Exhibits as Topic", "Exhibitions as Topic", 2020),
    ("Extraversion (Psychology)", "Extraversion, Psychological", 2020),
    ("Fetishism (Psychiatric)", "Fetishism, Psychiatric", 2020),
    ("Focused Assessment with Sonography of Trauma",
     "Focused Assessment with Sonography for Trauma", 2020),
    ("Generalization (Psychology)", "Generalization, Psychological", 2020),
    ("Glycophorin", "Glycophorins", 2020),
    ("Handling (Psychology)", "Handling, Psychological", 2020),
    ("Healthy Diet", "Diet, Healthy", 2020),
    ("Helix (Snails)", "Helix, Snails", 2020),
    ("Hypersomnolence, Idiopathic", "Idiopathic Hypersomnia", 2020),
    ("Identification (Psychology)", "Identification, Psychological", 2020),
    ("Imagery (Psychotherapy)", "Imagery, Psychotherapy", 2020),
    ("Imprinting (Psychology)", "Imprinting, Psychological", 2020),
    ("Infection", "Infections", 2020),
    ("Inhibition (Psychology)", "Inhibition, Psychological", 2020),
    ("Introversion (Psychology)", "Introversion, Psychological", 2020),
    ("Knowledge of Results (Psychology)", "Knowledge of Results, Psychological", 2020),
    ("L Cells (Cell Line)", "L Cells", 2020),
    ("Latency Period (Psychology)", "Latency Period, Psychological", 2020),
    ("Learning Disorders", "Learning Disabilities", 2020),
    ("Lewis Blood-Group System", "Lewis Blood Group Antigens", 2020),
    ("Literature Based Discovery", "Knowledge Discovery", 2020),
    ("Macedonia (Republic)", "Republic of North Macedonia", 2020),
    ("Mainstreaming (Education)", "Mainstreaming, Education", 2020),
    ("Mercury (Planet)", "Mercury, Planet", 2020),
    ("Mitochondrial Degradation", "Mitophagy", 2020),
    ("Moraxella (Branhamella) catarrhalis", "Moraxella catarrhalis", 2020),
    ("Moraxella (Moraxella) bovis", "Moraxella bovis", 2020),
    ("National Academies of Science, Engineering, and Medicine (U.S.) Health and Medicine "
     "Division", "National Academies of Science, Engineering, and Medicine, U.S., Health and "
     "Medicine Division", 2020),
    ("National Academy of Sciences (U.S.)", "National Academy of Sciences, U.S.", 2020),
    ("National Center for Health Care Technology (U.S.)",
     "National Center for Health Care Technology, U.S.", 2020),
    ("National Center for Health Statistics (U.S.)",
     "National Center for Health Statistics, U.S.", 2020),
    ("National Institute for Occupational Safety and Health (U.S.)",
     "National Institute for Occupational Safety and Health, U.S.", 2020),
    ("Neural Networks (Computer)", "Neural Networks, Computer", 2020),
    ("Nucleopolyhedrovirus", "Nucleopolyhedroviruses", 2020),
    ("Nurseries", "Nurseries, Infant", 2020),
    ("Outcome and Process Assessment (Health Care)",
     "Outcome and Process Assessment, Health Care", 2020),
    ("Outcome Assessment (Health Care)", "Outcome Assessment, Health Care", 2020),
    ("Power (Psychology)", "Power, Psychological", 2020),
    ("Practice (Psychology)", "Practice, Psychological", 2020),
    ("Process Assessment (Health Care)", "Process Assessment, Health Care", 2020),
    ("Programmed Instruction as Topic", "Programmed Instructions as Topic", 2020),
    ("Recognition (Psychology)", "Recognition, Psychology", 2020),
    ("Regression (Psychology)", "Regression, Psychology", 2020),
    ("Reinforcement (Psychology)", "Reinforcement, Psychology", 2020),
    ("Rejection (Psychology)", "Rejection, Psychology", 2020),
    ("Retention (Psychology)", "Retention, Psychology", 2020),
    ("Set (Psychology)", "Set, Psychology", 2020),
    ("Shadowing (Histology)", "Shadowing Technique, Histology", 2020),
    ("Skates (Fish)", "Skates, Fish", 2020),
    ("SOS Response (Genetics)", "SOS Response, Genetics", 2020),
    ("Street Drugs", "Illicit Drugs", 2020),
    ("Study Guide as Topic", "Study Guides as Topic", 2020),
    ("Swaziland", "Eswatini", 2020),
    ("Transfer (Psychology)", "Transfer, Psychology", 2020),
    ("Transference (Psychology)", "Transference, Psychology", 2020),
    ("Unconscious (Psychology)", "Unconscious, Psychology", 2020),
    # MeSH 2020, deleted and replaced (NLM bulletin; PubMed maps the unquoted name)
    ("Cascara", "Rhamnus", 2020),
    ("Coniferophyta", "Tracheophyta", 2020),
    ("Punicaceae", "Lythraceae", 2020),
    ("Taxodiaceae", "Cupressaceae", 2020),
    # MeSH 2021
    ("Aldehyde Dehydrogenase 1", "Aldehyde Dehydrogenase 1 Family", 2021),
    ("Bonding, Human-Pet", "Human-Animal Bond", 2021),
    ("Respiratory Distress Syndrome, Adult", "Respiratory Distress Syndrome", 2021),
    ("RNA Replicase", "RNA-Dependent RNA Polymerase", 2021),
    ("Social Distance", "Psychological Distance", 2021),
    ("Clostridium difficile", "Clostridioides difficile", 2021),
    ("Pectobacterium chrysanthemi", "Dickeya chrysanthemi", 2021),
    ("Mentally Disabled Persons", "Persons with Intellectual Disabilities", 2021),
    ("Debaromyces", "Debaryomyces", 2021),
    ("Site-Specific DNA-Methyltransferase (Cytosine-N(4)-Specific)",
     "Site-Specific DNA-Methyltransferase (Cytosine-N4-Specific)", 2021),
    ("Infantile Apparent Life-Threatening Event", "Brief, Resolved, Unexplained Event", 2021),
    # MeSH 2022
    ("Fermented Foods and Beverages", "Fermented Foods", 2022),
    ("Angiopoietin-like 4 Protein", "Angiopoietin-Like Protein 4", 2022),
    ("Environmental DNA", "DNA, Environmental", 2022),
    ("American Natives", "American Indian or Alaska Native", 2022),
    ("Dental Models", "Models, Dental", 2022),
    ("Echidna", "Tachyglossidae", 2022),
    ("Cingulata", "Xenarthra", 2022),
    ("Ethnic Groups", "Ethnicity", 2022),
    ("Hispanic Americans", "Hispanic or Latino", 2022),
    ("Housekeeping", "Household Work", 2022),
    ("Immunosuppression", "Immunosuppression Therapy", 2022),
    ("Insectivora", "Eulipotyphla", 2022),
    ("Purpura, Schoenlein-Henoch", "IgA Vasculitis", 2022),
    ("Kinesin", "Kinesins", 2022),
    ("Genus Pimenta", "Pimenta", 2022),
    ("African Continental Ancestry Group", "Black People", 2022),
    ("European Continental Ancestry Group", "White People", 2022),
    ("Asian Continental Ancestry Group", "Asian People", 2022),
    ("Oceanic Ancestry Group", "Native Hawaiian or Pacific Islander", 2022),
    ("Continental Population Groups", "Racial Groups", 2022),
    ("Anabaena flos-aquae", "Dolichospermum flos-aquae", 2022),
    ("Casein Kinase Iepsilon", "Casein Kinase 1 epsilon", 2022),
    ("Translational Medical Research", "Translational Research, Biomedical", 2022),
    # MeSH 2023
    ("Lactobacillus paracasei", "Lacticaseibacillus paracasei", 2023),
    ("Lactobacillus salivarius", "Ligilactobacillus salivarius", 2023),
    ("Lactobacillus sakei", "Latilactobacillus sakei", 2023),
    ("Xanthorrhoeaceae", "Asphodelaceae", 2023),
    ("Alaskan Natives", "Alaska Natives", 2023),
    ("Whole Exome Sequencing", "Exome Sequencing", 2023),
    ("Health Disparity, Minority and Vulnerable Populations",
     "Health Disparate Minority and Vulnerable Populations", 2023),
    ("Amputation", "Amputation, Surgical", 2023),
    ("Aneurysm, Dissecting", "Aortic Dissection", 2023),
    ("Asian Americans", "Asian", 2023),
    ("African Americans", "Black or African American", 2023),
    ("Inuits", "Inuit", 2023),
    ("Glycated Hemoglobin A", "Glycated Hemoglobin", 2023),
    ("Hantavirus", "Orthohantavirus", 2023),
    ("Homeless Persons", "Ill-Housed Persons", 2023),
    ("Lactobacillus casei", "Lacticaseibacillus casei", 2023),
    ("Serotonin Uptake Inhibitors", "Selective Serotonin Reuptake Inhibitors", 2023),
    ("RNA, Guide", "RNA, Guide, Kinetoplastida", 2023),
    ("Lycopersicon esculentum", "Solanum lycopersicum", 2023),
    ("Reconstructive Surgical Procedures", "Plastic Surgery Procedures", 2023),
    ("Blacks", "Black People", 2023),
    ("Whites", "White People", 2023),
    ("Asians", "Asian People", 2023),
    ("American Native Continental Ancestry Group", "American Indian or Alaska Native", 2023),
    ("SARS Virus", "Severe acute respiratory syndrome-related coronavirus", 2023),
    ("Lactobacillus brevis", "Levilactobacillus brevis", 2023),
    ("Lactobacillus fermentum", "Limosilactobacillus fermentum", 2023),
    ("Lactobacillus reuteri", "Limosilactobacillus reuteri", 2023),
    ("Lactobacillus rhamnosus", "Lacticaseibacillus rhamnosus", 2023),
    ("Alien Hand Syndrome", "Alien Limb Phenomenon", 2023),
    ("Waste Water", "Wastewater", 2023),
    ("Far East", "Asia, Eastern", 2023),
    # MeSH 2023, deleted (PubMed maps the unquoted name to the heading given here)
    ("American Indians or Alaska Natives", "American Indian or Alaska Native", 2023),
    ("Cervical Intraepithelial Neoplasia", "Uterine Cervical Dysplasia", 2023),
    # MeSH 2024
    ("Cyclophilin D", "Peptidyl-Prolyl Isomerase F", 2024),
    ("Tyrosine Protein Kinase Inhibitors", "Tyrosine Kinase Inhibitors", 2024),
    ("Phaeophyta", "Phaeophyceae", 2024),
    ("Biopterin", "Biopterins", 2024),
    ("Castor Bean", "Ricinus communis", 2024),
    ("2,5-Dimethoxy-4-Methylamphetamine", "DOM 2,5-Dimethoxy-4-Methylamphetamine", 2024),
    ("Influenzavirus C", "Gammainfluenzavirus", 2024),
    ("Soybeans", "Glycine max", 2024),
    ("Tobacco", "Nicotiana", 2024),
    ("Russell's Viper", "Daboia", 2024),
    ("Peas", "Pisum sativum", 2024),
    ("Lettuce", "Lactuca", 2024),
    ("Chicory", "Cichorium intybus", 2024),
    ("Ginger", "Zingiber officinale", 2024),
    ("Milk Thistle", "Silybum marianum", 2024),
    ("Influenzavirus A", "Alphainfluenzavirus", 2024),
    ("Influenzavirus B", "Betainfluenzavirus", 2024),
    ("Monkeypox", "Mpox, Monkeypox", 2024),
    ("Lysosome-Associated Membrane Glycoproteins", "Lysosomal Membrane Proteins", 2024),
    ("Extreme Cold Weather", "Extreme Cold", 2024),
    ("Hyalinosis, Systemic", "Hyaline Fibromatosis Syndrome", 2024),
    # MeSH 2024, deleted (PubMed maps the unquoted name to the heading given here)
    ("Extreme Hot Weather", "Extreme Heat", 2024),
    # MeSH 2025
    ("Abortion, Criminal", "Abortion, Illegal", 2025),
    ("Network Meta-Analysis", "Network Meta-Analysis as Topic", 2025),
    ("Obesity, Maternal", "Pregnancy in Obesity", 2025),
    ("Medicine, Persian", "Medicine, Iranian Traditional", 2025),
    ("Channa punctatus", "Channa punctata", 2025),
    ("Commitment of Mentally Ill", "Commitment of Persons with Psychiatric Disorders", 2025),
    ("Communication Aids for Disabled", "Communication Devices for People with Disabilities",
     2025),
    ("Dental Care for Disabled", "Dental Care for Persons with Disabilities", 2025),
    ("Education of Intellectually Disabled", "Education of Persons with Intellectual Disabilities",
     2025),
    ("Health Care Facilities, Manpower, and Services",
     "Health Care Facilities Workforce and Services", 2025),
    ("Disabled Persons", "Persons with Disabilities", 2025),
    ("Surrogate Mothers", "Gestational Carriers", 2025),
    ("Trityl Compounds", "Triphenylmethyl Compounds", 2025),
    ("Urodela", "Caudata", 2025),
    ("Lymphatic Vessel Tumors", "Neoplasm, Lymphatic Tissue", 2025),
    ("Fibromatosis, Aggressive", "Desmoid Tumors", 2025),
    ("Condoms, Female", "Single-Use Internal Condom", 2025),
    ("Persons With Hearing Impairments", "Persons with Hearing Disabilities", 2025),
    ("Visually Impaired Persons", "Persons with Visual Disabilities", 2025),
    ("Disabled Children", "Children with Disabilities", 2025),
    ("Persons with Mental Disabilities", "Persons with Intellectual Disabilities", 2025),
    ("Mentally Ill Persons", "Persons with Psychiatric Disorders", 2025),
    ("Pregnant Women", "Pregnant People", 2025),
    ("Mental Retardation, X-Linked", "X-Linked Intellectual Disability", 2025),
    ("Native Hawaiian or Other Pacific Islander", "Native Hawaiian or Pacific Islander", 2025),
    ("Mpox (monkeypox)", "Mpox, Monkeypox", 2025),
    ("Sex Reassignment Procedures", "Gender-Affirming Procedures", 2025),
    ("Sex Reassignment Surgery", "Gender-Affirming Surgery", 2025),
    ("Education of Visually Disabled", "Education of Persons with Visual Disabilities", 2025),
    ("Education of Hearing Disabled", "Education of Persons with Hearing Disabilities", 2025),
    # MeSH 2026
    ("Clostridiales", "Eubacteriales", 2026),
    ("Firmicutes", "Bacillota", 2026),
    ("Lactobacillus pentosus", "Lactiplantibacillus pentosus", 2026),
    ("Pain, Procedural", "Procedural Pain", 2026),
    ("Supermarkets", "Food Markets", 2026),
    ("Melanoma, Cutaneous Malignant", "Cutaneous Malignant Melanoma", 2026),
    ("Flighted Spongy Moth Complex", "Lymantria dispar", 2026),
    ("Scoping Review as Topic", "Scoping Reviews as Topic", 2026),
    ("Surgical Procedures, Colorectal", "Colorectal Surgical Procedures", 2026),
    ("Nightclubs", "Drinking Establishments", 2026),
    ("Carcinoma, Basal Cell", "Basal Cell Carcinoma", 2026),
    ("Consensus Development Conferences as Topic", "Consensus Statements as Topic", 2026),
    ("Depressive Disorder, Major", "Major Depressive Disorder", 2026),
    ("Fetal Membranes, Premature Rupture", "Premature Rupture of Fetal Membranes", 2026),
    ("Roma", "Romani People", 2026),
    ("Heparitin Sulfate", "Heparan Sulfate", 2026),
    ("Pain, Intractable", "Intractable Pain", 2026),
    ("Pain, Postoperative", "Postoperative Pain", 2026),
    ("Conscious Sedation", "Procedural Sedation", 2026),
    ("Receptors, Kainic Acid", "Kainic Acid Receptors", 2026),
    ("Receptor, ErbB-2", "Erb-b2 Receptor Tyrosine Kinases", 2026),
    ("Multidrug Resistance-Associated Proteins", "ATP-Binding Cassette, Sub-Family C Proteins",
     2026),
    ("Fumariaceae", "Fumarioideae", 2026),
    ("Clostridium bifermentans", "Paraclostridium bifermentans", 2026),
    ("Clostridium cellulolyticum", "Ruminiclostridium cellulolyticum", 2026),
    ("Clostridium histolyticum", "Hathewaya histolytica", 2026),
    ("Clostridium sordellii", "Paraclostridium sordellii", 2026),
    ("Clostridium sticklandii", "Acetoanaerobium sticklandii", 2026),
    ("Clostridium thermocellum", "Acetivibrio thermocellus", 2026),
    ("Lactobacillus plantarum", "Lactiplantibacillus plantarum", 2026),
    ("Basic Helix-Loop-Helix Transcription Factors", "Basic Helix-Loop-Helix Proteins", 2026),
    ("Fragile X Mental Retardation Protein", "Fragile X Messenger Ribonucleoprotein 1", 2026),
    ("Feminine Hygiene Products", "Hygiene Products", 2026),
    ("Pain, Referred", "Referred Pain", 2026),
    ("Gulf of Mexico", "Gulf of America", 2026),
    ("Dual MEDICAID MEDICARE Eligibility", "Dual Medicare Medicaid Eligibility", 2026),
    ("Secondary Care", "Secondary Health Care", 2026),
    ("Tertiary Healthcare", "Tertiary Health Care", 2026),
]
MESH_RENAMED = {key(o): n for o, n, _ in MESH_RENAMES}
MESH_RENAMED_YEAR = {key(o): y for o, _, y in MESH_RENAMES}
# Old names whose descriptor NLM deleted (not renamed); PubMed maps the unquoted name to the
# heading in MESH_RENAMES (checked 2026-11-12), so the report says "replaced by".
MESH_REPLACED = {key(n) for n in (
    "Cascara", "Coniferophyta", "Punicaceae", "Taxodiaceae", "American Natives",
    "American Indians or Alaska Natives", "Cervical Intraepithelial Neoplasia",
    "Extreme Hot Weather")}
# Headings NLM deleted for MeSH 2026 (marked [OBSOLETE] in the 2026 RDF). On 2026-11-12 each,
# quoted, gave 0 records with "quoted phrase not found"; unquoted, Meta-Research[mh] gave 0 too.
MESH_DELETED = {key(n): 2026 for n in (
    "Dietary Patterns", "Disordered Eating Behavior", "Meta-Research",
    "Assessment of Medication Adherence", "Nonsuppressible Insulin-Like Activity",
    "Korarchaeota")}
NOTES = {
    key("Retraction of Publication"): "NLM's own Retraction filter now runs "
                                      "'hasretractionof OR retraction notice[pt]'.",
    key("Classical Article"): "Seminal Article is itself on NLM's list of discontinued types: "
                              "older citations keep it, new citations no longer get it.",
    key("Government Document"): "Government Publication is itself on NLM's list of discontinued "
                                "types: older citations keep it, new citations no longer get it.",
}

TAG = re.compile(r"\[\s*(pt|ptyp|publication type)\s*\]", re.I)
MESH_TAG = re.compile(r"\[\s*(mh|mesh|majr|mesh terms|mesh major topic)(\s*:\s*noexp)?\s*\]", re.I)
OPS = re.compile(r"(?<![A-Za-z0-9_])(AND|OR|NOT)(?![A-Za-z0-9_])")
OP_END = re.compile(r"(?<![A-Za-z0-9_])(AND|OR|NOT)$")
OP_START = re.compile(r"(AND|OR|NOT)(?![A-Za-z0-9_])")
DELIMS = set("()\"'=`{}[]:;")


# ---------------------------------------------------------------- parsing (pure)
def _term_before(text, j):
    """(term, start, end) of the search term that ends just before index j (a field tag)."""
    while j > 0 and text[j - 1].isspace():
        j -= 1
    if j > 0 and text[j - 1] == '"':
        k = text.rfind('"', 0, j - 1)
        if k < 0:
            return "", j, j
        return text[k + 1:j - 1], k, j
    lo = j
    while lo > 0 and text[lo - 1] not in DELIMS:
        lo -= 1
    s = lo
    for m in OPS.finditer(text, lo, j):
        s = m.end()
    while s < j and text[s].isspace():
        s += 1
    return text[s:j], s, j


def operator_of(text, start, end):
    """(operator, side) joining the term text[start:end-of-tag] to its neighbours.

    side 'before': the operator comes before the term (skipping spaces and '('); side 'after':
    the term comes first and the operator follows (skipping spaces and ')'). (None, None) when the
    term stands alone. Implicit AND between bare words is not detected."""
    i = start
    while i > 0 and (text[i - 1].isspace() or text[i - 1] == "("):
        i -= 1
    m = OP_END.search(text, 0, i)
    if m:
        return m.group(1), "before"
    m = OP_START.match(text[end:].lstrip(" \t\r\n)"))
    if m:
        return m.group(1), "after"
    return None, None


def find_terms(text):
    """Every publication-type and MeSH term in text, in order: dicts with term, start, term_end,
    tag_end, tag, field ('pt' or 'mesh') and quoted (True if the term is in double quotes)."""
    out = []
    for field, rx in (("pt", TAG), ("mesh", MESH_TAG)):
        for m in rx.finditer(text):
            term, s, e = _term_before(text, m.start())
            if not term.strip():
                continue
            out.append({"term": term.strip(), "start": s, "term_end": e, "tag_end": m.end(),
                        "tag": text[m.start():m.end()], "field": field,
                        "quoted": text[s:s + 1] == '"'})
    out.sort(key=lambda d: d["start"])
    return out


def classify(term, field="pt", quoted=True):
    """(status, new_name). For MeSH headings, an unquoted old name is mapped to the new heading
    by PubMed, so it is 'renamed_mapped' (reported, not a problem). A deleted heading is
    'deleted', quoted or not."""
    k = key(term)
    if field == "mesh":
        if k in MESH_RENAMED:
            return ("renamed" if quoted else "renamed_mapped"), MESH_RENAMED[k]
        if k in MESH_DELETED:
            return "deleted", None
        return "ok", None
    if k in RENAMED:
        return "renamed", RENAMED[k]
    if k in DISCONTINUED:
        return "discontinued", None
    return "ok", None


def effect(status, op, side, new=None, field="pt"):
    """What PubMed does with a term of this status in this Boolean position."""
    if status == "discontinued":
        return ("Discontinued: still matches older citations, but NLM no longer assigns this "
                "type to new citations.")
    if status == "renamed_mapped":
        return ("PubMed maps this old heading name to \"%s\" because it is not in quotes; "
                "quoted, it would find nothing. Prefer the new name." % new)
    if status not in ("renamed", "not_recognized", "deleted"):
        return ""
    if new:
        newtype = ("records indexed with \"%s\"" if field == "mesh" else "records typed \"%s\"") % new
    else:
        newtype = "the records you meant"
    if op == "OR":
        return ("PubMed drops this term without an error, so the OR group silently misses %s."
                % newtype)
    if op == "NOT" and side == "before":
        return ("PubMed drops this term, so this NOT excludes nothing; %s stay in the results."
                % newtype)
    if op in ("AND", "NOT"):
        return "This clause matches nothing, so the search (or this AND clause) finds 0 records."
    return "PubMed finds 0 records for this term."


def renamed_year(term, field):
    k = key(term)
    if field == "mesh":
        return MESH_RENAMED_YEAR.get(k) or MESH_DELETED.get(k)
    return RENAMED_YEAR.get(k)


def check_text(text):
    """Findings for every publication-type and MeSH term in one piece of text (no network)."""
    out = []
    for t in find_terms(text):
        status, new = classify(t["term"], t["field"], t["quoted"])
        op, side = operator_of(text, t["start"], t["tag_end"])
        out.append({"term": t["term"], "tag": t["tag"], "field": t["field"],
                    "quoted": t["quoted"], "status": status, "new_name": new,
                    "mesh_year": (renamed_year(t["term"], t["field"])
                                  if (new or status == "deleted") else None),
                    "operator": op, "side": side,
                    "effect": effect(status, op, side, new, t["field"]),
                    "note": NOTES.get(key(t["term"]), "") if t["field"] == "pt" else "",
                    "start": t["start"], "term_end": t["term_end"]})
    return out


def fix_text(text):
    """text with every renamed publication type and MeSH heading replaced by its new name
    (quoted). Deleted headings are left for a person to replace."""
    for t in sorted(find_terms(text), key=lambda d: -d["start"]):
        status, new = classify(t["term"], t["field"], t["quoted"])
        if status in ("renamed", "renamed_mapped"):
            text = text[:t["start"]] + '"%s"' % new + text[t["term_end"]:]
    return text


def line_variants(line):
    """The line itself with escaped quotes undone, plus its URL-decoded form if it looks
    URL-encoded (PubMed links and E-utilities calls in scripts)."""
    out = [line.replace('\\"', '"')]
    low = line.lower()
    if "%5b" in low or "%22" in low:
        out.append(urllib.parse.unquote_plus(line).replace('\\"', '"'))
    return out


def scan_lines(text, source):
    """Findings for a multi-line text (a file), one pass per line and per line variant."""
    out, seen = [], set()
    for no, line in enumerate(text.splitlines(), 1):
        for variant in line_variants(line):
            for f in check_text(variant):
                sig = (no, f["field"], key(f["term"]), f["operator"], f["side"])
                if sig in seen:
                    continue
                seen.add(sig)
                f.update(source=source, line=no)
                out.append(f)
    return out


# ---------------------------------------------------------------- PubMed (--live)
def parse_esearch(obj):
    """{'count', 'recognized', 'not_found'} from an esearch JSON reply for one quoted term."""
    r = (obj or {}).get("esearchresult") or {}
    warn = r.get("warninglist") or {}
    err = r.get("errorlist") or {}
    nf = list(warn.get("quotedphrasesnotfound") or []) + list(err.get("phrasesnotfound") or [])
    try:
        count = int(r.get("count"))
    except (TypeError, ValueError):
        count = None
    return {"count": count, "recognized": (not nf) if count is not None else None,
            "not_found": nf}


def esearch_url(term, field="pt"):
    tag = "mh" if field == "mesh" else "pt"
    q = urllib.parse.urlencode({"db": "pubmed", "retmode": "json", "retmax": "0",
                                "term": '"%s"[%s]' % (term.replace('"', ""), tag),
                                "tool": TOOL, "email": MAILTO})
    return ESEARCH + "?" + q


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def live_key(term, field="pt"):
    return ("mesh:" if field == "mesh" else "") + key(term)


def live_lookup(terms, fetch=None, pause=0.4):
    """{live_key: parse_esearch result or {'error': ...}} for each distinct term. Items are
    publication-type names or (name, field) pairs."""
    fetch = fetch or fetch_json
    out = {}
    n = 0
    for item in terms:
        term, field = (item, "pt") if isinstance(item, str) else item
        k = live_key(term, field)
        if k in out:
            continue
        if n and pause:
            time.sleep(pause)
        n += 1
        try:
            out[k] = parse_esearch(fetch(esearch_url(term, field)))
        except Exception as e:  # network or JSON failure: reported, never fatal
            out[k] = {"error": "%s: %s" % (type(e).__name__, e)}
    return out


def wants_live(f):
    """Publication types are always checked; MeSH headings only when quoted (PubMed maps an
    unquoted entry term to its heading, so a quoted-phrase test would mislead)."""
    return f.get("field", "pt") == "pt" or f.get("quoted")


def apply_live(findings, live):
    """Attach live results; an 'ok' term PubMed does not recognize becomes 'not_recognized'."""
    for f in findings:
        if not wants_live(f):
            continue
        res = live.get(live_key(f["term"], f.get("field", "pt"))) or {}
        f["live"] = res
        if res.get("recognized") is False and f["status"] == "ok":
            f["status"] = "not_recognized"
            f["effect"] = effect("not_recognized", f["operator"], f["side"], None,
                                 f.get("field", "pt"))
        elif res.get("recognized") is True and f["status"] in ("renamed", "deleted"):
            f["effect"] = ("PubMed recognized this old name when checked (count %s); NLM has "
                           "still %s it, so prefer the current name." % (
                               res.get("count"),
                               "deleted" if f["status"] == "deleted" else "renamed"))
    return findings


def is_problem(f):
    if f["status"] == "not_recognized":
        return True
    if f["status"] in ("renamed", "deleted"):
        return (f.get("live") or {}).get("recognized") is not True
    return False


# ---------------------------------------------------------------- CLI
def read_input(arg, stdin):
    """(source, text, is_file)."""
    if arg == "-":
        return "<stdin>", stdin.read(), False
    if os.path.isfile(arg):
        with open(arg, encoding="utf-8", errors="replace") as fh:
            return arg, fh.read(), True
    return "<query>", arg, False


def run(inputs, live=False, fetch=None, stdin=None, pause=0.4):
    """(findings, errors) for a list of query strings, file paths or '-'."""
    findings, errors = [], []
    for arg in inputs:
        try:
            source, text, is_file = read_input(arg, stdin or sys.stdin)
        except OSError as e:
            errors.append("%s: %s" % (arg, e))
            continue
        if is_file:
            findings.extend(scan_lines(text, source))
        else:
            for f in check_text(text):
                f.update(source=source, line=None)
                findings.append(f)
    asked = [f for f in findings if wants_live(f)]
    if live and asked:
        res = live_lookup([(f["term"], f.get("field", "pt")) for f in asked], fetch=fetch,
                          pause=pause)
        apply_live(findings, res)
        for k, r in res.items():
            if "error" in r:
                errors.append("live lookup failed for %r: %s" % (k, r["error"]))
    return findings, errors


def describe(f):
    where = f["source"] + (":%d" % f["line"] if f.get("line") else "")
    head = '%s: "%s"%s' % (where, f["term"], f["tag"])
    what = "MeSH heading" if f.get("field") == "mesh" else "publication type"
    year = (" (MeSH %s)" % f["mesh_year"]) if f.get("mesh_year") else ""
    verb = ("replaced by" if f.get("field") == "mesh" and key(f["term"]) in MESH_REPLACED
            else "renamed to")
    if f["status"] == "renamed":
        head += ' -> %s "%s"%s.' % (verb, f["new_name"], year)
    elif f["status"] == "renamed_mapped":
        head += ' -> %s "%s"%s; mapped because unquoted.' % (verb, f["new_name"], year)
    elif f["status"] == "deleted":
        head += " -> heading deleted%s; replace it by hand." % year
    elif f["status"] == "discontinued":
        head += " -> discontinued type."
    elif f["status"] == "not_recognized":
        head += " -> PubMed does not recognize this %s today." % what
    else:
        head += " -> current."
    if f.get("operator"):
        head += " Joined by %s." % f["operator"]
    lines = [head]
    if f.get("effect"):
        lines.append("    " + f["effect"])
    if f.get("note"):
        lines.append("    " + f["note"])
    live = f.get("live") or {}
    if "count" in live:
        lines.append("    PubMed today: %s records for \"%s\"[%s]%s." % (
            live["count"], f["term"], "mh" if f.get("field") == "mesh" else "pt",
            "" if live.get("recognized") else " (phrase not found)"))
    return "\n".join(lines)


def main(argv=None, fetch=None, out=None, stdin=None):
    out = out or sys.stdout
    ap = argparse.ArgumentParser(prog="pubmed_pt_check.py", description=(
        "Find PubMed publication types ([pt]) and quoted MeSH headings ([mh]) that NLM renamed, "
        "deleted or discontinued."))
    ap.add_argument("inputs", nargs="+", help="query strings, file paths, or - for stdin")
    ap.add_argument("--live", action="store_true",
                    help="ask PubMed (E-utilities) whether each publication type and quoted "
                         "MeSH heading is recognized")
    ap.add_argument("--all", action="store_true", help="also list current terms")
    ap.add_argument("--fix", action="store_true",
                    help="print the input with renamed names replaced (one input only)")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--version", action="version", version="%(prog)s " + VERSION)
    a = ap.parse_args(argv)
    if a.fix:
        if len(a.inputs) != 1:
            out.write("--fix takes exactly one input\n")
            return 2
        try:
            _, text, _ = read_input(a.inputs[0], stdin or sys.stdin)
        except OSError as e:
            out.write("%s\n" % e)
            return 2
        out.write(fix_text(text))
        if not text.endswith("\n"):
            out.write("\n")
        return 0
    findings, errors = run(a.inputs, live=a.live, fetch=fetch, stdin=stdin)
    shown = [f for f in findings if a.all or f["status"] != "ok"]
    if a.json:
        out.write(json.dumps({"version": VERSION, "source": SOURCE, "findings": shown,
                              "errors": errors}, indent=1) + "\n")
    else:
        for f in shown:
            out.write(describe(f) + "\n")
        for e in errors:
            out.write("error: %s\n" % e)
        n = sum(1 for f in findings if is_problem(f))
        n_pt = sum(1 for f in findings if f.get("field", "pt") == "pt")
        out.write("checked %d publication-type term(s) and %d MeSH term(s): %d renamed, deleted "
                  "or unrecognized, %d discontinued.\n" % (
                      n_pt, len(findings) - n_pt, n,
                      sum(1 for f in findings if f["status"] == "discontinued")))
    if errors:
        return 2
    return 1 if any(is_problem(f) for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
