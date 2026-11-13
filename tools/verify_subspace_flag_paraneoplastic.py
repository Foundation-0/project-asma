"""Comprehensive Pure-Stdlib Verifier Across Five Project Asma Research Paths."""

from __future__ import annotations

import hashlib
import json
import math
import random
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

CDR2L_Q86X02 = (
    "MRRAAGMEDFSAEEEESWYDQQDLEQDLHLAAELGKTLLERNKELEGSLQQMYSTNEEQV"
    "QEIEYLTKQLDTLRHVNEQHAKVYEQLDLTARDLELTNHRLVLESKAAQQKIHGLTETIE"
    "RLQAQVEELQAQVEQLRGLEQLRVLREKRERRRTIHTFPCLKELCTSPRCKDAFRLHSSS"
    "LELGPRPLEQENERLQTLVGALRSQVSQERQRKERAEREYTAVLQEYSELERQLCEMEAC"
    "RLRVQELEAELLELQQMKQAKTYLLGPDDHLAEALLAPLTQAPEADDPQPGRGDDLGAQD"
    "GVSSPAASPGHVVRKSCSDTALNAIVAKDPASRHAGNLTLHANSVRKRGMSILREVDEQY"
    "HALLEKYEELLSKCRQHGAGVRHAGVQTSRPISRDSSWRDLRGGEEGQGEVKAGEKSLSQ"
    "HVEAVDKRLEQSQPEYKALFKEIFSRIQKTKADINATKVKTHSSK"
)

CDR2_Q01850 = (
    "MLAENLVEEFEMKEDEPWYDHQDLQQDLQLAAELGKTLLDRNTELEDSVQQMYTTNQEQL"
    "QEIEYLTKQVELLRQMNEQHAKVYEQLDVTARELEETNQKLVADSKASQQKILSLTETIE"
    "CLQTNIDHLQSQVEELKSSGQGRRSPGKCDQEKPAPSFACLKELYDLRQHFVYDHVFAEK"
    "ITSLQGQPSPDEEENEHLKKTVTMLQAQLSLERQKRVTMEEEYGLVLKENSELEQQLGAT"
    "GAYRARALELEAEVAEMRQMLQSEHPFVNGVEKLVPDSLYVPFKEPSQSLLEEMFLTVPE"
    "SHRKPLKRSSSETILSSLAGSDIVKGHEETCIRRAKAVKQRGISLLHEVDTQYSALKVKY"
    "EELLKKCQEEQDSLSHKAVQTSRAAAKDLTGVNAQSEPVASGWELASVNPEPVSSPTTPP"
    "EYKALFKEIFSCIKKTKQEIDEQRTKYRSLSSHS"
)

MONO_AA_MASS = {
    "A": 71.03711, "R": 156.10111, "N": 114.04293, "D": 115.02694, "C": 103.00919,
    "E": 129.04259, "Q": 128.05858, "G": 57.02146, "H": 137.05891, "I": 113.08406,
    "L": 113.08406, "K": 128.09496, "M": 131.04049, "F": 147.06841, "P": 97.05276,
    "S": 87.03203, "T": 101.04768, "W": 186.07931, "Y": 163.06333, "V": 99.06841,
}


def verify_cdr2l_mhc2_core_bifurcation() -> Dict[str, object]:
    assert len(CDR2L_Q86X02) == 465
    assert len(CDR2_Q01850) == 454
    assert hashlib.md5(CDR2L_Q86X02.encode("ascii")).hexdigest().upper() == "03593414DBB55B4A7F44D99B348723F3"
    assert hashlib.md5(CDR2_Q01850.encode("ascii")).hexdigest().upper() == "CCD9FF24C811DAD3EB3D1007AC803946"

    ep1 = CDR2L_Q86X02[431:446]
    ep2 = CDR2L_Q86X02[444:464]
    assert ep1 == "SQPEYKALFKEIFSR"
    assert ep2 == "SRIQKTKADINATKVKTHSS"

    cdr2_12mers = {CDR2_Q01850[j : j + 12] for j in range(len(CDR2_Q01850) - 11)}
    shared_12mers = [CDR2L_Q86X02[i : i + 12] for i in range(len(CDR2L_Q86X02) - 11) if CDR2L_Q86X02[i : i + 12] in cdr2_12mers]
    assert shared_12mers == ["NEQHAKVYEQLD", "PEYKALFKEIFS"]

    def best_9mer_match(core9: str) -> int:
        return max(
            sum(a == b for a, b in zip(core9, CDR2_Q01850[j : j + 9]))
            for j in range(len(CDR2_Q01850) - 8)
        )

    ep1_cores = [best_9mer_match(ep1[k : k + 9]) for k in range(len(ep1) - 8)]
    ep2_cores = [best_9mer_match(ep2[k : k + 9]) for k in range(len(ep2) - 8)]
    assert ep1_cores.count(9) == 4
    assert max(ep2_cores) == 5

    y1_cdr2l_arg = round(MONO_AA_MASS["R"] + 18.01056 + 1.00728, 5)
    y1_cdr2_cys = round(MONO_AA_MASS["C"] + 18.01056 + 1.00728, 5)
    assert abs((y1_cdr2l_arg - y1_cdr2_cys) - 53.09192) < 1e-4

    p_pf27644 = Fraction(34, 451) * Fraction(29, 446)
    assert p_pf27644 == Fraction(493, 100573)

    return {
        "cdr2l_432_446_peptide": ep1,
        "cdr2l_445_464_peptide": ep2,
        "shared_12mer_islands_proteome_wide": shared_12mers,
        "ep1_exact_9_of_9_cdr2_cores": ep1_cores.count(9),
        "ep2_max_9mer_identity_with_cdr2": max(ep2_cores),
        "pf27644_dual_localization_prob": f"{p_pf27644.numerator}/{p_pf27644.denominator}",
        "diagnostic_y1_arg446_vs_cys436_delta_da": round(y1_cdr2l_arg - y1_cdr2_cys, 5),
    }


def survival_q(p: Fraction, r: Fraction, c: Fraction) -> Fraction:
    one = Fraction(1, 1)
    return (r * p + c * (one - p)) / (r * p + (one - p))


def survival_three_pathway(p: Fraction, r: Fraction, c1: Fraction, a2: Fraction) -> Fraction:
    one = Fraction(1, 1)
    return (one - a2) * survival_q(p, r, c1) + a2


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
    c1 = (y_v1_apc_intact_p0 - a2) / (one - a2)
    phi_p = (one - p_interior) / (one - y_v2_interior)
    scale = (one - c1) * (one - a2)
    r_minus_1 = (phi_p * scale - one) / p_interior
    return (r_minus_1 + one, c1, a2)


def pairwise_offset_sep_bound(
    p_low: Fraction,
    p_high: Fraction,
    w1: Tuple[Fraction, Fraction],
    w2: Tuple[Fraction, Fraction],
    offset_cap: Fraction = Fraction(1, 20),
) -> Fraction:
    d_low = survival_q(p_low, w1[0], w1[1]) - survival_q(p_low, w2[0], w2[1])
    d_high = survival_q(p_high, w1[0], w1[1]) - survival_q(p_high, w2[0], w2[1])
    db = (d_low + d_high) / 2
    two_b = 2 * offset_cap
    if db > two_b:
        db = two_b
    elif db < -two_b:
        db = -two_b
    return max(abs(d_low - db), abs(d_high - db)) / 2


def verify_c15_monoid_and_offset_saturation() -> Dict[str, object]:
    r_true = Fraction(11, 1)
    worlds_c15 = [
        (Fraction(1, 4), Fraction(0, 1)),
        (Fraction(0, 1), Fraction(1, 4)),
        (Fraction(1, 7), Fraction(1, 8)),
    ]
    grid = [Fraction(0, 1), Fraction(1, 20), Fraction(1, 10), Fraction(1, 5), Fraction(3, 8), Fraction(2, 5), Fraction(3, 4), Fraction(1, 1)]
    ref = [survival_three_pathway(p, r_true, Fraction(1, 4), Fraction(0, 1)) for p in grid]
    for c1, a2 in worlds_c15:
        assert demorgan_combine(c1, a2) == Fraction(1, 4)
        assert [survival_three_pathway(p, r_true, c1, a2) for p in grid] == ref

    rec = recover_three_pathway_via_flag(
        survival_three_pathway(Fraction(0, 1), r_true, Fraction(0, 1), Fraction(1, 8)),
        survival_three_pathway(Fraction(0, 1), r_true, Fraction(1, 7), Fraction(1, 8)),
        Fraction(3, 8),
        survival_three_pathway(Fraction(3, 8), r_true, Fraction(1, 7), Fraction(1, 8)),
    )
    assert rec == (Fraction(11, 1), Fraction(1, 7), Fraction(1, 8))

    snap_worlds = [
        (Fraction(16, 1), Fraction(0, 1)),
        (Fraction(11, 1), Fraction(1, 4)),
        (Fraction(6, 1), Fraction(1, 2)),
        (Fraction(1, 1), Fraction(3, 4)),
    ]

    def all4_min(p_l: Fraction, p_h: Fraction) -> Fraction:
        return min(
            pairwise_offset_sep_bound(p_l, p_h, snap_worlds[i], snap_worlds[j])
            for i in range(4)
            for j in range(i + 1, 4)
        )

    b_pr78 = all4_min(Fraction(1, 10), Fraction(2, 5))
    b_pr83 = all4_min(Fraction(1, 20), Fraction(3, 8))
    b_2pct = all4_min(Fraction(1, 50), Fraction(3, 8))
    b_1pct = all4_min(Fraction(1, 100), Fraction(1, 3))
    b_zero = all4_min(Fraction(0, 1), Fraction(2, 7))
    assert b_pr78 == Fraction(3, 448)
    assert b_pr83 == Fraction(10179, 563920)
    assert b_2pct == Fraction(152579, 4189120)
    assert b_1pct == Fraction(20467, 430560)
    assert b_zero == Fraction(3, 40)

    noise = Fraction(1, 60)
    alpha_crit_pr83 = Fraction(1, 1) - noise / b_pr83
    alpha_crit_2pct = Fraction(1, 1) - noise / b_2pct
    alpha_crit_zero = Fraction(1, 1) - noise / b_zero
    assert alpha_crit_pr83 == Fraction(2341, 30537)
    assert alpha_crit_zero == Fraction(7, 9)

    return {
        "monoid_collision_worlds_verified": 3,
        "recovered_coexisting_world": [str(rec[0]), str(rec[1]), str(rec[2])],
        "c25_critical_paralog_bleed_fraction": f"{alpha_crit_pr83.numerator}/{alpha_crit_pr83.denominator}",
        "all4_bound_pr78_lh": str(b_pr78),
        "all4_bound_pr83_5pct": str(b_pr83),
        "all4_bound_2pct_seed": str(b_2pct),
        "all4_bound_1pct_seed": str(b_1pct),
        "all4_bound_0pct_supremum": str(b_zero),
        "bleed_tol_2pct_pct": round(float(alpha_crit_2pct) * 100.0, 2),
        "bleed_tol_0pct_pct": round(float(alpha_crit_zero) * 100.0, 2),
    }


def verify_soko_ilp_minimal_assays() -> Dict[str, object]:
    assays = [
        ("A0_Bulk_LH", [1, 1, 1, 0, 0, 1]),
        ("A1_APC_Free_p0_CDR2", [0, 0, 1, 0, 0, 0]),
        ("A2_APC_Intact_p0", [0, 1, 1, 0, 0, 0]),
        ("A3_Orth_445_464_Tetramer", [1, 1, 0, 1, 0, 0]),
        ("A4_Paired_CSF_Blood_TCR", [0, 0, 0, 1, 0, 0]),
        ("A5_QC_NullSpace_Audit", [0, 0, 0, 0, 0, 1]),
    ]
    valid_by_size: Dict[int, List[List[str]]] = {}
    for mask in range(1, 1 << len(assays)):
        picked = [assays[i] for i in range(len(assays)) if (mask >> i) & 1]
        sigs = {tuple(a[1][w] for a in picked) for w in range(6)}
        if len(sigs) == 6:
            valid_by_size.setdefault(len(picked), []).append([a[0] for a in picked])
    min_k = min(valid_by_size)
    assert min_k == 3
    assert 1 not in valid_by_size and 2 not in valid_by_size
    return {
        "minimal_assay_cardinality": min_k,
        "optimal_three_assay_sets": valid_by_size[min_k],
    }


def mat_vec_int(mat: Sequence[Sequence[int]], vec: Sequence[int]) -> List[int]:
    return [sum(r[j] * vec[j] for j in range(len(vec))) for r in mat]


def mat_add_id_int(delta: Sequence[Sequence[int]], scale_id: int = 1) -> List[List[int]]:
    n = len(delta)
    return [[delta[i][j] + (scale_id if i == j else 0) for j in range(n)] for i in range(n)]


def verify_paraneoplastic_cascade_gate() -> Dict[str, object]:
    scale = 10
    delta1_ungated = [[-4, 0, 0, 0], [3, 0, 0, 0], [3, 0, 0, 0], [0, 0, 0, 0]]
    delta2 = [[-2, -5, 0, 0], [0, 2, 0, 0], [0, 0, 2, 0], [0, 0, 4, 0]]
    delta1_gated = [[-4, 0, 0, 0], [3, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    m1_u = mat_add_id_int(delta1_ungated, scale)
    m2 = mat_add_id_int(delta2, scale)
    m1_g = mat_add_id_int(delta1_gated, scale)

    for b0 in (50, 100, 240):
        x0 = [b0, 0, 0, 0]
        assert mat_vec_int(m1_u, x0)[3] == 0
        assert mat_vec_int(m2, x0)[3] == 0
        rev = mat_vec_int(m1_u, mat_vec_int(m2, x0))
        fwd_u = mat_vec_int(m2, mat_vec_int(m1_u, x0))
        fwd_g = mat_vec_int(m2, mat_vec_int(m1_g, x0))
        assert rev[3] == 0 and rev[0] == 48 * b0
        assert fwd_u[3] == 12 * b0 and fwd_u[0] == 33 * b0
        assert fwd_g[3] == 0 and fwd_g[0] == 33 * b0

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


def exact_mann_whitney_wins(scores: Sequence[float], labels: Sequence[int]) -> float:
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    wins = 0.0
    for sp in pos:
        for sn in neg:
            if sp > sn + 1e-15:
                wins += 1.0
            elif abs(sp - sn) <= 1e-15:
                wins += 0.5
    return wins


def midrank_normalize(fold_scores: Sequence[float]) -> List[float]:
    n = len(fold_scores)
    indexed = sorted(enumerate(fold_scores), key=lambda x: x[1])
    out = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(indexed[j + 1][1] - indexed[i][1]) <= 1e-15:
            j += 1
        val = (0.5 * (i + j) + 0.5) / float(n)
        for m in range(i, j + 1):
            out[indexed[m][0]] = val
        i = j + 1
    return out


def exact_c22_mann_whitney_distribution() -> Tuple[Fraction, Fraction]:
    dp: Dict[Tuple[int, int], Dict[int, int]] = {(0, 0): {0: 1}}
    for _ in range(21):
        ndp: Dict[Tuple[int, int], Dict[int, int]] = {}
        for (i, j), umap in dp.items():
            if j < 8:
                tgt = ndp.setdefault((i, j + 1), {})
                for u, c in umap.items():
                    tgt[u] = tgt.get(u, 0) + c
            if i < 13:
                tgt = ndp.setdefault((i + 1, j), {})
                for u, c in umap.items():
                    tgt[u + j] = tgt.get(u + j, 0) + c
        dp = ndp
    dist = dp[(13, 8)]
    tot = sum(dist.values())
    assert tot == 203490
    p_ge_76 = Fraction(sum(c for u, c in dist.items() if u >= 76), tot)
    p_ge_75 = Fraction(sum(c for u, c in dist.items() if u >= 75), tot)
    assert p_ge_76 == Fraction(302, 6783)
    assert p_ge_75 == Fraction(10601, 203490)
    return p_ge_76, p_ge_75


def verify_prospective_n1_and_c22_power(n_reps: int = 24, c22_trials: int = 400) -> Dict[str, object]:
    p_ge_76, p_ge_75 = exact_c22_mann_whitney_distribution()

    p_dim = 64
    n_ref, n_sens = 52, 83
    labels = [1] * n_ref + [0] * n_sens
    folds = [idx % 5 for idx in range(n_ref)] + [idx % 5 for idx in range(n_sens)]
    total_pairs = n_ref * n_sens

    aucs_clean: List[float] = []
    aucs_raw: List[float] = []
    aucs_mid27: List[float] = []
    aucs_mid1: List[float] = []
    aucs_null1: List[float] = []
    max_drift = 0.0

    for rep in range(n_reps):
        rng = random.Random(20261113 + rep * 97)
        ortho = gram_schmidt_columns([[rng.gauss(0.0, 1.0) for _ in range(p_dim)] for _ in range(5)])
        u_bio, q_batch = ortho[0], ortho[1:5]
        leaks = [0.68, -0.58, 0.52, -0.46]
        beta_hat = [1.35 * u_bio[d] + sum(lw * qb[d] for lw, qb in zip(leaks, q_batch)) + rng.gauss(0.0, 0.03) for d in range(p_dim)]

        qc_probes = []
        for _ in range(12):
            w_qc = [rng.gauss(0.0, 1.0) for _ in range(4)]
            qc_probes.append([sum(w_qc[m] * q_batch[m][d] for m in range(4)) for d in range(p_dim)])
        q_est = gram_schmidt_columns(qc_probes)[:4]

        beta_perp = list(beta_hat)
        for _ in range(2):
            for q in q_est:
                pr = dot_f(beta_perp, q)
                beta_perp = [b - pr * qd for b, qd in zip(beta_perp, q)]

        fold_off = [[rng.gauss(0.0, 1.35) for _ in range(4)] for _ in range(5)]
        sc_clean, sc_raw, sc_null = [], [], []
        for idx, y in enumerate(labels):
            z_bio = (0.76 if y == 1 else -0.76) + rng.gauss(0.0, 1.0)
            x_c = [z_bio * u_bio[d] + rng.gauss(0.0, 0.30) for d in range(p_dim)]
            ffpe = [fold_off[folds[idx]][m] + rng.gauss(0.0, 1.15) for m in range(4)]
            x_s = [x_c[d] + sum(ffpe[m] * q_batch[m][d] for m in range(4)) for d in range(p_dim)]
            c_i, r_i, n_i = dot_f(x_c, beta_perp), dot_f(x_s, beta_hat), dot_f(x_s, beta_perp)
            max_drift = max(max_drift, abs(n_i - c_i))
            sc_clean.append(c_i)
            sc_raw.append(r_i)
            sc_null.append(n_i)

        sc_mid_b = [0.0] * len(labels)
        for f_id in range(5):
            f_idx = [i for i, f in enumerate(folds) if f == f_id]
            normed = midrank_normalize([sc_raw[i] for i in f_idx])
            for loc, gi in enumerate(f_idx):
                sc_mid_b[gi] = normed[loc]
        sc_mid_1 = [midrank_normalize([s])[0] for s in sc_raw]

        aucs_clean.append(exact_mann_whitney_wins(sc_clean, labels) / total_pairs)
        aucs_raw.append(exact_mann_whitney_wins(sc_raw, labels) / total_pairs)
        aucs_mid27.append(exact_mann_whitney_wins(sc_mid_b, labels) / total_pairs)
        aucs_mid1.append(exact_mann_whitney_wins(sc_mid_1, labels) / total_pairs)
        aucs_null1.append(exact_mann_whitney_wins(sc_null, labels) / total_pairs)

    rng21 = random.Random(20261113)
    labels21 = [1] * 13 + [0] * 8
    centers21 = [i % 3 for i in range(21)]
    pass_c, pass_r, pass_m, pass_n = 0, 0, 0, 0
    for _ in range(c22_trials):
        c_drifts = [[rng21.gauss(0.0, 1.25) for _ in range(4)] for _ in range(3)]
        s_c, s_r, s_n = [], [], []
        for idx, y in enumerate(labels21):
            xb = (0.68 if y == 1 else -0.68) + rng21.gauss(0.0, 1.0)
            ff = [c_drifts[centers21[idx]][m] + rng21.gauss(0.0, 1.05) for m in range(4)]
            s_c.append(1.35 * xb)
            s_r.append(1.35 * xb + 0.68 * ff[0] - 0.58 * ff[1] + 0.52 * ff[2] - 0.46 * ff[3])
            s_n.append(1.35 * xb)
        s_m = [0.0] * 21
        for cid in range(3):
            c_idx = [i for i, c in enumerate(centers21) if c == cid]
            nrm = midrank_normalize([s_r[i] for i in c_idx])
            for loc, gi in enumerate(c_idx):
                s_m[gi] = nrm[loc]
        if exact_mann_whitney_wins(s_c, labels21) >= 76.0:
            pass_c += 1
        if exact_mann_whitney_wins(s_r, labels21) >= 76.0:
            pass_r += 1
        if exact_mann_whitney_wins(s_m, labels21) >= 76.0:
            pass_m += 1
        if exact_mann_whitney_wins(s_n, labels21) >= 76.0:
            pass_n += 1

    def avg(xs: Sequence[float]) -> float:
        return round(sum(xs) / float(len(xs)), 5)

    return {
        "total_pairs": total_pairs,
        "auroc_clean_oracle_mean": avg(aucs_clean),
        "auroc_raw_pooled_shifted_mean": avg(aucs_raw),
        "auroc_midrank_batch27_mean": avg(aucs_mid27),
        "auroc_midrank_prospective_n1_mean": avg(aucs_mid1),
        "auroc_nullspace_gate_prospective_n1_mean": avg(aucs_null1),
        "max_logit_drift_under_batch_shift": round(max_drift, 14),
        "c22_exact_p_u_ge_76": f"{p_ge_76.numerator}/{p_ge_76.denominator}",
        "c22_exact_p_u_ge_75": f"{p_ge_75.numerator}/{p_ge_75.denominator}",
        "c22_power_raw_shifted": round(pass_r / float(c22_trials), 4),
        "c22_power_3center_midrank": round(pass_m / float(c22_trials), 4),
        "c22_power_nullspace_n1": round(pass_n / float(c22_trials), 4),
    }


def run_all_verifications() -> Dict[str, object]:
    res = {
        "cdr2l_mhc2_core_bifurcation": verify_cdr2l_mhc2_core_bifurcation(),
        "c15_monoid_and_offset_saturation": verify_c15_monoid_and_offset_saturation(),
        "soko_ilp_minimal_assays": verify_soko_ilp_minimal_assays(),
        "c10_c19_paraneoplastic_cascade_gate": verify_paraneoplastic_cascade_gate(),
        "c20_c22_prospective_n1_and_power": verify_prospective_n1_and_c22_power(),
    }
    res["verification_sha256"] = hashlib.sha256(json.dumps(res, sort_keys=True).encode("utf-8")).hexdigest()
    return res


if __name__ == "__main__":
    print(json.dumps(run_all_verifications(), indent=2, sort_keys=True))
