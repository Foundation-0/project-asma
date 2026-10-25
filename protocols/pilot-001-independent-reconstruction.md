# Pilot 001: public-input reconstruction contract

**Version:** 0.5. **Status:** pipeline and source adapter tested on fixtures; study-data
model execution not started.
The [decision record](pilot-001-reconstruction-decisions.md) now specifies the
reconstruction choices, and the [data-use disposition](../docs/pilot-001-data-use.md)
selects a conditional Canadian research-use basis and its execution-context checks.
External outreach remains on hold. These records do not alter the executed
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
| Source identity and reuse | Verified access/reuse conditions for each specific input; attributable release, full-file checksum, permitted storage and retention | Member identity is pinned. The selected run retains no patient-level files, so no persistent location is needed. A conditional Canadian fair-dealing assessment is selected for the noncommercial phase. Actual execution context and applicable hosting/review conditions must support it before fitting. No archive license or blanket clearance is inferred. |
| Matrix column identity | Source-backed column → measurement → explicit sample/patient relationship; no conflicting joins; complete selected-cohort coverage | The recovered author imputed-matrix header matches all 168 response-labelled measurement rows, 158 unique sample/patient keys and all 135 published score keys by exact equality. The complete-member audit verifies the same header hash and member CRC. This does not establish raw-PDC equivalence or correctness of abundance values. |
| Repeated measurements | Explicit repeated-sample relationships and a documented stage/rule for collapse; no patient split across train/test | Choose arithmetic means of all finite measurements grouped by exact Sample ID, on the released scale; require one selected sample per patient. Missing values stop the run. This is a declared replacement, not recovery of the commented author example. |
| Protein identity | All 64 fixed panel symbols map to documented features with explicit duplicate/protein-group handling | Choose each exact HGNC-symbol row as the operational feature and enforce published panel order. All 64 occur exactly once. No duplicate collapse, aliases or accession splitting. Isoform specificity and historical workspace equivalence are not claimed. |
| Transformation history | Evidence for input scale, reference channels, normalization, missingness/filtering, batch correction and imputation; declared order and fit population | Start from the released processed matrix; choose no additional transformation, filtering or imputation. The unknown upstream chain remains a disclosed limitation. No fully training-only evaluation claim is allowed. |
| Labels and ordering | Exact joins to the fixed membership, explicit positive class, ordered features and samples verified before every model call | The decision record fixes exact eligibility, sensitive=0/refractory=1, bytewise UTF-8 patient order and source panel order. Require ordered identity checks and complete measurement groups at execution. No positional label assignment. |

The current discovery protocol must not be presented as a faithful original
reproduction until the relevant input and method lineage is established. A
newly specified reconstruction can be useful, but its differences must be fixed
before fitting and preserved in the results.

## Freeze the implementation before fitting

The [decision record](pilot-001-reconstruction-decisions.md) fixes input assembly,
new patient-stratified fold rules, seeds, model parameters, score aggregation,
comparison and failure behavior. The [synthetic validation](../docs/pilot-001-synthetic-validation.md)
now records an original implementation, installed package inventory, pinned base
image and full fixture execution. The decision record remains frozen; these
implementation results supersede its prospective runtime status without changing
its scientific choices or recovering the original runtime and missing workspaces.

Fixture tests now check patient-disjoint folds, complete held-out coverage, ordered
identities, deterministic averaging and actual package behavior. The executed
record preserves implementation, runtime and specification hashes. A
[source adapter](../docs/pilot-001-source-adapter.md) now revalidates pinned bytes
and converts selected values into the in-memory input contract; its parsing and
acquisition paths have been tested on generated source formats and mocks only.
No tests on abstract fixtures establish scientific validity or close the data-use
conditions. Do not fit research values while those conditions remain unresolved.

## Output and continuation decision

During execution, in-memory records must link each score to input identity,
patient, repetition, fold, model and preprocessing fit. The chosen no-retention
design persists only reviewed aggregate counts, metrics, hashes and discrepancies;
no private patient-level output files, model weights or caches are retained.
The data-use disposition describes the remaining hosting/applicability checks.

The next work is to establish the actual research-execution context and verify
live acquisition there. Python parsing, transfer and fitting now share a pinned
container; its probe passes 40 checks but does not establish those wider
conditions. The adapter has not been executed on study files. Keep the selected
64-protein question; do not substitute the downstream combined CSV or its 60-protein target.
Verify the planned Canadian execution context and remaining conditions of the
selected research-use basis before research fitting. The exact member and panel
audits need not be rerun for this methods step; a future run must revalidate their pinned bytes.

If the remaining original-input contracts cannot be met, retain this pilot's
feasibility findings and finish the separate 2025 candidate's readiness checks
before selecting any replacement. Keep endpoint, assay and class direction
explicit; freeze that target's own analysis contract before fitting. External
review remains deferred and unfulfilled; no author contact or reviewer recruitment
is authorized by this contract.
