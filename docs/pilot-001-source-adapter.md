# Pilot 001: source adapter and execution-condition check

**Executed software and runtime checks; no study-data ingestion or fitting.**
The source adapter is implemented and tested with generated source-format files.
The combined Python/R container passed 40 observed technical checks. Actual
processing jurisdiction, hosting terms and applicable research/privacy obligations remain
unverified, so these checks do not open study-data execution.

## Source adapter

The original [Python adapter](../tools/source_data_adapter.py) offers two explicit
APIs. `parse_sources()` accepts bytes already held in memory; `load_pinned_sources()`
acquires only the fixed releases and passes their bytes to that parser. Neither
is invoked on research sources by a command-line entry point in this change.
Calling the acquisition API requires a supported execution context for the
whole data path; the function is not an approval mechanism.

The default contract preserves the prior [member audit](../registries/pilot-001-author-feature-summary.json)
and [supplement pins](../registries/pilot-001-supplement-summary.json). Acquisition
uses bounded ZIP ranges, validates the central directory and local header,
rechecks the directory, and limits each workbook read to its expected size plus
one byte. Unexpected responses, overflow or changed source identity stop the run.
The complete archive is not downloaded or claimed to be checksum-verified.

Before any XML or numerical parsing, the adapter requires exact workbook sizes
and hashes, and verifies the selected member's compressed/uncompressed sizes,
hashes, CRC and complete single deflate stream. It then checks:

- Selected workbook sheets, headers, exact clinical columns and cell addresses;
  formulas in used cells, external relationships and unsafe XML are rejected.
- All clinical measurement/sample/patient relationships, exclusions and complete
  replicate groups, with explicit nonpatient rows kept separate.
- The ordered 64-feature panel and its canonical checksum, exact published
  membership, matrix header checksum, 8,800 rows and 178 columns.
- Unique exact symbols, complete measurement columns and strict decimal finite
  values for every selected measurement. No imputation or transformation is added.

Only column A of discovery-score rows is interpreted as membership; published
prediction values are not decoded or used. The selected worksheet XML is still
read to locate those cells. Nonfinite values in excluded measurements can remain
missing; they cannot enter a selected sample's average. Nonpanel values and
nonpatient matrix columns do not enter the payload.

The [R bridge](../R/asma_source.R) validates the in-memory payload, preserves
identities and feature order, and calls the previously tested `assemble_input()`.
A bounded JSON stdin pipe carries fixed-panel binary64 values and required labels;
no payload file, command argument or Docker log is used. This transfer does not
change the scientific protocol. Numeric test tolerances cover floating-point
serialization and independent formula evaluation only; exact identity/label
checks and the scientific AUROC comparison rule remain unchanged.

## Executed validation

The [fixture generator](../tests/source_adapter_fixture.py) creates artificial
XLSX workbooks and a compressed matrix entirely in memory. It matches the source
geometry, including 231 clinical rows (168 biological and 63 explicit nonpatient
rows), five triplicate groups, 158 sample/subject identities and 135 selected
subjects. It reverses matrix-feature, measurement and membership orders, includes
excluded missing values, and puts deliberately uninterpretable formulas in unused
prediction cells. No study identities, symbols or measurements are included.

The [execution record](../registries/pilot-001-source-adapter-validation.json)
records the complete path from these bytes through Python parsing, private stdin
transfer, R assembly and the actual three model packages. All **18 R bridge
assertions** passed. An independent formula verified all 135 × 64 assembled values,
with exact identity and outcome checks. One full fivefold repetition produced
**405 model predictions, 135 ensemble predictions and 135 final scores**, with
complete coverage and agreement between both AUROC calculations. Artificial
scores and AUROC values are not retained or compared with the paper.

All **138 Python tests** passed, including 19 adapter/acquisition tests, 12
execution-probe tests, four runner-boundary tests and nine runtime-builder tests.
Acquisition tests mock every network dependency. The existing [100-repeat synthetic result](pilot-001-synthetic-validation.md)
remains separate and unchanged. An independent review of
[PR #12](https://github.com/Foundation-0/project-asma/pull/12) (2026-10-25, at
commit `ef1f522`) approved it with no blocking issues; its non-blocking items are
addressed in the addition below. This establishes source-format behavior on fixtures;
compatibility with the actual pinned bytes and current remote availability have
not been tested by this adapter.

The execution record preserves 25 implementation/runtime/protocol hashes and
observed Python/Expat/zlib versions. It predates the 2026-10-25 changes to
`R/asma_core.R`, which added the
[amendment 1](../protocols/pilot-001-reconstruction-amendment-1.md) output, and to
the runner's hash list. The fixture must be rerun in the pinned image before any
research run. A separate [combined runtime record](../registries/pilot-001-source-adapter-runtime.json)
identifies the tested image. It extends the previously validated R image with
CPython 3.12.14 from a hash-pinned official source archive and exact Ubuntu
OpenSSL/zlib development packages matching the existing runtime libraries.
Compilation has networking disabled; the existing R packages are preserved.
[Source and notice pins](../runtime/source-adapter-python.json) document the
inputs. Required standard-library modules pass build checks; unused optional
extension modules are listed as unavailable in the runtime record. No pip or
third-party Python packages are installed, and the image is not redistributed.

The builder prints only the two image IDs and its scope. No committed tool emits
the runtime record's other fields, and the commands that produced them are not
committed. Those fields include the `environment` block (with `compiler` and
`missing_optional_extension_modules`), `r_package_versions` and
`base_r_inventory_unchanged`. The validation record's `transport` block is
written as constants by the [worker](../tools/check_source_adapter.py). It
restates how the runner starts the container; it is not an observation. The probe
observes the container's network and log driver separately.

The outer launcher handles only software identity and aggregate output. A Python
worker runs with `-I -B` inside the container, generates/parses fixtures and starts
R through an internal stdin pipe. User-site initialization and bytecode writes
are disabled. Parsing, private transfer and fitting now share the same bounded
container; no fixture payload passes through the outer launcher.

**Addition, 2026-10-25 (after the execution records above).** These changes
address the non-blocking items of the PR #12 review. The records above predate
them and must be regenerated in the pinned image.

- **Direct tests for four checks.** New tests reject each of these:
  - a duplicated matrix symbol while every panel symbol is present;
  - a swapped panel order;
  - a biological measurement with no matrix column;
  - a replicate group of two.

  Removing any of these checks makes its test fail.
- **No file or URL loading in R.** The bridge decodes with `jsonlite::parse_json`.
  `fromJSON` reads a short non-JSON string as a file path or URL. A new bridge
  assertion, giving 19, passes the path of an existing file holding a valid
  abstract payload and requires rejection. That assertion fails with `fromJSON`.
- **No exception context.** `SourceAdapterError` is raised after the handler
  ends, so neither `__cause__` nor `__context__` holds the original exception.
- **Aggregate failure category.** Each failure carries one fixed `category`
  naming the stage that failed. The message is unchanged, and no category carries
  row data, symbols or values. The rejection rules are unchanged, including
  rejecting any `..` relationship target and requiring gap-free row numbers.
  The category makes such a failure diagnosable in a real-file check. The
  fixture worker does not print it.

| Category | Stage that failed |
| --- | --- |
| `contract` | Fixture-contract bounds (reachable only through the fixture seam) |
| `source_bytes` | Size, hash, MD5, deflate stream, CRC or uncompressed hash of the pinned bytes |
| `workbook` | Workbook container, relationships or sheet list |
| `clinical` | Clinical sheet content, labels, replicate geometry, joins or counts |
| `panel_membership` | Panel list, panel hash or published-score membership |
| `matrix` | Matrix header, rows, symbols, label coverage or panel coverage |
| `matrix_value` | A panel value fails the strict decimal rule, or a selected value is missing or non-finite |
| `acquisition` | Range fetch, member length, directory recheck or HTTP response (acquisition only) |

## Observed execution conditions

The [technical probe](../tools/probe_execution_conditions.py) reads actual kernel
and Docker state, rather than accepting invocation flags alone. Its
[aggregate record](../registries/pilot-001-execution-conditions.json) reports
**40/40 checks passed** for the combined runtime:

- Read-only root and checkout, owner UID, all capabilities dropped and no new
  privileges; only loopback interfaces and no IPv4 routes.
- Zero core-dump limits; 8 GiB memory, zero container swap, two CPUs and 256 tasks.
- A 256 MiB `tmpfs` with `noexec,nosuid`, R temporary/cache destinations there,
  and successful creation/removal of an artificial temporary marker.
- R startup, save/restore and history controls; Docker's log driver set to `none`.
- Python 3.12.14 and isolated/no-user-site/no-bytecode startup, with matching
  cgroup, mount namespace and network namespace for the Python and R processes.

The outer executor exposes no active swap devices, but its parent swap ceiling
is unbounded. That observation does not certify provider snapshots, monitoring,
erasure, unseen ancestor limits or future host configuration. The managed
environment tool reports current connectivity and enforced HTTP policy; it
exposes no processing region, governing hosting contract or retention evidence.
Only this allowlisted observation is retained, without account or environment IDs.
The probe does not emit it: `managed_environment_observation` was added to the
record separately. It reports the outer machine's network policy mode as
`unrestricted`. The container runs with networking disabled, but the machine that
runs it has no network restriction.

| Execution condition | Disposition |
| --- | --- |
| Combined runtime technical controls | Observed PASS on this run; rerun the probe on the actual execution host |
| Python parsing, private transfer and R fitting | Tested together in the pinned container; repeat checks on the actual research host, on study values only after the owner's sign-off in Gate 0 |
| Live acquisition | Implemented and mock-tested; network access, CA trust and data handling on the actual host still require verification, and the owner's sign-off in Gate 0, before study bytes are acquired |
| Actual processing and operator research location | UNKNOWN; requires evidence of the actual research and processing setting |
| Actual host/product terms and retention | UNKNOWN; generic cloud connectivity is insufficient evidence |
| Applicable institutional, funding, contractual and privacy obligations | UNKNOWN; no affiliation, approval or exemption is inferred |
| Selected use and legal route | Independent noncommercial scope remains selected; the Canadian research-use assessment remains conditional on the actual governing context |
| External scientific review | Pending; outreach remains on hold and no reviewer has been recruited |

The Canadian execution plan is a project choice, not a universal legal
requirement established here. A different actual execution setting needs its own
applicability assessment. No new blanket author-license or institutional-review
requirement has been imposed by this software step.

## Commands and continuation

With the existing synthetic R image available, build the combined image and run
from the repository root:

```sh
python3 tools/build_source_adapter_runtime.py
python3 tools/run_source_adapter_fixture.py
python3 tools/probe_execution_conditions.py
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

The fixture and probe CLIs accept no research path, URL or clearance override.
The fixture runner generates all its inputs. The probe writes only an artificial temporary
marker and makes no external network request. See the earlier
[runtime build instructions](pilot-001-synthetic-validation.md#commands) if the
base image is absent. The builder checks its exact identity and pins the new
Python/header inputs. A rebuilt image has its own identity and must be recorded
and tested rather than silently substituted for the executed image pin. Preserve
historical records when recording and pinning a newly validated replacement.

The next step is to choose an actual available execution setting, record its
research location and applicable obligations, inspect the relevant account/host
terms, and verify the tested combined runtime on that host. Once those facts
support the selected use basis, live acquisition of study files and a bounded
real-source input check can establish parser compatibility before fitting. These
steps, and any fitting on study values, need the owner's sign-off in Gate 0 of the [roadmap](roadmap.md): a dated
attestation of the execution context and a new explicit instruction. No researcher contact
is required merely to finish these technical and contextual checks. The prior
supplied-score discrepancy and frozen scientific methods remain unchanged.
