"""Offline design values for the pre-registered exploratory subset plan.

Exact null distribution of the Mann-Whitney statistic, its one-sided critical
values, and exact binomial intervals for the documented class counts. No
scores, individual observations, network access, model fitting or study files.
JSON on stdout is deterministic; --check compares it with the committed result.
"""
import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = 'registries/pilot-001-exploratory-subset-design.json'
PROTOCOL = 'protocols/pilot-001-exploratory-subset-plan.md'
# The same aggregate pins and prose phrase the validation-capacity calculation
# uses, so both design records rest on one documented count.
PINS = {
    'registries/pilot-001-supplement-summary.json':
        '69c155976f824caaec4238f968d6ddd51a332b4a366bbf70dd77c656cd57353d',
}
SPLIT_PHRASE = 'strictly independent, with no discovery record of any kind: **21 (13/8)**'
SPLIT_SOURCE = 'docs/pilot-001-open-questions.md'
# Frozen by the plan, not inherited from software defaults.
PLAN = {
    'positive_class': 'refractory',
    'score_direction': 'higher score predicts refractory',
    'primary_alpha_one_sided': Fraction(5, 100),
    'bootstrap_draws': 2000,
    'bootstrap_seed': 20261106,
    'minimum_valid_bootstrap_draws': 1000,
    'threshold_specificity_target': Fraction(98, 100),
    'interval_confidence': Fraction(95, 100),
}


def count(n, upper=10000):
    if type(n) is not int or not 0 <= n <= upper:
        raise ValueError('count must be an integer from 0 through %d' % upper)


def positive_count(n, upper=10000):
    count(n, upper)
    if n == 0:
        raise ValueError('count must be at least one')


def probability(p):
    if type(p) not in (int, float, Fraction) or not math.isfinite(p) or not 0 < p < 1:
        raise ValueError('probability must be finite and strictly between zero and one')


@lru_cache(maxsize=None)
def _placements(m, n):
    """Number of rank placements of m positives among m+n ranks, by U.

    The highest rank is a positive (beating all n negatives, U += n) or a
    negative (U unchanged). Exact integers; no ties.
    """
    if m == 0 or n == 0:
        return ((0, 1),)
    totals = {}
    for u, c in _placements(m - 1, n):
        totals[u + n] = totals.get(u + n, 0) + c
    for u, c in _placements(m, n - 1):
        totals[u] = totals.get(u, 0) + c
    return tuple(sorted(totals.items()))


def mann_whitney_null(m, n):
    """Exact null distribution of U = AUROC * m * n for m positives, n negatives."""
    positive_count(m, 200)
    positive_count(n, 200)
    distribution = dict(_placements(m, n))
    if sum(distribution.values()) != math.comb(m + n, m):
        raise ValueError('placement count does not match the binomial coefficient')
    return distribution


def upper_tail(m, n, u):
    """P(U >= u) under the null, as an exact fraction."""
    distribution = mann_whitney_null(m, n)
    count(u, m * n)
    return Fraction(sum(c for value, c in distribution.items() if value >= u), math.comb(m + n, m))


def critical_value(m, n, alpha):
    """Smallest u with P(U >= u) <= alpha; the one-sided rejection region is U >= u."""
    probability(alpha)
    alpha = Fraction(str(alpha)) if not isinstance(alpha, Fraction) else alpha
    for u in range(m * n + 1):
        tail = upper_tail(m, n, u)
        if tail <= alpha:
            return {
                'alpha': str(alpha), 'critical_u': u, 'pairs': m * n,
                'critical_auroc_exact': str(Fraction(u, m * n)),
                'critical_auroc': u / (m * n),
                'exact_p_at_critical_u': float(tail),
                'exact_p_one_below': float(upper_tail(m, n, u - 1)) if u else None,
            }
    raise ValueError('no rejection region at this level')


def binomial_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _solve(function, increasing):
    """Root of a monotone function on [0, 1] by bisection (numerical, not exact)."""
    low, high = 0.0, 1.0
    for _ in range(200):
        mid = (low + high) / 2
        if (function(mid) < 0) == increasing:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def clopper_pearson(k, n, confidence):
    """Exact (Clopper-Pearson) two-sided interval for k successes in n trials."""
    positive_count(n, 10000)
    count(k, n)
    probability(confidence)
    tail = (1 - Fraction(str(confidence))) / 2
    lower = 0.0 if k == 0 else _solve(lambda p: (1 - binomial_cdf(k - 1, n, p)) - float(tail), True)
    upper = 1.0 if k == n else _solve(lambda p: binomial_cdf(k, n, p) - float(tail), False)
    return {'successes': k, 'trials': n, 'proportion_exact': str(Fraction(k, n)),
            'proportion': k / n, 'lower': lower, 'upper': upper}


def one_sided_lower(k, n, confidence):
    """Exact one-sided lower confidence limit for k successes in n trials."""
    positive_count(n, 10000)
    count(k, n)
    probability(confidence)
    tail = 1 - Fraction(str(confidence))
    return 0.0 if k == 0 else _solve(lambda p: (1 - binomial_cdf(k - 1, n, p)) - float(tail), True)


def build_result(root=ROOT):
    # Fail closed on source drift; never emit source contents on failure.
    for path, expected in PINS.items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise ValueError('aggregate source fingerprint changed')
    try:
        report = (root / SPLIT_SOURCE).read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        raise ValueError('candidate split phrase changed')
    if SPLIT_PHRASE not in report:
        raise ValueError('candidate split phrase changed')
    source = json.loads((root / 'registries/pilot-001-supplement-summary.json').read_text(encoding='utf-8'))
    subsets = source['published_score_subsets']
    nonoverlap, overlap = subsets['Frozen_nonoverlap_pred_scores'], subsets['Frozen_overlap_pred_scores']
    if (nonoverlap['class_counts'] != {'refractory': 12, 'sensitive': 22}
            or nonoverlap['patient_keys_not_observed_in_all_discovery'] != 21
            or nonoverlap['patient_keys_not_observed_in_eligible_discovery'] != 28
            or overlap['class_counts'] != {'refractory': 7, 'sensitive': 20}
            or overlap['patient_keys_shared_with_all_discovery'] != 27):
        raise ValueError('aggregate source counts differ')
    confidence = PLAN['interval_confidence']
    cohorts = []
    for name, positive, negative, decision_rule, locator in (
            ('evaluation_no_discovery_record', 8, 13, True,
             'docs/pilot-001-open-questions.md, section 4, Candidate patient-independent subsets; inherited aggregate, linkage not rerun'),
            ('sensitivity_not_in_eligible_discovery', 11, 17, False,
             'registries/pilot-001-supplement-summary.json, published_score_subsets.Frozen_nonoverlap_pred_scores.patient_keys_not_observed_in_eligible_discovery; split from the same section 4')):
        cohorts.append({
            'cohort': name, 'refractory_positive_count': positive,
            'sensitive_negative_count': negative, 'count_locator': locator,
            'carries_primary_decision_rule': decision_rule,
            'positive_negative_pairs': positive * negative,
            # Joint patient draws miss a class with probability p^n + q^n; the
            # 1,000-valid-draw minimum is therefore not binding at these counts.
            'expected_class_empty_bootstrap_draws': float(PLAN['bootstrap_draws'] * (
                Fraction(negative, positive + negative) ** (positive + negative)
                + Fraction(positive, positive + negative) ** (positive + negative))),
            'null_upper_tail_by_u': {str(u): str(upper_tail(positive, negative, u))
                                     for u in range(positive * negative + 1)},
            'critical_values': [critical_value(positive, negative, alpha)
                                for alpha in (Fraction(5, 100), Fraction(25, 1000), Fraction(1, 100))],
            'sensitivity_intervals': [clopper_pearson(k, positive, confidence) for k in range(positive + 1)],
            'specificity_intervals': [clopper_pearson(j, negative, confidence) for j in range(negative + 1)],
            'specificity_one_sided_lower': [
                {'false_positives': negative - j, 'lower': one_sided_lower(j, negative, confidence)}
                for j in range(negative, max(negative - 4, -1), -1)],
        })
    return {
        'schema_version': 1,
        'evidence_class': 'executed aggregate-only design calculation; no model performance measured',
        'protocol': PROTOCOL,
        'source_sha256': PINS,
        'implementation_sha256': {'tools/plan_exploratory_subset_design.py':
                                  hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        'command': 'python3 tools/plan_exploratory_subset_design.py',
        'frozen_parameters': {k: (str(v) if isinstance(v, Fraction) else v) for k, v in PLAN.items()},
        'calibration_set': {
            'definition': 'all 40 scored frozen patients outside the evaluation set: the 27 overlap-sheet patients plus the 13 nonoverlap-sheet patients with a discovery record',
            'refractory_positive_count': 11, 'sensitive_negative_count': 29,
            'allowed_calibration_false_positives': int((1 - PLAN['threshold_specificity_target']) * 29),
            'count_locator': 'registries/pilot-001-supplement-summary.json, published_score_subsets.Frozen_overlap_pred_scores and Frozen_nonoverlap_pred_scores; 34 minus 21 by class',
        },
        'method': ('Mann-Whitney null: all C(m+n, m) rank placements equally likely, no ties; '
                   'U = AUROC * m * n; rejection region U >= critical_u with P(U >= critical_u) <= alpha. '
                   'Clopper-Pearson intervals invert exact binomial tails by bisection (numerical endpoints).'),
        'cohorts': cohorts,
        'assumptions_and_limits': [
            'The null distribution assumes exchangeable ranks and no exact ties; observed ties are reported and the test is not applied across tied cross-class pairs without the plan\'s stated handling.',
            'A rejection is an exploratory signal within this selected subset, not validation, reproduction or a population claim.',
            'Binomial intervals assume independent patients and a threshold fixed independently of the evaluation outcomes.',
            'Patient independence of the evaluation subset from upstream preprocessing is unresolved; a no-discovery-record match is not an untouched evaluation set.',
            'Folds, repeated fits, bootstrap resamples and multiple specimens do not increase the independent patient count.',
            'No source data were acquired, no score was read, no threshold was selected and no AUROC, calibration or clinical utility was evaluated.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify deterministic committed aggregate output')
    args = parser.parse_args()
    rendered = json.dumps(build_result(), indent=2, sort_keys=True, allow_nan=False) + '\n'
    if args.check:
        if (ROOT / OUTPUT).read_text() != rendered:
            raise SystemExit('exploratory-subset design artifact differs; regenerate and review')
        print('exploratory-subset design artifact matches')
    else:
        print(rendered, end='')


if __name__ == '__main__':
    main()
