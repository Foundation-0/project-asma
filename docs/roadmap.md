# Roadmap

Status: updated 2026-11-05. The [project mission](mission.md) defines useful
progress across **open-ended** ovarian cancer research. Pilot 001 keeps its
existing gates and endpoint; other work enters through the process below.

**Research continuation, 2026-11-04:** the
[preservation record](research-continuation.md) retains the broader public-source
work for the team. The current frontier proposal focuses on human anti-Yo
antigen recognition, presenting context and effector role, with two documented
exploration cycles and an executed synthetic identifiability check. It has no
patient-data execution result and does not close Gate 0. Its prior-art search,
competing models, stop rules and next literature task are recorded explicitly.

## Candidate directions (new tracks)

Ranked public-data possibilities live in [directions.md](directions.md). Any
**new direction** — not a continuation of Pilot 001 under its current protocol —
starts with:

1. A **protocol pull request** (population, endpoint, permitted inputs, stop
   rules, claim labels), using the [research-question template](../templates/research-question.md).
2. An **owner gate** mirroring **Gate 0** before live acquisition of study
   files, a real-source input check, or fitting on study values.

Software preparation and bounded metadata audits may proceed in parallel, as for
Pilot 001, but must not be described as closing Gate 0 without the owner's
dated execution-context attestation and explicit instruction.

The scaffold,
[static feasibility audit](pilot-001-feasibility-audit.md), and
[public input/linkage investigation](pilot-001-input-resolution.md) are completed.
Executed metadata checks advance Gates 0–1; they do not close the remaining
method, input, corrected-supplement or scientific-review requirements.

The **2026-11-04 software rerun** passed all 179 R assertions, the full
100-repeat synthetic pipeline, the current adapter fixture (19 bridge
assertions), 30 adapter Python tests under pinned CPython, and all 40
execution-condition checks on the rebuilt combined runtime. It closes the
post-October-27 fixture rerun and cgroup-probe gaps; it uses artificial inputs
only and does not close every Gate 0 item or the attestation, macOS preflight,
A2 option B and A3 steps still open after the
[2026-11-05 Gate 0 record](#pilot-001--gate-0-owner-decisions-2026-11-05).
*Status corrected 2026-11-08: Amendment 1 mechanisms have since landed; the
[pre-run readiness audit](pilot-001-pre-run-readiness-2026-11-08.md) records
per-item verdicts and the conformance gaps that remain. Statements in this
roadmap describing A2 option B or A3 implementation as outstanding are
superseded by that audit.* The [source-adapter report](pilot-001-source-adapter.md) records the
commands, hashes and remaining unknowns. The same day's
[GitHub source check](pilot-001-open-questions.md#github-follow-up-2026-11-04)
found no new upstream input release. Software preparation and bounded public
evidence reviews can continue while these scientific and execution questions
remain open.

The [validation-capacity analysis](pilot-001-validation-capacity.md) now makes
the high-specificity limitation quantitative using existing aggregate counts.
The candidate subset has 13 sensitive patients. Even perfect observed
specificity would give a one-sided 95% lower bound of 79.4%, under independent
binomial sampling and a fixed threshold. The favorable-outcome minimum for a
98% lower bound is 149 independent sensitive patients with zero false positives.
Owner decision (2026-11-05, Gate 0 Q5): treat the current candidate cohort as
exploratory only; a future confirmatory design needs more independent
patients and a separate power calculation. The
[held-out evaluation library](heldout-evaluation.md) prepares the comparisons
and uncertainty calculations in steps 4–5 of the pilot. It has artificial tests
only and does not resolve input independence or authorize study-data execution.

The [published-score verification](../protocols/pilot-001-score-verification.md)
ran under the user's explicit instruction, with external review still pending.
Its [AUROC result](pilot-001-score-verification-result.md) is 0.8088507878,
rounding to 0.81 and missing the fixed comparison against printed 0.83. This
advances the reproduction investigation through a recorded discrepancy; it does
not regenerate the original predictions or close Gate 2.
Owner decision (2026-10-25): the consolidated
[source request](../templates/pilot-001-source-request.md) is authorized as a
draft only. The owner alone decides whether and when to send it; automated
sessions never send it or contact authors, and the earlier automated posting
attempts should not have happened. The owner confirmed that the recorded data
inspections ([#2](https://github.com/Foundation-0/project-asma/pull/2), [#4](https://github.com/Foundation-0/project-asma/pull/4)) and synthetic model runs
([#11](https://github.com/Foundation-0/project-asma/pull/11)) were intended results of
autonomous research. Do not recruit
collaborators or reviewers without a new explicit instruction. Continue the
investigation using public sources and internal checks, within the owner
conditions in Gate 0, recording limits without treating deferred review as
completed. The
[code-audit addendum](pilot-001-code-audit-addendum.md) adds static findings and
the protocol/contract changes they motivate (numbered pilot 0.7 and contract 0.3
on their branch; integrated as pilot 0.10 and contract 0.6).

The [independent follow-up](pilot-001-independent-progress.md) tested the direct
PDC header/design routes and then found a useful downstream citation to the
original author archive. Its imputed discovery-matrix header matches all 168
response-labelled measurement rows and all 135 published discovery-score keys.
The subsequent complete-member audit verifies its ZIP CRC and finds all 64 panel
symbols exactly once among 8,800 feature rows. This resolves naming and feature
availability for the candidate input; transformation provenance remains open.
Score export and corrected legend provenance also remain unresolved.

On 2026-10-25 the [open-questions report](pilot-001-open-questions.md) narrowed,
without closing, the fold-helper, frozen-overlap and corrected-legend items. It
also found 64/64 panel coverage in the validation cohorts' published feature
lists and assessed the 2025 fallback as not ready. It computed no new
performance result; any patient-independent frozen metric still needs a
pre-specified protocol and the owner's decision. The
[exploratory subset plan](../protocols/pilot-001-exploratory-subset-plan.md)
(2026-11-06) is that pre-specified protocol for the 21-patient subset with no
discovery record: it freezes endpoints, permitted inputs, decision rules,
uncertainty methods and stop rules under the Gate 0 Q5 exploratory-only
decision. It is not executed; execution still needs the owner's dated
instruction naming the plan version, a dated attestation current for the run
date, the macOS preflight on the Gate 0 Q1 host and aggregate-only handling, and
its Tier B application to reconstruction outputs inherits every open Gate 0
item.

The [public-input reconstruction contract](../protocols/pilot-001-independent-reconstruction.md)
now links a concrete [decision record](../protocols/pilot-001-reconstruction-decisions.md)
for feature interpretation, sample-key averaging, ordering, new folds, models and
aggregation. The [synthetic validation](pilot-001-synthetic-validation.md) now
records the original implementation, installed dependency inventory and complete
100-repeat execution on abstract fixtures. The
[data-use disposition](pilot-001-data-use.md) selects independent noncommercial research, original implementation and no persistent patient-level
files. It clarifies private-computation and attribution conditions and selects a
conditional Canadian research fair-dealing basis. Actual execution context and
applicable hosting/review conditions must support that basis before fitting.

The [source adapter and execution check](pilot-001-source-adapter.md) now validate
generated source-format files through the actual model pipeline. At commit `ef1f522`, which
added the adapter, all 138 Python tests and 18 new R bridge assertions passed; the
[execution-conditions record](../registries/pilot-001-execution-conditions.json)
now lists 40 passed controls for the 2026-11-04 combined runtime, superseding
the earlier 2026-10-25 observation. The source
adapter has not ingested study bytes. The next step is to select
and assess an actual execution context, including host terms and applicable
obligations, and verify the combined runtime on that host. Live acquisition of study
files follows only after the owner's sign-off in Gate 0. Keep historical uncertainties explicit; do not repair them silently
to improve agreement. Research fitting remains conditional on the data-use disposition
and on the owner's sign-off in Gate 0. Before any research run, also resolve the
remaining open items in the [reconstruction contract](../protocols/pilot-001-independent-reconstruction.md):
a fixed sensitivity configuration and the per-repetition AUROC distribution.
Both items were adopted on 2026-11-05 and implemented. Remaining conformance
work is listed in the
[2026-11-08 readiness audit](pilot-001-pre-run-readiness-2026-11-08.md). The
per-model planted-signal direction test passed in the pinned image on
2026-10-27. No researcher contact is needed for the software preparation. The
2025 fallback remains unadopted.

## Pilot 001 — Gate 0 owner decisions (2026-11-05)

**Recorded:** 2026-11-05, 9:34 AM America/Chicago (15:34 UTC); **Q1 revised**
9:37 AM America/Chicago (15:37 UTC). **Sources:**
[Gate 0 answers](https://github.com/Foundation-0/project-asma/issues/31#issuecomment-6662111371);
[Q1 update](https://github.com/Foundation-0/project-asma/issues/31#issuecomment-6662169564);
[execution-context attestation](https://github.com/Foundation-0/project-asma/issues/31#issuecomment-6662220698).
The owner (Alkindus Arifuddin) answered in a Grok Bot chat; grk-helix checked
that chat's transcript.

| Item | Owner answer (verbatim) | As recorded |
| --- | --- | --- |
| Q1. Execution location | Initial: "run it on the bots' cloud computer". **Update:** "My MacBook is in Canada" (2026-11-05, 9:37 AM CT). Province: **Ontario** (9:39 AM CT). | **Study data:** the owner's personal MacBook (macOS), physically in Canada (Ontario). **Not for study data:** the Grok Bot team's shared cloud computer (AWS us-east-1 outbound address, Ashburn, Virginia, US — not a Canadian context). That host is for **CI and dry runs on artificial inputs only**. **Dropbox matrix:** conditional go on the MacBook per [data-use](pilot-001-data-use.md#assessment-for-owner-macbook-in-canada-gate-0-q1-update-2026-11-05) when conditions (a)–(c) are met; see attestation below. Openly licensed inputs (PDC000357–362 CC BY 4.0; MMC workbooks non-commercial) remain usable without that route. |
| Q2. Gate 0 sign-off | "yes" | The owner signs the execution-context attestation and instructs live acquisition of study files and fitting on study values, subject to the Q1 host and data-use conditions above. **Attestation recorded** 2026-11-05, 9:39 AM CT (verbatim in [execution-context attestation](https://github.com/Foundation-0/project-asma/issues/31#issuecomment-6662220698)). Condition **(a)** met for a run on **2026-11-05 only**; a later run date needs a fresh dated attestation. Conditions **(b)** macOS preflight and **(c)** aggregate-only output (including terminal and agent-chat output) remain **open**. |
| Q3. Amendment 1 | "take grk-helix's recommendations" | **A1: accept.** **A2: both** — option A XGBoost `hist`; option B outer seeds 101–200. Option B must be implemented, tested and reviewed before the run. **A3:** the proposed strict policy — all warnings, messages and console text are fatal, with an aggregate failure code. See [amendment 1](../protocols/pilot-001-reconstruction-amendment-1.md#owner-decision-required). |
| Q4. External scientific review | "defer" | Deferred. Any result must be labelled **not externally reviewed**. Deferred review is not completed review. |
| Q5. Cohort scope | "confirm" | The 13-sensitive-patient cohort is exploratory only. Confirmatory claims need more independent patients and a separate power calculation. |

**Owner execution-context attestation (2026-11-05, 9:39 AM America/Chicago).**
Verbatim ([issue #31](https://github.com/Foundation-0/project-asma/issues/31#issuecomment-6662220698)):

> I attest that on Nov 5, 2026 the Pilot 001 run executes on my own MacBook, physically in Canada; the use is noncommercial; and no institutional or funding obligations apply to it.

Province (verbatim): "Ontario". Condition **(a)** of the conditional Canadian route in
[data-use](pilot-001-data-use.md#assessment-for-owner-macbook-in-canada-gate-0-q1-update-2026-11-05)
is **met for a run on 2026-11-05 only**. A run on a later calendar date needs a
fresh dated attestation. Conditions **(b)** and **(c)** remain open.

Gate 0 is **partially closed**: Q1 execution host, Ontario provincial note and
Canadian-context assessment are recorded; Q2 attestation for 2026-11-05 and
Q3–Q5 are recorded. Before study-data fitting, still required: macOS runtime
preflight ([data-use](pilot-001-data-use.md#macos-runtime-preflight-study-data-host)),
condition **(c)** on the run, A2 option B implementation, and A3 implementation.
Issue [#31](https://github.com/Foundation-0/project-asma/issues/31) stays open until
preflight, condition (c) on an executed run, and A2 option B are satisfied.

Implementation status corrected 2026-11-08: A2 option B and A3 code has
landed. Preflight and condition (c) remain open. Per-item status and the
conformance items that remain are in the
[readiness audit](pilot-001-pre-run-readiness-2026-11-08.md). The issue #31
links in this section return 404 (checked 2026-11-08).

Owner decision (2026-11-05, Gate 0 Q3): adopt
[reconstruction amendment 1](../protocols/pilot-001-reconstruction-amendment-1.md)
as above. Merging that file alone never adopted it; this dated record does.
The direction test, the third open item,
passed in the pinned image on 2026-10-27. That rerun regenerated the synthetic
and source-adapter execution records (179 R assertions, the full 100-repeat run
and 19 bridge assertions; see the
[synthetic validation](pilot-001-synthetic-validation.md#pinned-image-rerun-2026-10-27)).
The execution-condition probe could not run on that cgroup v1 host. The
2026-11-04 rerun passes it on a cgroup v2 host. The owner-attestation follow-ups
([#22](https://github.com/Foundation-0/project-asma/pull/22)) then changed
`tools/source_data_adapter.py` and `tests/test_source_data_adapter.py`; both
are covered by the 2026-11-04 pinned-image fixture and unit-test rerun. A
real-file check needs the owner's execution-context attestation for the run date
(Gate 0 Q2; condition (a) met for 2026-11-05 only), macOS preflight (b), and
aggregate-only handling (c) per [data-use](pilot-001-data-use.md).

| Gate | Deliverable | Acceptance or stop rule |
| --- | --- | --- |
| 0. Agree scope and rights | Input-specific use disposition; applicable review requirements; code-licensing expectations | Original implementation can proceed. Bounded, in-memory source inspection, including rerunning the recorded audits, is part of autonomous research (owner decision, 2026-10-25) and keeps only aggregates; unresolved real-data use conditions stop fitting. Live acquisition of study files, a real-source input check or fitting on study values needs the owner's dated attestation and explicit instruction (recorded 2026-11-05, Q2) on the owner's MacBook in Canada with macOS preflight and data-use conditions met; the shared cloud host is CI and artificial-input dry runs only. Automated checks never satisfy this. No collaborator has been recruited. External scientific review is **deferred** (2026-11-05, Q4); label any result **not externally reviewed**. |
| 1. Establish provenance | Release/file/checksum manifest; private patient/aliquot overlap map; exclusion counts; pinned author commit and environment | Every cohort has a traceable source and independent-patient status. Unresolved identity, labels, or terms stop analysis. |
| 2. Reproduce one result | One specified Figure 3D result with commands, locked dependencies, seeds, inputs, and discrepancy log | Numerical agreement within a declared tolerance, or a reproducible explanation of failure. No performance claim from a hard-coded plot label. |
| 3. Stress-test | Patient-independent metrics with uncertainty; simple baselines; leakage and assay sensitivity analyses | Separate preservation/batch/cohort effects and original reproduction from revised evaluation. Report null and negative findings. |
| 4. Decide continuation | Short feasibility report and reviewed next question | Continue only if data access, sample independence, compute, and interpretation are adequate. No automatic expansion into a new classifier. |

An initial **2–4 week feasibility window is conditional**, not a delivery
commitment. It assumes accessible processed data, adequate metadata, tractable
author dependencies, modest compute, and availability of a gynecologic oncologist
and a proteomics/biostatistics collaborator. Unresolved rights, missing helper
files, overlap, or correction implications may require a pause or narrower target.

The first milestone bundles provenance and overlap, a reproducible environment,
one reproduced result, and an initial independent-patient evaluation with
uncertainty and simple baselines. Its details are in the
[pilot protocol](../protocols/pilot-001.md). No issue backlog is needed yet.
