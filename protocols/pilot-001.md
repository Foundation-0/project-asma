# Pilot 001: reproduce a primary platinum-refractoriness protein signature

**Status:** proposed; not executed. **Version:** 0.1, 2026-10-22.
**Scope:** research reproduction and robustness, not a novel classifier or new
clinical validation. No treatment recommendations or patient-facing output.

## Question and target

Can we reproduce one reported Figure 3D result from Chowdhury et al. (Cell, 2023)
and characterize performance on genuinely independent HGSOC patients?
[S01](https://doi.org/10.1016/j.cell.2023.07.004)

Start with the published 64-protein panel and primary refractory versus sensitive
labels. Before analysis, extract the exact original endpoint, response criteria,
timing, neoadjuvant exclusions, and specimen selection from methods and metadata.
Primary refractory disease concerns failure of initial platinum therapy; later
platinum-resistant recurrence is a different endpoint. Do not substitute one for
the other or pool histotypes.

Target: the discovery cross-validation ROC/AUC in Figure 3D, with the
frozen-independent evaluation as the first robustness comparison. Freeze the
exact panel, methods version, analysis subset, expected number, and tolerance
using corrected supplemental legends per [S11](https://doi.org/10.1016/j.cell.2024.01.016).
The paper reports discovery AUC 0.83 (95% CI 0.77–0.90); these are published
reference values, not results from this project. Proposed agreement tolerance:
absolute AUC difference ≤0.02 with matching endpoint and population; departures
must be explained rather than tuned away.

## Inputs and access gate

Candidate proteome studies: discovery **PDC000360**, FFPE validation **PDC000358**,
frozen validation **PDC000362**. Matched phosphoproteomes (359/357/361) are
registered for context and are outside the first analysis. See the
[dataset registry](../registries/datasets.json); study names were verified using
PDC metadata, but file-level access, terms, releases, and contents remain unchecked.
No datasets have been downloaded.

Author code was inspected, not executed: commit
`48357fd63ccbfe3954f38c8efc558b4f88bd6051`,
[Figure_3D_part3.R](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R).
It references local RData/CSV inputs and `balanced_folds.R`, and the plot contains
a literal AUC annotation. Resolve helper/input availability, object ordering,
dependencies, and reuse rights; recompute metrics from predictions. Do not treat
the README's folder labels as an executable workflow. Do not run downloaded code
until it has been reviewed.

## First milestone and design

1. **Provenance and patient overlap.** Complete the
   [manifest specification](../templates/provenance-manifest.md) privately. Record
   releases, checksums, transformation history, label sources, participant,
   specimen and aliquot relationships, including primary/metastatic pairs.
   The paper reports discovery/frozen overlap and uses shared samples for assay
   alignment. Reconcile those counts with eligibility exclusions. Explicitly
   classify each validation patient as independent, overlapping, or unresolved;
   unresolved patients cannot enter independent-patient metrics. The overlap is
   disclosed by the authors, not evidence of misconduct.
2. **Reproducible environment.** Pin R and package versions from an inspected
   dependency inventory, author commit, seeds, and execution commands. Record OS,
   session information, CPU/memory/time and all deviations. No unverified lockfile
   is supplied here. Use a small input smoke check after access approval, before
   full execution. This scaffold itself needs only Python's standard library.
3. **Faithful reproduction.** Implement the documented analysis as a distinct
   reproduction track, recording any upstream preprocessing shared across folds
   or cohorts. Recompute one ROC/AUC and its denominator from predictions; retain
   the discrepancy log. Do not silently change methods to improve agreement.
4. **Independent evaluation.** Separately evaluate a leakage-controlled track.
   Group every repeated tumor/aliquot by patient. Fit imputation, scaling,
   feature filtering/selection, batch adjustment, and any learned alignment only
   on training folds; apply frozen transformations to held-out patients. Tune
   models in nested training folds. Do not use held-out labels or distribution
   statistics for alignment or threshold choice. If published preprocessing
   cannot be reconstructed from sufficiently upstream inputs, disclose that
   limitation and stop claiming a fully leakage-controlled evaluation.
5. **Simple comparisons and uncertainty.** Compare the published panel/ensemble
   with a prevalence-only predictor and a regularized logistic regression on
   the same panel and patient splits. Use clinical-only baseline variables only
   when available, justified, and known before treatment. Fix splits and seeds;
   use no test-driven feature selection. Report AUROC, AUPRC with prevalence,
   sensitivity/specificity and confusion counts at a training-selected operating
   point targeting 98% specificity, and calibration/Brier score when sample size
   permits. Report achieved test specificity; do not force it to 98% using test
   labels. Use patient-level bootstrap 95% intervals (proposed 2,000 resamples,
   fixed seed), disclose class-empty resamples and instability. Small cohorts
   cannot support precise high-specificity estimates.

Retain FFPE and frozen evaluations separately. FFPE validation used model
re-estimation and CV in the paper; report it as such, not a locked external model
test. A published fixed panel may already reflect discovery-wide selection:
CV with that panel alone does not estimate de novo feature-selection performance.

## Stress tests and failure criteria

Inspect assay/site/batch and preservation effects, missingness by protein and
response group, tumor purity, pre-treatment status, endpoint ascertainment,
selection bias, and cohort class balance. Compare plausible training-only
missingness/imputation choices. Where counts allow, test leave-site/batch-out
evaluation and purity-stratified performance; otherwise describe the limitation.
Use patient-level label permutation within an appropriate training design as a
sanity check, not a discovery claim. Separate robustness analyses from the
faithful reproduction and disclose multiplicity.

Stop or narrow the pilot if legal access, patient identity linkage, endpoint
mapping, corrected supplements, essential inputs, or dependencies remain unresolved.
Do not replace missing evidence with synthetic patient records or invented results.

## Reviewable outputs

- Provenance/environment report and aggregate patient-flow/overlap counts.
- One recomputed figure/result with commands and declared agreement assessment.
- Independent-patient metrics, uncertainty, baselines, sensitivity analyses, and
  explicit unsupported or unrun stages.
- A short feasibility decision reviewed with a gynecologic oncologist and a
  proteomics/biostatistics collaborator; these partners are needed, not recruited.

Publish only safe aggregate outputs after disclosure review; keep row-level data
and patient keys out of Git. The [roadmap](../docs/roadmap.md) gives a conditional
2–4 week estimate, not a commitment. Current executed research results: **none**.
