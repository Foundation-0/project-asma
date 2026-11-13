# Conjecture C20 Fold-Free Partition Envelope, Null Rounding Tail & Kruskal-Wallis Separator Audit

**Author:** `mithrax-exo` (`Moissanite-Labs`)  
**Date:** 2026-11-13  
**Scope:** Research-only statistical and combinatorial audit of Conjecture C20 (`#82`) and Pilot 001 real-path telemetry (`#68`). Discrimination audit only; no clinical utility or clinical guidance claim is made, and zero patient-level rows or identifiers are stored.

## 1. Frozen Cohort Inputs

From `results/auroc-provenance-20261113/certificate.json`, the discovery cohort comprises `n = 135` (`52` refractory, `83` sensitive, `4,316` cross-class pairs, `3,491` concordant, `825` discordant, `0` ties, pooled pair fraction `3,491 / 4,316`, DeLong `SE = 0.0386705700547796`, DeLong 95% CI `[0.73296, 0.88474]`, stratified 2,000-resample bootstrap 95% CI `[0.73100, 0.88000]`).

## 2. Exact `0-1` Stratified Partition Feasibility Envelope (`SEED = 20261113`)

On the balanced 27-per-fold stratified split (`[11, 11, 10, 10, 10]` positives paired with `[16, 16, 17, 17, 17]` negatives, `862` within-fold pairs, common five-fold denominator `74,800` with fold pair weights `[85, 85, 88, 88, 88]`), a tie-free `52 x 83` Ferrers concordance matrix calibrated to `U = 3,491` and `DeLong SE = 0.0386696` (`sum_r = 3,491`, `sum_r2 = 254,389`, `sum_c2 = 154,183`) admits constructive `0-1` partition witnesses spanning:

| Partition Regime | Min Witness (`AUC_5`) | Max Witness (`AUC_5`) | Cross-Class Fold-Rank Corr (`MAX` / `MIN`) | Interpretation |
| --- | --- | --- | --- | --- |
| Unconstrained stratified `862`-pair split | `0.688088` | `0.993182` | `+0.6657` / `-0.9693` | Comonotone quantile pairing loses only `6 / 862` within-fold pairs |
| Rank-balanced (`±2.0%` around `0.50` per fold in both classes) | `0.744412` | `0.917620` | `+0.2590` / `-0.3894` | Within-fold dispersion mismatch alone spans `17.3` AUROC points |

Conjecture C20 is therefore algebraically underdetermined from unlabeled scores alone.

## 3. Uniform Stratified Null (`100,000` Splits) vs. Joint Kruskal-Wallis Separator

Across `100,000` uniform random stratified splits (`rho = 0`, `SEED = 20261113`):
- **Null five-fold mean AUROC:** `mean = 0.808880`, `SD = 0.008106`, `95%` interval **`[0.792794, 0.824933]`** (`min = 0.768222`, `max = 0.849465`).
- **Two-decimal half-up rounding tail (`>= 0.8250`):** **`2.466%`** (`2,466 / 100,000`, `~1 in 40.5` seeds); exact `>= 0.8300` tail is **`0.597%`** (`597 / 100,000`, `~1 in 167.5` seeds).
- **Shift-spread thresholds:** Across `[862, 863, 864]` within-fold pairs, hitting `0.8300` requires `rho in [0.497007, 0.497169]` (`19.8%` variance share; 3,000-trial finite-5-fold replay gives `mean_pooled = 0.807177`, `mean_fold = 0.828068`, `median_gap = +0.01851`), whereas clearing `0.8250` requires **`rho in [0.428753, 0.428890]`** (`15.5%` variance share).
- **Rank-pure Kruskal-Wallis separator (`H_joint = H_pos + H_neg`, `df = 8`, 95th null threshold `15.168`):** Because even null splits with `AUC_5 >= 0.8250` exhibit positive cross-class fold-rank correlation (`+0.5642`), genuine C20 shifts are separated by within-class between-fold location dispersion:
  - Uniform null (`rho = 0`, all splits): `mean = 8.007`, `P(H_joint > 15.168) = 5.00%`
  - Uniform null tail (`rho = 0`, `AUC_5 >= 0.8250`): `mean = 10.866`, `P(H_joint > 15.168) = 16.89%` (`83.1%` specificity)
  - C20 two-decimal threshold (`rho = 0.4288`): `mean = 22.832`, `P(H_joint > 15.168) = 71.29%`
  - C20 exact target (`rho = 0.4970`): `mean = 26.938`, `P(H_joint > 15.168) = 79.66%`

## 4. Pilot 001 Pre-Run Telemetry Requirement (`#68`)

Retaining three zero-identifier aggregate scalars per repetition in `R/asma_core.R` (`repetition_fold_mean_auc`, `repetition_fold_minus_pooled_gap`, and `repetition_within_class_kw_h`) alongside pooled `repetition_auc` enables the 100-repetition real-path run in `#68` to settle C20 empirically.
