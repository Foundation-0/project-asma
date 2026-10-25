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
remains separate and unchanged. Independent code review found no blocking issue. This establishes source-format behavior on fixtures;
compatibility with the actual pinned bytes and current remote availability have
not been tested by this adapter.

The execution record preserves 25 implementation/runtime/protocol hashes and
observed Python/Expat/zlib versions. A separate [combined runtime record](../registries/pilot-001-source-adapter-runtime.json)
identifies the tested image. It extends the previously validated R image with
CPython 3.12.14 from a hash-pinned official source archive and exact Ubuntu
OpenSSL/zlib development packages matching the existing runtime libraries.
Compilation has networking disabled; the existing R packages are preserved.
[Source and notice pins](../runtime/source-adapter-python.json) document the
inputs. Required standard-library modules pass build checks; unused optional
extension modules are listed as unavailable in the runtime record. No pip or
third-party Python packages are installed, and the image is not redistributed.

The outer launcher handles only software identity and aggregate output. A Python
worker runs with `-I -B` inside the container, generates/parses fixtures and starts
R through an internal stdin pipe. User-site initialization and bytecode writes
are disabled. Parsing, private transfer and fitting now share the same bounded
container; no fixture payload passes through the outer launcher.

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

| Execution condition | Disposition |
| --- | --- |
| Combined runtime technical controls | Observed PASS on this run; rerun the probe on the actual execution host |
| Python parsing, private transfer and R fitting | Tested together in the pinned container; repeat checks on the actual research host |
| Live acquisition | Implemented and mock-tested; network access, CA trust and data handling on the actual host still require verification before study bytes are acquired |
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
terms, and verify live acquisition plus the tested combined runtime on that host.
Once those facts support the selected use basis, a bounded real-source input
check can establish parser compatibility before fitting. That check needs the
owner's sign-off in Gate 0 of the [roadmap](roadmap.md): a dated attestation of the
execution context and a new explicit instruction. No researcher contact
is required merely to finish these technical and contextual checks. The prior
supplied-score discrepancy and frozen scientific methods remain unchanged.
