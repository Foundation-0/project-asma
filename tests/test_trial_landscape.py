"""Offline audit contracts using invented registry records, never live trials."""

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_trial_landscape as audit


VERSION = {"apiVersion": "fixture-version", "dataTimestamp": "2026-01-01T00:00:00"}
UNSET = object()


def study(number=1, *, title="Invented test study", eligibility="", phases=UNSET):
    """Invented, structurally valid records; identifiers are arbitrary test tokens."""
    design = {"studyType": "INTERVENTIONAL"}
    if phases is not UNSET:
        design["phases"] = phases
    return {"protocolSection": {
        "identificationModule": {"nctId": f"NCT99{number:06d}", "briefTitle": title},
        "statusModule": {"overallStatus": "RECRUITING"},
        "designModule": design,
        "eligibilityModule": {"eligibilityCriteria": eligibility},
    }}


def page(studies, total, token=UNSET):
    result = {"studies": studies, "totalCount": total}
    if token is not UNSET:
        result["nextPageToken"] = token
    return result


class Transport:
    """Finite response queue that fails on an unplanned request, without network."""

    def __init__(self, pages, *, before=None, after=None):
        self.responses = [copy.deepcopy(VERSION if before is None else before)]
        self.responses += copy.deepcopy(pages)
        self.responses += [copy.deepcopy(VERSION if after is None else after)]
        self.calls = []

    def __call__(self, url, max_bytes):
        self.calls.append((url, max_bytes))
        if not self.responses:
            raise AssertionError("Unexpected extra mock transport request")
        payload = self.responses.pop(0)
        encoded = json.dumps(payload, sort_keys=True).encode()
        return payload, hashlib.sha256(encoded).hexdigest()


class TrialLanguageChecks(unittest.TestCase):
    def test_unicode_nfkc_case_alpha_whitespace_and_dash_normalization(self):
        self.assertEqual(audit.normalize_text("  ＢＲＣＡ１\u00a0FRΑ\tα  "), "brca1 fralpha alpha")
        for dash in ("-", "\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015"):
            with self.subTest(dash=dash):
                found = audit.classify_study(study(title=f"PLATINUM{dash}RESISTANT; folate receptor{dash}α"))
                self.assertEqual(found["buckets"], {"platinum_resistant", "folate_receptor_alpha"})

    def test_unicode_whole_words_and_no_stemming(self):
        found = audit.classify_study(study(title="xbrca1 brca12 brca1x prébrca hrdé biomarkerish nonbiomarkers"))
        self.assertEqual(found["buckets"], set())
        found = audit.classify_study(study(title="(BRCA1/2), biomarkers; HRD."))
        self.assertEqual(found["buckets"], {"brca", "biomarker_generic", "hrd"})

    def test_negations_exclusions_and_background_still_count_mentions(self):
        found = audit.classify_study(study(
            title="No biomarker required; background: BRCA1",
            eligibility="Exclude platinum-resistant disease; HRD not required.",
        ))
        self.assertEqual(found["buckets"], {"biomarker_generic", "brca", "hrd", "platinum_resistant"})
        self.assertEqual(found["eligibility_buckets"], {"hrd", "platinum_resistant"})
        self.assertEqual(found["other_buckets"], {"biomarker_generic", "brca"})

    def test_phrase_cannot_cross_fields_or_list_items(self):
        row = study(title="platinum", eligibility="resistant")
        row["protocolSection"]["conditionsModule"] = {
            "conditions": ["homologous recombination", "deficient"],
            "keywords": ["folate receptor", "alpha"],
        }
        self.assertEqual(audit.classify_study(row)["buckets"], set())
        # The frozen literal rules do not infer a repeated shared head word.
        found = audit.classify_study(study(title="platinum resistant/refractory"))
        self.assertEqual(found["buckets"], {"platinum_resistant"})
        found = audit.classify_study(study(title="platinum refractory"))
        self.assertEqual(found["buckets"], {"platinum_refractory"})

    def test_each_projected_text_field_can_supply_a_mention(self):
        for path in audit.load_spec()["text_fields"].values():
            with self.subTest(path=path):
                row = study()
                module, field = path.split(".")
                value = ["BRCA1"] if field in ("conditions", "keywords") else "BRCA1"
                row["protocolSection"].setdefault(module, {})[field] = value
                self.assertEqual(audit.classify_study(row)["buckets"], {"brca"})

    def test_once_per_bucket_and_group_union_with_overlap(self):
        found = audit.classify_study(study(
            title="BRCA BRCA1 BRCA2 biomarkers HRD platinum resistant platinum refractory",
            eligibility="BRCA1 and BRCA1; platinum resistance and platinum refractoriness",
        ))
        self.assertEqual(found["buckets"], {
            "brca", "biomarker_generic", "hrd", "platinum_resistant", "platinum_refractory",
        })
        self.assertEqual(found["groups"], {"any_biomarker_bucket", "any_platinum_bucket"})
        self.assertEqual(found["eligibility_buckets"] & found["other_buckets"], {
            "brca", "platinum_resistant", "platinum_refractory",
        })

    def test_optional_missing_null_empty_and_whitespace_text_is_accepted(self):
        for value in (UNSET, None, "", " \t\n "):
            with self.subTest(value=value):
                row = study()
                ident = row["protocolSection"]["identificationModule"]
                if value is not UNSET:
                    ident["officialTitle"] = value
                found = audit.classify_study(row)
                self.assertIn("official_title", found["missing_text_fields"])
                self.assertEqual(found["buckets"], set())
        for module in ("descriptionModule", "conditionsModule", "eligibilityModule"):
            for value in (UNSET, None, {}):
                row = study()
                if value is UNSET:
                    row["protocolSection"].pop(module, None)
                else:
                    row["protocolSection"][module] = value
                with self.subTest(module=module, value=value):
                    self.assertEqual(audit.classify_study(row)["buckets"], set())

    def test_optional_arrays_absent_null_empty_or_blank_items_are_accepted(self):
        for value in (UNSET, None, [], ["", "  "]):
            with self.subTest(value=value):
                row = study()
                module = row["protocolSection"].setdefault("conditionsModule", {})
                if value is not UNSET:
                    module["keywords"] = value
                found = audit.classify_study(row)
                self.assertIn("keywords", found["missing_text_fields"])
                self.assertEqual(found["buckets"], set())

    def test_wrong_optional_text_types_are_rejected(self):
        for value in (False, 0, [], {}, ["BRCA1"]):
            with self.subTest(value=value):
                row = study()
                row["protocolSection"]["identificationModule"]["officialTitle"] = value
                with self.assertRaises(audit.AuditError):
                    audit.classify_study(row)

    def test_wrong_optional_array_types_and_items_are_rejected(self):
        for value in ("BRCA1", {}, False, 0, [None], [1], [False], [{}]):
            with self.subTest(value=value):
                row = study()
                row["protocolSection"]["conditionsModule"] = {"conditions": value}
                with self.assertRaises(audit.AuditError):
                    audit.classify_study(row)

    def test_malformed_study_or_module_structure_is_rejected(self):
        for row in (None, [], {}, {"protocolSection": []}, {"protocolSection": None}):
            with self.subTest(row=row), self.assertRaises(audit.AuditError):
                audit.classify_study(row)
        for value in ([], "BRCA1", 1):
            row = study()
            row["protocolSection"]["descriptionModule"] = value
            with self.subTest(module=value), self.assertRaises(audit.AuditError):
                audit.classify_study(row)

    def test_combined_phase_uses_canonical_order(self):
        self.assertEqual(audit.canonical_phase(["PHASE2", "PHASE1"]), "PHASE1+PHASE2")
        self.assertEqual(audit.classify_study(study(phases=["PHASE2", "PHASE1"]))["phase"], "PHASE1+PHASE2")

    def test_na_and_missing_phase_remain_distinct(self):
        self.assertEqual(audit.canonical_phase(["NA"]), "NA")
        for phases in (None, []):
            with self.subTest(phases=phases):
                self.assertEqual(audit.canonical_phase(phases), "NOT_REPORTED")
        self.assertEqual(audit.classify_study(study())["phase"], "NOT_REPORTED")

    def test_unknown_duplicate_mixed_na_and_malformed_phases_fail(self):
        for phases in (["PHASE0"], ["PHASE1", "PHASE1"], ["NA", "NA"],
                       ["NA", "PHASE2"], ["phase1"], [None], [1], "PHASE1", {}, False):
            with self.subTest(phases=phases), self.assertRaises(audit.AuditError):
                audit.canonical_phase(phases)

    def test_nonrecruiting_or_noninterventional_records_fail(self):
        for module, field, values in (
            ("statusModule", "overallStatus", ["COMPLETED", "NOT_YET_RECRUITING", "recruiting", None]),
            ("designModule", "studyType", ["OBSERVATIONAL", "interventional", None]),
        ):
            for value in values:
                row = study()
                row["protocolSection"][module][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(audit.AuditError):
                    audit.classify_study(row)

    def test_malformed_or_missing_registry_identity_fails(self):
        for value in (UNSET, None, "", "NCT123", "NCT123456789", "nct99000001", 99000001):
            row = study()
            ident = row["protocolSection"]["identificationModule"]
            if value is UNSET:
                del ident["nctId"]
            else:
                ident["nctId"] = value
            with self.subTest(value=value), self.assertRaises(audit.AuditError):
                audit.classify_study(row)


class TrialPaginationChecks(unittest.TestCase):
    def test_paginated_requests_pin_query_fields_and_record_exact_tokens(self):
        transport = Transport([page([study(1)], 2, "invented+/token="), page([study(2)], 2)])
        snapshot = audit.fetch_audit(fetch_json=transport)
        self.assertEqual(transport.responses, [])
        spec = audit.load_spec()
        self.assertEqual(transport.calls[0][0], spec["version_endpoint"])
        self.assertEqual(transport.calls[-1][0], spec["version_endpoint"])
        for url, limit in transport.calls:
            self.assertEqual(limit, spec["limits"]["max_response_bytes"])
        for index, (url, _) in enumerate(transport.calls[1:-1]):
            parsed = urlsplit(url)
            self.assertEqual(f"{parsed.scheme}://{parsed.netloc}{parsed.path}", spec["endpoint"])
            query = parse_qs(parsed.query)
            for key, value in {**spec["query"], **spec["request_options"]}.items():
                self.assertEqual(query[key], [value])
            self.assertEqual(query["fields"][0].split(","), spec["fields"])
            if index:
                self.assertEqual(query["pageToken"], ["invented+/token="])
            else:
                self.assertNotIn("pageToken", query)
        audit.check_snapshot(snapshot)

    def test_zero_result_terminal_page_succeeds(self):
        audit.check_snapshot(audit.fetch_audit(fetch_json=Transport([page([], 0)])))

    def test_repeated_page_token_is_rejected(self):
        transport = Transport([page([study(1)], 3, "same"), page([study(2)], 3, "same")])
        with self.assertRaises(audit.AuditError):
            audit.fetch_audit(fetch_json=transport)
        self.assertLessEqual(len(transport.calls), 3)

    def test_duplicate_study_within_or_across_pages_is_rejected(self):
        alternatives = ([page([study(1), study(1)], 2)],
                        [page([study(1)], 2, "next"), page([study(1)], 2)])
        for pages in alternatives:
            with self.subTest(pages=len(pages)), self.assertRaises(audit.AuditError):
                audit.fetch_audit(fetch_json=Transport(pages))

    def test_unstable_total_count_is_rejected(self):
        with self.assertRaises(audit.AuditError):
            audit.fetch_audit(fetch_json=Transport([page([study(1)], 2, "next"), page([study(2)], 3)]))

    def test_terminal_truncation_and_count_overrun_are_rejected(self):
        for total in (0, 2):
            with self.subTest(total=total), self.assertRaises(audit.AuditError):
                audit.fetch_audit(fetch_json=Transport([page([study()], total)]))

    def test_empty_intermediate_page_continues_until_terminal_page(self):
        for pages in ([page([], 1, "next"), page([study()], 1)],
                      [page([study()], 1, "next"), page([], 1)]):
            with self.subTest(pages=pages):
                transport = Transport(pages)
                snapshot = audit.fetch_audit(fetch_json=transport)
                self.assertEqual(snapshot["counts"]["total_studies"], 1)
                self.assertEqual(transport.responses, [])

    def test_subsequent_page_may_omit_total_count(self):
        second = {"studies": [study(2)]}
        snapshot = audit.fetch_audit(fetch_json=Transport([page([study(1)], 2, "next"), second]))
        self.assertEqual(snapshot["counts"]["total_studies"], 2)
        audit.check_snapshot(snapshot)

    def test_page_limit_without_terminal_page_is_rejected(self):
        spec = copy.deepcopy(audit.load_spec())
        spec["limits"]["max_pages"] = 2
        transport = Transport([page([study(1)], 3, "one"), page([study(2)], 3, "two")])
        with mock.patch.object(audit, "load_spec", return_value=spec), self.assertRaises(audit.AuditError):
            audit.fetch_audit(fetch_json=transport)
        self.assertLessEqual(len(transport.calls), 3)

    def test_missing_boolean_negative_and_noninteger_counts_fail(self):
        for total in (UNSET, None, True, -1, 1.0, "1"):
            response = page([study()], total)
            if total is UNSET:
                del response["totalCount"]
            with self.subTest(total=total), self.assertRaises(audit.AuditError):
                audit.fetch_audit(fetch_json=Transport([response]))

    def test_missing_or_malformed_studies_and_tokens_fail(self):
        for response in ({"totalCount": 0}, {"totalCount": 0, "studies": None},
                         {"totalCount": 0, "studies": {}}, page([study()], 1, 42),
                         page([study()], 1, [])):
            with self.subTest(response=response), self.assertRaises(audit.AuditError):
                audit.fetch_audit(fetch_json=Transport([response]))
        for token in ("", " ", "\t\n"):
            transport = Transport([page([], 1, token), page([study()], 1)])
            with self.subTest(blank_token=repr(token)), self.assertRaises(audit.AuditError):
                audit.fetch_audit(fetch_json=transport)
            self.assertEqual(len(transport.calls), 2)

    def test_api_version_or_data_timestamp_drift_fails(self):
        for field in VERSION:
            changed = "different-fixture-version" if field == "apiVersion" else "2026-01-02T00:00:00"
            after = {**VERSION, field: changed}
            with self.subTest(field=field), self.assertRaises(audit.AuditError):
                audit.fetch_audit(fetch_json=Transport([page([study()], 1)], after=after))

    def test_missing_or_malformed_version_metadata_fails(self):
        for field in VERSION:
            for value in (UNSET, None, "", 1, []):
                version = dict(VERSION)
                if value is UNSET:
                    del version[field]
                else:
                    version[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(audit.AuditError):
                    audit.fetch_audit(fetch_json=Transport([page([study()], 1)], before=version))
        for timestamp in ("2026-01-01", "2026-02-30T00:00:00", "2026-01-01T00:00:00Z"):
            version = {**VERSION, "dataTimestamp": timestamp}
            with self.subTest(timestamp=timestamp), self.assertRaises(audit.AuditError):
                audit.fetch_audit(fetch_json=Transport([page([study()], 1)], before=version))


class TrialAggregateChecks(unittest.TestCase):
    def setUp(self):
        self.rows = [
            study(1, title="BRCA1 BRCA1 HRD", eligibility="platinum resistant", phases=["PHASE2", "PHASE1"]),
            study(2, title="biomarkers BRCA2", phases=["NA"]),
            study(3, title="platinum resistance platinum refractory", phases=["PHASE2"]),
            study(4, title="No matching phrases"),
        ]

    def test_aggregate_counts_once_per_study_and_preserves_combined_phases(self):
        counts = audit.aggregate_studies(self.rows)
        self.assertEqual(counts["total_studies"], 4)
        self.assertEqual(counts["phase_counts"], {"PHASE1+PHASE2": 1, "NA": 1, "PHASE2": 1, "NOT_REPORTED": 1})
        self.assertEqual(sum(counts["phase_counts"].values()), 4)
        self.assertEqual(counts["bucket_counts"], {
            "biomarker_generic": 1, "brca": 2, "hrd": 1,
            "folate_receptor_alpha": 0, "platinum_resistant": 2, "platinum_refractory": 1,
        })
        self.assertEqual(counts["group_counts"], {"any_biomarker_bucket": 2, "any_platinum_bucket": 2})
        self.assertEqual(counts["biomarker_platinum_overlap"], {
            "both": 1, "biomarker_only": 1, "platinum_only": 1, "neither": 1,
        })
        self.assertEqual((counts["any_keyword"], counts["no_keyword"]), (3, 1))

    def test_aggregate_field_source_counts_and_missingness(self):
        counts = audit.aggregate_studies(self.rows)
        self.assertEqual(counts["eligibility_bucket_counts"]["platinum_resistant"], 1)
        self.assertEqual(counts["other_text_bucket_counts"]["platinum_resistant"], 1)
        self.assertEqual(counts["other_text_bucket_counts"]["brca"], 2)
        self.assertEqual(counts["missing_text_fields"], {
            "brief_title": 0, "official_title": 4, "brief_summary": 4,
            "conditions": 4, "keywords": 4, "eligibility": 3,
        })

    def test_snapshot_and_report_contain_no_study_identifiers_or_narratives(self):
        snapshot = audit.fetch_audit(fetch_json=Transport([page(self.rows, 4)]))
        text = json.dumps(snapshot) + audit.render_report_table(snapshot)
        for row in self.rows:
            ident = row["protocolSection"]["identificationModule"]
            self.assertNotIn(ident["nctId"], text)
            self.assertNotIn(ident["briefTitle"], text)
        self.assertNotIn("protocolSection", text)
        self.assertNotIn("eligibilityCriteria", text)

    def test_aggregate_and_classification_do_not_mutate_inputs(self):
        before = copy.deepcopy(self.rows)
        for row in self.rows:
            audit.classify_study(row)
        audit.aggregate_studies(self.rows)
        self.assertEqual(self.rows, before)

    def test_snapshot_rejects_impossible_counts_and_partition_mismatches(self):
        snapshot = audit.fetch_audit(fetch_json=Transport([page(self.rows, 4)]))
        changes = [
            (("total_studies",), 5),
            (("phase_counts", "PHASE1+PHASE2"), 2),
            (("bucket_counts", "brca"), 5),
            (("bucket_counts", "brca"), True),
            (("bucket_counts", "hrd"), -1),
            (("group_counts", "any_biomarker_bucket"), 1),
            (("biomarker_platinum_overlap", "both"), 2),
            (("any_keyword",), 2),
            (("no_keyword",), 2),
            (("missing_text_fields", "official_title"), 5),
            (("eligibility_bucket_counts", "hrd"), 2),
        ]
        for path, value in changes:
            changed = copy.deepcopy(snapshot)
            container = changed["counts"]
            for key in path[:-1]:
                container = container[key]
            container[path[-1]] = value
            # Re-sign the fixture so this checks numeric invariants, not only
            # the payload checksum's ability to detect an edit.
            changed["aggregate_payload_sha256"] = audit._payload_hash(changed)
            with self.subTest(path=path, value=value), self.assertRaises(audit.AuditError):
                audit.check_snapshot(changed)

    def test_snapshot_rejects_unexpected_row_level_payload(self):
        snapshot = audit.fetch_audit(fetch_json=Transport([page(self.rows, 4)]))
        snapshot["studies"] = self.rows
        snapshot["aggregate_payload_sha256"] = audit._payload_hash(snapshot)
        with self.assertRaises(audit.AuditError):
            audit.check_snapshot(snapshot)


class TrialCliChecks(unittest.TestCase):
    def test_help_succeeds_offline(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools/audit_trial_landscape.py"), "--help"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("usage:", completed.stdout.lower())
        self.assertEqual(completed.stderr, "")

    def test_cli_failure_does_not_disclose_exception_details_or_traceback(self):
        detail = "NCT99000001 invented-private-narrative https://fixture.invalid/secret"
        for exception in (audit.AuditError(detail), RuntimeError(detail)):
            stdout, stderr = io.StringIO(), io.StringIO()
            with self.subTest(exception=type(exception).__name__), mock.patch.object(
                audit, "fetch_audit", side_effect=exception
            ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(audit.main([]), 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertTrue(stderr.getvalue().strip())
            self.assertEqual(len(stderr.getvalue().strip().splitlines()), 1)
            for value in (detail, "NCT99000001", "invented-private-narrative", "Traceback"):
                self.assertNotIn(value, stderr.getvalue())

    def test_cli_failed_fetch_emits_no_partial_rows_or_files(self):
        for existing in (False, True):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "aggregate.json"
                if existing:
                    output.write_text("previous-complete-aggregate\n", encoding="utf-8")
                transport = Transport([
                    page([study(1, title="invented secret narrative BRCA1")], 2, "next"),
                    page([study(1)], 2),
                ])
                stdout, stderr = io.StringIO(), io.StringIO()
                with mock.patch.object(audit, "fetch_json", side_effect=transport), \
                        contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    self.assertEqual(audit.main(["--output", str(output)]), 1)
                self.assertEqual(stdout.getvalue(), "")
                self.assertNotIn("NCT99000001", stderr.getvalue())
                self.assertNotIn("invented secret narrative", stderr.getvalue())
                if existing:
                    self.assertEqual(output.read_text(), "previous-complete-aggregate\n")
                else:
                    self.assertFalse(output.exists())
                self.assertEqual(list(Path(directory).iterdir()), [output] if existing else [])

    def test_cli_success_writes_only_complete_aggregate_and_offline_check(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "aggregate.json"
            stdout, stderr = io.StringIO(), io.StringIO()
            with mock.patch.object(audit, "fetch_json", side_effect=Transport([page([study()], 1)])), \
                    contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(audit.main(["--output", str(output)]), 0)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")
            content = output.read_text(encoding="utf-8")
            self.assertNotIn("NCT99000001", content)
            self.assertNotIn("Invented test study", content)
            snapshot = json.loads(content)
            self.assertEqual(snapshot["counts"]["total_studies"], 1)
            audit.check_snapshot(snapshot)
            with mock.patch.object(audit, "fetch_audit", side_effect=AssertionError("Offline check attempted network")), \
                    contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(audit.main(["--check-snapshot", str(output)]), 0)
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(list(Path(directory).iterdir()), [output])

    def test_atomic_output_failure_cleans_temporary_file_and_preserves_previous(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "aggregate.json"
            output.write_text("previous-complete-aggregate\n", encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with mock.patch.object(audit, "fetch_json", side_effect=Transport([page([study()], 1)])), \
                    mock.patch.object(audit.os, "replace", side_effect=OSError("invented-secret-error")), \
                    contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(audit.main(["--output", str(output)]), 1)
            self.assertEqual(output.read_text(), "previous-complete-aggregate\n")
            self.assertEqual(list(Path(directory).iterdir()), [output])
            self.assertEqual(stdout.getvalue(), "")
            self.assertNotIn("invented-secret-error", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
