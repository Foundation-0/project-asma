"""Exact bounds for sensitive-patient counts stated on 11 November 2026.

The counts are the ones written in those notes. This file does not audit a
cohort and does not read a study file. A zero-false-positive bound is
``0.05 ** (1 / n)``, the same quantity as ``tools/analyze_validation_capacity.py``.
"""

import math
import argparse


STATED_N = (10, 13, 22, 44, 83, 115, 149, 236)
FALSE_POSITIVES = (0, 1, 2)
ALPHA = 0.05

# Two-sided 95% intervals the notes reported, recomputed for these fractions.
# 26 * 166 = 4,316 = 52 * 83. The audited discovery split remains 52 and 83.
STATED_FRACTIONS = (
    (26, 9),
    (166, 163),
    (20, 7),
    (80, 78),
)


def _log_pmf(n, j, p):
    if p <= 0.0:
        return 0.0 if j == 0 else float("-inf")
    if p >= 1.0:
        return 0.0 if j == n else float("-inf")
    return (math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
            + j * math.log(p) + (n - j) * math.log(1.0 - p))


def _upper_tail(n, successes, p):
    """Probability of at least ``successes`` successes in ``n`` trials."""
    if successes <= 0:
        return 1.0
    if successes > n:
        return 0.0
    logs = [_log_pmf(n, j, p) for j in range(successes, n + 1)]
    peak = max(logs)
    return math.exp(peak) * sum(math.exp(item - peak) for item in logs)


def lower_specificity(n, false_positives, alpha=ALPHA):
    """One-sided Clopper-Pearson lower bound after ``false_positives`` errors."""
    if type(n) is not int or n < 1 or type(false_positives) is not int:
        raise ValueError("n and false_positives must be integers")
    if false_positives < 0 or false_positives > n:
        raise ValueError("false_positives must lie between 0 and n")
    if false_positives == 0:
        return float(alpha) ** (1.0 / n)
    successes = n - false_positives
    low, high = 0.0, 1.0
    for _ in range(80):
        mid = (low + high) / 2.0
        if _upper_tail(n, successes, mid) > alpha:
            high = mid
        else:
            low = mid
    return (low + high) / 2.0


def minimum_n(false_positives, target=0.98, alpha=ALPHA):
    """Smallest n whose bound at this false-positive count reaches ``target``."""
    n = false_positives
    while n < 10000:
        n += 1
        if lower_specificity(n, false_positives, alpha) >= target:
            return n
    raise ValueError("required count exceeds supported range")


def two_sided_interval(n, successes, alpha=0.05):
    """Clopper-Pearson interval with equal tails of ``alpha / 2``."""
    if type(n) is not int or type(successes) is not int or not 0 <= successes <= n or n < 1:
        raise ValueError("successes must lie between 0 and n")
    tail = alpha / 2.0
    low, high = 0.0, 1.0
    for _ in range(80):
        mid = (low + high) / 2.0
        if _upper_tail(n, successes, mid) > tail:
            high = mid
        else:
            low = mid
    lower = (low + high) / 2.0
    low, high = 0.0, 1.0
    for _ in range(80):
        mid = (low + high) / 2.0
        # P(X <= successes) = 1 - P(X >= successes + 1).
        cdf = 1.0 - _upper_tail(n, successes + 1, mid)
        if cdf > tail:
            low = mid
        else:
            high = mid
    upper = (low + high) / 2.0
    return lower, upper


def percent(value):
    return round(100.0 * value + 1e-12, 2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if minimum_n(0) != 149 or minimum_n(1) != 236:
        raise SystemExit("sample-size minimum changed")
    for n in STATED_N:
        if abs(lower_specificity(n, 0) - (0.05 ** (1.0 / n))) > 1e-12:
            raise SystemExit(f"zero-error bound drifted for n={n}")
    rows = []
    for n in STATED_N:
        bounds = [percent(lower_specificity(n, k)) for k in FALSE_POSITIVES]
        rows.append((n, bounds))
        print(f"{n:4d}  " + "  ".join(f"{item:6.2f}%" for item in bounds))
    print("minima", minimum_n(0), minimum_n(1), minimum_n(2))
    for n, successes in STATED_FRACTIONS:
        lower, upper = two_sided_interval(n, successes)
        print(f"{successes}/{n}  {percent(successes / n):6.2f}%  {percent(lower):6.2f}% to {percent(upper):6.2f}%")
    if args.check:
        print("stated specificity bounds match")


if __name__ == "__main__":
    main()
