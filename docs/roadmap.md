# Roadmap

Status: updated 2026-10-23. The scaffold,
[static feasibility audit](pilot-001-feasibility-audit.md), and
[public input/linkage investigation](pilot-001-input-resolution.md) are completed.
Executed metadata checks advance Gates 0–1; they do not close the remaining
method, input, corrected-supplement or scientific-review requirements. No model
performance result has been reproduced.

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
