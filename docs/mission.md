# Purpose and measures of success

Project Asma honours Asma Ansari by working toward less suffering and loss from
ovarian cancer. Its contribution should be trustworthy evidence that helps
researchers answer consequential questions and, with appropriate validation,
helps patients, families and clinical teams understand their options.

The project needs to earn that usefulness. A working model, a high AUROC, a
website or a completed software test does not establish benefit to patients.

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
these outcomes. This repository remains a research workspace; it provides no
individual diagnosis, treatment recommendation or clinical decision service.

## The first contribution

[Pilot 001](../protocols/pilot-001.md) is designed to reproduce and stress-test a
published protein signature for
**primary platinum-refractory high-grade serous ovarian cancer**. Its immediate
value is to establish which parts of a published result can be verified, where
provenance fails, and whether an independent evaluation is possible.

That is one bounded contribution to the mission. It does not answer questions
about acquired platinum resistance, recurrence monitoring, early detection,
treatment selection or survival. Neither the pilot population nor its endpoint
should be assigned to an individual from a personal account of illness.

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
| A justified next research question | A defined population, decision and outcome; primary evidence; feasible data access; a comparison method; and a stop rule. Record why the answer would matter and what would change if it were negative. |
| Benefit beyond research | A separate prospectively defined evaluation of the intended use and patient or caregiver outcomes, with appropriate clinical review. No current result meets this milestone. |

The [roadmap](roadmap.md) is the execution sequence and decision record. Keep
experimental work focused on a bounded question. Evidence reviews and software
preparation for candidate questions may proceed in parallel. Software checks
may proceed independently of author replies; they do not supply missing
scientific evidence or execution authorization.

## Choosing the next question

At the next feasibility decision, compare at least a question about
recurrent disease or acquired resistance with a question about making existing
evidence easier to understand. Care coordination and symptom or function
outcomes are also candidate directions. These are possibilities to assess, not
adopted studies or a commitment to build a patient application.

Prefer the smallest study that can resolve an important uncertainty with
traceable evidence and feasible, permitted inputs. Reject a direction if its
endpoint is ambiguous, its data cannot support the intended claim, or its likely
answer would not inform a meaningful next decision. The current
[research-question template](../templates/research-question.md) provides the
starting record; a new endpoint needs a new protocol.

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
