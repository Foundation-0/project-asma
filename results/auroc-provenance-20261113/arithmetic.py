"""Exact AUROC identities for the discovery-score provenance check.

The functions operate on scores already in memory or on frozen aggregate
fractions. They do not read workbooks, and they do not interpret a
discrimination statistic as clinical utility.
"""

from __future__ import annotations

import math
import random
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction


PRINTED_DISCOVERY_AUC = Fraction(83, 100)
TOLERANCE = Fraction(2, 100)
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20261113


def inverse_normal_cdf(p: float) -> float:
    """Acklam rational approximation of the standard normal quantile."""
    if not 0.0 < p < 1.0:
        raise ValueError("probability must be in (0, 1)")
    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    )
    plow = 0.02425
    phigh = 1 - plow
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
        )
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
        )
    q = p - 0.5
    r = q * q
    return (
        (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
        / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    )


def fraction_parts(value: Fraction) -> dict:
    return {"numerator": value.numerator, "denominator": value.denominator}


def pair_counts(positives, negatives) -> dict:
    concordant = discordant = tied = 0
    for positive in positives:
        for negative in negatives:
            if positive > negative:
                concordant += 1
            elif positive < negative:
                discordant += 1
            else:
                tied += 1
    total = concordant + discordant + tied
    if total != len(positives) * len(negatives):
        raise ValueError("pair count does not match the class product")
    auc = Fraction(2 * concordant + tied, 2 * total)
    return {
        "concordant": concordant,
        "discordant": discordant,
        "tied": tied,
        "pairs": total,
        "auc": auc,
    }


def rank_auc(positives, negatives) -> Fraction:
    """Average-rank AUROC. Ties share the mean of the ranks they occupy."""
    labels = [1] * len(positives) + [0] * len(negatives)
    ordered = sorted(zip(list(positives) + list(negatives), labels), key=lambda pair: pair[0])
    rank_start = 1
    positive_rank_sum = Fraction(0)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][0] == ordered[index][0]:
            end += 1
        width = end - index
        average_rank = Fraction(2 * rank_start + width - 1, 2)
        positive_rank_sum += average_rank * sum(label for _, label in ordered[index:end])
        rank_start += width
        index = end
    positives_n = len(positives)
    negatives_n = len(negatives)
    return (positive_rank_sum - Fraction(positives_n * (positives_n + 1), 2)) / (
        positives_n * negatives_n
    )


def half_up(value: Fraction, places: int) -> str:
    quantum = Decimal("1").scaleb(-places)
    decimal = Decimal(value.numerator) / Decimal(value.denominator)
    return str(decimal.quantize(quantum, rounding=ROUND_HALF_UP))


def delong_components(positives, negatives) -> tuple[Fraction, Fraction, Fraction]:
    """Return (AUC, s10, s01) for the DeLong structural-component variance.

    s10 is the sample variance of the positive placements. s01 is the sample
    variance of the negative placements. Both use the n-1 divisor.
    """
    m = len(positives)
    n = len(negatives)
    if m < 2 or n < 2:
        raise ValueError("DeLong variance needs at least two scores in each class")
    v10 = []
    for positive in positives:
        concordant = sum(positive > negative for negative in negatives)
        tied = sum(positive == negative for negative in negatives)
        v10.append(Fraction(2 * concordant + tied, 2 * n))
    v01 = []
    for negative in negatives:
        concordant = sum(positive > negative for positive in positives)
        tied = sum(positive == negative for positive in positives)
        v01.append(Fraction(2 * concordant + tied, 2 * m))
    theta = sum(v10, Fraction(0)) / m
    s10 = sum((value - theta) ** 2 for value in v10) / (m - 1)
    s01 = sum((value - theta) ** 2 for value in v01) / (n - 1)
    return theta, s10, s01


def delong_interval(auc: Fraction, s10: Fraction, s01: Fraction, m: int, n: int) -> dict:
    variance = s10 / m + s01 / n
    se = math.sqrt(float(variance))
    z = inverse_normal_cdf(0.975)
    center = float(auc)
    lower = center - z * se
    upper = center + z * se
    return {
        "z_975": z,
        "variance_numerator": variance.numerator,
        "variance_denominator": variance.denominator,
        "standard_error": se,
        "lower": lower,
        "upper": upper,
        "contains_printed_0_83": lower <= float(PRINTED_DISCOVERY_AUC) <= upper,
    }


def stratified_bootstrap_numerators(positives, negatives, resamples: int, seed: int) -> list[int]:
    """Return 2*concordant+tied for each stratified resample.

    The denominator of every replicate is 2 * n_positive * n_negative.
    """
    m = len(positives)
    n = len(negatives)
    rng = random.Random(seed)
    numerators = []
    for _ in range(resamples):
        draw_pos = [positives[rng.randrange(m)] for _ in range(m)]
        draw_neg = [negatives[rng.randrange(n)] for _ in range(n)]
        counts = pair_counts(draw_pos, draw_neg)
        numerators.append(2 * counts["concordant"] + counts["tied"])
    return numerators


def percentile_type7(values: list[float], p: float) -> float:
    if not values or not 0.0 <= p <= 1.0:
        raise ValueError("percentile inputs are out of range")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * p
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def bootstrap_interval(numerators: list[int], denominator: int) -> dict:
    values = [numerator / denominator for numerator in numerators]
    lower = percentile_type7(values, 0.025)
    upper = percentile_type7(values, 0.975)
    return {
        "lower": lower,
        "upper": upper,
        "mean": sum(values) / len(values),
        "contains_printed_0_83": lower <= float(PRINTED_DISCOVERY_AUC) <= upper,
    }
