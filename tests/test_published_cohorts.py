"""Offline cohort-contract tests with abstract tokens, not workbook or patient data."""

import contextlib
import copy
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_published_cohorts as audit


def record(label="label-alpha", patient="abstract-patient-alpha", sample="abstract-sample-alpha", **changes):
    result = {
        audit.LABEL_COLUMN: label,
        "Patient ID": patient,
        "Sample ID": sample,
        "Neo-adjuvant": "no",
        "Tumor response": "sensitive",
        "Tumor Location Group": "OM",
        "Sample type": "abstract-tissue",
    }
    result.update(changes)
    return result


def missing_response_record():
    return record("label-missing", **{
        field: "NA" for field in (
            "Patient ID", "Sample ID", "Neo-adjuvant", "Tumor response",
            "Tumor Location Group", "Sample type",
        )
    })


class PublishedCohortChecks(unittest.TestCase):
    def test_classification_separates_literal_na_rows(self):
        biological = record()
        inputs = [biological, missing_response_record()]
        original = copy.deepcopy(inputs)
        selected, missing_rows = audit.classify_clinical(inputs)
        self.assertEqual(selected, [biological])
        self.assertEqual(missing_rows, [inputs[1]])
        self.assertEqual(inputs, original)
        # Literal NA labels are allowed only on fully classified NA rows; they
        # cannot become score keys or silently enter the biological population.
        na_label = missing_response_record()
        na_label[audit.LABEL_COLUMN] = "NA"
        self.assertEqual(audit.classify_clinical([na_label]), ([], [na_label]))

    def test_clinical_contract_rejects_wrong_flags_and_partial_missingness(self):
        changes = (
            {"Tumor response": "Sensitive"},
            {"Tumor response": "unknown"},
            {"Tumor response": "NA"},
            {"Neo-adjuvant": "Yes"},
            {"Neo-adjuvant": "NA"},
            {"Tumor Location Group": "UNKNOWN"},
            {"Patient ID": "NA"},
            {"Sample ID": ""},
            {"Sample type": "NA"},
            {audit.LABEL_COLUMN: "   "},
            {audit.LABEL_COLUMN: "NA"},
        )
        for change in changes:
            with self.subTest(change=change), self.assertRaises(audit.AuditError):
                audit.classify_clinical([record(**change)])
        for field in record():
            with self.subTest(missing=field):
                incomplete = record()
                del incomplete[field]
                with self.assertRaises(audit.AuditError):
                    audit.classify_clinical([incomplete])
        for field in ("Patient ID", "Sample ID", "Neo-adjuvant", "Sample type"):
            with self.subTest(na_row_field=field):
                incomplete = missing_response_record()
                incomplete[field] = ""
                with self.assertRaises(audit.AuditError):
                    audit.classify_clinical([incomplete])

    def test_technical_replicates_collapse_by_sample_and_require_agreement(self):
        first = record()
        replicate = record(label="label-replicate")
        other_specimen = record(label="label-other", sample="abstract-sample-other")
        unique = audit.collapse_replicates([first, replicate, other_specimen])
        self.assertEqual(unique, [first, other_specimen])
        self.assertEqual(audit.patient_keys(unique), {first["Patient ID"]})
        self.assertEqual(audit.sample_keys(unique), {
            first["Sample ID"], other_specimen["Sample ID"],
        })
        replacements = {
            "Patient ID": "abstract-patient-other",
            "Neo-adjuvant": "yes",
            "Tumor response": "refractory",
            "Tumor Location Group": "OV",
            "Sample type": "abstract-other-tissue",
        }
        for field in audit.CRITICAL:
            if field == "Sample ID":
                continue
            with self.subTest(disagreement=field):
                conflicting = copy.deepcopy(replicate)
                conflicting[field] = replacements[field]
                with self.assertRaises(audit.AuditError):
                    audit.collapse_replicates([first, conflicting])

    def test_score_join_uses_exact_technical_label(self):
        first = record()
        replicate = record(label="label-replicate")
        self.assertEqual(
            audit.join_score_membership(["label-replicate"], [first, replicate]),
            [replicate],
        )
        for key in ("LABEL-ALPHA", " label-alpha", "label-alpha ", "label-absent"):
            with self.subTest(key=key), self.assertRaises(audit.AuditError):
                audit.join_score_membership([key], [first])

    def test_score_keys_must_be_nonempty_and_unique(self):
        for keys in ([""], ["   "], [None], ["label-alpha", "label-alpha"]):
            with self.subTest(keys=keys), self.assertRaises(audit.AuditError):
                audit.join_score_membership(keys, [record()])

    def test_score_join_rejects_ambiguous_na_and_repeated_identities(self):
        first = record()
        failures = (
            (["label-alpha"], [first, copy.deepcopy(first)]),
            (["label-missing"], [missing_response_record()]),
            (["label-alpha", "label-replicate"], [first, record(label="label-replicate")]),
            (["label-alpha", "label-other"], [
                first, record(label="label-other", sample="abstract-sample-other"),
            ]),
            (["label-alpha", "label-other"], [
                first, record(label="label-other", patient="abstract-patient-other"),
            ]),
        )
        for keys, clinical in failures:
            with self.subTest(keys=keys, clinical=clinical), self.assertRaises(audit.AuditError):
                audit.join_score_membership(keys, clinical)

    def test_patient_overlap_does_not_require_identical_specimens(self):
        reference = [record()]
        candidates = [
            record(label="label-other", sample="abstract-sample-other"),
            record("label-beta", "abstract-patient-beta", "abstract-sample-beta"),
        ]
        self.assertEqual(audit.sample_keys(candidates) & audit.sample_keys(reference), set())
        self.assertEqual(audit.patient_overlap(candidates, reference), {
            "patient_keys_shared": 1, "patient_keys_not_observed": 1,
        })
        self.assertEqual(audit.patient_overlap(candidates + candidates, reference), {
            "patient_keys_shared": 1, "patient_keys_not_observed": 1,
        })

    def test_neo_and_mixed_location_exclusions_change_overlap(self):
        reference = [record(), record("label-beta", "abstract-patient-beta", "abstract-sample-beta")]
        candidates = [
            record("label-neo", sample="abstract-sample-neo", **{"Neo-adjuvant": "yes"}),
            record("label-mix", "abstract-patient-beta", "abstract-sample-mix", **{
                "Tumor Location Group": "Mix",
            }),
            record("label-gamma", "abstract-patient-gamma", "abstract-sample-gamma"),
        ]
        self.assertEqual(audit.patient_overlap(candidates, reference), {
            "patient_keys_shared": 2, "patient_keys_not_observed": 1,
        })
        eligible = audit.eligible_samples(audit.collapse_replicates(candidates))
        self.assertEqual(eligible, [candidates[2]])
        self.assertEqual(audit.patient_overlap(eligible, reference), {
            "patient_keys_shared": 0, "patient_keys_not_observed": 1,
        })

    def test_literal_na_location_is_preserved_for_membership_reconstruction(self):
        unresolved = record(**{"Tumor Location Group": "NA"})
        self.assertEqual(audit.classify_clinical([unresolved]), ([unresolved], []))
        self.assertEqual(audit.eligible_samples([unresolved]), [unresolved])
        self.assertEqual(audit.join_score_membership(["label-alpha"], [unresolved]), [unresolved])
        self.assertEqual(unresolved["Tumor Location Group"], "NA")
        unresolved["Neo-adjuvant"] = "yes"
        self.assertEqual(audit.eligible_samples([unresolved]), [])

    def test_help_succeeds_offline(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools/audit_published_cohorts.py"), "--help"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("usage:", completed.stdout.lower())
        self.assertEqual(completed.stderr, "")

    def test_cli_failures_are_sanitized(self):
        messages = []
        for error in (audit.AuditError("private-row-token"), RuntimeError("private-url-token")):
            stdout, stderr = io.StringIO(), io.StringIO()
            with mock.patch.object(audit, "run_audit", side_effect=error), \
                    contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertNotEqual(audit.main([]), 0)
            self.assertEqual(stdout.getvalue(), "")
            message = stderr.getvalue()
            self.assertTrue(message.strip())
            self.assertEqual(len(message.strip().splitlines()), 1)
            self.assertNotIn(str(error), message)
            self.assertNotIn("Traceback", message)
            messages.append(message)
        self.assertEqual(messages[0], messages[1])


if __name__ == "__main__":
    unittest.main()
