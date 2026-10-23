# Pilot 001: published discovery-score verification

**Version:** 0.1, 2026-10-23. **Status:** prepared for scientific review; no live
prediction-score calculation executed. This is a proposed narrower step within
[Pilot 001](pilot-001.md), not approval to bypass its review requirements.

## Question and scope

Do the supplied discovery prediction scores, linked to the supplied clinical
labels, yield an empirical AUROC consistent with the reported Figure 3D value
of 0.83? This checks the arithmetic of published predictions. It does not
regenerate predictions, reproduce feature selection/model fitting/repeated
cross-validation, or establish that the supplied scores are the exact original
out-of-fold predictions.

The full reproduction still requires the missing author workspaces/helper,
execution environment and transformation history. Frozen-cohort independence
and the corrected-supplement version remain unresolved. This proposal neither
changes the published groups nor treats the frozen cohort as independent.

## Source-fixed analysis contract

The source article is [Chowdhury et al., Cell 2023](https://doi.org/10.1016/j.cell.2023.07.004),
reviewed through [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10414761/fullTextXML).
Section S12, “A protein panel predictive of refractoriness,” reports discovery
CV AUC **0.83** and 95% CI **0.77–0.90**. S99, “Prediction Performance
Evaluation,” specifies 83 sensitive and 52 refractory tumors and fivefold CV.
These are published reference values, not Project Asma results.

S95, “Prediction Model Building,” describes the output as “a score between 0
and 1, indicating the probability of the tumor to be refractory.” Accordingly,
the proposed fixed direction is **refractory positive; higher score predicts
refractory**. A related author script encodes sensitive as 1, so this direction
requires explicit review against the specific supplement. No outcome-driven
direction selection or automatic AUC reversal is permitted. A disagreement must
remain a discrepancy until supported by independent source clarification.

| Contract | Fixed value |
| --- | --- |
| Prediction source | `NIHMS1918576-supplement-MMC4.xlsx`, `FFPE_pred_scores!A1:B136`, headers `Samples`, `Pred.scores` |
| Clinical source | `NIHMS1918576-supplement-MMC1.xlsx`, `FFPE_Discovery_clinical` |
| Exact join | Prediction `Samples` equals clinical `Data Label 2 <data set>_<TMTplex>_<sample source>_<patient ID>_sample ID>`; no normalization or substring matching |
| Identity | Explicit clinical `Patient ID` and `Sample ID`; each unique within the score cohort |
| Denominator | 135 score rows: 52 refractory positives and 83 sensitive negatives; 4,316 positive–negative pairs |
| Membership | Preserve the published discovery score set; verify equality with the previously audited literal no-neoadjuvant/non-`Mix` reconstruction |
| Missingness | Preserve and report the one retained discovery record with location group `NA`; do not infer nonmixed tissue or complete clinical eligibility |
| Metric | Empirical AUROC: fraction of positive–negative score pairs correctly ordered, with half credit for ties; independently cross-check with rank sums |
| Primary display comparison | Report the full calculated value, difference from 0.83, and whether decimal `ROUND_HALF_UP` to two places, calculated from the exact AUROC fraction, gives 0.83 |
| Existing proposed tolerance | Separately report whether absolute difference from 0.83 is ≤0.02; this is the model-reproduction protocol's proposed tolerance, not proof that the displayed statistic was recovered |
| Uncertainty | Do not calculate or claim reproduction of the published confidence interval; bootstrap details and the code/method discrepancy are unresolved |
| Excluded work | No other cohort metrics, thresholds, calibration, subgroup searches, model fitting, or repeated-CV reconstruction |

No averaging of AUCs or multiplication of the denominator by 100 is involved.
The inspected author script averages predictions per entry across repeats before
computing the ROC. The supplied final scores do not establish repeat completion,
fold assignments, patient grouping during training, or absence of leakage.

## Inputs, provenance and execution

The public source is the [documented NLM distribution](https://pmc-oa-opendata.s3.amazonaws.com/README.txt)
for [PMC10414761.1](https://pmc-oa-opendata.s3.amazonaws.com/PMC10414761.1/PMC10414761.1.json).
The [prior input report](../docs/pilot-001-input-resolution.md) and
[aggregate supplement audit](../registries/pilot-001-supplement-summary.json)
record rights review, exact joins and their limitations. These article supplements
have CC BY-NC-ND 4.0 metadata, distinct from PDC's terms; no full workbook or
patient-level output is redistributed.

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| [Clinical workbook MMC1](https://pmc-oa-opendata.s3.us-east-1.amazonaws.com/PMC10414761.1/NIHMS1918576-supplement-MMC1.xlsx) | 41,194,360 | `6e46fa0cb3023173a3643e95ce0360c44cfabb0ed737e9a05f70473dad552340` |
| [Panel/prediction workbook MMC4](https://pmc-oa-opendata.s3.us-east-1.amazonaws.com/PMC10414761.1/NIHMS1918576-supplement-MMC4.xlsx) | 591,065 | `f318ed9d2fac341097a8b1be3e034753f6d427bdeeb0cd2b92eb715cadadb6ab` |

The independent implementation is [verify_published_auc.py](../tools/verify_published_auc.py).
It uses Python's standard library and the reviewed source-loading/join helpers;
it does not execute author code. The prepared environment is CPython **3.12.14**
on Linux x86_64. There are no third-party package dependencies. The calculation
is deterministic, so a random seed is not applicable. Run output records the
actual Python/OS, source and implementation hashes, protocol hash, UTC time and
elapsed time. A later environment change must be recorded rather than represented
as the original author's environment.

After the scientific review below is recorded, the intended command is:

```sh
python3 tools/verify_published_auc.py > /tmp/asma-score-verification.json
```

Workbooks, identifiers, labels and prediction rows remain in process memory.
Only aggregate statistics/provenance may reach standard output or the result
file. Errors must omit source rows and remote response bodies. Inspect the
aggregate artifact before adding it to this public repository.

Stop without an output result on changed hashes/sizes, missing/ambiguous joins,
duplicate identity, unexpected categories, invalid/nonfinite/out-of-range scores,
changed denominator/class counts/membership, or disagreement between the two
AUROC calculations. Numeric disagreement with the published value is a valid
reported finding, not grounds to change direction, exclusions, or inputs.

## Review record and remaining execution gate

The user has authorized reproduction work. That authorization does not by itself
record the scientific review the user asked to preserve. The project's
[data rules](../docs/reproducibility-and-data.md#rights-and-publication) require:
“Obtain scientific review before such work advances beyond this research
scaffold.” The [roadmap](../docs/roadmap.md) also calls for collaborator review;
the pilot identifies a gynecologic oncologist and a proteomics/biostatistics
collaborator for its feasibility decision. Agent source/code checks are not a
substitute for that human review.

**Current outcome:** pending; no human reviewer or approval evidence is recorded
in this proposal. PR #2 had no submitted reviews at the 2026-10-23 check. No live
score calculation is claimed or stored. An existing review supplied by the owner
can satisfy the applicable requirement if it covers this narrowed scope and the
applicable protocol version; a duplicate approval is unnecessary.

The reviewer should record a name/role or suitable review reference, date,
protocol version/commit and disposition for these concrete questions:

1. Is this narrower arithmetic check appropriate while original model inputs,
   corrected-legend status and out-of-fold provenance remain unresolved?
2. Is refractory-positive/higher-score direction supported for this particular
   score sheet, and are the denominator, missing-location handling and two
   comparison criteria appropriate?
3. Are the scoped public-source use, transient processing and aggregate output
   appropriate under the project's data requirements?
4. Does the implementation correctly calculate this statistic without expanding
   it into a claim of independent validation, full reproduction or clinical use?

If approved, append the review evidence and execute the fixed command. Record
agreement or failure with the exact version and deviations. If not approved,
record the unresolved points; do not manufacture replacement records or declare
Gate 2 complete. A successful point-score check alone would not close Gate 2's
full model-reproduction requirements.

## Author clarification

The [prepared author request](../templates/pilot-001-source-request.md) was
authorized on 2026-10-23. Both the connected GitHub tool and the existing CLI
connection rejected posting to the [upstream issue](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/issues/1)
with “Resource not accessible by integration.” No comment was created. The
exact approved message remains available for an account with posting access.
Score orientation is also a review question if the current sources cannot settle
it; no additional message has been sent.
