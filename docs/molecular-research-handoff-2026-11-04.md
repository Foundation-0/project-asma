# Molecular research handoff: 2026-11-04

**Status: public-source evidence review and proposed work; no study analysis.**
This preserves molecular avenues considered under the expanded [mission](mission.md).
It complements the [broader handoff](research-handoff-2026-11-04.md), without
changing [Pilot 001](../protocols/pilot-001.md). **KNOWN** denotes cited external
evidence; **CONJECTURE** denotes our research questions and prioritization.
Access date: **2026-11-04**. No private correspondence, individual target
assignment, study dataset, or treatment recommendation is included.

## Keep measurements and mechanisms distinct

**CONJECTURE — proposed evidence schema:** record specimen, sampling date/site,
assay, measured entity, threshold, treatment context, endpoint and uncertainty.
Separate serum antigen, tumor membrane protein, RNA abundance, copy number,
mutation, antibody recognition, pathway activity and perturbation response.
None should silently substitute for another. Separate primary refractory
disease from acquired resistance, and histotypes from one another.

**KNOWN:** CA-125 assays concern MUC16-associated antigen; work targeting an
unshed MUC16 region addresses a different measurement and molecular context.
[Primary experimental source](https://pubmed.ncbi.nlm.nih.gov/32403071/).
A serum result cannot establish expression of a particular accessible tumor
epitope or prove a causal resistance mechanism. **CONJECTURE:** an assay-aware
evidence map is a tractable contribution before a new predictive model.

## CDR2L perturbation and tumor–neuron questions

**KNOWN — preclinical:** Solheim et al., *BMC Cancer* 24:645 (2024),
[10.1186/s12885-024-12399-z](https://doi.org/10.1186/s12885-024-12399-z),
reports OVCAR-3 CDR1/CDR2/CDR2L knockout multiomics. CDR2L loss affected
ribosome/translation and cell-cycle programs and impaired proliferation.
One cell-line background, clone effects, absent rescue validation and absent
Purkinje-neuron experiments limit interpretation. Knockout, antibody binding
and drug inhibition are different interventions.

The [author repository](https://github.com/ETSunhome/Multi_omics_profiling_of_knockout_of_CDR2L)
lists RNA, proteome and secretome inputs plus `preprocess.Rmd`, `GSEA.Rmd`
and `analysis.Rmd`. README and full GPLv3 license were inspected; study inputs
were not downloaded and analysis code was not executed. Repository licensing requires deliberate review
before code reuse; this project has no blanket third-party license grant.

**CONJECTURE — first bounded question:** which CDR2L-associated changes survive
alternative missing-protein handling, enrichment backgrounds and comparison
with CDR1/CDR2 loss? Distinguish generic slower proliferation from a specific
CDR2L mechanism. Stop a target claim without independent perturbation/rescue
evidence and a tumor-versus-neuron safety assessment. A reproducible negative
finding remains useful.

**KNOWN — human tumor profiling:** Vialatte de Pémille et al., *British Journal
of Cancer* 119:105–113 (2018),
[10.1038/s41416-018-0125-7](https://doi.org/10.1038/s41416-018-0125-7),
studied 12 anti-Yo PCD ovarian tumors. The article identifies ArrayExpress
`E-MTAB-5942` and [Figshare R scripts/supplements](https://figshare.com/projects/CVDP_antiYo_PCD_transcriptome/23503).
Public comparator tumors were presumed non-PCD because the syndrome is rare.
**CONJECTURE:** audit platform, tissue processing and cohort confounding before
interpreting classification performance. Patient-derived data and individual
Figshare licenses require separate assessment; none was acquired here.

**KNOWN — mechanistic caution:**
[Kråkenes et al. (2019)](https://doi.org/10.1002/ana.25511) identifies CDR2L
as the major endogenous Yo antigen; related CDR2 remains relevant to assay
interpretation. [Yshii et al. (2019)](https://doi.org/10.1172/jci.insight.127001)
demonstrated timing-dependent separation of neuronal protection and tumor
control with IFNγ blockade in an artificial shared-antigen mouse model.
That model is not native CDR2L ovarian disease or human treatment evidence.

[Vorasoot et al. (2023)](https://doi.org/10.3389/fimmu.2023.1265797) preserves
the assay-confirmation lead: isolated antigen-test reactivity needs appropriate
context and confirmation. [Farina et al. (2025)](https://doi.org/10.1177/17562864251377559)
reports five selected anti-Yo neurological cases after checkpoint inhibitors.
This cannot estimate incidence or determine treatment, but prevents assuming
that stronger antitumor immune activation is automatically neurologically safe.

## Protein targets: clinical evidence, sampling and eligibility

**KNOWN — United States regulatory notices, not worldwide approvals:**

| Pathway or assay | Dated evidence and essential boundary |
| --- | --- |
| FOLR1 / folate receptor alpha | [FDA, 2024-03-22](https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-mirvetuximab-soravtansine-gynx-fra-positive-platinum-resistant-epithelial-ovarian): regular approval of mirvetuximab for specified FRα-positive platinum-resistant disease after one to three regimens; approved tissue assay required. |
| ERBB2 / HER2 | [FDA, 2024-04-05](https://www.fda.gov/drugs/resources-information-approved-drugs/fda-grants-accelerated-approval-fam-trastuzumab-deruxtecan-nxki-unresectable-or-metastatic-her2): accelerated tumor-agnostic trastuzumab deruxtecan indication for HER2 IHC3+ unresectable/metastatic solid tumors after prior systemic treatment without satisfactory alternatives. An ERBB2 RNA value is not that criterion. |
| PD-L1 | [FDA, 2026-02-10](https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-pembrolizumab-paclitaxel-platinum-resistant-epithelial-ovarian-fallopian-tube-or): pembrolizumab plus paclitaxel, with or without bevacizumab, for specified platinum-resistant disease, PD-L1 CPS ≥1 and one or two prior regimens. |
| Glucocorticoid receptor pathway | [FDA, 2026-03-25](https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-relacorilant-nab-paclitaxel-platinum-resistant-epithelial-ovarian-fallopian-tube-or): relacorilant plus nab-paclitaxel after one to three prior regimens including bevacizumab; the notice does not require a receptor-expression companion assay. |

These are research-context summaries, not complete prescribing information or
individual eligibility determinations. Recheck current labels and jurisdiction
before any future clinical-evidence resource is released.

**KNOWN — sampling evidence:** Li et al., *British Journal of Cancer* 135:717–727
(2026), [10.1038/s41416-026-03482-2](https://doi.org/10.1038/s41416-026-03482-2),
reports spatial/temporal ADC-target heterogeneity, including changes in FRα
classification with sampling. Data access is by request.
**CONJECTURE:** map assay thresholds, sampling sites and intervals; test whether
a proposed interpretation depends on one historical specimen. Do not build a
replication plan that assumes the underlying tissue data are open.

**KNOWN — exploratory multiomics:** the DECIDER report,
[10.1038/s43856-026-01879-x](https://doi.org/10.1038/s43856-026-01879-x)
(2026-09-08), characterizes ADC targetability and heterogeneity. RNA expression
is not clinical protein-assay eligibility. Referenced EGA accessions
`EGAS00001006775`, `EGAS00001004714` and `EGAS00001005010` are controlled-access
routes, not an immediately executable open-data project.

**KNOWN:** CDH6- and B7-H4/VTCN1-directed ADC programs remain investigational leads
in this review. [R-DXd trial NCT06161025](https://clinicaltrials.gov/study/NCT06161025)
and the [NCI mocertatug rezetecan trial listing](https://www.cancer.gov/research/participate/clinical-trials/intervention/anti-b7-h4-top1i-antibody-drug-conjugate-gsk5733584)
illustrate prospective evaluation; target expression, early activity and
sponsor announcements do not establish comparative benefit or approval.

## Replication stress and adaptive resistance

**KNOWN — preclinical:**
[10.1038/s41467-025-58183-w](https://doi.org/10.1038/s41467-025-58183-w)
investigates PKMYT1/ATR inhibition in CCNE1-amplified models. Copy-number
amplification, cyclin E1 protein assays and BRCA/HRD measurements answer
different questions. [ASPENOVA](https://www.cancer.gov/research/participate/clinical-trials-search/v?id=NCI-2026-06153)
is prospective azenosertib/WEE1 research, not established biomarker-directed
benefit. **CONJECTURE:** specify the assay and acquired-resistance endpoint
before comparing replication-stress signatures.

**KNOWN — preclinical:** Raivola et al., *Cell Death & Disease* 17:276 (2026),
[10.1038/s41419-026-08501-x](https://doi.org/10.1038/s41419-026-08501-x),
studies ROR1–PI3K/AKT-associated adaptation to cell-cycle blockade. The
[Mendeley version-1 record](https://data.mendeley.com/datasets/dd6bvtrv9b/1)
lists single-cell and imaging-related material under CC BY 4.0; the
[author code repository](https://github.com/ungureanulab/OC-resistance-profiling)
was identified, but code-license suitability was not established.
**CONJECTURE:** reproduce one adaptive-state contrast and test growth-rate,
cell-line and modality dependence. Drug-adapted models do not automatically
represent clinical acquired platinum resistance. Stop without suitable
comparators, replication units or input rights.

## Small paired ascites study and continuation

**KNOWN — exploratory:**
[10.1002/prca.70053](https://doi.org/10.1002/prca.70053) (2026) compares
primary/recurrent ascites proteomics in three patients, with immune/metabolic
differences. Technical replicates do not increase the independent patient count.
The paper reports PRIDE `PXD073562`; portal accessibility and file-specific
terms were not independently verified. **CONJECTURE:** a paired descriptive
robustness study may be feasible; classifier validation is unsupported at this
scale. Cell composition and treatment history remain alternative explanations.

Review depth was primary abstracts/indexed article passages and availability
statements, with CDR2L full article/README/license and Mendeley metadata inspected
more closely. FDA notices were reviewed directly. No listed study dataset or
third-party analysis code was run. Exact-DOI correction/retraction searches for
the CDR2L knockout, 2018 transcriptomic, PKMYT1/ATR, heterogeneity, DECIDER,
ROR1 and ascites papers found no notice in returned
results; this is not an exhaustive clearance. Recheck versions, corrections,
access and licenses before protocol selection.

Next work should select one uncertainty, baseline and stop rule, then record a
new protocol and source/claim entries. Follow [Gate 0](roadmap.md) and
[data rules](reproducibility-and-data.md) before study-file acquisition or
analysis. Metadata availability does not close those gates. No author contact,
data request or clinical deployment is authorized by this handoff.
