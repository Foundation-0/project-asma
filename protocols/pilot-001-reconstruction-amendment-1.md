# Pilot 001: reconstruction decisions, amendment 1

**Version:** 1.0, 2026-10-25. **Status:** proposed; not adopted until the owner
records a dated decision below. Merging this file, including a merge by an
automated session, does not adopt it.

It does not edit the hash-pinned
[decision record](pilot-001-reconstruction-decisions.md) (version 1.0). Run
records must pin both files. No study data have been fitted, and nothing here
changes after seeing a research result.

The [reconstruction contract](pilot-001-independent-reconstruction.md) lists
three open pre-run items, and each must be resolved by a dated amendment before
any research run. This amendment proposes resolutions for two of them, both
drawn from the [code-audit addendum](../docs/pilot-001-code-audit-addendum.md)
and its review. The third, the per-model direction test, is a synthetic software
test recorded in the [synthetic validation](../docs/pilot-001-synthetic-validation.md);
its pinned-image run is still pending.

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

## A2. Environment sensitivity configuration (proposed configuration)

The contract requires one fixed sensitivity configuration, resolved by a dated
amendment before any research run. The chosen environment is new rather than the
authors', and it includes declared departures. One configuration fixed in advance
shows how much the AUROC depends on one documented environment choice.

Proposed configuration:

- **What changes.** XGBoost uses `tree_method = "hist"` instead of the declared
  `"exact"`. Registry S20 records two default changes in XGBoost 2.0: the tree
  method becomes `"hist"`, and the logistic intercept is estimated. This
  configuration varies the first. It runs with the pinned packages, so no second
  environment is built.
- **What stays the same.** Inputs, folds, seeds, the elastic net, the random
  forest, aggregation and all other XGBoost settings, including
  `base_score = 0.5`, so the intercept change is not varied.
- **Order.** It runs after the primary configuration and in the same execution
  context.
- **Reporting.** Its repeat-averaged AUROC, plus the A1 distribution if A1 is
  adopted, is reported as exploratory beside the primary result. It is not
  compared with 0.83, not used to choose a model, and does not replace the
  primary result if the two differ.

Implementation: `fit_models` takes `xgb_tree_method`, which must be `"exact"`
(the default, used by the primary run) or `"hist"`. The synthetic tests check the
following:
- an explicit `"exact"` equals the default;
- `"hist"` changes only the XGBoost component and keeps class 1 scored higher;
- any other value is rejected before fitting.

No research runner is enabled by this change.

**Alternative the owner may choose.** Declining a sensitivity configuration for
the first run would need the owner to waive the contract's requirement. It would
save one more full fit on study values and one more number to interpret. What is
lost: the first run would not measure how much the AUROC depends on the
environment.

## Owner decision required

Before any research run, the owner records a dated decision here:

- **A1:** accept, or reject (the computation is then removed).
- **A2:** accept the proposed `"hist"` configuration, specify a different one,
  or waive the requirement and decline it for the first run.

No decision has been recorded.
