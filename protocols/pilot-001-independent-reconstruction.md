# Pilot 001: public-input reconstruction contract

**Version:** 0.6, 2026-10-25. **Status:** pipeline and source adapter tested on fixtures; study-data
model execution not started. This version integrates the 2026-10-24 code-audit
revision, numbered 0.3 on its own branch, with the 2026-10-25 revisions 0.3–0.5.
The [decision record](pilot-001-reconstruction-decisions.md) now specifies the
reconstruction choices, and the [data-use disposition](../docs/pilot-001-data-use.md)
selects a conditional Canadian research-use basis and its execution-context checks.
The reconstruction is independent of any author response, and automated sessions
must not contact authors. These records do not alter the executed
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

The user's next-step instruction authorized the recorded integrity and
feature-annotation audit of the recovered discovery member. That instruction
covered that run; reruns follow the bounded-inspection rule in the
[agent guidance](../AGENTS.md). The paper's data-availability section
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
| Repeated measurements | Explicit repeated-sample relationships and a documented stage/rule for collapse; no patient split across train/test | Choose arithmetic means of all measurements (each must be finite) grouped by exact Sample ID, on the released scale; require one selected sample per patient. Missing values stop the run. This is a declared replacement, not recovery of the commented author example. |
| Protein identity | All 64 fixed panel symbols map to documented features with explicit duplicate/protein-group handling | Choose each exact HGNC-symbol row as the operational feature and enforce published panel order. All 64 occur exactly once in the discovery imputed member; coverage in frozen and FFPE-validation features is not recorded. No duplicate collapse, aliases or accession splitting. Isoform specificity and historical workspace equivalence are not claimed. |
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

The [code-audit addendum](../docs/pilot-001-code-audit-addendum.md) set further
requirements for this freeze. Their status against the decision record and the
fixture-tested implementation:

| Code-audit requirement | Status |
| --- | --- |
| Explicit discovery input; no dependence on the FFPE-validation workspace or earlier session state | Met by design: only pinned released files are read; no author workspace is loaded. |
| Declared `balanced_folds.R` replacement: patient-grouped, response-stratified, seeds 1–100, `RNGkind()` including `sample.kind`, and a decision on the per-forest `set.seed(1000000)` | Met: new folds with outer seed r, `RNGkind("Mersenne-Twister", "Inversion", "Rejection")`, and the reset kept before each forest. Inner elastic-net folds have their own seeds, so the source's coupling of those folds to the forest seed is not reproduced; this is a declared choice. |
| Exact versions; xgboost 1.x or explicit `tree_method` and `base_score`; feature-selection and object-flow discrepancies resolved explicitly | Met: R 4.4.3 and xgboost 1.7.8.1 with `tree_method="exact"` and `base_score=.5`; fixed panel without selection. These form a new environment, not the original one. |
| One alternative configuration fixed for sensitivity analysis before execution | **Proposed; owner decision required.** [Amendment 1](pilot-001-reconstruction-amendment-1.md) (A2) proposes XGBoost `tree_method = "hist"`, the XGBoost 2.0 default, with everything else identical, run after the primary configuration and reported as exploratory. `fit_models` supports it, with tests. With 108 training rows it considers the same candidate splits as `"exact"` and mainly moves thresholds, so its leverage on environment dependence is limited. The owner may instead choose a second block of fold seeds (outer seeds 101–200), which measures dependence on fold assignment rather than environment. The owner may also run both, specify a different configuration, or waive the requirement. |
| No missing labels or panel values; valid R names or the matrix interface | Met: every selected value must be finite, and the random forest uses the matrix interface. Checked 2026-10-25 with `python3 tools/audit_panel_names.py` ([record](../registries/pilot-001-panel-name-summary.json)): R's `make.names` alters none of the 64 pinned symbols, and they are unique, so `unique = TRUE` adds no suffixes. |
| Scope of every learned preprocessing step; globally preprocessed inputs not described as independent validation | Met for this track: released values are used as processed upstream, and only glmnet standardizes, within training subsets. Upstream processing scope remains unknown, and discovery cross-validation is not independent validation. |
| Denominators, score direction, metric, comparison rule, compute limits, failure behavior and stop rules | **Met for the decision record; A3 proposed; owner decision required.** 135 patients (83/52), 4,316 pairs, 40,500 model predictions, a two-hour/8 GiB limit and explicit stop rules. [Amendment 1](pilot-001-reconstruction-amendment-1.md) (A3) proposes which warnings and messages from model calls stop a run. It proposes that every warning stays fatal, that messages become fatal and that a fixed aggregate code records what stopped a run; the alternative counts glmnet's saturation warnings. A3's implementation is not done and precedes any research run. The record's aggregate failure reasons are not yet emitted; the proposed code would provide them. |
| Probability direction tested for each model (added at integration, from review of the synthetic validation) | **Test added; pinned-image run pending.** A planted-signal fixture now requires, for each model separately, a higher class-1 mean probability and a fixture AUROC of at least 0.8, and the check rejects flipped probabilities (see the [synthetic validation](../docs/pilot-001-synthetic-validation.md)). It passes in a development environment with the pinned glmnet, randomForest and xgboost versions (Rcpp, Matrix and the toolchain differ from the pinned image), and six direction and fold-wiring mutations fail it. It must also pass in the pinned image, with the execution record regenerated, before any research run; direction cannot be revisited after one. |
| Distribution of per-repetition AUROCs reported next to the repeat-averaged target | **Proposed; owner decision required; implemented.** [Amendment 1](pilot-001-reconstruction-amendment-1.md) (A1) proposes reporting the count, minimum, quartiles, maximum and mean of the per-repetition AUROCs as a descriptive secondary output that is not compared with 0.83. Each repetition's AUROC spans all 135 held-out scores; it is not an average of fold AUROCs. It is not adopted until the owner records a dated decision. If the owner rejects it, remove the computation before any research run. A pinned-image run is pending. |

The open items do not change the primary target, but each is required. Resolve
each by a dated amendment before any research run; the decision record itself
stays frozen. Before live acquisition of study files, a real-source input check or any fitting on study values, the owner must record a dated attestation of the actual execution context and give a new explicit instruction to run. An automated session's own checks never satisfy this condition.

## Output and continuation decision

During execution, in-memory records must link each score to input identity,
patient, repetition, fold, model and preprocessing fit. The chosen no-retention
design persists only reviewed aggregate counts, metrics, hashes and discrepancies;
no private patient-level output files, model weights or caches are retained.
The data-use disposition describes the remaining hosting/applicability checks.

The next work is to establish the actual research-execution context. Live
acquisition there follows only after the owner's sign-off stated above. Python parsing, transfer and fitting now share a pinned
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
