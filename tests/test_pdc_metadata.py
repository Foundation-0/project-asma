"""Offline contract checks using abstract relationship tokens, not patient data."""

import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_pdc_metadata as audit


STUDY_IDS = ("PDC000360", "PDC000358", "PDC000362")


def relationship(case, sample, aliquot, *, reference="No", pool="No"):
    """Describe only arbitrary graph identities and flags for parser tests."""
    return {
        "case_id": "case-" + case,
        "sample_id": "sample-" + sample,
        "aliquot_id": "aliquot-" + aliquot,
        "aliquot_is_ref": reference,
        "pool": pool,
        "project_name": "abstract-project",
    }


def fixture():
    reference = relationship("reference", "reference", "reference", reference="Yes")
    shared = relationship("shared", "shared", "shared")
    rows = {
        STUDY_IDS[0]: [
            relationship("alpha", "alpha", "alpha"),
            relationship("alpha", "alpha-other", "alpha-other"),
            copy.deepcopy(shared),
            relationship("pooled", "pooled", "pooled", pool="Yes"),
            copy.deepcopy(reference),
        ],
        STUDY_IDS[1]: [
            relationship("beta", "beta", "beta"),
            relationship("pooled", "pooled-other", "pooled-other", pool="Yes"),
            copy.deepcopy(reference),
        ],
        STUDY_IDS[2]: [
            relationship("gamma", "gamma", "gamma"),
            copy.deepcopy(shared),
            copy.deepcopy(reference),
        ],
    }
    studies = {
        study: {
            "study_id": f"abstract-study-{index}",
            "pdc_study_id": study,
            "submitter_id_name": f"Abstract catalog entry {index}",
            "cases_count": len({row["case_id"] for row in entries}),
            "aliquots_count": len(entries),
            "embargo_date": None,
            "versions": [{"number": "1"}],
        }
        for index, (study, entries) in enumerate(rows.items())
    }
    return studies, rows, copy.deepcopy(studies)


class MetadataAuditChecks(unittest.TestCase):
    def test_target_studies_and_aggregate_counts(self):
        self.assertEqual(audit.STUDY_IDS, STUDY_IDS)
        studies, rows, after = fixture()
        original = copy.deepcopy((studies, rows, after))
        result = audit.summarize(studies, rows, after)
        self.assertEqual(set(result["studies"]), set(STUDY_IDS))
        first = result["studies"][STUDY_IDS[0]]
        self.assertEqual(first["rows"], 5)
        self.assertEqual(first["reference_rows"], 1)
        self.assertEqual(first["non_reference_rows"], 4)
        self.assertEqual(first["pooled_non_reference_rows"], 1)
        self.assertEqual(first["unique_counts"]["all"], {
            "case_id": 4, "sample_id": 5, "aliquot_id": 5,
        })
        self.assertEqual(first["unique_counts"]["non_reference"], {
            "case_id": 3, "sample_id": 4, "aliquot_id": 4,
        })
        self.assertEqual((studies, rows, after), original)

    def test_overlap_excludes_references_and_retains_pooled_cases(self):
        result = audit.summarize(*fixture())
        overlaps = {(row["a"], row["b"]): row for row in result["overlap"]}
        expected = {
            (STUDY_IDS[0], STUDY_IDS[1]): (1, 2, 1),
            (STUDY_IDS[0], STUDY_IDS[2]): (1, 2, 1),
            (STUDY_IDS[1], STUDY_IDS[2]): (0, 2, 2),
        }
        self.assertEqual(set(overlaps), set(expected))
        for pair, counts in expected.items():
            with self.subTest(pair=pair):
                row = overlaps[pair]
                self.assertEqual((
                    row["shared_non_reference_cases"],
                    row["a_no_overlap_observed_cases"],
                    row["b_no_overlap_observed_cases"],
                ), counts)

    def test_aggregate_output_does_not_disclose_relationship_tokens(self):
        studies, rows, after = fixture()
        encoded = json.dumps(audit.summarize(studies, rows, after))
        identifiers = {
            row[field]
            for entries in rows.values()
            for row in entries
            for field in ("case_id", "sample_id", "aliquot_id")
        }
        for identifier in identifiers:
            self.assertNotIn(identifier, encoded)

    def test_missing_and_blank_row_fields_are_rejected(self):
        fields = tuple(fixture()[1][STUDY_IDS[0]][0])
        for field in fields:
            for value in (None, "", "   "):
                with self.subTest(field=field, value=value):
                    studies, rows, after = fixture()
                    rows[STUDY_IDS[0]][0][field] = value
                    with self.assertRaises(audit.AuditError):
                        audit.summarize(studies, rows, after)
            with self.subTest(missing=field):
                studies, rows, after = fixture()
                del rows[STUDY_IDS[0]][0][field]
                with self.assertRaises(audit.AuditError):
                    audit.summarize(studies, rows, after)

    def test_noncanonical_flags_are_rejected(self):
        for field in ("aliquot_is_ref", "pool"):
            for value in ("yes", "no", "Unknown", True, 0):
                with self.subTest(field=field, value=value):
                    studies, rows, after = fixture()
                    rows[STUDY_IDS[0]][0][field] = value
                    with self.assertRaises(audit.AuditError):
                        audit.summarize(studies, rows, after)

    def test_duplicate_row_or_aliquot_within_study_is_rejected(self):
        for changed_mapping in (False, True):
            with self.subTest(changed_mapping=changed_mapping):
                studies, rows, after = fixture()
                duplicate = copy.deepcopy(rows[STUDY_IDS[0]][0])
                if changed_mapping:
                    duplicate["sample_id"] = "sample-conflict"
                rows[STUDY_IDS[0]].append(duplicate)
                with self.assertRaises(audit.AuditError):
                    audit.summarize(studies, rows, after)

    def test_global_identity_and_project_conflicts_are_rejected(self):
        changes = (
            {"sample_id": "sample-alpha"},
            {"aliquot_id": "aliquot-alpha"},
            {"case_id": "case-shared", "project_name": "different-project"},
        )
        for change in changes:
            with self.subTest(change=change):
                studies, rows, after = fixture()
                rows[STUDY_IDS[1]][0].update(change)
                with self.assertRaises(audit.AuditError):
                    audit.summarize(studies, rows, after)

    def test_shared_aliquot_flags_must_agree(self):
        # An identical shared aliquot succeeds in the unmodified fixture.
        for field in ("aliquot_is_ref", "pool"):
            with self.subTest(field=field):
                studies, rows, after = fixture()
                rows[STUDY_IDS[2]][1][field] = "Yes"
                with self.assertRaises(audit.AuditError):
                    audit.summarize(studies, rows, after)

    def test_catalog_counts_must_match_observed_unique_identities(self):
        for field in ("cases_count", "aliquots_count"):
            with self.subTest(field=field):
                studies, rows, after = fixture()
                studies[STUDY_IDS[0]][field] += 1
                after[STUDY_IDS[0]][field] += 1
                with self.assertRaises(audit.AuditError):
                    audit.summarize(studies, rows, after)

    def test_required_catalog_fields_are_checked(self):
        for field in fixture()[0][STUDY_IDS[0]]:
            with self.subTest(missing=field):
                studies, rows, after = fixture()
                del studies[STUDY_IDS[0]][field]
                del after[STUDY_IDS[0]][field]
                with self.assertRaises(audit.AuditError):
                    audit.summarize(studies, rows, after)

    def test_wrong_catalog_identity_version_or_embargo_is_rejected(self):
        changes = (
            {"study_id": ""},
            {"submitter_id_name": "   "},
            {"pdc_study_id": "PDC999999"},
            {"versions": [{"number": "2"}]},
            {"versions": []},
            {"embargo_date": "2099-01-01"},
            {"cases_count": True},
            {"aliquots_count": "5"},
        )
        for change in changes:
            with self.subTest(change=change):
                studies, rows, after = fixture()
                studies[STUDY_IDS[0]].update(copy.deepcopy(change))
                after[STUDY_IDS[0]].update(copy.deepcopy(change))
                with self.assertRaises(audit.AuditError):
                    audit.summarize(studies, rows, after)

    def test_before_after_catalog_drift_is_rejected(self):
        changes = (
            {"study_id": "abstract-replacement-study"},
            {"versions": [{"number": "2"}]},
            {"cases_count": 5},
            {"aliquots_count": 6},
        )
        for change in changes:
            with self.subTest(change=change):
                studies, rows, after = fixture()
                after[STUDY_IDS[0]].update(change)
                with self.assertRaises(audit.AuditError):
                    audit.summarize(studies, rows, after)

    def test_canonical_fingerprint_is_key_order_independent_and_content_sensitive(self):
        original = {"z": [{"b": 2, "a": 1}], "a": [1, 2]}
        reordered = {"a": [1, 2], "z": [{"a": 1, "b": 2}]}
        digest = audit.canonical_sha256(original)
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(digest, audit.canonical_sha256(reordered))
        self.assertNotEqual(digest, audit.canonical_sha256({**original, "a": [2, 1]}))
        self.assertNotEqual(digest, audit.canonical_sha256({**original, "a": [1, 3]}))

    def test_fetch_workflow_pins_study_identity_and_rechecks_after_all_linkage_queries(self):
        studies, rows, after = fixture()

        def responses(final_studies):
            before_responses = [
                {"data": {"getPaginatedUIStudy": {"total": None, "uiStudies": [studies[key]]}}}
                for key in STUDY_IDS
            ]
            linkage_responses = [
                {"data": {"uiBiospecimenPerStudy": rows[key]}}
                for key in STUDY_IDS
            ]
            after_responses = [
                {"data": {"getPaginatedUIStudy": {"total": None, "uiStudies": [final_studies[key]]}}}
                for key in STUDY_IDS
            ]
            return before_responses + linkage_responses + after_responses

        with mock.patch.object(audit, "fetch_response", side_effect=responses(after)) as fetch:
            result = audit.run_audit()
        expected_queries = [mock.call(audit.STUDY_QUERY, {"id": key}) for key in STUDY_IDS]
        expected_queries += [
            mock.call(audit.BIOSPECIMEN_QUERY, {"id": studies[key]["study_id"]})
            for key in STUDY_IDS
        ]
        expected_queries += [mock.call(audit.STUDY_QUERY, {"id": key}) for key in STUDY_IDS]
        self.assertEqual(fetch.call_args_list, expected_queries)
        encoded = json.dumps(result)
        for key in STUDY_IDS:
            aggregate = result["studies"][key]
            self.assertEqual(aggregate["pdc_study_id"], key)
            self.assertEqual(aggregate["study_id"], studies[key]["study_id"])
            self.assertEqual(aggregate["study_version"], "1")
            for row in rows[key]:
                for field in ("case_id", "sample_id", "aliquot_id"):
                    self.assertNotIn(row[field], encoded)

        after[STUDY_IDS[0]]["study_id"] = "abstract-replacement-study"
        with mock.patch.object(audit, "fetch_response", side_effect=responses(after)):
            with self.assertRaises(audit.AuditError):
                audit.run_audit()

    def test_help_succeeds_offline(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools/audit_pdc_metadata.py"), "--help"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("usage:", completed.stdout.lower())
        self.assertEqual(completed.stderr, "")

    def test_cli_failure_is_fixed_and_does_not_disclose_exception_details(self):
        messages = []
        for detail in ("case-private-token", "https://private.invalid/secret"):
            stdout, stderr = io.StringIO(), io.StringIO()
            with self.subTest(detail=detail), mock.patch.object(
                audit, "run_audit", side_effect=audit.AuditError(detail)
            ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(audit.main([]), 1)
            self.assertEqual(stdout.getvalue(), "")
            message = stderr.getvalue()
            self.assertTrue(message.strip())
            self.assertEqual(len(message.strip().splitlines()), 1)
            self.assertNotIn(detail, message)
            self.assertNotIn("Traceback", message)
            messages.append(message)
        self.assertEqual(messages[0], messages[1])


if __name__ == "__main__":
    unittest.main()
