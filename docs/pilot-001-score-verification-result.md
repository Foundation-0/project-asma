# Pilot 001: published discovery-score AUROC result

**Executed:** 2026-10-23. **Evidence class:** preliminary arithmetic check of
published predictions, under the user's explicit instruction to proceed.
External scientific review remains pending. No model was fitted or regenerated.

The fixed check produced **AUROC 0.8088507878**, which rounds to **0.81**.
It did not recover the printed discovery value **0.83** and did not meet the
predeclared absolute-difference tolerance of **0.02** against that printed value.
The result is retained unchanged; no cohort, score direction or comparison
criterion was adjusted after observing it.

## Observed result and comparison

The [aggregate run artifact](../registries/pilot-001-score-verification.json)
contains the exact statistic, source hashes, selection checks and environment.

| Quantity | Observed result |
| --- | --- |
| Published discovery score rows | 135, each with a unique annotated patient key and sample key |
| Positive / negative class | 52 refractory / 83 sensitive; higher score predicts refractory |
| Positive–negative pairs | 4,316 |
| Concordant / discordant / tied pairs | 3,491 / 825 / 0 |
| Exact empirical AUROC | 3,491 / 4,316 |
| Decimal AUROC | 0.8088507877664504 |
| Decimal half-up rounding to two places | 0.81; does not match 0.83 |
| Absolute difference from printed 0.83 | 0.021149212233549583; exact fraction 1,141 / 53,950 |
| Predeclared tolerance ≤0.02 | Not met |
| Published confidence interval | Not recalculated or reproduced. The pinned code's `roc(ci = TRUE)` defaults to a DeLong interval (registry S19); the paper describes a bootstrap (article S99). |

The paper's S12 reports discovery fivefold-CV AUC 0.83 (95% CI 0.77–0.90).
S99 supplies the 83 sensitive / 52 refractory denominator, and S95 describes
scores as the probability of refractory disease. These source locations and
the fixed contract are recorded in the
[analysis specification](../protocols/pilot-001-score-verification.md).

**The comparison is to the printed, rounded value 0.83.** The original unrounded
Figure 3D estimate is unavailable here. Therefore this result does not establish
that its difference from that unrounded estimate exceeds 0.02, nor is it a test
of statistical significance.

The released score sheet has not been established as the exact original
averaged out-of-fold predictions used for Figure 3D. The observed disagreement
could concern score versions, model/output provenance or another unresolved
source relationship. This check does not identify a cause or establish an error
in the original paper.

Follow-up (2026-10-23 review, arithmetic only): score direction does not explain
the gap. From the recorded pair counts, with no re-run, reversing the direction
gives AUROC 825 / 4,316 = 0.191, further from the printed 0.83.
Neither direction recovers the printed value, so the disagreement cannot be
settled by relabelling the positive class.

## Execution and technical verification

The [implementation](../tools/verify_published_auc.py) and specification were
committed **before execution** at
`3ff523ffc1fc0750d4a82594f27f1d314c017b67`. Version 0.2 changed the execution/review
record only; the numerical contract had already been set in version 0.1. The
run's protocol, tool and shared-loader hashes matched the retained files at the
result commit. The shared loader later gained a pre-parse guard that only adds
rejections; see the [registry note](../registries/README.md) on recorded hashes.

Command:

```sh
python3 tools/verify_published_auc.py > /tmp/asma-score-verification.json
```

The process ran from 16:02:47.871599 to 16:02:50.669046 UTC on 2026-10-23
(2.797448 seconds reported elapsed), using CPython 3.12.14 and the standard
library on Linux 6.18.55, x86_64. The statistic is deterministic; no random seed
or model-training environment was involved.

Both NLM workbooks passed their fixed byte-count, MD5 and SHA-256 checks. Each
score joined exactly to one clinical annotation; the 135-row score membership
matched the audited reconstruction. The one retained missing location-group
annotation remained missing and was not used to change membership.

Pairwise concordance and an independent average-rank formula agreed as exact
fractions. A separate technical check using descending-score ROC trapezoids
also returned **3,491/4,316**. That additional check shared the pinned workbook
parser and exact-join helpers: its independence concerns arithmetic, not source
interpretation, patient identity or prediction provenance. No alternate cohort,
direction, threshold, confidence interval or performance metric was tried.

The retained aggregate artifact has SHA-256
`33dbc9abe8df6061172651b648562bc030619b218083821a23efd8ab7653360f`.
Raw workbooks, patient/sample keys, clinical rows, individual scores and ROC
thresholds were processed only in memory and were not retained in the repository
or emitted to chat. The workbook-holding processes have ended.

Offline tests and registry/link checks validate the implemented arithmetic,
failure handling and repository consistency. They do not establish clinical
validity, patient independence, the original model's training procedure or
external scientific approval.

## Disposition and next evidence needed

This is a completed, unsuccessful comparison of supplied-score AUROC with the
specified published reference. **It is not a completed model reproduction.**
Gate 2 remains open, and the result stays preliminary pending external scientific
review. The user's execution instruction is recorded separately from that
unfulfilled review; agent checks do not substitute for it.

The next source question is whether `FFPE_pred_scores` contains the exact final
averaged discovery out-of-fold predictions used for Figure 3D. Resolving it
requires the relevant score-generation/version history, original unrounded
estimate and missing fold/workspace provenance. Once available, record the
evidence and any justified specification change before another comparison.
Do not change tolerance, exclusions or direction to force agreement.

The [independent follow-up](pilot-001-independent-progress.md) locates the
repeated-CV score object but finds no export linking it to the workbook. It also
tests matrix linkage and documents a supplement-legend mismatch; neither finding
establishes the cause of the AUROC discrepancy.

The [source request](../templates/pilot-001-source-request.md) remains unsent.
After the unsuccessful posting attempts, the user placed external outreach on
hold; no authors or outside reviewers will be contacted without a new explicit
instruction. Follow-up (2026-10-24): that instruction was given for the
consolidated source request, which the owner sends; reviewer recruitment remains
on hold. Owner decision (2026-10-25): the request is a draft only, sent solely by the owner at their discretion; it remains unsent (see the [README](../README.md)). Full reproduction also still needs the missing helper,
original execution environment, intended transformations and corrected-legend
confirmation. No independent-patient validation or clinical/treatment claim
follows from this result.
