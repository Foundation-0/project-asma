#!/usr/bin/env python3
"""Recompute TCGA-OV cohort totals from frozen facet buckets and list text.

This reader sums facet buckets, parses sample-list descriptions, and checks
the fetch-time set-digest arithmetic. It does not import the export reader.
Identifier lists are not in the snapshot, so the intersection itself is not
rebuilt here.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

CHECKER = "recompute_buckets"
STUDIES = ("ov_tcga", "ov_tcga_pub", "ov_tcga_pan_can_atlas_2018")
KEY_LIST_CATEGORIES = (
    "all_cases_in_study",
    "all_cases_with_mutation_data",
    "all_cases_with_cna_data",
    "all_cases_with_mutation_and_cna_data",
    "all_cases_with_mutation_and_cna_and_mrna_data",
)
STUDY_FIELD_FOR_CATEGORY = {
    "all_cases_in_study": "all_sample_count",
    "all_cases_with_mutation_data": "sequenced_sample_count",
    "all_cases_with_cna_data": "cna_sample_count",
    "all_cases_with_mutation_and_cna_and_mrna_data": "complete_sample_count",
}
FORBIDDEN_KEYS = {
    "patientId", "patientIds", "sampleId", "sampleIds", "submitter_id",
    "case_id", "aliquot_id", "uniquePatientKey", "uniqueSampleKey",
}
BARCODE = re.compile(r"TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}")
EMAIL = re.compile(
    r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
    r"(?![A-Za-z0-9.-])"
)
PATIENT = re.compile(r"^TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}$")
EXTENDED = re.compile(r"^TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}(?:-[A-Z0-9]+)+$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SAMPLE_COUNT_IN_TEXT = re.compile(r"\((\d+) samples\)")
EXOME_OF = re.compile(r"exome sequencing of (\d+)", re.IGNORECASE)


class CountError(ValueError):
    """Malformed frozen aggregate. The message names a field, not a person."""


def _require(condition, message):
    if not condition:
        raise CountError(message)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "Duplicate JSON object key.")
        result[key] = value
    return result


def _reject_constant(value):
    raise CountError("Nonfinite JSON value.")


def decode_json(raw):
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    try:
        return json.loads(raw, object_pairs_hook=_pairs, parse_constant=_reject_constant)
    except CountError:
        raise
    except (ValueError, UnicodeError, RecursionError):
        raise CountError("Invalid JSON document.") from None


def load_json(path):
    return decode_json(Path(path).read_bytes())


def patient_barcode(value):
    """Return the 12-character TCGA patient barcode, or None."""
    if not isinstance(value, str):
        return None
    text = value.strip().upper()
    if PATIENT.fullmatch(text):
        return text
    if EXTENDED.fullmatch(text):
        return text[:12]
    return None


def set_sha256(values):
    """SHA-256 of sorted unique barcodes, one UTF-8 line each, including the last newline."""
    body = "".join(item + "\n" for item in sorted(values)).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def overlap(left, right):
    both = left & right
    only_left = left - right
    only_right = right - left
    return {
        "count": len(both),
        "sha256": set_sha256(both),
        "left_only": len(only_left),
        "left_only_sha256": set_sha256(only_left),
        "right_only": len(only_right),
        "right_only_sha256": set_sha256(only_right),
    }


def assert_public_aggregate(value, where="snapshot"):
    if isinstance(value, dict):
        for key, item in value.items():
            _require(key not in FORBIDDEN_KEYS, f"Identifier field in {where}.")
            assert_public_aggregate(item, where)
    elif isinstance(value, list):
        for item in value:
            assert_public_aggregate(item, where)
    elif isinstance(value, str):
        _require(EMAIL.search(value) is None, f"Email address in {where}.")
        _require(BARCODE.search(value) is None, f"TCGA barcode in {where}.")


def _int(value, label):
    _require(type(value) is int and value >= 0, f"{label} is not a nonnegative integer.")
    return value


def _buckets(payload, facet):
    aggregations = payload["data"]["aggregations"]
    _require(facet in aggregations, f"Missing facet {facet}.")
    found = {}
    for bucket in aggregations[facet]["buckets"]:
        key = bucket["key"]
        _require(isinstance(key, str) and key not in found, "Facet bucket key.")
        found[key] = _int(bucket["doc_count"], f"{facet} {key}")
    return dict(sorted(found.items()))


def _by_role(manifest):
    found = {}
    for item in manifest["files"]:
        found.setdefault(item["role"], []).append(item)
    return found


def _one(result_dir, grouped, role):
    rows = grouped.get(role) or []
    _require(len(rows) == 1, f"Expected one {role} file.")
    return load_json(result_dir / rows[0]["path"])


def _study_files(result_dir, grouped, role):
    rows = grouped.get(role) or []
    _require(len(rows) == len(STUDIES), f"Expected {len(STUDIES)} {role} files.")
    found = {}
    for item in rows:
        payload = load_json(result_dir / item["path"])
        study_id = item.get("study_id")
        _require(study_id in STUDIES and study_id not in found, "Study file id.")
        found[study_id] = payload
    _require(tuple(sorted(found)) == tuple(sorted(STUDIES)), "Study file set.")
    return found


def _description_count(description):
    found = [int(item) for item in SAMPLE_COUNT_IN_TEXT.findall(description or "")]
    if not found:
        return None
    _require(len(set(found)) == 1, "Sample-list description has conflicting counts.")
    return found[0]


def _exome_phrase_count(description):
    match = EXOME_OF.search(description or "")
    if not match:
        return None
    return int(match.group(1))


def _digest_set(record, label):
    _require(isinstance(record, dict), label)
    count = _int(record["count"], label)
    digest = record["sha256"]
    _require(isinstance(digest, str) and HEX64.fullmatch(digest), f"{label} hash.")
    return {"count": count, "sha256": digest}


def _digest_overlap(record, label):
    parsed = _digest_set(record, label)
    for key in ("gdc_only", "portal_only"):
        parsed[key] = _int(record[key], f"{label} {key}")
        digest = record[key + "_sha256"]
        _require(isinstance(digest, str) and HEX64.fullmatch(digest), f"{label} {key} hash.")
        parsed[key + "_sha256"] = digest
    return parsed


def derive(result_dir):
    result_dir = Path(result_dir)
    manifest = load_json(result_dir / "manifest.json")
    _require(manifest.get("schema_version") == 1, "Manifest schema.")
    grouped = _by_role(manifest)
    for item in manifest["files"]:
        assert_public_aggregate(load_json(result_dir / item["path"]), item["path"])

    status = _one(result_dir, grouped, "gdc_status")
    project_envelope = _one(result_dir, grouped, "gdc_project")
    cases = _one(result_dir, grouped, "gdc_cases_facets")
    open_files = _one(result_dir, grouped, "gdc_files_open_facets")
    access_files = _one(result_dir, grouped, "gdc_files_access_facets")
    info = _one(result_dir, grouped, "cbioportal_info")
    studies = _study_files(result_dir, grouped, "cbioportal_study")
    profiles = _study_files(result_dir, grouped, "cbioportal_profiles")
    lists = _study_files(result_dir, grouped, "cbioportal_sample_lists")
    digests = _one(result_dir, grouped, "set_digests")

    project = project_envelope["data"]
    summary = project["summary"]
    release = status["data_release"]
    _require(isinstance(release, str) and release.strip(), "GDC data release.")
    case_count = _int(summary["case_count"], "project case_count")
    file_count = _int(summary["file_count"], "project file_count")
    cases_total = _int(cases["data"]["pagination"]["total"], "cases total")
    open_total = _int(open_files["data"]["pagination"]["total"], "open files total")
    access_buckets = _buckets(access_files, "access")

    study_rows = {}
    for study_id in STUDIES:
        record = studies[study_id]
        _require(record.get("studyId") == study_id, "Study id.")
        _require(isinstance(profiles[study_id], list), "Profile list.")
        projected = lists[study_id]
        _require(projected.get("study_id") == study_id, "Sample-list study.")
        list_rows = []
        for item in projected["lists"]:
            _require("sampleIds" not in item, "Sample identifiers were retained.")
            description = item.get("description") or ""
            list_rows.append({
                "sample_list_id": item["sampleListId"],
                "category": item["category"],
                "name": item["name"],
                "sample_count": _int(item["sampleCount"], item["sampleListId"]),
                "sample_id_count": _int(item["sample_id_count"], item["sampleListId"] + " ids"),
                "description_count": _description_count(description),
            })
        digest = digests["studies"][study_id]
        patients = _digest_set(digest["patients"], study_id + " patients")
        samples = _digest_set(digest["samples"], study_id + " samples")
        study_rows[study_id] = {
            "name": record["name"],
            "cancer_type_id": record.get("cancerTypeId"),
            "pmid": record.get("pmid"),
            "citation": record.get("citation"),
            "public_study": record.get("publicStudy"),
            "reference_genome": record.get("referenceGenome"),
            "all_sample_count": _int(record["allSampleCount"], study_id + " all"),
            "sequenced_sample_count": _int(record["sequencedSampleCount"], study_id + " sequenced"),
            "cna_sample_count": _int(record["cnaSampleCount"], study_id + " cna"),
            "complete_sample_count": _int(record["completeSampleCount"], study_id + " complete"),
            "exome_phrase_count": _exome_phrase_count(record.get("description") or ""),
            "profile_count": len(profiles[study_id]),
            "sample_lists": list_rows,
            "patient_count": patients["count"],
            "patient_sha256": patients["sha256"],
            "patient_unparsed": _int(digest["patients"].get("unparsed", 0), "unparsed patients"),
            "sample_count_observed": samples["count"],
            "sample_sha256": samples["sha256"],
            "sample_unparsed": _int(digest["samples"].get("unparsed", 0), "unparsed samples"),
            "patients_with_a_sample": _digest_set(digest["patients_with_a_sample"], "with sample"),
            "patients_without_a_sample": _digest_set(digest["patients_without_a_sample"], "without sample"),
            "overlap_patients_with_gdc_cases": _digest_overlap(digest["overlap_patients_with_gdc_cases"], "patient overlap"),
            "overlap_sample_patients_with_gdc_cases": _digest_overlap(
                digest["overlap_sample_patients_with_gdc_cases"], "sample-patient overlap"
            ),
        }
        phrase = study_rows[study_id]["exome_phrase_count"]
        sequenced = study_rows[study_id]["sequenced_sample_count"]
        study_rows[study_id]["exome_phrase_conflicts_with_sequenced_count"] = (
            phrase is not None and phrase != sequenced
        )

    gdc_cases = _digest_set(digests["gdc_cases"], "GDC cases")
    open_cases = digests["open_file_cases"]
    result = {
        "checker": CHECKER,
        "retrieved_started_utc": manifest["retrieved_started_utc"],
        "retrieved_completed_utc": manifest["retrieved_completed_utc"],
        "gdc_data_release": release,
        "gdc_api_version": status.get("version"),
        "gdc_tag": status.get("tag"),
        "gdc_commit": status.get("commit"),
        "cbioportal_portal_version": info.get("portalVersion"),
        "cbioportal_db_version": info.get("dbVersion"),
        "cbioportal_git_commit": info.get("gitCommitId"),
        "gdc_project_id": project.get("project_id"),
        "gdc_project_name": project.get("name"),
        "gdc_project_case_count": case_count,
        "gdc_cases_pagination_total": cases_total,
        "gdc_project_file_count": file_count,
        "gdc_open_file_count": open_total,
        "gdc_controlled_file_count": access_buckets.get("controlled"),
        "gdc_access_open_file_count": access_buckets.get("open"),
        "disease_type_counts": _buckets(cases, "disease_type"),
        "primary_site_counts": _buckets(cases, "primary_site"),
        "sample_type_case_counts": _buckets(cases, "samples.sample_type"),
        "tissue_type_case_counts": _buckets(cases, "samples.tissue_type"),
        "open_files_by_category": _buckets(open_files, "data_category"),
        "open_files_by_data_type": _buckets(open_files, "data_type"),
        "open_files_by_strategy": _buckets(open_files, "experimental_strategy"),
        "project_strategy_case_counts": {
            row["experimental_strategy"]: _int(row["case_count"], "strategy cases")
            for row in summary["experimental_strategies"]
        },
        "project_strategy_file_counts": {
            row["experimental_strategy"]: _int(row["file_count"], "strategy files")
            for row in summary["experimental_strategies"]
        },
        "project_category_case_counts": {
            row["data_category"]: _int(row["case_count"], "category cases")
            for row in summary["data_categories"]
        },
        "project_category_file_counts": {
            row["data_category"]: _int(row["file_count"], "category files")
            for row in summary["data_categories"]
        },
        "project_strategy_file_count_sum": sum(
            _int(row["file_count"], "strategy files") for row in summary["experimental_strategies"]
        ),
        "project_strategy_file_count_gap": file_count - sum(
            _int(row["file_count"], "strategy files") for row in summary["experimental_strategies"]
        ),
        "gdc_case_set_count": gdc_cases["count"],
        "gdc_case_set_sha256": gdc_cases["sha256"],
        "gdc_case_unparsed": _int(digests["gdc_cases"].get("unparsed", 0), "unparsed cases"),
        "gdc_primary_tumor_cases": _digest_set(digests["gdc_primary_tumor_cases"], "primary tumor"),
        "gdc_tumor_tissue_cases": _digest_set(digests["gdc_tumor_tissue_cases"], "tumor tissue"),
        "gdc_cases_without_tumor_tissue": _digest_set(digests["gdc_cases_without_tumor_tissue"], "no tumor tissue"),
        "open_file_cases": open_cases,
        "studies": study_rows,
        "identifiers_retained": False,
        "controlled_access_files_requested": False,
        "biological_conclusion": "none",
        "clinical_guidance": "none",
    }
    result["citation_rows"] = _citations(result)
    _enforce(result)
    return result


def _enforce(result):
    """Reject a frozen aggregate whose independent sums disagree with named totals."""
    cases_total = result["gdc_cases_pagination_total"]
    _require(sum(result["disease_type_counts"].values()) == cases_total, "Disease-type buckets do not sum to the case total.")
    _require(sum(result["primary_site_counts"].values()) == cases_total, "Primary-site buckets do not sum to the case total.")
    _require(result["gdc_project_case_count"] == cases_total, "Project case_count differs from the cases total.")
    _require(result["gdc_case_set_count"] == cases_total, "Hashed GDC case set differs from the cases total.")
    for label, counts in (
        ("sample type", result["sample_type_case_counts"]),
        ("tissue type", result["tissue_type_case_counts"]),
    ):
        for key, count in counts.items():
            _require(count <= cases_total, f"{label} count exceeds the case total: {key}.")
    open_total = result["gdc_open_file_count"]
    _require(sum(result["open_files_by_category"].values()) == open_total, "Open category file counts do not sum.")
    _require(sum(result["open_files_by_data_type"].values()) == open_total, "Open data-type file counts do not sum.")
    _require(sum(result["open_files_by_strategy"].values()) == open_total, "Open strategy file counts do not sum.")
    _require(result["gdc_access_open_file_count"] == open_total, "Access facet open count differs from the open-file total.")
    _require(
        result["gdc_access_open_file_count"] + result["gdc_controlled_file_count"] == result["gdc_project_file_count"],
        "Open plus controlled file counts differ from the project file count.",
    )
    _require(
        result["project_strategy_file_count_sum"] + result["project_strategy_file_count_gap"]
        == result["gdc_project_file_count"],
        "Strategy file-count gap does not reconcile.",
    )
    _require(result["project_strategy_file_count_sum"] == sum(result["project_strategy_file_counts"].values()),
             "Strategy file-count sum was not recomputed from the rows.")
    gdc_count = result["gdc_case_set_count"]
    _require(
        result["gdc_tumor_tissue_cases"]["count"] + result["gdc_cases_without_tumor_tissue"]["count"] == gdc_count,
        "Tumor-tissue partition.",
    )
    for study_id, study in result["studies"].items():
        by_category = {}
        for item in study["sample_lists"]:
            _require(item["sample_id_count"] == item["sample_count"], f"{item['sample_list_id']} count mismatch.")
            if item["description_count"] is not None:
                _require(item["description_count"] == item["sample_count"], f"{item['sample_list_id']} description mismatch.")
            by_category.setdefault(item["category"], []).append(item)
        for category, field in STUDY_FIELD_FOR_CATEGORY.items():
            rows = by_category.get(category) or []
            if len(rows) == 1:
                _require(rows[0]["sample_count"] == study[field], f"{study_id} {category} differs from {field}.")
        _require(
            study["patients_with_a_sample"]["count"] + study["patients_without_a_sample"]["count"] == study["patient_count"],
            f"{study_id} patient partition.",
        )
        for key in ("overlap_patients_with_gdc_cases", "overlap_sample_patients_with_gdc_cases"):
            row = study[key]
            _require(row["count"] + row["gdc_only"] == gdc_count, f"{study_id} {key} GDC partition.")
        patient_overlap = study["overlap_patients_with_gdc_cases"]
        _require(
            patient_overlap["count"] + patient_overlap["portal_only"] == study["patient_count"],
            f"{study_id} patient overlap partition.",
        )
        sample_overlap = study["overlap_sample_patients_with_gdc_cases"]
        _require(
            sample_overlap["count"] + sample_overlap["portal_only"] == study["patients_with_a_sample"]["count"],
            f"{study_id} sample-patient overlap partition.",
        )
    open_cases = result["open_file_cases"]
    _require(open_cases["any"]["count"] <= gdc_count, "Open-file cases exceed the GDC case set.")
    _require(
        open_cases["gdc_cases_without_open_snv"]["count"] + open_cases["open_snv"]["count"] == gdc_count,
        "Open SNV partition.",
    )
    _require(
        open_cases["open_snv_and_cna"]["count"] <= open_cases["open_snv"]["count"],
        "Open SNV and CNA exceeds open SNV.",
    )
    _require(
        open_cases["open_snv_and_cna"]["count"] <= open_cases["open_cna"]["count"],
        "Open SNV and CNA exceeds open CNA.",
    )
    _require(result["identifiers_retained"] is False, "Identifier retention flag.")
    _require(result["controlled_access_files_requested"] is False, "Controlled-access flag.")
    _require(result["biological_conclusion"] == "none", "Biological conclusion flag.")
    _require(result["clinical_guidance"] == "none", "Clinical guidance flag.")


def _citations(result):
    published = result["studies"]["ov_tcga_pub"]
    return [
        {
            "location": "docs/directions.md GDC TCGA-OV case count",
            "printed_number": 608,
            "observed_number": result["gdc_project_case_count"],
            "cite_as": "GDC project TCGA-OV summary case_count on the recorded data release",
        },
        {
            "location": "docs/directions.md cBioPortal ov_tcga_pub sample count",
            "printed_number": 489,
            "observed_number": published["all_sample_count"],
            "cite_as": "cBioPortal ov_tcga_pub allSampleCount: the 2011 Nature analysed sample count for mRNA, microRNA, methylation and copy number",
        },
        {
            "location": "cBioPortal ov_tcga_pub sequencedSampleCount and PMID 21720365",
            "printed_number": None,
            "observed_number": published["sequenced_sample_count"],
            "cite_as": "Exome sequencing count. Do not cite the portal description's exome sentence when it disagrees with sequencedSampleCount",
        },
        {
            "location": "CLAIMS.md V40 Human Protein Atlas TCGA RNA cohort",
            "printed_number": 349,
            "observed_number": None,
            "cite_as": "Human Protein Atlas version 26.0 RNA cohort size for ovary serous cystadenocarcinoma. Not the GDC case count and not the 2011 analysed-sample count. Not remeasured here",
        },
    ]


def comparable(result):
    copied = json.loads(json.dumps(result))
    copied.pop("checker", None)
    return copied
