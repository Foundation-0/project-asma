# Candidate research directions

**Checked:** 2026-11-04 (re-verified after PR #35 review). **Scope:** ranked
possibilities for a small open team using **public, de-identified or open-licensed
inputs only**. This is not a commitment to run any direction. Controlled-access
cohorts (dbGaP-controlled TCGA, EGA, and similar) require a data-access request
and an **owner decision**; they are **not** planned here.

Each direction lists a verifiable deliverable (re-runnable script plus aggregate
numbers), feasibility limits, and a claim label for the “why it matters” statement.
No direction below is clinical guidance.

Prior-art gaps are phrased as **we did not find** with the search named; nothing
here is called novel without that search.

## How to adopt a direction

The [2026-11-04 continuation record](research-continuation.md) supplements this
feasibility shortlist with broader evidence handoffs and a focused anti-Yo
frontier proposal. Its literature review and synthetic checks have run;
mechanistic hypotheses and study-data analyses remain unexecuted. Feasibility
ranking here must not be interpreted as a novelty ranking.

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
| **Why it matters** | **KNOWN:** Chowdhury et al. (Cell, 2023) report a 64-protein signature with published discovery AUC 0.83 (95% CI 0.77–0.90) and emphasize that high specificity still misses many refractory cases — specificity is not overall accuracy. [DOI 10.1016/j.cell.2023.07.004](https://doi.org/10.1016/j.cell.2023.07.004). Correction to supplemental legends: [DOI 10.1016/j.cell.2024.01.016](https://doi.org/10.1016/j.cell.2024.01.016). |
| **Public inputs** | **PDC open tier:** **PDC000360**, **PDC000358**, **PDC000362** (see verification log). **NLM open supplements** for PMC10414761 (MMC1/MMC4, article-associated **CC BY-NC-ND 4.0** — no redistribution of workbooks). Author-processed matrix offered in article supplements (reuse route in [pilot-001-data-use.md](pilot-001-data-use.md), not a blanket grant). |
| **Licence summary** | PDC releases: **CC BY 4.0** with attribution. NLM MMC1/MMC4: **CC BY-NC-ND 4.0** — private noncommercial analysis may be permitted; **do not commit or redistribute** source tables. |
| **Deliverable** | Protocol-frozen commands, aggregate AUROC/overlap counts, discrepancy log — as in [pilot-001-score-verification-result.md](pilot-001-score-verification-result.md) for the one executed score check; full reproduction still open. |
| **Feasibility** | High for bounded audits and software; **low** for closed Gate 2 until provenance, corrected supplements, and patient independence are resolved. |
| **Main limitation** | Small refractory/sensitive counts; overlapping discovery/frozen patients; alignment and missing author workspaces ([pilot-001-input-resolution.md](pilot-001-input-resolution.md)). |

### 2. TCGA-OV open-tier genomic and clinical characterization (serous ovarian carcinoma)

| Field | Content |
| --- | --- |
| **Question** | For **TCGA-OV** open-access releases only, what do reproducible aggregates show about molecular subtypes, **BRCA1/2** alteration prevalence, and survival associations in **serous ovarian carcinoma** — stated as exploratory, not predictive medicine? |
| **Why it matters** | **KNOWN:** The TCGA ovarian analysis reports integrated genomic, transcriptomic, and clinical features of **serous** ovarian carcinoma and defines molecular subtypes with distinct survival patterns. [DOI 10.1038/nature10166](https://doi.org/10.1038/nature10166) (Nature 474:609–615); [PMID 21720365](https://pubmed.ncbi.nlm.nih.gov/21720365/). |
| **Public inputs** | **GDC open tier:** project **TCGA-OV** — [portal project page](https://portal.gdc.cancer.gov/projects/TCGA-OV); GDC `projects/TCGA-OV?expand=summary` reports **608** cases (verification log). **cBioPortal (public study):** **`ov_tcga_pub`**. |
| **Licence summary** | GDC open-access tier — read current rules in [GDC documentation](https://docs.gdc.cancer.gov/) before download. dbGaP-controlled **copy** of TCGA is **out of scope** without DAR + owner decision. cBioPortal: public study export; cite TCGA and cBioPortal. |
| **Deliverable** | Script querying GDC/cBioPortal (or pinned export files) that prints fixed tables: sample/case counts, alteration frequencies, Kaplan–Meier summary statistics with declared censoring — all aggregates, no row-level commits. |
| **Feasibility** | **Medium:** mature APIs and prior code examples; treatment covariates need careful endpoint definitions. |
| **Main limitation** | **TCGA-OV is serous ovarian carcinoma, not a multi-histotype pan-ovarian cohort** (608 GDC cases). cBioPortal **`ov_tcga_pub`** profile count (489) differs from GDC case count — document which denominator each table uses. Survival analyses are **observational**. |

### 3. CPTAC ovarian proteogenomics via GDC aggregator (cross-resource audit)

| Field | Content |
| --- | --- |
| **Question** | For CPTAC ovarian cases mirrored in **GDC/cBioPortal**, how complete are public proteomics/clinical fields for **pre-specified** audit questions (e.g., case counts, gene-level detection rates for DNA-repair genes) without training a clinical classifier? |
| **Why it matters** | **KNOWN:** CPTAC programs publish multi-omic tumor characterization intended to complement genomics; proteomic coverage informs whether a protein-level question is answerable from open releases. **CONJECTURE:** systematic open-tier audits would reduce wasted effort on incomplete joins — we did not find a public, frozen audit script in this repository (search: `rg CPTAC docs/` and `registries/` on 2026-11-04). |
| **Public inputs** | **cBioPortal:** **`ovary_cptac_gdc`**. **PDC open tier:** **PDC000360/358/362** (PTRC HGSOC proteome studies; [datasets.json](../registries/datasets.json)). |
| **Licence summary** | GDC/CPTAC open releases: attribution and GDC terms; PDC **CC BY 4.0**. Do not assume PDC matrices substitute for author-processed Pilot inputs without provenance proof. |
| **Deliverable** | Re-runnable audit script emitting JSON summaries (field completeness, sample counts, gene lists) checked into `registries/` only as aggregates; no matrix commits. |
| **Feasibility** | **Medium** for metadata audits; **low** for patient-level performance claims without independence mapping. |
| **Main limitation** | Overlap with Pilot 001 cohorts; proteomic and genomic case IDs must be matched explicitly; correlation ≠ treatment benefit. |

### 4. DepMap: ovarian cell-line dependencies and DNA-repair context

| Field | Content |
| --- | --- |
| **Question** | Among **public** DepMap ovarian lines, what are reproducible associations between **PRISM** drug sensitivity readouts (including PARP inhibitors and platinum agents where present in the release) and annotated **BRCA1/2** or HR-pathway alterations — described as in vitro screening biology, not patient outcome? |
| **Why it matters** | **KNOWN:** Large-scale dependency maps and **PRISM** pharmacological profiling support hypothesis generation about DNA-damage response vulnerabilities in cancer cell lines. **CONJECTURE:** open aggregates could contextualize HGSOC therapy-resistance hypotheses — not a substitute for clinical validation. |
| **Public inputs** | Two pinned Figshare releases (API-verified in log): **(A) DepMap omics / models — [27993248](https://figshare.com/articles/dataset/DepMap_Public_24Q4/27993248)** title **`DepMap 24Q4 Public`**, version **1** — use **`Model.csv`** (ovarian lineage filter), **`OmicsSomaticMutationsMatrixDamaging.csv`** (BRCA1/2 and HR-pathway columns). **`PortalCompounds.csv`** is compound metadata only (no dose–response matrix). **(B) PRISM repurposing screens — [25917643](https://figshare.com/articles/dataset/Repurposing_Public_24Q2/25917643)** title **`Repurposing Public 24Q2`**, version **1** — use **`Repurposing_Public_24Q2_LFC_COLLAPSED.csv`** (collapsed log-fold-change sensitivity), **`Repurposing_Public_24Q2_Treatment_Meta_Data.csv`** (map compounds; filter PARP inhibitors and platinum agents by name in protocol), and **`Repurposing_Public_24Q2_Cell_Line_Meta_Data.csv`** (join to DepMap **`Model.csv`** via DepMap model identifiers). Pin file SHA-256 at execution; no full matrices in Git. We did not find a newer **`Repurposing Public`** Figshare record than 24Q2 (Broad DepMap profile search + article API on 2026-11-04). |
| **Licence summary** | DepMap [terms of use](https://depmap.org/portal/terms/) — follow attribution and redistribution rules on download; no redistribution of full matrix in Git. |
| **Deliverable** | Script reading pinned CSV slices (in execution environment only) that prints line counts, mutation counts, and Spearman correlations with bootstrap CIs — fixed seed, aggregate output only. |
| **Feasibility** | **High** for small-team tabular analysis; **low** for translating to patient platinum refractoriness (different endpoint). |
| **Main limitation** | Cell lines ≠ tumors; culture conditions; **correlation ≠ causation**; small ovarian subset within DepMap. |

### 5. Stroma (CAF) expression contrasts in HGSOC (GEO + Yeung et al., 2013)

| Field | Content |
| --- | --- |
| **Question** | Under fixed preprocessing, do laser-captured **cancer-associated stroma** versus **epithelial** expression profiles in **GSE40595** reproduce the stroma-enriched expression patterns described for CAF biology in Yeung et al. (2013) — without claiming patient survival endpoints absent from that paper? |
| **Why it matters** | **KNOWN:** Yeung et al. ([PMID 23824740](https://pubmed.ncbi.nlm.nih.gov/23824740/), [DOI 10.1158/0008-5472.CAN-13-0023](https://doi.org/10.1158/0008-5472.CAN-13-0023)) report that TGF-β upregulates **CAF-derived versican** and modulates **ovarian cancer invasion** in the tumor microenvironment. The PubMed abstract does **not** report survival or outcome analyses. **CONJECTURE:** GEO submitter text for GSE40595 mentions survival correlation; that text is not verified here as a primary outcome claim (GEO series summary vs publication abstract). |
| **Public inputs** | **GEO open tier:** **GSE40595** (verification log). |
| **Licence summary** | GEO series — follow NIH/GEO terms on the accession record before download. |
| **Deliverable** | Normalization script + fixed gene/contrast list + aggregate differential-expression summaries (e.g., rank correlation of stroma–epithelial log fold changes vs a published gene set table), with no CEL files in Git. **Do not** frame deliverables as survival-quartile replication unless a separate protocol cites a primary outcome paper verified from its abstract. |
| **Feasibility** | **Medium:** array preprocessing and probeset mapping dominate. |
| **Main limitation** | Small sample size; microdissection batch effects; invasion biology **in vitro/in silico** ≠ clinical benefit. |

### 6. Multi-histotype ovarian carcinoma expression contrasts (GEO)

| Field | Content |
| --- | --- |
| **Question** | Using **GSE66957**, what reproducible pathway-level contrasts separate ovarian carcinomas from normal surface epithelium — **without** pooling histotypes into a single “ovarian cancer” label? |
| **Why it matters** | **KNOWN:** Histotype (serous, clear cell, endometrioid, mucinous) carries different biology and should not be conflated in biomarker work ([mission](mission.md)). GSE66957 metadata describe mixed ovarian carcinomas versus normals (verification log). |
| **Public inputs** | **GEO open tier:** **GSE66957**. |
| **Licence summary** | GEO open tier; no UK Biobank or controlled-access genomics. |
| **Deliverable** | Script producing ranked pathway scores (e.g., GSEA-style aggregates) with histotype-stratified tables and explicit “not run” stages if labels missing. |
| **Feasibility** | **Medium** with standard array tools; label curation effort. |
| **Main limitation** | Mixed histotypes in one series; custom Rosetta/Affymetrix platform (GPL15048); **exploratory** biology only. |

### 7. mRNA oxidative-stress / fibrosis clustering (GEO)

| Field | Content |
| --- | --- |
| **Question** | In **GSE26193**, does unsupervised clustering or pathway scoring of **mRNA microarray** profiles separate high-grade ovarian adenocarcinoma samples along **oxidative-stress and fibrosis** axes described in the series metadata — under fixed preprocessing? |
| **Why it matters** | **KNOWN:** GEO series metadata state transcriptome analysis of high-grade ovarian adenocarcinomas testing **oxidative stress and fibrosis** pathways (verification log). The series title mentions miRNA, but deposited data are **Expression profiling by array** on **GPL570** (mRNA), not a miRNA platform. The series links [PMID 30244973](https://pubmed.ncbi.nlm.nih.gov/30244973/) (PML/chemosensitivity paper); treat that link as GEO’s citation field — read the abstract before attributing specific pathway claims to that paper. |
| **Public inputs** | **GEO open tier:** **GSE26193**. |
| **Licence summary** | GEO open tier as above. |
| **Deliverable** | Cluster assignment agreement rate (e.g., adjusted Rand) or pathway score correlation vs a **protocol-pinned** figure/table — aggregates only. |
| **Feasibility** | **Medium**; may stall if supplemental gene lists are unavailable — record stop. |
| **Main limitation** | Title/metadata mismatch (miRNA wording vs mRNA array); cluster stability; not a treatment-selection tool. |

### 8. Recruiting interventional trial landscape (ClinicalTrials.gov metadata)

| Field | Content |
| --- | --- |
| **Question** | As of **2026-11-04**, how many **recruiting** **interventional** trials on ClinicalTrials.gov for condition **Ovarian Cancer** fall into phase and keyword buckets (biomarker language, platinum-resistance language) — a descriptive map, not trial enrollment advice? |
| **Why it matters** | **KNOWN:** Trial registries document active research priorities; summarizing them helps researchers see where public evidence is thin. **CONJECTURE:** a frozen aggregate snapshot would help this project prioritize questions — we did not find an existing snapshot in-repo (search: `ClinicalTrials.gov` in `docs/` on 2026-11-04). |
| **Public inputs** | **ClinicalTrials.gov API v2** with exact query (verification log): **`query.cond=Ovarian Cancer`**, **`filter.overallStatus=RECRUITING`**, **`query.term=AREA[StudyType]INTERVENTIONAL`** → **`totalCount=590`** on 2026-11-04. Example first hit: **NCT06404671**. |
| **Licence summary** | U.S. government registry data; follow [ClinicalTrials.gov terms](https://clinicaltrials.gov/about-site/terms-conditions) before bulk reuse. |
| **Deliverable** | Script using the **same query string and date** printing counts and keyword buckets; optional committed **aggregate** JSON (counts only, no patient rows). |
| **Feasibility** | **High** for metadata; **no patient data**. |
| **Main limitation** | Registry text ≠ results; eligibility strings are inconsistent; **not** a substitute for systematic review or care decisions. |

## Directions explicitly excluded here

| Resource | Reason |
| --- | --- |
| **UK Biobank** | Not open; application required — excluded by owner direction. |
| **dbGaP-controlled TCGA**, **EGA** | Controlled access — DAR + owner decision; not planned. |
| **Row-level patient downloads in Git** | Violates [reproducibility and data rules](reproducibility-and-data.md). |

## Verification log (retrieved 2026-11-04)

Sources: [Crossref REST API](https://api.crossref.org/),
[NCBI E-utilities](https://eutils.ncbi.nlm.nih.gov/),
[GEO FTP soft family / acc.cgi text](https://ftp.ncbi.nlm.nih.gov/geo/),
[GDC API](https://api.gdc.cancer.gov/),
[cBioPortal API](https://www.cbioportal.org/api/),
[PDC GraphQL](https://pdc.cancer.gov/graphql),
[Figshare API v2](https://api.figshare.com/v2/articles/27993248) and [25917643](https://api.figshare.com/v2/articles/25917643),
[ClinicalTrials.gov API v2](https://clinicaltrials.gov/data-api/).

### DOI and PMID checks (title + first author must match the citation)

| ID | First author (API) | Title (API) | Cited in direction | Matches claim? |
| --- | --- | --- | --- | --- |
| DOI [10.1016/j.cell.2023.07.004](https://doi.org/10.1016/j.cell.2023.07.004) | Shrabanti Chowdhury (Crossref) | Proteogenomic analysis of chemo-refractory high-grade serous ovarian cancer | 1 | Yes — signature paper |
| DOI [10.1016/j.cell.2024.01.016](https://doi.org/10.1016/j.cell.2024.01.016) | Shrabanti Chowdhury (Crossref) | Proteogenomic analysis of chemo-refractory high-grade serous ovarian cancer | 1 | Yes — same article correction notice |
| DOI [10.1038/nature10166](https://doi.org/10.1038/nature10166) | *(author list omitted on Crossref)*; PubMed lists **Cancer Genome Atlas Research Network** | Integrated genomic analyses of ovarian carcinoma | 2 | Yes — TCGA serous OV paper (Nature 474:609–615) |
| DOI [10.1038/nature11456](https://doi.org/10.1038/nature11456) | Myles R. Allen (Crossref) | Erratum: Corrigendum: Constraints on future changes in climate and the hydrologic cycle | *(not cited)* | **No** — climate erratum; **do not use** for TCGA-OV |
| PMID [21720365](https://pubmed.ncbi.nlm.nih.gov/21720365/) | Cancer Genome Atlas Research Network | Integrated genomic analyses of ovarian carcinoma. | 2 | Yes — pairs with DOI 10.1038/nature10166 |
| PMID [23824740](https://pubmed.ncbi.nlm.nih.gov/23824740/) | Yeung TL | TGF-β modulates ovarian cancer invasion by upregulating CAF-derived versican in the tumor microenvironment. | 5 | Yes for **invasion/CAF/versican**; **no** survival/outcome endpoint in abstract |
| DOI [10.1158/0008-5472.CAN-13-0023](https://doi.org/10.1158/0008-5472.CAN-13-0023) | Yeung (Crossref family name) | TGF-β Modulates Ovarian Cancer Invasion by Upregulating CAF-Derived Versican in the Tumor Microenvironment | 5 | Yes — same paper as PMID 23824740 |
| PMID [30244973](https://pubmed.ncbi.nlm.nih.gov/30244973/) | Gentric G | PML-Regulated Mitochondrial Metabolism Enhances Chemosensitivity in Human Ovarian Cancers. | 7 | GEO link field only — **not** the same as the series title’s miRNA wording; read before citing pathways |

### Accession and registry checks (title + sample count + platform/source)

| Accession / ID | Title (API) | Sample / case count (API) | Platform or source type (API) | Direction | Matches claim? |
| --- | --- | --- | --- | --- | --- |
| **PDC000360** | PTRC HGSOC FFPE Discovery - Proteome | 161 cases / 161 aliquots | Proteome (PDC GraphQL `getPaginatedUIStudy`) | 1, 3 | Yes |
| **PDC000358** | PTRC HGSOC FFPE Validation - Proteome | 21 / 21 | Proteome (PDC GraphQL) | 1, 3 | Yes |
| **PDC000362** | PTRC HGSOC Frozen Validation - Proteome | 66 / 66 | Proteome (PDC GraphQL) | 1, 3 | Yes |
| **TCGA-OV** | Ovarian Serous Cystadenocarcinoma | **608** cases (`projects/TCGA-OV?expand=summary`) | Multi-omic GDC project (open state) | 2 | Yes — **serous**, not all histotypes |
| **ov_tcga_pub** | Ovarian Serous Cystadenocarcinoma (TCGA, Nature 2011) | 489 samples (`allSampleCount`) | cBioPortal study export | 2 | Yes — serous TCGA; note count ≠ 608 cases |
| **ovary_cptac_gdc** | Ovarian Cancer (CPTAC GDC, 2025) | 112 samples | cBioPortal public study | 3 | Yes |
| **GSE40595** | A cancer associated fibroblasts (CAFs) specific gene signature in high grade serous ovarian cancer | 77 series samples (GEO soft) | **GPL570** — [HG-U133_Plus_2] Affymetrix Human Genome U133 Plus 2.0 Array (GEO `acc.cgi?acc=GPL570`) | 5 | Yes |
| **GSE66957** | Pathways of ovarian cancer development | 69 series samples | **GPL15048** — Rosetta/Merck Human RSTA Custom Affymetrix 2.0 microarray (GEO platform soft) | 6 | Yes |
| **GSE26193** | Control of oxidative stress by miRNA and impact on ovarian tumorigenesis | 107 series samples | **GPL570** mRNA array; series type *Expression profiling by array* (GEO soft) | 7 | Yes — **mRNA**, not miRNA platform |
| **Figshare 27993248** | **DepMap 24Q4 Public** | **73** files (API `files?page_size=100`) | DepMap quarterly release (CRISPR, omics, **`Model.csv`**); **no** PRISM LFC matrices in file list | 4 | Yes — omics/annotation half of direction 4 |
| **Figshare 25917643** | **Repurposing Public 24Q2** | **11** files (API `files?page_size=100`) | **PRISM** repurposing dose–response tables (`Repurposing_Public_24Q2_LFC_COLLAPSED.csv`, treatment/cell-line metadata) | 4 | Yes — drug sensitivity half of direction 4 |
| **ClinicalTrials.gov v2** | *(query result set)* | **590** recruiting interventional studies | API query: `query.cond=Ovarian Cancer&filter.overallStatus=RECRUITING&query.term=AREA[StudyType]INTERVENTIONAL` | 8 | Yes — matches interventional wording |

This log does not prove scientific conclusions, licence interpretation for your
jurisdiction, or that downloads will remain unchanged. Re-run the API checks
before executing a protocol that depends on them.
