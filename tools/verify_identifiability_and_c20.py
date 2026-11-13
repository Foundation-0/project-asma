#!/usr/bin/env python3
"""Zero-dependency verification for compartment bounds, paralog bleed, and C20."""
from fractions import Fraction
import math, random

def q_frac(p, r, c):
    return (r * p + c * (1 - p)) / (r * p + (1 - p))

def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def norm_ppf(p):
    lo, hi = -6.0, 6.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if norm_cdf(mid) < p: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)

def mw_auc(pos, neg):
    u = sum(1.0 if x > y else (0.5 if x == y else 0.0) for x in pos for y in neg)
    return u / (len(pos) * len(neg)), u

def main():
    worlds = {"S": (16, 0), "C25": (11, Fraction(1,4)), "C50": (6, Fraction(1,2)), "C75": (1, Fraction(3,4))}
    for r, c in worlds.values():
        assert q_frac(Fraction(1,5), r, c) == Fraction(4,5)
    for c in [Fraction(1,4), Fraction(1,2), Fraction(3,4)]:
        r = 16 - 20 * c
        for p in [Fraction(0,1), Fraction(1,20), Fraction(1,10), Fraction(3,8)]:
            assert q_frac(p, 16, 0) - q_frac(p, r, c) == c * (5*p - 1)*(1 - p) / ((15*p + 1)*((15 - 20*c)*p + 1))
            assert (1 - c) * q_frac(p, r, 0) + c == q_frac(p, r, c)
    dS = q_frac(Fraction(3,8), 16, 0) - q_frac(Fraction(1,20), 16, 0)
    eps_c50 = (dS - (q_frac(Fraction(3,8), 6, Fraction(1,2)) - q_frac(Fraction(1,20), 6, Fraction(1,2)))) / 4
    eps_c25 = (dS - (q_frac(Fraction(3,8), 11, Fraction(1,4)) - q_frac(Fraction(1,20), 11, Fraction(1,4)))) / 4
    assert eps_c50 == Fraction(9451, 213325) and eps_c25 == Fraction(10179, 563920) > Fraction(1, 60)

    w_in, w_cr = 863 / 4316.0, 3453 / 4316.0
    req_cr = (float(Fraction(3491, 4316)) - w_in * 0.83) / w_cr
    d_p = math.sqrt(2.0) * norm_ppf(0.83)
    rho = math.sqrt((d_p / (math.sqrt(2.0) * norm_ppf(req_cr))) ** 2 - 1.0)
    rng = random.Random(20261113)
    f1, f2 = [11, 11, 10, 10, 10], [17, 16, 17, 17, 16]
    hit = False
    for _ in range(3000):
        fa, pr, nr = [], [], []
        for k in range(5):
            dk = rng.gauss(0.0, rho)
            pk = [d_p + rng.gauss(0.0, 1.0) + dk for _ in range(f1[k])]
            nk = [rng.gauss(0.0, 1.0) + dk for _ in range(f2[k])]
            fa.append(mw_auc(pk, nk)[0]); pr.extend(pk); nr.extend(nk)
        _, u = mw_auc(pr, nr)
        if u == 3491 and abs(sum(fa)/5.0 - 0.83) < 0.0025:
            hit = True; break
    assert hit
    print("OK: all exact rational and C20 shift-attenuation checks passed.")

if __name__ == "__main__":
    main()
