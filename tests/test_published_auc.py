"""Offline arithmetic/join checks using abstract tokens and simple numbers only."""

import contextlib
import copy
import io
import json
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_published_cohorts as audit
import verify_published_auc as verify


def abstract_record(token, response="sensitive", **changes):
    row = {audit.LABEL_COLUMN: f"abstract-label-{token}",
           "Patient ID": f"abstract-person-{token}", "Sample ID": f"abstract-specimen-{token}",
           "Neo-adjuvant": "no", "Tumor response": response,
           "Tumor Location Group": "OM", "Sample type": "abstract-material"}
    row.update(changes)
    return row


def workbook_double():
    """Provide abstract tables of the fixed dimensions; never open a workbook."""
    records = [abstract_record(str(index), "refractory" if index < 52 else "sensitive", **{
        "Neo-adjuvant": "no" if index < 135 else "yes",
        "Tumor Location Group": "NA" if index in (0, 135) else "OM",
    }) for index in range(158)]
    header = dict(zip("ABCDEFG", records[0]))
    clinical = [header] + [{column: row[field] for column, field in header.items()} for row in records]
    # Reverse score rows to make positional joins wrong, while all equal scores
    # give a hand-checkable AUROC independent of the class ordering.
    predictions = [{"A": "Samples", "B": "Pred.scores"}] + [
        {"A": row[audit.LABEL_COLUMN], "B": "0.375"} for row in reversed(records[:135])
    ]

    class AbstractWorkbook:
        def __init__(self, source):
            self.source = source

        def rows(self, sheet, columns=None):
            if self.source == audit.SOURCES["clinical"] and sheet == verify.CLINICAL_SHEET and columns is None:
                return copy.deepcopy(clinical)
            if self.source == audit.SOURCES["panel_and_scores"] and sheet == verify.SCORE_SHEET and columns == {"A", "B"}:
                return copy.deepcopy(predictions)
            raise AssertionError("Unexpected worksheet or column consumption")

    return AbstractWorkbook


class PublishedAucChecks(unittest.TestCase):
    def test_fixed_direction_perfect_reversed_and_constant(self):
        labels = [verify.POSITIVE, verify.NEGATIVE]
        for scores, expected in ((["1", "0"], Fraction(1)), (["0", "1"], Fraction(0)),
                                 (["0.4", "0.40"], Fraction(1, 2))):
            with self.subTest(scores=scores):
                actual, counts = verify.compute_auc(scores, labels)
                self.assertEqual(actual, expected)
                self.assertEqual(sum(counts[key] for key in
                                     ("concordant_pairs", "tied_pairs", "discordant_pairs")), 1)

    def test_mixed_ties_permutation_and_reversed_labels(self):
        scores = ["0.5", "0.9", "0.1", "0.5", "0.9"]
        labels = [verify.POSITIVE] * 2 + [verify.NEGATIVE] * 3
        result, counts = verify.compute_auc(scores, labels)
        self.assertEqual(result, Fraction(2, 3))
        self.assertEqual(counts, {"positive_negative_pairs": 6, "concordant_pairs": 3,
                                  "tied_pairs": 2, "discordant_pairs": 1})
        order = [4, 1, 3, 0, 2]
        self.assertEqual(verify.compute_auc([scores[index] for index in order],
                                           [labels[index] for index in order]), (result, counts))
        inverted = [verify.NEGATIVE if label == verify.POSITIVE else verify.POSITIVE for label in labels]
        self.assertEqual(verify.compute_auc(scores, inverted)[0], 1 - result)

    def test_source_precision_is_not_rounded_into_a_tie(self):
        scores = ["0.500000000000000000000000000001", "0.5"]
        self.assertEqual(verify.compute_auc(scores, [verify.POSITIVE, verify.NEGATIVE])[0], 1)
        self.assertEqual(verify.probability("5E-1"), verify.probability("0.500"))

    def test_invalid_scores_are_rejected_without_imputation(self):
        for value in (None, True, 0.5, "", " ", " 0.5", "0.5 ", "NaN", "sNaN", "Infinity",
                      "-Infinity", "1.0001", "-0.1", "0_5", "private-score-token"):
            with self.subTest(value=value), self.assertRaises(audit.AuditError):
                verify.compute_auc([value, "0.5"], [verify.POSITIVE, verify.NEGATIVE])

    def test_one_class_empty_mismatched_and_unknown_labels_fail(self):
        failures = (([], []), (["0.1"], []), (["0.1", "0.2"], [verify.POSITIVE] * 2),
                    (["0.1"], [verify.NEGATIVE]), (["0.1", "0.2"], [verify.POSITIVE, "unknown"]))
        for scores, labels in failures:
            with self.subTest(labels=labels), self.assertRaises(audit.AuditError):
                verify.compute_auc(scores, labels)

    def test_independent_rank_disagreement_stops_the_check(self):
        with mock.patch.object(verify, "rank_auc", return_value=Fraction(0)), self.assertRaises(audit.AuditError):
            verify.compute_auc(["1", "0"], [verify.POSITIVE, verify.NEGATIVE])

    def test_exact_join_preserves_score_key_pairing(self):
        negative = abstract_record("alpha")
        positive = abstract_record("beta", verify.POSITIVE)
        rows = [{"A": positive[audit.LABEL_COLUMN], "B": "0.9"},
                {"A": negative[audit.LABEL_COLUMN], "B": "0.1"}]
        scores, labels, joined = verify.join_predictions(rows, [negative, positive])
        self.assertEqual(scores, ["0.9", "0.1"])
        self.assertEqual(labels, [verify.POSITIVE, verify.NEGATIVE])
        self.assertEqual(joined, [positive, negative])
        self.assertEqual(verify.compute_auc(scores, labels)[0], 1)

    def test_missing_ambiguous_duplicate_and_incomplete_prediction_joins_fail(self):
        record = abstract_record("alpha")
        row = {"A": record[audit.LABEL_COLUMN], "B": "0.5"}
        failures = (([{"A": "abstract-absent", "B": "0.5"}], [record]),
                    ([row], [record, copy.deepcopy(record)]), ([row, row], [record]),
                    ([{"A": record[audit.LABEL_COLUMN]}], [record]))
        for rows, records in failures:
            with self.subTest(rows=rows), self.assertRaises(audit.AuditError):
                verify.join_predictions(rows, records)

    def test_tolerance_and_half_up_rounding_are_distinct_exact_checks(self):
        for value in (Fraction(81, 100), Fraction(85, 100)):
            result = verify.comparison(value)
            self.assertTrue(result["within_0_02_model_tolerance"])
            self.assertFalse(result["reproduces_displayed_0_83"])
        self.assertFalse(verify.comparison(Fraction(85001, 100000))["within_0_02_model_tolerance"])
        self.assertTrue(verify.comparison(Fraction(825, 1000))["reproduces_displayed_0_83"])
        self.assertFalse(verify.comparison(Fraction(835, 1000))["reproduces_displayed_0_83"])

    def test_mocked_fixed_cohort_run_emits_only_aggregate_result_and_provenance(self):
        with mock.patch.object(audit, "Workbook", workbook_double()):
            output = verify.run_verification()
        encoded = json.dumps(output, allow_nan=False)
        self.assertEqual(output["metric"]["auc_exact"], {"numerator": 1, "denominator": 2})
        self.assertEqual(output["metric"]["pair_counts"]["positive_negative_pairs"], 4316)
        self.assertEqual(output["selection"]["positive_count"], 52)
        self.assertEqual(output["selection"]["negative_count"], 83)
        self.assertEqual(output["selection"]["retained_score_cohort_location_group_NA"], 1)
        self.assertIsNone(output["metric"]["confidence_interval"])
        self.assertFalse(output["metric"]["comparison"]["within_0_02_model_tolerance"])
        for prefix in ("abstract-label-", "abstract-person-", "abstract-specimen-", "0.375"):
            self.assertNotIn(prefix, encoded)
        for key in ("tool_sha256", "membership_helper_sha256"):
            self.assertRegex(output["execution"][key], r"^[0-9a-f]{64}$")
        self.assertEqual(output["sources"]["clinical"]["sha256"], audit.SOURCES["clinical"]["sha256"])

    def test_fixed_cohort_class_drift_stops_before_metric_calculation(self):
        original_join = verify.join_predictions

        def changed_join(rows, records):
            scores, labels, joined = original_join(rows, records)
            labels[-1] = verify.NEGATIVE
            return scores, labels, joined

        with mock.patch.object(audit, "Workbook", workbook_double()), \
                mock.patch.object(verify, "join_predictions", side_effect=changed_join), \
                mock.patch.object(verify, "compute_auc") as metric, self.assertRaises(audit.AuditError):
            verify.run_verification()
        metric.assert_not_called()

    def test_missing_contract_stops_before_network_access(self):
        with mock.patch.object(Path, "is_file", return_value=False), \
                mock.patch.object(audit, "Workbook") as workbook, self.assertRaises(audit.AuditError):
            verify.run_verification()
        workbook.assert_not_called()

    def test_help_is_offline_and_contains_the_review_contract_and_command(self):
        completed = subprocess.run([sys.executable, str(ROOT / "tools/verify_published_auc.py"), "--help"],
                                   capture_output=True, text=True, timeout=10, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(verify.CONTRACT, completed.stdout)
        self.assertIn("python3 tools/verify_published_auc.py", completed.stdout)
        self.assertEqual(completed.stderr, "")

    def test_cli_failure_is_sanitized_without_partial_output(self):
        for error in (audit.AuditError("private-score-token"), RuntimeError("private-url-token")):
            stdout, stderr = io.StringIO(), io.StringIO()
            with mock.patch.object(verify, "run_verification", side_effect=error), \
                    contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = verify.main([])
            self.assertEqual(result, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), verify.FAILURE_MESSAGE + "\n")
            self.assertNotIn(str(error), stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
