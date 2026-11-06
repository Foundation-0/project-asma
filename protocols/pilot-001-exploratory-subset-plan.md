# Pilot 001: pre-registered exploratory analysis plan for the frozen patients with no discovery record

**Version:** 0.1, 2026-11-06. **Status:** proposed; nothing in this plan has been
executed. **Scope:** an exploratory, pre-specified evaluation on the candidate
subset of **13 sensitive and 8 refractory patients** that has no observed
discovery record. It is a statistical contract written before any real-data
Pilot 001 number exists, for the frozen-cohort evaluation that
[Pilot 001](pilot-001.md) steps 4–5 leave to their own rules; its executable
tier is a published-score subset check modelled on the
[score-verification specification](pilot-001-score-verification.md). It is not
a reproduction of a published figure, not a validation study, not a new
classifier and not clinical decision support.

**Owner decision on record.** Gate 0 Q5 (2026-11-05, [issue #31](https://github.com/Foundation-0/project-asma/issues/31#issuecomment-6662111371),
[roadmap](../docs/roadmap.md#pilot-001--gate-0-owner-decisions-2026-11-05)): this
cohort is **exploratory only**; confirmatory claims need more independent
patients and a separate power calculation. Gate 0 Q4: external scientific
review is **deferred**; every result under this plan is labelled **not externally
reviewed**.

**Claim labels** follow [CLAIMS.md](../CLAIMS.md): PROVEN, VERIFIED, KNOWN,
CONJECTURE. Each numbered statement below carries one. The plan's own design
values are in the [design record](../registries/pilot-001-exploratory-subset-design.json),
regenerated with `python3 tools/plan_exploratory_subset_design.py` (VERIFIED,
claim V28). Field headings follow the
[research question template](../templates/research-question.md).

## 1. Question and falsifiable hypothesis

**Question.** Within the 21 frozen-cohort patients who appear in no discovery
record, do refractory-prediction scores rank refractory tumours above sensitive
tumours better than chance, and what operating characteristics does a threshold
fixed on other patients give?

**Hypothesis H1 (CONJECTURE, claim C22).** On this subset, the prediction
source's AUROC exceeds 0.5. The pre-specified test and its critical value are in
section 6. The alternative outcome, no signal demonstrated, is an equally valid
result of this plan.

**What the plan does not ask.** It does not test whether the published discovery
AUROC 0.83 (KNOWN, K01) or the released-score AUROC 0.8088507878 (VERIFIED,
V08) is reproduced; those remain governed by the
[score-verification specification](pilot-001-score-verification.md) and the
[discrepancy analysis](../docs/pilot-001-auc-discrepancy.md) (V23, C20). It does
not ask whether specificity is at least 98%: with 13 negatives that question is
unanswerable even under a perfect outcome (VERIFIED, V09).

## 2. Whose decision could this change

Only the owner's continuation decision under roadmap Gate 4 and the design of a
future confirmatory study: whether an exploratory signal justifies planning
independent-patient validation at a powered size (C06), or whether the public
frozen material should be set aside. No clinical, diagnostic or treatment
decision depends on this plan, and no patient-facing output is produced.

## 3. Histotype, population, treatment setting, endpoint and horizon

High-grade serous ovarian cancer, stage III/IV, primary debulking followed by
initial platinum/taxane therapy, as the paper's "Patient Selection and Cohorts"
describes (KNOWN; [feasibility audit](../docs/pilot-001-feasibility-audit.md),
section "Published endpoint, cohorts, and evaluation"). The endpoint is the
paper's **primary refractory** versus **sensitive** label: refractory means
radiographically detectable or progressing/stable residual disease at completion
of six cycles; sensitive means progression-free survival of at least two years
after primary resection and adjuvant platinum/taxane. Later platinum-resistant
recurrence is a different endpoint and is not substituted (KNOWN, K06). Labels
are the released clinical annotations; this plan assigns none.

The population is the frozen validation cohort of the paper (PDC000362; 64
tumours, 44 sensitive, 20 refractory, one institution), restricted as in
section 4. Horizon: the labels are fixed historical outcomes; no follow-up is
collected.

## 4. Population: the evaluation subset and the sets around it

All membership rules use the public released workbooks and the exact join the
[supplement audit](../registries/pilot-001-supplement-summary.json) records:
score `Samples` equals clinical `Data Label 2`, no normalisation (VERIFIED, V11).
"Patient key" means the explicit clinical `Patient ID` field, compared across
sheets by exact string equality with no trimming, case folding or other
normalisation, as the audit's `patient_linkage` records. Counts below are the
documented aggregates; the plan freezes them as expectations and stop rules.

| Set | Rule | Expected count (sensitive / refractory) | Role | Label |
| --- | --- | --- | --- | --- |
| **Evaluation subset** | Patient keys in the 34-row `Frozen_nonoverlap_pred_scores` sheet whose patient key appears in none of the 158 unique response-labelled discovery patient keys obtained by `classify_clinical` then `collapse_replicates` of `tools/audit_published_cohorts.py` on the 231 `FFPE_Discovery_clinical` worksheet rows (63 explicit-NA rows set aside, 168 response-labelled rows collapsed to 158; neoadjuvant and mixed-tissue discovery rows included) | **21 (13 / 8)** | Carries the primary endpoint and the only decision rule | KNOWN (K31): 21 from the audit registry `patient_keys_not_observed_in_all_discovery`; 13/8 from section 4 of the [open-questions report](../docs/pilot-001-open-questions.md), inherited, not rerun |
| Sensitivity set | Patient keys in the same sheet not in the 135-row eligible discovery score set | 28 (17 / 11) | One pre-specified sensitivity analysis, descriptive only | KNOWN (K31) |
| Calibration set | The 27 `Frozen_overlap_pred_scores` patients plus the 13 nonoverlap-sheet patients who do have a discovery record (34 − 21) | 40 (29 / 11) | Threshold selection only; never enters an operating-point metric. Seven of the 40 also sit in the descriptive 28-patient sensitivity set | KNOWN (K31), derived by subtraction |
| Published frozen "independent" set | The whole 34-row sheet | 34 (22 / 12) | Reference for the printed metrics; not evaluated here | KNOWN (K30) |

The calibration set is the only scored frozen material outside the evaluation
subset. Its patients overlap discovery, which is permitted for threshold
selection and forbidden for evaluation; it holds both classes (29 / 11).

**Independence status (stated, not assumed).** The 21 did not take part in the
published cross-cohort alignment, which pairs specimens by patient (open-questions
section 4, "Likely"), and have no discovery measurement. They are **not an
untouched evaluation set**: the panel's markers were filtered on detectability in
the validation data (paper P177), and their material is in the pooled reference
channel run in every discovery TMT plex (P129). Thirteen of the 34 published
"independent" tumours come from discovery patients (P145, P183); the 21 exclude
them. The 7 patients that separate the 28 from the 21 had mixed-tissue discovery
specimens that took part in discovery-wide preprocessing; the sensitivity set is
therefore **not** independent of upstream preprocessing. All 64 frozen patients
are from one institution, so no site independence exists. These facts are
documented in the open-questions report; nothing here reverifies them (KNOWN).

**Stop rule on membership.** If the executed join does not yield exactly 21
evaluation keys with 13 sensitive and 8 refractory labels, exactly 40
calibration keys with 29 and 11, and exactly 28 sensitivity keys with 17 and 11,
stop and report the counts. Do not re-derive membership, relabel, or exclude to
recover the expected numbers.

**Frozen-side membership check.** Before any subset is formed, the executor
reproduces the audit's equality: the 34 + 27 score sample keys must equal
`eligible_samples(Frozen_clinical)` (literal `Neo-adjuvant == 'no'` and
`Tumor Location Group != 'Mix'`: 61 samples, 3 neoadjuvant excluded, 0 Mix),
and reports those counts. The neoadjuvant and tissue-location fields serve that
check and nothing else; no subset is formed on them.

## 5. Permitted inputs, rights and access gates

**Tier A (this plan's executable analysis): released published scores.**

| Input | Role | Terms and handling |
| --- | --- | --- |
| `NIHMS1918576-supplement-MMC4.xlsx`, sheets `Frozen_nonoverlap_pred_scores` (34 rows) and `Frozen_overlap_pred_scores` (27 rows) | Prediction scores per sample | NLM article supplement, CC BY-NC-ND 4.0 metadata (KNOWN, K03). Read in process memory only; aggregates out. Bytes 591,065; SHA-256 `f318ed9d2fac341097a8b1be3e034753f6d427bdeeb0cd2b92eb715cadadb6ab` |
| `NIHMS1918576-supplement-MMC1.xlsx`, sheet `Frozen_clinical` (64 unique samples) | Labels, patient keys, neoadjuvant and tissue fields | Same terms. Bytes 41,194,360; SHA-256 `6e46fa0cb3023173a3643e95ce0360c44cfabb0ed737e9a05f70473dad552340` |
| `FFPE_Discovery_clinical` sheet of MMC1 | Only to decide "no discovery record" | Same terms; patient keys compared in memory |
| Byte source | How the workbooks reach the run | Both workbooks are local files already present on the permitted host, obtained by the owner under the data-use record (how is recorded in section 15). The Tier A implementation reads them through a local-bytes entry point added to the reused parser (whose constructor otherwise downloads from the NLM bucket), verifies bytes and SHA-256 before parsing, and makes no network request; any fetch attempt is a stop (section 8) |

These are the pinned inputs of the executed score verification (V08) and
supplement audit (V11). The frozen score values themselves have never been read
numerically (the audit reads only the key column). Computing a new subset
metric is, by the open-questions report and this plan, a **new performance
result**; Tier A reads study files live into memory and estimates a threshold
on study values. It therefore runs only under the study-data conditions of the
Gate 0 record in [data-use](../docs/pilot-001-data-use.md) and
[AGENTS.md](../AGENTS.md). All of them apply unconditionally; an instruction to
this plan can add to them, never waive one:

- the owner's explicit, dated instruction to execute, naming this plan version;
  a session's own checks never supply it, and Gate 0 Q5 alone is not read here
  as that instruction;
- the owner's dated attestation of the execution context, **current for the run
  date** (condition (a): the adapter attestation file and the public record;
  the attestation on record covers 2026-11-05 only);
- the host named by the Gate 0 Q1 record, the owner's MacBook in Ontario,
  Canada, with the macOS runtime preflight of data-use passed before any study
  byte is loaded (condition (b)); the host changes only by a dated Gate 0 Q1
  revision in the roadmap and the data-use record, never by an instruction to
  this plan, and the shared cloud host runs artificial inputs only;
- aggregate-only handling throughout, including terminal and agent-chat output
  (condition (c), section 6): an obligation during and after the run rather
  than a precondition that can be met in advance; the review before
  publication confirms it.

No study matrix, no model fitting and no acquisition of PDC or author files is
involved in Tier A; that narrows what the run touches, not which conditions
apply. The MMC workbooks' CC BY-NC-ND terms permit private noncommercial
adaptation, and whether the fair-dealing assessment of data-use is also needed
for these workbooks is not decided here; the conditions above apply either way.
[AGENTS.md](../AGENTS.md) separately allows rerunning the recorded audits (V08,
V23) as bounded inspection, while the Gate 0 Q1 record lists the same workbooks
as study data for the MacBook only; main does not reconcile the two, and this
plan resolves the question conservatively toward the host record pending the
owner's clarification. The 21-count is corroborated by the PDC catalog (21
frozen case records with no discovery match,
[linkage summary](../registries/pilot-001-linkage-summary.json)), as a count
only; exact correspondence between the two sets is not established.

**Tier B (later): reconstruction outputs.** The same contract applied to
predictions from the project's own reconstruction on the frozen PDC000362
proteome (CC BY 4.0, K02) is specified in section 14. Nothing in the repository
can produce such predictions today: the reconstruction is discovery-only and
keeps no fitted model, no frozen matrix is pinned or mappable to these patients,
and no per-patient transfer route exists. Tier B needs those prerequisites, every
open Gate 0 item, and a dated addendum to this plan before any frozen-matrix
acquisition.

**Never permitted under this plan:** `Foundation-0/asma-data` or any identifiable
clinical record; the author Dropbox matrix outside its conditional route in
[data-use](../docs/pilot-001-data-use.md); execution on the shared cloud host for
study data; persistence of any per-patient score, key or row; medical advice.

## 6. Frozen analysis contract

Fixed before execution. The [design record](../registries/pilot-001-exploratory-subset-design.json)
holds the exact null distribution, critical values and interval tables (V28).

| Item | Fixed value |
| --- | --- |
| Positive class and direction | Refractory positive; higher score predicts refractory (article section S95, as fixed in the [score-verification specification](pilot-001-score-verification.md)); asserted in code, never reversed on inspection of results |
| Primary estimand | Empirical AUROC on the 21: fraction of the 104 refractory–sensitive score pairs correctly ordered, half credit for exact ties, the convention shared by V08, `checked_auc` in `R/asma_core.R` and `evaluate_heldout`; cross-checked against the rank-sum formula as in V08, in exact fractions |
| Primary decision rule | Exact one-sided conditional permutation test of the AUROC against 0.5 at **α = 0.05**: p = (number of the C(21, 8) = 203,490 label placements over the observed scores whose half-credit U* is ≥ the observed U) / 203,490; reject iff p ≤ 0.05. The operative statement is in integers: with no tied scores among the 21 (within or across classes) this is the Mann–Whitney null and the rule reads **U ≥ 76 of 104** (AUROC ≥ 19/26 ≈ 0.7308, exact p = 0.04452; p at U = 75 is 0.05210). A rounded decimal is never the rule. With any tied scores the enumeration supplies p; no other handling is permitted. The design record's α = 0.025 and 0.01 rows are informational and are never reported as a decision or headline |
| Primary uncertainty | 95% percentile interval from a patient-level bootstrap with the conventions of [`tools/evaluate_heldout.py`](../tools/evaluate_heldout.py), not the stratified bootstrap of the discrepancy tool: **2,000** draws from `random.Random(20261106)`, each draw one `randrange` index per patient over the 21 jointly (not stratified by class), class-empty draws excluded and counted, endpoints by linear interpolation at (n − 1)p for p = 0.025 and 0.975, at least **1,000** valid draws required, degenerate intervals flagged and the bootstrap range reported. The 21 score/label pairs are ordered by ascending patient key (Python string sort, as `keys()` of `evaluate_heldout` orders them) before any index is drawn. The design record gives the expected class-empty count (about 0.085 of 2,000), so the minimum is not binding. The run uses CPython 3.12 or later, with the exact version declared in section 15 before the run and recorded in the artifact; a different ordering or interpreter is a deviation, not a rerun |
| Secondary interval | DeLong 95% interval on the same scores, with `delong_ci` of [`tools/analyze_auc_discrepancy.py`](../tools/analyze_auc_discrepancy.py) (the method of V23 (e)); it takes two positionally aligned lists, the parsed scores and the label strings `POSITIVE`/`NEGATIVE` of that module ('refractory'/'sensitive', not 0/1 and not a keyed mapping), which the executor builds in the pinned patient-key order and checks with `labels.count(POSITIVE) == 8` before the call; the executor copies only `auc`, `standard_error`, `lower` and `upper` into the artifact, and discards `contains_printed_0_83`, which has no meaning here. Its bounds are clipped to [0, 1]; a zero standard error is reported as degenerate, as for the bootstrap. Both classes exceed one patient, as its variance requires |
| Threshold | Chosen on the **calibration set only**, by the rule of `calibrate_threshold`, reimplemented in the Tier A code because that function accepts only `int`/`float` scores: target specificity 0.98 on 29 negatives allows int(0.02 × 29) = **0** false positives, so the threshold is the smallest representable value above the largest sensitive calibration score; positive if score ≥ threshold. The operating point therefore rests on one order statistic of the 29 calibration negatives; that is reported, not adjusted. Computed from the 40 calibration rows only and frozen before any evaluation metric is computed; the implementation must not reference evaluation rows in the threshold computation, although the sheet holding both is parsed at once. Numeric types: scores are parsed as `Decimal` by the V08 rule, and all ranking, AUROC, enumeration, AP and Brier arithmetic is exact; the threshold alone is a binary64 value, `math.nextafter(float(largest sensitive calibration score), math.inf)`, and the operating-point comparison is `float(score) >= threshold`. The executor reports how many distinct `Decimal` scores among the 61 share one binary64 image (expected 0) and how many evaluation scores equal the largest sensitive calibration score |
| Operating-point outputs | TP, FP, TN, FN on the 21; sensitivity k/8 and specificity j/13 with the two-sided 95% Clopper–Pearson intervals pre-tabulated in the design record (correctly rounded roots of the exact binomial tails); the result note reports the two-sided intervals only, and the record's one-sided table is a design-capacity reference (V09), not an outcome statistic; achieved specificity reported as observed, never forced to 98% |
| Other secondary outputs | Grouped average precision as defined in `_metrics` of `tools/evaluate_heldout.py` (per tied-score group, add the group's share of positives times the precision at the end of the group), with the subset prevalence 8/21 as its chance reference; Brier score of the released scores read as probabilities (article section S95). Both are reimplemented in the Tier A code in exact arithmetic (that private function is not called; its `Decimal` Brier would not serialise), with unit tests asserting agreement with `_metrics` on a fixture before the run; both descriptive within the selected-cohort design, not population calibration |
| Comparators (Tier A) | Chance (AUROC 0.5) through the decision rule; the printed frozen-independent AUC 0.79 (95% CI 0.63–0.96) and sensitivity 0.25 at 98% specificity, both on the 34-tumour set including 12 refractory (KNOWN, K30), reported **beside** the result with no agreement tolerance: different denominators, unknown published threshold rule, so no pass/fail |
| Sensitivity analysis | The same AUROC, bootstrap interval and DeLong interval on the 28 (17/11). No decision rule; its design critical value (U ≥ 130 of 187, AUROC ≥ 130/187 ≈ 0.6952) is recorded only so that no one invents one later; no enumeration is run on the 28 |
| Multiplicity | One primary endpoint, one decision rule, one prediction source per tier. Everything else is descriptive. Any further comparison is post hoc and labelled so |
| Software | Python standard library only; an implementation committed **before** execution that reuses the workbook parser, `classify_clinical`, `collapse_replicates`, `eligible_samples`, `join_score_membership` and the exact-join helpers of `tools/audit_published_cohorts.py` as the V08 tool did. The run artifact records under `implementation_sha256` the SHA-256 of every module the run imports or reimplements from (the Tier A implementation, `tools/audit_published_cohorts.py`, `tools/analyze_auc_discrepancy.py`, `tools/evaluate_heldout.py`) and of this file; the design record's `implementation_sha256` names the design tool. The exploratory path of both tiers runs through this implementation; `evaluate_heldout` fails closed unless every contract boolean is truthfully `True`, which Tier A cannot assert (section 4), so Tier A never calls it |
| Output | One aggregate JSON artifact at `registries/pilot-001-exploratory-subset-result.json` and a dated result note at `docs/pilot-001-exploratory-subset-result.md`. The note holds, in order: the label line of section 7, the membership and frozen-side counts of section 4, the point AUROC as an exact fraction, the exact p-value and decision, both intervals with their status flags, the tie counts on the 21 and the 40, the 2 × 2 table with its intervals (subject to section 13), AP and Brier, the 28-patient sensitivity analysis, the printed 34-tumour comparators, and the deviations and stops of section 15; the artifact holds the same aggregates with the hashes, versions and seed. No patient key, score, rank or per-patient hash leaves process memory, including terminal and agent-chat output. The threshold value itself is not emitted; the published 2 × 2 together with the public score sheet determines its rank position among the calibration scores, which is disclosed by design (section 13) |

**Ties.** The released discovery scores had zero cross-class ties (V23 (a)). The
executor reports the numbers of tied scores on the 21, within and across
classes, and on the 40. Ties change nothing in the rules above; they are handled
by half credit and by the conditional enumeration, whose p-value then differs
from the tie-free table.

## 7. Decision rules and permitted wording

| Observed outcome | What may be said | Label of the statement |
| --- | --- | --- |
| Exact p ≤ 0.05 (no ties: U ≥ 76) | "Within this 21-patient subset, the evaluated scores ranked refractory above sensitive tumours more than expected by chance at the pre-specified 5% level (exploratory; not externally reviewed)." | VERIFIED for the arithmetic; the inference is a **CONJECTURE-level signal** for a future design |
| Exact p > 0.05 | "No discrimination signal was demonstrated in this subset at the pre-specified level; the interval is reported. This is not evidence of absence." | VERIFIED for the arithmetic; interpretation CONJECTURE |
| Any outcome | The point AUROC, both intervals, tie counts, the operating-point table, AP, Brier, and the 28-patient sensitivity analysis, each beside the printed 34-tumour values | VERIFIED (aggregates) |
| Stopped under section 8 | "This plan was stopped before a result was produced; the stop reason and the observed counts are recorded. No discrimination estimate was computed and none may be inferred (exploratory; not externally reviewed)." | VERIFIED for the recorded counts |
| Any outcome | Never: "validated", "independent validation", "reproduced", "specificity ≥ 98%", "clinical utility", any statement about an individual patient, or a comparison that implies the printed 0.79 was tested | — |

A result or stop note's label line must read: **exploratory; selected single-institution
subset; not independent of upstream preprocessing; not externally reviewed.**

## 8. Success criterion, stop rules and confounders

**Success** means the plan was executed exactly as written and its outcome
recorded, whichever outcome occurred. Agreement with any published number is
not a success criterion.

**Stop before or during execution, without producing a result, if:**

- any item of the section 5 gate is missing: the owner's dated instruction
  naming this plan version, a dated attestation current for the run date, the
  Gate 0 Q1 host with its macOS preflight passed, or aggregate-only handling;
  or execution would leave that host or handling;
- a workbook's bytes or SHA-256 differ from section 5; a score sheet's row
  count differs from 34 or 27; or the clinical sheets' unique patient keys
  differ from 64 (`Frozen_clinical`, 72 response-labelled rows in four
  triplicate blocks) and 158 (`FFPE_Discovery_clinical`), the counts of the
  supplement audit;
- a workbook is not supplied as local bytes, or the implementation attempts
  any network request;
- a technical-replicate group disagrees on any field in `CRITICAL` of
  `tools/audit_published_cohorts.py`, or the frozen-side membership equality of
  section 4 fails;
- the join is not exact and one-to-one, a key is duplicated, or a clinical
  field needed for labels or discovery matching is missing or ambiguous;
- membership counts differ from section 4;
- a score is non-numeric, non-finite or outside [0, 1];
- the two AUROC calculations disagree, or the enumeration total for the 21 is
  not 203,490;
- fewer than 1,000 bootstrap draws contain both classes;
- the implementation's hash was not committed before the run.

Numeric disagreement with a printed value is a reportable finding, never grounds
to change direction, membership, threshold rule, α, seed or draw count.

**Confounders and effects that cannot be separated at n = 21:** preservation
(frozen versus FFPE), single institution, assay batch, tumour purity, tissue
location, residual-disease category, and the marker-detectability filter applied
to the validation data. The plan reports these as limits; it fits nothing to
adjust for them.

## 9. What this sample size can and cannot support

**Can support (all exploratory):**

- A one-sided exploratory test of discrimination above chance with the exact
  critical value U ≥ 76 of 104 pairs, AUROC ≥ 19/26 ≈ 0.7308 (VERIFIED, V28).
  The region is minimal: U = 75 gives p = 0.0521.
- Descriptive estimates with honest width. With 8 refractory patients, every
  two-sided 95% sensitivity interval is at least 0.36 wide (for example 2/8 →
  3.2%–65.1%, 3/8 → 8.5%–75.5%); with 13 sensitive patients, a perfect
  specificity gives a one-sided 95% lower bound of 79.42% and a two-sided lower
  endpoint of 75.29% (VERIFIED, V09 and V28).
- Whether released predictions carry rank information in a subset that took no
  part in the published alignment fit; a basis for deciding whether a powered
  design is worth planning (C06).

**Cannot support:**

- Specificity of at least 98% with any bound: zero false positives would need
  149 (one-sided) or 183 (two-sided) independent negatives (VERIFIED, V09).
  Exact 98% specificity is unattainable with a denominator of 13.
- A confirmatory validation claim, a reproduction claim for the printed 0.83 or
  0.79, or an estimate transportable to a population: the cohort selects
  extreme responders at one institution, and the subset is not independent of
  upstream preprocessing (owner decision Q5; K30, K31).
- Calibration assessment, subgroup analyses, or any comparison between models
  with meaningful power.
- Any clinical inference.

Repeated folds, bootstrap resamples, technical replicates or multiple tumours
from one patient do not add independent patients; the counts above are the
counts.

## 10. Next decision after each outcome

- **Signal (p ≤ 0.05):** record it as an exploratory signal; propose, as a
  separate protocol pull request with its own power calculation, an
  independent-patient design (C06 gives the zero-error minima); do not expand the
  present subset analysis.
- **No signal:** record it; no automatic further search in the public material.
  The next decision is whether Tier B (section 14) is still worth its gates.
- **Inconclusive (stopped):** record the stop reason; a changed plan is a new
  dated version, executed afresh, never a patched run.

## 11. Required expertise, review, compute and dependencies

Execution needs only Python's standard library and the pinned workbooks (under
a minute: V08 ran in 2.8 s, and enumerating the 203,490 placements takes tens of
seconds in pure Python). Interpretation needs a proteomics/biostatistics
collaborator and a gynecologic oncologist, who have not been recruited and must
not be recruited without a new explicit instruction. External scientific review
is deferred (Q4); internal agent checks are technical checks only. Dependencies:
the section 5 gate (instruction, current attestation, host preflight); the
supplement audit's pins staying valid.

## 12. Planned deliverables and what has actually been executed

Planned: this plan; the design record; after the section 5 gate is met, one
committed Tier A implementation, one aggregate artifact, one dated result note
with the label line of section 7, and the matching ledger entries.

Executed so far: **nothing on study data.** The design calculation ran offline on
documented counts (V28). No workbook was read for this plan, no score was seen,
no threshold was selected, no AUROC was computed on any subset.

## 13. Limits on interpretation, publication and data protection

- Aggregates only, and a disclosure review precedes publication. Proposed
  disclosure rule, a project choice for the owner to confirm with the execution
  instruction: the 2 × 2 counts on the 21 and the tie counts are published
  without cell suppression, because every label and score behind them is
  already public per patient in the released supplements and the counts derive
  nothing new about any patient. This departs from the general small-cell
  wording of [reproducibility-and-data](../docs/reproducibility-and-data.md)
  for public per-patient inputs only; sensitivity k/8 and specificity j/13
  determine the same four cells, so suppression would be form, not protection,
  which is why the choice is recorded as a decision rather than assumed. Until
  the owner confirms it, the 2 × 2 table and tie counts stay out of the public
  outputs. The review before publication confirms that the artifact holds only
  the aggregates of section 6, and no per-patient value, key, rank or hash is
  persisted or emitted.
- The released frozen scores are not established as the exact predictions behind
  the printed frozen metrics (open-questions section 4, "Open"); the released
  discovery sheet already misses the printed 0.83 (V08). Tier A evaluates the
  released scores as released.
- Nothing in this plan changes the published groups, resolves the six-key
  overlap discrepancy, or treats the frozen cohort as independent.
- Supplement terms are non-commercial and no-derivatives for redistribution;
  only computed aggregates are published, with citation of the article version
  and supplements.

## 14. Tier B: the same contract on reconstruction outputs

If the project's own reconstruction ever produces frozen-cohort predictions,
sections 4, 6, 7, 8, 9 and 13 apply unchanged, with the substitutions fixed
here. Tier B is **not** authorised by this plan, and the repository at this
version cannot run it: the [decision record](pilot-001-reconstruction-decisions.md)
and [reconstruction contract](pilot-001-independent-reconstruction.md) cover
discovery only; `fit_models` in `R/asma_models.R` returns held-out
probabilities for the 27-patient test fold and keeps no model object; the
model-input checks accept only the 108/27 geometry; the first-run input manifest
pins no frozen matrix; the PDC000362 header has no exact match to the clinical
labels ([matrix-header summary](../registries/pilot-001-matrix-header-summary.json));
the archive's likely frozen member (the unverified PR #18 listing in
open-questions section 3) is unpinned and its rights unassessed; and the
first-run output validator's exact key schema and forbidden key tokens leave no
field for keyed predictions (its numeric-vector heuristic alone, at 31, would
not catch a 21- or 27-entry list), so no route carries them to
`evaluate_heldout`. These are absent, not disabled.

**Fixed now (carry over unchanged):**

| Item | Tier B value |
| --- | --- |
| Evaluation, sensitivity and calibration sets | Exactly as section 4, applied to the frozen patients' own keys; the 21 are evaluated, the 40 calibrate, the 28 are the sensitivity analysis |
| Prediction source configuration | The **primary** configuration of the adopted [amendment 1](pilot-001-reconstruction-amendment-1.md) (outer seeds 1–100, XGBoost `exact`); the `hist` and seed-block configurations never supply the Tier B model and are never chosen after seeing any AUROC |
| Harmonisation | Pilot step 4 strategy (a), narrowed: any FFPE–frozen mapping is fitted only on the 27 overlap-sheet pairs. The 6 same-patient different-tumour keys of K09, whose FFPE side is also in the 135, are excluded from the fit and stay in the calibration set (33 scored frozen patients share eligible discovery in all; registry `eligible_frozen_shared_with_eligible_discovery`). Patients in the fit never enter the evaluation subset, and the 21 contain none of them. Strategies (b) and (c) are not used |
| Evaluation library | `evaluate_heldout` with its contract booleans set **truthfully**: `development_inventory_complete` and `upstream_independence_verified` may be `True` only when the step 1 manifest lists every development patient and classifies each of the 21 as independent. If any of the 21 is classified unresolved, the library refuses (it fails closed on a `False` boolean) and Tier B reports through the plan's own implementation under this exploratory contract, as Tier A does, never as an independent-patient metric |
| Comparators | The library's prevalence baseline from the 135 discovery training labels (52/135), and the regularized logistic baseline of pilot step 5 trained on the same panel and discovery patients; `reference_model` fixed as `prevalence` before evaluation |
| Thresholds | `calibrate_threshold` on the 40 calibration patients' Tier B predictions, specificity target 0.98, frozen before any evaluation outcome is accessed |
| Decision rule, intervals, seed, draws | As section 6; the critical value is the same because the counts are the same |

**Absent today; a dated addendum must fix each before any frozen-matrix
acquisition:**

- a final-model rule (which fit, on which patients, with which ensemble
  averaging) that yields one frozen model per section 6, since the first run
  discards every fit;
- a pinned, hash-verified frozen input with an exact mapping to the 61 eligible
  frozen patients, a data-use disposition for that input, and a source-adapter
  contract for it;
- a tested, non-persisting in-memory route from the R pipeline to the Python
  evaluation at full precision, with the output validator's key schema extended
  by a reviewed change (not by relying on its vector-length heuristic) and
  nothing per-patient leaving process memory;
- the step 1 classification of each of the 21 as independent, overlapping or
  unresolved, with the P177 detectability filter and the pooled-reference
  channel stated as limits either way;
- the open Gate 0 items of the [roadmap](../docs/roadmap.md): a dated attestation
  for the run date, macOS preflight, condition (c), and the reviewed A2 option B
  and A3 implementations;
- the regularized logistic baseline's implementation and tests.

Tier B inherits every requirement of the roadmap and of
[data-use](../docs/pilot-001-data-use.md); meeting the list above does not by
itself authorise a run.

## 15. Execution instruction and review record

The first group is completed before execution and the second immediately
after; both groups empty means not executed.

Before execution:

- Owner's dated instruction to execute Tier A (date, verbatim wording, link):
- Attestation current for the run date (condition (a); date, public record link):
- Gate 0 Q1 host and macOS preflight (condition (b); pass/fail, date):
- Executing account and CPython version; how the workbook bytes reached the host:
- Commit hash of this plan and of the Tier A implementation:

After execution:

- Run artifact SHA-256 and result note, or the stop reason and observed counts:
- Aggregate-only handling confirmed by the review before publication (condition (c)):
- Deviations and their reasons:
- Disclosure rule of section 13: confirmed, replaced or pending:
- External scientific review: **deferred (Gate 0 Q4)**; record any later review
  separately with name/role, date, version and disposition.

## 16. AI assistance

This plan, its design tool, tests and ledger entries were written by **Claude**
(Anthropic; Claude Code) under human direction, with independent internal agent
review of the design values and wording. Internal review is not external
scientific peer review, and no AI system is an author of patient-facing guidance.
