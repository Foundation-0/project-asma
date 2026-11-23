"""Synthetic and frozen-snapshot checks for the TCGA-OV cohort readers."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import tcga_ov_cohort_export as export_reader
from tools import tcga_ov_cohort_recompute as recompute_reader

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/tcga-ov-cohort-reconciliation-20261113"
EMPTY_SHA = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class TcgaOvCohort(unittest.TestCase):
    def test_readers_do_not_import_each_other(self):
        export_source = (ROOT / "tools/tcga_ov_cohort_export.py").read_text(encoding="utf-8")
        recompute_source = (ROOT / "tools/tcga_ov_cohort_recompute.py").read_text(encoding="utf-8")
        self.assertNotIn("tcga_ov_cohort_recompute", export_source)
        self.assertNotIn("tcga_ov_cohort_export", recompute_source)

    def test_barcode_and_hash_agree(self):
        for reader in (export_reader, recompute_reader):
            self.assertEqual(reader.patient_barcode(" tcga-aa-a1b2-01a "), "TCGA-AA-A1B2")
            self.assertEqual(reader.patient_barcode("TCGA-AA-A1B2"), "TCGA-AA-A1B2")
            self.assertIsNone(reader.patient_barcode("not-a-barcode"))
            self.assertEqual(reader.set_sha256(set()), EMPTY_SHA)
            self.assertEqual(
                reader.set_sha256({"TCGA-AA-A1B2", "TCGA-BB-0001"}),
                reader.set_sha256({"TCGA-BB-0001", "TCGA-AA-A1B2"}),
            )

    def test_overlap_arithmetic_agrees(self):
        left = {"TCGA-AA-0001", "TCGA-AA-0002"}
        right = {"TCGA-AA-0002", "TCGA-AA-0003"}
        exported = export_reader.overlap(left, right)
        recomputed = recompute_reader.overlap(left, right)
        self.assertEqual(exported, recomputed)
        self.assertEqual(exported["count"], 1)
        self.assertEqual(exported["left_only"], 1)
        self.assertEqual(exported["right_only"], 1)
        self.assertEqual(exported["count"] + exported["left_only"], len(left))
        self.assertEqual(exported["count"] + exported["right_only"], len(right))

    def test_pinned_snapshot_readers_agree(self):
        exported = export_reader.derive(RESULT)
        recomputed = recompute_reader.derive(RESULT)
        self.assertEqual(export_reader.comparable(exported), recompute_reader.comparable(recomputed))
        self.assertEqual(exported["checker"], "export_fields")
        self.assertEqual(recomputed["checker"], "recompute_buckets")
        self.assertEqual(exported["gdc_project_case_count"], 608)
        self.assertEqual(exported["studies"]["ov_tcga_pub"]["all_sample_count"], 489)
        self.assertEqual(exported["studies"]["ov_tcga_pub"]["sequenced_sample_count"], 316)
        self.assertFalse(exported["identifiers_retained"])
        self.assertEqual(exported["clinical_guidance"], "none")
        self.assertEqual(exported["biological_conclusion"], "none")

    def test_recompute_rejects_a_headline_that_disagrees_with_the_case_total(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "result"
            shutil.copytree(RESULT, dest)
            project_path = dest / "snapshot/gdc-project-tcga-ov.json"
            project = json.loads(project_path.read_text(encoding="utf-8"))
            project["data"]["summary"]["case_count"] = 1
            project_path.write_text(json.dumps(project), encoding="utf-8")
            exported = export_reader.derive(dest)
            self.assertEqual(exported["gdc_project_case_count"], 1)
            self.assertEqual(exported["gdc_cases_pagination_total"], 608)
            with self.assertRaises(recompute_reader.CountError):
                recompute_reader.derive(dest)


if __name__ == "__main__":
    unittest.main()
