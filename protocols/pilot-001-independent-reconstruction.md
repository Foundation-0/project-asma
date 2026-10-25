# Pilot 001: public-input reconstruction contract

**Version:** 0.3, 2026-10-25. **Status:** prospective; decisions declared,
model execution not started.
This specifies a possible reconstruction from public inputs while outreach is
on hold. It does not alter the executed
[score-verification specification](pilot-001-score-verification.md) or its result.
The [source investigation](../docs/pilot-001-independent-progress.md) records
which input and method contracts are still unresolved. Version 0.3 adopts the
[reconstruction decision record](../docs/pilot-001-reconstruction-decisions.md)
(decisions D1–D12) and its offline
[contract module](../tools/reconstruction_contracts.py); the target, cohort,
score direction, aggregation and comparison rules are unchanged from 0.2.

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

## Bounded source inspection

The user's next-step instruction authorizes an integrity and feature-annotation
audit of the recovered discovery member. The paper's data-availability section
(article XML S27) explicitly offers the processed data at a publicly accessible
URL. This supports the requested source inspection; it is not an inferred
license for redistribution or general dataset reuse. No archive-specific reuse
grant has been established.

For this audit only, read the complete compressed member into transient memory,
verify its ZIP integrity and calculate content hashes, and inspect protein
annotations against the fixed panel. Decompression necessarily traverses the
abundance fields; discard them without numeric conversion, analysis or storage.
Keep all matrix bytes, headers and sample keys out of files and tool output.
Retain only aggregate feature counts, source and implementation hashes, and
execution metadata. Do not execute author code or fit models. This audit does
not satisfy the separate reuse, storage or transformation contracts below.

## Contracts required before using abundance values

| Contract | Acceptance evidence | Current state / stop rule |
| --- | --- | --- |
| Source identity and reuse | Verified access/reuse conditions for each specific input; attributable release, full-file checksum, permitted storage and retention | The bounded source inspection verified member CRC and established a full member SHA-256 without retaining data. PDC and downstream Figshare terms remain distinct; archive-specific later reuse conditions and any retention location remain unverified. |
| Matrix column identity | Source-backed column → measurement → explicit sample/patient relationship; no conflicting joins; complete selected-cohort coverage | The recovered author imputed-matrix header matches all 168 response-labelled measurement rows, 158 unique sample/patient keys and all 135 published score keys by exact equality. The complete-member audit verifies the same header hash and member CRC. This does not establish raw-PDC equivalence or correctness of abundance values. |
| Repeated measurements | Explicit repeated-sample relationships and a documented stage/rule for collapse; no patient split across train/test | Clinical replicate consistency is checked (five groups of three measurements). A commented author example averages after imputation, but its group identities and execution are unverified. Do not assume it generated the released input. |
| Protein identity | All 64 fixed panel symbols map to documented features with explicit duplicate/protein-group handling | All 64 fixed symbols occur exactly once among 8,800 HGNC-symbol rows in the recovered member. No symbol substitution or collapse is needed for row selection. Biological protein-group interpretation and conversion to original workspace row names remain unverified. |
| Transformation history | Evidence for input scale, reference channels, normalization, missingness/filtering, batch correction and imputation; declared order and fit population | Static source review locates label-dependent missingness filtering, provisional imputation, batch correction, missingness restoration and final imputation. The archive-to-workspace chain and fit population remain unproven; replacement choices are declared in decision record D9. A metadata-only directory listing located a batch-corrected discovery member before imputation as the candidate input for a leakage-controlled track; its header, coverage and integrity are uninspected. |
| Labels and ordering | Exact joins to the fixed membership, explicit positive class, ordered features and samples verified before every model call | Published-score and matrix-header joins are known; every panel symbol has one exact row. Decisions D3–D5 fix the feature order (matrix row order among exact matches, fingerprinted), replicate collapse by explicit sample key and sorted patient-key sample order; historical workspace ordering and collapse remain unverified. No positional label assignment. |

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
  Decision D6 declares this replacement; `assign_folds` implements it with a
  pinned test fingerprint.
- Exact R/package versions, model parameters and training-only tuning rules.
  Resolve the recorded feature-selection/object-flow discrepancies explicitly.
  Newly chosen versions are a new environment, not the original environment.
- The scope of every learned preprocessing step. A separate evaluation must fit
  these steps within training folds. Do not describe globally preprocessed
  inputs as proving fully independent validation.
- Expected denominators, score direction, metric definition, comparison rule,
  compute limits and failure behavior. Stop on missing features, ambiguous
  identities, class-empty folds or incomplete prediction coverage.

Offline tests with abstract tokens now check patient-disjoint splits, one
held-out prediction per patient per repetition, complete coverage, stable
ordering, deterministic averaging and rejection of missing/duplicate scores
([tests](../tests/test_reconstruction_contracts.py)). They cannot establish
scientific validity or equivalence to the absent helper. Model fitting code is
not committed until an environment exists to run it; an unused general
pipeline or speculative environment is still not needed. The freeze is recorded
with `python3 tools/reconstruction_contracts.py`, which pins this contract, the
decision record and the implementation by SHA-256 without reading data.

## Output and continuation decision

Private execution records must link each score to input identity, patient,
repetition, fold, model and preprocessing fit. Public outputs contain reviewed
aggregate counts, source/code/environment hashes and discrepancies only.
No new row-level prediction file belongs in Git.

Continue source checks against specific unresolved contracts. The bounded
readiness screen found a 2025 follow-up that led back to the original processed
archive and resolved candidate-input naming. Prioritize that recovered discovery
matrix: member CRC and exact panel coverage now pass, and the
[decision record](../docs/pilot-001-reconstruction-decisions.md) fixes feature
interpretation, sample-key averaging, ordering, preprocessing scope and the
helper/environment replacements. What remains before fitting: the owner's
decision on the archive reuse basis, a bounded header and integrity audit of
the batch-corrected discovery member, a separate imputation contract for the
leakage-controlled track, a pinned R environment, and the freeze. Do not
substitute the downstream combined CSV or its 60-protein target for the
original 64-protein question.

If the remaining original-input contracts cannot be met, retain this pilot's
feasibility findings and finish the separate 2025 candidate's readiness checks
before selecting any replacement. Keep endpoint, assay and class direction
explicit; freeze that target's own analysis contract before fitting. External
review remains deferred and unfulfilled; no author contact or reviewer recruitment
is authorized by this contract.
