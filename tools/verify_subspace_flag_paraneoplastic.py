"""Verifier for Subspace-Flag Paraneoplastic Gates, C15 Monoid Collapse, and N=1 FFPE Calibration."""

from __future__ import annotations

import hashlib
import json
import math
import random
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple


def survival_three_pathway(p: Fraction, r: Fraction, c1: Fraction, a2: Fraction) -> Fraction:
    one = Fraction(1, 1)
    q_inner = (r * p + c1 * (one - p)) / (r * p + (one - p))
    return (one - a2) * q_inner + a2


def demorgan_combine(c1: Fraction, a2: Fraction) -> Fraction:
    return c1 + a2 - c1 * a2


def recover_three_pathway_via_flag(
    y_v0_apc_free_p0: Fraction,
    y_v1_apc_intact_p0: Fraction,
    p_interior: Fraction,
    y_v2_interior: Fraction,
) -> Tuple[Fraction, Fraction, Fraction]:
    one = Fraction(1, 1)
    a2 = y_v0_apc_free_p0
    if a2 >= one:
        raise ValueError("paralog bleed saturates dynamic range (a2 >= 1)")
    c1 = (y_v1_apc_intact_p0 - a2) / (one - a2)
    if c1 >= one:
        raise ValueError("indirect conversion saturates dynamic range (c1 >= 1)")
    phi_p = (one - p_interior) / (one - y_v2_interior)
    scale = (one - c1) * (one - a2)
    r_minus_1 = (phi_p * scale - one) / p_interior
    return (r_minus_1 + one, c1, a2)


def verify_c15_monoid_and_flag() -> Dict[str, object]:
    r_true = Fraction(11, 1)
    worlds = {
        "W_indirect_only": (Fraction(1, 4), Fraction(0, 1)),
        "W_paralog_only": (Fraction(0, 1), Fraction(1, 4)),
        "W_coexisting_both": (Fraction(1, 7), Fraction(1, 8)),
    }
    grid = [
        Fraction(0, 1),
        Fraction(1, 20),
        Fraction(1, 10),
        Fraction(1, 5),
        Fraction(3, 8),
        Fraction(2, 5),
        Fraction(3, 4),
        Fraction(1, 1),
    ]

    ref_curve = [survival_three_pathway(p, r_true, Fraction(1, 4), Fraction(0, 1)) for p in grid]
    for name, (c1, a2) in worlds.items():
        if demorgan_combine(c1, a2) != Fraction(1, 4):
            raise AssertionError(f"monoid mismatch in {name}")
        curve = [survival_three_pathway(p, r_true, c1, a2) for p in grid]
        if curve != ref_curve:
            raise AssertionError(f"curve mismatch in {name}")

    c1_co, a2_co = worlds["W_coexisting_both"]
    y_v0 = survival_three_pathway(Fraction(0, 1), r_true, Fraction(0, 1), a2_co)
    y_v1 = survival_three_pathway(Fraction(0, 1), r_true, c1_co, a2_co)
    p_int = Fraction(3, 8)
    y_v2 = survival_three_pathway(p_int, r_true, c1_co, a2_co)
    rec_r, rec_c1, rec_a2 = recover_three_pathway_via_flag(y_v0, y_v1, p_int, y_v2)
    assert (rec_r, rec_c1, rec_a2) == (r_true, c1_co, a2_co)

    c25_opt_ceiling = Fraction(10179, 563920)
    noise_floor = Fraction(1, 60)
    alpha_crit = Fraction(1, 1) - noise_floor / c25_opt_ceiling
    assert alpha_crit == Fraction(2341, 30537)
    assert (Fraction(1, 1) - Fraction(2340, 30537)) * c25_opt_ceiling > noise_floor
    assert (Fraction(1, 1) - Fraction(2341, 30537)) * c25_opt_ceiling == noise_floor
    assert (Fraction(1, 1) - Fraction(2342, 30537)) * c25_opt_ceiling < noise_floor

    return {
        "monoid_collision_worlds_verified": 3,
        "recovered_coexisting_world": [str(rec_r), str(rec_c1), str(rec_a2)],
        "c25_critical_paralog_bleed_fraction": f"{alpha_crit.numerator}/{alpha_crit.denominator}",
        "c25_critical_paralog_bleed_pct": round(float(alpha_crit) * 100.0, 4),
    }


def mat_vec_int(mat: Sequence[Sequence[int]], vec: Sequence[int]) -> List[int]:
    return [sum(r[j] * vec[j] for j in range(len(vec))) for r in mat]


def mat_add_id_int(delta: Sequence[Sequence[int]], scale_id: int = 1) -> List[List[int]]:
    n = len(delta)
    return [[delta[i][j] + (scale_id if i == j else 0) for j in range(n)] for i in range(n)]


def verify_paraneoplastic_cascade_gate() -> Dict[str, object]:
    scale = 10
    delta1_ungated = [
        [-4, 0, 0, 0],
        [3, 0, 0, 0],
        [3, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    delta2 = [
        [-2, -5, 0, 0],
        [0, 2, 0, 0],
        [0, 0, 2, 0],
        [0, 0, 4, 0],
    ]
    m1_ungated = mat_add_id_int(delta1_ungated, scale)
    m2 = mat_add_id_int(delta2, scale)

    delta1_gated = [
        [-4, 0, 0, 0],
        [3, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    m1_gated = mat_add_id_int(delta1_gated, scale)

    for b0 in (50, 100, 240):
        x0 = [b0, 0, 0, 0]
        s1_only = mat_vec_int(m1_ungated, x0)
        assert s1_only[3] == 0
        s2_only = mat_vec_int(m2, x0)
        assert s2_only[3] == 0
        rev_state = mat_vec_int(m1_ungated, mat_vec_int(m2, x0))
        assert rev_state[3] == 0
        fwd_ungated = mat_vec_int(m2, mat_vec_int(m1_ungated, x0))
        assert fwd_ungated[3] == 12 * b0
        fwd_gated = mat_vec_int(m2, mat_vec_int(m1_gated, x0))
        assert fwd_gated[3] == 0
        assert fwd_gated[0] == fwd_ungated[0] == 33 * b0
        assert fwd_gated[0] < rev_state[0] == 48 * b0

    return {
        "residual_tumor_pct_reversed": 48.0,
        "residual_tumor_pct_forward_ungated": 33.0,
        "residual_tumor_pct_forward_adjoint_gated": 33.0,
        "purkinje_injury_single_stage_1": 0,
        "purkinje_injury_single_stage_2": 0,
        "purkinje_injury_forward_ungated_at_b100": 1200,
        "purkinje_injury_forward_adjoint_gated_at_b100": 0,
    }


def dot_f(u: Sequence[float], v: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(u, v))


def gram_schmidt_columns(cols: Sequence[Sequence[float]], tol: float = 1e-12) -> List[List[float]]:
    basis: List[List[float]] = []
    for c in cols:
        v = list(c)
        for _ in range(2):
            for q in basis:
                proj = dot_f(v, q)
                v = [vj - proj * qj for vj, qj in zip(v, q)]
        nrm = math.sqrt(dot_f(v, v))
        if nrm > tol:
            basis.append([vj / nrm for vj in v])
    return basis


def exact_auroc(scores: Sequence[float], labels: Sequence[int]) -> float:
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    wins = 0.0
    for sp in pos:
        for sn in neg:
            if sp > sn + 1e-15:
                wins += 1.0
            elif abs(sp - sn) <= 1e-15:
                wins += 0.5
    return wins / float(len(pos) * len(neg))


def midrank_normalize(fold_scores: Sequence[float]) -> List[float]:
    n = len(fold_scores)
    indexed = sorted(enumerate(fold_scores), key=lambda x: x[1])
    out = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(indexed[j + 1][1] - indexed[i][1]) <= 1e-15:
            j += 1
        avg_rank = 0.5 * (i + j) + 1.0
        val = (avg_rank - 0.5) / float(n)
        for m in range(i, j + 1):
            out[indexed[m][0]] = val
        i = j + 1
    return out


def verify_prospective_n1_batch_nullspace(n_reps: int = 24) -> Dict[str, float | int]:
    p_dim = 64
    n_ref, n_sens = 52, 83
    labels = [1] * n_ref + [0] * n_sens
    folds = [0] * len(labels)
    for idx in range(n_ref):
        folds[idx] = idx % 5
    for idx in range(n_sens):
        folds[n_ref + idx] = idx % 5

    within_pairs = sum(
        1 for i in range(n_ref) for j in range(n_sens) if folds[i] == folds[n_ref + j]
    )
    cross_pairs = (n_ref * n_sens) - within_pairs
    assert n_ref * n_sens == 4316
    assert 862 <= within_pairs <= 864
    assert 3452 <= cross_pairs <= 3454

    aucs_clean: List[float] = []
    aucs_raw_pooled: List[float] = []
    aucs_midrank_batch27: List[float] = []
    aucs_midrank_prospective_n1: List[float] = []
    aucs_nullgate_prospective_n1: List[float] = []
    max_logit_drift_nullgate = 0.0

    for rep in range(n_reps):
        rng = random.Random(20261113 + rep * 97)
        raw_vecs = [[rng.gauss(0.0, 1.0) for _ in range(p_dim)] for _ in range(5)]
        ortho = gram_schmidt_columns(raw_vecs)
        u_bio = ortho[0]
        q_batch = ortho[1:5]

        leak_weights = [0.68, -0.58, 0.52, -0.46]
        beta_hat = [
            1.35 * u_bio[d] + sum(lw * qb[d] for lw, qb in zip(leak_weights, q_batch)) + rng.gauss(0.0, 0.03)
            for d in range(p_dim)
        ]

        qc_probes: List[List[float]] = []
        for _ in range(12):
            w_qc = [rng.gauss(0.0, 1.0) for _ in range(4)]
            qc_probes.append([sum(w_qc[m] * q_batch[m][d] for m in range(4)) for d in range(p_dim)])
        q_est = gram_schmidt_columns(qc_probes)[:4]

        beta_perp = list(beta_hat)
        for _ in range(2):
            for q in q_est:
                pr = dot_f(beta_perp, q)
                beta_perp = [b - pr * qd for b, qd in zip(beta_perp, q)]

        fold_offsets = [[rng.gauss(0.0, 1.35) for _ in range(4)] for _ in range(5)]

        scores_clean: List[float] = []
        scores_raw: List[float] = []
        scores_null_n1: List[float] = []

        for idx, y in enumerate(labels):
            f_id = folds[idx]
            z_bio = (0.76 if y == 1 else -0.76) + rng.gauss(0.0, 1.0)
            x_clean = [z_bio * u_bio[d] + rng.gauss(0.0, 0.30) for d in range(p_dim)]

            specimen_ffpe = [fold_offsets[f_id][m] + rng.gauss(0.0, 1.15) for m in range(4)]
            x_shifted = [
                x_clean[d] + sum(specimen_ffpe[m] * q_batch[m][d] for m in range(4))
                for d in range(p_dim)
            ]

            s_clean_i = dot_f(x_clean, beta_perp)
            s_raw_i = dot_f(x_shifted, beta_hat)
            s_null_i = dot_f(x_shifted, beta_perp)
            max_logit_drift_nullgate = max(max_logit_drift_nullgate, abs(s_null_i - s_clean_i))

            scores_clean.append(s_clean_i)
            scores_raw.append(s_raw_i)
            scores_null_n1.append(s_null_i)

        scores_mid_batch = [0.0] * len(labels)
        for f_id in range(5):
            f_indices = [i for i, f in enumerate(folds) if f == f_id]
            normed = midrank_normalize([scores_raw[i] for i in f_indices])
            for loc, glob_i in enumerate(f_indices):
                scores_mid_batch[glob_i] = normed[loc]

        scores_mid_n1 = [midrank_normalize([s])[0] for s in scores_raw]

        aucs_clean.append(exact_auroc(scores_clean, labels))
        aucs_raw_pooled.append(exact_auroc(scores_raw, labels))
        aucs_midrank_batch27.append(exact_auroc(scores_mid_batch, labels))
        aucs_midrank_prospective_n1.append(exact_auroc(scores_mid_n1, labels))
        aucs_nullgate_prospective_n1.append(exact_auroc(scores_null_n1, labels))

    def mean(xs: Sequence[float]) -> float:
        return round(sum(xs) / float(len(xs)), 5)

    return {
        "n_patients": len(labels),
        "p_features": p_dim,
        "total_pairs": n_ref * n_sens,
        "within_fold_pairs": within_pairs,
        "cross_fold_pairs": cross_pairs,
        "auroc_clean_oracle_mean": mean(aucs_clean),
        "auroc_raw_pooled_shifted_mean": mean(aucs_raw_pooled),
        "auroc_midrank_batch27_mean": mean(aucs_midrank_batch27),
        "auroc_midrank_prospective_n1_mean": mean(aucs_midrank_prospective_n1),
        "auroc_nullspace_gate_prospective_n1_mean": mean(aucs_nullgate_prospective_n1),
        "max_logit_drift_under_batch_shift": round(max_logit_drift_nullgate, 14),
    }


def run_all_verifications() -> Dict[str, object]:
    res = {
        "c15_monoid_and_flag": verify_c15_monoid_and_flag(),
        "c10_c19_paraneoplastic_cascade_gate": verify_paraneoplastic_cascade_gate(),
        "c20_prospective_n1_batch_nullspace": verify_prospective_n1_batch_nullspace(),
    }
    digest = hashlib.sha256(json.dumps(res, sort_keys=True).encode("utf-8")).hexdigest()
    res["verification_sha256"] = digest
    return res


if __name__ == "__main__":
    summary = run_all_verifications()
    print(json.dumps(summary, indent=2, sort_keys=True))
