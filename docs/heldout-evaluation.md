# Offline independent-patient evaluation

`tools/evaluate_heldout.py` is original Python standard-library code, tested only
on abstract fixtures. It has no file/network loader, CLI ingestion or model fitting.
It does not change the frozen discovery reconstruction or authorize a study run.

The API requires one unique patient key, binary label (1 = refractory), and
probability from each frozen model per evaluation patient. Key sets must agree.
Row position never joins predictions. Development keys must inventory everyone
used for fitting, feature selection, preprocessing and alignment. Calibration
keys are supplied separately. Either set overlapping evaluation is rejected.
Calibration may overlap development: disjoint calibration is preferable, but
the code does not silently assert it. A caller must explicitly attest complete
development inventory, upstream independence and models/thresholds frozen before
evaluation. Those assertions do not establish the facts. Unknown upstream scope
cannot be repaired by setting booleans. Repeated-CV designs are rejected.

Call `calibrate_threshold` with calibration labels/probabilities and the desired
specificity, then freeze its return before accessing evaluation outcomes.
Prediction is positive at `score >= threshold`. The cutoff is the smallest
representable value above the negative-score boundary allowing at most the
specified false-positive count. All boundary ties are excluded conservatively.
Positive calibration scores do not set the cutoff. Both classes are still
required, so a calibration set missing a class is rejected; this does not detect
swapped or partly wrong labels. A cutoff just above 1 means predict none.
Empirical calibration specificity is not a population guarantee. The evaluator
accepts externally frozen thresholds. It cannot prove their selection history.

`evaluate_heldout` reports AUROC (half credit for ties), grouped average
precision (sum of precision times recall increments at distinct scores, **not
trapezoidal PR area**), Brier score, sensitivity, specificity and confusion
counts. All inputs must be probabilities in [0,1]. A prevalence comparator uses
a separately supplied classifier-training patient set and labels, which must be
contained in the broad development inventory. It uses a fixed 0.5 classification
threshold. Sensitivity/specificity differences against it are not comparisons at
the same specificity target. Because the comparator is constant, its thresholded
sensitivity/specificity and their differences are always structural: 0/1 below
0.5, 1/0 at 0.5 or above. Ranking and probability metrics remain meaningful.
This module has no loader by design. A caller supplies keyed predictions in
memory, so patient-level scores need not be persisted to reach it. Its AUROC
uses half credit for ties, matching `checked_auc` in `R/asma_core.R`, which also
checks pairwise agreement against rank agreement.

Supply additional keyed predictions for a separately trained regularized
logistic baseline. This module does not fit it. Set `reference_model` to a
supplied model key (for example a regularized logistic baseline) or the default
`"prevalence"`. Fix this choice before evaluation, never select it using
outcomes. `differences_from_reference` and paired intervals are model minus the
named reference. Lower Brier is better.

The ordinary patient bootstrap uses the same sampled patient indices for every
model and the prevalence comparator. Models, baseline prevalence and thresholds
remain frozen. It reports percentile 95% intervals using linear interpolation,
paired difference intervals and class-empty draw counts. Class-empty draws are
excluded for all metrics, not redrawn. Thus intervals condition on both classes
being represented. Fewer than 1,000 valid draws returns no interval, with an
explicit status and reason. This conservative software minimum limits extreme Monte Carlo
undersampling. It is not a coverage guarantee. Small requested draw counts
remain allowed for software tests only.

Each metric and paired difference also carries an interval status and observed
bootstrap range. `degenerate` means all valid draws gave the same statistic.
The interval is retained and explicitly flagged. This can be structural (a
constant baseline or identical models) or a boundary artifact, not evidence of
precise population performance. Percentile endpoints can coincide even when
rare draws differ. The full bootstrap range makes that distinction visible.

These intervals describe sampling of independent evaluation patients conditional
on fitted models and thresholds. They omit training, feature-selection,
calibration and model-selection uncertainty. They are not valid repeated-CV
uncertainty estimates. Bootstrap intervals can collapse at perfect observed
specificity. They must not support a high-specificity guarantee. Correlated
patients or clustered sampling require a different design. Selected refractory
and sensitive cohorts do not establish population prevalence or risk calibration.
Brier score alone is not a calibration assessment.

The abstract 13-negative perfect-classification test illustrates the boundary:
the bootstrap specificity interval is [1,1] and flagged `degenerate`, while the
one-sided exact 95% lower specificity bound is about 79.42%. See the separate
[validation-capacity analysis](pilot-001-validation-capacity.md) for exact
binomial planning, source references and cohort-denominator limitations.

The bootstrap block records the Python version and implementation alongside the
seed, because the bootstrap index sequence is not guaranteed across interpreter
versions.

Before real evaluation, prospectively register cohort/endpoint eligibility,
upstream independence evidence, model definitions, calibration design, threshold
target, comparator, bootstrap seed/count, handling of invalid draws, intended
claims, and a tested, non-persisting transfer route from the R pipeline at
full precision. The default is 2,000 draws and seed 1729. These are software defaults,
not adoption of a research protocol. Resolve the repository's separate data-use,
execution and scientific review gates. The API returns aggregates only, but
small-cell disclosure review remains necessary before publication. No patient
keys, individual scores or fitted models are returned.

Run offline tests with:

```sh
python3 -m unittest discover -s tests -p 'test_evaluate_heldout.py' -v
```

Metric conventions follow the official definitions of [average precision](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
and [binary Brier score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html),
checked on 2026-10-29 (registry S35–S36). The code is original and has no
scikit-learn dependency. The distinction between held-out and cross-validation
uncertainty is also motivated by [Bates, Hastie and Tibshirani](https://arxiv.org/abs/2104.00673v4)
(S34, abstract reviewed). That paper does not validate this implementation.
