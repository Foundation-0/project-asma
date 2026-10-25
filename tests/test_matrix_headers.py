"""Offline header-linkage contracts using abstract tokens only."""

import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_matrix_headers as audit


def record(label="label-alpha", patient="abstract-person", sample="abstract-specimen", **changes):
    result = {audit.clinical.LABEL_COLUMN: label, "Patient ID": patient, "Sample ID": sample,
              "Neo-adjuvant": "no", "Tumor response": "sensitive", "Tumor Location Group": "OV",
              "Sample type": "abstract-type"}
    result.update(changes)
    return result


def na_record(label="label-control"):
    return record(label, **{key: "NA" for key in audit.clinical.CRITICAL})


def response(body=b"Index\tlabel-alpha\tNA\nunused-matrix-values\n", **changes):
    stream = io.BytesIO(body)
    stream.status = 206
    stream.headers = {"Content-Range": "bytes 0-65535/100000"}
    for key, value in changes.items():
        setattr(stream, key, value)
    return stream


def study_fixture():
    return {sid: {"study_id": spec[0], "pdc_study_id": sid, "submitter_id_name": "abstract-study-" + sid,
                  "cases_count": 1, "aliquots_count": 1, "embargo_date": None, "versions": [{"number": "1"}]}
            for sid, spec in audit.FILES.items()}


def file_fixture(sid="PDC000360"):
    row = dict(zip(("study_id", "file_id", "file_name", "file_size", "md5sum"), audit.FILES[sid]))
    row.update(pdc_study_id=sid, data_category=audit.CATEGORY, access="Open", downloadable="Yes", embargo_date=None)
    return {"data": {"getPaginatedUIFile": {"total": 1, "uiFiles": [row],
                                           "pagination": {"count": 1, "total": 1, "pages": 1}}}}


class MatrixHeaderChecks(unittest.TestCase):
    def test_matches_do_not_confuse_clinical_na_with_patients(self):
        rows = [record(), record("label-replicate"), na_record(), na_record("NA")]
        original = copy.deepcopy(rows)
        summary = audit.summarize_labels(["Index", "label-alpha", "label-replicate", "label-control", "NA"], rows)
        self.assertEqual(summary["exact_label_matches"], 3)
        self.assertEqual(summary["matched_response_labelled_rows"], 2)
        self.assertEqual(summary["matched_clinical_NA_rows"], 1)
        self.assertEqual(summary["matched_unique_patient_keys"], 1)
        self.assertEqual(summary["matched_unique_sample_keys"], 1)
        self.assertEqual(summary["clinical_rows_without_linkable_label"], 1)
        self.assertEqual(summary["matrix_columns_without_exact_clinical_label"], 2)
        self.assertEqual(rows, original)
        self.assertNotIn("label-alpha", json.dumps(summary))

    def test_exact_join_never_normalizes_or_splits(self):
        headers = ["LABEL-ALPHA", "label-alpha ", "prefix_label-alpha", "label.alpha", "Index"]
        summary = audit.summarize_labels(headers, [record()])
        self.assertEqual(summary["exact_label_matches"], 0)
        self.assertEqual(summary["unmatched_linkable_clinical_labels"], 1)
        self.assertEqual(summary["unmatched_response_labelled_rows"], 1)
        self.assertFalse(summary["all_response_labelled_rows_mapped"])

    def test_duplicate_headers_and_clinical_labels_fail(self):
        with self.assertRaises(ValueError):
            audit.summarize_labels(["label-alpha", "label-alpha"], [record()])
        with self.assertRaises(ValueError):
            audit.summarize_labels(["label-alpha"], [record(), record()])
        with self.assertRaises(ValueError):
            audit.summarize_labels(["label-control"], [na_record(), na_record()])

    def test_missing_or_malformed_clinical_fields_fail(self):
        bad_rows = [record(label=""), record(label=" label-alpha"), record(label="NA"),
                    record(**{"Patient ID": "NA"}), record(**{"Tumor response": "NA"})]
        incomplete = record()
        del incomplete["Sample ID"]
        bad_rows.append(incomplete)
        for row in bad_rows:
            with self.subTest(row=row), self.assertRaises(ValueError):
                audit.summarize_labels(["Index"], [row])

    def test_conflicting_replicates_fail_even_when_unmatched(self):
        with self.assertRaises(ValueError):
            audit.summarize_labels(["Index"], [record(), record("second-label", **{"Tumor response": "refractory"})])

    def test_header_read_stops_before_matrix_values(self):
        stream = response()
        fields, provenance = audit.read_header(stream, 100000)
        self.assertEqual(fields, ["Index", "label-alpha", "NA"])
        self.assertEqual(stream.tell(), len(b"Index\tlabel-alpha\tNA\n"))
        self.assertEqual(provenance["header_bytes_read"], stream.tell())
        self.assertEqual(len(provenance["header_sha256"]), 64)

    def test_full_response_rejected_before_read(self):
        stream = response(status=200)
        with self.assertRaises(ValueError):
            audit.read_header(stream, 100000)
        self.assertEqual(stream.tell(), 0)

    def test_range_identity_and_transfer_encoding_required(self):
        for headers in ({}, {"Content-Range": "bytes 1-65535/100000"},
                        {"Content-Range": "bytes 0-65535/99999"},
                        {"Content-Range": "bytes 0-99999/100000"},
                        {"Content-Range": "bytes 0-65535/100000", "Content-Encoding": "gzip"}):
            stream = response(headers=headers)
            with self.subTest(headers=headers), self.assertRaises(ValueError):
                audit.read_header(stream, 100000)
            self.assertEqual(stream.tell(), 0)

    def test_incomplete_oversized_duplicate_or_malformed_headers_fail(self):
        bodies = (b"Index\tno-terminator", b"x" * (audit.MAX_HEADER_BYTES + 1) + b"\n",
                  b"Index\talpha\talpha\n", b'Index\t"unclosed\n', b"\xff\talpha\n")
        for body in bodies:
            stream = response(body)
            with self.subTest(length=len(body)), self.assertRaises((ValueError, UnicodeError, audit.csv.Error)):
                audit.read_header(stream, 100000)
            self.assertLessEqual(stream.tell(), audit.MAX_HEADER_BYTES + 1)

    def test_catalog_contract_rejects_changed_access_identity_and_counts(self):
        studies = study_fixture()
        baseline = file_fixture()
        result = audit.file_from_response(baseline, "PDC000360", studies["PDC000360"])
        self.assertEqual(result["file_name"], audit.FILES["PDC000360"][2])
        for field, value in (("access", "Controlled"), ("downloadable", "No"), ("embargo_date", "future"),
                             ("file_id", "changed"), ("md5sum", "changed"), ("file_size", "42")):
            changed = copy.deepcopy(baseline)
            changed["data"]["getPaginatedUIFile"]["uiFiles"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                audit.file_from_response(changed, "PDC000360", studies["PDC000360"])
        changed = copy.deepcopy(baseline)
        changed["data"]["getPaginatedUIFile"]["pagination"]["total"] = 2
        with self.assertRaises(ValueError):
            audit.file_from_response(changed, "PDC000360", studies["PDC000360"])

    def test_snapshot_requires_no_release_or_catalog_drift(self):
        studies = study_fixture()
        files = {sid: audit.file_from_response(file_fixture(sid), sid, studies[sid]) for sid in studies}
        audit.verify_snapshot(studies, files, copy.deepcopy(studies), copy.deepcopy(files))
        changed_studies = copy.deepcopy(studies)
        changed_studies["PDC000360"]["versions"] = [{"number": "2"}]
        with self.assertRaises(ValueError):
            audit.verify_snapshot(studies, files, changed_studies, files)
        changed_files = copy.deepcopy(files)
        changed_files["PDC000360"]["md5sum"] = "changed"
        with self.assertRaises(ValueError):
            audit.verify_snapshot(studies, files, studies, changed_files)

    def test_cli_failure_never_prints_remote_or_row_details(self):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(audit, "run_audit", side_effect=RuntimeError("private-key signed-url-secret")), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(audit.main([]), 1)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), audit.FAILURE_MESSAGE + "\n")


if __name__ == "__main__":
    unittest.main()
