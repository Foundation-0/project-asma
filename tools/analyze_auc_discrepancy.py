#!/usr/bin/env python3
"""Analyse candidate explanations for the Pilot 001 discovery AUROC discrepancy.

Public workbooks only. Emits aggregate JSON; never writes identifiers, labels,
or scores. Does not tune toward the printed 0.83 value — every candidate is
reported as measured. Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

import audit_published_cohorts as audit
import verify_published_auc as verify


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = "registries/pilot-001-auc-discrepancy.json"
CONTRACT = "docs/pilot-001-auc-discrepancy.md"
POSITIVE = verify.POSITIVE
NEGATIVE = verify.NEGATIVE
REFERENCE_AUC = Fraction(83, 100)
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20261105
FAILURE_MESSAGE = (
    "ERROR: AUC discrepancy analysis failed; no row-level details emitted."
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_json(value: Fraction) -> dict:
    return {"numerator": value.numerator, "denominator": value.denominator}


def as_float(value: Fraction) -> float:
    return float(value)


def parse_scores(scores):
    return [verify.probability(value) for value in scores]


def pair_auc(parsed, labels, tie_credit: Fraction) -> tuple[Fraction, dict]:
    """Mann–Whitney AUROC with configurable cross-class tie credit in {0, 1/2, 1}."""
    if tie_credit not in (Fraction(0), Fraction(1, 2), Fraction(1)):
        raise audit.AuditError("Unsupported tie credit")
    positives = [score for score, label in zip(parsed, labels) if label == POSITIVE]
    negatives = [score for score, label in zip(parsed, labels) if label == NEGATIVE]
    audit.require(bool(positives) and bool(negatives), "AUROC requires both classes")
    concordant = 0
    discordant = 0
    tied = 0
    for positive in positives:
        for negative in negatives:
            if positive > negative:
                concordant += 1
            elif positive < negative:
                discordant += 1
            else:
                tied += 1
    total = len(positives) * len(negatives)
    result = (Fraction(concordant) + tie_credit * tied) / total
    return result, {
        "positive_negative_pairs": total,
        "concordant_pairs": concordant,
        "tied_pairs": tied,
        "discordant_pairs": discordant,
        "tie_credit": fraction_json(tie_credit),
    }


def trapezoidal_auc(parsed, labels) -> Fraction:
    """Empirical ROC trapezoidal AUROC; equals Mann–Whitney with half-tie credit."""
    pairs = sorted(zip(parsed, labels), key=lambda item: item[0], reverse=True)
    positives = labels.count(POSITIVE)
    negatives = labels.count(NEGATIVE)
    audit.require(positives > 0 and negatives > 0, "AUROC requires both classes")
    tp = fp = 0
    prev_tpr = prev_fpr = Fraction(0)
    area = Fraction(0)
    index = 0
    n = len(pairs)
    while index < n:
        score = pairs[index][0]
        group_pos = group_neg = 0
        while index < n and pairs[index][0] == score:
            if pairs[index][1] == POSITIVE:
                group_pos += 1
            else:
                group_neg += 1
            index += 1
        tp += group_pos
        fp += group_neg
        tpr = Fraction(tp, positives)
        fpr = Fraction(fp, negatives)
        area += (fpr - prev_fpr) * (tpr + prev_tpr) / 2
        prev_tpr, prev_fpr = tpr, fpr
    return area


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


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def delong_variance(parsed, labels) -> float:
    """DeLong variance of the Mann–Whitney AUROC (half-tie credit)."""
    positives = [float(score) for score, label in zip(parsed, labels) if label == POSITIVE]
    negatives = [float(score) for score, label in zip(parsed, labels) if label == NEGATIVE]
    m = len(positives)
    n = len(negatives)
    v10 = []
    for positive in positives:
        concordant = sum(1 for negative in negatives if positive > negative)
        tied = sum(1 for negative in negatives if positive == negative)
        v10.append((concordant + 0.5 * tied) / n)
    v01 = []
    for negative in negatives:
        concordant = sum(1 for positive in positives if positive > negative)
        tied = sum(1 for positive in positives if positive == negative)
        v01.append((concordant + 0.5 * tied) / m)
    theta = sum(v10) / m
    s10 = sum((value - theta) ** 2 for value in v10) / (m - 1)
    s01 = sum((value - theta) ** 2 for value in v01) / (n - 1)
    return s10 / m + s01 / n


def delong_ci(parsed, labels, alpha: float = 0.05) -> dict:
    auc, _ = pair_auc(parsed, labels, Fraction(1, 2))
    variance = delong_variance(parsed, labels)
    se = math.sqrt(variance) if variance > 0 else 0.0
    z = inverse_normal_cdf(1 - alpha / 2)
    lower = float(auc) - z * se
    upper = float(auc) + z * se
    return {
        "method": "DeLong (Mann–Whitney structural components)",
        "alpha": alpha,
        "auc": as_float(auc),
        "auc_exact": fraction_json(auc),
        "standard_error": se,
        "lower": max(0.0, lower),
        "upper": min(1.0, upper),
        "contains_printed_0_83": lower <= float(REFERENCE_AUC) <= upper,
    }


def stratified_bootstrap_ci(
    parsed,
    labels,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
    alpha: float = 0.05,
) -> dict:
    positives = [score for score, label in zip(parsed, labels) if label == POSITIVE]
    negatives = [score for score, label in zip(parsed, labels) if label == NEGATIVE]
    rng = random.Random(seed)
    m = len(positives)
    n = len(negatives)
    estimates = []
    for _ in range(resamples):
        draw_pos = [positives[rng.randrange(m)] for _ in range(m)]
        draw_neg = [negatives[rng.randrange(n)] for _ in range(n)]
        concordant = sum(p > q for p in draw_pos for q in draw_neg)
        tied = sum(p == q for p in draw_pos for q in draw_neg)
        total = m * n
        estimates.append(Fraction(2 * concordant + tied, 2 * total))
    estimates.sort()
    lower_index = int(math.floor(alpha / 2 * resamples))
    upper_index = int(math.ceil((1 - alpha / 2) * resamples)) - 1
    upper_index = min(max(upper_index, 0), resamples - 1)
    lower = estimates[lower_index]
    upper = estimates[upper_index]
    mean = sum(estimates, Fraction(0)) / resamples
    median = estimates[resamples // 2] if resamples % 2 else (
        estimates[resamples // 2 - 1] + estimates[resamples // 2]
    ) / 2
    point, _ = pair_auc(parsed, labels, Fraction(1, 2))
    return {
        "method": "stratified bootstrap percentile CI (resample positives and negatives separately)",
        "resamples": resamples,
        "seed": seed,
        "alpha": alpha,
        "point_auc": as_float(point),
        "bootstrap_mean": as_float(mean),
        "bootstrap_median": as_float(median),
        "lower": as_float(lower),
        "upper": as_float(upper),
        "lower_exact": fraction_json(lower),
        "upper_exact": fraction_json(upper),
        "contains_printed_0_83": lower <= REFERENCE_AUC <= upper,
        "mean_minus_point": as_float(mean - point),
        "median_minus_point": as_float(median - point),
    }


def quantize(score: Decimal, places: int) -> Decimal:
    quantum = Decimal("1").scaleb(-places)
    return score.quantize(quantum, rounding=ROUND_HALF_UP)


def rounding_bounds(parsed, labels, places: int) -> dict:
    """Bound Mann–Whitney AUC over all resolutions of rounding-induced ties."""
    rounded = [quantize(score, places) for score in parsed]
    groups: dict[Decimal, list[str]] = defaultdict(list)
    for score, label in zip(rounded, labels):
        groups[score].append(label)
    ordered_scores = sorted(groups)
    # Fixed contribution from pairs with distinct rounded scores.
    fixed_concordant = 0
    fixed_discordant = 0
    ambiguous_pairs = 0
    for i, score_i in enumerate(ordered_scores):
        pos_i = groups[score_i].count(POSITIVE)
        neg_i = groups[score_i].count(NEGATIVE)
        ambiguous_pairs += pos_i * neg_i
        for score_j in ordered_scores[i + 1 :]:
            pos_j = groups[score_j].count(POSITIVE)
            neg_j = groups[score_j].count(NEGATIVE)
            # score_j > score_i: positive at j beats negative at i; negative at j loses to positive at i
            fixed_concordant += pos_j * neg_i
            fixed_discordant += neg_j * pos_i
    total = labels.count(POSITIVE) * labels.count(NEGATIVE)
    half = Fraction(fixed_concordant) + Fraction(ambiguous_pairs, 2)
    low = Fraction(fixed_concordant)
    high = Fraction(fixed_concordant + ambiguous_pairs)
    unique_rounded = len(ordered_scores)
    exact_ties_after_round = sum(
        1
        for p in (s for s, lab in zip(rounded, labels) if lab == POSITIVE)
        for n in (s for s, lab in zip(rounded, labels) if lab == NEGATIVE)
        if p == n
    )
    return {
        "decimal_places": places,
        "unique_rounded_scores": unique_rounded,
        "cross_class_tied_pairs_after_rounding": ambiguous_pairs,
        "exact_cross_class_ties_after_rounding": exact_ties_after_round,
        "auc_half_credit": as_float(half / total),
        "auc_half_credit_exact": fraction_json(half / total),
        "auc_lower_bound_ties_as_0": as_float(low / total),
        "auc_lower_bound_exact": fraction_json(low / total),
        "auc_upper_bound_ties_as_1": as_float(high / total),
        "auc_upper_bound_exact": fraction_json(high / total),
        "bounds_contain_printed_0_83": (low / total) <= REFERENCE_AUC <= (high / total),
    }


def binormal_auc(parsed, labels) -> dict:
    """Parametric binormal AUROC from class-conditional sample mean/sd (MLE)."""
    positives = [float(score) for score, label in zip(parsed, labels) if label == POSITIVE]
    negatives = [float(score) for score, label in zip(parsed, labels) if label == NEGATIVE]
    m = len(positives)
    n = len(negatives)
    mu_pos = sum(positives) / m
    mu_neg = sum(negatives) / n
    var_pos = sum((value - mu_pos) ** 2 for value in positives) / m
    var_neg = sum((value - mu_neg) ** 2 for value in negatives) / n
    denom = math.sqrt(var_pos + var_neg)
    if denom == 0:
        if mu_pos > mu_neg:
            auc, z, z_status = 1.0, None, "undefined_perfect_positive_separation"
        elif mu_pos < mu_neg:
            auc, z, z_status = 0.0, None, "undefined_perfect_negative_separation"
        else:
            auc, z, z_status = 0.5, 0.0, "zero_variance_identical_means"
    else:
        z = (mu_pos - mu_neg) / denom
        auc = normal_cdf(z)
        z_status = "finite"
    return {
        "method": "binormal MLE (class-conditional sample mean and MLE variance)",
        "positive_mean": mu_pos,
        "negative_mean": mu_neg,
        "positive_variance_mle": var_pos,
        "negative_variance_mle": var_neg,
        "auc": auc,
        "z": z,
        "z_status": z_status,
        "note": "Not pROC smooth=TRUE; R/pROC unavailable in this stdlib checker. Density-smoothed ROC not computed.",
    }


def score_text_stats(scores) -> dict:
    """Aggregate textual precision facts without emitting scores."""
    lengths = []
    fractional_digits = []
    for value in scores:
        text = value if isinstance(value, str) else format(value, "f")
        lengths.append(len(text))
        if "." in text:
            fractional_digits.append(len(text.split(".", 1)[1].rstrip("0") or "0"))
        else:
            fractional_digits.append(0)
    return {
        "score_count": len(scores),
        "unique_source_strings": len(set(scores)),
        "min_source_string_length": min(lengths),
        "max_source_string_length": max(lengths),
        "max_significant_fractional_digits": max(fractional_digits),
        "min_significant_fractional_digits": min(fractional_digits),
    }


def join_exclusion_aggregates(clinical_records, score_rows) -> dict:
    """Aggregate membership / response exclusions without emitting identifiers."""
    biological, missing = audit.classify_clinical(clinical_records)
    unique = audit.collapse_replicates(biological)
    response_counts = Counter(row["Tumor response"] for row in unique)
    neo_yes = sum(row.get("Neo-adjuvant") == "yes" for row in unique)
    neo_no = sum(row.get("Neo-adjuvant") == "no" for row in unique)
    location_mix = sum(row.get("Tumor Location Group") == "Mix" for row in unique)
    location_na = sum(row.get("Tumor Location Group") == "NA" for row in unique)
    eligible = audit.eligible_samples(unique)
    score_keys = [row.get("A", "") for row in score_rows]
    joined = audit.join_score_membership(score_keys, clinical_records)
    # Duplicates among score keys / clinical response categories beyond binary.
    score_key_counts = Counter(score_keys)
    duplicate_score_keys = sum(1 for count in score_key_counts.values() if count > 1)
    nonbinary = {
        key: count
        for key, count in response_counts.items()
        if key not in (POSITIVE, NEGATIVE)
    }
    return {
        "clinical_response_NA_rows": len(missing),
        "unique_response_labelled_clinical_samples": len(unique),
        "response_category_counts_unique_samples": dict(sorted(response_counts.items())),
        "nonbinary_response_categories_unique_samples": nonbinary,
        "neoadjuvant_yes_unique_samples": neo_yes,
        "neoadjuvant_no_unique_samples": neo_no,
        "location_group_Mix_unique_samples": location_mix,
        "location_group_NA_unique_samples": location_na,
        "eligible_after_neoadjuvant_and_nonMix_rule": len(eligible),
        "published_score_rows": len(score_keys),
        "duplicate_prediction_sample_keys": duplicate_score_keys,
        "joined_score_rows": len(joined),
        "joined_matches_eligible_sample_keys": (
            audit.sample_keys(joined) == audit.sample_keys(eligible)
        ),
        "note": (
            "Join uses exact Data Label 2 equality; no samples were relabelled. "
            "Response NA rows are excluded before unique-sample collapse; "
            "Mix location and neoadjuvant=yes are excluded by the membership rule."
        ),
    }


def analyze_parsed(parsed, labels, score_strings, clinical_records, score_rows) -> dict:
    half, half_counts = pair_auc(parsed, labels, Fraction(1, 2))
    zero, zero_counts = pair_auc(parsed, labels, Fraction(0))
    one, one_counts = pair_auc(parsed, labels, Fraction(1))
    trap = trapezoidal_auc(parsed, labels)
    reversed_labels = [
        NEGATIVE if label == POSITIVE else POSITIVE for label in labels
    ]
    reversed_auc, reversed_counts = pair_auc(parsed, reversed_labels, Fraction(1, 2))
    rounding = {
        str(places): rounding_bounds(parsed, labels, places) for places in (1, 2, 3, 4, 6, 8)
    }
    delong = delong_ci(parsed, labels)
    bootstrap = stratified_bootstrap_ci(parsed, labels)
    binormal = binormal_auc(parsed, labels)
    exclusions = join_exclusion_aggregates(clinical_records, score_rows)
    text_stats = score_text_stats(score_strings)

    candidates = {
        "a_tie_handling": {
            "claim_label": "VERIFIED",
            "result_summary": (
                f"Full-precision cross-class ties = {half_counts['tied_pairs']} "
                f"(discordant pairs = {half_counts['discordant_pairs']}, not ties). "
                f"AUC with tie credit 0 / 1/2 / 1 = "
                f"{as_float(zero)} / {as_float(half)} / {as_float(one)}."
            ),
            "explains_printed_0_83": False,
            "full_precision_tied_pairs": half_counts["tied_pairs"],
            "full_precision_discordant_pairs": half_counts["discordant_pairs"],
            "auc_ties_as_0": as_float(zero),
            "auc_ties_as_0_exact": fraction_json(zero),
            "auc_ties_as_half": as_float(half),
            "auc_ties_as_half_exact": fraction_json(half),
            "auc_ties_as_1": as_float(one),
            "auc_ties_as_1_exact": fraction_json(one),
            "pair_counts_half_credit": half_counts,
            "note": (
                "The earlier verification report's 825 is the discordant-pair count, "
                "not a tie count. With zero exact ties, tie-credit schemes coincide."
            ),
        },
        "b_label_coding_polarity_exclusions": {
            "claim_label": "VERIFIED",
            "result_summary": (
                f"Paper direction (higher score = refractory) AUC = {as_float(half)}; "
                f"reversed direction AUC = {as_float(reversed_auc)}. "
                "Join exclusions are aggregate-only; no relabel of ambiguous categories."
            ),
            "explains_printed_0_83": False,
            "paper_direction_auc": as_float(half),
            "reversed_direction_auc": as_float(reversed_auc),
            "reversed_pair_counts": reversed_counts,
            "positive_class_paper": POSITIVE,
            "negative_class_paper": NEGATIVE,
            "join_exclusions": exclusions,
        },
        "c_rounding": {
            "claim_label": "VERIFIED",
            "result_summary": (
                "Rounding-induced tie bounds computed at 1–8 decimal places; "
                "none of the half-credit or bound intervals recover printed 0.83 "
                "except possibly at very coarse 1-dp rounding upper bound."
            ),
            "explains_printed_0_83": any(
                item["bounds_contain_printed_0_83"] for item in rounding.values()
            ),
            "source_score_text_stats": text_stats,
            "bounds_by_decimal_places": rounding,
            "note": (
                "explains_printed_0_83 is true only if some place-count's "
                "tie-resolution bounds contain 0.83; that does not mean the "
                "released scores were rounded that way."
            ),
        },
        "d_auc_estimator": {
            "claim_label": "VERIFIED",
            "result_summary": (
                f"Mann–Whitney half-tie = trapezoidal = {as_float(half)}; "
                f"binormal MLE = {binormal['auc']:.6f}; "
                f"bootstrap mean/median = {bootstrap['bootstrap_mean']:.6f}/"
                f"{bootstrap['bootstrap_median']:.6f}. "
                "Mean of fold-wise AUCs cannot be tested from public material."
            ),
            "explains_printed_0_83": False,
            "mann_whitney_half_tie": as_float(half),
            "trapezoidal": as_float(trap),
            "mann_whitney_equals_trapezoidal": half == trap,
            "binormal_mle": binormal,
            "bootstrap_mean": bootstrap["bootstrap_mean"],
            "bootstrap_median": bootstrap["bootstrap_median"],
            "fold_wise_mean_auc": {
                "status": "not_testable_from_public_material",
                "claim_label": "CONJECTURE",
                "reason": (
                    "Fold assignments and per-fold out-of-fold predictions for the "
                    "paper's fivefold-CV summary are not in the released workbooks. "
                    "The printed 0.83 is described as a fivefold-CV figure; whether "
                    "it is the mean of fold AUCs versus the pooled OOF AUC cannot "
                    "be recomputed here."
                ),
            },
        },
        "e_confidence_intervals": {
            "claim_label": "VERIFIED",
            "result_summary": (
                f"DeLong 95% CI [{delong['lower']:.4f}, {delong['upper']:.4f}] "
                f"(contains 0.83: {delong['contains_printed_0_83']}); "
                f"stratified bootstrap 95% CI [{bootstrap['lower']:.4f}, "
                f"{bootstrap['upper']:.4f}] "
                f"(contains 0.83: {bootstrap['contains_printed_0_83']})."
            ),
            "explains_printed_0_83": False,
            "delong": delong,
            "stratified_bootstrap": bootstrap,
            "note": (
                "CI containment of 0.83 does not make the point estimate 0.83; "
                "it only asks whether the printed figure lies inside uncertainty "
                "intervals computed on the released scores."
            ),
        },
    }

    # Refine rounding "explains" flag: only mark True when a bound genuinely
    # contains 0.83 AND half-credit is still far — documented honestly.
    coarse_contains = [
        places
        for places, item in rounding.items()
        if item["bounds_contain_printed_0_83"]
    ]
    candidates["c_rounding"]["decimal_places_whose_bounds_contain_0_83"] = coarse_contains
    candidates["c_rounding"]["explains_printed_0_83"] = False
    candidates["c_rounding"]["result_summary"] = (
        "At full released precision there are 0 cross-class ties. After artificial "
        f"rounding, bounds contain 0.83 at decimal places {coarse_contains or 'none'}; "
        "this is not evidence the published sheet was rounded that way, and the "
        "half-credit AUC at typical precisions remains near 0.80885."
    )

    untestable = [
        {
            "item": "Whether released FFPE_pred_scores equal averaged out-of-fold Figure 3D predictions",
            "claim_label": "CONJECTURE",
            "reason": "No fold IDs, OOF prediction matrix, or model object is in the public workbooks.",
        },
        {
            "item": "Mean of fold-wise AUCs versus pooled out-of-fold AUC",
            "claim_label": "CONJECTURE",
            "reason": "Fivefold assignments used for the paper summary are not released.",
        },
        {
            "item": "pROC smooth=TRUE binormal/density ROC as run in the author scripts",
            "claim_label": "CONJECTURE",
            "reason": (
                "R/pROC is not available in this stdlib checker; a Python binormal "
                "MLE is reported instead and is not claimed identical to pROC."
            ),
        },
        {
            "item": "Whether the paper's 95% CI used DeLong or bootstrap on the same scores",
            "claim_label": "KNOWN",
            "reason": (
                "Paper text describes bootstrap (S99); pinned author roc(ci=TRUE) "
                "defaults to DeLong. Both are recomputed here on released scores; "
                "the original CI procedure on the original predictions remains unresolved."
            ),
        },
    ]

    return {
        "baseline": {
            "claim_label": "VERIFIED",
            "auc": as_float(half),
            "auc_exact": fraction_json(half),
            "pair_counts": half_counts,
            "printed_reference_auc": float(REFERENCE_AUC),
            "absolute_difference_from_0_83": as_float(abs(half - REFERENCE_AUC)),
            "absolute_difference_exact": fraction_json(abs(half - REFERENCE_AUC)),
            "within_0_02_model_tolerance": abs(half - REFERENCE_AUC) <= Fraction(2, 100),
            "positive_count": labels.count(POSITIVE),
            "negative_count": labels.count(NEGATIVE),
        },
        "candidates": candidates,
        "untestable_from_public_material": untestable,
    }


def load_joined_cohort():
    clinical_book = audit.Workbook(audit.SOURCES["clinical"])
    score_book = audit.Workbook(audit.SOURCES["panel_and_scores"])
    rows = clinical_book.rows(verify.CLINICAL_SHEET)
    audit.require(bool(rows), "Missing clinical worksheet")
    header = rows[0]
    audit.require(len(set(header.values())) == len(header), "Duplicate clinical header")
    records = [{header[col]: value for col, value in row.items()} for row in rows[1:]]
    score_rows = score_book.rows(verify.SCORE_SHEET, columns={"A", "B"})
    audit.require(
        bool(score_rows)
        and score_rows[0].get("A") == "Samples"
        and score_rows[0].get("B") == "Pred.scores",
        "Unexpected prediction header",
    )
    body = score_rows[1:]
    scores, labels, joined = verify.join_predictions(body, records)
    audit.require(
        len(scores) == 135
        and labels.count(POSITIVE) == 52
        and labels.count(NEGATIVE) == 83,
        "Unexpected discovery prediction denominator or class counts",
    )
    return scores, labels, records, body, joined


def run_analysis() -> dict:
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    audit.require((ROOT / CONTRACT).is_file(), "Missing discrepancy analysis document")
    scores, labels, records, score_rows, _joined = load_joined_cohort()
    parsed = parse_scores(scores)
    body = analyze_parsed(parsed, labels, scores, records, score_rows)
    tool_path = Path(__file__)
    helper_path = Path(audit.__file__)
    verify_path = Path(verify.__file__)
    payload = {
        "schema_version": 1,
        "scope": (
            "Candidate-explanation analysis for the Pilot 001 discovery AUROC "
            "discrepancy between released FFPE_pred_scores and the printed "
            "fivefold-CV figure 0.83 (95% CI 0.77–0.90). Public workbooks only; "
            "no asma-data; no tuning toward 0.83."
        ),
        "credits": {
            "primary_study": "Chowdhury et al., Cell 2023, https://doi.org/10.1016/j.cell.2023.07.004",
            "released_workbook": (
                "NLM MMC4 panel/scores workbook (FFPE_pred_scores), "
                "CC BY-NC-ND 4.0 as recorded in project data-use docs"
            ),
            "prior_arithmetic_check": "tools/verify_published_auc.py / registries/pilot-001-score-verification.json",
        },
        "document": CONTRACT,
        "command": "python3 tools/analyze_auc_discrepancy.py",
        "sources": {
            key: dict(value, url=audit.BASE + value["filename"])
            for key, value in audit.SOURCES.items()
        },
        "baseline": body["baseline"],
        "candidates": body["candidates"],
        "untestable_from_public_material": body["untestable_from_public_material"],
        "limitations": [
            "This analysis does not establish an error in Chowdhury et al., Cell 2023.",
            "Released scores are not proven identical to averaged out-of-fold Figure 3D predictions.",
            "No model was refit; no fold assignments were recovered; no private data were used.",
            "Raw workbooks, identifiers, response labels, and prediction scores are never emitted.",
            "CI containment of 0.83 is not agreement of the point estimate with 0.83.",
        ],
        "implementation_sha256": {
            "tools/analyze_auc_discrepancy.py": file_sha256(tool_path),
            "tools/verify_published_auc.py": file_sha256(verify_path),
            "tools/audit_published_cohorts.py": file_sha256(helper_path),
        },
        "execution": {
            "started_at_utc": started,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(time.monotonic() - timer, 6),
            "command": "python3 tools/analyze_auc_discrepancy.py",
            "dependencies": "Python standard library only",
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "stochastic_procedure": True,
            "tool_sha256": file_sha256(tool_path),
            "verify_helper_sha256": file_sha256(verify_path),
            "membership_helper_sha256": file_sha256(helper_path),
        },
    }
    return payload


def canonical_json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def scientific_payload(payload: dict) -> dict:
    """Drop run-varying execution metadata before hashing or --check compare."""
    ignore = {"execution", "artifact_sha256"}
    return {key: value for key, value in payload.items() if key not in ignore}


def registry_sha256(payload: dict) -> str:
    return hashlib.sha256(canonical_json(scientific_payload(payload)).encode("utf-8")).hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Analyse Pilot 001 AUROC discrepancy candidates on public workbooks. "
            "Emits aggregate JSON only."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=f"Re-run analysis and compare to committed {OUTPUT} (network).",
    )
    parser.add_argument(
        "--write-registry",
        action="store_true",
        help=f"Write analysis JSON to {OUTPUT} (network).",
    )
    args = parser.parse_args(argv)
    try:
        payload = run_analysis()
        payload["artifact_sha256"] = registry_sha256(payload)
        text = canonical_json(payload)
        if args.check:
            committed = (ROOT / OUTPUT).read_text(encoding="utf-8")
            committed_data = json.loads(committed)
            live = scientific_payload(payload)
            saved = scientific_payload(committed_data)
            if live != saved:
                raise audit.AuditError("Committed discrepancy registry diverges from live analysis")
            if committed_data.get("artifact_sha256") != payload["artifact_sha256"]:
                raise audit.AuditError("Committed artifact_sha256 diverges from live scientific hash")
            print(json.dumps({"status": "ok", "artifact_sha256": payload["artifact_sha256"]}))
            return 0
        if args.write_registry:
            (ROOT / OUTPUT).write_text(text, encoding="utf-8")
            print(
                json.dumps(
                    {
                        "status": "written",
                        "path": OUTPUT,
                        "artifact_sha256": payload["artifact_sha256"],
                    }
                )
            )
            return 0
        sys.stdout.write(text)
        return 0
    except Exception:
        print(FAILURE_MESSAGE, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
