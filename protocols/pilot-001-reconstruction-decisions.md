# Pilot 001: discovery reconstruction decisions

**Version:** 1.0, 2026-10-25. **Status:** methods specified; not executed.
This is a new implementation using released inputs. It does not recover the
original workspaces, fold assignments or preprocessing history. The
[data-use disposition](../docs/pilot-001-data-use.md) and a tested execution
environment remain separate requirements. The earlier supplied-score
specification and AUROC result are unchanged.

## Selected question

Reconstruct the discovery-only, fixed-panel, three-model ensemble on the exact
135 published discovery samples: 83 sensitive and 52 refractory. Higher
probabilities represent refractory disease. Use five outer folds and 100
repetitions. No frozen or FFPE-validation evaluation, panel rediscovery,
confidence interval, threshold metric, calibration or alternative model search
is part of this first run.

Source-visible model settings below come from pinned
[Figure_3D_part3.R, lines 23–127](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L23-L127).
The script was inspected, not copied or executed. Additional settings and
replacement algorithms are declared choices, not historical facts.

## Input construction

| Decision | Required behavior |
| --- | --- |
| Matrix identity | Use only `FFPE_discovery_globalprotein_imputed.tsv`, uncompressed SHA-256 `b7eea435bb7fa65f31a6e8f50d977ff046f0f9bd851126e43cf9a5f52e62be62`, 18,498,831 bytes, CRC32 `9f713751`. Require the pinned header and ZIP metadata from the [feature artifact](../registries/pilot-001-author-feature-summary.json). Stop on changed bytes. |
| Feature meaning | One feature is the released row whose decoded `HGNC symbol` exactly equals a panel symbol. This operational definition does not assert isoform or shared-peptide specificity. |
| Feature order | Exactly `64_protein_predictors!A2:A65`, in source order, with canonical panel SHA-256 `77329920b86dacaffc6778ed7e7c6b827683beed1aad7f2229b8bafe2f535144`. Require exactly one row per symbol. No aliases, accession splitting, syntactic renaming, substitution or feature selection. |
| Clinical identity | Use the exact header → `Data Label 2` → explicit sample/patient joins already audited. Verify all 168 response-labelled measurements represent 158 samples/patients, with five triplicate groups and 153 singletons. Ignore other columns; do not infer identities from their names. |
| Eligibility | Select the exact 135 published score sample keys without reading their numeric scores. Independently require equality with the recorded neoadjuvant/`Mix` exclusions. Retain the one missing location annotation; its eligibility limitation remains explicit. |
| Repeated measurements | For each selected sample and panel feature, take the arithmetic mean of **all** its explicitly linked measurement values, in bytewise UTF-8 measurement-label order, on the released scale. Every value must be finite. No missing-value removal, substitute replicate, additional imputation or averaging of different samples from one patient. |
| Patient representation | Require one selected sample per explicit patient. Sort the 135 resulting rows by bytewise UTF-8 patient key, independent of locale. Retain keys only in process memory. |
| Outcome | Exact clinical `sensitive` → 0 and `refractory` → 1. Require 83 zeros and 52 ones. Stop on other labels or a conflicting replicate annotation. |

The two source workbooks must match their existing
[byte/hash pins](../registries/pilot-001-supplement-summary.json). Verify each
selected sample's measurement-group completeness against clinical metadata
before averaging; using only the one column that matches a published score key
would discard its other measurements. Every model call must check ordered
patient and feature identity, not just dimensions. Final input shape is 135 × 64.

## Processing scope

Use the already processed values as released. Apply **no additional** logarithm,
bridge subtraction, median/MAD alignment, ComBat, DreamAI, missingness filtering
or response-dependent selection. This avoids inventing the unknown transformation
chain. Neither 10^-7 nor 10^-10 is selected as an outlier threshold because this
track does not rerun that upstream stage.

Arithmetic averaging after release is a declared reconstruction choice,
consistent with the located commented example but not proof of its execution.
Finite-value failure is deliberately stricter than that example's `na.rm=TRUE`.
Do not silently change the rule if the selected values contain missingness.

Only glmnet performs its native predictor standardization, within each fitted
training subset, including its inner fits. Do not globally standardize the
cohort. The released matrix and fixed panel still have unresolved upstream
fitting/selection scope. Later patient-disjoint folds cannot remove that history;
this reconstruction cannot establish a fully training-only evaluation.

## Folds and random-number streams

Use R `RNGkind("Mersenne-Twister", "Inversion", "Rejection")`. The replacement
fold procedure receives bytewise UTF-8 ordered patient keys, verifies one row per
patient and both classes, and then:

1. Resets the seed specified below.
2. Processes class 0 before class 1, independently permuting each class's ordered
   keys with `sample.int(class_size)`.
3. Assigns successive permuted keys round-robin to folds 1…K, **continuing the
   offset across classes**, rather than restarting at fold 1 for class 1.

Generate fold assignments independently of model fitting. Model random-number
consumption must not change any later fold assignment or another model's seed.

| Operation | Seed / expected geometry |
| --- | --- |
| Outer repetition r = 1…100 | Seed r; K=5. Five test folds of 27, each with 108 training patients. Three test folds have 17 sensitive/10 refractory; two have 16 sensitive/11 refractory. |
| Inner EN CV for outer fold f = 1…5 | Seed `10000 + 100*r + f`; same algorithm, K=3, restricted to that outer training set. Each inner validation fold has 36 patients; class counts are 22–23 sensitive and 13–14 refractory. |
| XGBoost | Call `set.seed(20000 + 100*r + f)` before each fit. Omit the native `seed` argument: the selected R API ignores it. |
| Random forest | Reset R seed to `1000000` before each fit, following the visible source convention. |

Require disjoint explicit patient sets for every train/test pair. These are new
fold rules; they do not claim equivalence to the missing `balanced_folds.R`.

## Model choices

All models use only the same 64 features. No additional hyperparameter search
beyond the specified inner-CV lambda selection, and no class weighting, is
allowed. Model errors or convergence failures stop the run.

| Model | Source-visible settings retained | Explicit reconstruction settings |
| --- | --- | --- |
| Elastic net | Binomial, alpha 0.2, three inner folds, prediction at `lambda.min` | `type.measure="deviance"`, `standardize=TRUE`, `intercept=TRUE`, `nlambda=100`, `lambda.min.ratio=1e-4`, `grouped=TRUE`, `alignment="lambda"`, `type.logistic="Newton"`, `thresh=1e-7`, `maxit=100000`, all penalty factors 1. Supply the inner `foldid`; no alpha search. |
| XGBoost | `objective="binary:logistic"`, depth 2, eta 0.1, 100 rounds | CPU `gbtree`, `tree_method="exact"`, **one thread** rather than the source's two, `base_score=.5`, `min_child_weight=1`, `gamma=0`, `subsample=1`, all column-sampling fractions 1, `lambda=1`, `alpha=0`, `max_delta_step=0`. No early stopping or tuning. |
| Random forest | 100 trees, `importance=TRUE`, `proximity=TRUE`, seed 1,000,000 | Classification factor levels `c("0","1")`; extract named probability column `"1"`. `mtry=8`, `nodesize=1`, replacement sampling, `sampsize=108`, `maxnodes=NULL`, no class weights and equal cutoffs. |

The EN path is generated on the outer training data; select lambda using only
its inner CV. Verify that package behavior matches the declared settings in an
isolated synthetic smoke check before using research values. Any remaining
implementation-affecting defaults must be recorded in the execution manifest.

## Runtime selection and execution readiness

Select R **4.4.3**, glmnet **4.1-8**, randomForest **4.7-1.2** and XGBoost
**1.7.8.1** as a new R API target. These published source releases preserve the
interfaces used by the selected model calls; they are not claimed to be the
authors' versions. Their downloaded source-archive hashes and declared licenses
are in the [runtime source record](../registries/pilot-001-reconstruction-runtime.json).
Release metadata/license files and XGBoost R seed handling were inspected; no
packages were executed. In the pinned XGBoost archive, `R/xgb.train.R` lines
318–319 direct R users to `set.seed()` and warn that a native `seed` is ignored.

This is a direct-component selection, **not an installed or tested lock**.
R is not installed in the inspected workspace. Before fitting, build an isolated
environment, pin all transitive dependencies, compiler/BLAS/OS and source hashes,
review their license notices, and test the actual model APIs on abstract fixtures.
Set BLAS/OpenMP and model parallelism to one thread. Record all deviations before
examining a research performance result; do not swap versions to improve AUROC.

Use existing compute, with no paid services or GPU. Set a two-hour wall-time and
8 GiB memory limit for the complete research run. Exceeding a limit is a recorded
failed run, not a reason to reduce the number of repetitions or drop a model.
The initial research run is designed for a verified Canadian execution context
under the conditional data-use assessment. Current workspace location is not
established; verify actual processing and relevant operator/provider circumstances
before real data. Abstract software tests do not require research data or claim
that jurisdictional preflight has passed.
The implementation, complete environment and this protocol must be hash-pinned
before execution; methods specification alone does not open the execution gate.

## Predictions, metric and failure behavior

Require one held-out probability from each model for every patient/repetition,
finite and in [0,1]. The expected counts are **40,500 model predictions**,
**13,500 repetition-level ensemble predictions** and **135 final patient scores**.
Average EN, XGBoost and random-forest probabilities in that fixed order, then
average each patient's 100 ensemble scores in repetition order. Never remove
missing predictions, pool repetitions as patients, average fold AUROCs, use
in-sample scores or fit the source's separate logistic stack.

Compute empirical AUROC over the 135 final scores and 4,316 positive–negative
pairs, awarding half credit for exact ties. Independently check the rank-sum
formulation. Do not round scores before either computation. Report the full
value and absolute difference from printed 0.83 against the fixed ≤0.02 rule.
Agreement is numerical concordance for this reconstruction, not proof that the
original result has been reproduced. The unrounded original figure estimate is
unknown, and the earlier supplied-score result remains a separate record.

Stop without a final AUROC on source/hash/schema drift, missing or duplicate
features, conflicting identities, incomplete replicate groups, nonfinite values,
class-empty folds, fit/convergence failure, incomplete predictions or metric
disagreement. Record aggregate failure reasons without patient keys or values.
Do not select alternate seeds, cohorts, directions, transformations or tolerances
after seeing performance.

## Retention and review

Keep inputs, linkage, folds, scores and fitted model objects in process memory
only. Persist aggregate counts, metrics, source/code/environment/protocol hashes,
runtime/resource information and a deviation log. Do not persist models, patient
rows, per-fold predictions or per-patient hashes. Disable caches, workspace saves,
core dumps and data-bearing logs before any research run; verify the actual
runtime's temporary-storage behavior. Process exit ends working retention, but
is not a claim of certified erasure by the hosting provider.

External scientific review remains pending and outreach remains on hold. This
decision record neither certifies clinical validity nor authorizes a clinical
application. The next technical step is an original implementation and a tested
dependency lock using abstract fixtures; real-data fitting remains conditional
on the [data-use disposition](../docs/pilot-001-data-use.md).
