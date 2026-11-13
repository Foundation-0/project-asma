# Subspace-Flag Paraneoplastic Gates, C15 Monoid Collapse, and N=1 Calibration

Date: 2026-11-13
Status: Synthetic mathematical proofs (`PROVEN` in `formal/AsmaSubspaceFlagProofs.lean`) and deterministic replay checks (`VERIFIED` in `tools/verify_subspace_flag_paraneoplastic.py`). Does not claim clinical or study-data validation of open conjectures in `CLAIMS.md`.

## 1. Three Verified Results

1. **C15 / C17 / C18 Three-Pathway De Morgan Monoid Collapse & `2341/30537` (`7.67%`) Bleed Cliff:**
   - Under simultaneous direct selection `r`, indirect `HLA-II`/APC antigen delivery `c1`, and `CDR2`/`CDR2L` (`81.6%` sequence identity) paralog bleed `a2`, observed survival `y(p, r, c1, a2)` collapses onto `q(p, r, c1 + a2 - c1 * a2)` across all `p in [0, 1]`. Pure indirect delivery `(1/4, 0)`, pure paralog bleed `(0, 1/4)`, and coexisting mechanisms `(1/7, 1/8)` yield bitwise identical readouts even at `p = 0`. A 3-stage orthogonal assay flag `V0 < V1 < V2` uniquely recovers `(r = 11, c1 = 1/7, a2 = 1/8)`.
   - Under the `(1/20, 3/8)` optimal low-seed design (`C25` ceiling `10179 / 563920` vs `1 / 60` noise floor), uncompensated `CDR2` paralog bleed preserves `C25` separability iff `a2 < 2341 / 30537` (`~7.6661%`).

2. **C10 / C18 / C19 Multi-Compartment Transitive Regimen Neurotoxicity & Adjoint Flag Gate:**
   - Extending 2-compartment sequence models (`tools/analyze_treatment_sequence.py`) to the 4-channel `(Tumor, APC_TumSafe, APC_ParalogBleed, Purkinje_Injury)` cascade proves that two individually neuro-safe stages (`Delta_1`, `Delta_2`) generate 2-hop transitive Purkinje injury `12 * b0 > 0` under `Delta_2 o Delta_1`. Projecting Stage 1 onto the Composed Adjoint Null-Space Flag (`C10` presenting-context separation) guarantees `0` Purkinje injury across all tumor burdens `b0 > 0` while retaining the full `33%` vs `48%` synergistic tumor clearance.

3. **C02 / C04 / C20 Zero-Shot Prospective `N = 1` Patient Batch-Nullspace Calibration (`p = 64`, `4,316` Pairs):**
   - On isolated prospective `N = 1` evaluations (Gate 0 / `C04`), empirical mid-ranking `(rank - 0.5) / N_k` collapses to `0.5000` AUROC (`0.75289` on `N_k = 27` batches under specimen FFPE block-age subspace drift). Projecting `beta` into `ker(Q_batch^T)` recovers full clean oracle AUROC (`0.83570` vs `0.71668` raw shifted) at `N = 1` with `< 1e-14` logit drift.

## 2. Replay Commands

```bash
lean formal/AsmaSubspaceFlagProofs.lean
python3 tools/verify_subspace_flag_paraneoplastic.py
python3 -m unittest discover -s tests -p "test_subspace_flag_paraneoplastic.py" -v
```
