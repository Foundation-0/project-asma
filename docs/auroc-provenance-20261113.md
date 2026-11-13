# Discovery AUROC provenance, 2026-11-13

**Evidence class:** one KNOWN reading of the public article, figure, and pinned
script, and one VERIFIED arithmetic check of the public discovery score sheet.
No model was refit. No patient-level file is stored. External scientific review
is pending. This page separates **discrimination** from **clinical utility**.

**Credits:** Chowdhury et al., *Cell* 2023
(https://doi.org/10.1016/j.cell.2023.07.004), the NLM-released workbooks named
below, and the pinned Wang Lab script at commit `48357fd`. The 2024 correction
is https://doi.org/10.1016/j.cell.2024.01.016.

**Claim labels:** **K44** (where 0.83 and n=135 are printed), **K45** (the plot
annotation is a literal string), **V44** (the sheet AUROC and its interval),
**C26** (the unrounded cross-validation value is still unpublished). Earlier
rows V08, V23, K01, and C20 stay in the ledger. K07 is the class counts, not
the AUROC.

## What each number is

| Number | Where it comes from | Cohort, marker, comparison, split |
| --- | --- | --- |
| **0.83** (95% CI 0.77–0.90) | Printed once in the article, paragraph **P33**, section titled “A protein panel predictive of refractoriness” | FFPE discovery proteomic data. 64-protein ensemble of elastic net, random forest, and XGBoost. Five-fold cross-validation. Refractory versus sensitive. |
| **AUC = 0.83** and **n=135** | Printed on Figure 3, the panel marked 3. The caption calls that panel D3. The caption does not restate 0.83 | Same discovery ROC. The image also prints n=135 under the AUC. |
| **0.79, n=34** | Same figure, frozen validation, non-overlap | A different cohort. |
| **0.81, n=27** | Same figure, frozen validation, overlap | A different cohort. This is the paper’s printed 0.81. |
| **0.91, n=20** | Same figure, FFPE validation | A different cohort. The methods say this one used three-fold cross-validation. |
| **0.8088507877664504** | This repository, from the public sheet `FFPE_pred_scores` joined to `FFPE_Discovery_clinical` | 135 rows: 52 refractory and 83 sensitive. 3,491 concordant pairs out of 4,316. Higher score means refractory. The article XML does not contain this decimal. |
| **0.81** as a rounding | Half-up of 3,491/4,316 to two decimals | The sheet value. It is the same two-character string as the frozen-overlap AUC above, and it is a different comparison. |
| **0.809** | Half-up of 3,491/4,316 to three decimals | The code-audit addendum’s “0.809” is this rounding. |

Paragraph P33’s sentence, copied from the Europe PMC XML read on 2026-11-13, is:

> We evaluated performance of the prediction model through 5-fold cross validation (CV) using the FFPE discovery cohort proteomic data. The ROC of the ensemble prediction models evaluated on the CV sets showed an AUC of 0.83 (95% CI: 0.77–0.90) (Figures 3D3).

The XML writes the cross-reference as “Figures 3D3”. The JATS record places the article at *Cell* **186**(16):3476–3498.e35. The Figure 3 JPEG comment string says 3476-3498.e36. Paragraph P33 has no page number of its own in the author-manuscript XML.

STAR Methods paragraph **P177** and paragraph **P183** both say “83 sensitive and 52 refractory HGSOC tumors”. Their sum is 135. The article’s AUC sentence does not print the numeral 135. The figure does. Paragraph **P179** defines the score as the probability that the tumour is refractory. Paragraph **P183** says the 95% confidence intervals for the AUCs were calculated by a bootstrap. The pinned script calls `roc(..., ci = TRUE)`, which is a DeLong interval in the pROC default this repository already recorded. Those two interval procedures are different descriptions. This check does not decide which procedure produced the printed 0.77–0.90.

The 2024 correction text does not contain “AUC” or “0.83”. It says the supplemental figure legends were corrected. Figure 3 is a main-text figure.

## The plot label is typed, and the sheet value is calculated

At commit `48357fd63ccbfe3954f38c8efc558b4f88bd6051`, `Figure_3D_part3.R` line 184 draws the literal string `AUC = 0.83`. The line does not read `roc.all1` and does not round it. Earlier in the same file, `roc.all1` is the ROC of the simple mean of the three model probabilities, averaged within each row across 100 repetitions, with `ci = TRUE`. A search of the 42 R and Rmd files in that commit found no `n=135`. The sample size on the published figure is an image label.

The public workbooks are the inputs to the sheet calculation. Their SHA-256 values are in the count block. The workbooks were read in memory on 2026-11-13 and were not stored. Two readers, pair counting and average ranks, agree.

<!-- BEGIN GENERATED AUROC PROVENANCE -->
sheet_n: 135
refractory: 52
sensitive: 83
pairs: 4316
concordant: 3491
discordant: 825
tied: 0
pair_auc: 3491/4316
rank_auc: 3491/4316
half_up_2dp: 0.81
half_up_3dp: 0.809
printed_discovery_auc: 0.83
two_decimal_half_up_equals_printed: false
absolute_difference: 1141/53950
difference_exceeds_0_02: true
delong_95: 0.7347956138 0.8829059617
bootstrap_95: 0.7309951344 0.8760484245
bootstrap_seed: 20261113
bootstrap_resamples: 2000
mmc1_sha256: 6e46fa0cb3023173a3643e95ce0360c44cfabb0ed737e9a05f70473dad552340
mmc4_sha256: f318ed9d2fac341097a8b1be3e034753f6d427bdeeb0cd2b92eb715cadadb6ab
discrimination_only: true
clinical_utility: false
clinical_guidance: false
<!-- END GENERATED AUROC PROVENANCE -->

The DeLong 95% interval and the stratified bootstrap 95% percentile interval both contain the printed 0.83. An interval that contains 0.83 describes uncertainty around 3,491/4,316. It does not make the point estimate equal to 0.83.

## Adjudication

**0.83 is the printed five-fold cross-validation AUC.** It is on the page once and on the discovery panel of Figure 3 with n=135. **0.8088507877664504 is the AUROC of the released discovery score sheet.** Half-up rounding of that fraction to two decimals is 0.81. The printed 0.83 and the sheet AUROC are different displayed values. The public script does not produce 0.83 by rounding `roc.all1`. The unrounded cross-validation number is not in the article, the workbooks, or the pinned scripts, so this record does not call 0.83 a misquote of 0.80885. Whether the released sheet is the vector drawn in Figure 3D remains the open question already labelled C20, and C26 states the remaining gap.

## Discrimination and clinical utility

An AUROC summarizes how the scores rank the two classes. It does not say how many refractory tumours would be found at a threshold a clinician could use, and it does not say whether using the score would help or harm anyone. The same paragraph prints a separate operating point: sensitivity 0.35 (95% CI 0.19–0.52) at 98% specificity. That operating point was not recomputed here. Neither number is clinical utility, a treatment rule, or a statement about an individual tumour.

## Repository occurrences

A fresh scan for the tokens `0.80885` and a standalone `0.83` is frozen in
[occurrences.json](../results/auroc-provenance-20261113/occurrences.json).
The site pages and the coordinate assets do not contain either token. The
integrity-audit JSON repeats ledger sentences and is omitted from that scan so
the checker can regenerate it.

Citations corrected in this result:

- K07’s citation had been read by the ledger exporter as registry sources S95 and S99. Those registry records are different documents. The class counts are paragraphs P177 and P183 (S174).
- The 11 November extract called the sheet AUROC check K07. K07 is the class-count row. The AUROC rows are V08, V23, and V44.
- The code-audit addendum’s 0.809 is the three-decimal half-up of 3,491/4,316.
- The score-verification protocol’s “S12”, “S95”, and “S99” are Europe PMC XML section ids. They are not registry source ids.

The sent source-request draft says the released-score AUROC is 0.81 beside Figure 3D’s 0.83. That 0.81 is the two-decimal half-up of the sheet fraction. The draft was left unchanged because it is the text that was sent.

## What this check cannot re-do offline

The offline command replays the frozen fractions, the DeLong formula from the
frozen variance components, and the bootstrap percentile from the frozen
numerators. It does not download the workbooks, re-open the figure, or recover
`roc.all1`’s unrounded value. Recomputing from the workbooks requires the
public files and the command below. Fold identifiers are not in the public
sheet, so a mean of fold-wise AUCs cannot be calculated here.

```sh
python3 results/auroc-provenance-20261113/recompute.py
python3 results/auroc-provenance-20261113/verify.py
```

## AI assistance

This note, the checker, and the certificate were written by a Cursor cloud
agent (**Grok 4.7**) under human direction. Claim labels describe what was
checked. No AI system is a legal author of patient-facing guidance.
