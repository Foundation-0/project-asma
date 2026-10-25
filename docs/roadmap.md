# Roadmap

Status: updated 2026-10-25. The scaffold,
[static feasibility audit](pilot-001-feasibility-audit.md), and
[public input/linkage investigation](pilot-001-input-resolution.md) are completed.
Executed metadata checks advance Gates 0–1; they do not close the remaining
method, input, corrected-supplement or scientific-review requirements.

The [published-score verification](../protocols/pilot-001-score-verification.md)
ran under the user's explicit instruction, with external review still pending.
Its [AUROC result](pilot-001-score-verification-result.md) is 0.8088507878,
rounding to 0.81 and missing the fixed comparison against printed 0.83. This
advances the reproduction investigation through a recorded discrepancy; it does
not regenerate the original predictions or close Gate 2.
External outreach is on hold at the user's request. The source request remains
unsent; do not contact authors or recruit collaborators/reviewers without a new
explicit instruction. Continue the early investigation using public sources and
internal checks, recording limits without treating deferred review as completed.

The [independent follow-up](pilot-001-independent-progress.md) tested the direct
PDC header/design routes and then found a useful downstream citation to the
original author archive. Its imputed discovery-matrix header matches all 168
response-labelled measurement rows and all 135 published discovery-score keys.
The subsequent complete-member audit verifies its ZIP CRC and finds all 64 panel
symbols exactly once among 8,800 feature rows. This resolves naming and feature
availability for the candidate input; transformation provenance remains open.
Score export and corrected legend provenance also remain unresolved.

The [public-input reconstruction contract](../protocols/pilot-001-independent-reconstruction.md)
defines a prospective reconstruction target and its remaining requirements.
The [reconstruction decision record](pilot-001-reconstruction-decisions.md)
(2026-10-25) completes the step it called for: decisions D1–D12 fix the cohort,
input columns, feature interpretation and order, replicate collapse, labels,
the replacement for the absent fold helper, model settings, aggregation and
metric, preprocessing fit scope, environment, stop rules and outputs, each
separated from the unresolved history it cannot recover. The conventions that
need no data are implemented and tested offline in
`tools/reconstruction_contracts.py`. A metadata-only listing of the pinned
archive directory also located a batch-corrected discovery member before
imputation, the candidate input for a leakage-controlled track. The source
review's outlier threshold discrepancy and object-name mismatches remain
unresolved history. No abundance value was read and nothing was fitted.

Before fitting, the remaining steps are: the owner's decision below on the
archive reuse basis; a bounded header and integrity audit of the batch-corrected
member; a separate imputation contract for the leakage-controlled track; a
pinned R environment; and the freeze recorded with the contract command. Source
investigation does not require contacting researchers. The screened 2025
result remains a separate fallback; no replacement target has been adopted.

## Decisions requested from the owner

1. **Archive reuse basis.** The article's data-availability statement (S27)
   offers the processed data publicly, but no archive-specific reuse grant was
   found. Decide whether transient, in-memory analysis of the two discovery
   global-protein members (imputed; batch-corrected before imputation) may
   proceed on that statement with CPTAC/PTRC attribution, no row-level
   retention in Git and private storage per the data rules, or whether author
   confirmation is required first. Author contact is blocked by the outreach
   hold, so the second option pauses Gate 2 until the hold is lifted.
2. **Execution environment.** Approve an R environment with pinned package
   versions for the private run, recorded as a new environment; no model code
   is committed before one exists.
3. **Repository license.** Unchanged and still open.

| Gate | Deliverable | Acceptance or stop rule |
| --- | --- | --- |
| 0. Agree scope and rights | Owner license decision; collaborator review; correction and reuse/access review | No data ingestion or third-party code reuse until requirements are understood. No collaborator has been recruited. |
| 1. Establish provenance | Release/file/checksum manifest; private patient/aliquot overlap map; exclusion counts; pinned author commit and environment | Every cohort has a traceable source and independent-patient status. Unresolved identity, labels, or terms stop analysis. |
| 2. Reproduce one result | One specified Figure 3D result with commands, locked dependencies, seeds, inputs, and discrepancy log | Numerical agreement within a declared tolerance, or a reproducible explanation of failure. No performance claim from a hard-coded plot label. |
| 3. Stress-test | Patient-independent metrics with uncertainty; simple baselines; leakage and assay sensitivity analyses | Separate preservation/batch/cohort effects and original reproduction from revised evaluation. Report null and negative findings. |
| 4. Decide continuation | Short feasibility report and reviewed next question | Continue only if data access, sample independence, compute, and interpretation are adequate. No automatic expansion into a new classifier. |

An initial **2–4 week feasibility window is conditional**, not a delivery
commitment. It assumes accessible processed data, adequate metadata, tractable
author dependencies, modest compute, and availability of a gynecologic oncologist
and a proteomics/biostatistics collaborator. Unresolved rights, missing helper
files, overlap, or correction implications may require a pause or narrower target.

The first milestone bundles provenance and overlap, a reproducible environment,
one reproduced result, and an initial independent-patient evaluation with
uncertainty and simple baselines. Its details are in the
[pilot protocol](../protocols/pilot-001.md). No issue backlog is needed yet.
