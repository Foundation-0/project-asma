# Project Asma

Project Asma is a small research project on ovarian cancer. It asks one
question: can a published result be reproduced? A 2023 study reported a set of
64 proteins that marks the most treatment-resistant form of high-grade serous
ovarian cancer (HGSOC). This project plans to rebuild that result from the
public data, check each step, and report what holds and what does not.

**Website:** [foundation-0.github.io/project-asma](https://foundation-0.github.io/project-asma/)

**Research only.** This repository is not clinical advice, a diagnostic
service, or clinical decision support. Reproduction does not establish a new
classifier, clinical validity, or improved patient outcomes.

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

The scaffold on this branch is dated **2026-10-22**. Primary literature,
official approval notices, author code, and PDC study metadata were inspected.
Some source pages were inaccessible; the registry records the access limits.
No research data were downloaded, no author analysis code was executed, no
model was trained, and no scientific result has been reproduced here. Local
scaffold validation is separate from scientific validation.

Follow-up work sits in open pull requests, under review at the time of
writing:

- The feasibility audit and the patient-linkage audit recover the 64-protein
  panel and rebuild the published score cohorts (135 discovery, 61 frozen,
  20 FFPE). They also record a membership discrepancy: six patient keys in
  the frozen sheet labelled non-overlapping also occur in the discovery
  score set.
- A check of the published discovery scores gives AUROC 0.80885, against the
  printed 0.83. The check is arithmetic on the released scores. It does not
  establish an error in the paper, because the released scores have not been
  shown to be the exact predictions behind the printed value.
- A later audit recovers the link between the author-released discovery
  matrix and the clinical records: its header matches all 168
  response-labelled measurement rows and all 135 published score keys, and
  all 64 panel proteins occur exactly once among its 8,800 feature rows.

The scope starts with HGSOC. Primary refractory disease (failure of initial
therapy) must be distinguished from later platinum-resistant recurrence.
Other histotypes require their own questions, labels, and study designs.

## Check the scaffold

Python 3.10+ and its standard library are sufficient; no package installation
or network access is needed:

```sh
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

The validator checks registry structure, cross-references, and local Markdown
file/heading links. It does not check external availability, scientific truth,
dataset contents, or access rights. See the [registry guide](registries/README.md).

## Decisions still needed

The owner must choose repository licensing; **no license grant is supplied**.
Third-party code and data retain their own terms. Before ingestion or
execution, review access and reuse terms, pin corrected supplemental
materials, resolve patient overlap, and assess computational requirements.
A gynecologic oncologist and a proteomics/biostatistics collaborator are
needed; none is recruited by this scaffold. See the [roadmap](docs/roadmap.md)
for feasibility gates.
