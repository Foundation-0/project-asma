# Candidate research directions

**Checked:** 2026-11-04. **Scope:** ranked possibilities for a small open team using
**public, de-identified or open-licensed inputs only**. This is not a commitment
to run any direction. Controlled-access cohorts (dbGaP-controlled TCGA, EGA, and
similar) require a data-access request and an **owner decision**; they are **not**
planned here.

Each direction lists a verifiable deliverable (re-runnable script plus aggregate
numbers), feasibility limits, and a claim label for the “why it matters” statement.
No direction below is clinical guidance.

Prior-art gaps are phrased as **we did not find** with the search named; nothing
here is called novel without that search.

## How to adopt a direction

1. Open a **protocol pull request** (population, endpoint, permitted inputs, stop
   rules) mirroring the rigor of [Pilot 001](../protocols/pilot-001.md).
2. Pass the **owner gate** in [roadmap](roadmap.md) Gate 0 before live acquisition,
   real-source parsing checks, or fitting on study values.
3. Ship results as **one pull request per executed result**, with claim labels and
   reproduction commands.

## Ranked shortlist

### 1. Primary platinum-refractory HGSOC protein signature (active track — Pilot 001)

| Field | Content |
| --- | --- |
| **Question** | Can a published Figure 3D discovery cross-validation result for **primary** platinum-refractory HGSOC be reproduced and stress-tested on genuinely independent patients? |
| **Why it matters** | **KNOWN:** Chowdhury et al. (Cell, 2023) report a 64-protein signature with published discovery AUC 0.83 (95% CI 0.77–0.90) and emphasize that high specificity still misses many refractory cases — specificity is not overall accuracy. [DOI 10.1016/j.cell.2023.07.004](https://doi.org/10.1016/j.cell.2023.07.004) (HTTP 200 on 2026-11-04). Correction to supplemental legends: [DOI 10.1016/j.cell.2024.01.016](https://doi.org/10.1016/j.cell.2024.01.016) (HTTP 200 on 2026-11-04). |
| **Public inputs** | **PDC open tier:** proteome studies **PDC000360** (discovery), **PDC000358** (FFPE validation), **PDC000362** (frozen validation) — portal pages HTTP 200 on 2026-11-04; PDC public-data terms CC BY 4.0 per project [data-use](pilot-001-data-use.md) review. **NLM open supplements** for PMC10414761 (MMC1/MMC4, article-associated **CC BY-NC-ND 4.0** — no redistribution of workbooks). Author-processed matrix offered in article supplements (reuse route documented in [pilot-001-data-use.md](pilot-001-data-use.md), not a blanket grant). |
| **Licence summary** | PDC releases: **CC BY 4.0** with attribution. NLM MMC1/MMC4: **CC BY-NC-ND 4.0** — private noncommercial analysis may be permitted; **do not commit or redistribute** source tables. |
| **Deliverable** | Protocol-frozen commands, aggregate AUROC/overlap counts, discrepancy log — as in [pilot-001-score-verification-result.md](pilot-001-score-verification-result.md) for the one executed score check; full reproduction still open. |
| **Feasibility** | High for bounded audits and software; **low** for closed Gate 2 until provenance, corrected supplements, and patient independence are resolved. |
| **Main limitation** | Small refractory/sensitive counts; overlapping discovery/frozen patients; alignment and missing author workspaces ([pilot-001-input-resolution.md](pilot-001-input-resolution.md)). |

### 2. TCGA-OV open-tier genomic and clinical characterization (all histotypes in cohort)

| Field | Content |
| --- | --- |
| **Question** | For **TCGA-OV** open-access releases only, what do reproducible aggregates show about molecular subtypes, **BRCA1/2** alteration prevalence, and survival associations — stated as exploratory, not predictive medicine? |
| **Why it matters** | **KNOWN:** The TCGA ovarian analysis reports integrated genomic, transcriptomic, and clinical features of serous ovarian carcinoma and defines molecular subtypes with distinct survival patterns. [DOI 10.1038/nature11456](https://doi.org/10.1038/nature11456) (HTTP 200 on 2026-11-04); PubMed landing page fetched for [PMID 21720365](https://pubmed.ncbi.nlm.nih.gov/21720365/) on 2026-11-04. |
| **Public inputs** | **GDC open tier:** project **TCGA-OV** — [portal project page](https://portal.gdc.cancer.gov/projects/TCGA-OV) and [GDC API project record](https://api.gdc.cancer.gov/projects/TCGA-OV) HTTP 200 on 2026-11-04. **cBioPortal (public study):** **`ov_tcga_pub`** — [study summary](https://www.cbioportal.org/study/summary?id=ov_tcga_pub); API name “Ovarian Serous Cystadenocarcinoma (TCGA, Nature 2011)” on 2026-11-04. |
| **Licence summary** | GDC open-access tier via [GDC documentation](https://docs.gdc.cancer.gov/) (HTTP 200 on 2026-11-04 — read current access and attribution rules before download). dbGaP-controlled **copy** of TCGA is **out of scope** without DAR + owner decision. cBioPortal: public study download for academic use; cite TCGA and cBioPortal. |
| **Deliverable** | Script querying GDC/cBioPortal (or pinned export files) that prints fixed tables: sample counts by subtype, alteration frequencies, Kaplan–Meier summary statistics with declared censoring — all aggregates, no row-level commits. |
| **Feasibility** | **Medium:** mature APIs and prior code examples; histotype labels and treatment covariates need careful endpoint definitions. |
| **Main limitation** | TCGA-OV is largely **HGSOC**-enriched; survival analyses are **observational**; subtype calls depend on assay era and platform. |

### 3. CPTAC ovarian proteogenomics via GDC aggregator (cross-resource audit)

| Field | Content |
| --- | --- |
| **Question** | For CPTAC ovarian cases mirrored in **GDC/cBioPortal**, how complete are public proteomics/clinical fields for **pre-specified** audit questions (e.g., case counts, gene-level detection rates for DNA-repair genes) without training a clinical classifier? |
| **Why it matters** | **KNOWN:** CPTAC programs publish multi-omic tumor characterization intended to complement genomics; proteomic coverage informs whether a protein-level question is answerable from open releases. **CONJECTURE:** systematic open-tier audits would reduce wasted effort on incomplete joins — we did not find a public, frozen audit script in this repository (search: `rg CPTAC docs/` and `registries/` on 2026-11-04). |
| **Public inputs** | **cBioPortal:** **`ovary_cptac_gdc`** — [study summary](https://www.cbioportal.org/study/summary?id=ovary_cptac_gdc); API reports 112 samples, public on 2026-11-04. **PDC open tier:** **PDC000360/358/362** (same PTRC HGSOC proteome studies as Pilot 001; metadata verified in [datasets.json](../registries/datasets.json)). |
| **Licence summary** | GDC/CPTAC open releases: attribution and GDC terms; PDC **CC BY 4.0**. Do not assume PDC matrices substitute for author-processed Pilot inputs without provenance proof. |
| **Deliverable** | Re-runnable audit script emitting JSON summaries (field completeness, sample counts, gene lists) checked into `registries/` only as aggregates; no matrix commits. |
| **Feasibility** | **Medium** for metadata audits; **low** for patient-level performance claims without independence mapping. |
| **Main limitation** | Overlap with Pilot 001 cohorts; proteomic and genomic case IDs must be matched explicitly; correlation ≠ treatment benefit. |

### 4. DepMap: ovarian cell-line dependencies and DNA-repair context

| Field | Content |
| --- | --- |
| **Question** | Among **public** DepMap ovarian lines, what are reproducible associations between **PARP/platinum sensitivity scores** and annotated **BRCA1/2** or HR-pathway alterations — described as in vitro screening biology, not patient outcome? |
| **Why it matters** | **KNOWN:** Large-scale dependency maps support hypothesis generation about DNA-damage response vulnerabilities in cancer cell lines. **CONJECTURE:** open aggregates could contextualize HGSOC therapy-resistance hypotheses — not a substitute for clinical validation (DepMap FAQ and papers cited on [depmap.org](https://depmap.org/portal/terms/) — terms page HTTP 200 on 2026-11-04). |
| **Public inputs** | **DepMap Public 24Q4** release file endpoint HTTP 200 on 2026-11-04: `https://depmap.org/portal/download/api/download/depmap_public_24q4` (filename/version pinned in protocol at execution time). |
| **Licence summary** | DepMap [terms of use](https://depmap.org/portal/terms/) — follow attribution and redistribution rules on download; no redistribution of full matrix in Git. |
| **Deliverable** | Script reading pinned CSV slices (in execution environment only) that prints line counts, mutation counts, and Spearman correlations with bootstrap CIs — fixed seed, aggregate output only. |
| **Feasibility** | **High** for small-team tabular analysis; **low** for translating to patient platinum refractoriness (different endpoint). |
| **Main limitation** | Cell lines ≠ tumors; culture conditions; **correlation ≠ causation**; small ovarian subset within DepMap. |

### 5. Stroma (CAF) expression signature replication in HGSOC (GEO)

| Field | Content |
| --- | --- |
| **Question** | Does a published **cancer-associated fibroblast** expression signature in laser-captured HGSOC stroma reproduce specified aggregate associations (e.g., survival quartile ordering) under a fixed preprocessing script? |
| **Why it matters** | **KNOWN:** Birrer/Mok et al. profiled microdissected stroma versus epithelium in high-grade serous ovarian cancer and linked stromal expression to patient outcomes in the original publication. Series linked to [PMID 23824740](https://pubmed.ncbi.nlm.nih.gov/23824740/) (landing fetched 2026-11-04). |
| **Public inputs** | **GEO open tier:** **GSE40595** — FTP soft header verified 2026-11-04 (`!Series_title` = “A cancer associated fibroblasts (CAFs) specific gene signature in high grade serous ovarian cancer”; 31 cancer stroma / 32 epithelial samples per series metadata). |
| **Licence summary** | GEO series typically public domain / NIH terms; verify GEO [accession page](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE40595) (HTTP 200 on 2026-11-04) before download. |
| **Deliverable** | Normalization script + fixed gene list + aggregate survival/statistics matching published direction of effect within declared tolerance; no CEL files in Git. |
| **Feasibility** | **Medium:** array preprocessing choices dominate; must pre-register probeset mapping. |
| **Main limitation** | Small sample size; microdissection batch effects; **observational** survival association. |

### 6. Multi-histotype ovarian carcinoma expression contrasts (GEO)

| Field | Content |
| --- | --- |
| **Question** | Using **GSE66957**, what reproducible pathway-level contrasts separate ovarian carcinomas from normal surface epithelium — **without** pooling histotypes into a single “ovarian cancer” label? |
| **Why it matters** | **KNOWN:** Histotype (serous, clear cell, endometrioid, mucinous) carries different biology and should not be conflated in biomarker work ([mission](mission.md)). GSE66957 series metadata (FTP soft header verified 2026-11-04) describes 57 carcinomas and 12 normals with title “Pathways of ovarian cancer development”. |
| **Public inputs** | **GEO open tier:** **GSE66957** — [accession page](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE66957) HTTP 200 on 2026-11-04. |
| **Licence summary** | Same as other GEO series; no UK Biobank or controlled-access genomics. |
| **Deliverable** | Script producing ranked pathway scores (e.g., GSEA-style aggregates) with histotype-stratified tables and explicit “not run” stages if labels missing. |
| **Feasibility** | **Medium** with standard array tools; label curation effort. |
| **Main limitation** | Mixed histotypes in one series; old Affymetrix platform; **exploratory** biology only. |

### 7. miRNA–oxidative-stress cluster reproducibility (GEO)

| Field | Content |
| --- | --- |
| **Question** | In **GSE26193**, does a published hierarchical clustering of high-grade ovarian adenocarcinomas by oxidative-stress/fibrosis pathways reproduce under fixed preprocessing? |
| **Why it matters** | **KNOWN:** The series summary (FTP soft header verified 2026-11-04) states transcriptome analysis testing oxidative stress and fibrosis pathways in high-grade ovarian adenocarcinomas. Original paper should be cited from the series PubMed link when executing — fetch series metadata before claiming specific effect sizes. |
| **Public inputs** | **GEO open tier:** **GSE26193** — FTP soft header HTTP 200 on 2026-11-04 (`!Series_title` = “Control of oxidative stress by miRNA and impact on ovarian tumorigenesis”). |
| **Licence summary** | GEO open tier as above. |
| **Deliverable** | Cluster assignment agreement rate (e.g., adjusted Rand) or pathway score correlation vs published figure — aggregates only. |
| **Feasibility** | **Medium**; may stall if supplemental gene lists are unavailable — record stop. |
| **Main limitation** | miRNA platform era; cluster stability; not a treatment-selection tool. |

### 8. Recruiting interventional trial landscape (ClinicalTrials.gov metadata)

| Field | Content |
| --- | --- |
| **Question** | As of a pinned date, how many **recruiting** interventional trials on ClinicalTrials.gov tag **ovarian cancer** by phase, biomarker keyword, and platinum-resistance language — a descriptive map, not trial enrollment advice? |
| **Why it matters** | **KNOWN:** Trial registries document active research priorities; summarizing them helps researchers see where public evidence is thin. **CONJECTURE:** a frozen CSV snapshot would help this project prioritize questions — we did not find an existing snapshot in-repo (search: `ClinicalTrials.gov` in `docs/` on 2026-11-04). |
| **Public inputs** | **ClinicalTrials.gov API v2** — example query returned **774** recruiting studies for condition “Ovarian Cancer” on 2026-11-04 (`filter.overallStatus=RECRUITING`; first NCT **NCT06404671**). [Example study page](https://clinicaltrials.gov/study/NCT06404671) HTTP 200 on 2026-11-04. |
| **Licence summary** | U.S. government registry data; follow [ClinicalTrials.gov terms](https://clinicaltrials.gov/about-site/terms-conditions) before bulk reuse. |
| **Deliverable** | Script printing counts and keyword buckets; optional committed **aggregate** JSON (counts only, no patient rows). |
| **Feasibility** | **High** for metadata; **no patient data**. |
| **Main limitation** | Registry text ≠ results; eligibility strings are inconsistent; **not** a substitute for systematic review or care decisions. |

## Directions explicitly excluded here

| Resource | Reason |
| --- | --- |
| **UK Biobank** | Not open; application required — excluded by owner direction. |
| **dbGaP-controlled TCGA**, **EGA** | Controlled access — DAR + owner decision; not planned. |
| **Row-level patient downloads in Git** | Violates [reproducibility and data rules](reproducibility-and-data.md). |

## Verification log (2026-11-04)

| Target | Route | Result |
| --- | --- | --- |
| DOI 10.1016/j.cell.2023.07.004 | `curl -L -o /dev/null -w %{http_code}` | 200 |
| DOI 10.1038/nature11456 | same | 200 |
| GSE40595 / GSE66957 / GSE26193 soft headers | NCBI FTP `*_family.soft.gz` | Titles/accessions match table |
| TCGA-OV | GDC API + portal | 200 |
| ov_tcga_pub / ovary_cptac_gdc | cBioPortal API | JSON study records |
| PDC000360 | PDC portal filter URL | 200 |
| DepMap Public 24Q4 API path | depmap.org download API | 200 |
| ClinicalTrials.gov v2 | recruiting ovarian cancer count | 774 totalCount |

This log does not prove scientific conclusions, licence interpretation for your
jurisdiction, or that downloads will remain unchanged.
