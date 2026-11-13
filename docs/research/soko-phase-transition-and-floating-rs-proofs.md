# Soko Phase-Transition & Floating-Selection Proofs for Synthetic Asma Discriminators

**Scope & Governance:** Purely synthetic, offline mathematical research scaffolding (`study_data_bytes = 0`, `patient_data_rows = 0`). Makes zero clinical claims or clinical decision recommendations.

## Verified Mathematical Results

1. **Floating-Selection (`r_S = 19`) Continuum Impossibility & Exact Remedies (`PROVEN`):**
   - Against externally pinned pure selection `S(16, 0)`, shifting `(1/10, 2/5)` ([PR #78](https://github.com/Foundation-0/project-asma/pull/78)) to `(1/20, 3/8)` ([Issue #82](https://github.com/Foundation-0/project-asma/issues/82)) raises the uniform `LH` separation against `C25(11, 1/4)` from `3/448` to `10179/563920` (`0.01805 > 1/60`).
   - When pure selection's fitness ratio `r_S > 0` floats, the integer witness `r_S = 19` satisfies `q(p; 19, 0) - q(p; 11, 1/4) = (14p - 1)(1 - p) / (4(18p + 1)(10p + 1))`, which equals `-1/40` at `p = 1/20` (half-gap `1/80 < 1/60`), crosses zero at `p = 1/14`, and remains strictly within `+-1/30` across all `p in [1/20, 1]` because `2(18p + 1)(10p + 1) - 15(14p - 1)(1 - p) = 570p^2 - 169p + 17 > 0` (`Delta = -10199 < 0`).
   - **Remedy A:** Pairing `p_0 = 1/5` (`r_S <= 20` at `eps = 1/60`) with `p_low` satisfying `125p^2 + 328p - 13 < 0` (`p_low <= 1/26`; `p = 1/25` fails at `+8/25`, `p = 1/26` succeeds at `-135/676`) restores single-channel separation across all `r_S > 0`.
   - **Remedy B:** Pairing `(1/20, 3/8)` with newly converted survivor fraction `u(p; r, c) = c(1 - p) / (rp + 1 - p)` ([PR #86](https://github.com/Foundation-0/project-asma/pull/86)) certifies an `r_S`-invariant Farkas minimax margin of `19/240` (`4.75x` above `1/60`).

2. **Turn-End Crushing-Gate Phase Transition (`P04`, `VERIFIED`):**
   - Replaces sticky safety with turn-end scaffold-quorum re-evaluation ([ahrazzle/soko PR #42](https://github.com/ahrazzle/soko/pull/42)), separating false sticky shortcuts (`3` steps at `w = 2`; `4` steps under clonal monotherapy) from certified wall-transmuting schedules (`0` Bellman violations).

3. **Causal Complementary-Rung Conservation & Parent-Gated Non-Stuttering CNF (`P01+`, `VERIFIED`):**
   - Breaks `11/11` static bipartite Dinic ties down to `11/11` vs. `8/11` on synthetic internal dipeptide-swap chimeras while retaining `0` peak-intensity bytes ([Issue #71](https://github.com/Foundation-0/project-asma/issues/71)).
