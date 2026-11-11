"""Exact bounds for sensitive-patient counts stated on 11 November 2026.

The counts are the ones written in those notes. This file does not audit a
cohort and does not read a study file. A zero-false-positive bound is
``0.05 ** (1 / n)``, the same quantity as ``tools/analyze_validation_capacity.py``.
"""

import argparse
import json
import math
from pathlib import Path


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


def _walk(node, path):
    for key in path:
        node = node[key]
    return node


def _class_pair(node):
    return int(node["sensitive"]), int(node["refractory"])


def _all_class_pairs(node):
    found = []
    if isinstance(node, dict):
        if set(node) == {"sensitive", "refractory"}:
            found.append(_class_pair(node))
        else:
            for value in node.values():
                found.extend(_all_class_pairs(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(_all_class_pairs(value))
    return found


# Sensitive/refractory pairs written in the 11 November notes, in note order.
# Compared with registries/pilot-001-supplement-summary.json. Not a new audit.
NOTE_COHORT_PAIRS = (
    ("FFPE validation", 10, 11),
    ("Frozen independent non-NACT", 22, 20),
    ("Full frozen validation", 44, 42),
    ("FFPE discovery", 83, 52),
    ("All non-overlapping", 115, 83),
    ("Frozen subset 13/8", 13, 8),
)

# Fields this page cites. A change in the pinned summary fails the check.
AUDIT_FIELDS = (
    (("clinical_cohorts", "FFPE_Discovery_clinical", "eligible_class_counts"), (83, 52)),
    (("clinical_cohorts", "FFPE_Discovery_clinical", "class_counts"), (91, 67)),
    (("clinical_cohorts", "Frozen_clinical", "class_counts"), (44, 20)),
    (("clinical_cohorts", "Frozen_clinical", "eligible_class_counts"), (42, 19)),
    (("published_score_subsets", "FFPE_pred_scores", "class_counts"), (83, 52)),
    (("published_score_subsets", "FFPE_valid_pred_scores", "class_counts"), (10, 10)),
    (("published_score_subsets", "Frozen_nonoverlap_pred_scores", "class_counts"), (22, 12)),
)


def load_supplement(root):
    path = Path(root) / "registries/pilot-001-supplement-summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def cohort_field(summary, path):
    return _class_pair(_walk(summary, path))


def check_stated_cohorts(summary):
    """Fail if a cited audit field moved, or if a note pair was silently adopted."""
    for path, expected in AUDIT_FIELDS:
        got = cohort_field(summary, path)
        if got != expected:
            raise ValueError(f"{'.'.join(path)} is {got}, expected {expected}")
    clinical = summary["clinical_cohorts"]["FFPE_Discovery_clinical"]
    if clinical["response_labelled_measurement_rows"] != 168:
        raise ValueError("discovery measurement-row count moved")
    scores = summary["published_score_subsets"]["FFPE_pred_scores"]
    if scores["unique_patient_keys"] != 135:
        raise ValueError("discovery score-sheet patient count moved")
    if summary["panel"]["count"] != 64:
        raise ValueError("panel count moved")
    nonoverlap = summary["published_score_subsets"]["Frozen_nonoverlap_pred_scores"]
    if nonoverlap["patient_keys_not_observed_in_all_discovery"] != 21:
        raise ValueError("no-discovery-record count moved")
    pairs = set(_all_class_pairs(summary))
    if (83, 52) not in pairs:
        raise ValueError("audited discovery pair missing")
    for _label, sensitive, refractory in NOTE_COHORT_PAIRS:
        if (sensitive, refractory) == (83, 52):
            continue
        if (sensitive, refractory) in pairs:
            raise ValueError(f"note pair {sensitive}/{refractory} is now an audit pair")
    return pairs


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
    summary = load_supplement(Path(__file__).resolve().parents[1])
    pairs = check_stated_cohorts(summary)
    print("audit pairs", " ".join(f"{s}/{r}" for s, r in sorted(pairs)))
    if args.check:
        print("stated specificity bounds match")


if __name__ == "__main__":
    main()
