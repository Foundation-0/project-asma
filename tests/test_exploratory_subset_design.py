"""Exact distribution identities and safe aggregate provenance, without study rows."""
import importlib.util
from fractions import Fraction
from itertools import combinations
import json
import math
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('design', ROOT / 'tools/plan_exploratory_subset_design.py')
design = importlib.util.module_from_spec(spec)
spec.loader.exec_module(design)


def enumerated_null(m, n):
    """Brute-force U counts over every placement of m positives among m+n ranks."""
    totals = {}
    for placed in combinations(range(m + n), m):
        u = sum(rank - index for index, rank in enumerate(placed))
        totals[u] = totals.get(u, 0) + 1
    return totals


class ExploratorySubsetDesignTests(unittest.TestCase):
    def test_null_distribution_matches_enumeration_and_is_symmetric(self):
        for m, n in ((1, 1), (2, 3), (3, 5), (4, 4), (8, 13)):
            distribution = design.mann_whitney_null(m, n)
            self.assertEqual(distribution, enumerated_null(m, n))
            self.assertEqual(sum(distribution.values()), math.comb(m + n, m))
            self.assertEqual(distribution, {m * n - u: c for u, c in distribution.items()})
        self.assertEqual(design.upper_tail(8, 13, 0), 1)
        self.assertEqual(design.upper_tail(8, 13, 104), Fraction(1, 203490))

    def test_critical_values_for_the_documented_counts(self):
        rule = design.critical_value(8, 13, Fraction(5, 100))
        self.assertEqual((rule['critical_u'], rule['critical_auroc_exact']), (76, '19/26'))
        self.assertLessEqual(rule['exact_p_at_critical_u'], .05)
        self.assertGreater(rule['exact_p_one_below'], .05)
        self.assertEqual(design.critical_value(8, 13, .025)['critical_u'], 80)
        self.assertEqual(design.critical_value(8, 13, .01)['critical_u'], 84)
        self.assertEqual(design.critical_value(11, 17, .05)['critical_u'], 130)
        # The region is minimal: no smaller u has tail probability within alpha.
        self.assertGreater(design.upper_tail(8, 13, 75), Fraction(5, 100))
        self.assertLessEqual(design.upper_tail(8, 13, 76), Fraction(5, 100))

    def test_clopper_pearson_inverts_exact_binomial_tails(self):
        for k, n in ((0, 8), (2, 8), (3, 8), (8, 8), (12, 13), (13, 13), (5, 29)):
            interval = design.clopper_pearson(k, n, .95)
            self.assertLessEqual(interval['lower'], k / n)
            self.assertLessEqual(k / n, interval['upper'])
            if k:
                self.assertAlmostEqual(1 - design.binomial_cdf(k - 1, n, interval['lower']), .025, places=9)
            else:
                self.assertEqual(interval['lower'], 0)
            if k < n:
                self.assertAlmostEqual(design.binomial_cdf(k, n, interval['upper']), .025, places=9)
            else:
                self.assertEqual(interval['upper'], 1)

    def test_reference_values_agree_with_the_capacity_record(self):
        # Full-precision values recorded in registries/pilot-001-validation-capacity.json;
        # the report rounds them to 79.42% and 75.29%.
        self.assertAlmostEqual(design.one_sided_lower(13, 13, .95), .7941833348134493)
        self.assertAlmostEqual(design.clopper_pearson(13, 13, .95)['lower'], .752947361999529)
        two_of_eight = design.clopper_pearson(2, 8, .95)
        self.assertAlmostEqual(two_of_eight['lower'], .032, places=3)
        self.assertAlmostEqual(two_of_eight['upper'], .651, places=3)
        three_of_eight = design.clopper_pearson(3, 8, .95)
        self.assertAlmostEqual(three_of_eight['lower'], .085, places=3)
        self.assertAlmostEqual(three_of_eight['upper'], .755, places=3)

    def test_reject_invalid_inputs(self):
        for m in (True, 0, -1, 1.5, '8', 201):
            with self.assertRaises(ValueError):
                design.mann_whitney_null(m, 13)
        for alpha in (True, 0, 1, -.1, float('nan'), float('inf'), '.05'):
            with self.assertRaises(ValueError):
                design.critical_value(8, 13, alpha)
        for k, n in ((-1, 8), (9, 8), (1.0, 8), (1, 0)):
            with self.assertRaises(ValueError):
                design.clopper_pearson(k, n, .95)
        with self.assertRaises(ValueError):
            design.upper_tail(8, 13, 105)

    def test_source_drift_fails_without_echoing_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in design.PINS:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text('untrusted source content')
            with self.assertRaisesRegex(ValueError, '^aggregate source fingerprint changed$'):
                design.build_result(root)
            for path in design.PINS:
                (root / path).write_bytes((ROOT / path).read_bytes())
            report = (ROOT / design.SPLIT_SOURCE).read_text(encoding='utf-8')
            self.assertIn(design.SPLIT_PHRASE, report)
            dest = root / design.SPLIT_SOURCE
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(report.replace(design.SPLIT_PHRASE, 'candidate split removed'), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, '^candidate split phrase changed$'):
                design.build_result(root)

    def test_committed_artifact_matches(self):
        result = design.build_result()
        self.assertEqual(result, json.loads((ROOT / design.OUTPUT).read_text()))
        self.assertEqual([(c['refractory_positive_count'], c['sensitive_negative_count'])
                          for c in result['cohorts']], [(8, 13), (11, 17)])
        self.assertEqual([c['carries_primary_decision_rule'] for c in result['cohorts']], [True, False])
        # Fewer than one class-empty draw is expected in 2,000 for either cohort.
        self.assertTrue(all(0 < c['expected_class_empty_bootstrap_draws'] < 1 for c in result['cohorts']))
        self.assertAlmostEqual(result['cohorts'][0]['expected_class_empty_bootstrap_draws'],
                               2000 * ((13 / 21) ** 21 + (8 / 21) ** 21), places=9)
        self.assertEqual(result['calibration_set']['allowed_calibration_false_positives'], 0)
        self.assertTrue((ROOT / result['protocol']).is_file())
        self.assertEqual(set(result['implementation_sha256']), {'tools/plan_exploratory_subset_design.py'})
