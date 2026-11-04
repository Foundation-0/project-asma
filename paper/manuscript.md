# Reproducing and stress-testing a primary platinum-refractory HGSOC protein signature

**Status:** manuscript scaffold — not submitted, not peer reviewed.  
**Version:** 0.1 (2026-11-04).  
**Scope:** research reproduction and robustness only. Not clinical decision support.

## Abstract

*(Placeholder — write after Pilot 001 reaches a declared milestone in the
[roadmap](../docs/roadmap.md).)*

## Question

Can an independent group reproduce one reported discovery cross-validation result
(Figure 3D) from Chowdhury et al. (Cell, 2023) for **primary platinum-refractory
high-grade serous ovarian cancer (HGSOC)**, and characterize what can be verified
when inputs, patient overlap, and author execution remain partially unresolved?

Primary refractory disease (failure of initial platinum therapy) is not acquired
platinum-resistant recurrence. Other histotypes require separate endpoints.

## Background (known prior art)

Chowdhury et al. report a 64-protein panel and discovery fivefold cross-validated
AUC **0.83** (95% CI 0.77–0.90) for primary refractory versus sensitive HGSOC
([Cell 2023](https://doi.org/10.1016/j.cell.2023.07.004)). Those numbers are
**published reference values**, not results from Project Asma. Supplementary
materials and six PDC studies (**PDC000358**, **PDC000360**, **PDC000362** proteome;
**PDC000357**, **PDC000359**, **PDC000361** phosphoproteome) are registered in
[registries](../registries/) with their reuse terms (see [datasets.json](../registries/datasets.json)).

## Methods (pre-registered)

Methods follow **[Pilot 001](../protocols/pilot-001.md)** (version 0.10, 2026-10-25)
and linked specifications unless a dated amendment says otherwise:

1. **Provenance and patient overlap** — manifest specification (private),
   classification of validation patients as independent, overlapping, or unresolved.
2. **Reproducible environment** — pinned R/Python runtimes; synthetic fixture tests
   before any authorized study-data execution ([reconstruction decisions](../protocols/pilot-001-reconstruction-decisions.md),
   [synthetic validation](../docs/pilot-001-synthetic-validation.md)).
3. **Published-score verification** — fixed arithmetic check of released discovery
   scores against printed AUC ([score verification protocol](../protocols/pilot-001-score-verification.md)).
4. **Independent reconstruction** — discovery-only pipeline written without running
   author scripts ([reconstruction contract](../protocols/pilot-001-independent-reconstruction.md)).
5. **Robustness and validation design** — frozen-cohort comparisons only after
   independence is resolved; validation-capacity limits precomputed from documented counts.

Execution gates, data-use disposition, and stop rules are in the protocol and
[data-use record](../docs/pilot-001-data-use.md). No study abundance matrices,
score rows, or patient identifiers are committed to this repository.

## Results

**Not yet run for this manuscript.** The subsections below are placeholders only.
Do not treat them as completed analyses.

### 3.1 Full model reproduction (Figure 3D)

*Not yet run.* Gate 2 in the [roadmap](../docs/roadmap.md) remains open.

### 3.2 Published discovery-score arithmetic check

One **executed** preliminary check is recorded elsewhere and may be summarized here
when the manuscript is drafted:

- Under the fixed contract in [pilot-001-score-verification-result.md](../docs/pilot-001-score-verification-result.md),
  discovery AUROC **0.8088507878** (exact fraction 3,491 / 4,316 pairs) versus
  the printed reference **0.83**, absolute difference **0.02115**, outside the
  predeclared tolerance **0.02**.
- Registry artifact: [pilot-001-score-verification.json](../registries/pilot-001-score-verification.json).
- This is a **reproduction discrepancy under investigation**, not evidence of an
  error in the original paper, not model regeneration, and not clinical validation.

### 3.3 Independent reconstruction on study data

*Not yet run.* Synthetic and fixture-only software checks are documented in
[docs/pilot-001-synthetic-validation.md](../docs/pilot-001-synthetic-validation.md)
and [docs/pilot-001-source-adapter.md](../docs/pilot-001-source-adapter.md).

### 3.4 Validation cohort performance

*Not yet run.* Design limits from aggregate counts are in
[docs/pilot-001-validation-capacity.md](../docs/pilot-001-validation-capacity.md).

## Discussion

*(Placeholder.)*

## Data and code availability

Public source locators and aggregate registries only; no row-level study data in
the repository. Software is described in the [README](../README.md) and
[CLAIMS.md](../CLAIMS.md).

## Author contributions and AI disclosure

See [CONTRIBUTORS.md](../CONTRIBUTORS.md). This scaffold was extended toward the
Foundation-0 repository standard with AI assistance (see repository PR).

## Competing interests

*(To be completed by human authors before submission.)*

## References

Chowdhury S et al. Proteogenomic analysis of chemo-refractory high-grade serous
ovarian cancer. *Cell* 2023. https://doi.org/10.1016/j.cell.2023.07.004

*(Additional references to match [registries/sources.json](../registries/sources.json)
when the manuscript is drafted.)*
