# What the available cohort can establish about 98% specificity

**Executed on 2026-10-29:** an offline calculation using existing public
aggregate counts. No classifier performance was measured, no study files were
acquired and no patient-level data were read. The calculation does not change
any protocol, execution authorization or scientific-review gate.

The candidate subset without an observed discovery record contains only **13
sensitive patients and 8 refractory patients**. Even if a fixed classifier
correctly classified every one of those 13 sensitive patients, the one-sided
95% lower confidence bound on specificity would be **79.42%**. The corresponding
lower endpoint of a two-sided 95% interval would be **75.29%**. This cohort cannot
establish specificity of at least 98% with either bound, even under this best
possible hypothetical outcome.

| Existing aggregate cohort | Sensitive / refractory | Hypothetical false positives | One-sided 95% lower bound | Two-sided 95% lower endpoint |
| --- | ---: | ---: | ---: | ---: |
| Candidate with no observed discovery record | 13 / 8 | 0 | 79.42% | 75.29% |
| Published frozen `nonoverlap` score set | 22 / 12 | 0 | 87.27% | 84.56% |

These are conditional design calculations, **not observed confidence intervals
for the signature**. The second cohort includes discovery-overlapping patients.
Its row is illustrative, not a claim that independent-binomial inference is
valid for that published evaluation. Independence and an untouched evaluation
set remain unresolved even for the first cohort.

## Why this calculation matters

The paper reports sensitivity at 98% specificity for the discovery and frozen
evaluations (main-text paragraph P33). Its methods describe 34 frozen evaluation
tumors (P183) and alignment using 29 overlapping pairs plus 14 additional pairs
from the same patients (P145). These passages were checked against the
[primary article XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC10414761.1/PMC10414761.1.xml)
on 2026-10-29. The [2024 correction](https://doi.org/10.1016/j.cell.2024.01.016)
concerns supplemental figure legends. It supplies no revised numerical
specificity result.

At a fixed deterministic threshold, specificity changes in increments of
**1/13 = 7.69 percentage points** or **1/22 = 4.55 percentage points** in these
sets. Exact empirical specificity of 98% is unattainable with either denominator.
One false positive would yield 92.31% or 95.45%, respectively. An interpolated
ROC point at 98% is a different quantity from an attainable confusion matrix
for a fixed deterministic classifier. This observation does not establish
which calculation produced the paper's point. Sensitivity likewise changes in
steps of 1/8 or 1/12 for these refractory denominators.

For the sensitivity side, the binding constraint is the 8 refractory patients.
Exact 95% intervals are about 3.2%-65.1% for 2/8 and about 8.5%-75.5% for 3/8.
The published frozen value, 0.25 = 3/12, would be about 5.5%-57.2% on its own
denominator.

The practical implication is to retain exploratory discrimination and honest
uncertainty as attainable objectives. Repeated folds, bootstrap resamples,
technical replicates or multiple tumors do not create additional independent
patients with which to establish high specificity. These calculations do not
show that the classifier's actual specificity is low.

## Method and best-case sample size

For a classifier and threshold fixed independently of the test outcomes, assume
independent negative patients with common true specificity p. If all n negatives
are correctly classified, the probability of that outcome is p^n. Inverting
this binomial tail gives the exact Clopper–Pearson lower limit:

- One-sided 95%: L = 0.05^(1/n).
- Lower endpoint of a two-sided 95% interval: L = 0.025^(1/n).

The [NIST exact-binomial reference](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm)
was checked on 2026-10-29. “Exact” describes binomial coverage. Floating-point
root evaluation in the tool is numerical. For minimum sample sizes the tool
uses rational arithmetic to check target^n ≤ tail probability and verifies
that n−1 fails the condition.

With **zero false positives**, specificity ≥98% first becomes supportable by
these lower bounds at **149 negative patients** (one-sided 95%) or **183 negative
patients** (two-sided 95%). These are best-case minima, not a powered study
design, recruitment recommendation or assurance of a successful result. False
positives would require larger samples. A future design must specify expected
specificity, power/assurance, target population and evaluation procedure.
The deliberately selected refractory/sensitive cohorts do not establish
population prevalence or transportability.

## Provenance and reproduction

The [aggregate result](../registries/pilot-001-validation-capacity.json) records
source-file SHA-256 hashes, the calculation's implementation hash, counts,
complete specificity grids and assumptions. It contains no patient records,
identifiers, scores, or per-patient hashes.

- The 22/12 published-score counts and candidate total 21 come from
  [the existing supplement audit](../registries/pilot-001-supplement-summary.json),
  `published_score_subsets.Frozen_nonoverlap_pred_scores`.
- The candidate 13/8 class split comes from section 4 of the existing
  [open-questions report](pilot-001-open-questions.md). That split is not present
  in the older aggregate JSON. It is explicitly inherited from the documented
  audit, not reconstructed or independently reverified here.
- The supplement JSON is hash-pinned. The candidate split is checked by an
  exact phrase in section 4 of the open-questions report, so unrelated edits
  to that living report do not stop the calculation, while rewording or
  removing the split does. A changed source stops the calculation rather
  than silently changing the scientific inputs. Future revisions require
  reviewing and deliberately updating the pin or the phrase.

Run from the repository root, using Python's standard library only:

```sh
python3 tools/analyze_validation_capacity.py --check
python3 -m unittest discover -s tests -p test_validation_capacity.py -v
```

To regenerate after a reviewed change:

```sh
python3 tools/analyze_validation_capacity.py > registries/pilot-001-validation-capacity.json
```

Tests check the binomial-tail identity, rational minimality, reference values,
empirical grids, invalid inputs, source-drift refusal and exact agreement with
the retained artifact. They establish the calculation's software and
mathematical contracts, not patient independence, upstream count correctness,
model performance or clinical utility. No AUROC bound, fitted model,
threshold-selection result or new patient-subset metric is asserted here.
