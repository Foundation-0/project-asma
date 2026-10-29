"""Offline design calculations from pinned, already-public aggregate counts.

No scores, individual observations, network access, or model fitting. JSON on
stdout is deterministic; --check compares it with the committed result.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = 'registries/pilot-001-validation-capacity.json'
PINS = {
    'registries/pilot-001-supplement-summary.json':
        '69c155976f824caaec4238f968d6ddd51a332b4a366bbf70dd77c656cd57353d',
    'docs/pilot-001-open-questions.md':
        'dc063156d69e2289d44d861d175d057fab63c4ed85d0a6d6bca190374ae699ce',
}


def positive_integer(n):
    if type(n) is not int or not 1 <= n <= 10000:
        raise ValueError('count must be an integer from 1 through 10000')


def probability(p):
    if type(p) not in (int, float, Fraction) or not math.isfinite(p) or not 0 < p < 1:
        raise ValueError('probability must be finite and strictly between zero and one')


def perfect_lower_bound(n, tail_probability):
    """Exact binomial all-success lower limit, numerically evaluated."""
    positive_integer(n)
    probability(tail_probability)
    return float(tail_probability) ** (1 / n)


def minimum_perfect_n(target, tail_probability):
    """Minimum zero-failure n, using rational comparisons to prove minimality."""
    probability(target)
    probability(tail_probability)
    target = Fraction(str(target))
    tail_probability = Fraction(str(tail_probability))
    for n in range(1, 10001):
        if target ** n <= tail_probability:
            return n
    raise ValueError('required count exceeds supported range')


def specificity_grid(n):
    positive_integer(n)
    return [
        {'false_positives': fp, 'true_negatives': n - fp,
         'specificity_exact': str(Fraction(n - fp, n)),
         'specificity': (n - fp) / n}
        for fp in range(n + 1)
    ]


def build_result(root=ROOT):
    # Fail closed on source drift; these are historical aggregate inputs, not
    # a fresh patient-level reanalysis. Never emit source contents on failure.
    for path, expected in PINS.items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise ValueError('aggregate source fingerprint changed')
    source = json.loads((root / 'registries/pilot-001-supplement-summary.json').read_text())
    subset = source['published_score_subsets']['Frozen_nonoverlap_pred_scores']
    if (subset['class_counts'] != {'refractory': 12, 'sensitive': 22}
            or subset['patient_keys_not_observed_in_all_discovery'] != 21):
        raise ValueError('aggregate source counts differ')
    # 13/8 is recorded in the pinned prose section 4, not in the JSON registry.
    cohorts = [
        ('candidate_no_discovery_record', 13, 8,
         'docs/pilot-001-open-questions.md, section 4, Candidate patient-independent subsets; inherited aggregate, linkage not rerun'),
        ('published_frozen_nonoverlap', 22, 12,
         'registries/pilot-001-supplement-summary.json, published_score_subsets.Frozen_nonoverlap_pred_scores.class_counts'),
    ]
    results = []
    for name, negative, positive, locator in cohorts:
        results.append({
            'cohort': name, 'sensitive_negative_count': negative,
            'refractory_positive_count': positive, 'count_locator': locator,
            'hypothetical_false_positives': 0,
            'perfect_specificity_lower_95_one_sided': perfect_lower_bound(negative, .05),
            'perfect_specificity_lower_95_two_sided': perfect_lower_bound(negative, .025),
            'specificity_grid': specificity_grid(negative),
            'sensitivity_step_exact': str(Fraction(1, positive)),
        })
    return {
        'schema_version': 1,
        'evidence_class': 'executed aggregate-only design calculation; no model performance measured',
        'source_sha256': PINS,
        'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'command': 'python3 tools/analyze_validation_capacity.py',
        'methods_source': 'https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm',
        'methods_source_checked_on': '2026-10-29',
        'method': 'Clopper-Pearson all-success lower bound L=tail_probability**(1/n); minimum n satisfies target**n <= tail_probability',
        'target_specificity': .98,
        'minimum_zero_false_positive_negatives': {
            'one_sided_95': minimum_perfect_n(Fraction(98, 100), Fraction(5, 100)),
            'two_sided_95': minimum_perfect_n(Fraction(98, 100), Fraction(25, 1000)),
        },
        'cohorts': results,
        'assumptions_and_limits': [
            'All-perfect outcomes are hypothetical, not observed classifier results.',
            'Binomial inference assumes independent negative patients with a common specificity and a fixed threshold chosen independently of test outcomes.',
            'Candidate patient independence remains unresolved; no-source-match is not proof of an untouched validation cohort.',
            'The published nonoverlap cohort contains patients overlapping discovery; its calculation is illustrative and does not certify binomial coverage there.',
            'Cross-validation folds, repeated fits, bootstrap samples and multiple specimens do not increase the independent patient count.',
            '149 and 183 are best-case zero-error minima, not sample sizes achieving specified power or assurance.',
            'The specificity grid describes deterministic empirical confusion counts; interpolated ROC operating points need not be attainable by a fixed threshold.',
            'No source data were acquired, no threshold was selected and no model, AUROC, calibration or clinical utility was evaluated.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify deterministic committed aggregate output')
    args = parser.parse_args()
    rendered = json.dumps(build_result(), indent=2, sort_keys=True, allow_nan=False) + '\n'
    if args.check:
        if (ROOT / OUTPUT).read_text() != rendered:
            raise SystemExit('validation-capacity artifact differs; regenerate and review')
        print('validation-capacity artifact matches')
    else:
        print(rendered, end='')


if __name__ == '__main__':
    main()
