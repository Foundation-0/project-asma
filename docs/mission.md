# Purpose and measures of success

Project Asma honours Asma Ansari by working toward less suffering and loss from
ovarian cancer. The workspace is **open-ended**: any rigorous, permitted
contribution to ovarian cancer research may fit — reproductions, open-data
analyses, methods, curated resources, and well-documented negative results —
provided it follows the guardrails below. Its contribution should be trustworthy
evidence that helps researchers answer consequential questions and, with
appropriate validation, helps patients, families and clinical teams understand
their options.

The project needs to earn that usefulness. A working model, a high AUROC, a
website or a completed software test does not establish benefit to patients.
This repository provides **no** individual diagnosis, treatment recommendation,
or clinical decision service. Use only **public, de-identified or open-licensed**
inputs; respect licence terms; do not redistribute restricted source tables;
label claims (**PROVEN / VERIFIED / KNOWN / CONJECTURE**); ship **one pull
request per executed result**; and obtain **owner gates** before live acquisition
of study files, real-source input checks, or fitting on study values (see
[roadmap](roadmap.md) Gate 0).

## What the work should serve

- **Understand treatment failure.** Investigate clearly defined questions about
  response, progression and resistance, keeping initial treatment failure
  separate from resistance that develops later.
- **Make evidence understandable.** Explain what a result establishes, which
  population it applies to, and what remains uncertain. Distinguish clinical
  evidence from exploratory findings, testimonials and commercial claims.
- **Keep daily life in view.** Future questions should consider symptoms,
  function, quality of life and the burden of navigating care alongside tumour
  measurements. These outcomes require their own evidence and evaluation.

These are project priorities, not claims that the current research delivers
these outcomes.

## One active track: Pilot 001 (unchanged endpoint)

[Pilot 001](../protocols/pilot-001.md) remains the first **bounded protocol** in
this repository. It is designed to reproduce and stress-test a published protein
signature for **primary platinum-refractory high-grade serous ovarian cancer**.
Its endpoint, gates, tolerance, and data-use rules are **not loosened** here.
Its immediate value is to establish which parts of a published result can be
verified, where provenance fails, and whether an independent evaluation is
possible.

Pilot 001 is **one track** toward the broader mission. It does not answer
questions about acquired platinum resistance, recurrence monitoring, early
detection, treatment selection or survival. Neither the pilot population nor its
endpoint should be assigned to an individual from a personal account of illness.
Other directions start as protocol proposals — see [candidate directions](directions.md).

A reproducible discrepancy or a well-supported decision to stop is a useful
result. Agreement must never be obtained by changing the target, cohort or
tolerance after seeing the answer. The existing
[score discrepancy](pilot-001-score-verification-result.md) and
[validation-capacity limit](pilot-001-validation-capacity.md) remain findings to
explain, not problems to tune away.

## What counts as progress

| Deliverable | Evidence needed to call it complete |
| --- | --- |
| Reliable research software | Pinned runtime and code hashes; passing unit and source-format fixture checks; a recorded execution-condition probe on the intended host. Artificial-data results remain labelled as such. |
| An interpretable Pilot 001 result | Fixed protocol, permitted inputs and execution context, commands, aggregate result or failure reason, and an explanation of agreement or discrepancy. Independent reconstruction must remain distinct from reproduction of the authors' procedure. |
| An independent evaluation | Documented patient separation and preprocessing provenance, a fixed endpoint, a threshold fixed independently of test outcomes, appropriate comparators and uncertainty, and enough independent observations for the stated claim. |
| A justified next research question | A defined population, decision and outcome; primary evidence; feasible **open-tier** data access; a comparison method; and a stop rule. Record why the answer would matter and what would change if it were negative. Controlled-access cohorts require a DAR and an owner decision, not silent planning. |
| An open-data analysis or resource | Pinned public inputs, licence review, re-runnable commands, aggregate outputs only in Git, claim labels, and limitations stated without clinical guidance. |
| Benefit beyond research | A separate prospectively defined evaluation of the intended use and patient or caregiver outcomes, with appropriate clinical review. No current result meets this milestone. |

The [roadmap](roadmap.md) is the execution sequence and decision record. Keep
experimental work focused on a bounded question. Evidence reviews and software
preparation for candidate questions may proceed in parallel. Software checks
may proceed independently of author replies; they do not supply missing
scientific evidence or execution authorization.

## Choosing the next question

Use the ranked [candidate directions](directions.md) as a starting shortlist.
At each feasibility decision, compare at least one new open-data direction with
continuing Pilot 001 and with work that makes existing evidence easier to
understand. Recurrent disease, acquired resistance, care coordination, and
symptom or function outcomes remain possibilities to assess — not adopted studies
or a commitment to build a patient application.

Prefer the smallest study that can resolve an important uncertainty with
traceable evidence and feasible, permitted inputs. Reject a direction if its
endpoint is ambiguous, its data cannot support the intended claim, or its likely
answer would not inform a meaningful next decision. A new endpoint needs a **new
protocol pull request** and the same **owner gate** pattern as Gate 0 in the
[roadmap](roadmap.md). The [research-question template](../templates/research-question.md)
remains the starting record.

## Private context and public work

Personal correspondence can explain why this work matters. It is not a research
cohort, a source of model labels, or evidence of treatment efficacy or the cause
of an individual outcome. Permission to read it for orientation does not imply
permission to publish it or use it for model training.

Keep personal messages, attachments, medical histories, contact details,
mailbox links and identifiers out of this public repository, its pull requests,
issues and site. Publish general research requirements and independently
supported scientific findings under the existing
[data rules](reproducibility-and-data.md). The public tribute does not authorize
disclosure of additional personal details.
