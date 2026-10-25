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
its pinned-image run is still pending. A3 adds a policy for warnings and messages
from model calls, raised in a review of the model adapters.

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

## A2. Sensitivity configuration (proposed configuration and owner options)

The contract requires one fixed sensitivity configuration, resolved by a dated
amendment before any research run. The code-audit addendum asks for it next to
exact versions, because any chosen environment is new rather than the authors'.

### Option A (proposed): XGBoost `tree_method = "hist"`

- **What changes.** XGBoost uses `tree_method = "hist"`, with its default 256
  bins, instead of the declared `"exact"`. Registry S20 records two default
  changes in XGBoost 2.0: the tree method becomes `"hist"`, and the logistic
  intercept is estimated. This configuration varies the first. It runs with the
  pinned packages, so no second environment is built.
- **What stays the same.** Inputs, folds, seeds, the elastic net, the random
  forest, aggregation and all other XGBoost settings, including
  `base_score = 0.5`, so the intercept change is not varied.
- **Order.** It runs after the primary configuration and in the same execution
  context.
- **Reporting.** Its repeat-averaged AUROC, plus the A1 distribution if A1 is
  adopted, is reported as exploratory beside the primary result. It is not
  compared with 0.83, not used to choose a model, and does not replace the
  primary result if the two differ.

**What it measures.** Each training set has 108 rows, so a feature has at most
108 distinct values, fewer than the 256 bins. As a review pointed out, `"hist"`
then considers the same candidate splits as `"exact"`. It mainly moves each
threshold within the gap between two adjacent training values. So it measures
how much the result depends on that threshold placement, plus occasional
tie-breaking. It does not test the histogram approximation, the estimated
intercept, the elastic net, the forest or any other part of the environment. Its
leverage on the environment question is limited.

The evidence comes from a development environment with the pinned glmnet,
randomForest and xgboost versions; the pinned image was not available. Only
abstract fixtures were used:
- **Same splits.** On the 500 outer folds of the full synthetic fixture, 498
  XGBoost fits had the same split features, training-row partitions and gains in
  all 100 trees, and identical training-row predictions. So did all 22 fits on
  `rnorm` fixtures like those in the model tests.
- **Thresholds.** `"exact"` puts each threshold midway between two adjacent
  training values; `"hist"` puts it at the upper value.
- **Ties.** In the other 2 fits, two splits in the first tree had equal gain, and
  the methods broke the tie differently. This can happen on any data: in the
  first tree every gradient is ±0.5, so the gain depends only on class counts.
- **Held-out rows.** A held-out value between a midpoint and the next training
  value is routed differently. Over the 500 folds, 32.8% of the 13,500 held-out
  XGBoost probabilities changed. Among those, the median change was 0.024, the
  90th percentile 0.11 and the largest 0.66. After averaging over 100
  repetitions, with XGBoost weighted by a third in the ensemble, final scores
  changed by at most 0.048 (median 0.0013).

These results describe software behaviour on artificial values. They do not show
how much the study AUROC would change.

Implementation: `fit_models` takes `xgb_tree_method`, which must be `"exact"`
(the default, used by the primary run) or `"hist"`. The synthetic tests check the
following:
- an explicit `"exact"` equals the default;
- `"hist"` changes only the XGBoost component and keeps class 1 scored higher;
- held-out rows that copy training values get identical `"exact"` and `"hist"`
  probabilities, the premise above;
- any other value is rejected before fitting.

The pinned-image runner repeats these checks when the suite is rerun there. No
research runner is enabled by this change.

### Option B: a second, disjoint block of fold seeds

The same review suggested this as having more leverage.

- **What changes.** Outer seeds 101–200 replace 1–100. The record's rules then
  give inner elastic-net seeds `10000 + 100r + f` = 20101–30005 and XGBoost seeds
  `20000 + 100r + f` = 30101–40005, for r = 101…200 and f = 1…5. The forest seed
  stays 1,000,000 before each fit. Everything else matches the primary
  configuration.
- **Seed checks** (development environment). Within the block, no value seeds
  two roles. Its inner seeds take the same 500 values as the primary block's
  XGBoost seeds. They start different operations in separate runs, so no seed
  starts the same operation twice. All 200 outer seeds give different outer
  partitions. A partition depends only on the seed and the 83/52 class sizes, so
  this holds for any keys.
- **What it measures.** How much the repeat-averaged AUROC depends on which 100
  fold assignments were drawn. It does not vary the software environment. It
  gives one more value of the target, so the two values differ by one observed
  amount, not an estimated spread.
- **Relation to A1.** A1 shows how single repetitions vary within a block. It
  cannot show how much the 100-repetition average varies, because scores are
  averaged before the AUROC is computed. Option B shows one such difference
  directly. If A1 is adopted, the block's own distribution can be reported too.
- **What is lost if chosen alone.** The code-audit addendum's question of
  environment and version sensitivity stays unmeasured, as under the waiver.
- **Order and reporting.** As for option A. If both options run, option A runs
  first and option B second, both after the primary configuration.
- **Implementation.** Proposed work, not done. `run_reconstruction` uses the
  repetition number as its outer seed, and the model adapter accepts repetitions
  1–100 only. A seed-block argument, tests and a regenerated execution record
  would be needed.

Option A is still proposed because it is the only option here that varies an
environment setting named in the code-audit addendum, and it needs no second
environment. If the owner's question is how much the target depends on fold
assignment, option B is more informative. Each option adds a second full set of
model fits on study values.

**Waiver.** Declining a sensitivity configuration for the first run would need
the owner to waive the contract's requirement. It would save the extra fits on
study values and one more number to interpret. What is lost: the first run would
not measure how much the AUROC depends on the environment or, beyond A1, on fold
assignment.

## A3. Warnings and messages from model calls (proposed policy)

The decision record says model errors and convergence failures stop the run. The
implementation stops on more than that. A review of the model adapters noted
that one benign warning in any fit would discard a whole run. It asked for the
protocol to fix, before any study values are loaded, which conditions stop a run
and which are only counted.

**Current behaviour**, checked with stub calls in the development environment:
- Any R warning raised in a model call stops the run.
- Any console text, on either output stream, stops the run.
- A nonzero glmnet error code on the outer elastic-net fit stops the run.
- An R message raised inside a model call is discarded and not counted.
  Elsewhere inside the model adapter's boundary, a message stops the run.
- A stopped run reports only that a contract failed, not which model, step or
  condition.

**Reachable sites.** The installed R code of glmnet 4.1-8, randomForest 4.7-1.2
and xgboost 1.7.8.1 was read in the development environment. These `warning()`
sites lie on the declared call paths:

| Site | Raised when | Class under the declared settings |
| --- | --- | --- |
| glmnet `lognet`, error code −k | The kth lambda has not converged after `maxit = 100000` iterations; larger-lambda solutions are returned | Convergence failure, already fatal under the record |
| glmnet `getcoef` | No lambda was fitted ("an empty model has been returned") | Convergence failure |
| glmnet `lognet`, error code below −20000 | Fitted probabilities saturate at the kth lambda; larger-lambda solutions are returned | Potentially benign; depends on the data |
| glmnet `lognet`, error code −10000−k | More nonzero coefficients than `pmax` | Impossible: `pmax` defaults to 64, the number of predictors |
| glmnet `lognet` | A class has fewer than 8 rows | Impossible: the smallest class in any fit has 27 rows |
| glmnet `cv.glmnet`, `cv.glmnet.raw`, `cv.lognet`, `cvtype` | Fraction alignment with a given lambda; under 3 rows per fold; AUC with under 10 rows per fold; an unavailable measure | Impossible: `alignment = "lambda"`, 36 rows per inner fold, deviance |
| glmnet `glmnet` | `alpha` outside [0, 1]; a Cox model | Impossible: `alpha = 0.2`, binomial |
| randomForest `randomForest.default` | A regression response; invalid `mtry`; `maxnodes` too large | Impossible: factor response, `mtry = 8` of 64, `maxnodes = NULL` |
| randomForest `predict.randomForest` | Proximity requested without new data | Impossible: new data given, no proximity requested |
| xgboost `check.booster.params`, `check.deprecation`, `xgb.train` | A repeated parameter; a partially matched deprecated argument; a native `seed` | Impossible: a fixed list of unique parameters, no extra arguments, no `seed` |

Other sites and limits:
- In the three packages' R code, the only `message()` sites are package startup
  messages. The adapter calls the packages through `::`, which loads them without
  attaching, so these are not reached.
- Other sites (Cox and relaxed fits, glmnet's family-object path, plots,
  `xgb.cv`, model loading) are not on the declared call paths.
- Not covered: warnings and messages from base R, Matrix or other dependencies
  that these packages call. The development environment's Matrix (1.7-6) differs
  from the pinned image's (1.7-2), so the fixture runs below do not cover the
  pinned Matrix either. In the development build, none of the three compiled
  libraries imports R's C-level warning function. Console text from compiled code
  stops the run.

**Fixture runs.** In the development environment (not the pinned image), with the
declared settings, 210 elastic-net, 210 XGBoost and 48 random-forest fits raised
no warning, message or console text. The abstract `rnorm` fixtures had no
signal, planted signals up to complete separation, or collinear, duplicated,
constant, heavy-tailed or rescaled columns. Every outer glmnet error code was 0.
With settings that are not declared, `maxit = 1` and `pmax = 3` raised the
convergence and `pmax` warnings, so the check could see them. The saturation
code could not be induced, even on a separable fixture with glmnet's deviance
stopping rules switched off. Fixture runs cannot show what study values will
raise.

**Proposed policy:**
- **Fatal, as now:** every error, every R warning from a model call, any console
  text, and any nonzero glmnet error code on the outer fit. Every `warning()`
  site found on the declared paths in the three packages' R code, except
  saturation, is either a convergence failure, which the record already makes
  fatal, or impossible with the validated inputs. Saturation could not be
  induced on fixtures.
- **Messages:** an R message inside a model call also stops the run, instead of
  being discarded. No `message()` site on the declared paths was found in the
  three packages' R code, and none appeared in fixture runs. Messages from base
  R, Matrix or other dependencies were not enumerated. An unexpected message is
  no longer lost silently.
- **Failure code:** a stopped run records a fixed aggregate code. It names the
  model, the step (fitting or prediction) and the condition class (error,
  warning, message, console text or glmnet error code). It holds no condition
  text, patient keys or values. It would also meet the decision record's
  existing requirement to record aggregate failure reasons without patient keys
  or values. The current implementation does not meet that requirement, so
  rejecting the code would leave it unmet.

What is lost: one saturation warning in any of the run's 2,000 elastic-net path
fits (four per outer fold) discards the run. So does a benign warning or message
from a source not enumerated above. The run gives no AUROC, so revising
the policy afterwards involves no choice made after seeing performance. A rerun
still needs a new amendment and the owner's instruction, and it repeats the
fitting on study values.

**Alternative the owner may choose.** Count saturation codes instead of stopping;
all other conditions stay fatal. If the outer fit saturates, its lambda path is
shorter, and `lambda.min` is chosen from the remaining lambdas. If an inner-fold
fit saturates, `cv.glmnet` still scores every outer lambda; for lambdas beyond
that fold's shorter path, its held-out predictions are held at its last fitted
solution. The aggregate record gives the number of affected fits. What is lost:
affected fits depart from the declared path, and the result reports this only as
a count. A misclassified condition could also pass unnoticed.

**Implementation.** Proposed work, not done. The message change, the failure
code and the counting alternative each need changes to the model adapters, the
silent-call boundary and the runners' allow-listed output, with tests. The
execution records would then be regenerated. This amendment changes no R code
for A3.

## Owner decision required

Before any research run, the owner records a dated decision here:

- **A1:** accept, or reject (the computation is then removed).
- **A2:** accept option A (`"hist"`), choose option B (outer seeds 101–200), run
  both, specify a different configuration, or waive the requirement for the
  first run.
- **A3:** accept the proposed policy, choose the counting alternative, or specify
  another. Its implementation follows the decision and precedes any research run.

No decision has been recorded.
