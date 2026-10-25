# Pilot 001: synthetic pipeline validation

**Executed software validation; no study-data model fit.** An original R
implementation of the frozen [reconstruction decisions](../protocols/pilot-001-reconstruction-decisions.md)
passed 149 assertions and a complete 100-repeat run using the actual pinned
model packages. The [execution record](../registries/pilot-001-synthetic-validation.json)
contains aggregate coverage, UTC timing, package/toolchain inventory and hashes.
It contains no fixture predictions or clinical performance result.

## Implementation and evidence

| Component | Executed checks |
| --- | --- |
| [Input assembly](../R/asma_input.R) | 41 assertions: exact identities, complete replicate groups, exclusions, panel/order checks, hand-calculated means, retained missing location, and rejection of conflicting or missing inputs |
| [Folds and aggregation](../R/asma_core.R) | 77 assertions: patient-disjoint and balanced folds, RNG preservation, row-order invariance, complete prediction coverage, deterministic averaging, independent AUROC formulas, and sanitized errors/output |
| [Model adapters](../R/asma_models.R) | 31 assertions with actual glmnet, XGBoost and randomForest fits: pinned versions, deterministic reruns, probability direction/order, input preservation, and unchanged predictions when unrelated held-out rows change |
| Full integration | 135 artificial subjects × 64 features; 100 repetitions × 5 outer folds; 40,500 model predictions, 13,500 ensemble predictions and 135 final scores; complete coverage and agreement between pairwise and rank-based AUROC calculations |

The full run, including all 149 assertions, took 57.619 seconds inside R on the
recorded environment. This is an observed fixture runtime, not a compute estimate
for source ingestion or a scientific performance measurement. No artificial
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
streams, and the container runs as the checkout owner so private file permissions
work with all capabilities dropped. These are implementation fixes; the frozen
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
provides actual package and container integration evidence. The final offline
validator and all 94 Python tests passed. Independent implementation review
found no blocking issue and verified all 15 recorded source/specification hashes;
this internal software review is not external scientific review.

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
all 149 R assertions; `--full` also performs the complete 100-repeat integration.
Each runner prints reviewed aggregate JSON only. The wrapper resolves the local
image tag to its immutable image ID before execution. Input pins do not imply
bit-identical rebuilds or identical scores across platforms.

## Remaining work

The synthetic entry point accepts no study-file path or URL. A future source
adapter must revalidate the pinned member/workbook bytes, parse values without
persistent patient files, and pass the existing exact input contracts. The
[data-use disposition](pilot-001-data-use.md) still requires a supported actual
jurisdiction, host and applicable review/privacy context before study-data fitting.
The current fixture run does not establish those conditions.

Unknown upstream preprocessing and workspace history, the corrected-legend gap,
validation-patient independence and external scientific review remain open.
External outreach stays on hold. The next independent step is to specify and
test the source adapter and complete the research-execution preflight. Synthetic
success neither reproduces the published result nor establishes clinical validity.
