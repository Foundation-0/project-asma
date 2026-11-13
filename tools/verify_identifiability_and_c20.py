#!/usr/bin/env python3
"""Exact rational checks for compartment identifiability and paralog bleed, plus a
fitted consistency check for Conjecture C20 (Pilot 001 fold-wise AUROC).

Part 1 is exact arithmetic with fractions.Fraction. It mirrors
formal/AsmaIdentifiabilityProofs.lean.

Part 2 is a fitted consistency check and makes no prediction. It solves the
fold-shift spread rho from two observed inputs (pooled U = 3491 of 4316 pairs and
the printed fold mean 0.83), fixes rho, and then simulates the model to report
the pooled and fold-mean AUROC it produces. Agreement with 3491/4316 shows the
model can reproduce the inputs it was fitted to. It is not independent evidence
for C20, which stays a CONJECTURE in CLAIMS.md.
"""
from fractions import Fraction
import math
import random

N_POS, N_NEG = 52, 83
TOTAL_PAIRS = N_POS * N_NEG
U_OBSERVED = 3491
PRINTED_FOLD_MEAN = 0.83
# Balanced stratified split: every fold has 27 samples.
FOLD_POS = [11, 11, 10, 10, 10]
FOLD_NEG = [16, 16, 17, 17, 17]
SEED = 20261113
TRIALS = 3000


def q_frac(p, r, c):
    return (r * p + c * (1 - p)) / (r * p + (1 - p))


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p):
    lo, hi = -6.0, 6.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def mw_auc(pos, neg):
    u = sum(1.0 if x > y else (0.5 if x == y else 0.0) for x in pos for y in neg)
    return u / (len(pos) * len(neg)), u


def check_exact_rationals():
    worlds = {
        "S": (16, Fraction(0)),
        "C25": (11, Fraction(1, 4)),
        "C50": (6, Fraction(1, 2)),
        "C75": (1, Fraction(3, 4)),
    }
    for r, c in worlds.values():
        assert q_frac(Fraction(1, 5), r, c) == Fraction(4, 5)
    for c in [Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)]:
        r = 16 - 20 * c
        for p in [Fraction(0), Fraction(1, 20), Fraction(1, 10), Fraction(3, 8)]:
            assert q_frac(p, 16, 0) - q_frac(p, r, c) == c * (5 * p - 1) * (1 - p) / (
                (15 * p + 1) * ((15 - 20 * c) * p + 1)
            )
            assert (1 - c) * q_frac(p, r, 0) + c == q_frac(p, r, c)
            # Survival-ratio pencil: Phi(p) = (1 - p) / (1 - q) = ((r - 1) * p + 1) / (1 - c).
            if p != 1:
                assert (1 - p) / (1 - q_frac(p, r, c)) == ((r - 1) * p + 1) / (1 - c)
        assert (1 - Fraction(1, 5)) / (1 - q_frac(Fraction(1, 5), r, c)) == 4

    low, high = Fraction(1, 20), Fraction(3, 8)
    assert q_frac(low, 11, Fraction(1, 4)) == Fraction(21, 40)
    contrast = {k: q_frac(high, r, c) - q_frac(low, r, c) for k, (r, c) in worlds.items()}
    eps = {
        (a, b): abs(contrast[a] - contrast[b]) / 4
        for i, a in enumerate(worlds)
        for b in list(worlds)[i + 1:]
    }
    assert eps[("S", "C25")] == Fraction(10179, 563920)
    assert eps[("S", "C50")] == Fraction(9451, 213325)
    assert eps[("S", "C75")] == Fraction(21801, 237440)
    assert eps[("C25", "C50")] == Fraction(4589, 174800)
    assert eps[("C25", "C75")] == Fraction(897, 12160)
    assert eps[("C50", "C75")] == Fraction(3497, 73600)
    assert all(v > Fraction(1, 60) for v in eps.values())
    assert min(eps.values()) == Fraction(10179, 563920)
    return eps


def fit_shift_spread(within_pairs):
    """Solve rho from the observed pooled AUROC and the printed fold mean.

    Model: pooled AUROC = w_in * fold AUROC + w_cr * cross-fold AUROC, where a
    Gaussian fold shift of spread rho lowers the cross-fold binormal AUROC.
    Both observed numbers are inputs, so this is a fit.
    """
    w_in = within_pairs / TOTAL_PAIRS
    w_cr = 1.0 - w_in
    req_cross = (U_OBSERVED / TOTAL_PAIRS - w_in * PRINTED_FOLD_MEAN) / w_cr
    d_prime = math.sqrt(2.0) * norm_ppf(PRINTED_FOLD_MEAN)
    rho = math.sqrt((d_prime / (math.sqrt(2.0) * norm_ppf(req_cross))) ** 2 - 1.0)
    return d_prime, req_cross, rho


def simulate(d_prime, rho, trials=TRIALS, seed=SEED):
    rng = random.Random(seed)
    pooled, fold_means = [], []
    for _ in range(trials):
        fa, pr, nr = [], [], []
        for k in range(5):
            dk = rng.gauss(0.0, rho)
            pk = [d_prime + rng.gauss(0.0, 1.0) + dk for _ in range(FOLD_POS[k])]
            nk = [rng.gauss(0.0, 1.0) + dk for _ in range(FOLD_NEG[k])]
            fa.append(mw_auc(pk, nk)[0])
            pr.extend(pk)
            nr.extend(nk)
        pooled.append(mw_auc(pr, nr)[0])
        fold_means.append(sum(fa) / 5.0)
    return sum(pooled) / trials, sum(fold_means) / trials


def main():
    check_exact_rationals()

    assert sum(FOLD_POS) == N_POS and sum(FOLD_NEG) == N_NEG
    assert all(a + b == 27 for a, b in zip(FOLD_POS, FOLD_NEG))
    within = sum(a * b for a, b in zip(FOLD_POS, FOLD_NEG))
    assert within == 862 and TOTAL_PAIRS - within == 3454

    d_prime, req_cross, rho = fit_shift_spread(within)
    mean_pooled, mean_fold = simulate(d_prime, rho)
    mean_pooled_no_shift, mean_fold_no_shift = simulate(d_prime, 0.0)
    target = U_OBSERVED / TOTAL_PAIRS
    print("C20 fitted consistency check (fit inputs: U = 3491 of 4316, fold mean 0.83)")
    print(f"  fitted rho = sigma_delta/sigma_s = {rho:.6f}, d' = {d_prime:.6f}, cross-fold AUROC = {req_cross:.6f}")
    print(f"  model at fitted rho, {TRIALS} draws, seed {SEED}: mean pooled AUROC {mean_pooled:.5f}, mean fold AUROC {mean_fold:.5f}")
    print(f"  model at rho = 0: mean pooled AUROC {mean_pooled_no_shift:.5f}, mean fold AUROC {mean_fold_no_shift:.5f}")
    print(f"  observed pooled AUROC 3491/4316 = {target:.5f}")
    # The fitted model should land near the inputs it was fitted to.
    assert abs(mean_pooled - target) < 0.01
    assert abs(mean_fold - PRINTED_FOLD_MEAN) < 0.01
    print("OK: exact rational checks passed; C20 fitted model is consistent with its fit inputs.")


if __name__ == "__main__":
    main()
