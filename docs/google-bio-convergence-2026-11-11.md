# Public extract of the 11 November 2026 convergence notes

Three research notes were committed on 11 November 2026. This page keeps the part that belongs in the public repository. That part is arithmetic on counts the notes stated, titles of papers the notes named, and a list of calculations the notes described but did not commit.

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

Titles and DOIs below were read from Europe PMC on 11 November 2026. Residue numbers, binding constants, splicing fractions and prevalence ranges in the notes were not re-extracted.

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

Europe PMC's record PMC12851941 is titled "AlphaGenome: a framework for integrated regulatory variant interpretation" and carries DOI [10.7150/ijbs.133555](https://doi.org/10.7150/ijbs.133555). The notes use AlphaGenome as a method name from DeepMind. This page does not treat that PMC record as that method.

The notes also name AlphaFold 3, AlphaProteo and Cell2Sentence-Scale. This page does not add a methods citation for those names. Chowdhury et al. remains the existing source for the cohort counts already audited.

## Proposals that were not re-run

The notes join four ideas. HLA pocket chemistry, tissue-specific EEF1D splicing, chromosome 17 co-location of platinum-sensitivity regions with CDR2L, and a blood index that compares CA-125 with hemoglobin, the neutrophil-to-lymphocyte ratio, LDH and platelets.

They name a Python file, `project_asma_verification_and_clinical_kinetics.py`, and these entry points:

- `audit_pilot_001_complete`
- `run_alphagenome_alphafold_er_interactome_model`
- `run_spatial_hgsoc_clonal_divergence_simulation`
- `run_purkinje_anti_yo_neuro_immuno_simulation`

A second note names `spatial_hgsoc_clonal_divergence.py` and `purkinje_anti_yo_er_homeostasis.py`. None of those files was in the commit. Binding constants, occupancy percentages and simulator endpoints in the notes are not results of this repository. They are not a regimen.

## Boundary

No private-archive identifier, image name, correspondence or row-level measurement is on this page. The claim rows for this extract are V31, K34, K35 and C23 in the [claims ledger](../CLAIMS.md).
