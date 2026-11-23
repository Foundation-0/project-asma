#!/usr/bin/env python3
"""Exact-Rational Optimal Trace-Inertia Rank Bound & Sound Congruence TCB.

Zero-float (`fractions.Fraction` only) verification and synthesis instrument bridging:
  - Foundation-0/project-asma (chimeric MS1/MS2 multi-scan Gram rank certification)
  - siliconcordat/loom PR #7 (`docs/10-exact-inertia-certificates.md` unscaled R_G)
  - Gemini Session 2 (`pair_06_block_00.py` fixed-c Lemma 3.2 & Mode B exploit)
  - Gemini Session 1 (`pair_21_block_01.py` Form III effective rank r_eff = exp(H_1))

Main New Mathematical Result (Jointly Scale-and-Weight Optimal Trace-Inertia Rank Bound):
  Let M = P_1 + Q be n x n real symmetric (or complex Hermitian) with P_1 >= 0 (rank r)
  and n_+(Q) <= b. Let m = tr(M), S = ||M||_HS^2 = tr(M^2) > 0, and let t_minus <= tr(Q)
  be any certified rational lower bound on tr(Q). Then:

      r >= R_opt(m, t_minus, S, b) =
          { b * (m - t_minus)^2 / (b * S - t_minus^2),
                if b > 0, t_minus > 0, t_minus * m >= b * S, and b * S > t_minus^2;
          { max(0, m^2 / S - b),
                if m > 0 and not in Branch 1;
          { 0,  otherwise.

  Proof sketch (holds for ALL non-commuting Hermitian matrices):
    By Weyl's inequalities, h_{r+b+1}(M) <= 0 and sum_{j=1}^b h_j(M) >= sum_{j=1}^b q_j(Q)
    >= tr(Q) >= t_minus. For any scale a > 0 and weight k >= 1 (setting c = 2(k-1) >= 0):
      f(a, k) = 2 a m + 2 a (k - 1) t_minus - a^2 S - k^2 b
              <= sum_{j=1}^b (2 a k h_j - a^2 h_j^2 - k^2)
                 + sum_{i=b+1}^{b+r} (2 a h_i - a^2 h_i^2)
                 + sum_{i > b+r} (2 a h_i - a^2 h_i^2)
              <= 0 + r + 0 = r.
    Taking sup_{a > 0, k >= 1} f(a, k) gives R_opt exactly, strictly dominating both:
      - siliconcordat/loom PR #7 docs/10 R_G = sup_{k >= 1} f(1, k) by the exact square
        ((m - t_minus) - (S - t_minus^2/b))^2 / (S - t_minus^2/b) >= 0, and
      - Session 2 fixed-c bound R_S2(c) = sup_{a > 0} f(a, c) by the exact square
        ((b*S - t_minus^2) / S) * (c - k_star)^2 >= 0.
    Furthermore, R_opt is strictly scale-invariant: R_opt(lam*M, lam*Q) = R_opt(M, Q)
    for all rational lam > 0, whereas R_G collapses under rescaling.

Run:
  python3 -O -B studies/expedition-mobius-ropt/optimal_inertia_rank.py
  python3 -O -B studies/expedition-mobius-ropt/optimal_inertia_rank.py --json
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
import random
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

Mat = List[List[Fraction]]
# Canonical lowest-terms ASCII rational: "0", non-leading-zero integer, or reduced "p/q" (q >= 2).
STRICT_INT_RE = re.compile(r"\A(?:0|-?[1-9][0-9]*)\Z")
STRICT_FRAC_RE = re.compile(r"\A(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")


# ---------------------------------------------------------------------------
# 1. Fail-Closed Exact-Rational Parsing & Matrix Primitives (Zero Float)
# ---------------------------------------------------------------------------

def to_frac(x: Any) -> Fraction:
    """Strictly convert exact int/canonical-ASCII-'p/q' str/Fraction to Fraction.

    Rejects bool, float, whitespace, underscores, non-ASCII digits, leading zeros ("007", "01/2"),
    "-0", unreduced fractions ("2/4", "0/5"), and denominator 1 ("3/1").
    """
    if isinstance(x, bool) or isinstance(x, float):
        raise ValueError(f"REJECT_NON_EXACT_INPUT: got {type(x).__name__}")
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    if isinstance(x, str):
        if not STRICT_FRAC_RE.fullmatch(x):
            raise ValueError(f"REJECT_MALFORMED_RATIONAL_STRING: {x!r}")
        if "/" in x:
            num_s, den_s = x.split("/", 1)
            if not STRICT_INT_RE.fullmatch(num_s) or den_s.startswith("0"):
                raise ValueError(f"REJECT_NONCANONICAL_RATIONAL: {x!r}")
            num_i, den_i = int(num_s), int(den_s)
            if den_i <= 1 or num_i == 0 or math.gcd(abs(num_i), den_i) != 1:
                raise ValueError(f"REJECT_UNREDUCED_RATIONAL: {x!r}")
            return Fraction(num_i, den_i)
        return Fraction(int(x), 1)
    raise ValueError(f"UNSUPPORTED_VALUE_TYPE: {type(x).__name__}")


def _require_exact_square_matrix(M: Any, name: str, expected_n: Optional[int] = None) -> int:
    """Fail-closed check that M is a non-empty square matrix of exact Fraction/int (no float/bool/ragged)."""
    if not isinstance(M, list) or len(M) == 0:
        raise ValueError(f"{name}_EMPTY_OR_NOT_LIST")
    n = len(M)
    if expected_n is not None and n != expected_n:
        raise ValueError(f"{name}_DIM_MISMATCH: expected {expected_n}, got {n}")
    for row in M:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError(f"{name}_NOT_SQUARE_OR_RAGGED")
        for v in row:
            if isinstance(v, bool) or isinstance(v, float) or not isinstance(v, (int, Fraction)):
                raise ValueError(f"{name}_NON_EXACT_ENTRY: got {type(v).__name__}")
    return n


def loads_strict_json(raw: str) -> Any:
    """Parse JSON while rejecting floats, NaN/Inf, and duplicate object keys."""
    def reject_float(tok: str) -> Any:
        raise ValueError(f"REJECT_FLOAT_JSON: {tok!r}")

    def reject_const(tok: str) -> Any:
        raise ValueError(f"REJECT_CONSTANT_JSON: {tok!r}")

    def no_dupes(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in pairs:
            if k in out:
                raise ValueError(f"REJECT_DUPLICATE_KEY: {k!r}")
            out[k] = v
        return out

    return json.loads(
        raw,
        parse_float=reject_float,
        parse_constant=reject_const,
        object_pairs_hook=no_dupes,
    )


def mat_zero(n: int, m: int) -> Mat:
    return [[Fraction(0) for _ in range(m)] for _ in range(n)]


def mat_eye(n: int) -> Mat:
    return [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]


def mat_t(A: Mat) -> Mat:
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def mat_mul(A: Mat, B: Mat) -> Mat:
    n, k, m = len(A), len(B), len(B[0])
    if len(A[0]) != k:
        raise ValueError("MAT_DIM_MISMATCH")
    return [
        [sum((A[i][t] * B[t][j] for t in range(k)), Fraction(0)) for j in range(m)]
        for i in range(n)
    ]


def mat_add(A: Mat, B: Mat) -> Mat:
    return [[a + b for a, b in zip(rA, rB)] for rA, rB in zip(A, B)]


def mat_sub(A: Mat, B: Mat) -> Mat:
    return [[a - b for a, b in zip(rA, rB)] for rA, rB in zip(A, B)]


def mat_scale(c: Fraction, A: Mat) -> Mat:
    return [[c * v for v in row] for row in A]


def is_symmetric(A: Mat) -> bool:
    n = len(A)
    if n == 0 or any(len(r) != n for r in A):
        return False
    return all(A[i][j] == A[j][i] for i in range(n) for j in range(i + 1, n))


def trace(A: Mat) -> Fraction:
    return sum((A[i][i] for i in range(len(A))), Fraction(0))


def hs_norm_sq(A: Mat) -> Fraction:
    return sum((v * v for row in A for v in row), Fraction(0))


def exact_rank(A: Mat) -> int:
    """Exact rank over Q via Fraction Gaussian elimination."""
    m = len(A)
    n = len(A[0])
    R = [row[:] for row in A]
    rank = 0
    for col in range(n):
        piv = None
        for r in range(rank, m):
            if R[r][col] != 0:
                piv = r
                break
        if piv is None:
            continue
        R[rank], R[piv] = R[piv], R[rank]
        pv = R[rank][col]
        for r in range(rank + 1, m):
            if R[r][col] != 0:
                fac = R[r][col] / pv
                for c in range(col, n):
                    R[r][c] -= fac * R[rank][c]
        rank += 1
        if rank == m:
            break
    return rank


def exact_rational_householder(v: Sequence[Fraction]) -> Mat:
    """Exact orthogonal matrix U = I - 2 v v^T / (v^T v) over Q (U^T U = I)."""
    n = len(v)
    norm2 = sum((x * x for x in v), Fraction(0))
    if norm2 == 0:
        raise ValueError("ZERO_HOUSEHOLDER_VECTOR")
    two_over = Fraction(2) / norm2
    return [
        [(Fraction(1) if i == j else Fraction(0)) - two_over * v[i] * v[j] for j in range(n)]
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# 2. Exact Block-LDL^T Producer & Fail-Closed Congruence Inertia Verifiers
# ---------------------------------------------------------------------------

def produce_block_ldl(M: Mat) -> Tuple[List[int], Mat, Mat]:
    """Compute exact P M P^T = L D L^T over Q with 1x1 and 2x2 symmetric blocks in D.

    Returns (perm, L, D) where perm maps new index i -> old index perm[i].
    Works on every symmetric rational matrix, including zero-diagonal indefinite matrices.
    """
    if not is_symmetric(M):
        raise ValueError("MATRIX_NOT_SYMMETRIC")
    n = len(M)
    A = [row[:] for row in M]
    perm = list(range(n))
    L = mat_eye(n)
    D = mat_zero(n, n)

    k = 0
    while k < n:
        # Look for a nonzero diagonal entry in A[k:, k:]
        diag_piv = None
        for i in range(k, n):
            if A[i][i] != 0:
                diag_piv = i
                break

        if diag_piv is not None:
            if diag_piv != k:
                perm[k], perm[diag_piv] = perm[diag_piv], perm[k]
                A[k], A[diag_piv] = A[diag_piv], A[k]
                for r in range(n):
                    A[r][k], A[r][diag_piv] = A[r][diag_piv], A[r][k]
                for c in range(k):
                    L[k][c], L[diag_piv][c] = L[diag_piv][c], L[k][c]

            d = A[k][k]
            D[k][k] = d
            for i in range(k + 1, n):
                L[i][k] = A[i][k] / d
            for i in range(k + 1, n):
                lik = L[i][k]
                if lik == 0:
                    continue
                for j in range(i, n):
                    val = A[i][j] - lik * d * L[j][k]
                    A[i][j] = val
                    A[j][i] = val
            k += 1
            continue

        # All remaining diagonal entries are zero; look for a nonzero off-diagonal entry
        off_piv = None
        for i in range(k, n):
            for j in range(i + 1, n):
                if A[i][j] != 0:
                    off_piv = (i, j)
                    break
            if off_piv is not None:
                break

        if off_piv is None:
            # Remaining trailing submatrix is identically zero
            break

        p1, p2 = off_piv
        # Swap p1 -> k, then p2 -> k+1
        if p1 != k:
            perm[k], perm[p1] = perm[p1], perm[k]
            A[k], A[p1] = A[p1], A[k]
            for r in range(n):
                A[r][k], A[r][p1] = A[r][p1], A[r][k]
            for c in range(k):
                L[k][c], L[p1][c] = L[p1][c], L[k][c]
            if p2 == k:
                p2 = p1
        if p2 != k + 1:
            perm[k + 1], perm[p2] = perm[p2], perm[k + 1]
            A[k + 1], A[p2] = A[p2], A[k + 1]
            for r in range(n):
                A[r][k + 1], A[r][p2] = A[r][p2], A[r][k + 1]
            for c in range(k):
                L[k + 1][c], L[p2][c] = L[p2][c], L[k + 1][c]

        # 2x2 symmetric block [[0, b], [b, 0]] has det = -b^2 < 0 and inverse [[0, 1/b], [1/b, 0]]
        b_val = A[k][k + 1]
        D[k][k + 1] = b_val
        D[k + 1][k] = b_val
        inv_b = Fraction(1) / b_val
        for i in range(k + 2, n):
            L[i][k] = A[i][k + 1] * inv_b
            L[i][k + 1] = A[i][k] * inv_b
        for i in range(k + 2, n):
            li0, li1 = L[i][k], L[i][k + 1]
            for j in range(i, n):
                lj0, lj1 = L[j][k], L[j][k + 1]
                # [li0, li1] [[0, b], [b, 0]] [lj0, lj1]^T = b * (li0*lj1 + li1*lj0)
                val = A[i][j] - b_val * (li0 * lj1 + li1 * lj0)
                A[i][j] = val
                A[j][i] = val
        k += 2

    return perm, L, D


def verify_block_ldl_inertia(M: Mat, perm: Sequence[int], L: Mat, D: Mat) -> Tuple[int, int, int]:
    """Fail-closed verifier for P M P^T = L D L^T. Returns exact inertia (n_pos, n_neg, n_zero)."""
    n = _require_exact_square_matrix(M, "M")
    _require_exact_square_matrix(L, "L", expected_n=n)
    _require_exact_square_matrix(D, "D", expected_n=n)
    if not is_symmetric(M):
        raise ValueError("M_NOT_SYMMETRIC")
    if (
        len(perm) != n
        or any(isinstance(p, bool) or not isinstance(p, int) for p in perm)
        or sorted(perm) != list(range(n))
    ):
        raise ValueError("INVALID_PERMUTATION")
    for i in range(n):
        if L[i][i] != 1:
            raise ValueError("L_NON_UNIT_DIAGONAL")
        for j in range(i + 1, n):
            if L[i][j] != 0:
                raise ValueError("L_NOT_LOWER_TRIANGULAR")
    if not is_symmetric(D):
        raise ValueError("D_NOT_SYMMETRIC")
    for i in range(n):
        for j in range(n):
            if abs(i - j) > 1 and D[i][j] != 0:
                raise ValueError("D_NOT_TRIDIAGONAL_BLOCK")

    # Verify non-overlapping 1x1 / 2x2 block structure and read exact inertia
    n_pos = n_neg = n_zero = 0
    i = 0
    while i < n:
        has_off = (i + 1 < n) and (D[i][i + 1] != 0)
        if has_off:
            # Ensure this 2x2 block does not overlap with a following off-diagonal entry
            if i + 2 < n and D[i + 1][i + 2] != 0:
                raise ValueError("D_OVERLAPPING_2X2_BLOCKS")
            a, b_val, c = D[i][i], D[i][i + 1], D[i + 1][i + 1]
            det = a * c - b_val * b_val
            tr = a + c
            if det < 0:
                n_pos += 1
                n_neg += 1
            elif det > 0:
                if tr > 0:
                    n_pos += 2
                else:
                    n_neg += 2
            else:
                if tr > 0:
                    n_pos += 1
                    n_zero += 1
                elif tr < 0:
                    n_neg += 1
                    n_zero += 1
                else:
                    n_zero += 2
            i += 2
        else:
            d = D[i][i]
            if d > 0:
                n_pos += 1
            elif d < 0:
                n_neg += 1
            else:
                n_zero += 1
            i += 1

    # Verify exact matrix identity P M P^T == L D L^T
    PMP = [[M[perm[r]][perm[c]] for c in range(n)] for r in range(n)]
    LDL = mat_mul(mat_mul(L, D), mat_t(L))
    if PMP != LDL:
        raise ValueError("LDL_IDENTITY_MISMATCH")

    return (n_pos, n_neg, n_zero)


def verify_general_congruence_inertia(
    Q: Mat, C: Mat, C_inv: Mat, D_diag: Sequence[Fraction]
) -> Tuple[int, int, int]:
    """Fail-closed verifier for C C_inv == I and C Q C^T == diag(D_diag)."""
    n = _require_exact_square_matrix(Q, "Q")
    _require_exact_square_matrix(C, "C", expected_n=n)
    _require_exact_square_matrix(C_inv, "C_inv", expected_n=n)
    if not is_symmetric(Q):
        raise ValueError("Q_NOT_SYMMETRIC")
    if len(D_diag) != n or any(isinstance(d, bool) or isinstance(d, float) or not isinstance(d, (int, Fraction)) for d in D_diag):
        raise ValueError("INVALID_D_DIAG")
    if mat_mul(C, C_inv) != mat_eye(n):
        raise ValueError("CONGRUENCE_NOT_INVERTIBLE")
    cong = mat_mul(mat_mul(C, Q), mat_t(C))
    for i in range(n):
        for j in range(n):
            expected = D_diag[i] if i == j else Fraction(0)
            if cong[i][j] != expected:
                raise ValueError("CONGRUENCE_IDENTITY_MISMATCH")
    n_pos = sum(1 for d in D_diag if d > 0)
    n_neg = sum(1 for d in D_diag if d < 0)
    n_zero = sum(1 for d in D_diag if d == 0)
    return (n_pos, n_neg, n_zero)


# ---------------------------------------------------------------------------
# 3. Jointly Scale-and-Weight Optimal Trace-Inertia Rank Bound (R_opt)
# ---------------------------------------------------------------------------

def r_opt_bound(
    tr_M: Fraction,
    tr_Q_lower: Fraction,
    hs2_M: Fraction,
    b: int,
) -> Dict[str, Any]:
    """Compute the exact closed-form optimal trace-inertia rank lower bound R_opt.

    Valid for ANY symmetric/Hermitian decomposition M = P_1 + Q with P_1 >= 0,
    n_+(Q) <= b, and certified trace lower bound tr_Q_lower <= tr(Q).
    """
    if b < 0:
        raise ValueError("NEGATIVE_INERTIA_BOUND")
    if hs2_M < 0:
        raise ValueError("NEGATIVE_HS_NORM")
    p_plus = tr_M - tr_Q_lower
    if hs2_M == 0 or p_plus <= 0 or tr_M <= 0:
        return {"bound": Fraction(0), "branch": "zero_or_nonpositive_trace", "k_opt": Fraction(1), "a_opt": Fraction(0)}

    b_f = Fraction(b)
    if b > 0 and tr_Q_lower > 0 and tr_Q_lower * tr_M >= b_f * hs2_M:
        denom = b_f * hs2_M - tr_Q_lower * tr_Q_lower
        if denom <= 0:
            raise ValueError("INCONSISTENT_HYPOTHESES: tr_Q_lower^2 >= b * ||M||_HS^2 with tr_M > tr_Q_lower is impossible for P_1 >= 0")
        bound = b_f * p_plus * p_plus / denom
        k_opt = (p_plus * tr_Q_lower) / denom
        a_opt = (b_f * p_plus) / denom
        return {"bound": bound, "branch": "branch1_strong_interference", "k_opt": k_opt, "a_opt": a_opt}

    raw = (tr_M * tr_M) / hs2_M - b_f
    bound = raw if raw > 0 else Fraction(0)
    return {"bound": bound, "branch": "branch2_weak_or_negative_interference", "k_opt": Fraction(1), "a_opt": tr_M / hs2_M}


def r_loom_doc10_bound(tr_M: Fraction, tr_Q_lower: Fraction, hs2_M: Fraction, b: int) -> Fraction:
    """Fable's siliconcordat/loom PR #7 docs/10 unscaled best member R_G (scale a=1 fixed)."""
    b_f = Fraction(b)
    if b > 0 and tr_Q_lower >= b_f:
        return Fraction(2) * (tr_M - tr_Q_lower) + (tr_Q_lower * tr_Q_lower) / b_f - hs2_M
    return Fraction(2) * tr_M - hs2_M - b_f


def r_session2_fixed_c(
    tr_M: Fraction, tr_Q_lower: Fraction, hs2_M: Fraction, b: int, c: Fraction = Fraction(2)
) -> Fraction:
    """Session 2 Pair 6 scale-optimized fixed-c bound T_c^2 / ||M||_HS^2 - c^2 b (c >= 1)."""
    if c < 1:
        raise ValueError("REQUIRE_C_GE_1")
    if hs2_M <= 0:
        return Fraction(0)
    T_c = (tr_M - tr_Q_lower) + c * tr_Q_lower
    if T_c <= 0:
        return Fraction(0)
    return (T_c * T_c) / hs2_M - (c * c) * Fraction(b)


def certify_sound_decomposition_rank(
    M: Mat,
    Q: Mat,
    Q_cert: Tuple[List[int], Mat, Mat],
    P_cert: Tuple[List[int], Mat, Mat],
    target_rank_gt: int,
) -> Dict[str, Any]:
    """Sound Mode B TCB: certifies BOTH n_+(Q) = b AND P_1 = M - Q >= 0 via exact LDL^T witnesses."""
    if isinstance(target_rank_gt, bool) or not isinstance(target_rank_gt, int) or target_rank_gt < 0:
        raise ValueError("INVALID_TARGET_RANK_GT")
    if not is_symmetric(M) or not is_symmetric(Q) or len(M) != len(Q):
        raise ValueError("NON_SYMMETRIC_OR_SHAPE_MISMATCH")
    b_pos, _, _ = verify_block_ldl_inertia(Q, *Q_cert)
    P = mat_sub(M, Q)
    _, p_neg, _ = verify_block_ldl_inertia(P, *P_cert)
    if p_neg != 0:
        raise ValueError(f"P_NOT_PSD: certified negative inertia n_-(M - Q) = {p_neg}")

    tr_M = trace(M)
    tr_Q = trace(Q)
    hs2 = hs_norm_sq(M)
    res = r_opt_bound(tr_M, tr_Q, hs2, b_pos)
    if res["bound"] <= Fraction(target_rank_gt):
        raise ValueError(f"RANK_BOUND_NOT_CERTIFIED: R_opt={res['bound']} <= {target_rank_gt}")
    return {
        "certified_min_rank": target_rank_gt + 1,
        "certified_b": b_pos,
        "R_opt_exact": str(res["bound"]),
        "R_opt_float": round(float(res["bound"]), 6),
        "branch": res["branch"],
        "k_opt_exact": str(res["k_opt"]),
        "a_opt_exact": str(res["a_opt"]),
    }


def certify_noise_envelope_rank(
    G_obs: Mat,
    Q_known: Mat,
    Q_known_cert: Tuple[List[int], Mat, Mat],
    noise_upper_diag: Sequence[Fraction],
    target_rank_gt: int,
) -> Dict[str, Any]:
    """Non-circular noise-envelope TCB for G_obs = P_sig + Q_known + N with 0 <= N <= diag(noise_upper_diag).

    Requires NO knowledge of P_sig or N:
      Set M = G_obs - D_tau = P_sig + Q where Q = Q_known + (N - D_tau).
      Since N <= D_tau, Q <= Q_known => n_+(Q) <= n_+(Q_known) = b (Weyl).
      Since N >= 0,     Q >= Q_known - D_tau => tr(Q) >= tr(Q_known) - tr(D_tau) = t_minus.
    """
    if isinstance(target_rank_gt, bool) or not isinstance(target_rank_gt, int) or target_rank_gt < 0:
        raise ValueError("INVALID_TARGET_RANK_GT")
    if not is_symmetric(G_obs) or not is_symmetric(Q_known) or len(G_obs) != len(Q_known):
        raise ValueError("NON_SYMMETRIC_OR_SHAPE_MISMATCH")
    n = len(G_obs)
    if len(noise_upper_diag) != n or any(t < 0 for t in noise_upper_diag):
        raise ValueError("INVALID_NOISE_UPPER_BOUND")
    b_pos, _, _ = verify_block_ldl_inertia(Q_known, *Q_known_cert)
    D_tau = [[noise_upper_diag[i] if i == j else Fraction(0) for j in range(n)] for i in range(n)]
    M = mat_sub(G_obs, D_tau)
    tr_M = trace(M)
    t_minus = trace(Q_known) - sum(noise_upper_diag, Fraction(0))
    hs2 = hs_norm_sq(M)
    res = r_opt_bound(tr_M, t_minus, hs2, b_pos)
    if res["bound"] <= Fraction(target_rank_gt):
        raise ValueError(f"RANK_BOUND_NOT_CERTIFIED: R_opt={res['bound']} <= {target_rank_gt}")
    return {
        "certified_min_rank": target_rank_gt + 1,
        "certified_b": b_pos,
        "tr_M": str(tr_M),
        "tr_Q_lower": str(t_minus),
        "hs2_M": str(hs2),
        "R_opt_exact": str(res["bound"]),
        "R_opt_float": round(float(res["bound"]), 6),
        "branch": res["branch"],
    }


# ---------------------------------------------------------------------------
# 4. Complete Anti-Shadow Verification & Cross-Domain Benchmark Suite
# ---------------------------------------------------------------------------

def run_suite() -> Dict[str, Any]:
    report: Dict[str, Any] = {"checks": {}}

    # --- Check 1: Reproduce Session 2 Mode B Exploit & Verify Patched TCB Rejects It ---
    H_exp = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    Q_exp = [[Fraction(10), Fraction(0)], [Fraction(0), Fraction(0)]]
    # Naive Session 2 calculation (without P >= 0 check):
    naive_Tc = (trace(H_exp) - trace(Q_exp)) + Fraction(2) * trace(Q_exp)
    naive_bound = (naive_Tc * naive_Tc) / hs_norm_sq(H_exp) - Fraction(4)
    if naive_bound != Fraction(117):
        raise RuntimeError(f"Expected naive exploit bound 117, got {naive_bound}")
    q_cert = produce_block_ldl(Q_exp)
    p_cert = produce_block_ldl(mat_sub(H_exp, Q_exp))
    exploit_rejected = False
    try:
        certify_sound_decomposition_rank(H_exp, Q_exp, q_cert, p_cert, target_rank_gt=0)
    except ValueError as exc:
        if "P_NOT_PSD" in str(exc):
            exploit_rejected = True
    if not exploit_rejected:
        raise RuntimeError("Patched TCB failed to reject Session 2 Mode B exploit!")
    report["checks"]["session2_mode_b_exploit"] = {
        "naive_forged_bound_on_2x2": str(naive_bound),
        "patched_tcb_rejected_with_P_NOT_PSD": exploit_rejected,
    }

    # --- Check 2: Scale Invariance (Gate 2) & Exact Dominance Over loom#7 R_G and Session 2 c=2 ---
    P_scale = [
        [Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0)],
    ]
    Q_scale = [
        [Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(50)],
    ]
    scale_rows = []
    for lam in (Fraction(1, 100), Fraction(1, 10), Fraction(1), Fraction(10), Fraction(100)):
        Ms = mat_scale(lam, mat_add(P_scale, Q_scale))
        Qs = mat_scale(lam, Q_scale)
        trM, trQ, S = trace(Ms), trace(Qs), hs_norm_sq(Ms)
        ropt = r_opt_bound(trM, trQ, S, 1)["bound"]
        rg = r_loom_doc10_bound(trM, trQ, S, 1)
        rs2 = r_session2_fixed_c(trM, trQ, S, 1, Fraction(2))
        if ropt != Fraction(2):
            raise RuntimeError(f"Scale invariance broken at lam={lam}: R_opt={ropt}")
        if ropt < rg or ropt < rs2:
            raise RuntimeError("Dominance violated!")
        scale_rows.append({
            "lambda": str(lam),
            "R_opt": str(ropt),
            "R_loom_doc10": round(float(rg), 6),
            "R_session2_c2": round(float(rs2), 6),
        })
    report["checks"]["scale_invariance_and_dominance"] = scale_rows

    # --- Check 3: Orthogonal Basis Invariance (Gate 2) via Exact Rational Householder ---
    U = exact_rational_householder([Fraction(1), Fraction(2), Fraction(-1)])
    if mat_mul(U, mat_t(U)) != mat_eye(3):
        raise RuntimeError("Householder matrix not orthogonal!")
    M_base = mat_add(P_scale, Q_scale)
    M_rot = mat_mul(mat_mul(U, M_base), mat_t(U))
    Q_rot = mat_mul(mat_mul(U, Q_scale), mat_t(U))
    b_rot, _, _ = verify_block_ldl_inertia(Q_rot, *produce_block_ldl(Q_rot))
    r_rot = r_opt_bound(trace(M_rot), trace(Q_rot), hs_norm_sq(M_rot), b_rot)["bound"]
    if b_rot != 1 or r_rot != Fraction(2):
        raise RuntimeError(f"Basis invariance failed: b_rot={b_rot}, r_rot={r_rot}")
    report["checks"]["basis_invariance_householder"] = {
        "exact_b_after_rotation": b_rot,
        "exact_R_opt_after_rotation": str(r_rot),
        "exact_match": True,
    }

    # --- Check 4: Non-Circular Noise-Envelope Application to project-asma (3-Component Chimeric) ---
    # 5 elution scans: strong known CDR2L backbone (weight 9/10) + 2 weaker chimeric species
    # (weights 1/20 each) + unknown PSD noise N bounded by 0 <= N <= tau * I_5.
    # Analytic sensitivity law (trace-slack amplification):
    #   b*S - t_-^2 = b*||P||_F^2 + (t^2 - t_-^2) ~ b*||P||_F^2 + 2*t*Delta_t,
    # so certifying rank >= 2 on P = diag(w, w) buried under Q = diag(q) requires
    #   Delta_t = T*tau < w^2 / q = (1/400)/(9/10) = 1/360 (~0.00278, i.e., tau < 1/1800 for T=5).
    V_rot = exact_rational_householder([Fraction(1), Fraction(-1), Fraction(2), Fraction(1), Fraction(0)])
    diag_Q = [[Fraction(9, 10) if i == j == 0 else Fraction(0) for j in range(5)] for i in range(5)]
    diag_P = [[Fraction(1, 20) if (i == j and i in (1, 2)) else Fraction(0) for j in range(5)] for i in range(5)]
    Q_asma = mat_mul(mat_mul(V_rot, diag_Q), mat_t(V_rot))
    P_asma = mat_mul(mat_mul(V_rot, diag_P), mat_t(V_rot))

    # Regime 4a: tau = 1/5000 (T*tau = 1/1000 < critical Delta_t* = 1/360) -> R_opt certifies >= 2!
    diag_N_low = [[Fraction(1, 10000) if i == j else Fraction(0) for j in range(5)] for i in range(5)]
    G_asma = mat_add(mat_add(Q_asma, P_asma), diag_N_low)
    tau_low = [Fraction(1, 5000)] * 5
    asma_cert = certify_noise_envelope_rank(
        G_asma, Q_asma, produce_block_ldl(Q_asma), tau_low, target_rank_gt=1
    )
    # Compare with Mode A net-of-b (c=1, b=1), Session 2 Mode B (b=1, c=2), and loom doc10 R_G on exact same M:
    D_tau_low = [[tau_low[i] if i == j else Fraction(0) for j in range(5)] for i in range(5)]
    M_asma = mat_sub(G_asma, D_tau_low)
    trM_a, tmin_a, hs2_a = trace(M_asma), trace(Q_asma) - sum(tau_low, Fraction(0)), hs_norm_sq(M_asma)
    mode_a_net = r_session2_fixed_c(trM_a, tmin_a, hs2_a, 1, Fraction(1))  # = tr(M)^2/||M||^2 - b
    mode_b_s2 = r_session2_fixed_c(trM_a, tmin_a, hs2_a, 1, Fraction(2))
    loom_rg_a = r_loom_doc10_bound(trM_a, tmin_a, hs2_a, 1)

    # Regime 4b: Above critical slack threshold tau = 1/1000 (T*tau = 1/200 > 1/360)
    # Confirms exact sensitivity law: unknown-amplitude R_opt drops <= 1, while direct subtraction
    # of known Q_asma gives b=0 bound R_opt(G - Q_asma - D_tau, b=0) > 1.9!
    diag_N_hi = [[Fraction(1, 2000) if i == j else Fraction(0) for j in range(5)] for i in range(5)]
    G_asma_hi = mat_add(mat_add(Q_asma, P_asma), diag_N_hi)
    tau_hi = [Fraction(1, 1000)] * 5
    D_tau_hi = [[tau_hi[i] if i == j else Fraction(0) for j in range(5)] for i in range(5)]
    M_hi = mat_sub(G_asma_hi, D_tau_hi)
    ropt_above_thresh = r_opt_bound(
        trace(M_hi), trace(Q_asma) - sum(tau_hi, Fraction(0)), hs_norm_sq(M_hi), 1
    )["bound"]
    M_sub = mat_sub(M_hi, Q_asma)
    ropt_subtracted_b0 = r_opt_bound(trace(M_sub), Fraction(0), hs_norm_sq(M_sub), 0)["bound"]
    if not (ropt_above_thresh <= 1 and ropt_subtracted_b0 > Fraction(19, 10)):
        raise RuntimeError("Trace-slack sensitivity check failed!")

    # Negative control: single chimeric component only (rank 1) must NOT certify rank >= 2
    diag_P1 = [[Fraction(1, 20) if i == j == 1 else Fraction(0) for j in range(5)] for i in range(5)]
    G_null = mat_add(mat_add(Q_asma, mat_mul(mat_mul(V_rot, diag_P1), mat_t(V_rot))), diag_N_low)
    null_rejected = False
    try:
        certify_noise_envelope_rank(G_null, Q_asma, produce_block_ldl(Q_asma), tau_low, target_rank_gt=1)
    except ValueError as exc:
        if "RANK_BOUND_NOT_CERTIFIED" in str(exc):
            null_rejected = True
    if not null_rejected:
        raise RuntimeError("Negative control falsely certified rank >= 2!")

    report["checks"]["project_asma_3component_chimeric"] = {
        "true_chimeric_rank": 2,
        "critical_slack_Delta_t_star": "1/360",
        "below_threshold_tau_1_5000": {
            "R_opt_cert": asma_cert,
            "Mode_A_c1_net_of_b": round(float(mode_a_net), 6),
            "Session2_Mode_B_c2_b1": round(float(mode_b_s2), 6),
            "loom_doc10_R_G": round(float(loom_rg_a), 6),
            "R_opt_alone_certifies_rank_ge_2": (
                Fraction(asma_cert["R_opt_exact"]) > 1
                and mode_a_net <= 1
                and mode_b_s2 <= 1
                and loom_rg_a <= 1
            ),
        },
        "above_threshold_tau_1_1000": {
            "unknown_Q_R_opt_float": round(float(ropt_above_thresh), 6),
            "known_Q_subtracted_b0_R_opt_float": round(float(ropt_subtracted_b0), 6),
        },
        "single_chimeric_negative_control_rejected": null_rejected,
    }

    # --- Check 5: Exact Session 1 <-> Session 2 Spectral Entropy Hierarchy ---
    # rank(G) = exp(H_0) >= r_eff(G) = exp(H_1) >= R_2(G) = (tr G)^2 / ||G||_HS^2 = R_opt(b=0)
    spectra = [
        ("rank_collapse_strong", [Fraction(9, 10), Fraction(1, 20), Fraction(1, 20), Fraction(0)]),
        ("uniform_rank3", [Fraction(1, 3), Fraction(1, 3), Fraction(1, 3), Fraction(0)]),
        ("scan23848_split", [Fraction(6404, 10000) ** 2, Fraction(3596, 10000) ** 2, Fraction(0)]),
    ]
    entropy_bridge = []
    for label, eigs in spectra:
        n = len(eigs)
        G_sp = [[eigs[i] if i == j else Fraction(0) for j in range(n)] for i in range(n)]
        r_exact = sum(1 for e in eigs if e > 0)
        r2_exact = r_opt_bound(trace(G_sp), Fraction(0), hs_norm_sq(G_sp), 0)["bound"]
        tot = float(sum(eigs, Fraction(0)))
        probs = [float(e) / tot for e in eigs if e > 0]
        r_eff = math.exp(-sum(p * math.log(p) for p in probs))
        if not (r_exact + 1e-12 >= r_eff >= float(r2_exact) - 1e-12):
            raise RuntimeError(f"Entropy hierarchy violated on {label}")
        entropy_bridge.append({
            "case": label,
            "exact_rank_exp_H0": r_exact,
            "shannon_r_eff_exp_H1": round(r_eff, 6),
            "exact_renyi2_R_opt_b0": round(float(r2_exact), 6),
            "exact_renyi2_fraction": str(r2_exact),
        })
    report["checks"]["session1_session2_entropy_bridge"] = entropy_bridge

    # --- Check 6: 1,000 Seeded Random Non-Commuting Rational Property & Dominance Test ---
    rng = random.Random(20261120)
    n_trials = 1000
    exact_dom_doc10_identities = 0
    exact_dom_s2_identities = 0
    max_gap_over_doc10 = Fraction(0)
    max_gap_over_s2 = Fraction(0)
    tight_hits = 0

    for _ in range(n_trials):
        n = rng.randint(2, 5)
        k_p = rng.randint(0, n)
        P = mat_zero(n, n)
        for _ in range(k_p):
            vec = [Fraction(rng.randint(-3, 3), rng.randint(1, 3)) for _ in range(n)]
            w = Fraction(rng.randint(1, 4), rng.randint(1, 3))
            for i in range(n):
                for j in range(n):
                    P[i][j] += w * vec[i] * vec[j]
        k_q = rng.randint(1, n + 1)
        Q = mat_zero(n, n)
        for _ in range(k_q):
            vec = [Fraction(rng.randint(-3, 3), rng.randint(1, 3)) for _ in range(n)]
            sgn = Fraction(1) if rng.random() < 0.5 else Fraction(-1)
            w = sgn * Fraction(rng.randint(1, 4), rng.randint(1, 3))
            for i in range(n):
                for j in range(n):
                    Q[i][j] += w * vec[i] * vec[j]

        M = mat_add(P, Q)
        r_true = exact_rank(P)
        q_ldl = produce_block_ldl(Q)
        b_true, _, _ = verify_block_ldl_inertia(Q, *q_ldl)

        trM, trQ, S = trace(M), trace(Q), hs_norm_sq(M)
        if S == 0:
            continue
        res = r_opt_bound(trM, trQ, S, b_true)
        ropt = res["bound"]
        if ropt > Fraction(r_true):
            raise RuntimeError(f"THEOREM VIOLATION: R_opt={ropt} > rank(P)={r_true}")
        if ropt == Fraction(r_true) and r_true > 0:
            tight_hits += 1

        rg = r_loom_doc10_bound(trM, trQ, S, b_true)
        if ropt < rg:
            raise RuntimeError(f"DOMINANCE VIOLATION vs loom#7 R_G: {ropt} < {rg}")
        if ropt - rg > max_gap_over_doc10:
            max_gap_over_doc10 = ropt - rg

        # Check exact algebraic square identity vs R_G in overlap region
        if (
            res["branch"] == "branch1_strong_interference"
            and b_true > 0
            and trQ >= Fraction(b_true)
        ):
            D_res = S - (trQ * trQ) / Fraction(b_true)
            p_val = trM - trQ
            expected_diff = ((p_val - D_res) ** 2) / D_res
            if ropt - rg != expected_diff:
                raise RuntimeError("Exact square identity vs R_G failed!")
            exact_dom_doc10_identities += 1

        for c_test in (Fraction(1), Fraction(3, 2), Fraction(2), Fraction(4)):
            rs2 = r_session2_fixed_c(trM, trQ, S, b_true, c_test)
            if ropt < rs2:
                raise RuntimeError(f"DOMINANCE VIOLATION vs S2(c={c_test}): {ropt} < {rs2}")
            if c_test == Fraction(2) and ropt - rs2 > max_gap_over_s2:
                max_gap_over_s2 = ropt - rs2
            if res["branch"] == "branch1_strong_interference" and (trM - trQ) + c_test * trQ > 0:
                k_star = res["k_opt"]
                expected_s2_diff = (Fraction(b_true) * S - trQ * trQ) / S * ((c_test - k_star) ** 2)
                if ropt - rs2 != expected_s2_diff:
                    raise RuntimeError("Exact square identity vs S2(c) failed!")
                exact_dom_s2_identities += 1

    # --- Check 7: Must-Fail Adversarial Forgery Controls on Inertia Checker & Strict JSON ---
    forgeries_rejected = 0
    # 7a: Overlapping 2x2 blocks in D
    M_ov = [[Fraction(1), Fraction(1), Fraction(0)],
            [Fraction(1), Fraction(1), Fraction(1)],
            [Fraction(0), Fraction(1), Fraction(1)]]
    try:
        verify_block_ldl_inertia(M_ov, [0, 1, 2], mat_eye(3), M_ov)
        raise RuntimeError("Accepted overlapping 2x2 blocks!")
    except ValueError:
        forgeries_rejected += 1
    # 7b: Repeated permutation index
    M_diag = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(-1)]]
    try:
        verify_block_ldl_inertia(M_diag, [0, 0], mat_eye(2), [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]])
        raise RuntimeError("Accepted repeated permutation index!")
    except ValueError:
        forgeries_rejected += 1
    # 7c: Non-lower-triangular L
    L_bad = [[Fraction(1), Fraction(1)], [Fraction(1), Fraction(1)]]
    M_22 = [[Fraction(2), Fraction(2)], [Fraction(2), Fraction(2)]]
    try:
        verify_block_ldl_inertia(M_22, [0, 1], L_bad, mat_eye(2))
        raise RuntimeError("Accepted upper-triangular nonzero in L!")
    except ValueError:
        forgeries_rejected += 1
    # 7d: Float JSON rejection
    try:
        loads_strict_json('{"x": 1.5}')
        raise RuntimeError("Accepted float in strict JSON!")
    except ValueError:
        forgeries_rejected += 1
    # 7e: Duplicate JSON key rejection
    try:
        loads_strict_json('{"x": "1", "x": "2"}')
        raise RuntimeError("Accepted duplicate JSON key!")
    except ValueError:
        forgeries_rejected += 1
    # 7f: Non-canonical rational strings ("007", "-0", "2/4", "0/5", "01/2", "3/1", "1_000", "\u0661/\u0662")
    for bad_s in ("007", "-0", "2/4", "0/5", "01/2", "3/1", "1_000", " 1/2", "\u0661/\u0662"):
        try:
            to_frac(bad_s)
            raise RuntimeError(f"Accepted non-canonical rational string {bad_s!r}!")
        except ValueError:
            pass
    forgeries_rejected += 1
    # 7g: Direct Python API float entry & ragged congruence rejection
    try:
        verify_block_ldl_inertia([[1.0]], [0], [[Fraction(1)]], [[Fraction(1)]])  # type: ignore[list-item]
        raise RuntimeError("Accepted float matrix in verify_block_ldl_inertia!")
    except ValueError:
        pass
    try:
        verify_general_congruence_inertia(
            [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]],
            [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1), Fraction(99)]],
            mat_eye(2),
            [Fraction(1), Fraction(1)],
        )
        raise RuntimeError("Accepted ragged C in verify_general_congruence_inertia!")
    except ValueError:
        pass
    forgeries_rejected += 1

    report["checks"]["random_property_and_dominance"] = {
        "trials": n_trials,
        "seed": 20261120,
        "theorem_violations": 0,
        "dominance_violations_vs_loom_doc10": 0,
        "dominance_violations_vs_session2": 0,
        "exact_square_identities_verified_doc10": exact_dom_doc10_identities,
        "exact_square_identities_verified_session2": exact_dom_s2_identities,
        "max_margin_over_doc10_float": round(float(max_gap_over_doc10), 4),
        "max_margin_over_session2_c2_float": round(float(max_gap_over_s2), 4),
        "exact_tight_hits": tight_hits,
    }
    report["checks"]["adversarial_forgeries_rejected"] = {
        "rejected": forgeries_rejected,
        "expected": 7,
        "all_rejected": forgeries_rejected == 7,
    }

    # --- Check 8: Portal 1 Novel-Subspace Rank Bound rank(Pi_{W^perp} P Pi_{W^perp}) >= R_opt ---
    # Construct exact rational orthogonal subspaces W = span(e0) and W^perp = span(e1, e2, e3),
    # rotated by exact Householder U4, where P has rank 2 (one component IN W, one in W^perp)
    # so rank(P) = 2 while novel-subspace rank(Pi_{W^perp} P Pi_{W^perp}) = 1!
    U4 = exact_rational_householder([Fraction(1), Fraction(-1), Fraction(1), Fraction(1)])
    # Q has W = range(Q_+) = span(u0) (eigenvalue 10); P = 1*u0 u0^T + 3*u1 u1^T
    # (rank(P) = 2, while novel-subspace rank(Pi_{W^perp} P Pi_{W^perp}) = 1; R_opt = 8/15 in (0, 1]!)
    Q_diag4 = [[Fraction(10) if i == j == 0 else Fraction(0) for j in range(4)] for i in range(4)]
    P_diag4 = [[Fraction(1) if i == j == 0 else (Fraction(3) if i == j == 1 else Fraction(0)) for j in range(4)] for i in range(4)]
    Pi_Wperp_diag = [[Fraction(0) if i == j == 0 else (Fraction(1) if i == j else Fraction(0)) for j in range(4)] for i in range(4)]
    Q4 = mat_mul(mat_mul(U4, Q_diag4), mat_t(U4))
    P4 = mat_mul(mat_mul(U4, P_diag4), mat_t(U4))
    Pi4 = mat_mul(mat_mul(U4, Pi_Wperp_diag), mat_t(U4))
    M4 = mat_add(P4, Q4)
    rk_P4 = exact_rank(P4)
    rk_novel4 = exact_rank(mat_mul(mat_mul(Pi4, P4), Pi4))
    b4, _, _ = verify_block_ldl_inertia(Q4, *produce_block_ldl(Q4))
    ropt4 = r_opt_bound(trace(M4), trace(Q4), hs_norm_sq(M4), b4)["bound"]
    if not (rk_P4 == 2 and rk_novel4 == 1 and Fraction(0) < ropt4 <= Fraction(rk_novel4)):
        raise RuntimeError(f"Portal 1 novel-subspace bound check failed: ropt={ropt4}, rk_novel={rk_novel4}")
    # Also test 200 random exact-rational non-commuting decompositions with exact rational W = range(Q_+)
    novel_violations = 0
    for _ in range(200):
        # Pick random exact Householder frame Uf on R^4; put Q_+ on coords 0..b-1, Q_- on coords b..3
        vf = [Fraction(rng.randint(-3, 3)) for _ in range(4)]
        if all(x == 0 for x in vf):
            vf[0] = Fraction(1)
        Uf = exact_rational_householder(vf)
        b_k = rng.randint(1, 2)
        Qd = [[Fraction(rng.randint(1, 5)) if (i == j and i < b_k) else (Fraction(-rng.randint(0, 4)) if i == j else Fraction(0)) for j in range(4)] for i in range(4)]
        Pi_d = [[Fraction(1) if (i == j and i >= b_k) else Fraction(0) for j in range(4)] for i in range(4)]
        Qf = mat_mul(mat_mul(Uf, Qd), mat_t(Uf))
        Pif = mat_mul(mat_mul(Uf, Pi_d), mat_t(Uf))
        # Arbitrary non-commuting PSD P of random rank
        Pf = mat_zero(4, 4)
        for _ in range(rng.randint(0, 3)):
            pv = [Fraction(rng.randint(-2, 2)) for _ in range(4)]
            for r in range(4):
                for c in range(4):
                    Pf[r][c] += pv[r] * pv[c]
        Mf = mat_add(Pf, Qf)
        S_f = hs_norm_sq(Mf)
        if S_f == 0:
            continue
        ropt_f = r_opt_bound(trace(Mf), trace(Qf), S_f, b_k)["bound"]
        rk_nov_f = exact_rank(mat_mul(mat_mul(Pif, Pf), Pif))
        if ropt_f > Fraction(rk_nov_f):
            novel_violations += 1
    if novel_violations != 0:
        raise RuntimeError(f"Portal 1 novel-subspace bound violated {novel_violations} times!")
    report["checks"]["portal1_novel_subspace_rank"] = {
        "example_rank_P": rk_P4,
        "example_novel_subspace_rank": rk_novel4,
        "example_R_opt_exact": str(ropt4),
        "random_noncommuting_trials": 200,
        "novel_subspace_violations": novel_violations,
    }

    # --- Check 9 (SEAM-06): Exact Zero-Float Stacked-Adapter Spectral Bound Eliminating warp#15 1/N^2 Tax ---
    # 4 zone adapters (bio, math, code, astro) in R^8, each rank-2 with exact sigma_max = 1,
    # acting on disjoint 2D orthogonal blocks (so true sigma_max(sum B_k A_k) = 1!).
    # warp#15 Cauchy-Schwarz bound requires N * sum(sigma_k^2) = 4 * 4 = 16 (beta >= 4, 16x squared tax!).
    # Exact stacked Gram matrix Q_stack(s) = s G_B - G_B G_A G_B >= 0 certifies s = 1 (beta = 1)!
    # Plus Contextual Compute (`docs/08`): add a shared `"fluid dynamics"` conflict vector between bio & astro:
    #   - Opening both bio + astro causes sigma_max^2 = 4 > 1 (certified n_-(Q_stack(1)) = 1 > 0: REJECTED at s=1!)
    #   - Closing astro (g_astro = 0) restores exact sigma_max^2 = 1 (PSD at s=1) with ZERO astro activation!
    d_dim = 8
    N_zones = 4
    # Disjoint orthogonal basis blocks (rotated by exact rational Householder on R^8 for basis invariance!)
    U8 = exact_rational_householder([Fraction(1), Fraction(-1), Fraction(1), Fraction(-1), Fraction(1), Fraction(1), Fraction(-1), Fraction(1)])
    # Each adapter k uses columns 2k, 2k+1 of U8: B_k (8x2), A_k (2x8) = B_k^T => B_k A_k is rank-2 orth proj (sigma_max = 1)
    B_list = []
    A_list = []
    for k in range(N_zones):
        Bk = [[U8[row][2 * k + col] for col in range(2)] for row in range(d_dim)]
        Ak = mat_t(Bk)
        B_list.append(Bk)
        A_list.append(Ak)

    def check_stack_gram_psd(Bs: List[Mat], As: List[Mat], s_val: Fraction) -> Tuple[int, int, int]:
        # Concatenate B_stack = [B_1, ..., B_m] (d x R) and A_stack = [A_1; ...; A_m] (R x d)
        B_st = [[v for Bk in Bs for v in Bk[r]] for r in range(len(Bs[0]))]
        A_st = [row[:] for Ak in As for row in Ak]
        G_B = mat_mul(mat_t(B_st), B_st)
        G_A = mat_mul(A_st, mat_t(A_st))
        Q_s = mat_sub(mat_scale(s_val, G_B), mat_mul(mat_mul(G_B, G_A), G_B))
        return verify_block_ldl_inertia(Q_s, *produce_block_ldl(Q_s))

    # 9a: 4 disjoint orthogonal adapters at s = 1 (exact!)
    in_disjoint = check_stack_gram_psd(B_list, A_list, Fraction(1))
    if in_disjoint[1] != 0:
        raise RuntimeError(f"4 orthogonal adapters should be PSD at s=1, got inertia {in_disjoint}")
    # Must fail at s = 99/100 (since true sigma_max^2 == 1)
    in_disjoint_tight = check_stack_gram_psd(B_list, A_list, Fraction(99, 100))
    if in_disjoint_tight[1] == 0:
        raise RuntimeError("Tightness check failed: accepted s = 99/100 < 1!")

    # 9b: Shared `"fluid dynamics"` carrier vector u0 between bio (k=0) and astro (k=3)
    # Put astro's first basis vector on u0 (same as bio's first basis vector -> constructive interference 2 * u0 u0^T, sigma_max^2 = 4!)
    B_astro_shared = [[U8[row][0], U8[row][7]] for row in range(d_dim)]
    A_astro_shared = mat_t(B_astro_shared)
    # Both bio + astro open -> fails s = 1 (negative inertia = 1!), passes s = 4!
    in_both_s1 = check_stack_gram_psd([B_list[0], B_astro_shared], [A_list[0], A_astro_shared], Fraction(1))
    in_both_s4 = check_stack_gram_psd([B_list[0], B_astro_shared], [A_list[0], A_astro_shared], Fraction(4))
    # Contextual Compute gate closes astro (g_astro = 0) -> bio alone passes s = 1!
    in_bio_only_s1 = check_stack_gram_psd([B_list[0]], [A_list[0]], Fraction(1))
    if not (in_both_s1[1] == 1 and in_both_s4[1] == 0 and in_bio_only_s1[1] == 0):
        raise RuntimeError("Contextual Compute stacked-adapter gating check failed!")

    report["checks"]["seam06_warp15_stacked_adapter_gram"] = {
        "N_orthogonal_adapters": N_zones,
        "warp15_cauchy_schwarz_s_bound": N_zones * N_zones,
        "exact_Q_stack_s_bound": 1,
        "squared_tax_eliminated_factor": N_zones * N_zones,
        "disjoint_inertia_at_s1": list(in_disjoint),
        "disjoint_inertia_at_s_99_100": list(in_disjoint_tight),
        "shared_carrier_bio_plus_astro_inertia_at_s1": list(in_both_s1),
        "shared_carrier_bio_plus_astro_inertia_at_s4": list(in_both_s4),
        "contextual_gate_astro_closed_bio_only_inertia_at_s1": list(in_bio_only_s1),
    }

    # --- Check 10 (Portal 11): project-asma Exact PGL(2) Mobius Cross-Ratio Invariant ---
    # In Foundation-0/project-asma/formal/AsmaIdentifiabilityProofs.lean, the compartment
    # observation map q(p; r, c) = (r*p + c*(1-p)) / (r*p + (1-p)) is a non-degenerate
    # PGL(2) Mobius transformation (det = r*(1-c) != 0) with universal fixed point q(1) = 1.
    # Therefore BOTH the 4-point cross-ratio CR(q1, q2; q3, q4) == CR(p1, p2; p3, p4) AND
    # the 3-point fixed-point cross-ratio CR(q1, q2; q3, 1) == CR(p1, p2; p3, 1) cancel
    # BOTH nuisance parameters (r, c) identically across all four Lean worlds S, C25, C50, C75
    # (and arbitrary rational r > 0, c < 1), while a 3-compartment / density-dependent
    # model r(p) = r0 + alpha*p breaks the invariant strictly!
    def asma_q(p_val: Fraction, r_val: Fraction, c_val: Fraction) -> Fraction:
        return (r_val * p_val + c_val * (Fraction(1) - p_val)) / (
            r_val * p_val + (Fraction(1) - p_val)
        )

    def cross_ratio(x1: Fraction, x2: Fraction, x3: Fraction, x4: Fraction) -> Fraction:
        return ((x1 - x3) * (x2 - x4)) / ((x1 - x4) * (x2 - x3))

    p_quad = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 5), Fraction(2, 5))
    cr4_p = cross_ratio(*p_quad)
    cr3_p = cross_ratio(p_quad[0], p_quad[1], p_quad[2], Fraction(1))
    asma_worlds = [
        ("S", Fraction(16), Fraction(0)),
        ("C25", Fraction(11), Fraction(1, 4)),
        ("C50", Fraction(6), Fraction(1, 2)),
        ("C75", Fraction(1), Fraction(3, 4)),
        ("generic_rational", Fraction(37, 5), Fraction(2, 11)),
    ]
    world_results = []
    for w_name, r_w, c_w in asma_worlds:
        qs = [asma_q(pv, r_w, c_w) for pv in p_quad]
        cr4_q = cross_ratio(*qs)
        cr3_q = cross_ratio(qs[0], qs[1], qs[2], Fraction(1))
        if cr4_q != cr4_p or cr3_q != cr3_p:
            raise RuntimeError(f"Portal 11 Mobius cross-ratio broken on world {w_name}!")
        world_results.append({
            "world": w_name,
            "r": str(r_w),
            "c": str(c_w),
            "CR4_q": str(cr4_q),
            "CR3_q_fixed1": str(cr3_q),
            "exact_invariant": True,
        })
    # Negative control: non-Mobius density-dependent yield r(p) = 6 + 10*p breaks BOTH cross-ratios!
    qs_nonmob = [asma_q(pv, Fraction(6) + Fraction(10) * pv, Fraction(1, 2)) for pv in p_quad]
    cr4_nonmob = cross_ratio(*qs_nonmob)
    cr3_nonmob = cross_ratio(qs_nonmob[0], qs_nonmob[1], qs_nonmob[2], Fraction(1))
    if cr4_nonmob == cr4_p or cr3_nonmob == cr3_p:
        raise RuntimeError("Portal 11 non-Mobius negative control failed to break cross-ratio!")

    report["checks"]["portal11_asma_mobius_cross_ratio"] = {
        "p_seeds": [str(pv) for pv in p_quad],
        "CR4_p": str(cr4_p),
        "CR3_p_fixed1": str(cr3_p),
        "worlds_verified": world_results,
        "non_mobius_3comp_falsifier": {
            "CR4_non_mobius": str(cr4_nonmob),
            "CR3_non_mobius": str(cr3_nonmob),
            "breaks_cross_ratio_identically": (cr4_nonmob != cr4_p and cr3_nonmob != cr3_p),
        },
    }
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args(argv)
    rep = run_suite()
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print("=== optimal_inertia_rank.py: ALL CHECKS PASSED (exact decision paths zero-float; Check 5 sampled/float) ===")
        c = rep["checks"]
        print(f"1. Session 2 Mode B exploit: naive forged bound={c['session2_mode_b_exploit']['naive_forged_bound_on_2x2']} on 2x2; patched TCB rejected={c['session2_mode_b_exploit']['patched_tcb_rejected_with_P_NOT_PSD']}")
        print(f"2. Scale invariance (lam=1/100..100): R_opt=2 at ALL 5 scales; R_loom_doc10 ranges {[r['R_loom_doc10'] for r in c['scale_invariance_and_dominance']]}; S2(c=2)={c['scale_invariance_and_dominance'][0]['R_session2_c2']}")
        print(f"3. Exact rational Householder basis invariance: b={c['basis_invariance_householder']['exact_b_after_rotation']}, R_opt={c['basis_invariance_householder']['exact_R_opt_after_rotation']}")
        pa = c["project_asma_3component_chimeric"]
        pa_lo = pa["below_threshold_tau_1_5000"]
        pa_hi = pa["above_threshold_tau_1_1000"]
        print(f"4. project-asma 3-component chimeric (Delta_t*={pa['critical_slack_Delta_t_star']}): below thresh R_opt={pa_lo['R_opt_cert']['R_opt_float']} (CERTIFIES >=2 vs ModeA_net={pa_lo['Mode_A_c1_net_of_b']}, S2={pa_lo['Session2_Mode_B_c2_b1']}, loom={pa_lo['loom_doc10_R_G']}); above thresh unknown-Q={pa_hi['unknown_Q_R_opt_float']}, known-Q-sub={pa_hi['known_Q_subtracted_b0_R_opt_float']}; null rejected={pa['single_chimeric_negative_control_rejected']}")
        print(f"5. S1<->S2 spectral entropy bridge: verified exact rank >= r_eff >= R_2 across {len(c['session1_session2_entropy_bridge'])} spectra")
        rp = c["random_property_and_dominance"]
        print(f"6. Random property test ({rp['trials']} non-commuting rational matrices): 0 violations; {rp['exact_square_identities_verified_doc10']} doc10 & {rp['exact_square_identities_verified_session2']} S2 exact square identities verified")
        print(f"7. Adversarial forgeries rejected: {c['adversarial_forgeries_rejected']['rejected']}/{c['adversarial_forgeries_rejected']['expected']}")
        p1 = c["portal1_novel_subspace_rank"]
        print(f"8. Portal 1 novel-subspace rank: rank(P)={p1['example_rank_P']}, rank(Pi_Wperp P Pi_Wperp)={p1['example_novel_subspace_rank']}, R_opt={p1['example_R_opt_exact']} ({p1['random_noncommuting_trials']} trials, {p1['novel_subspace_violations']} violations)")
        s6 = c["seam06_warp15_stacked_adapter_gram"]
        print(f"9. SEAM-06 warp#15 stacked Gram (N={s6['N_orthogonal_adapters']}): CS tax s={s6['warp15_cauchy_schwarz_s_bound']} -> exact Q_stack s={s6['exact_Q_stack_s_bound']} ({s6['squared_tax_eliminated_factor']}x eliminated); shared bio+astro at s=1 inertia={s6['shared_carrier_bio_plus_astro_inertia_at_s1']} vs astro-closed={s6['contextual_gate_astro_closed_bio_only_inertia_at_s1']}")
        p11 = c["portal11_asma_mobius_cross_ratio"]
        print(f"10. Portal 11 project-asma PGL(2) Mobius cross-ratio: CR4={p11['CR4_p']}, CR3(q(1)=1)={p11['CR3_p_fixed1']} exact across all {len(p11['worlds_verified'])} Lean/rational worlds; non-Mobius breaks ({p11['non_mobius_3comp_falsifier']['CR4_non_mobius']} != {p11['CR4_p']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
