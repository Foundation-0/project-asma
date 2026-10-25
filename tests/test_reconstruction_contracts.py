"""Offline checks of the declared reconstruction conventions using abstract tokens only."""

import contextlib
import hashlib
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
import reconstruction_contracts as contracts
import verify_published_auc as verify


def abstract_cohort(positives=52, negatives=83):
    """Patient labels in the published discovery shape, with abstract keys."""
    labels = {f"abstract-person-{index:03d}": contracts.POSITIVE for index in range(positives)}
    labels.update({f"abstract-person-{index:03d}": contracts.NEGATIVE
                   for index in range(positives, positives + negatives)})
    return labels


def abstract_predictions(labels, assignments, models=contracts.MODELS, value="0.5"):
    for repetition, assignment in assignments.items():
        for model in models:
            for patient, fold in assignment.items():
                yield {"repetition": repetition, "fold": fold, "model": model,
                       "patient": patient, "probability": value}


class FoldAssignmentChecks(unittest.TestCase):
    def test_every_repetition_is_patient_complete_stratified_and_class_balanced(self):
        labels = abstract_cohort()
        for seed in contracts.REPETITIONS:
            assignment = contracts.assign_folds(labels, seed)
            self.assertEqual(set(assignment), set(labels))
            for fold in range(1, contracts.FOLDS + 1):
                members = [patient for patient, value in assignment.items() if value == fold]
                positives = sum(labels[patient] == contracts.POSITIVE for patient in members)
                self.assertIn(positives, (10, 11))
                self.assertIn(len(members) - positives, (16, 17))

    def test_assignment_is_deterministic_per_seed_and_independent_of_input_order(self):
        labels = abstract_cohort()
        reversed_labels = dict(reversed(list(labels.items())))
        first = contracts.assign_folds(labels, 7)
        self.assertEqual(first, contracts.assign_folds(labels, 7))
        self.assertEqual(first, contracts.assign_folds(reversed_labels, 7))
        self.assertNotEqual(first, contracts.assign_folds(labels, 8))
        self.assertGreater(len({json.dumps(contracts.assign_folds(labels, seed), sort_keys=True)
                                for seed in range(1, 11)}), 1)

    def test_convention_fingerprint_is_pinned(self):
        # Changing the hashing or dealing rule must fail here, so the declared
        # convention cannot drift silently between the record and the code.
        labels = abstract_cohort(positives=6, negatives=9)
        encoded = json.dumps(contracts.assign_folds(labels, 1, folds=3), sort_keys=True)
        self.assertEqual(hashlib.sha256(encoded.encode()).hexdigest(),
                         "9132b318a33cee2a971670bdd671f7d4e0a355b7c45236185d1478f938547677")

    def test_patients_group_measurements_and_conflicts_fail(self):
        measurements = [("m1", "p1", contracts.POSITIVE), ("m2", "p1", contracts.POSITIVE),
                        ("m3", "p2", contracts.NEGATIVE)]
        labels, sizes = contracts.patient_labels(measurements)
        self.assertEqual(labels, {"p1": contracts.POSITIVE, "p2": contracts.NEGATIVE})
        self.assertEqual(sizes, {"p1": 2, "p2": 1})
        failures = ([("m1", "p1", contracts.POSITIVE), ("m2", "p1", contracts.NEGATIVE)],
                    [("m1", "p1", contracts.POSITIVE), ("m1", "p2", contracts.NEGATIVE)],
                    [("m1", "NA", contracts.POSITIVE)], [("m1", "p1", "unknown")], [("m1", "p1")], [])
        for entries in failures:
            with self.subTest(entries=entries), self.assertRaises(contracts.ContractError):
                contracts.patient_labels(entries)

    def test_small_classes_bad_seeds_and_bad_labels_fail(self):
        labels = abstract_cohort(positives=4, negatives=9)
        with self.assertRaises(contracts.ContractError):
            contracts.assign_folds(labels, 1)
        good = abstract_cohort(positives=6, negatives=9)
        for seed in (0, -1, True, 1.0, "1"):
            with self.subTest(seed=seed), self.assertRaises(contracts.ContractError):
                contracts.assign_folds(good, seed)
        for folds in (1, 5.0, "5"):
            with self.subTest(folds=folds), self.assertRaises(contracts.ContractError):
                contracts.assign_folds(good, 1, folds=folds)
        for bad in ({}, {"NA": contracts.POSITIVE}, {" p": contracts.NEGATIVE}, {"p": "unknown"}):
            with self.subTest(bad=bad), self.assertRaises(contracts.ContractError):
                contracts.assign_folds(dict(good, **bad) if bad else bad, 1)


class OrderingAndReplicateChecks(unittest.TestCase):
    def test_panel_rows_are_located_once_in_matrix_order(self):
        symbols = ["z-feature", "b-feature", "x-feature", "a-feature", "b-feature-2"]
        self.assertEqual(contracts.panel_rows(symbols, ["a-feature", "b-feature"]), [1, 3])
        self.assertEqual(contracts.panel_rows(symbols, ["b-feature", "a-feature"]), [1, 3])
        ordered = [symbols[index] for index in contracts.panel_rows(symbols, ["a-feature", "x-feature"])]
        self.assertEqual(contracts.fingerprint(ordered), contracts.fingerprint(["x-feature", "a-feature"]))

    def test_panel_rows_reject_missing_repeated_or_inexact_symbols(self):
        symbols = ["a-feature", "b-feature", "b-feature", " c-feature"]
        failures = (["absent"], ["b-feature"], ["c-feature"], ["A-FEATURE"], ["a-feature", "a-feature"],
                    [], ["a-feature", "NA"])
        for panel in failures:
            with self.subTest(panel=panel), self.assertRaises(contracts.ContractError):
                contracts.panel_rows(symbols, panel)

    def test_replicates_average_exactly_per_sample_key_without_missing_value_removal(self):
        sample_of = {"col-1": "specimen-a", "col-2": "specimen-a", "col-3": "specimen-a", "col-4": "specimen-b"}
        values = {"col-1": ["1.0", "4"], "col-2": ["2", "5.5"], "col-3": ["3", "6.5"], "col-4": ["7", "8"]}
        collapsed, summary = contracts.collapse_measurements(sample_of, values)
        self.assertEqual(collapsed, {"specimen-a": [Fraction(2), Fraction(16, 3)], "specimen-b": [Fraction(7), Fraction(8)]})
        self.assertEqual(summary, {"samples": 2, "columns": 4, "group_sizes": {"1": 1, "3": 1}})
        for broken in ({"col-2": ["NA", "5.5"]}, {"col-2": ["2"]}, {"col-2": [2, 5.5]}, {"col-2": []}):
            with self.subTest(broken=broken), self.assertRaises(contracts.ContractError):
                contracts.collapse_measurements(sample_of, dict(values, **broken))
        with self.assertRaises(contracts.ContractError):
            contracts.collapse_measurements(sample_of, {key: values[key] for key in list(values)[:3]})

    def test_numbers_are_exact_and_never_coerced(self):
        self.assertEqual(contracts.number("0.1") + contracts.number("0.2"), Fraction(3, 10))
        self.assertEqual(contracts.number("5E-1"), Fraction(1, 2))
        for value in (None, 0.5, "", " 1", "1 ", "NaN", "Infinity", "1,5", "abstract-token"):
            with self.subTest(value=value), self.assertRaises(contracts.ContractError):
                contracts.number(value)


class AggregationChecks(unittest.TestCase):
    def setUp(self):
        self.labels = abstract_cohort(positives=6, negatives=9)
        self.repetitions = (1, 2)
        self.assignments = {seed: contracts.assign_folds(self.labels, seed, folds=3) for seed in self.repetitions}

    def records(self, probability):
        for repetition, assignment in self.assignments.items():
            for model in contracts.MODELS:
                for patient, fold in assignment.items():
                    yield {"repetition": repetition, "fold": fold, "model": model,
                           "patient": patient, "probability": probability(repetition, model, patient)}

    def test_two_stage_mean_is_exact_and_order_independent(self):
        values = {"elastic_net": "0.1", "xgboost": "0.2", "random_forest": "0.6"}

        def probability(repetition, model, patient):
            return values[model] if repetition == 1 else "1"

        records = list(self.records(probability))
        final, coverage = contracts.aggregate_predictions(records, self.assignments, self.labels,
                                                          repetitions=self.repetitions)
        # Repetition 1 averages to 0.3 and repetition 2 to 1; the mean is 0.65.
        self.assertEqual(set(final.values()), {Fraction(13, 20)})
        self.assertEqual(coverage, {"repetitions": 2, "models": 3, "patients": 15,
                                    "held_out_predictions": 90, "predictions_per_patient": 6})
        shuffled = list(reversed(records))
        self.assertEqual(contracts.aggregate_predictions(shuffled, self.assignments, self.labels,
                                                         repetitions=self.repetitions)[0], final)

    def test_missing_duplicate_mismatched_and_invalid_predictions_stop_the_run(self):
        records = list(self.records(lambda *_: "0.5"))
        duplicate = records + [records[0]]
        shifted = [dict(record, fold=record["fold"] % 3 + 1) if index == 0 else record
                   for index, record in enumerate(records)]
        stranger = records[1:] + [dict(records[0], patient="abstract-person-999")]
        unknown_model = records[1:] + [dict(records[0], model="stack")]
        unknown_repetition = records[1:] + [dict(records[0], repetition=3)]
        boolean_repetition = records[1:] + [dict(records[0], repetition=True)]
        out_of_range = records[1:] + [dict(records[0], probability="1.5")]
        missing_value = records[1:] + [dict(records[0], probability="NA")]
        float_value = records[1:] + [dict(records[0], probability=0.5)]
        incomplete = records[1:]
        for name, broken in (("duplicate", duplicate), ("shifted", shifted), ("stranger", stranger),
                             ("unknown_model", unknown_model), ("unknown_repetition", unknown_repetition),
                             ("boolean_repetition", boolean_repetition), ("out_of_range", out_of_range),
                             ("missing_value", missing_value), ("float_value", float_value),
                             ("incomplete", incomplete)):
            with self.subTest(case=name), self.assertRaises(contracts.ContractError):
                contracts.aggregate_predictions(broken, self.assignments, self.labels, repetitions=self.repetitions)
        with self.assertRaises(contracts.ContractError):
            contracts.aggregate_predictions(records, {1: self.assignments[1]}, self.labels,
                                            repetitions=self.repetitions)
        with self.assertRaises(contracts.ContractError):
            contracts.aggregate_predictions(records, self.assignments, dict(list(self.labels.items())[:-1]),
                                            repetitions=self.repetitions)

    def test_auroc_matches_the_executed_check_definition_including_ties(self):
        scores = {"abstract-person-000": "0.9", "abstract-person-001": "0.5", "abstract-person-002": "0.5",
                  "abstract-person-003": "0.1"}
        labels = {"abstract-person-000": contracts.POSITIVE, "abstract-person-001": contracts.POSITIVE,
                  "abstract-person-002": contracts.NEGATIVE, "abstract-person-003": contracts.NEGATIVE}
        final = {patient: contracts.number(value) for patient, value in scores.items()}
        result, counts = contracts.auroc(final, labels)
        ordered = sorted(scores)
        expected, expected_counts = verify.compute_auc([scores[patient] for patient in ordered],
                                                       [labels[patient] for patient in ordered])
        self.assertEqual((result, counts), (expected, expected_counts))
        self.assertEqual(result, Fraction(7, 8))
        inverted = {patient: contracts.NEGATIVE if label == contracts.POSITIVE else contracts.POSITIVE
                    for patient, label in labels.items()}
        self.assertEqual(contracts.auroc(final, inverted)[0], 1 - result)

    def test_auroc_rejects_incomplete_one_class_or_disagreeing_inputs(self):
        final = {"abstract-person-000": Fraction(1, 2), "abstract-person-001": Fraction(1, 4)}
        labels = {"abstract-person-000": contracts.POSITIVE, "abstract-person-001": contracts.NEGATIVE}
        with self.assertRaises(contracts.ContractError):
            contracts.auroc({"abstract-person-000": Fraction(1, 2)}, labels)
        with self.assertRaises(contracts.ContractError):
            contracts.auroc(final, {key: contracts.POSITIVE for key in labels})
        with self.assertRaises(contracts.ContractError):
            contracts.auroc({"abstract-person-000": 0.5, "abstract-person-001": Fraction(1, 4)}, labels)
        with mock.patch.object(verify, "rank_auc", return_value=Fraction(0)), \
                self.assertRaises(contracts.ContractError):
            contracts.auroc(final, labels)


class ContractDescriptionChecks(unittest.TestCase):
    def test_declared_contract_pins_documents_and_carries_no_tokens(self):
        output = contracts.declared_contract()
        for relative, digest in output["documents"].items():
            self.assertEqual(digest, hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())
        self.assertEqual(output["folds"]["count"], 5)
        self.assertEqual(output["folds"]["repetition_seeds"], {"first": 1, "last": 100, "count": 100})
        self.assertEqual(output["cohort"]["patients"], 135)
        self.assertEqual(output["models"], ["elastic_net", "xgboost", "random_forest"])
        self.assertNotIn("abstract-", json.dumps(output))

    def test_missing_decision_record_fails_safely(self):
        with mock.patch.object(Path, "is_file", return_value=False), self.assertRaises(contracts.ContractError):
            contracts.declared_contract()

    def test_cli_is_offline_and_failures_are_sanitized(self):
        completed = subprocess.run([sys.executable, str(ROOT / "tools/reconstruction_contracts.py")],
                                   capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["folds"]["count"], 5)
        self.assertEqual(completed.stderr, "")
        helped = subprocess.run([sys.executable, str(ROOT / "tools/reconstruction_contracts.py"), "--help"],
                                capture_output=True, text=True, timeout=20, check=False)
        self.assertIn(contracts.DECISION_RECORD, helped.stdout)
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(contracts, "declared_contract", side_effect=RuntimeError("private-token")), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(contracts.main([]), 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), contracts.FAILURE_MESSAGE + "\n")


if __name__ == "__main__":
    unittest.main()
