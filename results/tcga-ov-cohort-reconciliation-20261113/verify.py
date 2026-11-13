#!/usr/bin/env python3
"""Offline agreement check for the TCGA-OV cohort reconciliation.

Replays two readers on frozen aggregate responses. Catalog counts are not a
biological conclusion and not clinical guidance.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from tools import tcga_ov_cohort_export as export_reader
from tools import tcga_ov_cohort_recompute as recompute_reader

DOC = ROOT / "docs/tcga-ov-cohort-reconciliation-20261113.md"
CERTIFICATE = RESULT / "certificate.json"
SUMS = RESULT / "SHA256SUMS"
BEGIN = "<!-- BEGIN GENERATED TCGA OV COHORT COUNTS -->"
END = "<!-- END GENERATED TCGA OV COHORT COUNTS -->"
PINNED_CODE = (
    "tools/fetch_tcga_ov_cohort.py",
    "tools/tcga_ov_cohort_export.py",
    "tools/tcga_ov_cohort_recompute.py",
    "results/tcga-ov-cohort-reconciliation-20261113/verify.py",
)
EMAIL_ADDRESS = re.compile(
    r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
    r"(?![A-Za-z0-9.-])"
)
BARCODE = re.compile(r"TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}")
FORBIDDEN_KEYS = {
    "patientId", "patientIds", "sampleId", "sampleIds", "submitter_id",
    "case_id", "aliquot_id", "uniquePatientKey", "uniqueSampleKey",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def render(result):
    published = result["studies"]["ov_tcga_pub"]
    firehose = result["studies"]["ov_tcga"]
    pancan = result["studies"]["ov_tcga_pan_can_atlas_2018"]
    lines = [
        f"retrieved_started_utc: {result['retrieved_started_utc']}",
        f"retrieved_completed_utc: {result['retrieved_completed_utc']}",
        f"gdc_data_release: {result['gdc_data_release']}",
        f"gdc_tag: {result['gdc_tag']}",
        f"gdc_api_version: {result['gdc_api_version']}",
        f"cbioportal_portal_version: {result['cbioportal_portal_version']}",
        f"cbioportal_db_version: {result['cbioportal_db_version']}",
        f"gdc_project_case_count: {result['gdc_project_case_count']}",
        f"gdc_case_set_count: {result['gdc_case_set_count']}",
        f"gdc_case_set_sha256: {result['gdc_case_set_sha256']}",
        f"gdc_primary_tumor_cases: {result['gdc_primary_tumor_cases']['count']}",
        f"gdc_tumor_tissue_cases: {result['gdc_tumor_tissue_cases']['count']}",
        f"gdc_cases_without_tumor_tissue: {result['gdc_cases_without_tumor_tissue']['count']}",
        f"gdc_project_file_count: {result['gdc_project_file_count']}",
        f"gdc_open_file_count: {result['gdc_open_file_count']}",
        f"gdc_controlled_file_count: {result['gdc_controlled_file_count']}",
        f"project_strategy_file_count_sum: {result['project_strategy_file_count_sum']}",
        f"project_strategy_file_count_gap: {result['project_strategy_file_count_gap']}",
        f"open_snv_cases: {result['open_file_cases']['open_snv']['count']}",
        f"open_cna_cases: {result['open_file_cases']['open_cna']['count']}",
        f"open_snv_and_cna_cases: {result['open_file_cases']['open_snv_and_cna']['count']}",
        f"gdc_cases_without_open_snv: {result['open_file_cases']['gdc_cases_without_open_snv']['count']}",
        f"open_wxs_cases: {result['open_file_cases']['open_wxs']['count']}",
        f"open_file_cases_any: {result['open_file_cases']['any']['count']}",
        f"open_file_cases_outside_gdc: {result['open_file_cases']['outside_gdc_case_set']}",
        f"ov_tcga_pub_all_samples: {published['all_sample_count']}",
        f"ov_tcga_pub_sequenced_samples: {published['sequenced_sample_count']}",
        f"ov_tcga_pub_cna_samples: {published['cna_sample_count']}",
        f"ov_tcga_pub_complete_samples: {published['complete_sample_count']}",
        f"ov_tcga_pub_patients: {published['patient_count']}",
        f"ov_tcga_pub_patients_with_a_sample: {published['patients_with_a_sample']['count']}",
        f"ov_tcga_pub_patients_without_a_sample: {published['patients_without_a_sample']['count']}",
        f"ov_tcga_pub_patient_sha256: {published['patient_sha256']}",
        f"ov_tcga_pub_overlap_gdc: {published['overlap_patients_with_gdc_cases']['count']}",
        f"ov_tcga_pub_gdc_only: {published['overlap_patients_with_gdc_cases']['gdc_only']}",
        f"ov_tcga_pub_portal_only: {published['overlap_patients_with_gdc_cases']['portal_only']}",
        f"ov_tcga_pub_overlap_sha256: {published['overlap_patients_with_gdc_cases']['sha256']}",
        f"ov_tcga_pub_exome_phrase_count: {published['exome_phrase_count']}",
        f"ov_tcga_pub_exome_phrase_conflicts: {published['exome_phrase_conflicts_with_sequenced_count']}",
        f"ov_tcga_all_samples: {firehose['all_sample_count']}",
        f"ov_tcga_patients: {firehose['patient_count']}",
        f"ov_tcga_overlap_gdc: {firehose['overlap_patients_with_gdc_cases']['count']}",
        f"ov_tcga_gdc_only: {firehose['overlap_patients_with_gdc_cases']['gdc_only']}",
        f"ov_tcga_portal_only: {firehose['overlap_patients_with_gdc_cases']['portal_only']}",
        f"ov_tcga_pan_can_atlas_2018_all_samples: {pancan['all_sample_count']}",
        f"ov_tcga_pan_can_atlas_2018_patients: {pancan['patient_count']}",
        f"ov_tcga_pan_can_atlas_2018_sequenced_samples: {pancan['sequenced_sample_count']}",
        f"ov_tcga_pan_can_atlas_2018_cna_samples: {pancan['cna_sample_count']}",
        f"ov_tcga_pan_can_atlas_2018_overlap_gdc: {pancan['overlap_patients_with_gdc_cases']['count']}",
        f"ov_tcga_pan_can_atlas_2018_gdc_only: {pancan['overlap_patients_with_gdc_cases']['gdc_only']}",
        f"ov_tcga_pan_can_atlas_2018_portal_only: {pancan['overlap_patients_with_gdc_cases']['portal_only']}",
        f"identifiers_retained: {result['identifiers_retained']}",
        f"controlled_access_files_requested: {result['controlled_access_files_requested']}",
        f"biological_conclusion: {result['biological_conclusion']}",
        f"clinical_guidance: {result['clinical_guidance']}",
    ]
    for key, value in sorted(result["disease_type_counts"].items()):
        lines.append(f"disease_type: {key} {value}")
    for key, value in sorted(result["primary_site_counts"].items()):
        lines.append(f"primary_site: {key} {value}")
    for key, value in sorted(result["project_strategy_case_counts"].items()):
        lines.append(f"project_strategy_cases: {key} {value}")
    for key, value in sorted(result["open_files_by_category"].items()):
        lines.append(f"open_files_category: {key} {value}")
    for key, value in sorted(result["open_files_by_strategy"].items()):
        lines.append(f"open_files_strategy: {key} {value}")
    for key, value in sorted(result["open_files_by_data_type"].items()):
        lines.append(f"open_files_data_type: {key} {value}")
    for key, row in sorted(result["open_file_cases"]["by_data_category"].items()):
        lines.append(f"open_cases_category: {key} {row['count']}")
    for key, row in sorted(result["open_file_cases"]["by_experimental_strategy"].items()):
        lines.append(f"open_cases_strategy: {key} {row['count']}")
    for row in result["citation_rows"]:
        lines.append(
            f"citation: {row['location']} printed={row['printed_number']} observed={row['observed_number']}"
        )
    return "\n".join(lines)


def marked(text):
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("Generated count markers are missing or duplicated.")
    return text.split(BEGIN, 1)[1].split(END, 1)[0].strip("\n")


def resolve_sum_path(name):
    if name.startswith(("protocols/", "tools/", "results/", "registries/")):
        return ROOT / name
    return RESULT / name


def walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_KEYS:
                raise ValueError("Identifier field remains in a frozen file.")
            walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            walk_keys(item)


def check_no_identifiers():
    for path in sorted(RESULT.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".md", ".py"}:
            continue
        text = path.read_text(encoding="utf-8")
        if EMAIL_ADDRESS.search(text):
            raise ValueError(f"Email address remains in {path.name}.")
        if BARCODE.search(text):
            raise ValueError(f"TCGA barcode remains in {path.name}.")
        if path.suffix == ".json":
            walk_keys(json.loads(text))


def check_sums():
    seen = set()
    for line in SUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split("  ", 1)
        if name in seen:
            raise ValueError("Duplicate SHA256SUMS path.")
        seen.add(name)
        if sha256(resolve_sum_path(name).read_bytes()) != digest:
            raise ValueError(f"SHA256SUMS mismatch for {name}.")
    manifest = json.loads((RESULT / "manifest.json").read_text(encoding="utf-8"))
    required = {"manifest.json", "certificate.json"}
    for item in manifest["files"]:
        required.add(item["path"])
    if not required <= seen:
        raise ValueError("SHA256SUMS does not cover the manifest and certificate.")
    return manifest


def agreed_result():
    exported = export_reader.derive(RESULT)
    recomputed = recompute_reader.derive(RESULT)
    if exported["checker"] == recomputed["checker"]:
        raise ValueError("Checkers did not keep independent labels.")
    if export_reader.comparable(exported) != recompute_reader.comparable(recomputed):
        raise ValueError("Export and recompute checkers disagree.")
    return export_reader.comparable(exported)


def certificate_body(result):
    return {
        "schema_version": 1,
        "biological_conclusion": "none",
        "clinical_guidance": "none",
        "controlled_access_files_requested": False,
        "counts": result,
        "identifiers_retained": False,
        "implementation_sha256": {path: sha256((ROOT / path).read_bytes()) for path in PINNED_CODE},
        "readers": ["export_fields", "recompute_buckets"],
        "retrieved_completed_utc": result["retrieved_completed_utc"],
        "retrieved_started_utc": result["retrieved_started_utc"],
    }


def write_outputs(result):
    body = certificate_body(result)
    CERTIFICATE.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    names = ["certificate.json", "manifest.json"]
    manifest = json.loads((RESULT / "manifest.json").read_text(encoding="utf-8"))
    names.extend(item["path"] for item in manifest["files"])
    names.extend(PINNED_CODE)
    lines = []
    for name in names:
        lines.append(sha256(resolve_sum_path(name).read_bytes()) + "  " + name)
    SUMS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    write = "--write-certificate" in sys.argv
    result = agreed_result()
    if write:
        write_outputs(result)
        print(render(result))
        return
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    if certificate.get("counts") != result:
        raise ValueError("Certificate counts differ from the checkers.")
    if certificate.get("clinical_guidance") != "none" or certificate.get("biological_conclusion") != "none":
        raise ValueError("Certificate does not keep the non-guidance labels.")
    if certificate.get("identifiers_retained") is not False:
        raise ValueError("Certificate says identifiers were retained.")
    if certificate.get("controlled_access_files_requested") is not False:
        raise ValueError("Certificate says controlled-access files were requested.")
    if "certificate_sha256" in certificate:
        raise ValueError("Certificate must not carry a self-hash field.")
    for path in PINNED_CODE:
        if certificate["implementation_sha256"][path] != sha256((ROOT / path).read_bytes()):
            raise ValueError(f"Implementation hash differs for {path}.")
    manifest = check_sums()
    for item in manifest["ephemeral_requests"]:
        if item.get("retained") is not False:
            raise ValueError("An identifier response was marked retained.")
    check_no_identifiers()
    doc = DOC.read_text(encoding="utf-8")
    if marked(doc) != render(result):
        raise ValueError("Report count block differs from the checkers.")
    published = result["studies"]["ov_tcga_pub"]
    required = (
        "not clinical guidance",
        "not a biological conclusion",
        "identifiers were not stored",
        "controlled-access file contents were not downloaded",
        f"{result['gdc_project_case_count']} GDC cases",
        f"{published['all_sample_count']} samples",
        "PMID 21720365",
        "316",
    )
    for phrase in required:
        if phrase not in doc:
            raise ValueError(f"Report is missing the required phrase: {phrase}")
    print("PASS: two offline readers agree on the frozen aggregates, certificate, hashes and report block.")
    print("This check does not rebuild identifier sets and does not establish why a case is in one catalog only.")
    print("It is not a biological conclusion and not clinical guidance.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
