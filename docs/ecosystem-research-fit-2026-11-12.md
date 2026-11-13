# From plausible explanations to discriminating tests

**12 November 2026, America/Chicago (inspection continued 13 November UTC).**
Static assessment of current public code, reports and review state. No upstream
solver, Lean proof, study-source analysis or patient model was executed. This
record preserves a research recommendation, not adoption or a new biological
finding. Source observations are **KNOWN (K38)**; proposed transfers and their
expected value are **CONJECTURE (C24)**.

## Recommendation

Use the ecosystem's progress to make **one unresolved research claim easier to
challenge**. The strongest transfer combines a broad search for candidate
explanations with a small checker that independently reconstructs what each
candidate establishes. It should preserve ambiguous and negative outcomes and
identify an observation that could distinguish explanations.

For the anti-Yo frontier, the most concrete biological question is now:
**does the located breast-cell-line spectrum distinguish the proposed CDR2L
peptide from credible alternative assignments?** Pending source work has moved
beyond catalog annotations. For a computational first increment, use existing
synthetic examples to test a search/checker contract before considering any
source-spectrum analysis. A second research direction asks which additional
measurements can distinguish the compartment or surgery-response models that
already agree on existing observations.

This is a proposal to improve falsifiability and experiment selection. It does
not establish a novel mechanism, a new treatment, or a complete virtual human.
The present inspection is not a systematic novelty review.

## What is already present

| Repository and inspected revision | Established scope | Consequence for this assessment |
| --- | --- | --- |
| [Project Asma, `39285f3`](https://github.com/Foundation-0/project-asma/tree/39285f33aea735501abeab47e409ead2205efbab) | Evidence graph; source audits; exact synthetic compartment and treatment-order examples; an unexecuted reconstruction and exploratory subset plan. Latest main includes #74's public convergence-note audit and #76's runtime-build fix. | Extend the existing examples and evidence checks. The named molecular/disease simulator endpoints in the convergence notes are proposals, not implemented models. |
| [Virtual Human, `6b10b45`](https://github.com/Foundation-0/virtual-human/tree/6b10b458704e36cd592552ab8165d55ce5fe64ec) | Reaction/intervention engine, exact conservation checks, restricted SBML importer and optional scalar evidence bindings. | These are already merged capabilities. Asma's current adoption is a graph core and synthetic bridge, not the whole molecular/PBPK stack. |
| [Soko, `27406dd`](https://github.com/ahrazzle/soko/tree/27406dd2c5599c91fa2b63e8f577861a78c22ffb) | Search proposals, rechecked exclusion certificates, exact bounds and provenance-aware room triage. | Borrow patterns through an independent, small implementation. Puzzle transitions are deterministic and completely specified; biology is not. |
| [Foundation-0/proven-commons, `903c185`](https://github.com/Foundation-0/proven-commons/tree/903c1858be856776de21675cf5c4e26fb9eebcdf) | An anthology of pinned upstream Lean libraries, builds and an axiom audit. | Distinguish the anthology from the **Proven-Commons organization** and inspect current upstream versions. Its main snapshot is older than the libraries below. |
| [Proven-Commons/mission, `7b22e54`](https://github.com/Proven-Commons/mission/tree/7b22e542f0db0f3013ab1439cf5d1947676a5083) | Verification standard and adversarial claim/statement reviews. | A proof needs a separately reviewed statement that actually captures the intended claim. |
| [finite-state-proofs, `9eeb3da`](https://github.com/Foundation-0/finite-state-proofs/tree/9eeb3da2cdd6ba6b100ac24d23b32c369c0db8ec) | Exact certificates for eleven recurrences, a written model argument and a separately written checker using a different representation. Human sign-off remains pending. | A model argument plus a finite algebraic certificate can establish more than a long list of successful examples. It is not a Lean proof or a biological model. |
| [formal-claims-audit, `bacf059`](https://github.com/Foundation-0/formal-claims-audit/tree/bacf05953c10bf5105fa1209a127392d395e2f92) | Verdict schema and structural validator; no completed research verdicts on inspected main. | Reuse its explicit claim/statement/evidence separation as a review pattern. A valid verdict file is not a verified theorem comparison. |

The [existing evidence graph](evidence-graph-result-2026-11-05.md) already blocks
unsupported cross-assay conjunctions and separates recognition from injury. Its
fixtures check encoded expectations, not independently measured scientific
accuracy. The [compartment examples](compartment-identifiability.md) and
[treatment-sequence result](research/rosen-treatment-sequence-assumptions.md)
already establish synthetic nonidentifiability examples. Repeating those results
under a new tool name would add little.

Virtual Human's [evidence bindings](https://github.com/Foundation-0/virtual-human/blob/6b10b458704e36cd592552ab8165d55ce5fe64ec/docs/evidence_bindings.md)
check declared quantity, unit, basis and context and refuse missing, conflicting
or conjectural inputs. They preserve uncertainty metadata **without propagating
it**. They cannot supply the missing ovarian growth, surgical-retention or drug
kinetic parameters, detect every omitted assumption, or establish applicability.
The SBML importer does not check units. These limits survive composition.

## What transfers, with what evidence

### 1. Search widely; accept narrowly

Soko's [refinement checker](https://github.com/ahrazzle/soko/blob/27406dd2c5599c91fa2b63e8f577861a78c22ffb/experiments/causal_solver/refinement.py#L326)
reconstructs a bounded problem, checks source/mechanics metadata and rechecks the
candidate certificate. [Installing an exclusion](https://github.com/ahrazzle/soko/blob/27406dd2c5599c91fa2b63e8f577861a78c22ffb/experiments/causal_solver/refinement.py#L388)
ignores a supplied `verified` label. An unknown result, mismatched model or
invalid certificate leaves the candidate space unchanged. A fresh solver is
still a trusted solver; rebuilding the same encoding does not eliminate a
shared modeling mistake.

Its separate [transport checker](https://github.com/ahrazzle/soko/blob/27406dd2c5599c91fa2b63e8f577861a78c22ffb/experiments/transport_relaxation/cut_certificate.py)
reconstructs network boundaries, including disabled edges another assignment
could enable. [Adversarial tests](https://github.com/ahrazzle/soko/blob/27406dd2c5599c91fa2b63e8f577861a78c22ffb/tests/test_global_cut_certificates.py)
check corrupted evidence and preservation of feasible tiny assignments.

**Proposed Asma use:** accept a candidate peptide comparison or synthetic
intervention trace only after reconstructing its declared inputs and rules.
A counterexample should eliminate only the assumptions it actually contradicts.
Store the model revision, evidence scope, checker revision and remaining
alternatives. A payload hash identifies bytes; it does not establish truth.

This distinction is already relevant to open Asma
[#67](https://github.com/Foundation-0/project-asma/pull/67): its source replay
repairs enforce precursor/charge agreement, require locator fields and separate
producing-code hashes from later checker hashes. Build on that work.

### 2. Find an observation on which explanations disagree

**Proposed research ingress:** take a declared, bounded set of competing models
that fit the same existing observations. Search a small menu of additional
measurements or perturbations for a difference in their predictions. A checker
recomputes those predictions and their allowed uncertainty ranges. If all
ranges overlap, report that this model set and observation menu did not yield
a discriminator; do not conclude the mechanisms are indistinguishable in life.

Two starting fixtures already exist here:

- Selection/retention and conversion can yield the same compartment contrast.
  Ask which temporal or state-transition observation breaks that equivalence
  under the explicit fixture assumptions.
- Two surgery-response maps can agree in the observed treatment order and differ
  in the other. Ask which pre/postoperative burden and composition observations
  distinguish the maps, before interpreting any order preference.

These are examples of partial identification and experimental design, established
method classes. The potential contribution is a useful, checked comparison for
this research question. It is not a claim that the method itself is new.
Unknown rates remain unknown; no arbitrary parameter fills an evidence gap.
Stochastic or partially observed models need their own semantics. A deterministic
puzzle exclusion cannot be carried over without a justification.

### 3. Review the statement as carefully as the proof

The [tar audit](https://github.com/Proven-Commons/mission/blob/7b22e542f0db0f3013ab1439cf5d1947676a5083/reviews/tar/2026-10-24-bar-audit.md)
is a concrete lesson. Standard-axiom proofs passed, but the historical theorem's
path-component predicate did not forbid an embedded slash. The theorem was
weaker than the claimed destination confinement. The audit did **not** show that
the implementation actually escaped the destination; its complaint concerned
the statement and the unproved connection to the implementation.

In Asma, the analogous gaps are “this sequence occurs in this reference” versus
“this spectrum identifies this protein,” and “this receptor is activated” versus
“this mechanism causes neural injury.” A theorem or successful checker about
the former cannot supply the latter.

**Proposed small review record:** exact public claim; independently restated
meaning; source/version; assumptions and applicability; checked mathematical or
computational statement; what remains outside it; reviewer and unresolved
obligations. Use three existing claims before creating a general framework.
The [formal-claims validator](https://github.com/Foundation-0/formal-claims-audit/blob/bacf05953c10bf5105fa1209a127392d395e2f92/scripts/check_verdicts.py)
checks structure and types, not Lean execution, statement equivalence or source
truth. A later Lean rule about a joint-observation claim being witnessed by one
complete record would verify that matching rule, not the truth of its records.

### 4. Keep bounds and negative results attached to their domain

In [finite-state-proofs](https://github.com/Foundation-0/finite-state-proofs/blob/9eeb3da2cdd6ba6b100ac24d23b32c369c0db8ec/PROOF.md),
a written correspondence with a transfer matrix and an exact residual reaching
a zero vector establish specified recurrences for every later height. The
finite certificate has force because the model argument connects it to the
infinite claim. It does not justify extrapolating arbitrary biological samples.

For Asma, distinguish:

- a counterexample under specified assumptions;
- no witness found within a compute budget;
- an exhaustive result over an explicitly enumerated finite domain;
- a theorem over a mathematical model, with its assumptions stated;
- an empirical result in a specified population and assay context.

Soko's [scoped-invariant tests](https://github.com/ahrazzle/soko/blob/27406dd2c5599c91fa2b63e8f577861a78c22ffb/tests/test_invariant_scope.py)
and [exact cost-partition checks](https://github.com/ahrazzle/soko/blob/27406dd2c5599c91fa2b63e8f577861a78c22ffb/soko_mcp/formal_kernel.py#L1390)
illustrate the boundary. Do not sum purportedly independent intervention costs
when one action affects several pathways. In the inspected
[portfolio adapter](https://github.com/ahrazzle/soko/blob/27406dd2c5599c91fa2b63e8f577861a78c22ffb/experiments/portfolio/triage.py),
imported bounds remain reported claims. The generic
[`triage_formal_portfolio`](https://github.com/ahrazzle/soko/blob/27406dd2c5599c91fa2b63e8f577861a78c22ffb/soko_mcp/formal_kernel.py#L1963)
still trusts supplied floors and labels equality optimal. That shortcut is
unsuitable for research evidence. Biological importance and measurement
feasibility also belong in prioritization; a numerical gap is not expected value.

## A bounded next increment

**Recommendation: pattern only now; propose a small synthetic prototype.**
No solver dependency or proof toolchain is needed for the first comparison.
This proposal is not an execution protocol for study data.

| Item | Proposed contract |
| --- | --- |
| Decision | Can checked exclusions or a discriminator witness add useful error detection beyond the existing exact examples and plain evidence table? |
| Inputs | Existing artificial Asma fixtures; explicit finite model/action/observation sets. No patient, spectrum or new study inputs. |
| Method | One independent standard-library enumerator plus a separately written checker. Search may propose exclusions or distinguishing observations; the checker reconstructs the model's result. |
| Budget | One engineer-day for the first fixture, at most three actions and fewer than 1,000 enumerated states, under five minutes test compute. This is a planning cap, not measured effort. |
| Acceptance | Preserve a known valid sequence; reject a planted invalid sequence, forged/rehashed result and revision mismatch; retain all candidates after timeout; compare every accepted exclusion against exhaustive enumeration. Include a shared-effect action that invalidates naïve additive bounds. For an observation witness, independently reproduce separation under the declared noise intervals. Report which faults the existing checks already catch and which additional fault or discriminator this prototype contributes. |
| Meaning of success | Demonstrated error detection or a checked discriminator within the artificial domain. No biological efficacy, universal identifiability or novelty claim. |
| Stop | A sound state/transition model cannot be stated; a valid candidate is excluded; required rates are invented; existing simple tables/checks already do the job; or scope expands beyond the cap. |
| Follow-up | Package a useful result with its checker and limitations in one PR. A reusable interface belongs in Virtual Human only after the Asma fixture shows value; scientific question and interpretation remain here. |

For a more general certificate/checker package, budget **2–4 engineering days**
after the first fixture succeeds, with independent review. A three-claim
statement audit is a separate **1–3 day** estimate. Maintaining the current
reports alone is the baseline: it has almost no integration cost and remains
preferable if the proposed machinery finds no additional error or useful test.

## Biological follow-through and current dependencies

The following are dated observations, not a new queue of duplicate issues.
Other teams retain ownership of their open changes.

| Track | Current evidence and unresolved dependency | Next useful decision |
| --- | --- | --- |
| CDR2L identification | Open [#66](https://github.com/Foundation-0/project-asma/pull/66), inspected at `539092b26c5eaa640baf47cf4b1dcb77d6c7b00d`, traces an original breast-cell-line identification to a deposited peak list. This is locator/integrity evidence, not independent peptide identification. Stacked [#67](https://github.com/Foundation-0/project-asma/pull/67), `e23f379b2a9cfbf92661e8d156ce49042ca2dea4`, hardens replay. | Complete those reviews and resolve [#71](https://github.com/Foundation-0/project-asma/issues/71)'s source-retention policy question before a new source-spectrum analysis. Then specify candidate alternatives, acquisition/search settings, ion rules, modifications, tolerances and decision criteria. |
| Candidate spectrum comparison | No new comparison executed here. A declared candidate universe permits a finite ambiguity analysis. | Report competing explanations and sensitivity to assumptions. Fragment matches alone do not establish a calibrated false-discovery rate or proteome-wide uniqueness. Stop if acquisition/search metadata cannot support the comparison. |
| HLA and receptor/injury | Source lineage and sequence compatibility do not establish a particular presenting HLA molecule, natural processing in the disease context, receptor recognition or injury. | Keep each experimental obligation separate. Neither library proofs nor a search result closes them. |
| Pilot 001 implementation | Main's [real-mode runner](https://github.com/Foundation-0/project-asma/blob/39285f33aea735501abeab47e409ead2205efbab/tools/pilot001_first_run/analyze_container.py) requests five repetitions instead of the frozen 100. Open [#68](https://github.com/Foundation-0/project-asma/pull/68), `362df78e451c78921ee59befaec81b1d73ce2cd3`, addresses this. [#69](https://github.com/Foundation-0/project-asma/pull/69), `9c1004bea0fa5e3d81569f70379760f123121328`, and [#70](https://github.com/Foundation-0/project-asma/issues/70) track broader conformance/readiness. | Complete and verify the existing fixes, including current synthetic execution evidence. Code paths have landed, but that does not establish protocol conformance or authorize a study run. |
| Study execution | [Runbook](pilot-001-first-run-runbook.md), [data rules](reproducibility-and-data.md) and owner gates remain controlling. | Fresh dated instruction/attestation, approved host, data-use conditions and preflight are prerequisites. This assessment provides none of them. |

During review, metadata refreshed to open #66 head
`7dcad04f5431ae135f8688251c773a709b05064b` and stacked #67 head
`e7917f1349247d78db3f0e4e4c3f2273ac5adc79`. The code assessment above remains
pinned to the earlier inspected revisions; the newer heads were not re-audited
for this report. #68/#69 heads were unchanged. Follow the live PR links for
subsequent work, rather than treating this snapshot as a landing decision.

Issue #71 also describes a historical failure to access #31. The current API
inspection successfully returned #31; do not treat a stale access failure as a
current missing authorization record. A readable historical record still does
not provide a fresh execution instruction.

## Adoption, freshness and rights

| Candidate | Decision and scope | Constraints that matter |
| --- | --- | --- |
| Soko | **Pattern only** for rechecked search constraints, scoped negatives and provenance-aware triage. | Inspected package metadata declares Apache-2.0, but no standalone LICENSE/NOTICE was found in that tree. Discussion prose and puzzle/source material have separate terms. No code copied; confirm file-level scope/notices before copying. Its [#25](https://github.com/ahrazzle/soko/pull/25) report records 35 failed/265 passed/6 skipped with no new failing IDs against baseline, not an all-green dependency. |
| finite-state-proofs | **Pattern only** for independent certificate checking and model-to-certificate arguments. | Main's [NOTICE](https://github.com/Foundation-0/finite-state-proofs/blob/9eeb3da2cdd6ba6b100ac24d23b32c369c0db8ec/NOTICE.md) says no repository-wide grant. Open [#3](https://github.com/Foundation-0/finite-state-proofs/pull/3) proposes licensing; it is not a current grant. No source code or certificates copied. |
| formal-claims-audit / mission | **Pattern only** for statement correspondence and adversarial review. | The structural validator is not a scientific evaluator. Formal-claims-audit is Apache-2.0; no implementation or review prose copied. |
| Proven-Commons CSV / JSON | **Watch**, not a parser migration. | Current inspected [CSV](https://github.com/Proven-Commons/csv/tree/9d15dc85f786e7b99b2bb6c6e6b72db79ee1c9b4) and [JSON](https://github.com/Proven-Commons/json/tree/4ff8eb6483e21ec87da03a80abdb0af45ba9b7f2) include Apache-2.0 licenses. Round-trip theorems do not establish full grammar coverage, clinical column meaning, duplicate-key policy or all numeric semantics. Asma's present pipeline is Python/R/XLSX, so integration adds a toolchain and semantic boundary without resolving the main scientific gaps. |
| Virtual Human | **Extend existing use only after a bounded need is shown.** | MIT attribution to Rohan Arun remains. Input evidence checks and synthetic engines are already available; they neither fill missing parameters nor validate biological composition. |
| certified-orbits | **Watch** for future rigorous numerics. | Inspected [main `51f6983`](https://github.com/Foundation-0/certified-orbits/tree/51f69833cd64ff3c1bc65c429566714fa2c9c17e) has plans; open #10/#12 do not supply a completed rigorous integrator/certifier. No present Asma dependency is justified. |

The anthology's October snapshot still reports older namespace and license
limitations. The [12 November sync run](https://github.com/Foundation-0/proven-commons/actions/runs/43232349581)
completed “Sync, build and audit” then failed at opening/updating its PR. That
publication failure is not a proof failure. Inspect current upstream pins before
making an adoption decision. Likewise, Soko's Pareto-cut report is not yet its
completed selection implementation; sampled Bellman consistency checks are not
an exhaustive certificate, as [#33](https://github.com/ahrazzle/soko/pull/33)
explicitly corrects. Do not import performance headlines as Asma predictions.

## Preservation and verification

Primary code/report pointers and inspection limits are recorded as S136–S143 in
[the source registry](../registries/sources.json). Source credit belongs to the
linked repositories' authors, with Rohan Arun's Virtual Human lineage retained.
The user pointed out these projects in this session; that discovery pointer is
separate from authorship. Existing [ingestion #563](https://github.com/aska-digital/ingestion/issues/563)
is the living Soko source discussion; its existing source-record PR remains
separate from adoption.

Only public repository code, documentation and public issue/PR state were read.
No private archive or correspondence was consulted; no study spectra, sequences,
matrices or patient records were acquired for this assessment. Upstream test
counts and proof outcomes above are attributed reports/static observations,
not fresh executions by this review. Local repository validation checks only
the resulting documentation and scaffold, not the proposed transfer's efficacy.

Prepared with OpenAI Codex and GPT-6 Astra agents for Asma status, Soko methods,
and Proven Commons/Foundation-0 evidence assessment. Internal review is not
external scientific peer review. Implementation, merges and deployments are not
part of this assessment.
