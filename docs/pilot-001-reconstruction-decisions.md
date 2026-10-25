# Pilot 001: reconstruction decision record

**Version:** 0.1, 2026-10-25. **Status:** declared choices for the prospective
public-input reconstruction; nothing fitted. **Evidence class:** read-only
source inspection, one metadata-only archive directory listing, and offline
software contracts tested with abstract tokens. External outreach remains on
hold; external scientific review remains pending.

This record completes the step named in the [roadmap](roadmap.md): translate
the [located preprocessing steps](pilot-001-preprocessing-provenance.md) and the
[score lineage](pilot-001-independent-progress.md) into explicit choices for
feature interpretation, replicate averaging, ordering, fit scope and
replacements for the missing helper, workspaces and environment. Every decision
below separates **source evidence**, the **unresolved history** it cannot
recover, the **declared choice**, and what the choice **does not claim**. The
[reconstruction contract](../protocols/pilot-001-independent-reconstruction.md)
remains the governing specification; this record supplies its decisions.

The declared conventions that need no data are implemented in
[reconstruction_contracts.py](../tools/reconstruction_contracts.py) and
exercised by offline tests. The command below prints them with the SHA-256 of
this record and of the contract, for the later freeze. It reads no data.

```sh
python3 tools/reconstruction_contracts.py
```

No abundance value was read, no model was fitted and no performance result
exists for this reconstruction. The executed supplied-score AUROC
**0.8088507878** is unchanged.

## Source pins for this record

Author code was re-fetched read-only on 2026-10-25 at commit
`48357fd63ccbfe3954f38c8efc558b4f88bd6051`; nothing was executed or copied.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| [Figure_3D_part3.R](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R) | 7,326 | `c1327f639739f3cea548824b4602bc6f5efd12321b7bb2ec3d06f06a6ba470e1` |
| [Figure_3D_part2.R](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part2.R) | 4,222 | `4ca3b6cd026d2d1305b7c9d207a82293195c0cc3cc18f5191466afc6ec0b721a` |
| [preprocessing.R](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocessing.R) | 12,512 | `44e927c85b878f037b61826ed2cfd526b670c71fc78b562c152b3425464e88de` |
| [preprocess_markdown.Rmd](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocess_markdown.Rmd) | 4,254 | `c62f99b098c136c5b04a24b570622e15dfe929e53ed3e35c5251d93635c5a080` |

The `preprocessing.R` hash equals the value recorded on 2026-10-23. The
recovered input remains the author archive member
`FFPE_discovery_globalprotein_imputed.tsv` (member SHA-256
`b7eea435bb7fa65f31a6e8f50d977ff046f0f9bd851126e43cf9a5f52e62be62`, CRC32
`9f713751`, header SHA-256
`e39ef0ffaafaa92ca6dd7351ed578856be22f4e03b2cf26111106790bd7521c9`), with
the panel at canonical SHA-256
`77329920b86dacaffc6778ed7e7c6b827683beed1aad7f2229b8bafe2f535144`.

## Decisions

### D1. Cohort, run selection and fold count

**Source evidence.** Part 3 loads the discovery and FFPE-pilot workspaces into
one environment (lines 5–9) and runs five folds unconditionally (lines 23–45).
Methods S99 specify fivefold discovery CV with 83 sensitive and 52 refractory
tumors. The published 135-key discovery score set joins exactly to clinical
rows and equals the literal no-neoadjuvant/non-`Mix` reconstruction.

**Unresolved history.** Which loaded objects survived the consecutive loads
cannot be established without the absent workspaces.

**Declared choice.** Discovery only: the 135 published score keys, 52
refractory and 83 sensitive, five folds, 100 repetitions. Membership is fixed
by exact clinical joins before any model call, and the run stops if the three
counts differ. The one retained record with location group `NA` stays in the
cohort and is reported, as in the executed score check. The FFPE-pilot
threefold evaluation and the frozen cohort are outside this reconstruction.

**Not claimed.** That this equals the original fitting population in every
measurement-level detail, or that excluded samples did not shape upstream
preprocessing (see D9).

### D2. Input columns and the unclassified header column

**Source evidence.** The imputed member has 178 header columns: nine named
annotation fields, 168 columns that equal response-labelled clinical labels
exactly, and one further column without an exact clinical label.

**Unresolved history.** The 63 clinical-`NA` rows match no header column, so
at most one of them could correspond to the single unmatched column; the
identity of that column is not established by any inspected source.

**Declared choice.** Use only the 168 exactly matched measurement columns and
the `HGNC symbol` annotation field. The remaining column must be explicitly
classified from a documented source before a run; until then its presence is a
recorded fact and it is never read as a measurement, a bridge, a pool or a
patient. No substring, positional or pattern-based column assignment is used.

**Not claimed.** Equivalence of these columns to the absent workspace object
`data.nocb.coll.nopool`, or to the raw PDC matrix of 237 columns.

### D3. Feature interpretation and order

**Source evidence.** Part 3 selects rows with `which(rownames(...) %in% com)`
(line 11), which keeps the matrix row order and would silently keep duplicate
row names. Every one of the 64 panel symbols occurs exactly once among the
8,800 `HGNC symbol` values of the recovered member. All 64 matched rows carry a
delimiter in their protein-accession annotations.

**Unresolved history.** The original workspace row names, their mapping from
protein groups, and the `make.names` renaming used in Part 2 and in the frozen
block (lines 15 and 142) cannot be matched to the archive annotations.

**Declared choice.** Whole-string equality between the panel symbol and the
`HGNC symbol` field, exactly one row per symbol or stop. Features keep the
matrix row order among the 64 matched rows, mirroring the `%in%` selection;
the ordered symbol list is fingerprinted (SHA-256, LF after every symbol) in
the freeze record before fitting. Model matrices are samples by features.
Protein-group ambiguity is disclosed, not resolved: no isoform, alias or
shared-peptide interpretation is applied.

**Not claimed.** Biological identity between a matched row and the original
model feature, or that feature order is immaterial to every model.

### D4. Replicate collapse

**Source evidence.** The clinical annotations contain five groups of three
measurements and 153 singletons, so 168 measurement columns represent 158
explicit samples and patients. A commented author example (preprocessing.R,
lines 295–328) averages replicate columns after imputation with
`mean(x, na.rm=TRUE)`, located through `Process.ID` substrings, and keeps each
group's first column.

**Unresolved history.** `Process.ID` is absent from the public clinical sheet,
the comment's group literals match no recovered label exactly, and the
example's execution and output destination are unverified.

**Declared choice.** Collapse after imputation and before eligibility
exclusion by the exact arithmetic mean of the imputed values of all columns
sharing one explicit `Sample ID`, keyed by the exact clinical join rather than
substrings. Expected group sizes are five groups of three and 153 singletons;
a different partition stops the run. Any missing value in a collapsed column
stops the run: there is no `na.rm`. The later-excluded samples (13 neoadjuvant
and 10 mixed-location, with no overlap) are collapsed by the same rule and
then excluded, so the 135 fitted columns map one-to-one to explicit patient
keys.

**Not claimed.** That the historical workspace was produced by this rule, or
that averaging imputed replicates equals averaging before imputation.

### D5. Labels, positive class and ordering of samples

**Source evidence.** Methods S95 describe the output as the probability of
refractory disease. Part 3 takes random-forest column `[,2]`, the probability
of the second factor level, and computes `roc(senref, score, direction="<")`
(lines 81 and 127). Another author script encodes sensitive as 1.

**Unresolved history.** The numeric encoding inside the absent `senref` object
is not visible. The AUROC is invariant to flipping label and direction
together, so the printed 0.83 does not settle it; the released scores give
0.8089 under refractory-positive and would give 0.1911 under the reverse.

**Declared choice.** Refractory is the positive class and is encoded as 1;
sensitive is 0. The run verifies that the factor levels passed to the random
forest are exactly `"0"` and `"1"` and that the AUROC direction is "higher
score means refractory", stopping otherwise. Samples are ordered by the sorted
explicit patient key and the ordered key list is fingerprinted privately; no
positional label assignment is allowed.

**Not claimed.** That the original `senref` used this encoding; the direction
remains a source-interpretation question for external review.

### D6. Fold assignment: replacement for the absent helper

**Source evidence.** Part 3 calls `set.seed(j)` then `balanced.folds.vec(senref, 5)`
for `j` in 1–100 (lines 23–27). `balanced_folds.R` is absent from the pinned
tree, its history and three public forks. CRAN package
[pamr 1.57](https://cran.r-project.org/package=pamr) (tarball SHA-256
`01968f7620f1a5e4be1ce666f7ff52211b9dcf6cf5948112c7441aabae56af3d`, GPL-2,
published 2024-07-01) ships a function with the same base name,
`balanced.folds(y, nfolds)`, which splits indices by class, shuffles each
class with `sample`, reshapes into folds and returns a list of index vectors.
It was read, not run. Part 2 instead uses an unstratified
`sample(rep(1:5, c(27,27,27,27,27)), 135)`.

**Unresolved history.** The author `.vec` variant is unavailable, and R's
`sample` changed behaviour in R 3.6.0, so even a recovered helper would need
the original R version to reproduce the original folds.

**Declared choice.** A new, language-independent convention implemented in
`assign_folds`: the unit is the explicit patient key; within each class,
patients are sorted by the lowercase hexadecimal SHA-256 of
`"<seed>\x1f<patient key>"` (UTF-8, with the unit-separator byte) and dealt
round-robin to folds 1–5 starting at fold
`(int(SHA-256("<seed>\x1f<class label>"), 16) mod 5) + 1`. Seeds are the
integers 1–100, one per repetition, retained only as repetition labels. Every
fold's count of each class is within one of every other fold's; a class-empty
fold or a class smaller than the fold count stops the run. A pinned test
fingerprint guards the convention against silent drift. The paper's and
pamr's stratification is retained; the balanced-size feature of the pamr
function is retained; its random stream is not.

**Not claimed.** Recovery of the original folds, equivalence to pamr or to the
author helper, or that the fold assignment affects the result less than
model randomness does.

### D7. Model settings in cross-validation

**Source evidence.** Part 3 lines 51–81 fit, per fold: `cv.glmnet` with
`family="binomial"`, `alpha=0.2`, `nfolds=3`, predicting `type="response"` at
`s="lambda.min"`; `xgboost` with `max_depth=2`, `eta=0.1`, `nthread=2`,
`nrounds=100`, `objective="binary:logistic"`; `randomForest` on the formula
interface with `ntree=100` after `set.seed(1000000)`, with `importance=TRUE`
and `proximity=TRUE`. The frozen block uses 500 rounds and 1,000 trees
(lines 163–172), matching the paper's model subsections. An elastic-net error
breaks the inner loop (lines 53–56).

**Unresolved history.** Package versions are unknown, so defaults that changed
later (for example the xgboost tree method, which became histogram-based by
default in version 2.0) are not fixed by the script. `cv.glmnet` draws its
three inner folds from the R random stream, which the new outer folds already
alter.

**Declared choice.** Keep the cross-validation stage settings above
unchanged: 100 rounds and 100 trees, not the frozen-stage 500 and 1,000.
Call `set.seed(j)` at the start of repetition `j`, as the script does, and let
`cv.glmnet` draw its inner folds from that stream; call `set.seed(1000000)`
immediately before each random-forest fit. Set the xgboost tree method
explicitly to the exact greedy method and `nthread=1`, recording both as
declared choices made for determinism rather than recovered settings. Drop
`importance` and `proximity`, which do not change predictions; record this
deviation. Any model error in any fold stops the whole run; no repetition is
averaged from partial folds. The logistic stack (lines 93–100) is not
computed, because Figure 3D uses the simple mean.

**Not claimed.** That these calls reproduce the original fits under the
original package versions. Newly pinned versions are a new environment.

### D8. Aggregation and metric

**Source evidence.** Within a repetition, Part 3 averages the three held-out
probabilities per entry (lines 105–107); after 100 repetitions it averages per
entry with `mean(x, na.rm=TRUE)` (line 123) and computes one ROC on the final
scores with `ci=TRUE` (line 127). The sensitivity ribbon comes from `ci.se`.

**Unresolved history.** `na.rm=TRUE` would hide incomplete repetitions; the
confidence-interval method is not set explicitly, so the pinned pROC default
decides it.

**Declared choice.** Implemented in `aggregate_predictions` and `auroc`: exactly
one held-out prediction per patient per model per repetition, or stop; exact
rational arithmetic for the within-repetition mean of three models and the
across-repetition mean per patient; AUROC as the fraction of correctly ordered
refractory–sensitive pairs with half credit for exact ties, cross-checked by
the rank formula already used for the executed published-score check. Report
the full value and the two fixed comparisons: half-up rounding to two places
against the printed 0.83 and the pilot's absolute tolerance of 0.02. Also
report the difference from the supplied-score AUROC 0.8088507878 as a second
reference, because agreement with it would bear on the released scores'
provenance. Report a patient-level bootstrap interval (2,000 resamples, fixed
seed) as the pilot's uncertainty measure and the pROC default interval as the
code-implied one, each labelled; neither is the original interval.

**Not claimed.** That a reconstructed AUROC near 0.83 or near 0.8089 proves the
original procedure or the released scores' origin; either outcome stays a
finding to be explained, never tuned.

### D9. Preprocessing fit scope and the two tracks

**Source evidence.** The displayed workflow filters proteins using response
labels of all samples, imputes provisionally, batch-corrects on plex, restores
missingness and imputes with DreamAI, all before any split. The recovered
imputed member contains all 168 measurement columns, including the 13
neoadjuvant and 10 mixed-location columns later excluded. The metadata-only
directory listing recorded below shows that the same archive also contains
`FFPE_discovery_globalprotein_batchcorrected_before_imputation.tsv`.

**Unresolved history.** The archive-to-workspace chain, the imputation that
produced the released member, and the 10^-7 versus 10^-10 outlier threshold
remain unproven and are preserved as open discrepancies.

**Declared choice.** Two tracks, never merged in reporting. The
**reproduction track** fits on the released imputed member and discloses that
label-dependent filtering, batch correction and imputation were global and
included later-excluded samples; it is not leakage-controlled. The
**leakage-controlled track** will start from the batch-corrected member before
imputation, fit imputation within training folds only, and apply the frozen
transformation to held-out patients; it still inherits global filtering and
batch correction and must say so. Its imputation method is a new choice to be
fixed in a separate contract before fitting; the authors' provisional KNN
settings (`k=10`, `rowmax=0.9`, `colmax=0.9`) are a candidate, not a recovered
step. The 64 panel rows must also be checked for presence in that member.

**Not claimed.** That either track yields a fully training-only evaluation,
or that the batch-corrected member's integrity or columns have been verified:
only its directory entry was read.

### D10. Environment

**Source evidence.** Part 2 loads `randomForest`, `glmnet`, `xgboost`, `pROC`,
`ggplot2`, `ggpubr` and `DiagrammeR`; no lockfile or session record exists in
the pinned tree. This workspace has Python 3 only and no R installation.

**Declared choice.** The language-independent parts (folds, ordering,
replicate collapse, coverage, averaging, metric) are fixed here in Python with
exact arithmetic and can be re-implemented from this record in R. Model
fitting will use R with versions pinned at freeze time and recorded as a new
environment, together with the R version, `RNGkind`, platform and session
information. No R code is committed before an environment exists to run it.

**Not claimed.** Recovery of the original environment.

### D11. Stop rules

The run stops, without writing a result, on any of: changed source hashes or
member CRC; cohort counts other than 135, 52 and 83; a panel symbol matched
zero or several times; an unclassified column used as data; a replicate
partition other than five groups of three; any missing value during collapse
or aggregation; conflicting labels within a patient; a class-empty fold; a
model error in any fold; incomplete held-out coverage; a factor level or
direction check failure; or disagreement between the two AUROC calculations.
A result that disagrees with 0.83 is a finding, not a stop.

### D12. Outputs

Private execution records link each prediction to input hashes, patient key,
repetition, fold, model and preprocessing fit, and stay in authorized storage
outside Git. Public outputs are the freeze record, aggregate counts, the final
AUROC with its fixed comparisons, the two labelled intervals, environment and
hashes, and the discrepancy log. No row-level prediction, patient key, fold
assignment or abundance value enters the repository.

## Metadata-only archive directory listing

To settle whether a more upstream discovery input exists, the pinned archive's
central directory was listed on 2026-10-25 using the repository's bounded range
fetch and validation: 65,557 tail bytes were read, the central-directory
SHA-256 matched the pinned `5dd3db7c674ab2952a148af474da6604c1daf88a4e2cf2ff45d939f7530ae5a0`,
the entry count was 42 and the selected member's contract held. Only entry
names, sizes, CRCs and ZIP dates were read; no member bytes were fetched. The
listing took 1.878 seconds. It is exploratory and is not a retained tool.

The 42 entries are one directory entry, 20 files and 21 macOS resource-fork
entries. The files are a README, a `.DS_Store`, and 18 data tables: global
protein and phosphoprotein tables for the discovery, FFPE-validation and frozen
cohorts, each as imputed and as batch-corrected before imputation, plus
discovery and FFPE-validation CNV, LOH and RNA-seq tables. The global-protein
entries are:

| Member under `processed_data/` | CRC32 | Compressed / uncompressed bytes | ZIP entry date |
| --- | --- | ---: | --- |
| `FFPE_discovery_globalprotein_imputed.tsv` | `9f713751` | 7,993,706 / 18,498,831 | 2023-03-22 |
| `FFPE_discovery_globalprotein_batchcorrected_before_imputation.tsv` | `54a640b6` | 7,581,063 / 17,717,677 | 2022-08-18 |
| `Frozen_globalprotein_imputed.tsv` | `299f7ac3` | 3,489,041 / 7,941,483 | 2023-03-22 |
| `Frozen_globalprotein_batchcorrected_before_imputation.tsv` | `7479644f` | 3,291,027 / 7,580,143 | 2022-08-18 |
| `FFPE_validation_globalprotein_imputed.tsv` | `6e9168e8` | 1,215,069 / 2,809,724 | 2023-03-22 |
| `FFPE_validation_globalprotein_batchcorrected_before_imputation.tsv` | `08ced300` | 1,204,803 / 2,789,237 | 2022-08-18 |

ZIP entry dates are archive metadata, not evidence about analysis order. The
batch-corrected discovery member is the candidate input for the
leakage-controlled track in D9. Its header, column linkage, feature coverage
and integrity have not been inspected; a bounded header and complete-member
check like the existing audits is the next source step for that track. The
frozen and FFPE-validation members are outside this reconstruction.

## Gates this record does not close

| Gate | State |
| --- | --- |
| Archive reuse and retention | The article's data-availability statement offers the processed data publicly; no archive-specific reuse grant or retention location is established. The owner's decision on the basis for transient, in-memory analysis is requested in the [roadmap](roadmap.md). |
| External scientific review | Pending. Agent source and code checks are technical checks only. |
| Freeze | After the reuse decision: run the contract command, record its output with the ordered-symbol and sample-key fingerprints, pinned R versions and the exact command, then fit. Any change to this record after the freeze is a new version. |
| Separate imputation contract | Required before the leakage-controlled track fits anything. |
| 2025 fallback target | Unchanged and separate; no replacement target is adopted. |

## What changed and what did not

The offline tests for the new module cover patient-complete, stratified and
deterministic folds for all 100 seeds, the pinned convention fingerprint,
conflicting labels, exact panel-row location, replicate averaging without
missing-value removal, exact two-stage averaging, rejection of missing,
duplicate, misassigned, out-of-range and float-typed predictions, agreement of
the AUROC with the executed check's definition, and token-free CLI output.
They validate software contracts, not scientific validity.

This record adds no performance result, changes no executed result and does
not treat internal checks as external review. No author, collaborator or
reviewer was contacted.
