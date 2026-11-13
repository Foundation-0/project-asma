# Pilot 001: pre-run readiness audit (2026-11-08)

**Status:** executed static audit record. **Scope:** `main` @
`4f365cc098baac4461d1e45a075f947fe8fb6c23`. Code, tests, registries and
protocol text were read at that revision; one offline Python unit test
(implementation-hash check) was executed and passed. No first-run, preflight,
build or container command was executed, no study files were fetched, and no
models were fitted. This record does not close any part of Gate 0 and does not
authorize a research run.

This is a dated status correction. The frozen
[decision record](../protocols/pilot-001-reconstruction-decisions.md) is not
edited. Where the [amendment](../protocols/pilot-001-reconstruction-amendment-1.md),
the [reconstruction contract](../protocols/pilot-001-independent-reconstruction.md)
or the [roadmap](roadmap.md) still describe Amendment 1 implementation as
proposed or not done, this record supersedes that status text; the protocol
files keep their historical wording and remain the specification.

## Bottom line

Amendment 1 *mechanisms* landed (first in `34993a9`, "Add Pilot 001 first-run
runner, preflight, and Amendment 1 paths"). The executable first run is
**not yet protocol-conformant**: the real first-run path hard-codes 5
repetitions, so the frozen 100-repetition configurations (outer seeds 1–100
and 101–200) cannot be executed through the documented entrypoint; A3 failure
codes do not yet name model/step/glmnet-code class as specified; A2B seed
derivation is essentially untested; and no genuine pinned-image rerun of the
current test suite is recorded. A conformance fix for the repetitions defect
and host-side validation is proposed in
[#68](https://github.com/Foundation-0/project-asma/pull/68) (open at writing;
this audit describes the pre-fix revision).

## Per-item verdicts

| Item | Mechanism | First-run readiness |
| --- | --- | --- |
| A1 per-repetition AUROC distribution | Done and tested (`R/asma_core.R:251-271`; `tests/r/test_core.R:110-157`) | Partial: real runner would emit `count=5`, not 100 |
| A2 option A (`tree_method="hist"`) | Done and tested (`R/asma_models.R:49-56,141-148`; `tests/r/test_models.R:141-179`) | Partial: exercised at 5 repetitions only |
| A2 option B (outer seeds 101–200) | Implemented; formulas match spec by inspection (`R/asma_core.R:131-168`; `R/asma_models.R:199,211`) | Partial and untested: one 1-repetition stub test (`tests/r/test_core.R:288-289`); no test asserts seeds 101–200, inner-seed ranges 20101–30005 / 30101–40005, adapter bounds, or invalid-block rejection |
| A3 strict policy + aggregate code | Fatality done (warning/message/console/error fatal; no condition text retained, `R/asma_models.R:17-46`) | Partial: all model failures report `ENSEMBLE-FIT` (`R/asma_models.R:165,241`); glmnet error code collapses into `ERROR`; message-stream text degrades to `P001-FAIL-INTERNAL`. Does not meet amendment-1.md:237-239 granularity |
| Per-model direction test | Done and tested (`tests/r/test_models.R:103-120`) | Done |

## Blocking defect: 5 repetitions in the real path

- Real path: `"--repetitions=5"` at `tools/pilot001_first_run/analyze_container.py:90`.
- Dry path: `"--repetitions=5"` at `tools/pilot001_first_run/runner.py:203`.
- The R runner accepts 1–100 (`tools/run_pilot001_reconstruction.R:14-17`) but
  the Python entrypoint exposes no override (`tools/run_pilot001_first_run.py:58-70`).
- The host validator checked only that `repetitions` is an integer and accepted
  any 1–8 allow-listed configurations without label↔seed↔method cross-checks
  (`tools/pilot001_first_run/output_validator.py:103-114,210-252`). The test
  suite's own valid-aggregate fixture used 5 repetitions and 158 "patients"
  and passed (`tests/test_pilot001_first_run.py:53-81`).

Consequence: through the documented entrypoint, A1 would report a 5-value
distribution and A2B would run seeds 101–105. The current first-run command is
a smoke configuration, not the frozen reconstruction.

## Execution-record and freeze caveats

- `registries/pilot-001-synthetic-validation.json` carries 2026-11-04
  timestamps/elapsed/environment with assertion counts (181) and hashes edited
  in place by later commits (`aa944ef`, `5026273`); its integration block omits
  fields the current synthetic runner emits (`tools/run_synthetic_pipeline.R:28-33`).
  There is no recorded pinned-image rerun of the current suite. Restoring the
  record requires a sanctioned synthetic rerun; counts in
  [synthetic validation](pilot-001-synthetic-validation.md) (179) should be
  updated from that rerun, not edited by hand.
- Two registries carry allow-listed stale hashes for
  `tools/probe_execution_conditions.py` (recorded at `ef1f522`); they pass by
  explicit drift allowance and do not describe the current probe file.
- No `implementation_sha256` registry pins the first-run stack
  (`tools/run_pilot001_first_run.py`, `tools/run_pilot001_reconstruction.R`,
  `tools/pilot001_first_run/*`), so the hash freeze does not cover the code
  that would execute a run. Extend freeze coverage after the conformance fixes
  land, from final code.

## Minimal remaining in-repo work (before any research run)

1. Repetitions conformance + validator hardening (proposed in #68).
2. A3 granularity: per-model/per-step operation labels (elastic net, XGBoost,
   random forest × fit/predict) and a distinct glmnet-error-code class, with
   exact-code tests through `fit_models`.
3. A2B tests: 2-repetition wiring test at `outer_seed_start=101` asserting
   outer/inner fold seeds; adapter bound tests (`outer_seed` 200 pass / 201
   fail); seed-formula table tests ((101,1)→30101, (200,5)→40005; inner
   20101/30005); invalid-block rejections; one seed-101 golden fold vector.
4. Sanctioned synthetic rerun in the pinned image regenerating the execution
   record, then doc/count updates from that record.
5. First-run stack added to implementation-hash freeze coverage.

## Owner-only blockers (unchanged; code cannot satisfy these)

- Fresh dated attestation for the run date plus a new explicit instruction.
  The recorded attestation covers 2026-11-05 only ([roadmap](roadmap.md)
  Gate 0). The matching entry must exist in the git-ignored
  `registries/pilot-001-owner-attestations.json`; the reference date must equal
  the run day in America/Toronto (`tools/pilot001_first_run/gates.py:16-42`).
- macOS preflight on the Gate 0 Q1 host in the same invocation, condition (b),
  open ([data use](pilot-001-data-use.md)); runbook steps 0–5 on that host.
- Condition (c), aggregate-only handling throughout the run, open until a run
  completes without breach.
- Dropbox matrix: CONDITIONAL GO on the owner's MacBook only if (a)–(c) hold,
  NO-GO otherwise ([data use](pilot-001-data-use.md)). No separate clearance
  record exists in the data-use disposition; `--dropbox-cleared` is an
  invocation assertion gated in code on host + same-invocation preflight only.

## Provenance note

Roadmap and runbook cite Gate 0 source comments on issue #31. As of this audit
that issue returns 404 from the GitHub API, so those citation links are dead.
The decisions remain recorded in [roadmap](roadmap.md) Gate 0; restoring a
canonical link target is an owner decision. This audit does not change any
Gate 0 decision.

## What this audit does not establish

Static inspection cannot establish that the pinned runtime executes correctly
on the Q1 host, that study inputs parse, or any scientific result. Hosted CI
results were not consulted as audit evidence. R test suites were read, not run
(no local R runtime); their execution record is the synthetic-validation
record discussed above.
