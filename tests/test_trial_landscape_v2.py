"""Synthetic checks for the v2 trial-landscape readers. No network and no patients."""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import trial_landscape_v2_export as export_reader
from tools import trial_landscape_v2_recompute as recompute_reader

SPEC = export_reader.load_spec()
RESULT = ROOT / "results/trial-landscape-v2-2026-11-13"
EMAIL_ADDRESS = re.compile(
    r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
    r"(?![A-Za-z0-9.-])"
)


def study(nct, title="", summary="", official="", status="RECRUITING", phases=None,
          conditions=None, keywords=None, interventions=None, omit_phases=False):
    design = {"studyType": "INTERVENTIONAL"}
    if not omit_phases:
        design["phases"] = ["PHASE2"] if phases is None else phases
    if interventions is None:
        interventions = [{"type": "DRUG", "name": "placebo"}]
    return {"protocolSection": {
        "identificationModule": {
            "nctId": nct, "briefTitle": title, "officialTitle": official,
        },
        "statusModule": {"overallStatus": status},
        "designModule": design,
        "descriptionModule": {"briefSummary": summary},
        "conditionsModule": {
            "conditions": [] if conditions is None else conditions,
            "keywords": [] if keywords is None else keywords,
        },
        "armsInterventionsModule": {"interventions": interventions},
    }}


def both(records):
    left = export_reader.aggregate_records(records, SPEC)
    right = recompute_reader.tally(records, SPEC)
    return left, right


class TrialLandscapeV2(unittest.TestCase):
    def test_readers_do_not_import_each_other(self):
        export_source = (ROOT / "tools/trial_landscape_v2_export.py").read_text(encoding="utf-8")
        recompute_source = (ROOT / "tools/trial_landscape_v2_recompute.py").read_text(encoding="utf-8")
        self.assertNotIn("trial_landscape_v2_recompute", export_source)
        self.assertNotIn("trial_landscape_v2_export", recompute_source)

    def test_normalization_and_boundaries_agree(self):
        rows = [
            study("NCT00000001", title="FRα-positive; PD-1"),
            study("NCT00000002", title="comparative olaparibx cohort"),
            study("NCT00000003", title="olaparib maintenance"),
            study("NCT00000004", title="CDR2L only"),
            study("NCT00000005", title="CDR2 peptide"),
            study("NCT00000006", summary="not a PARP inhibitor"),
        ]
        left, right = both([
            export_reader.record_from_study(item, SPEC) for item in rows
        ])
        # The recompute reader consumes its own records; rebuild to avoid shared objects.
        right = recompute_reader.tally(
            [recompute_reader.study_to_record(item, SPEC) for item in rows], SPEC
        )
        left = export_reader.aggregate_records(
            [export_reader.record_from_study(item, SPEC) for item in rows], SPEC
        )
        self.assertEqual(left["class_counts"], right["class_counts"])
        self.assertEqual(left["class_counts"]["folr1_language"], 1)
        self.assertEqual(left["class_counts"]["immunotherapy"], 1)
        self.assertEqual(left["class_counts"]["parp_inhibitor"], 2)
        self.assertEqual(left["class_counts"]["cdr2_cdr2l"], 2)
        self.assertEqual(left["class_counts"]["fralpha_adc"], 0)

    def test_adc_name_or_conjunction(self):
        rows = [
            study("NCT00000011", title="mirvetuximab soravtansine"),
            study("NCT00000012", title="folate receptor alpha antibody-drug conjugate"),
            study("NCT00000013", title="folate receptor alpha imaging"),
            study("NCT00000014", title="ADC manufacturing process"),
        ]
        left = export_reader.aggregate_records(
            [export_reader.record_from_study(item, SPEC) for item in rows], SPEC
        )
        right = recompute_reader.tally(
            [recompute_reader.study_to_record(item, SPEC) for item in rows], SPEC
        )
        self.assertEqual(left["class_counts"], right["class_counts"])
        self.assertEqual(left["class_counts"]["fralpha_adc"], 2)
        self.assertEqual(left["class_counts"]["folr1_language"], 2)

    def test_phase_intervention_and_partition(self):
        rows = [
            study("NCT00000021", phases=["PHASE1", "PHASE2"],
                  interventions=[{"type": "DRUG", "name": "a"}, {"type": "BIOLOGICAL", "name": "b"}]),
            study("NCT00000022", omit_phases=True, interventions=[]),
            study("NCT00000023", phases=["NA"], status="COMPLETED",
                  interventions=[{"type": "DRUG", "name": "a"}]),
        ]
        left = export_reader.aggregate_records(
            [export_reader.record_from_study(item, SPEC) for item in rows], SPEC
        )
        right = recompute_reader.tally(
            [recompute_reader.study_to_record(item, SPEC) for item in rows], SPEC
        )
        self.assertEqual(left, right)
        self.assertEqual(left["phase_counts"]["PHASE1+PHASE2"], 1)
        self.assertEqual(left["phase_counts"]["NOT_REPORTED"], 1)
        self.assertEqual(left["phase_counts"]["NA"], 1)
        self.assertEqual(left["intervention_type_counts"]["DRUG"], 2)
        self.assertEqual(left["intervention_type_counts"]["BIOLOGICAL"], 1)
        self.assertEqual(left["intervention_type_counts"]["NOT_REPORTED"], 1)
        self.assertEqual(left["studies_without_intervention"], 1)
        self.assertEqual(sum(left["status_counts"].values()), 3)
        self.assertEqual(left["any_target_class"] + left["no_target_class"], 3)

    def test_rejects_bad_phase_and_duplicate(self):
        bad = study("NCT00000031", phases=["PHASE2", "NA"])
        with self.assertRaises(export_reader.CountError):
            export_reader.record_from_study(bad, SPEC)
        with self.assertRaises(recompute_reader.RecountError):
            recompute_reader.study_to_record(bad, SPEC)
        one = export_reader.record_from_study(study("NCT00000032"), SPEC)
        with self.assertRaises(export_reader.CountError):
            export_reader.aggregate_records([one, one], SPEC)

    def test_prior_without_identifiers_is_not_a_named_diff(self):
        prior = json.dumps({"counts": {"total_studies": 592}})
        rows = [{"nct_id": "NCT00000041", "overall_status": "RECRUITING"}]
        self.assertEqual(
            export_reader.diff_against_prior(prior, rows),
            recompute_reader.diff_against_prior(prior, rows),
        )
        diff = export_reader.diff_against_prior(prior, rows)
        self.assertEqual(diff["nct_level_diff"], "not_reconstructable")
        self.assertIsNone(diff["new_nct_ids"])
        self.assertIsNone(diff["removed_nct_ids"])
        self.assertIsNone(diff["status_changes"])

    def test_prior_identifier_list_names_overlap_only(self):
        prior = "retained NCT00000051 and NCT00000052"
        rows = [
            {"nct_id": "NCT00000052", "overall_status": "COMPLETED"},
            {"nct_id": "NCT00000053", "overall_status": "RECRUITING"},
        ]
        diff = export_reader.diff_against_prior(prior, rows)
        self.assertEqual(diff, recompute_reader.diff_against_prior(prior, rows))
        self.assertEqual(diff["new_nct_ids"], ["NCT00000053"])
        self.assertEqual(diff["removed_nct_ids"], ["NCT00000051"])
        self.assertIsNone(diff["status_changes"])

    def test_ca125_is_not_a_target_class(self):
        row = study("NCT00000061", summary="CA-125 will be measured")
        left = export_reader.aggregate_records(
            [export_reader.record_from_study(row, SPEC)], SPEC
        )
        self.assertEqual(left["class_counts"]["ca125_language"], 1)
        self.assertEqual(left["class_counts"]["muc16"], 0)
        self.assertEqual(left["any_target_class"], 0)
        self.assertEqual(left["no_target_class"], 1)

    def test_real_prior_certificate_has_no_nct_identifiers(self):
        text = (ROOT / "results/trial-landscape-2026-11-05/certificate.json").read_text(encoding="utf-8")
        diff = export_reader.diff_against_prior(text, [])
        self.assertEqual(diff["nct_level_diff"], "not_reconstructable")
        self.assertIsNone(diff["status_changes"])

    def test_frozen_pages_have_no_contact_emails(self):
        for path in sorted((RESULT / "snapshot").glob("studies-page-*.json")):
            text = path.read_text(encoding="utf-8")
            match = EMAIL_ADDRESS.search(text)
            self.assertIsNone(match, f"mailbox address remains in {path.name}: {match}")


if __name__ == "__main__":
    unittest.main()
