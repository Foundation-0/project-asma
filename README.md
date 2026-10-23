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

No full PDC abundance matrix was downloaded, no author analysis code was executed,
and no model was trained or performance result reproduced. Scientific review and
resolution of the remaining input/method gaps are still required. Some source
routes were inaccessible or incomplete; the report records those limits.

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

The optional network commands `python3 tools/audit_pdc_metadata.py` and
`python3 tools/audit_published_cohorts.py` rerun the public catalog comparison
and pinned supplemental membership checks in memory. They print aggregate JSON
only and are separate from the offline checks. Neither establishes independence
from upstream preprocessing or reproduces model performance.

## Decisions still needed

The owner must choose repository licensing; **no license grant is supplied**.
Third-party code and data retain their own terms. Before ingestion or execution,
review access and reuse terms, pin corrected supplemental materials, resolve
patient overlap, and assess computational requirements. A gynecologic oncologist and a
proteomics/biostatistics collaborator are needed; none is recruited by this
scaffold. See the [roadmap](docs/roadmap.md) for feasibility gates.
