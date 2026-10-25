# Pilot 001: reconstruction decisions, amendment 1

**Version:** 1.0, 2026-10-25. **Status:** proposed; takes effect when the owner
merges it. It does not edit the hash-pinned
[decision record](pilot-001-reconstruction-decisions.md) (version 1.0). Run
records must pin both files. No study data have been fitted, and nothing here
changes after seeing a research result.

The [reconstruction contract](pilot-001-independent-reconstruction.md) lists two
open pre-run items from the
[code-audit addendum](../docs/pilot-001-code-audit-addendum.md). Each must be
resolved, or declined with a reason, before any research run. This amendment does
both.

## A1. Per-repetition AUROC distribution (adopted as a secondary output)

The primary target is unchanged. It is the AUROC of each patient's average over
100 repetitions of the equal-weight ensemble, compared with printed 0.83 under
the fixed ≤0.02 rule.

Add one descriptive secondary output:

- **Computation.** For each repetition, compute the AUROC over all 135
  repetition-level ensemble scores, using the record's exact pairwise rule
  (4,316 pairs, half credit for ties) and the rank-sum cross-check. Do not
  average fold AUROCs or pool repetitions as patients.
- **Reported values.** The count of repetitions, and the minimum, lower quartile,
  median, upper quartile, maximum and mean of the 100 values. Quantiles use R's
  `quantile(type = 7)`. These are aggregate metrics; nothing patient-level is
  added to retention.
- **Interpretation.** The distribution shows how much a single repetition's AUROC
  depends on fold assignment. Averaging scores over repetitions can give a
  different AUROC from a typical single repetition. The distribution is not a
  confidence interval, not a test, and not compared with 0.83. It does not alter
  the primary target, the comparison rule or the stop rules.

Implementation: `run_reconstruction` returns these values as
`summary$repetition_auc`. The synthetic tests check them on constant and
alternating fixtures, including a case where every repetition's AUROC is 0 or 1
but the averaged scores all tie at 0.5.

## A2. Sensitivity configuration (declined for the first research run)

The decision record already excludes alternative model search from the first
run. The amendment proposes not fixing a second configuration for it:

- **Compute and multiplicity.** A second configuration would double fitting on
  study values and add a second performance number to interpret.
- **Version sensitivity is already constrained.** Exact R and package versions
  are pinned, and XGBoost's `tree_method` and `base_score` are explicit.
- **No post-hoc swaps.** Swapping configurations after seeing a result is already
  forbidden.

Any later sensitivity analysis must be specified and recorded before it runs, and
reported as exploratory, separately from the primary result.

**Owner decision.** A2 records a reason to decline, as the contract allows. The
owner may instead require a sensitivity configuration before the first run; in
that case it must be specified here before execution.
