# Pilot 001: discovery AUROC discrepancy analysis

**Evidence class:** executed arithmetic and interval analysis of **public**
released discovery predictions. No model refit. No private `asma-data`. External
scientific review remains pending.

**Credits:** Chowdhury et al., *Cell* 2023
(https://doi.org/10.1016/j.cell.2023.07.004) and the NLM-released MMC4 workbook
sheet `FFPE_pred_scores`. Prior baseline arithmetic:
[score verification result](pilot-001-score-verification-result.md).

**Claim labels** follow [CLAIMS.md](../CLAIMS.md) and [CONTRIBUTING.md](../CONTRIBUTING.md).
Ledger IDs for this analysis: **V23** (VERIFIED candidates (a)–(e) on released scores) and **C20** (CONJECTURE leading open explanation).

## Baseline (VERIFIED)

On the pinned public workbooks, the fixed-direction Mann–Whitney AUROC with
half-credit for exact ties is:

| Quantity | Value | Label |
| --- | --- | --- |
| Concordant / discordant / tied pairs | 3491 / 825 / **0** | VERIFIED |
| Exact AUROC | 3491 / 4316 = 0.8088507878 | VERIFIED |
| Printed discovery fivefold-CV figure | 0.83 (95% CI 0.77–0.90) | KNOWN (Chowdhury et al.) |
| Absolute difference \|0.80885 − 0.83\| | 0.02115 (> 0.02 tolerance) | VERIFIED |

Command (network; aggregates only):

```sh
python3 tools/analyze_auc_discrepancy.py
python3 tools/analyze_auc_discrepancy.py --write-registry
```

Offline unit coverage of the arithmetic helpers:

```sh
python3 -m unittest tests.test_auc_discrepancy -v
```

The committed aggregate artifact is
[registries/pilot-001-auc-discrepancy.json](../registries/pilot-001-auc-discrepancy.json)
(with `artifact_sha256`=`76ed00504f78064c2a4f4476bae3c3b9d4e75520ca081cc7c59f2c501d588206` and `implementation_sha256`).

## Candidate explanations

Each candidate was measured as specified. **Nothing was tuned toward 0.83.**

| ID | Candidate | Result | Label | Explains 0.83? |
| --- | --- | --- | --- | --- |
| (a) | Tie handling at full released precision; AUC with ties as 0, ½, 1 | Exact cross-class ties = **0**. Discordant pairs = 825 (not ties). With zero ties, AUC under tie credit 0 / ½ / 1 is identical: **0.8088507878**. | VERIFIED | No |
| (b) | Label coding / polarity; join exclusions or relabels | Paper direction (higher = refractory) **0.80885**; reversed **0.19115**. Response-NA, neoadjuvant=yes, and Mix-location exclusions match the audited membership rule; no ambiguous categories were relabelled into the 135-row join; duplicate prediction keys = 0. | VERIFIED | No |
| (c) | Rounding of released scores; bounds over tie resolutions | Source strings already carry high fractional precision. Artificial rounding at 1–8 decimal places creates cross-class ties; half-credit AUC stays near 0.80885 at ≥2 dp. Coarse 1-dp bounds can numerically contain 0.83 under adversarial tie resolution, which is **not** evidence the sheet was rounded that way. | VERIFIED | No (not supported as the cause) |
| (d) | AUC estimator (Mann–Whitney vs trapezoidal; binormal; fold-mean; bootstrap mean/median) | Mann–Whitney half-tie **equals** trapezoidal (exact) at 0.8088507878. Python binormal MLE ≈ 0.802747 (not pROC). Bootstrap mean/median stay near the point estimate. **Mean of fold-wise AUCs vs pooled OOF AUC: not testable** from public material. | VERIFIED (estimators); CONJECTURE (fold-mean) | Not established; fold-mean remains open |
| (e) | DeLong CI and stratified bootstrap CI (≥2000, fixed seed); is 0.83 inside? | DeLong 95% CI [0.7348, 0.8829] contains 0.83: **True**. Stratified bootstrap (n=2000, seed=20261105) 95% CI [0.7329, 0.8802] contains 0.83: **True**. Bootstrap mean/median ≈ 0.808187/0.809082. CI containment ≠ point-estimate agreement. | VERIFIED | No (intervals describe uncertainty, not a 0.83 point) |

Detailed numeric fields for (a)–(e) live in the registry JSON; this document does
not restate every float so the checker remains the single source of truth.

## What public material cannot test (stated plainly)

| Item | Label | Why |
| --- | --- | --- |
| Released scores ≡ averaged out-of-fold Figure 3D predictions | CONJECTURE | No fold IDs, OOF prediction matrix, or fitted model object in the public workbooks. |
| Mean of fold-wise AUCs vs pooled OOF AUC | CONJECTURE | The paper’s 0.83 is a fivefold-CV summary; fold assignments are not released. |
| Author `pROC::roc(..., smooth=TRUE)` binormal/density ROC | CONJECTURE | R/pROC is outside this stdlib checker; a Python binormal MLE is reported instead and is not claimed identical. |
| Exact CI procedure used for the printed 0.77–0.90 interval on the original predictions | KNOWN conflict in sources; unresolved on original scores | Paper text cites bootstrap (S99); pinned author `roc(ci=TRUE)` defaults to DeLong. Both are recomputed here only on the released sheet. |

## Interpretation

**VERIFIED (V23):** the released-score point AUROC is 3491/4316 ≈ 0.80885, not 0.83.
Candidates (a), (b), and ordinary precision rounding do not close the gap.
Estimator choice between Mann–Whitney and trapezoidal does not close it.
Confidence intervals on the released scores may or may not contain 0.83; that
does not change the point estimate.

**CONJECTURE (C20, leading open explanation):** the printed 0.83 is a fivefold-CV
summary (possibly a mean of fold-wise AUCs, or computed on predictions that are
not identical to the released `FFPE_pred_scores` sheet). Public material cannot
confirm or reject that without fold-level or model-object provenance.

This analysis does **not** establish an error in Chowdhury et al., *Cell* 2023.

## AI assistance

This document, checker, tests, and registry were written by **grk-axiom**, an AI
agent operated for **Foundation-0**, under human direction. Claim labels describe
what was checked, not clinical meaning. No AI system is a legal author of
patient-facing guidance.
