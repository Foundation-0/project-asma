# Pilot 001: synthetic pipeline validation

**Executed software validation; no study-data model fit.** An original R
implementation of the frozen [reconstruction decisions](../protocols/pilot-001-reconstruction-decisions.md)
passed all 179 assertions and a complete 100-repeat run in the pinned image on
2026-10-27 (see [Pinned-image rerun](#pinned-image-rerun-2026-10-27)); the first
record (2026-10-25) covered 149. The [execution record](../registries/pilot-001-synthetic-validation.json)
contains aggregate coverage, UTC timing, package/toolchain inventory and hashes.
It contains no fixture predictions or clinical performance result.

## Implementation and evidence

| Component | Executed checks |
| --- | --- |
| [Input assembly](../R/asma_input.R) | 41 assertions: exact identities, complete replicate groups, exclusions, panel/order checks, hand-calculated means, retained missing location, and rejection of conflicting or missing inputs |
| [Folds and aggregation](../R/asma_core.R) | 87 assertions (77 in the first record; the additions are described below): patient-disjoint and balanced folds, RNG preservation, row-order invariance, complete prediction coverage, deterministic averaging, independent AUROC formulas, and sanitized errors/output |
| [Model adapters](../R/asma_models.R) | 51 assertions (31 in the first record; the additions are described below) with actual glmnet, XGBoost and randomForest fits: pinned versions, deterministic reruns, prediction order, input preservation, and unchanged predictions when unrelated held-out rows change |
| Full integration | 135 artificial subjects × 64 features; 100 repetitions × 5 outer folds; 40,500 model predictions, 13,500 ensemble predictions and 135 final scores; complete coverage and agreement between pairwise and rank-based AUROC calculations |

The model fixture carries no label signal, so these assertions do not show that
each model scores refractory (class 1) higher. A planted-signal direction test
was added as a pre-run requirement of the
[reconstruction contract](../protocols/pilot-001-independent-reconstruction.md);
it passed in the pinned image on 2026-10-27 (see below).

**Addition, 2026-10-25 (after the first execution record).** The first record and
its 149-assertion count predated these tests; the 2026-10-27 rerun covers them.

- **Direction.** A planted-signal fixture adds a fixed shift of 1.5 on eight
  artificial features for class 1. For the elastic net, XGBoost and the random
  forest separately, class-1 held-out rows must receive a higher mean probability
  and a fixture AUROC of at least 0.8. A flipped probability must fail the same
  check. These are software checks, not simulated clinical evidence.
- **Non-trivial order checks.** The elastic net's predictions must vary on that
  fixture, and the held-out reordering and isolation checks are repeated on it.
- **Fold wiring.** Every fold, training set and inner fold captured inside
  `run_reconstruction` must match an independent recomputation from the declared
  seeds: outer r, inner 10000 + 100r + f.
- **Fold assignment.** Golden vectors pin which key lands in which fold. An
  11-key case (7/4 classes, K=3, seed 7) has a fold mapping derived by hand from
  R's `sample.int` output after `set.seed(7)` under the declared RNG kinds. The
  135-key fixture (83/52, K=5, seed 1) is pinned as a literal string of fold
  digits; a separate base-R recomputation gave the same string. The fold-wiring
  check recomputes with the same function, so it cannot catch a change to the
  algorithm itself; these catch changes that alter the pinned assignments.

The suite now has 162 assertions: 41 input, 81 core and 40 model. The fold check
covers both the observer's copy and the arguments the model adapter receives.

Six deliberate mutations each fail the new suite but pass the previous one:
- inverting the elastic net's probability;
- inverting XGBoost's probability;
- taking the forest's class-0 column;
- reversing glmnet's factor levels;
- shifting the inner-fold seed;
- passing the model adapter different inner folds from the observer's.

Fold-algorithm mutations each fail both golden assertions:
- processing class 1 before class 0;
- restarting the round-robin at fold 1 for class 1;
- the "Rounding" sample kind;
- permuting with `order(runif(n))` instead of `sample.int`;
- a seed one higher or one lower.

The suite before the golden vectors (79 core assertions) already rejects the
first two through its fold-size and class-count checks. It passes the others.
Replacing `members[sample.int(length(members))]` with `sample(members)` passes,
as it should: for more than one element, base R's `sample(x)` is
`x[sample.int(length(x))]`, so the draw is the same.

[Amendment 1](../protocols/pilot-001-reconstruction-amendment-1.md) (proposed,
pending an owner decision) adds the per-repetition AUROC distribution and six core
assertions. It also adds four model assertions for the proposed `"hist"`
sensitivity setting, giving 172: 41 input, 87 core and 44 model. The fixtures are:
- constant scores;
- alternating scores, where every repetition's AUROC is 0 or 1 but the averaged
  scores all tie;
- fold-offset scores, where each within-fold AUROC is 1 but the 135-score AUROC
  is lower. Every reported field must match an independent recomputation.

Averaging fold AUROCs, using quantile type 6, swapping fields, reporting the
median as the mean, or pooling repetitions each fail these assertions. For the
`"hist"` setting, the explicit default must equal the declared `"exact"` fit.
`"hist"` must change the XGBoost predictions on the planted-signal fixture, keep
class 1 scored higher, and leave the elastic net and forest unchanged. Any other
value must be rejected. Four mutations each fail these checks:
- ignoring the setting;
- removing the guard;
- making `"hist"` the default;
- letting the setting change the forest's seed.

A fourth assertion checks the premise of A2: held-out rows that copy training
values must get identical `"exact"` and `"hist"` XGBoost probabilities. Three
mutations fail it and pass the rest of the suite. Each changes `"hist"`
fits only: 16 bins, a different `eta`, or a different `min_child_weight`.

**Fitted settings.** `fit_models` now checks each fitted object against the
declaration and stops before predicting if any check fails. This addresses
non-blocking item 1 of the
[#11 review](https://github.com/Foundation-0/project-asma/pull/11#pullrequestreview-5641905944).
- **XGBoost.** The booster's own configuration (`xgb.config`) must show:
  - the objective, booster and tree method;
  - all eleven declared training values;
  - `base_score`, one thread and 100 trees.

  In xgboost 1.7.8.1's R package, an unused (for example misspelled) parameter
  is reported only as console text, never as an R warning, at any verbosity. So
  the warnings-as-errors rule cannot catch it, but this check can.
- **Random forest.** It must be a classification forest with `mtry` 8, class
  importance and a 108 × 108 proximity matrix.
- **Elastic net.** It must be a binomial fit with class names `"0","1"`, the
  deviance measure and at most 100 λ values. The fitted object does not report
  `alpha`, so the check reads it from the recorded call. That only restates the
  literal 0.2 passed in; it is not evidence read from the fit. `cv.glmnet` keeps
  no fold IDs with the declared `keep = FALSE`, so the fold wiring test checks
  the folds passed in instead.

Seven model assertions test the XGBoost check directly, giving 179: 41 input,
87 core and 51 model. Fits with the declared exact and `"hist"` settings must
pass. Each of these must fail it:
- a changed `eta`;
- a changed `base_score`;
- a misspelled `max_depth`;
- the wrong tree method;
- 99 rounds.

Nine mutations fail the new suite:
- in the forest, `mtry` 7 or no importance;
- in the elastic net, `alpha` 0.5 or the classification-error measure;
- in XGBoost, a misspelled `max_depth`, `eta` 0.3, `base_score` 0.6 or 99
  rounds;
- removing the check's training-value comparison.

The first eight also pass the previous suite; the ninth removes code that suite
does not have. The check compares against a second copy of the declared values, so it
detects a setting that did not take effect or drifted from that copy. A
consistent edit of both copies would still need review against the decision
record.

These results come from a development environment, not the pinned image. It used
conda-forge R 4.4.3 with the pinned versions of glmnet (4.1-8), randomForest
(4.7-1.2), jsonlite (1.9.1) and data.table (1.17.0). xgboost 1.7.8.1 was built
from the CRAN read-only GitHub mirror's tagged source, because conda-forge has no
matching build.

Other components differ from the pinned image: Rcpp 1.1.2 (pinned 1.0.14),
Matrix 1.7-6 (recorded 1.7-2), survival 3.8-12 and lattice 0.23-1, and the conda
compiler toolchain. Each model's fixture AUROC was 1.0. A pinned-image rerun of
all 179 assertions, with a regenerated execution record, was required before any
research run; the 2026-10-27 rerun below meets it.

## Pinned-image rerun, 2026-10-27

The runtime was rebuilt from the same pinned inputs (`rocker/r-ver` base by
digest, hash-checked CRAN sources, build networking disabled) and both runners
were executed in it. Results, now in the
[execution record](../registries/pilot-001-synthetic-validation.json):

- **All 179 R assertions passed** (41 input, 87 core, 51 model), including the
  planted-signal direction test, the golden fold vectors, the fold-wiring check,
  the fitted-settings checks and the amendment 1 code. A separate run without
  `--full` (the R runner's `--tests` mode) took 14.7 seconds; its output was not
  committed, and the record is the `--full` run below. These are the first runs
  of those tests on the pinned toolchain (Rcpp 1.0.14, Matrix 1.7-2).
- **The full 100-repeat integration passed** in 104.9 seconds: 40,500 model
  predictions, 13,500 ensemble predictions and 135 final scores, complete
  coverage, and agreement between the pairwise and rank-based AUROC calculations.
  No AUROC value is emitted or compared with the paper.
- **Rebuild fidelity.** The installed package inventory and toolchain equal the
  2026-10-25 record exactly. The image ID differs (`sha256:c7592401…` versus
  `sha256:93037440…`): the rebuild used Docker 29 with the containerd image store,
  and pinned inputs do not imply bit-identical images. It is recorded as a new
  runtime, not substituted for the old one.
- All 16 implementation hashes in the new record match the committed files,
  including both hash-pinned protocol files.

The development-environment results above (mutation runs, the 1.0 fixture
AUROCs and the amendment 1 fixture probes) were not repeated here; only the
committed suites were run.

The first full run (2026-10-25), including 149 assertions, took 57.619 seconds
inside R; the 2026-10-27 recorded run, including 179, took 104.858 seconds.
These are observed fixture runtimes, not compute estimates for source ingestion
or a scientific performance measurement. No artificial
AUROC is compared with the paper's 0.83 or the existing supplied-score result.

The [fixture generator](../tests/r/synthetic_fixture.R) constructs abstract keys,
feature names and numeric values from mathematical formulas. Its geometry
exercises 168 biological measurements, five triplicate groups, 158 sample/subject
identities and 135 selected subjects with 83/52 class balance. It also includes
an explicit nonpatient control and an unmatched column, plus an unused feature.
Its 145 selected measurements are a **fixture property**, not a newly measured
study count. These values are not synthetic clinical evidence and were not
estimated from research measurements.

Input assembly, folds, model calls and predictions remain in memory. Tests include
hand-calculated examples and deliberate failures, rather than relying only on a
successful model fit. The full integration uses actual package APIs; separate
control-flow tests use stubs to verify exact aggregation and failure behavior.

Integration corrected an adapter guard to accept 66/42 or 67/41 training-class
counts after a 27-subject held-out fold. Package checks normalize R's equivalent
hyphen/dot version notation. The silent-call boundary captures both R output
streams, and the container runs with the invoking user's UID and GID (`--user`),
so private file permissions work with all capabilities dropped. These are implementation fixes; the frozen
scientific choices and earlier score-verification result are unchanged.

## Runtime and boundaries

The [source manifest](../runtime/synthetic-packages.json) pins ten downloaded
package archives by size and SHA-256, records dependency/license metadata, and
pins the Linux amd64 base image by digest. The installed record includes R 4.4.3,
glmnet 4.1-8, XGBoost 1.7.8.1, randomForest 4.7-1.2, all installed dependencies,
Ubuntu 24.04.4, GCC/Fortran 13.3 and BLAS/LAPACK paths. The runtime was built and
tested locally; no image or third-party source archive is redistributed here.
Package notices remain applicable to any later runtime distribution. No project
license grant has been added.

The builder downloads only the declared public software archives, verifies them,
and compiles with build-step networking disabled. Execution uses the local
Docker daemon, a read-only root and checkout, disabled network, dropped Linux
capabilities, no new privileges, disabled core dumps and swap, a 256 MiB temporary
filesystem, an 8 GiB memory limit and a two-CPU limit. Model thread counts are one.
The wrapper enforces a two-hour timeout and attempts removal of its uniquely
named container even after failure. These are recorded invocation controls;
they do not certify host isolation, Canadian hosting or memory erasure.

The [Python runtime tests](../tests/test_synthetic_runtime.py) check hash/size
failures, bounded downloads, source selection, local daemon configuration,
execution controls, timeout cleanup, sanitized cleanup failures and rejection
of dataset arguments. They run offline without Docker; the separate R run
provides actual package and container integration evidence. At `2c9d68a`
(2026-10-25), the offline validator and all 94 Python tests passed. An independent
[review of the pipeline PR](https://github.com/Foundation-0/project-asma/pull/11#pullrequestreview-5641905944)
(2026-10-25, at `2c9d68a`) verified all 15 recorded implementation hashes and the
package pins. Its one blocking finding was that probability direction was
claimed but untested; the planted-signal test above now covers it. This internal
software review is not external scientific review.

## Commands

Use Python 3.10+ on a Linux host with Docker access through
`/var/run/docker.sock`. The build targets `linux/amd64`. From the repository root:

```sh
python3 tools/build_synthetic_runtime.py
python3 tools/run_synthetic_pipeline.py
python3 tools/run_synthetic_pipeline.py --full
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

The first command downloads the pinned base image and package sources and may
take several minutes. An optional `--source-cache` directory can supply package
archives; each is still checked against the manifest. The second command runs
all R assertions (179 in the 2026-10-27 record);
`--full` also performs the complete 100-repeat integration.
Each runner prints reviewed aggregate JSON only. The wrapper resolves the local
image tag to its immutable image ID before execution. Input pins do not imply
bit-identical rebuilds or identical scores across platforms.

## Remaining work

The synthetic entry point accepts no study-file path or URL. The
[source adapter](pilot-001-source-adapter.md) revalidates the pinned
member/workbook bytes, parses values in memory and passes them to the same input
contracts. It has been tested only with generated fixtures, most recently in the
2026-10-27 pinned-image rerun, and has not read study bytes. The
[data-use disposition](pilot-001-data-use.md) still requires a supported actual
jurisdiction, host and applicable review/privacy context before study-data fitting.
The current fixture run does not establish those conditions.

Unknown upstream preprocessing and workspace history, the corrected-legend gap,
validation-patient independence and external scientific review remain open.
External outreach stays on hold. The next independent step is to complete the
research-execution preflight: a probe of the current runtime on a cgroup v2 host
and a pinned-image rerun of the adapter fixture after the attestation changes. Synthetic
success neither reproduces the published result nor establishes clinical validity.
