# Public extract of the 11 November 2026 convergence notes

Three research notes were committed on 11 November 2026. This page keeps the part that belongs in the public repository. That part is arithmetic on counts the notes stated, a comparison of those counts with the existing supplement audit, and sentences checked in papers the notes named. Calculations the notes described but did not commit stay listed as proposals.

The notes also contained a private clinical section and routing instructions. Those are not copied here. No study file was read for this page. Nothing here is a diagnosis or a treatment recommendation.

## Counts the repository already checked

The discovery comparison is unchanged. The audited discovery cohort has 83 platinum-sensitive patients and 52 primary platinum-refractory patients, which is 4,316 pairs. Mann-Whitney U is 3,491. The exact AUROC is 3,491 / 4,316 = 0.8088507878.

That check is recorded in the [discrepancy analysis](pilot-001-auc-discrepancy.md) and as K07 in the [claims ledger](../CLAIMS.md). The printed 0.83 remains outside the 0.02 tolerance.

One note factorized the same 4,316 pairs as 166 by 26. Both products equal 4,316. The audited split is 83 by 52, not 166 by 26.

That note reported intervals for a set of 192 and a set of 100. The 192 intervals match the two-sided 95% Clopper-Pearson intervals for 9/26 and 163/166. The 100 intervals match the same kind of interval for 7/20 and 78/80.

The command in the next section recomputes them. They are intervals for those fractions. They are not adopted as the discovery operating point. This page does not check the notes' "FHCRC" label against the paper.

The notes' list of possible causes for the 0.83 gap repeats the existing analysis. Ties, score direction, ordinary rounding and the usual AUC formulas were already checked. Averaging fold-wise curves remains open (C20 in the claims ledger).

## Specificity bounds on stated denominators

For a sensitive-patient count n and k false positives, the one-sided 95% lower bound is the largest L such that the chance of at least n minus k successes is 0.05. With zero false positives this is 0.05 raised to 1/n. That is the same quantity as the [validation-capacity record](pilot-001-validation-capacity.md).

| Stated n | Relation to audited counts | 0 false positives | 1 false positive | 2 false positives |
| --- | --- | ---: | ---: | ---: |
| 10 | Not an audited count here | 74.11% | 60.58% | 49.31% |
| 13 | Sensitive count for the candidate with no observed discovery record. That record's refractory count is 8 | 79.42% | 68.37% | 58.99% |
| 22 | Sensitive count of the published frozen nonoverlap score set. That audit's refractory count is 12, not 20 | 87.27% | 80.19% | 74.05% |
| 44 | Not an audited count here | 93.42% | 89.67% | 86.37% |
| 83 | Discovery sensitive count. The audited refractory count is 52 | 96.46% | 94.41% | 92.61% |
| 115 | Not an audited count here | 97.43% | 95.94% | 94.63% |
| 149 | Smallest n whose zero-false-positive bound reaches 98%. Not an observed cohort | 98.01% | 96.86% | 95.84% |
| 236 | Smallest n whose one-false-positive bound reaches 98%. Not an observed cohort | 98.74% | 98.01% | 97.36% |

Zero-false-positive cells match the notes after rounding to two decimals, except 96.455%, which this table shows as 96.46%. The notes' other cells differ from this tail by at most 0.94 percentage points. This table is the recomputed tail. These bounds assume a perfect or nearly perfect outcome on a stated denominator. They are not measured specificity.

Run from the repository root:

```sh
python3 tools/check_stated_specificity_bounds.py --check
python3 -m unittest tests.test_stated_specificity_bounds -v
```

## Papers named in the notes

Titles and DOIs below were read from Europe PMC on 11 November 2026. Residue sentences, three abstracts and the AlphaGenome record were checked later the same day. Binding constants, splicing fractions, occupancy percentages and the notes' prevalence range were not adopted.

| What the notes used it for | Year | Title | Record |
| --- | --- | --- | --- |
| CDR2, kinectin and ER sheets | 2025 | CDR2 is a dynein adaptor recruited by kinectin to regulate ER sheet organization | [10.1083/jcb.202411034](https://doi.org/10.1083/jcb.202411034) |
| Kinectin and the multi-tRNA synthetase complex | 2026 | Variant-specific interaction of kinectin 1 with the multi-tRNA synthetase complex regulates ER sheet organization | [10.1016/j.isci.2025.114303](https://doi.org/10.1016/j.isci.2025.114303) |
| EEF1D splicing | 2026 | The ER anchoring and abundance of the EEF1B complex is affected by tissue-specific alternative EEF1D splicing | [10.26508/lsa.202503513](https://doi.org/10.26508/lsa.202503513) |
| Anti-Yo HLA association | 2018 | Complex HLA association in paraneoplastic cerebellar ataxia with anti-Yo antibodies | [PMID 29306402](https://pubmed.ncbi.nlm.nih.gov/29306402/) |
| Missense effect scores | 2023 | Accurate proteome-wide missense variant effect prediction with AlphaMissense | [PMID 37733863](https://pubmed.ncbi.nlm.nih.gov/37733863/) |
| Spatial proteomics survey | 2025 | Spatially resolved proteomics surveys the chemo-refractory proteins related to high-grade serous ovarian cancer | [10.1002/ctm2.70422](https://doi.org/10.1002/ctm2.70422) |
| Breast carcinomas and anti-Yo disease | 2022 | Immune and Genetic Signatures of Breast Carcinomas Triggering Anti-Yo-Associated Paraneoplastic Cerebellar Degeneration | [10.1212/nxi.0000000000200015](https://doi.org/10.1212/nxi.0000000000200015) |
| CDR2 and CDR2L review | 2024 | Roles of CDR2 and CDR2L in Anti-Yo Paraneoplastic Cerebellar Degeneration: A Literature Review | [10.3390/ijms26010070](https://doi.org/10.3390/ijms26010070) |
| Ovarian cancer etiology review | 2022 | An Etiological Investigation of Paraneoplastic Cerebellar Degeneration in Ovarian Cancer Patients: A Systematic Review | [10.7759/cureus.31154](https://doi.org/10.7759/cureus.31154) |

The notes also name AlphaFold 3, AlphaProteo and Cell2Sentence-Scale. No methods citation is added for those names. Chowdhury et al. remains the existing source for the cohort counts already audited.

## Stated cohort pairs against the supplement audit

The notes named six sensitive and refractory pairs. The command in the specificity section also reads the [supplement audit](../registries/pilot-001-supplement-summary.json) and checks the fields this table cites. It does not open a study workbook.

| Notes' name | Notes | Audit field | Audit counts |
| --- | --- | --- | --- |
| FFPE validation | 10 / 11 | FFPE_valid_pred_scores | 10 / 10 |
| Frozen independent, no neoadjuvant | 22 / 20 | Frozen_nonoverlap_pred_scores | 22 / 12 |
| Full frozen validation | 44 / 42 | Frozen_clinical class counts. Eligible counts are separate | 44 / 20. Eligible counts are 42 / 19 |
| FFPE discovery | 83 / 52 | FFPE_pred_scores and the eligible discovery counts | 83 / 52 |
| All non-overlapping cohorts | 115 / 83 | No class-count pair in the summary | Not present |
| Frozen subset | 13 / 8 | No class-count pair in the summary | [K31](../CLAIMS.md) records this split among 21 frozen patients with no discovery record |

Counts are sensitive, then refractory. The discovery clinical sheet has 168 response-labelled measurement rows. The discovery score sheet has 135 patient keys. The panel list has 64 symbols. Those three figures match the audit. K11 records the 64 symbols among 8,800 feature rows. The unfiltered discovery clinical sheet is 91 / 67, so 83 / 52 is the eligible pair, not every labelled row.

One note calls 0.818 a Table S3 summary. A Europe PMC search for PMC10414761 and the string 0.818 returned no article. In this repository, 0.8181818 is the fraction 9/11 on the [validation-capacity grid](../registries/pilot-001-validation-capacity.json). It is not a discovery AUC.

Only the 83 / 52 pair matches the audit on both numbers.

## Sentences checked in the named papers

The PMC page for the 2025 kinectin paper, [10.1083/jcb.202411034](https://doi.org/10.1083/jcb.202411034), was read on 11 November 2026.

The CC1 box deletion is residues 23-39. CDR2 residues 1-146 form a complex with dynein light intermediate chain residues 388-523. The C-terminal CDR2 helix 404-454 localizes to ER sheets. One deletion of the kinectin binding site is 1114-1153. A later experiment deletes 1114-1157. The notes' span 1114-1157 matches the second deletion.

The paper says residues 33-60 of eEF1Bβ, the beta subunit of elongation factor eEF1B, are predicted to occupy the same kinectin site. It identifies that subunit as UniProt P29692, encoded by EEF1D. The binding experiment uses residues 30-66. The paper places HBS1 about 30 residues after the CC1 box. It does not call residues 23-145 the HBS1 motif.

The kinectin-complex abstract says the complex has eight aminoacyl-tRNA synthetases and three other proteins, and that exon V2 and QARS are required to recruit it to the ER. The abstract does not give an N-terminal domain, a UniProt accession for QARS, or a chromosome 14 window.

The EEF1D abstract says exon 5 is required for anchoring to kinectin and RRBP1. It does not give a splicing fraction or a chromosome 8 window.

The 2018 HLA abstract reports an odds ratio of 5.4 for DRB1*13:01~DQA1*01:03~DQB1*06:03 in ovarian cases, and an odds ratio of 0 for DRB1*04:01~DQA1*03:03. Both are given with p = 0.0016. The notes' range 5.4-8.87 is not that abstract.

The breast-cancer abstract says all 22 anti-Yo breast cancers in that study had at least one CDR2L alteration. A 59 to 65 percent figure in the notes is not that sentence.

## AlphaGenome record and the CDR2L span

PMC12851941 is Avsec and colleagues, Nature, 2026, PMID 41606153, DOI [10.1038/s41586-025-10014-0](https://doi.org/10.1038/s41586-025-10014-0). PubMed and the PMC article page agree. The abstract states an input of 1 Mb of DNA. A text search of that PMC page found no CDR2, no EEF1D, no Purkinje, and neither base-pair window named in the notes.

NCBI Gene 30850 places human CDR2L on NC_000017.11 at 74,987,631-75,005,799, in band 17q25.1. The notes' interval 74,992,096-75,021,497 is on chromosome 17 in the same band. It is a different base interval.

## Proposals that were not re-run

The notes join four ideas. HLA pocket chemistry, tissue-specific EEF1D splicing, chromosome 17 co-location of platinum-sensitivity regions with CDR2L, and a blood index that compares CA-125 with hemoglobin, the neutrophil-to-lymphocyte ratio, LDH and platelets.

They name a Python file, `project_asma_verification_and_clinical_kinetics.py`, and these entry points:

- `audit_pilot_001_complete`
- `run_alphagenome_alphafold_er_interactome_model`
- `run_spatial_hgsoc_clonal_divergence_simulation`
- `run_purkinje_anti_yo_neuro_immuno_simulation`

A second note names `spatial_hgsoc_clonal_divergence.py` and `purkinje_anti_yo_er_homeostasis.py`. None of those files was in the commit. Binding constants, occupancy percentages and simulator endpoints in the notes are not results of this repository. They are not a regimen.

## Boundary

No private-archive identifier, image name, correspondence or row-level measurement is on this page. The claim rows for this extract are V31, V32, K34, K35, K36, K37 and C23 in the [claims ledger](../CLAIMS.md).
