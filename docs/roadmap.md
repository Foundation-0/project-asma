# Roadmap

Status: updated 2026-10-24. The scaffold,
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
On 2026-10-24 the user authorized putting the code-audit questions to the
authors through the consolidated
[source request](../templates/pilot-001-source-request.md). GitHub refused
automated posting, so the owner confirms the text and sends it. Do not recruit
collaborators or reviewers without a new explicit instruction. Continue the
investigation using public sources and internal checks, recording limits without
treating deferred review as completed. The
[code-audit addendum](pilot-001-code-audit-addendum.md) adds static findings and
the protocol/contract changes they motivate (pilot 0.7, contract 0.3).

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
The next independent step is an explicit reconstruction decision record using
the [located preprocessing steps](pilot-001-preprocessing-provenance.md): fix
feature interpretation, sample-key averaging, ordering, fit scope and replacements
for missing helper/environment objects. The source review found an outlier
threshold discrepancy and object-name mismatches; preserve them as unresolved
history. Satisfy remaining data-use conditions before abundance analysis, and
freeze an implementation before fitting. Source investigation does not
require contacting researchers. The screened 2025 result remains a separate
fallback; no replacement target has been adopted.

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
