# Pilot 001: Figure 3D feasibility audit

**Date:** 2026-10-22. **Status:** static source review completed; reproduction
not started. **Decision:** do not start numerical reproduction until the
specific input, method, and rights gaps below are resolved. This advances the
feasibility review in [Pilot 001](../protocols/pilot-001.md), not its scientific
validation. No patient data were ingested, author code executed, or models trained.

The intended contribution is to establish whether a published signature of
primary platinum refractoriness can be reproduced and evaluated on independent
HGSOC patients. A successful reproduction would support further research; it
would not establish a treatment benefit or a cure.

## Evidence boundary

Sources: [S01, original paper](https://doi.org/10.1016/j.cell.2023.07.004),
[S08, author code](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/tree/48357fd63ccbfe3954f38c8efc558b4f88bd6051),
and [S11, correction](https://doi.org/10.1016/j.cell.2024.01.016). Access routes and
limits are recorded in the [source registry](../registries/sources.json).
All observations here were checked on the audit date. Published numbers below
are reference values, not Project Asma results.

The author commit is `48357fd63ccbfe3954f38c8efc558b4f88bd6051`. Its
[recursive Git tree](https://api.github.com/repos/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/git/trees/48357fd63ccbfe3954f38c8efc558b4f88bd6051?recursive=1)
contains 77 entries (62 files), with `truncated: false`. File absence means
absence from that tree only, not unavailability from the authors, supplements,
or another repository. Only the README and three scripts below were inspected
for this audit; this is not a review of every analysis script.

| Inspected script | Git blob SHA |
| --- | --- |
| [Figure_3D_part2.R](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part2.R) | `5f2c2da334d4cd24e2f76244bbdfd2325e9a0a7d` |
| [Figure_3D_part3.R](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R) | `80bdc8117883d4bf66fe1205b31f1215720a8507` |
| [FZ_data_alignment.r](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/FZ_data_alignment.r) | `edf9fb77b47fab2b9938ccdc25ac2723d6089b73` |

These are Git object identifiers, not downloaded data checksums. No source code
or paper full text is redistributed in this repository.

## Published endpoint, cohorts, and evaluation

The paper's STAR Methods, “Patient Selection and Cohorts” (XML section S29),
describes stage III/IV HGSOC treated with primary debulking followed by initial
platinum/taxane therapy. Refractory eligibility includes R0 tumors with
radiographically detectable disease at completion of six cycles, and R1 tumors
with radiographic residual disease progressing or remaining stable after six
cycles. Sensitive eligibility comprises R1/R2 disease treated with primary
resection and adjuvant platinum/taxane, with progression-free survival of at
least two years; R0 tumors are excluded from that sensitive group. Retain these source-specific
surgical-residual categories and response definitions when mapping labels.
They are not interchangeable with later platinum-resistant recurrence.

| Published stage | Reported sample/tumor count | Interpretation |
| --- | --- | --- |
| Discovery profiling | 158 biopsies: 91 sensitive, 67 refractory | Starting profiling cohort, not the prediction denominator. |
| Discovery prediction/selection | 135 tumors: 83 sensitive, 52 refractory | “Feature Selection” (S94) excludes neoadjuvant samples and samples mixing primary/metastatic tumors. Per-reason counts and relationships still need reconciliation. |
| Frozen profiling | 64 tumors: 44 sensitive, 20 refractory | Includes overlap with discovery. |
| Frozen prediction | 34 described as independent; 27 as overlapping after exclusions | Published grouping from “Prediction Performance Evaluation” (S99); not verified patient independence. Class counts for these subsets remain to be established. |
| FFPE validation | 20 tumors: 10 sensitive, 10 refractory | Model re-estimation and threefold CV, not a locked external-model test. |

These are reported sample/tumor counts, not newly verified unique-patient
denominators. S29 reports 13 tumors later found to have received neoadjuvant
therapy; do not attribute the whole 158-to-135 reduction to that category.

“Alignment of proteomics data from Frozen samples to FFPE discovery samples”
(S66) reports **29 overlapping samples plus 14 additional FFPE–frozen pairs from
different primary/metastatic tumors of the same patients**, using all 43 pairs
for alignment. This makes patient linkage an essential unresolved question.
Do not equate the paper's 34 “independent” samples with 34 verified independent
patients, or subtract 14 mechanically: pair multiplicity, exclusions, and
patient relationships have not been reconciled. The published overlap is
disclosed by the authors. Independent evaluation must account for participation
in alignment as well as model fitting.

S94 also removes eight candidate markers because they were undetected in the
frozen/FFPE validation datasets. Thus panel construction used validation feature
availability. This limits a claim of completely untouched external validation;
it does not itself show use of validation outcome labels in that filtering step.

The discovery reference is fivefold CV AUC 0.83 (95% CI 0.77–0.90). Frozen
prediction uses a model trained on the eligible discovery cohort; FFPE
validation re-estimates models with threefold CV. The final ensemble described
in “Prediction Model Building” (S95) is the simple mean of three model probabilities.
The selected refractory/long-term-sensitive groups do not establish population
prevalence, real-world risk calibration, or treatment benefit. AUPRC, Brier score,
and calibration from these cohorts must be interpreted within their selection
scheme.

The correction notice says supplemental figure legends were incorrect or
missing and were corrected online. It does not state that the Figure 3D
performance estimates changed. The corrected supplementary materials have
**not** been pinned or compared here; that remains a protocol-freeze requirement.

## Missing input and environment contracts

Every input filename in this table is absent from the pinned tree. The table
records references in code; it does not assert the contents of any RData object.

| Stage and code locator | Referenced inputs | Evidence needed before execution |
| --- | --- | --- |
| Part 2, lines 1–14 | `balanced_folds.R`; `meta_genes.RData`; `data_prediction_FFPE_UM_primmets.RData`; `senref_FFPE_UM_primmets.RData` | Helper implementation and provenance; origin of `meta`, `genes`, expression matrix and labels; exact eligible population. |
| Part 3, lines 1–13 | `Final_64_proteins.csv`; `data_prediction_FFPE_UM_primmets_noneo.RData`; `senref_FFPE_UM_primmets_noneo.RData`; `data_prediction_UM_Pilot.RData`; `senref_UM_Pilot.RData`; `balanced_folds.R` | Authoritative 64-protein identifiers and `Proteins` column; isolated object inventory for each load; explicit discovery versus FFPE-validation run configuration. |
| Part 3, lines 136–152 | `data_nov.RData`; `senref_nov.RData`; the discovery `noneo` files above | Provenance of `data.nocb.coll.nopool1`, `data.nocb.rib.Frozen`, `senref` and `senref1`; protein/sample ordering; independently verified patient membership. |
| Alignment, lines 2–6 | `FD_GLBLprot_MI_FDbridge_Abund_20201002_Batch_v02.tsv`; `FD_GLBLprot_MI_FDbridge_Abund_20201002_Imput_v02.tsv`; `FZ_GLBLprot_MI_FZbridge_Abund_20201002_Batch_v02.tsv`; `FZ_GLBLprot_MI_FZbridge_Abund_20201002_Imput_v02.tsv` | File releases, terms, checksums, annotation-column schema, matching rules, upstream batch correction and imputation provenance. |

Part 2 writes `rf.RData`, `glmnet.RData` and `xgboost.RData`, then prints a
feature union; it does not write the `Final_64_proteins.csv` consumed by Part 3.
The alignment script writes an aligned TSV, whereas Part 3 consumes RData
objects. The inspected scripts do not establish these conversion steps.
The tree has no `Figure_3D_part1.R`; do not infer its existence or contents from
the numbering.

Part 2 explicitly loads `randomForest`, `glmnet`, `xgboost`, `pROC`, `ggplot2`,
`ggpubr`, and `DiagrammeR`. Part 3 calls functions from the first five without
its own library-loading block. The alignment script uses standard R functions.
R/package versions, a session record, and a dependency lock are not established
by these files; no `renv.lock` is present in the pinned tree. Installing current
versions would not reconstruct the original environment. No license file named
LICENSE or COPYING is present in that tree; reuse rights still require review,
and absence of such a file is not a legal determination.

## Static findings and required resolutions

These are source-level observations and reproducibility questions. They do not
show which code was used for the publication or establish an effect on its
reported results. Preserve the original track and record any correction as an
explicit deviation.

1. **The discovery/FFPE run is not unambiguously selected.**
   [Part 3, lines 5–11](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L5-L11)
   loads discovery and pilot files consecutively into the same environment,
   then uses generic matrix and label names. Whether objects overwrite one
   another cannot be determined without authorized object inventories.
   Require one explicit cohort configuration per run, with label-to-column
   identity checks; do not infer the population from the filename or plot label.

2. **The exact panel cannot be reconstructed from Part 2 as documented.**
   [Part 2, lines 119–148](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part2.R#L119-L148)
   collects `xgb.importance` results, but the shared reducer replaces feature
   names with row names and thresholds `MeanDecreaseGini`; the `Gain` path is
   commented out. That reducer is then applied to the XGBoost output. Resolve
   the intended importance schema and feature identities before regeneration.
   The reducer and elastic-net filter use frequency `>0.4` (lines 144 and 172),
   whereas the paper's STAR Methods, “Feature selection,” says at least 50%.
   Obtain the authoritative panel and selection history; do not tune a threshold
   to make the downstream AUC agree. Part 2 also hard-codes 135 entries in its
   folds (lines 24, 59 and 100), so its input count must be established first.

3. **The plotted CV result is the simple ensemble, not the fitted stack.**
   [Part 3, lines 93–127](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L93-L127)
   computes both a logistic stack and a simple mean of three model probabilities.
   `roc.all1` uses the simple mean, averaged per entry over 100 repetitions;
   the logistic-stack predictions are not its input. Do not pool 100 predictions
   per entry as 100 independent observations. In an authorized run, verify the
   patient grouping and count valid predictions per patient and repeat: an
   elastic-net error breaks the inner loop (lines 51–56), while the final average
   removes missing values (line 123), potentially concealing incomplete repeats.

4. **Training settings and uncertainty need a declared reconciliation.**
   [Part 3, lines 51–81](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L51-L81)
   uses elastic-net alpha 0.2 with three inner folds, XGBoost 100 rounds and
   random forest 100 trees in CV. The frozen block uses 500 rounds and 1,000
   trees (lines 163–173), matching the counts in the paper's model-method
   subsections. Record whether this is intended stage-specific behavior rather
   than silently normalizing it. Outer-repeat seeds are 1–100; random forest
   resets to 1,000,000 within each fold. The paper describes bootstrap AUC
   intervals, but `roc(..., ci=TRUE)` does not explicitly set the CI method.
   Resolve the pinned pROC behavior and separate the AUC interval from the
   `ci.se` sensitivity ribbon. The plot's
   [literal “AUC = 0.83”](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L182-L189)
   is not a numerical check; derive any reproduction annotation from predictions.

5. **Frozen alignment has a coefficient-indexing discrepancy.**
   [Alignment, lines 19–28](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/FZ_data_alignment.r#L19-L28)
   constructs a protein-by-two matrix of intercepts and slopes. The application
   selects `coef.0[2,]` and `coef.0[1,]`, which are rows, rather than the
   per-protein coefficient columns. This does not express the per-protein
   affine transformation implied by the preceding calculation. Obtain the
   intended implementation and establish whether the supplied aligned inputs
   used it; the impact on the published analysis is unknown. Also check zero or
   missing standard deviations, protein order, and the identity-matching rule
   (lines 8–9 use substrings of sample names). A future corrected implementation
   needs a small mathematical check before use with authorized data.

6. **Frozen evaluation does not establish an independent subset in this script.**
   [Part 3, lines 140–179](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L140-L179)
   has a comment referring to both overlapping and non-overlapping samples;
   actual cohort membership depends on loaded objects. `data.nocb.rib.Frozen`
   is used without an explicit construction in the inspected script. Sorting with `match` does
   not prove complete one-to-one protein correspondence. Require verified
   patient linkage, identical ordered feature identities, no unmatched or
   duplicate keys, explicit label encoding, and separate membership lists for
   each reported evaluation. Keep these records in approved private storage.

## Decision record and next executable milestone

The audit establishes specific questions to resolve; it does not close the
[roadmap's](roadmap.md) access or scientific-review gates. No author contact has
been made. The next deliverable is a reviewed, private input/environment manifest
and a frozen analysis specification with the following acceptance evidence:

| Resolution | Acceptance evidence |
| --- | --- |
| Source and reuse | Terms and appropriate authorization for each input and any reused code; repository license decision; corrected supplement version and provenance. |
| Exact target | Endpoint and eligible population; source-confirmed 64-protein list; explicit discovery run; denominator and class counts; AUC aggregation and interval method; predeclared tolerance. |
| Complete inputs | File identifiers, versions and checksums; helper source; each RData object's names, shapes and ordering; transformations from portal/supplement inputs to script inputs. |
| Patient independence | Private patient/specimen/aliquot mapping across all cohorts and alignment pairs; aggregate exclusions and overlap counts; unresolved patients excluded from independent metrics. |
| Methods and environment | Reconciliation of selection threshold, importance reducer, alignment indexing and model settings; reviewed code; R/package versions, seeds and run command; explicit deviations. |

Only after these requirements and the existing scientific-review gate are met
should an authorized small smoke run test input contracts and complete out-of-fold
prediction coverage. Then attempt the specified discovery AUC and a separate
independent-patient evaluation. If essential evidence remains unavailable,
report the narrowed feasibility result rather than inventing replacement data
or claiming a faithful reproduction.

Local `tools/validate.py` and unit tests can check repository structure and links.
They cannot resolve these scientific questions, establish rights, or reproduce
the published numbers. Current executed research results: **none**.
