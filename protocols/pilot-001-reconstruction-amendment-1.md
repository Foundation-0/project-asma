# Pilot 001: reconstruction decisions, amendment 1

**Version:** 1.0, 2026-10-25. **Status:** proposed; not adopted until the owner
records a dated decision below. Merging this file, including a merge by an
automated session, does not adopt it.

It does not edit the hash-pinned
[decision record](pilot-001-reconstruction-decisions.md) (version 1.0). Run
records must pin both files. No study data have been fitted, and nothing here
changes after seeing a research result.

The [reconstruction contract](pilot-001-independent-reconstruction.md) lists two
open pre-run items from the
[code-audit addendum](../docs/pilot-001-code-audit-addendum.md). Each must be
resolved, or declined with a reason, before any research run. This amendment
proposes how.

## A1. Per-repetition AUROC distribution (proposed secondary output)

The primary target is unchanged. It is the AUROC of each patient's average over
100 repetitions of the equal-weight ensemble, compared with printed 0.83 under
the fixed ≤0.02 rule.

Proposed descriptive secondary output:

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

Implementation: `run_reconstruction` already returns these values as
`summary$repetition_auc`, and the synthetic tests check them. Both runners emit
only allow-listed fields, so nothing new is printed. If the owner rejects A1,
remove the computation before any research run.

## A2. Environment/version sensitivity configuration (proposed: decline for the first run)

The addendum asked for one alternative software/version configuration, fixed
before execution. The chosen environment is new rather than the authors'. It
includes declared departures, such as one XGBoost thread and inner elastic-net
folds decoupled from the forest seed. A second configuration would show how much
the AUROC depends on those choices.

Proposed: do not run one in the first research run.

- **Compute and multiplicity.** It would double fitting on study values and add a
  second performance number to interpret.
- **Reproducibility.** Exact R and package versions are pinned, and XGBoost's
  `tree_method` and `base_score` are explicit. The first run is therefore
  reproducible, although it does not measure environment dependence.
- **No post-hoc swaps.** Swapping configurations after seeing a result is already
  forbidden.

**What is lost.** The first run would give no estimate of how much the AUROC
depends on the chosen environment and the declared departures. Any later
sensitivity analysis must be specified and recorded here before it runs, and
reported as exploratory, separately from the primary result.

## Owner decision required

Before any research run, the owner records a dated decision here:

- **A1:** accept, or reject (the computation is then removed).
- **A2:** accept the decline, or specify one environment/version configuration
  to run.

No decision has been recorded.
