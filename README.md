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
| [Roadmap](docs/roadmap.md) | Small milestones and decision gates |
| [Registries](registries/README.md) | Structured sources and candidate data provenance |
| [Reproducibility and data protection](docs/reproducibility-and-data.md) | What may be collected, stored, and published |
| [Contributing](CONTRIBUTING.md) / [agent guidance](AGENTS.md) | Review and evidence standards |
| [Question](templates/research-question.md), [experiment](templates/experiment.md), [manifest](templates/provenance-manifest.md) templates | Reusable working records |

## Current state

This is a draft research scaffold dated **2026-10-22**. Primary literature,
official approval notices, author code, and PDC study metadata were inspected.
Some source pages were inaccessible; the registry records the access limits.
No research data were downloaded, no author analysis code was executed, no model
was trained, and no scientific result has been reproduced here. Local scaffold
validation is separate from scientific validation.

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

## Decisions still needed

The owner must choose repository licensing; **no license grant is supplied**.
Third-party code and data retain their own terms. Before ingestion or execution,
review access and reuse terms, pin corrected supplemental materials, resolve
patient overlap, and assess computational requirements. A gynecologic oncologist and a
proteomics/biostatistics collaborator are needed; none is recruited by this
scaffold. See the [roadmap](docs/roadmap.md) for feasibility gates.
