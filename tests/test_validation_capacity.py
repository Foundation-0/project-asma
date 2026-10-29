"""Mathematical identities and safe aggregate provenance, without study rows."""
import importlib.util
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('capacity', ROOT / 'tools/analyze_validation_capacity.py')
capacity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capacity)


class ValidationCapacityTests(unittest.TestCase):
    def test_all_success_binomial_identity(self):
        # At the lower limit, probability of n successes is the tail mass.
        for n in (1, 2, 13, 22, 149, 183, 1000):
            for alpha in (.05, .025):
                self.assertAlmostEqual(capacity.perfect_lower_bound(n, alpha) ** n, alpha, places=13)

    def test_reference_values(self):
        self.assertAlmostEqual(capacity.perfect_lower_bound(13, .05), .7941833348134493)
        self.assertAlmostEqual(capacity.perfect_lower_bound(22, .05), .8726945683451612)
        self.assertAlmostEqual(capacity.perfect_lower_bound(13, .025), .752947361999529)

    def test_exact_minimality(self):
        target = Fraction(49, 50)
        for alpha, expected in ((Fraction(1, 20), 149), (Fraction(1, 40), 183)):
            n = capacity.minimum_perfect_n(target, alpha)
            self.assertEqual(n, expected)
            self.assertLessEqual(target ** n, alpha)
            self.assertGreater(target ** (n - 1), alpha)

    def test_grid_and_unattainable_98_percent(self):
        for n in (13, 22):
            grid = capacity.specificity_grid(n)
            self.assertEqual(len(grid), n + 1)
            self.assertEqual(grid[0]['specificity'], 1)
            self.assertEqual(grid[-1]['specificity'], 0)
            self.assertNotIn(Fraction(49, 50), [Fraction(r['specificity_exact']) for r in grid])
            self.assertEqual([r['false_positives'] + r['true_negatives'] for r in grid], [n] * (n + 1))

    def test_reject_invalid_inputs(self):
        for n in (True, 0, -1, 1.5, '13', 10001):
            with self.assertRaises(ValueError):
                capacity.perfect_lower_bound(n, .05)
        for p in (True, 0, 1, -.1, float('nan'), float('inf'), '.05'):
            with self.assertRaises(ValueError):
                capacity.perfect_lower_bound(13, p)
            with self.assertRaises(ValueError):
                capacity.minimum_perfect_n(p, .05)

    def test_source_drift_fails_without_echoing_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in capacity.PINS:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text('untrusted source content')
            with self.assertRaisesRegex(ValueError, '^aggregate source fingerprint changed$'):
                capacity.build_result(root)

    def test_candidate_split_phrase_drift_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            supplement = ROOT / 'registries/pilot-001-supplement-summary.json'
            dest = root / 'registries/pilot-001-supplement-summary.json'
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(supplement.read_bytes())
            report = (ROOT / 'docs/pilot-001-open-questions.md').read_text()
            self.assertIn(capacity.SPLIT_PHRASE, report)
            dest = root / 'docs/pilot-001-open-questions.md'
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(report.replace(capacity.SPLIT_PHRASE, 'candidate split removed'))
            with self.assertRaisesRegex(ValueError, 'candidate split phrase changed'):
                capacity.build_result(root)

    def test_committed_artifact_matches(self):
        result = capacity.build_result()
        self.assertEqual(result, json.loads((ROOT / capacity.OUTPUT).read_text()))
        self.assertEqual([(c['sensitive_negative_count'], c['refractory_positive_count']) for c in result['cohorts']], [(13, 8), (22, 12)])
