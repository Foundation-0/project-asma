# Pilot 001: preprocessing provenance

Follow-up: the [reconstruction decision record](pilot-001-reconstruction-decisions.md)
(2026-10-25) declares the replacement choices for the gaps recorded below
without resolving the historical discrepancies. The observations below are
preserved as of 2026-10-23.

**Checked:** 2026-10-23. **Evidence class:** read-only source inspection.
The recovered discovery matrix has a candidate patient-label bridge; its exact
generation and conversion into the prediction workspaces remain unverified.
The following instructions are visible in source code, not an executed history
of the released file. No author code was executed or copied into this repository.

All code locators use author commit
`48357fd63ccbfe3954f38c8efc558b4f88bd6051`. Article paragraph identifiers refer to
the [pinned XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC10414761.1/PMC10414761.1.xml),
449,678 bytes, SHA-256
`1d88848c7b3dcda6f6b7734922f2f75b0ddeb0796d682d900d68cc2ffddd187b`.

## Located steps and limits

| Stage | Source evidence | Limit for reconstruction |
| --- | --- | --- |
| Quantification | Article P135–138 describes protein inference, unique/razor peptides, 1% protein FDR and TMT-Integrator summaries. | Does not establish protein-group interpretation or mapping to original workspace row names. |
| Input and naming | [Rmd 42–54](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocess_markdown.Rmd#L42-L54) reads `FFPE_abund.tsv`, separates columns `1:5,237`, loads an absent annotation CSV and calls `col.name`. | The old positional schema does not describe the recovered 178-column file. Earlier data labels and `Process.ID` remain unavailable. |
| Scale and normalization | Article P142 removes reference bridges, aligns medians and scales median absolute deviations. [Function 51–96](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocessing.R#L51-L96) uses target mean medians/MADs across samples. | Rmd 58 says median alignment is already done; neither this function nor the log2-ratio function at 27–47 is called there. Their presence does not establish the recovered file's scale. |
| Plex outliers | [Function 101–136](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocessing.R#L101-L136) removes bridge-pattern columns and compares each protein's plex with remaining plexes using equal-variance t-tests, marking significant plex observations missing. | Rmd 78 uses **10^-10**, whereas article P143 specifies **10^-7**. The archive-generating choice is unknown. |
| Missingness filter | [Function 141–165](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocessing.R#L141-L165) retains the union having missing fraction **<0.5 in sensitive OR refractory samples**. Article P144 clarifies this OR rule. | This is label-dependent filtering before model splitting in the displayed workflow. Label alignment and the actual fitting population must be established. |
| Batch correction | [Function 263–286](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocessing.R#L263-L286) temporarily imputes with KNN, applies ComBat using plex membership, then restores original missing positions. | No fold-specific fitting is shown. Package versions and the actual archive-generating invocation are absent. |
| Final imputation | [Rmd 108–142](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocess_markdown.Rmd#L108-L142) invokes DreamAI, appends annotations and exports `FFPE_UM_imputed.tsv`. | It creates `data.batch.corrected` but passes `data`; stores `result.impute` but reads `result$Ensemble`. The export name differs from the recovered archive member. |
| Replicate averaging | [Commented example 295–328](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocessing.R#L295-L328) starts from `result$Ensemble`, averages five groups per protein, keeps each first column, removes the others and saves `FFPE_imp_coll.RData`. | This supports an after-imputation arithmetic-mean example, not verified execution or the prediction-workspace generator. |
| Prediction features | [Part 3, 1–11](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L1-L11) selects panel membership from matrix row names after loading RData. Part 2 uses absent `genes` and `make.names(..., unique=TRUE)`. | Neither provides the archive-annotation conversion, biological duplicate rule or explicit panel ordering. Syntactic renaming is not a protein-identity rule. |

The provisional KNN call specifies `k=10`, `rowmax=.9`, `colmax=.9`,
`maxp=nrow(data)` and `rng.seed=362436069`. The displayed DreamAI call specifies
KNN, MissForest, ADMIN, Brinn, SpectroFM and RegImpute; `k=10`, `maxiter_MF=10`,
`ntree=100`, `maxnodes=NULL`, `maxiter_ADMIN=30`, `tol=.01`, `gamma_ADMIN=0`,
`gamma=50`, `CV=TRUE`, `fillmethod="row_mean"`, `maxiter_RegImpute=10`,
`conv_nrmse=1e-6`, `iter_SpectroFM=40`, ensemble output, `SamplesPerBatch=8`,
`n.bag=1` and `ProcessNum=1`. These are source-visible choices, not verified
parameters for the released matrix; they must not be silently treated as a
recovered environment or complete executable specification.

## Replicate identity and the missing workspace bridge

The published clinical annotations contain **five groups of three measurements**
and **153 singleton samples**: 168 measurement rows represent 158 unique explicit
samples/patients. The five repeated groups explain the ten additional measurements.
The commented averaging example instead locates groups using `Process.ID`, which
is absent from the clinical sheet. An exploratory exact-literal comparison found
no whole-string matches between its five group literals and the recovered
headers, repeated sample keys or repeated patient keys. No expressions were
evaluated and no string normalization was inferred.

The inline comment examples also do not match the recovered labels exactly.
Some examples list only two labels; they do not establish the actual cardinality
of historical groups. The example averages with `na.rm=TRUE`, assigns row names
from another object's `Index`, and is entirely commented out. Its availability
does not validate a replicate partition or show which file received those means.
An unrelated immune-clustering script averages repeated patient measurements
using different inputs; it does not resolve this prediction workflow.

The literal comparison was exploratory and is not a retained runnable audit.
It reverified the pinned clinical workbook, archive header and source file.
For `preprocessing.R`, Git blob is
`b555df2041d576f7f5a412e2b82c3cb22c291790` and SHA-256 is
`44e927c85b878f037b61826ed2cfd526b670c71fc78b562c152b3425464e88de`.
Only aggregate findings are retained.

Targeted searches across all **42 R/r/Rmd files** at the pinned commit found no
reference to `FFPE_discovery_globalprotein_imputed.tsv`, no generator for the
discovery `*_primmets_noneo.RData` workspaces, and no assignment creating
`data.nocb.coll.nopool`. These are bounded negative searches, not proof that the
missing history never existed.

## Consequence for independent progress

The sequence is partly documented: normalization, plex outlier handling,
label-dependent filtering, temporary imputation, batch correction, missingness
restoration, final imputation and a commented averaging example. The exact
archive-to-workspace chain is still missing. The 10^-7/10^-10 discrepancy and
object-name mismatches must be preserved as unresolved choices, not repaired
silently to obtain agreement with the published AUROC.

A future reconstruction can define averaging groups from explicit published
sample keys, verify patient grouping, and enforce ordered feature identities.
Those would be declared reconstruction choices. It cannot claim to recover the
historical workspace merely because all panel symbols are present.

Any CV using the released, already processed matrix retains unresolved upstream
fitting scope. Label-dependent filtering or imputation fitted outside folds
cannot be made training-only by changing the later split helper. A fully
training-only evaluation requires sufficiently upstream inputs and a separately
fixed processing plan. See the
[reconstruction contract](../protocols/pilot-001-independent-reconstruction.md).
