# Project Asma

A small, evidence-led workspace for ovarian cancer research. The first proposed
contribution is to reproduce and stress-test a published protein signature for
**primary platinum-refractory high-grade serous ovarian cancer (HGSOC)**.

**Research only.** This repository is not clinical advice, a diagnostic service,
or clinical decision support. Reproduction does not establish a new classifier,
clinical validity, or improved patient outcomes.

## Start here

| Read | Purpose |
| --- | --- |
| [Research frontier — 2026-10-22](docs/frontier-2026-10-22.md) | Evidence, open questions, and limits |
| [Pilot protocol](protocols/pilot-001.md) | Proposed reproduction and robustness study |
| [Pilot feasibility audit](docs/pilot-001-feasibility-audit.md) | Source-checked inputs, methods, patient-independence questions, and execution blockers |
| [Input and linkage resolution — 2026-10-23](docs/pilot-001-input-resolution.md) | Executed metadata checks, recovered source locations, and remaining reproduction gaps |
| [Published-score verification specification](protocols/pilot-001-score-verification.md) | Fixed numerical check and recorded execution basis |
| [Discovery-score AUROC result](docs/pilot-001-score-verification-result.md) | Executed preliminary result, comparison failure and remaining provenance limits |
| [Independent progress](docs/pilot-001-independent-progress.md) | Matrix-header diagnostic, score lineage and concrete supplement-legend mismatch |
| [Preprocessing provenance](docs/pilot-001-preprocessing-provenance.md) | Located transformations, replicate-averaging example and unresolved execution history |
| [Public-input reconstruction contract](protocols/pilot-001-independent-reconstruction.md) | Prospective discovery-only requirements and stop rules |
| [Code-audit addendum — 2026-10-24](docs/pilot-001-code-audit-addendum.md) | Static code findings beyond the earlier audit, reconciled with it |
| [Reconstruction decisions](protocols/pilot-001-reconstruction-decisions.md) | Fixed input assembly, folds, model settings, aggregation and runtime target |
| [Synthetic pipeline validation](docs/pilot-001-synthetic-validation.md) | Executed fixture tests, complete model run and pinned runtime |
| [Source adapter and execution conditions](docs/pilot-001-source-adapter.md) | Verified-byte parsing, source-format fixtures and observed runtime controls |
| [Data-use disposition](docs/pilot-001-data-use.md) | Noncommercial research scope, source terms and remaining execution conditions |
| [Roadmap](docs/roadmap.md) | Small milestones and decision gates |
| [Registries](registries/README.md) | Structured sources and candidate data provenance |
| [Reproducibility and data protection](docs/reproducibility-and-data.md) | What may be collected, stored, and published |
| [Contributing](CONTRIBUTING.md) / [agent guidance](AGENTS.md) | Review and evidence standards |
| [Question](templates/research-question.md), [experiment](templates/experiment.md), [manifest](templates/provenance-manifest.md) templates | Reusable working records |

## Current state

The scaffold and static audit were followed by public-source investigation on
**2026-10-23**. PDC metadata and processed-file headers were inspected in memory;
the [resolution report](docs/pilot-001-input-resolution.md) separates measured
catalog overlap from the paper's prediction eligibility and missing analysis
inputs. Public supplemental materials were also inspected transiently. Only
reviewed aggregate results and source provenance are retained here.

The [published-score check](docs/pilot-001-score-verification-result.md) has now
run under the user's explicit instruction: discovery AUROC is **0.80885**
(rounds to **0.81**), versus printed **0.83**, with difference **0.02115** outside
the fixed 0.02 tolerance. Source files and exact joins passed validation; this
is a preliminary supplied-score discrepancy, not evidence of an original-paper
error or completed model reproduction. External scientific review remains pending.

No full PDC abundance matrix was downloaded, no author analysis code was executed,
and no model was trained on study data. Missing input/method provenance still
prevents full reproduction. On 2026-10-25 the owner decided that the
consolidated [source request](templates/pilot-001-source-request.md) is
authorized **as a draft only**: the owner alone decides whether and when to send
it, from their own account. No author message has been posted. Automated
sessions never post or send it, and the earlier automated posting attempts
should not have happened. The owner also confirmed that the recorded data
inspections and synthetic model runs were intended results of autonomous
research. Recruiting collaborators or reviewers remains on hold. Work continues from public sources
and internal checks; unresolved provenance and external-review questions remain
explicit.

A [code-audit addendum](docs/pilot-001-code-audit-addendum.md) (2026-10-24) adds
static findings, mostly beyond the earlier records. These cover which loaded
objects can feed the plotted cross-validation, label orientation and operating
points, the uncoded branches of panel selection, alignment details, and
package-version sensitivity.

Independent investigation recovered an author-released imputed discovery matrix
whose header exactly matches **all 168 response-labelled measurement rows and
all 135 published discovery-score sample keys**. This resolves the naming gap
for that candidate input. A complete-member audit now verifies its ZIP CRC and
finds **all 64 panel symbols exactly once among 8,800 feature rows**. Abundance
fields were discarded after hashing, without numerical analysis. Transformation
into the original model workspaces and later reuse conditions remain unresolved.

The direct PDC header route did not supply patient links. The code's discovery
score lineage is located, but its export to the released scores remains untraced.
A content mismatch also makes the available Figure S3 legend unsuitable for
authoritative figure-panel assignments. The [progress report](docs/pilot-001-independent-progress.md)
records the recovered input, these limitations and the reconstruction path.

On **2026-10-25**, the [decision record](protocols/pilot-001-reconstruction-decisions.md)
specifies a discovery-only reconstruction with explicit replicate averaging,
patient-stratified folds, seeds, model parameters and complete prediction checks.
Direct R/package releases are hash-pinned; the subsequent
[synthetic validation](docs/pilot-001-synthetic-validation.md) records the installed
dependency inventory and execution tests. The selected phase is independent
noncommercial research with no persistent patient-level files and no reuse of author analysis code. The
[data-use assessment](docs/pilot-001-data-use.md) separates those choices from
a conditional Canadian research-use basis and its remaining execution-context
checks. The current workspace is not yet verified for that research run.
The independently written pipeline has now been tested on artificial fixtures,
including all 100 repetitions using the three pinned model packages. No study-data
model fit or new clinical result is claimed. The frozen decision record remains
unchanged; its prospective runtime status is superseded by the validation report.

The [source adapter](docs/pilot-001-source-adapter.md) now validates pinned source
bytes, exact clinical membership and selected values before R assembly. Generated
XLSX/matrix fixtures passed the complete adapter-to-model path. A separate runtime
probe passed 40 technical checks. Python parsing, private transfer and R fitting
now share a pinned container with Docker logging disabled. Live acquisition,
processing jurisdiction and hosting/use conditions remain unverified.
No study sources were ingested by the adapter. Those remaining conditions must
cover acquisition, parsing, transfer and fitting before research execution.
Live acquisition of study files, a real-source input check and fitting each need
the owner's sign-off in Gate 0 of the [roadmap](docs/roadmap.md).

The scope starts with HGSOC. Primary refractory disease (failure of initial
therapy) must be distinguished from later platinum-resistant recurrence. Other
histotypes require their own questions, labels, and study designs.

## Check the scaffold

Python 3.10+ and its standard library are sufficient; no package installation or
network access is needed:

```sh
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

The validator checks registry structure, cross-references, and local Markdown
file/heading links. It does not check external availability, scientific truth,
dataset contents, or access rights. See the [registry guide](registries/README.md).
With R and jsonlite, `Rscript --vanilla tools/check_panel_name_tokens.R` checks
the token expectations of the panel-name tests against R's own `make.names`. It
is offline, prints only counts and is not part of the Python suite.

The network commands `python3 tools/audit_pdc_metadata.py` and
`python3 tools/audit_published_cohorts.py` rerun the public catalog comparison
and pinned supplemental membership checks in memory. They print aggregate JSON
only and are separate from the offline checks. Neither establishes independence
from upstream preprocessing or reproduces model performance.
`python3 tools/audit_matrix_headers.py` reruns the bounded matrix-header to
clinical-label diagnostic; it reads no abundance rows and emits aggregates only.
`python3 tools/audit_author_archive.py` verifies the recovered discovery input's
header linkage using bounded ZIP ranges and exact clinical/score-key joins.
`python3 tools/audit_author_features.py` checks the complete selected member
in memory for CRC, hashes and exact panel coverage under the documented bounded
inspection scope; it emits no source rows or abundance values.
`python3 tools/audit_panel_names.py` counts pinned panel symbols that R's
`make.names` would alter. It downloads the hash-pinned MMC4 workbook into memory,
parses only the panel worksheet (and the workbook's shared-string table) and
prints counts, no symbols.
`python3 tools/audit_validation_panel_coverage.py` counts exact 64-panel
coverage in the pinned MMC1 per-cohort protein association lists in memory and
prints counts and fingerprints only.
These audits, like `python3 tools/verify_published_auc.py`, read patient-level
clinical or linkage metadata, published scores or the full matrix member in
memory. They follow the bounded-inspection rule in the
[agent guidance](AGENTS.md): in memory, aggregates only, recording what was read
and why. They are not routine offline checks.

To build and test the isolated R pipeline on abstract fixtures, follow the
[synthetic validation commands](docs/pilot-001-synthetic-validation.md#commands).
The synthetic runner has no dataset path or URL option. The
[source-adapter and runtime-probe commands](docs/pilot-001-source-adapter.md#commands-and-continuation)
also operate without research inputs.

## Decisions still needed

The owner must choose repository licensing; **no license grant is supplied**.
Third-party code and data retain their own terms. Before ingestion or execution,
review access and reuse terms, pin corrected supplemental materials, resolve
patient overlap, and assess computational requirements. Clinical interpretation
and later validation will require domain review; recruiting reviewers is deferred.
Public-source investigation can continue independently under the
[roadmap](docs/roadmap.md) and [reconstruction contract](protocols/pilot-001-independent-reconstruction.md),
within the owner conditions in the [agent guidance](AGENTS.md).
