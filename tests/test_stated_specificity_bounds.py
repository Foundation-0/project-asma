"""Replay the 11 November 2026 specificity arithmetic. No study rows."""

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "bounds", ROOT / "tools/check_stated_specificity_bounds.py")
bounds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bounds)

# Rounded one-sided 95% bounds at 0, 1 and 2 false positives.
EXPECTED = {
    10: (74.11, 60.58, 49.31),
    13: (79.42, 68.37, 58.99),
    22: (87.27, 80.19, 74.05),
    44: (93.42, 89.67, 86.37),
    83: (96.46, 94.41, 92.61),
    115: (97.43, 95.94, 94.63),
    149: (98.01, 96.86, 95.84),
    236: (98.74, 98.01, 97.36),
}

# Two-sided 95% intervals for the fractions named by the product 166 x 26
# and by the notes' 100-patient pair. Not an audited cohort.
FRACTION_INTERVALS = {
    (26, 9): (17.21, 55.67),
    (166, 163): (94.81, 99.63),
    (20, 7): (15.39, 59.22),
    (80, 78): (91.26, 99.70),
}

PRIVATE_MARKERS = (
    "Butler", "Roche", "RPAP", "D08", "D09", "D10", "D11",
    "drive.google", "orda-aska", "gpt-forge", "IMG_",
)


class StatedSpecificityBoundsTests(unittest.TestCase):
    def test_zero_errors_match_the_power_form(self):
        for n in bounds.STATED_N:
            self.assertAlmostEqual(bounds.lower_specificity(n, 0), 0.05 ** (1.0 / n))

    def test_rounded_table(self):
        for n, expected in EXPECTED.items():
            got = tuple(bounds.percent(bounds.lower_specificity(n, k)) for k in (0, 1, 2))
            self.assertEqual(got, expected)

    def test_more_errors_lower_the_bound(self):
        for n in bounds.STATED_N:
            values = [bounds.lower_specificity(n, k) for k in (0, 1, 2)]
            self.assertGreater(values[0], values[1])
            self.assertGreater(values[1], values[2])

    def test_minima_for_a_98_percent_bound(self):
        self.assertEqual(bounds.minimum_n(0), 149)
        self.assertEqual(bounds.minimum_n(1), 236)
        self.assertLess(bounds.lower_specificity(148, 0), 0.98)
        self.assertLess(bounds.lower_specificity(235, 1), 0.98)

    def test_note_intervals_match_those_fractions(self):
        for (n, successes), (low, high) in FRACTION_INTERVALS.items():
            lower, upper = bounds.two_sided_interval(n, successes)
            self.assertEqual((bounds.percent(lower), bounds.percent(upper)), (low, high))

    def test_public_page_carries_the_table_and_no_private_markers(self):
        page = (ROOT / "docs/google-bio-convergence-2026-11-11.md").read_text(encoding="utf-8")
        for n, triple in EXPECTED.items():
            for value in triple:
                self.assertIn(f"{value:.2f}%", page)
        for marker in PRIVATE_MARKERS:
            self.assertNotIn(marker, page)
        for snippet in (
            "10 / 11", "10 / 10", "22 / 20", "22 / 12", "44 / 42",
            "42 / 19", "91 / 67", "115 / 83",
            "74,987,632-75,005,800", "74,992,096-75,021,497",
            "1114-1153", "1114-1157",
            "41606153", "10.1038/s41586-025-10014-0",
            "5.4", "8.87",
        ):
            self.assertIn(snippet, page)
        self.assertNotIn("10.7150/ijbs.133555", page)

    def test_note_cohort_pairs_against_the_supplement_audit(self):
        summary = bounds.load_supplement(ROOT)
        pairs = bounds.check_stated_cohorts(summary)
        self.assertIn((83, 52), pairs)
        self.assertIn((22, 12), pairs)
        self.assertIn((10, 10), pairs)
        self.assertNotIn((10, 11), pairs)
        self.assertNotIn((22, 20), pairs)
        self.assertNotIn((44, 42), pairs)
        self.assertNotIn((115, 83), pairs)
        self.assertNotIn((13, 8), pairs)

    def test_rejects_bad_counts(self):
        for n, k in ((0, 0), (10, -1), (10, 11), (True, 0)):
            with self.assertRaises(ValueError):
                bounds.lower_specificity(n, k)
