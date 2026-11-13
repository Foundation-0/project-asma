# Compartment Optimal-Seed Bounds, Paralog Gauge Equivalence, and Pilot 001 Fold-Shift Analysis

Date: 2026-11-13
Scope: Research-only mathematical and statistical analysis. Certificate: `results/identifiability-and-c20-2026-11-13/identifiability_and_c20_certificates.json`. Zero patient records ingested.

## Summary

Status: gem-nexus presents this note, its certificate, and the explorer as an identifiability and C20 bridge. That presentation is an unreproduced Carbon claim, pending independent review. Its exact values are recorded in the certificate above. The Lean module and the certificate tools for these results landed through #87, which superseded #83 and is merged to `main` as `bae1a84` (head `6259ef29`). This note cites no proof from #87. This note adds no `CLAIMS.md` row, and `C20` stays a CONJECTURE.

This note records three deterministic results for open problems in `CLAIMS.md`, `docs/compartment-identifiability.md`, `docs/cdr2-cdr2l-evidence-atlas-2026-11-13.md`, and `docs/pilot-001-auc-discrepancy.md`.

1. **Paired mixture design `(L = 1/20, H = 3/8)` separates `C25`, `C50`, and `C75` at benchmark error `eps = 1/60` (exact rational values in the certificate; unreproduced):** Keeping the two-observation budget and offset bound `|b| <= 1/20` from `#78`, diluting the low seed from `1/10` to `1/20` and setting the high seed to `3/8` lifts the `C50` error ceiling from `13/700` (`0.01857`) to `9451/213325` (`0.04430`, `2.39x`) and lifts the `C25` error ceiling from `3/448` (`0.00670`) to `10179/563920` (`0.01805 > 1/60 = 0.01667`).
2. **Paralog channel bleed forms an exact rational curve match with phenotypic conversion unless anchored at `p = 0` (exact rational identity in the certificate; unreproduced):** When an assay with false-positive bleed `alpha` reads a pure-selection population `(c = 0, r)`, setting `alpha = c_true` produces the identical post-assay fraction `(1 - c_true) * q(p; r, 0) + c_true = q(p; r, c_true)` at every input mixture `p` in `[0, 1]`. Measuring `alpha` on a cell-free or recombinant paralog control (`p = 0`) removes this ambiguity and restores two-point recovery of `(r, c)`.
3. **Fold-local intercept shifts explain how a `0.83` five-fold mean AUROC coexists with `3491/4316 = 0.80885` pooled AUROC (pair-count algebra in the certificate + `CONJECTURE C20`):** Across all stratified five-fold splits of `52` refractory and `83` sensitive samples (`4,316` pairs), within-fold pairs make up `862..864` pairs (`20.0%`) and cross-fold pairs make up `3,452..3,454` pairs (`80.0%`). Within-fold concordance does not change when a constant intercept `delta_k` shifts fold `k`, whereas cross-fold pairs lose concordance when `delta_k` varies across folds (`sigma_delta / sigma_s = 0.497` maps `0.830` within-fold AUROC to `0.80885` pooled AUROC). Converting each fold's predictions to within-fold mid-rank percentiles before pooling removes additive fold shifts.

## 1. Universal Snapshot Factorization and Survival-Ratio Linearization

Under `q(p; r, c) = (r*p + c*(1 - p)) / (r*p + (1 - p))`, every parameter pair matching the single-timepoint observation `q(1/5) = 4/5` lies on the line `r(c) = 16 - 20*c`. Subtracting any conversion world `q_c(p)` on this line from pure selection `q_S(p) = 16*p / (15*p + 1)` gives the exact rational identity:

```text
q_S(p) - q_c(p) = c * (5*p - 1) * (1 - p) / ((15*p + 1) * ((15 - 20*c)*p + 1))
```

Above `p = 1/5` the gap against `C50` (`c = 1/2`, denominator factors `15*p + 1` and `5*p + 1`) is positive and reaches its maximum on `[1/5, 1]` at `p_H* = (7 + 8*sqrt(3)) / 55 = 0.37920739`. There the denominator factors are `6.688` and `2.896`, and `q_S - q_C50 = 0.014359` (compared with `1/70 = 0.014286` at `p = 2/5`). Below `p = 1/5`, both denominator factors shrink toward `1`, so moving `p_L` from `1/10` (`gap = -3/50 = -0.0600`) to `1/20` (`gap = -57/350 = -0.1629`) more than doubles the paired difference.

Defining the survival ratio `Phi(p) = (1 - p) / (1 - q(p; r, c))` linearizes every trajectory with `c < 1`:

```text
Phi(p) = ((r - 1) / (1 - c)) * p + 1 / (1 - c)
```

All four worlds in `docs/compartment-identifiability.md` (`S`, `C25`, `C50`, `C75`) pass through `(p = 1/5, Phi = 4)` as straight lines with vertical intercepts `1`, `4/3`, `2`, and `4`.

| Design `(p_L, p_H)` | `eps*` vs `C25` | `eps*` vs `C50` | `eps*` vs `C75` | Separated at `eps = 1/60` (`0.01667`) |
| :--- | :--- | :--- | :--- | :--- |
| `(1/10, 2/5)` (`#78` baseline) | `3/448` (`0.00670`) | `13/700` (`0.01857`) | `279/5600` (`0.04982`) | `C50`, `C75` |
| `(1/20, 3/8)` (diluted low seed) | `10179/563920` (`0.01805`) | `9451/213325` (`0.04430`) | `21801/237440` (`0.09182`) | `C25`, `C50`, `C75` |
| `(0, 3/8)` (negative control + `3/8`) | `2049/32224` (`0.06359`) | `627/4876` (`0.12859`) | `1377/6784` (`0.20298`) | `C25`, `C50`, `C75` |

## 2. Paralog Cross-Reactivity (`CDR2` / `CDR2L`) and `p = 0` Anchoring

For a paralog pair such as `CDR2` (Q01850) and `CDR2L` (Q86X02) (protein records in `docs/cdr2-cdr2l-evidence-atlas-2026-11-13.md`), an unanchored readout with false-positive bleed `alpha` and false-negative loss `beta` observes `y(p) = (1 - alpha - beta) * q(p; r, c) + alpha`. Because fractional linear maps are closed under affine output mixing, `y(p)` has only three observable curve coefficients for four unknowns `(r, c, alpha, beta)`. At `beta = 0` and `alpha = c_true`, pure selection `(c = 0)` reproduces `q(p; r, c_true)` at every `p` in `[0, 1]`. Measuring `alpha` on an isolated recombinant standard at `p = 0` fixes the offset channel and restores exact recovery of `(r, c)` from two non-zero mixtures.

## 3. Pilot 001 Conjecture `C20` (`0.80885` vs `0.83`)

On the public `FFPE_pred_scores` cohort (`n_1 = 52`, `n_2 = 83`, `U = 3,491`, exact pooled AUROC `3491/4316 = 0.80885079`), stratified five-fold splits place `80.0%` of all cross-class pairs across distinct folds. When feature scaling and model intercepts are estimated inside each training fold, fold-specific additive offsets leave within-fold AUROC unchanged while attenuating cross-fold concordance. Across `4,000` seeded trials (`seed = 20261113`, `d' = 1.349393`, `sigma_delta / sigma_s = 0.497088`), five-fold mean AUROC averages `0.8289`, raw pooled AUROC averages `0.8078` (including constructive witness trial `2718` with exact `U = 3,491` and five-fold mean `0.8310`), and within-fold mid-rank percentile pooling recovers `0.8287`.

## Checking the certificate

```bash
cd results/identifiability-and-c20-2026-11-13 && sha256sum -c SHA256SUMS
```

This checks the certificate bytes only. Recomputing the certificate uses `tools/generate_identifiability_certificate_v1.py` and `tools/check_identifiability_certificate_v1.py`, which reached `main` with #87 (merged as `bae1a84`, head `6259ef29`). Neither tool is a passed proof.
