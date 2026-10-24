# Pilot 001: reproduce a primary platinum-refractoriness protein signature

**Status:** full model reproduction proposed; input/linkage and preliminary
published-score checks executed. **Version:** 0.7, 2026-10-24.
**Scope:** research reproduction and robustness, not a novel classifier or new
clinical validation. No treatment recommendations or patient-facing output.

## Question and target

Can we reproduce one reported Figure 3D result from Chowdhury et al. (Cell, 2023)
and characterize performance on genuinely independent HGSOC patients?
[S01](https://doi.org/10.1016/j.cell.2023.07.004)

Start with the published 64-protein panel and primary refractory versus sensitive
labels. The [static feasibility audit](../docs/pilot-001-feasibility-audit.md)
records the paper's response definitions, published cohort counts, missing inputs,
and code/method discrepancies. The
[input/linkage follow-up](../docs/pilot-001-input-resolution.md) recovers the panel
and reconciles the published prediction membership to explicit clinical fields.
Literal missing location annotations remain unresolved; matching published
membership does not establish complete clinical eligibility. The original
analysis workspaces and execution remain unverified. The
[code-audit addendum](../docs/pilot-001-code-audit-addendum.md) adds details on
object provenance, label orientation, panel branches, alignment and version
sensitivity.
Primary refractory disease concerns failure of initial platinum therapy; later
platinum-resistant recurrence is a different endpoint. Do not substitute one for
the other or pool histotypes.

Target: the discovery cross-validation ROC/AUC in Figure 3D, with the
frozen-cohort evaluation, restricted to independent patients per step 1, as the
first robustness comparison. Freeze the exact panel, methods version, analysis
subset, expected number, and tolerance using corrected supplemental legends per
[S11](https://doi.org/10.1016/j.cell.2024.01.016). The hash-pinned MMC4 panel is
a provisional freeze until a corrected artifact is confirmed.
The paper reports discovery AUC 0.83 (95% CI 0.77–0.90); these are published
reference values, not results from this project. Proposed agreement tolerance:
absolute AUC difference ≤0.02 with matching endpoint and population; departures
must be explained rather than tuned away.

A [narrower published-score verification](pilot-001-score-verification.md) ran
under the user's explicit instruction while external scientific review remains
pending. The [result](../docs/pilot-001-score-verification-result.md), AUROC
0.8088507878, rounds to 0.81 and misses the fixed comparison against printed 0.83.
It does not regenerate models, establish original out-of-fold score provenance,
reproduce the repeated-CV procedure or close the full reproduction gates.

The [independent follow-up](../docs/pilot-001-independent-progress.md) adds a
repeatable matrix-header diagnostic, score-lineage inspection and a concrete
supplement-legend mismatch. A separate
[public-input reconstruction contract](pilot-001-independent-reconstruction.md)
specifies prospective work that does not depend on an author response. A subsequent
complete-member inspection verifies the recovered author matrix's ZIP CRC and
finds all 64 panel symbols exactly once among 8,800 feature rows. The
[preprocessing history review](../docs/pilot-001-preprocessing-provenance.md)
records remaining transformation and workspace gaps. This does not change
the executed score check or treat internal checks as external scientific review.

## Inputs and access gate

Candidate proteome studies: discovery **PDC000360**, FFPE validation **PDC000358**,
frozen validation **PDC000362**. Matched phosphoproteomes (359/357/361) are
registered for context and are outside the first analysis. See the
[dataset registry](../registries/datasets.json). Version-1 study and open
processed-file metadata, PDC public-data terms, and catalog overlap were checked;
only file headers were read, not full PDC abundance matrices. Published clinical
and panel/score workbooks were inspected in memory, with only aggregate findings
retained. The follow-up report pins exact source files, sheets, hashes and limits.

Author code was inspected, not executed: commit
`48357fd63ccbfe3954f38c8efc558b4f88bd6051`,
[Figure_3D_part3.R](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R).
It references local RData/CSV inputs and `balanced_folds.R`, and the plot contains
a literal AUC annotation. Resolve helper/input availability, which loaded objects
feed each block, object ordering, dependencies, and reuse rights; recompute
metrics from predictions. Do not treat
the README's folder labels as an executable workflow. Do not run downloaded code
until it has been reviewed.

## First milestone and design

1. **Provenance and patient overlap.** Complete the
   [manifest specification](../templates/provenance-manifest.md) privately. Record
   releases, checksums, transformation history, label sources, participant,
   specimen and aliquot relationships, including primary/metastatic pairs.
   The paper reports discovery/frozen overlap and uses shared samples for assay
   alignment, including 14 additional pairs from different tumors of the same
   patients. Exact supplemental joins now identify six patient keys in the
   published 34-row frozen `nonoverlap` score sheet also present in the eligible
   135-row discovery score set. There are 28 frozen patient keys with no observed
   eligible-discovery match, and 21 with no observed match to any discovery
   record; neither is yet proven independent of upstream fitting/alignment.
   Preserve published and revised membership separately and resolve this
   discrepancy with scientific review before evaluation. Explicitly
   classify each validation patient as independent, overlapping, or unresolved;
   unresolved patients cannot enter independent-patient metrics. The paper
   discloses cross-cohort overlap and assay alignment; the six-key score-membership
   discrepancy remains to be clarified.
2. **Reproducible environment.** Pin R and package versions from an inspected
   dependency inventory, author commit, seeds, and execution commands. Record OS,
   session information, CPU/memory/time and all deviations. No unverified lockfile
   is supplied here. Use a small input smoke check after access approval, before
   full execution. This scaffold itself needs only Python's standard library.
3. **Faithful reproduction.** Implement the documented analysis as a distinct
   reproduction track, recording any upstream preprocessing shared across folds
   or cohorts. Recompute one ROC/AUC and its denominator from predictions; retain
   the discrepancy log. Do not silently change methods to improve agreement.
   Report the per-repeat AUC distribution as a secondary output next to the
   repeat-averaged estimand in the
   [reconstruction contract](pilot-001-independent-reconstruction.md). Before
   comparing regenerated predictions with published values, confirm which input
   objects feed the cross-validation and how labels are coded.
4. **Independent evaluation.** Separately evaluate a leakage-controlled track.
   Group every repeated tumor/aliquot by patient. Fit imputation, scaling,
   feature filtering/selection, batch adjustment, and any learned alignment only
   on training folds; apply frozen transformations to held-out patients. Tune
   models in nested training folds. Do not use held-out labels or distribution
   statistics for alignment or threshold choice. If published preprocessing
   cannot be reconstructed from sufficiently upstream inputs, disclose that
   limitation and stop claiming a fully leakage-controlled evaluation.
   The published alignment is estimated on samples present in both cohorts.
   Before frozen labels are used, pre-specify one harmonisation strategy:
   (a) a mapping fitted only on pairs whose FFPE specimens are training data,
   with those patients excluded from independent metrics; at most 28 eligible
   frozen patient keys lack an eligible-discovery match, and 21 lack any
   discovery match (step 1); (b) a non-learned, strictly per-sample
   normalisation, with retraining declared as a deviation and the training
   matrix's global preprocessing disclosed; or (c) re-estimating the model by
   cross-validation within the frozen cohort (61 eligible, 19 refractory),
   reported as within-cohort re-estimation rather than a test of the FFPE-trained
   model.
5. **Simple comparisons and uncertainty.** Compare the published panel/ensemble
   with a prevalence-only predictor and a regularized logistic regression on
   the same panel and patient splits. Use clinical-only baseline variables only
   when available, justified, and known before treatment. Fix splits and seeds;
   use no test-driven feature selection. Report AUROC, AUPRC with prevalence,
   sensitivity/specificity and confusion counts at a training-selected operating
   point targeting 98% specificity, and calibration/Brier score when sample size
   permits. Treat refractory disease as the positive class and assert this in
   code. If the authors' label coding differs, record the re-orientation as a
   deviation, and compare operating points with published values only when the
   orientations match. Report achieved test specificity; do not force it to 98%
   using test labels. Use patient-level bootstrap 95% intervals (proposed 2,000 resamples,
   fixed seed), disclose class-empty resamples and instability. Small cohorts
   cannot support precise high-specificity estimates.

The cohorts deliberately select refractory and long-term-sensitive tumors.
Their class balance is not population prevalence; interpret AUPRC, Brier score,
and calibration within that selection scheme, without claiming population-risk
calibration. The published panel also used validation-set protein detectability
in its construction; distinguish fixed-panel transfer evaluation from validation
that was untouched throughout model development. The
[audit](../docs/pilot-001-feasibility-audit.md) provides source locators.

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
If the inputs behind the published cross-validation cannot be identified, stop
claiming a faithful reproduction and continue only as the declared reconstruction.
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
2–4 week estimate, not a commitment. Executed results include input/membership
checks and the preliminary supplied-score AUROC discrepancy. The original model
and reported performance have not been reproduced; external review is pending.
