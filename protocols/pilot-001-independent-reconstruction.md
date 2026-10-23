# Pilot 001: public-input reconstruction contract

**Version:** 0.1, 2026-10-23. **Status:** prospective; model execution not started.
This specifies a possible reconstruction from public inputs while outreach is
on hold. It does not alter the executed
[score-verification specification](pilot-001-score-verification.md) or its result.
The [source investigation](../docs/pilot-001-independent-progress.md) records
which input and method contracts are still unresolved.

## Target and scope

Use the fixed 64-protein panel and the published 135-patient discovery membership
(52 refractory, 83 sensitive). Higher scores must represent refractory disease.
The panel checksum, source workbooks, exact clinical joins, exclusions and one
retained missing location annotation remain as recorded in the
[input report](../docs/pilot-001-input-resolution.md). Preserve that missingness;
do not silently reinterpret it or exclude the record to improve agreement.

The target is one held-out probability per patient per repetition, with five
folds and 100 repetitions. Average the three model probabilities within each
repetition, then average each patient's probabilities over repetitions, following
the located discovery score lineage. Recompute AUROC from those final scores.
Do not pool all repetitions as independent observations or substitute in-sample
predictions. The printed 0.83 remains a reference; the earlier supplied-score
comparison and its fixed tolerance remain a separate executed record.

This stage covers discovery only. Frozen patient independence, assay alignment,
FFPE-validation threefold CV, confidence intervals and clinical utility are
separate questions. Fixed-panel CV cannot estimate the performance of discovering
the panel anew.

## Contracts required before using abundance values

| Contract | Acceptance evidence | Current state / stop rule |
| --- | --- | --- |
| Source identity and reuse | Verified access/reuse conditions for each specific input; attributable release, full-file checksum, permitted storage and retention | PDC and downstream Figshare terms checked; archive-specific reuse terms, matrix bodies/checksums and any retention location remain unverified. In-memory metadata work can continue. |
| Matrix column identity | Source-backed column → measurement → explicit sample/patient relationship; no conflicting joins; complete selected-cohort coverage | The recovered author imputed-matrix header matches all 168 response-labelled measurement rows, 158 unique sample/patient keys and all 135 published score keys by exact equality. This resolves candidate-input naming; it does not establish raw-PDC equivalence or full-file integrity. |
| Repeated measurements | Explicit repeated-sample relationships and a documented stage/rule for collapse; no patient split across train/test | Clinical replicate consistency is checked; abundance-level transformation and collapse order are unresolved. |
| Protein identity | All 64 fixed panel symbols map to documented features with explicit duplicate/protein-group handling | Panel is recovered; coverage and multiplicity in candidate matrices have not been checked. Do not silently drop or substitute proteins. |
| Transformation history | Evidence for input scale, reference channels, normalization, missingness/filtering, batch correction and imputation; declared order and fit population | Candidate abundance files are not the missing model workspaces. If historical operations cannot be recovered, label every replacement as a reconstruction choice. |
| Labels and ordering | Exact joins to the fixed membership, explicit positive class, ordered features and samples verified before every model call | Both published-score and recovered matrix-header joins are known. Abundance-row/feature ordering and replicate collapse still need verification. No positional label assignment. |

The current discovery protocol must not be presented as a faithful original
reproduction until the relevant input and method lineage is established. A
newly specified reconstruction can be useful, but its differences must be fixed
before fitting and preserved in the results.

## Freeze the implementation before fitting

Once the input contracts are satisfied, record one execution specification with:

- Explicit discovery workspace selection; no implicit overwrite by the FFPE
  validation workspace. Pin input, implementation and specification hashes.
- A declared replacement for `balanced_folds.R` if it remains unavailable. Group
  by explicit patient key and stratify by response; preserve seeds 1–100 as a
  documented starting convention, without claiming to recover original folds.
- Exact R/package versions, model parameters and training-only tuning rules.
  Resolve the recorded feature-selection/object-flow discrepancies explicitly.
  Newly chosen versions are a new environment, not the original environment.
- The scope of every learned preprocessing step. A separate evaluation must fit
  these steps within training folds. Do not describe globally preprocessed
  inputs as proving fully independent validation.
- Expected denominators, score direction, metric definition, comparison rule,
  compute limits and failure behavior. Stop on missing features, ambiguous
  identities, class-empty folds or incomplete prediction coverage.

Small offline tests with abstract tokens can then check patient-disjoint splits,
one held-out prediction per patient per repetition, complete coverage, stable
ordering, deterministic averaging and rejection of missing/duplicate scores.
They cannot establish scientific validity or equivalence to the absent helper.
Build these checks alongside the implementation they will validate; an unused
general pipeline or speculative environment is not needed now.

## Output and continuation decision

Private execution records must link each score to input identity, patient,
repetition, fold, model and preprocessing fit. Public outputs contain reviewed
aggregate counts, source/code/environment hashes and discrepancies only.
No new row-level prediction file belongs in Git.

Continue source checks against specific unresolved contracts. The bounded
readiness screen found a 2025 follow-up that led back to the original processed
archive and resolved candidate-input naming. Prioritize that recovered discovery
matrix: verify applicable reuse terms, full member integrity and feature coverage;
document its transformation/collapse history; then freeze a reconstruction
implementation. Do not substitute the downstream combined CSV or its 60-protein
target for the original 64-protein question.

If the remaining original-input contracts cannot be met, retain this pilot's
feasibility findings and finish the separate 2025 candidate's readiness checks
before selecting any replacement. Keep endpoint, assay and class direction
explicit; freeze that target's own analysis contract before fitting. External
review remains deferred and unfulfilled; no author contact or reviewer recruitment
is authorized by this contract.
