# TCGA-OV cohort reconciliation, 2026-11-13 UTC

**Checked:** 2026-11-13T06:03:12Z to 2026-11-13T06:03:41Z. **Question:** the repository cites **608** GDC TCGA-OV cases and **489** cBioPortal `ov_tcga_pub` samples. What does each number count, and which denominator should an existing citation use?

This is a catalog reconciliation. It is **not clinical guidance** and **not a biological conclusion**. The frozen record is about 608 GDC cases and 489 samples (PMID 21720365; exome subset 316). In this copy, identifiers were not stored and controlled-access file contents were not downloaded.

## How 608 and 489 arise

| Number | What it counts on this retrieval | What it does not count |
| --- | --- | --- |
| **608** | GDC project `TCGA-OV` `summary.case_count`, and the `/cases` pagination total, on **Data Release 46.0 - August 10, 2026** (API tag 8.5.0). The hashed GDC case set has the same size. | Not the 2011 analysed cohort. Not an exome-sequenced cohort. Not a count of tumours with every assay. |
| **489** | cBioPortal study `ov_tcga_pub` (`Ovarian Serous Cystadenocarcinoma (TCGA, Nature 2011)`) `allSampleCount`, the `all_cases_in_study` sample list, and the `all_cases_with_cna_data` sample list. The PMC summary of PMID 21720365 says the project analyzed mRNA expression, miRNA expression, promoter methylation, and DNA copy number in **489** high-grade serous ovarian adenocarcinomas, and the DNA sequences of exons from coding genes in **316** of these tumors. | Not the current GDC case count. Not the exome-sequenced subset. The study description's phrase "Whole exome sequencing of 489" conflicts with `sequencedSampleCount` and with the paper. Do not cite that sentence for the exome denominator. |
| **316** | `ov_tcga_pub` `sequencedSampleCount`, the mutation sample list, the mutation-and-CNA sample list, and the mutation-and-CNA-and-mRNA sample list. That 316 is the exon-sequence count in the same summary sentence. | Not 489, and not 608. |
| **492** | Patient records returned for `ov_tcga_pub`. **489** of them have a sample in that study and **3** do not. | Not a third biological cohort. The reason those 3 patients have no sample is not established. |
| **617 / 600** | `ov_tcga` (Firehose Legacy): **617** samples and **600** patients. Samples exceed patients, so this study is not one sample per patient. | Not the GDC case count. |
| **585** | `ov_tcga_pan_can_atlas_2018`: **585** samples and **585** patients. Sequenced samples **523**. CNA samples **572**. | Not 608 and not 489. |
| **349** | Human Protein Atlas version 26.0 RNA cohort size for ovary serous cystadenocarcinoma, already recorded as V40. Not remeasured here. | Not the GDC case count and not the 2011 analysed-sample count. |

Every one of the 492 `ov_tcga_pub` patient barcodes was inside the 608 GDC cases. **116** GDC cases were outside that patient set. Relative to the 489 patients who have a sample, **119** GDC cases were outside (116 plus the 3 patients who have no sample). The overlap hash equals the patient-set hash because the portal-only side is empty.

GDC cases are not a uniform assay set. On the project summary, which counts files of every access level, WXS is attached to **457** cases, WGS to **363**, and RNA-Seq to **427**. Those are not a partition. The open-file case counts below are smaller where the sequencing reads are controlled. Open simple-nucleotide-variation files cover **419** cases, open WXS files cover **419** cases, and **189** GDC cases have no open simple-nucleotide-variation file. Open copy-number files cover **601** cases. The intersection of open SNV and open CNA is **417** cases. Every GDC case has at least one open file (clinical or biospecimen included). **599** cases have a primary-tumour sample record and **600** have a tumour tissue record. **8** cases have no tumour tissue record. Eight cases also have disease type "not reported"; this check does not show whether those are the same eight.

Disease type on the case facet: cystic, mucinous and serous neoplasms **600**; not reported **8**. Primary site: ovary **601**; retroperitoneum and peritoneum **7**. The project name remains Ovarian Serous Cystadenocarcinoma. These are catalog labels, not a new histotype review.

## Open-file counts

GDC file metadata, not file contents: **32,891** files on the project, of which **14,519** are `access=open` and **18,372** are `access=controlled`. The controlled count is an open metadata tally. Controlled-access file contents were not downloaded.

Open simple-nucleotide-variation files, open WXS files, and the masked-somatic-mutation data type are each **482** files. This certificate does not prove those three sets are the same files. It does record that the open SNV and open WXS **case** counts are both 419. There is no open "Sequencing Reads" category in the open-file facet. The project summary still lists Sequencing Reads for **584** cases, which is consistent with sequencing reads sitting in the controlled tier. That is a data-availability statement.

The project summary's experimental-strategy file counts sum to **30,567**, which is **2,324** below the project file count. The open-file strategy facet has a `_missing` bucket of **2,324**. Those two gaps are equal in size. This check does not identify them as the same files.

Per-category, per-strategy, and per-data-type counts are in the generated block. Case counts and file counts use the strings each endpoint returned, so category labels differ in case between the file facet and the file records.

## Overlap with each cBioPortal patient set

Overlaps were computed in memory from GDC case submitter identifiers and cBioPortal patient identifiers, then reduced to counts and SHA-256 values. A patient value is the uppercase 12-character participant barcode. No identifier was written. Portal-only counts are zero for all three studies: each cBioPortal patient set is a subset of the current GDC case set.

| Study | Samples | Patients | Patients with a sample | In GDC | GDC only | Portal only |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `ov_tcga_pub` | 489 | 492 | 489 | 492 | 116 | 0 |
| `ov_tcga` | 617 | 600 | 600 | 600 | 8 | 0 |
| `ov_tcga_pan_can_atlas_2018` | 585 | 585 | 585 | 585 | 23 | 0 |

`ov_tcga` has 617 samples and 600 patients, so some patients contribute more than one sample. That is why a sample count can exceed the GDC case count without any patient falling outside GDC.

## Which number each existing citation should use

The 2026-11-04 verification log in [directions](directions.md) printed 608 and 489. Both digits were still returned on this retrieval. The correction is the denominator, not a silent edit of an older certificate.

| Existing text | Keep the digit? | Cite it as |
| --- | --- | --- |
| directions.md GDC `projects/TCGA-OV` **608** cases | Yes, 608 | GDC project `TCGA-OV` summary case count on Data Release 46.0. Not the 2011 analysed set. |
| directions.md cBioPortal `ov_tcga_pub` **489** samples | Yes, 489 | `allSampleCount` for `ov_tcga_pub`: the Nature 2011 expression, microRNA, methylation and copy-number cohort. Not the exome count and not the GDC case count. |
| Exome or mutation-and-CNA denominator, including the `ov_tcga_pub` description sentence that says whole exome sequencing of 489 | No | **316**, from `sequencedSampleCount`, the mutation and mutation-and-CNA sample lists, and PMID 21720365. |
| V40 "TCGA 349" ovary serous cystadenocarcinoma cohort size | Yes, 349, with a narrower label | Human Protein Atlas version 26.0 RNA cohort size. Not remeasured here. Not 608 and not 489. |

## Requests

GDC base `https://api.gdc.cancer.gov`. cBioPortal base `https://www.cbioportal.org/api`. Exact URLs, filters, and the fetch clock are in [manifest.json](../results/tcga-ov-cohort-reconciliation-20261113/manifest.json).

Frozen aggregate responses:

- `GET /status` — data release, tag, commit.
- `GET /projects/TCGA-OV` with `expand=summary,summary.data_categories,summary.experimental_strategies`.
- `GET /cases` for project `TCGA-OV`, `size=0`, facets `disease_type`, `primary_site`, `samples.sample_type`, `samples.tissue_type`.
- `GET /files` for project `TCGA-OV` and `access=open`, `size=0`, facets `data_category`, `data_type`, `experimental_strategy`.
- `GET /files` for project `TCGA-OV`, `size=0`, facet `access` (open versus controlled file counts only).
- `GET /api/info`, projected to version fields. Commit message and author fields were dropped before storage.
- `GET /api/studies/{ov_tcga,ov_tcga_pub,ov_tcga_pan_can_atlas_2018}`, plus each study's molecular profiles and sample-list index.

Identifier responses were requested only to count and hash, and were not retained: GDC case submitter identifiers, open-file case identifiers, cBioPortal patients, samples, and sample-list membership. cBioPortal info was portal version `v7.2.3`, database version `3.1.0`. GDC commit `8f7c2a51ab0084b216ad1b62a3fae8b945439c53`.

## Generated counts

<!-- BEGIN GENERATED TCGA OV COHORT COUNTS -->
retrieved_started_utc: 2026-11-13T06:03:12.019489+00:00
retrieved_completed_utc: 2026-11-13T06:03:41.863445+00:00
gdc_data_release: Data Release 46.0 - August 10, 2026
gdc_tag: 8.5.0
gdc_api_version: 1
cbioportal_portal_version: v7.2.3
cbioportal_db_version: 3.1.0
gdc_project_case_count: 608
gdc_case_set_count: 608
gdc_case_set_sha256: 4ded93e7468896709cdd4d77eafdb711f55c7fcb7dbee03c61297541dd868ea4
gdc_primary_tumor_cases: 599
gdc_tumor_tissue_cases: 600
gdc_cases_without_tumor_tissue: 8
gdc_project_file_count: 32891
gdc_open_file_count: 14519
gdc_controlled_file_count: 18372
project_strategy_file_count_sum: 30567
project_strategy_file_count_gap: 2324
open_snv_cases: 419
open_cna_cases: 601
open_snv_and_cna_cases: 417
gdc_cases_without_open_snv: 189
open_wxs_cases: 419
open_file_cases_any: 608
open_file_cases_outside_gdc: 0
ov_tcga_pub_all_samples: 489
ov_tcga_pub_sequenced_samples: 316
ov_tcga_pub_cna_samples: 489
ov_tcga_pub_complete_samples: 316
ov_tcga_pub_patients: 492
ov_tcga_pub_patients_with_a_sample: 489
ov_tcga_pub_patients_without_a_sample: 3
ov_tcga_pub_patient_sha256: a97109d515733e7402173aae8f25aa03cf687b55c9448e0b9b7b80ebe65ce479
ov_tcga_pub_overlap_gdc: 492
ov_tcga_pub_gdc_only: 116
ov_tcga_pub_portal_only: 0
ov_tcga_pub_overlap_sha256: a97109d515733e7402173aae8f25aa03cf687b55c9448e0b9b7b80ebe65ce479
ov_tcga_pub_exome_phrase_count: 489
ov_tcga_pub_exome_phrase_conflicts: True
ov_tcga_all_samples: 617
ov_tcga_patients: 600
ov_tcga_overlap_gdc: 600
ov_tcga_gdc_only: 8
ov_tcga_portal_only: 0
ov_tcga_pan_can_atlas_2018_all_samples: 585
ov_tcga_pan_can_atlas_2018_patients: 585
ov_tcga_pan_can_atlas_2018_sequenced_samples: 523
ov_tcga_pan_can_atlas_2018_cna_samples: 572
ov_tcga_pan_can_atlas_2018_overlap_gdc: 585
ov_tcga_pan_can_atlas_2018_gdc_only: 23
ov_tcga_pan_can_atlas_2018_portal_only: 0
identifiers_retained: False
controlled_access_files_requested: False
biological_conclusion: none
clinical_guidance: none
disease_type: cystic, mucinous and serous neoplasms 600
disease_type: not reported 8
primary_site: ovary 601
primary_site: retroperitoneum and peritoneum 7
project_strategy_cases: Diagnostic Slide 106
project_strategy_cases: Expression Array 530
project_strategy_cases: Genotyping Array 597
project_strategy_cases: Methylation Array 602
project_strategy_cases: RNA-Seq 427
project_strategy_cases: Reverse Phase Protein Array 422
project_strategy_cases: Tissue Slide 589
project_strategy_cases: WGS 363
project_strategy_cases: WXS 457
project_strategy_cases: miRNA-Seq 522
open_files_category: biospecimen 2601
open_files_category: clinical 1204
open_files_category: copy number variation 5799
open_files_category: dna methylation 1869
open_files_category: proteome profiling 432
open_files_category: simple nucleotide variation 482
open_files_category: transcriptome profiling 2132
open_files_strategy: Diagnostic Slide 107
open_files_strategy: Expression Array 548
open_files_strategy: Genotyping Array 5247
open_files_strategy: Methylation Array 1869
open_files_strategy: RNA-Seq 434
open_files_strategy: Reverse Phase Protein Array 432
open_files_strategy: Tissue Slide 1374
open_files_strategy: WGS 552
open_files_strategy: WXS 482
open_files_strategy: _missing 2324
open_files_strategy: miRNA-Seq 1150
open_files_data_type: Allele-specific Copy Number Segment 1238
open_files_data_type: Biospecimen Supplement 1120
open_files_data_type: Clinical Supplement 597
open_files_data_type: Copy Number Segment 1564
open_files_data_type: Gene Expression Quantification 434
open_files_data_type: Gene Level Copy Number 1797
open_files_data_type: Isoform Expression Quantification 575
open_files_data_type: Masked Copy Number Segment 1200
open_files_data_type: Masked Intensities 1246
open_files_data_type: Masked Somatic Mutation 482
open_files_data_type: Methylation Beta Value 623
open_files_data_type: Pathology Report 607
open_files_data_type: Protein Expression Quantification 432
open_files_data_type: Raw Intensities 548
open_files_data_type: Slide Image 1481
open_files_data_type: miRNA Expression Quantification 575
open_cases_category: Biospecimen 608
open_cases_category: Clinical 608
open_cases_category: Copy Number Variation 601
open_cases_category: DNA Methylation 602
open_cases_category: Proteome Profiling 422
open_cases_category: Simple Nucleotide Variation 419
open_cases_category: Transcriptome Profiling 559
open_cases_strategy: Diagnostic Slide 106
open_cases_strategy: Expression Array 530
open_cases_strategy: Genotyping Array 597
open_cases_strategy: Methylation Array 602
open_cases_strategy: RNA-Seq 427
open_cases_strategy: Reverse Phase Protein Array 422
open_cases_strategy: Tissue Slide 589
open_cases_strategy: WGS 331
open_cases_strategy: WXS 419
open_cases_strategy: _missing 608
open_cases_strategy: miRNA-Seq 522
citation: docs/directions.md GDC TCGA-OV case count printed=608 observed=608
citation: docs/directions.md cBioPortal ov_tcga_pub sample count printed=489 observed=489
citation: cBioPortal ov_tcga_pub sequencedSampleCount and PMID 21720365 printed=None observed=316
citation: CLAIMS.md V40 Human Protein Atlas TCGA RNA cohort printed=349 observed=None
<!-- END GENERATED TCGA OV COHORT COUNTS -->

## Reproduction

```sh
python3 results/tcga-ov-cohort-reconciliation-20261113/verify.py
python3 -m unittest tests.test_tcga_ov_cohort -v
```

`verify.py` reruns the export reader and the recompute reader on the frozen files. They must agree. The recompute reader sums facet buckets and checks overlap arithmetic (`overlap + GDC-only = 608`, `overlap + portal-only = patient count`). The export reader reads named API fields. A fixture test checks the barcode and hash functions, because the offline replay cannot rebuild the sets.

A live rerun is `python3 tools/fetch_tcga_ov_cohort.py`. It refuses to overwrite an existing snapshot unless `--force` is passed. A later GDC release can change 608. This copy is the 2026-11-13 retrieval.

## Limits

- Identifiers were not stored. Offline verification does not recompute the set hashes from barcodes. It checks that the pinned hashes are well formed and that the counts partition.
- Unparsed barcodes were zero for the GDC case set and for all three patient and sample sets.
- The access facet on an already access-filtered file query is not used. Open versus controlled file counts come from a separate unfiltered access facet.
- Sample-type facet counts are cases that have at least one sample of that type. They are not a partition of 608.
- Catalog labels such as `hgsoc`, disease type, and primary site are copied from the responses. They are not a histotype adjudication and not a statement about an individual tumour.
- Nothing here selects a treatment, estimates benefit, or interprets survival.

Prepared with AI assistance (Cursor cloud agent, Grok 4.7) under human direction. Counts are from the Genomic Data Commons and cBioPortal public APIs. The 2011 cohort definition is from the TCGA Research Network paper, PMID 21720365. Those providers are the sources. The dual offline recount is this project's check of the frozen responses.
