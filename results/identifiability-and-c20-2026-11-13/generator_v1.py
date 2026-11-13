#!/usr/bin/env python3
"""Reproducible verification suite for compartment identifiability upgrades,
CDR2/CDR2L PGL_2 cross-reactivity gauge equivalence, and Pilot 001 Conjecture C20
5-fold shift-symmetry attenuation.

Research-only verification module (zero third-party dependencies, exact rational
arithmetic via fractions.Fraction + seeded finite-sample simulation).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
from fractions import Fraction
from typing import Dict, List, Tuple


def q_fraction(p: Fraction, r: Fraction, c: Fraction) -> Fraction:
    """Post-assay resistant/target fraction q(p; r, c) = (r*p + c*(1-p)) / (r*p + (1-p))."""
    return (r * p + c * (1 - p)) / (r * p + (1 - p))


def survival_ratio(p: Fraction, r: Fraction, c: Fraction) -> Fraction:
    """Affine survival-ratio linearization Phi(p) = (1 - p) / (1 - q(p; r, c))."""
    q = q_fraction(p, r, c)
    return (1 - p) / (1 - q)


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    lo, hi = -6.0, 6.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def mann_whitney_auc(pos: List[float], neg: List[float]) -> Tuple[float, float]:
    u = 0.0
    for x in pos:
        for y in neg:
            if x > y:
                u += 1.0
            elif x == y:
                u += 0.5
    return u / (len(pos) * len(neg)), u


def verify_compartment_theorems() -> Dict[str, object]:
    worlds = {
        "S":   (Fraction(16, 1), Fraction(0, 1)),
        "C25": (Fraction(11, 1), Fraction(1, 4)),
        "C50": (Fraction(6, 1),  Fraction(1, 2)),
        "C75": (Fraction(1, 1),  Fraction(3, 4)),
    }
    p_ref = Fraction(1, 5)
    for name, (r, c) in worlds.items():
        assert q_fraction(p_ref, r, c) == Fraction(4, 5), f"Snapshot mismatch on {name}"

    # Verify affine survival-ratio linearization Phi(p) = ((r-1)/(1-c))*p + 1/(1-c)
    test_ps = [Fraction(0, 1), Fraction(1, 20), Fraction(1, 10), Fraction(1, 5), Fraction(3, 8), Fraction(2, 5)]
    linearized_lines = {}
    for name, (r, c) in worlds.items():
        slope = (r - 1) / (1 - c)
        intercept = Fraction(1, 1) / (1 - c)
        for p in test_ps:
            assert survival_ratio(p, r, c) == slope * p + intercept
        assert survival_ratio(p_ref, r, c) == Fraction(4, 1)
        linearized_lines[name] = {"slope": str(slope), "intercept": str(intercept)}

    # Verify universal snapshot gap factorization along r(c) = 16 - 20c:
    # q_S(p) - q_c(p) == c*(5p - 1)*(1 - p) / [(15p + 1)*((15 - 20c)p + 1)]
    for c_val in [Fraction(1, 10), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)]:
        r_val = 16 - 20 * c_val
        for p in test_ps:
            lhs = q_fraction(p, Fraction(16, 1), Fraction(0, 1)) - q_fraction(p, r_val, c_val)
            rhs = (c_val * (5 * p - 1) * (1 - p)) / ((15 * p + 1) * ((15 - 20 * c_val) * p + 1))
            assert lhs == rhs

    # Compare PR #78 baseline (1/10, 2/5) vs Opt-Low (1/20, 3/8) vs Cell-Free Anchor (0, 3/8)
    bench_eps = Fraction(1, 60)
    designs = {
        "PR78_LH_1_10_to_2_5": (Fraction(1, 10), Fraction(2, 5)),
        "OptLow_1_20_to_3_8":  (Fraction(1, 20), Fraction(3, 8)),
        "Anchor_0_to_3_8":     (Fraction(0, 1),  Fraction(3, 8)),
    }
    design_certs = {}
    for dname, (pL, pH) in designs.items():
        dS = q_fraction(pH, Fraction(16, 1), Fraction(0, 1)) - q_fraction(pL, Fraction(16, 1), Fraction(0, 1))
        ceilings = {}
        separated = []
        for wname in ["C25", "C50", "C75"]:
            r, c = worlds[wname]
            dW = q_fraction(pH, r, c) - q_fraction(pL, r, c)
            eps_star = abs(dS - dW) / 4
            ceilings[wname] = {
                "exact_fraction": str(eps_star),
                "decimal": round(float(eps_star), 8),
                "exceeds_benchmark_1_60": bool(eps_star > bench_eps),
            }
            if eps_star > bench_eps:
                separated.append(wname)
        design_certs[dname] = {
            "p_L": str(pL),
            "p_H": str(pH),
            "q_S_at_pL_pH": [
                str(q_fraction(pL, Fraction(16, 1), Fraction(0, 1))),
                str(q_fraction(pH, Fraction(16, 1), Fraction(0, 1))),
            ],
            "ceilings": ceilings,
            "worlds_separated_at_eps_1_60": separated,
        }

    assert design_certs["PR78_LH_1_10_to_2_5"]["ceilings"]["C50"]["exact_fraction"] == "13/700"
    assert design_certs["PR78_LH_1_10_to_2_5"]["ceilings"]["C25"]["exact_fraction"] == "3/448"
    assert design_certs["PR78_LH_1_10_to_2_5"]["worlds_separated_at_eps_1_60"] == ["C50", "C75"]
    assert design_certs["OptLow_1_20_to_3_8"]["ceilings"]["C50"]["exact_fraction"] == "9451/213325"
    assert design_certs["OptLow_1_20_to_3_8"]["ceilings"]["C25"]["exact_fraction"] == "10179/563920"
    assert design_certs["OptLow_1_20_to_3_8"]["worlds_separated_at_eps_1_60"] == ["C25", "C50", "C75"]

    p_h_star = (7.0 + 8.0 * math.sqrt(3.0)) / 55.0
    return {
        "snapshot_reference": {"p_R": "1/5", "q_R": "4/5", "pivot_Phi": "4"},
        "linearized_survival_pencil": linearized_lines,
        "universal_gap_formula": "c*(5*p - 1)*(1 - p) / ((15*p + 1)*((15 - 20*c)*p + 1))",
        "global_high_seed_argmax_C50": {
            "closed_form": "(7 + 8*sqrt(3)) / 55",
            "decimal": round(p_h_star, 8),
        },
        "paired_design_comparison": design_certs,
    }


def verify_pgl2_cross_reactivity() -> Dict[str, object]:
    """Verify exact PGL_2 gauge equivalence between true conversion c_true and
    pure selection (c=0) with false-positive paralog channel bleed alpha = c_true,
    plus unique parameter recovery once anchored at p=0 (recombinant paralog control).
    """
    grid_p = [Fraction(k, 20) for k in range(21)]
    checked_pairs = 0
    for c_true in [Fraction(1, 10), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)]:
        r_true = 16 - 20 * c_true
        alpha = c_true
        for p in grid_p:
            q_conv = q_fraction(p, r_true, c_true)
            y_bleed = (1 - alpha) * q_fraction(p, r_true, Fraction(0, 1)) + alpha
            assert q_conv == y_bleed
            checked_pairs += 1

    # Verify unique recovery when alpha is anchored at p=0 (y(0)_control = alpha_known):
    # Given known alpha, beta=0, deflating q_corr(p) = (y(p) - alpha) / (1 - alpha) recovers q(p; r, c),
    # and two distinct mixtures p1 != p2 in (0, 1) uniquely recover (r, c)!
    alpha_known = Fraction(3, 20)  # e.g. 15% residual paralog bleed measured on recombinant standard
    r_true, c_true = Fraction(6, 1), Fraction(1, 2)
    p1, p2 = Fraction(1, 20), Fraction(3, 8)
    y1 = (1 - alpha_known) * q_fraction(p1, r_true, c_true) + alpha_known
    y2 = (1 - alpha_known) * q_fraction(p2, r_true, c_true) + alpha_known
    q1 = (y1 - alpha_known) / (1 - alpha_known)
    q2 = (y2 - alpha_known) / (1 - alpha_known)
    phi1 = (1 - p1) / (1 - q1)
    phi2 = (1 - p2) / (1 - q2)
    slope = (phi2 - phi1) / (p2 - p1)
    intercept = phi1 - slope * p1
    c_rec = 1 - Fraction(1, 1) / intercept
    r_rec = 1 + slope / intercept
    assert (r_rec, c_rec) == (r_true, c_true)

    return {
        "exact_gauge_identity": "(1 - c)*q(p; r, 0) + c == q(p; r, c) for all p in [0, 1]",
        "grid_identities_verified": checked_pairs,
        "anchored_two_point_recovery_verified": {
            "alpha_known": str(alpha_known),
            "true_r_c": [str(r_true), str(c_true)],
            "recovered_r_c": [str(r_rec), str(c_rec)],
        },
    }


def verify_pilot001_c20() -> Dict[str, object]:
    n1, n2 = 52, 83
    total_pairs = n1 * n2
    u_obs = 3491
    auc_pooled = Fraction(u_obs, total_pairs)

    fold_n1 = [11, 11, 10, 10, 10]
    within_counts = {
        "aligned": sum(a * b for a, b in zip(fold_n1, [17, 17, 17, 16, 16])),
        "mixed":   sum(a * b for a, b in zip(fold_n1, [17, 16, 17, 17, 16])),
        "anti":    sum(a * b for a, b in zip(fold_n1, [16, 16, 17, 17, 17])),
    }
    assert within_counts == {"aligned": 864, "mixed": 863, "anti": 862}

    w_in = 863 / 4316.0
    w_cr = 3453 / 4316.0
    target_fold = 0.8300
    target_pool = float(auc_pooled)
    req_cross = (target_pool - w_in * target_fold) / w_cr
    d_prime = math.sqrt(2.0) * norm_ppf(target_fold)
    d_cross = math.sqrt(2.0) * norm_ppf(req_cross)
    rho_exact = math.sqrt((d_prime / d_cross) ** 2 - 1.0)

    rng = random.Random(20261113)
    f2 = [17, 16, 17, 17, 16]
    fold_means, pooled_raws, pooled_cals = [], [], []
    exact_witness = None
    for trial in range(4000):
        f_aucs, pos_raw, neg_raw, pos_cal, neg_cal = [], [], [], [], []
        for k in range(5):
            dk = rng.gauss(0.0, rho_exact)
            pk = [d_prime + rng.gauss(0.0, 1.0) + dk for _ in range(fold_n1[k])]
            nk = [rng.gauss(0.0, 1.0) + dk for _ in range(f2[k])]
            ak, _ = mann_whitney_auc(pk, nk)
            f_aucs.append(ak)
            pos_raw.extend(pk)
            neg_raw.extend(nk)
            comb = sorted(pk + nk)
            m = len(comb)
            pos_cal.extend([(sum(1 for z in comb if z < x) + 0.5 * sum(1 for z in comb if z == x)) / m for x in pk])
            neg_cal.extend([(sum(1 for z in comb if z < y) + 0.5 * sum(1 for z in comb if z == y)) / m for y in nk])
        mf = sum(f_aucs) / 5.0
        pr, ur = mann_whitney_auc(pos_raw, neg_raw)
        pc, _ = mann_whitney_auc(pos_cal, neg_cal)
        fold_means.append(mf)
        pooled_raws.append(pr)
        pooled_cals.append(pc)
        if ur == 3491 and abs(mf - 0.83) < 0.0025 and exact_witness is None:
            exact_witness = {
                "trial_index": trial,
                "fold_mean_auroc": round(mf, 6),
                "pooled_u_concordant": int(ur),
                "pooled_raw_auroc": round(pr, 8),
                "rank_calibrated_pooled_auroc": round(pc, 6),
                "fold_aurocs": [round(v, 4) for v in f_aucs],
            }

    assert exact_witness is not None
    return {
        "cohort_counts": {"n_refractory": n1, "n_sensitive": n2, "total_pairs": total_pairs, "u_observed": u_obs},
        "exact_pooled_auroc_fraction": str(auc_pooled),
        "exact_pooled_auroc_decimal": round(float(auc_pooled), 10),
        "stratified_5fold_within_pairs": within_counts,
        "stratified_5fold_cross_pair_share": round(w_cr, 6),
        "analytical_binormal_shift_solution": {
            "target_5fold_mean_auroc": target_fold,
            "required_cross_fold_auroc": round(req_cross, 6),
            "latent_d_prime": round(d_prime, 6),
            "sigma_delta_over_sigma_s": round(rho_exact, 6),
        },
        "monte_carlo_4000_trials": {
            "seed": 20261113,
            "mean_5fold_auroc": round(sum(fold_means) / len(fold_means), 6),
            "mean_pooled_raw_auroc": round(sum(pooled_raws) / len(pooled_raws), 6),
            "mean_rank_calibrated_pooled_auroc": round(sum(pooled_cals) / len(pooled_cals), 6),
            "constructive_exact_3491_witness": exact_witness,
        },
    }


def main() -> None:
    comp = verify_compartment_theorems()
    pgl2 = verify_pgl2_cross_reactivity()
    c20 = verify_pilot001_c20()
    payload = {
        "schema": "foundation-0.project-asma.identifiability-and-c20-certificates.v1",
        "date": "2026-11-13",
        "epistemic_scope": "Deterministic rational algebra + seeded finite-sample simulation (research-only; zero patient data ingested).",
        "compartment_identifiability": comp,
        "cdr2_cdr2l_pgl2_gauge": pgl2,
        "pilot001_c20_shift_attenuation": c20,
    }
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "identifiability_and_c20_certificates.json")
    raw = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(raw)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    print(f"OK: all assertions passed -> {out_path} (SHA-256: {digest})")


if __name__ == "__main__":
    main()
