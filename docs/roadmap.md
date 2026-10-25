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
now links a concrete [decision record](../protocols/pilot-001-reconstruction-decisions.md)
for feature interpretation, sample-key averaging, ordering, new folds, models and
aggregation. The [synthetic validation](pilot-001-synthetic-validation.md) now
records the original implementation, installed dependency inventory and complete
100-repeat execution on abstract fixtures. The
[data-use disposition](pilot-001-data-use.md) selects independent noncommercial research, original implementation and no persistent patient-level
files. It clarifies private-computation and attribution conditions and selects a
conditional Canadian research fair-dealing basis. Actual execution context and
applicable hosting/review conditions must support that basis before fitting.

The [source adapter and execution check](pilot-001-source-adapter.md) now validate
generated source-format files through the actual model pipeline. All 138 Python
tests and 18 new R bridge assertions pass; 40 observed combined-runtime controls
pass. The source adapter has not ingested study bytes. The next step is to select
and assess an actual execution context, including host terms and applicable
obligations, then verify live acquisition and the combined runtime on that host. Keep historical uncertainties explicit; do not repair them silently
to improve agreement. Research fitting remains conditional on the data-use disposition. No researcher contact
is needed for the software preparation. The 2025 fallback remains unadopted.

| Gate | Deliverable | Acceptance or stop rule |
| --- | --- | --- |
| 0. Agree scope and rights | Input-specific use disposition; applicable review requirements; code-licensing expectations | Original implementation and source inspection can proceed; unresolved real-data use conditions stop fitting. No collaborator has been recruited and external scientific review remains pending. |
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
