# Exact `PGL(2)` Möbius Cross-Ratio Invariant & Optimal Spectral-Inertia Rank Bound (`R_opt`)

**Status:** Independently **`VERIFIED`** (`AUDIT-002` `N2` core `R_opt`, `AUDIT-006R` `VERIFIED`) — 100% zero-float exact rational (`fractions.Fraction`, pure Python 3 stdlib, zero external dependencies).

## Summary of Exact Results

[`optimal_inertia_rank.py`](./optimal_inertia_rank.py) provides two zero-float exact-rational instruments directly applicable to `Foundation-0/project-asma`:

1. **Parameter-Free `PGL(2)` Möbius Cross-Ratio Invariant (Check 10, Portal 11):**
   - In `formal/AsmaIdentifiabilityProofs.lean`, the two-compartment observation map
     $$q(p; r, c) = \frac{r p + c(1 - p)}{r p + (1 - p)}$$
     is a non-degenerate $PGL(2)$ Möbius transformation ($\det = r(1-c) \ne 0$) with **universal fixed point $q(1; r, c) \equiv 1$**.
   - Therefore, **without fitting either nuisance parameter $(r, c)$**:
     - The **4-point cross-ratio** $\mathrm{CR}_4(q_1, q_2; q_3, q_4) \equiv \mathrm{CR}_4(p_1, p_2; p_3, p_4)$ (`9/7` on seeds `(1/20, 1/10, 1/5, 2/5)`), and
     - The **3-point fixed-point cross-ratio** $\mathrm{CR}_3(q_1, q_2; q_3, 1) \equiv \mathrm{CR}_3(p_1, p_2; p_3, 1)$ (`27/19` on `(1/20, 1/10, 1/5)`)
     are **exact invariants across all four canonical Lean worlds** (`S = (16, 0)`, `C25 = (11, 1/4)`, `C50 = (6, 1/2)`, `C75 = (1, 3/4)`) and every rational $(r > 0, c < 1)$.
   - **Negative Control:** A non-Möbius density-dependent / 3-compartment yield $r(p) = 6 + 10p$ breaks both invariants identically (`1431/1133 != 9/7`), giving a 100% parameter-free model-class falsifier.

2. **Scale-Invariant Optimal Spectral-Inertia Rank Bound `R_opt` & Trace-Slack Sensitivity Law (Checks 1–9):**
   - For any symmetric rational $M = P + Q$ ($P \succeq 0$, $n_+(Q) \le b$ certified via exact block-$LDL^\top$ congruence over $\mathbb{Q}$, $W = \operatorname{range}(Q_+)$), the closed-form rational bound
     $$R_{\mathrm{opt}} = \begin{cases} \dfrac{(t_M - t_-)^2}{S - t_-^2 / b} & \text{if } b > 0,\; t_- > 0,\; b t_M > t_- \text{ and } b S > t_-^2, \\ \max\!\left(0, \dfrac{t_M^2}{S} - b\right) & \text{otherwise} \end{cases}$$
     provably lower-bounds $\operatorname{rank}(\Pi_{W^\perp} P \Pi_{W^\perp}) \le \operatorname{rank}(P)$ (`1000/1000` random non-commuting matrices & `200/200` Portal 1 novel-subspace trials, `0` violations), is strictly invariant under global scaling and orthogonal conjugation, and strictly dominates fixed-$c$ and `loom#7` $R_G$ bounds via exact algebraic square identities.
   - **Trace-Slack Amplification Law (Check 4):** On a 3-component `project-asma` chimeric Gram matrix (`w_1 = 9/10` backbone + two `1/20` chimeric species) under unknown PSD noise $0 \preceq N \preceq \tau I_5$, the exact critical slack threshold is $\Delta t^* = \|P\|_F^2 / (2 t) = 1/360$. Below threshold ($\tau = 1/5000$), $R_{\mathrm{opt}} = 1.530561 > 1$ **uniquely certifies $\operatorname{rank}(P_{\mathrm{chim}}) \ge 2$** while Mode A (`0.226`), Session 2 `c=2` (`0.424`), and `loom` $R_G$ (`0.184`) all fail (single-chimeric negative control rejected).
   - **Hardened R3/R4 TCB:** Strict canonical lowest-terms ASCII rational parser + fail-closed exact matrix type/shape guards (`7/7` built-in adversarial forgeries rejected; `23/23` + `6/6` independent verifier forgeries blocked in `AUDIT-006R`).

## Reproduction

```bash
python3 -I -O -B -W error studies/expedition-mobius-ropt/optimal_inertia_rank.py
python3 -I -O -B -W error studies/expedition-mobius-ropt/optimal_inertia_rank.py --json
```
