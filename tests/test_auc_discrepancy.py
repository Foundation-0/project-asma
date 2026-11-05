"""Offline arithmetic checks for AUC discrepancy candidates (no network)."""

from __future__ import annotations

import copy
import io
import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_auc_discrepancy as analyze
import audit_published_cohorts as audit
import verify_published_auc as verify


def abstract_record(token, response="sensitive", **changes):
    row = {
        audit.LABEL_COLUMN: f"abstract-label-{token}",
        "Patient ID": f"abstract-person-{token}",
        "Sample ID": f"abstract-specimen-{token}",
        "Neo-adjuvant": "no",
        "Tumor response": response,
        "Tumor Location Group": "OM",
        "Sample type": "abstract-material",
    }
    row.update(changes)
    return row


class AucDiscrepancyMath(unittest.TestCase):
    def test_tie_credits_zero_half_one(self):
        parsed = [verify.probability(value) for value in ("1", "0.5", "0")]
        labels = [verify.POSITIVE, verify.POSITIVE, verify.NEGATIVE]
        # pairs: (1,0) concordant, (0.5,0) concordant — no ties
        half, counts = analyze.pair_auc(parsed, labels, Fraction(1, 2))
        self.assertEqual(counts["tied_pairs"], 0)
        self.assertEqual(half, Fraction(1))
        zero, _ = analyze.pair_auc(parsed, labels, Fraction(0))
        one, _ = analyze.pair_auc(parsed, labels, Fraction(1))
        self.assertEqual(zero, one)
        self.assertEqual(zero, half)

        tied_parsed = [verify.probability(value) for value in ("0.5", "0.5")]
        tied_labels = [verify.POSITIVE, verify.NEGATIVE]
        self.assertEqual(analyze.pair_auc(tied_parsed, tied_labels, Fraction(0))[0], 0)
        self.assertEqual(analyze.pair_auc(tied_parsed, tied_labels, Fraction(1, 2))[0], Fraction(1, 2))
        self.assertEqual(analyze.pair_auc(tied_parsed, tied_labels, Fraction(1))[0], 1)

    def test_mann_whitney_equals_trapezoidal_with_ties(self):
        scores = ["0.9", "0.5", "0.5", "0.1", "0.7"]
        labels = [verify.POSITIVE, verify.POSITIVE, verify.NEGATIVE, verify.NEGATIVE, verify.NEGATIVE]
        parsed = [verify.probability(value) for value in scores]
        half, _ = analyze.pair_auc(parsed, labels, Fraction(1, 2))
        trap = analyze.trapezoidal_auc(parsed, labels)
        self.assertEqual(half, trap)

    def test_reversed_polarity_complements_auc(self):
        parsed = [verify.probability(value) for value in ("0.9", "0.2", "0.1")]
        labels = [verify.POSITIVE, verify.NEGATIVE, verify.NEGATIVE]
        forward, _ = analyze.pair_auc(parsed, labels, Fraction(1, 2))
        reversed_labels = [
            verify.NEGATIVE if label == verify.POSITIVE else verify.POSITIVE for label in labels
        ]
        backward, _ = analyze.pair_auc(parsed, reversed_labels, Fraction(1, 2))
        self.assertEqual(forward + backward, 1)

    def test_rounding_bounds_contain_half_credit(self):
        # Distinct scores that collide at 1 decimal place.
        # 0.81/0.84 and 0.82/0.83 all HALF_UP-round to 0.8 at 1 dp → cross-class ties.
        parsed = [verify.probability(value) for value in ("0.81", "0.84", "0.82", "0.83")]
        labels = [verify.POSITIVE, verify.POSITIVE, verify.NEGATIVE, verify.NEGATIVE]
        bounds = analyze.rounding_bounds(parsed, labels, 1)
        half = Fraction(bounds["auc_half_credit_exact"]["numerator"],
                        bounds["auc_half_credit_exact"]["denominator"])
        low = Fraction(bounds["auc_lower_bound_exact"]["numerator"],
                       bounds["auc_lower_bound_exact"]["denominator"])
        high = Fraction(bounds["auc_upper_bound_exact"]["numerator"],
                        bounds["auc_upper_bound_exact"]["denominator"])
        self.assertLessEqual(low, half)
        self.assertLessEqual(half, high)
        self.assertGreater(bounds["cross_class_tied_pairs_after_rounding"], 0)

    def test_delong_ci_contains_perfect_auc(self):
        parsed = [verify.probability(value) for value in ("1", "1", "0", "0")]
        labels = [verify.POSITIVE, verify.POSITIVE, verify.NEGATIVE, verify.NEGATIVE]
        ci = analyze.delong_ci(parsed, labels)
        self.assertEqual(ci["auc"], 1.0)
        self.assertTrue(ci["lower"] <= 1.0 <= ci["upper"])

    def test_stratified_bootstrap_is_deterministic_for_seed(self):
        parsed = [verify.probability(value) for value in ("0.9", "0.8", "0.2", "0.1", "0.3")]
        labels = [
            verify.POSITIVE,
            verify.POSITIVE,
            verify.NEGATIVE,
            verify.NEGATIVE,
            verify.NEGATIVE,
        ]
        first = analyze.stratified_bootstrap_ci(parsed, labels, resamples=200, seed=7)
        second = analyze.stratified_bootstrap_ci(parsed, labels, resamples=200, seed=7)
        self.assertEqual(first, second)
        self.assertEqual(first["resamples"], 200)
        self.assertLessEqual(first["lower"], first["bootstrap_median"])
        self.assertLessEqual(first["bootstrap_median"], first["upper"])

    def test_binormal_perfect_separation(self):
        parsed = [verify.probability(value) for value in ("0.9", "0.8", "0.2", "0.1")]
        labels = [verify.POSITIVE, verify.POSITIVE, verify.NEGATIVE, verify.NEGATIVE]
        fit = analyze.binormal_auc(parsed, labels)
        self.assertGreater(fit["auc"], 0.95)

    def test_score_text_stats_omit_values(self):
        stats = analyze.score_text_stats(["0.5", "0.5001", "1"])
        encoded = json.dumps(stats)
        self.assertNotIn("0.5001", encoded)
        self.assertEqual(stats["score_count"], 3)
        self.assertEqual(stats["unique_source_strings"], 3)

    def test_help_is_offline(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools/analyze_auc_discrepancy.py"), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("discrepancy", completed.stdout.lower())
        self.assertEqual(completed.stderr, "")

    def test_cli_failure_is_sanitized(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(analyze, "run_analysis", side_effect=audit.AuditError("private-token")), \
                mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            result = analyze.main([])
        self.assertEqual(result, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), analyze.FAILURE_MESSAGE + "\n")
        self.assertNotIn("private-token", stderr.getvalue())

    def test_registry_schema_keys_when_mocked(self):
        # Minimal abstract cohort: 2 pos / 3 neg, constant-safe AUROC.
        records = [
            abstract_record(str(i), "refractory" if i < 2 else "sensitive")
            for i in range(5)
        ]
        # Pad clinical-like fields used by classify/eligible helpers as needed via workbook mock.
        score_rows = [
            {"A": records[i][audit.LABEL_COLUMN], "B": "0.75" if i < 2 else "0.25"}
            for i in range(5)
        ]

        class FakeBook:
            def __init__(self, source):
                self.source = source

            def rows(self, sheet, columns=None):
                if sheet == verify.CLINICAL_SHEET:
                    header = {
                        "A": audit.LABEL_COLUMN,
                        "B": "Patient ID",
                        "C": "Sample ID",
                        "D": "Neo-adjuvant",
                        "E": "Tumor response",
                        "F": "Tumor Location Group",
                        "G": "Sample type",
                    }
                    body = []
                    for row in records:
                        body.append({col: row[field] for col, field in header.items()})
                    return [header] + body
                if sheet == verify.SCORE_SHEET:
                    return [{"A": "Samples", "B": "Pred.scores"}] + copy.deepcopy(score_rows)
                raise AssertionError(sheet)

        # Bypass the fixed 135/52/83 gate for the unit mock by patching load gate.
        original_require = audit.require

        def selective_require(condition, message):
            if "Unexpected discovery prediction denominator" in message:
                return
            return original_require(condition, message)

        with mock.patch.object(audit, "Workbook", FakeBook), \
                mock.patch.object(audit, "require", side_effect=selective_require), \
                mock.patch.object(Path, "is_file", return_value=True):
            # Still need classify_clinical / eligible to work on abstract rows.
            # eligible_samples filters neoadjuvant and Mix — our rows are fine.
            # join_score_membership needs LABEL_COLUMN present — yes.
            # But load_joined_cohort also checks sample_keys equality via analyze? No, only counts.
            payload = analyze.run_analysis()
        self.assertEqual(payload["schema_version"], 1)
        self.assertIn("a_tie_handling", payload["candidates"])
        self.assertEqual(payload["baseline"]["claim_label"], "VERIFIED")
        self.assertEqual(
            payload["ledger_claim_ids"],
            {
                "verified_candidates_a_through_e": "V23",
                "conjecture_leading_open_explanation": "C20",
            },
        )
        # artifact_sha256 is attached in main(), not run_analysis().
        self.assertNotIn("artifact_sha256", payload)
        encoded = json.dumps(payload, allow_nan=False)
        for token in ("abstract-label-", "abstract-person-", "abstract-specimen-"):
            self.assertNotIn(token, encoded)

    def test_artifact_hash_stable_for_identical_payload(self):
        payload = {"schema_version": 1, "baseline": {"auc": 0.5}}
        first = analyze.registry_sha256(payload)
        second = analyze.registry_sha256(payload)
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
