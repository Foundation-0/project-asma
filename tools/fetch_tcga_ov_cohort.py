#!/usr/bin/env python3
"""Fetch open GDC and cBioPortal aggregate metadata for TCGA-OV.

Identifier responses are reduced in memory to counts and SHA-256 values.
Those bodies are not written. Controlled-access file contents are not requested.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/tcga-ov-cohort-reconciliation-20261113"
GDC = "https://api.gdc.cancer.gov"
CBIO = "https://www.cbioportal.org/api"
STUDIES = ("ov_tcga", "ov_tcga_pub", "ov_tcga_pan_can_atlas_2018")
USER_AGENT = (
    "ProjectAsma-TCGAOVReconciliation/2026-11-13 "
    "(public aggregate metadata; https://github.com/Foundation-0/project-asma)"
)
PATIENT = re.compile(r"^TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}$")
EXTENDED = re.compile(r"^TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}(?:-[A-Z0-9]+)+$")
BARCODE = re.compile(r"TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}")
EMAIL = re.compile(
    r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
    r"(?![A-Za-z0-9.-])"
)
FORBIDDEN_KEYS = {
    "patientId", "patientIds", "sampleId", "sampleIds", "submitter_id",
    "case_id", "aliquot_id", "uniquePatientKey", "uniqueSampleKey",
}
INFO_KEEP = (
    "portalVersion", "goRewriteVersion", "goRewriteJavaParityCommit", "dbVersion",
    "genesetVersion", "geneTableVersion", "gitBranch", "gitCommitId",
    "gitCommitIdDescribe", "gitCommitIdDescribeShort", "gitDirty",
)
INFO_OMIT = (
    "gitCommitMessageFull", "gitCommitMessageShort",
    "gitCommitMessageUserEmail", "gitCommitMessageUserName",
)
CASE_FILTER = {"op": "and", "content": [
    {"op": "=", "content": {"field": "project.project_id", "value": "TCGA-OV"}},
]}
FILE_PROJECT_FILTER = {"op": "and", "content": [
    {"op": "=", "content": {"field": "cases.project.project_id", "value": "TCGA-OV"}},
]}
OPEN_FILE_FILTER = {"op": "and", "content": [
    {"op": "=", "content": {"field": "cases.project.project_id", "value": "TCGA-OV"}},
    {"op": "=", "content": {"field": "access", "value": "open"}},
]}


class FetchError(RuntimeError):
    pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise FetchError("Unexpected redirect.")


def set_sha256(values):
    body = "".join(item + "\n" for item in sorted(values)).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def patient_barcode(value):
    if not isinstance(value, str):
        return None
    text = value.strip().upper()
    if PATIENT.fullmatch(text):
        return text
    if EXTENDED.fullmatch(text):
        return text[:12]
    return None


def identity_code(value):
    if not isinstance(value, str):
        return None
    text = value.strip().upper()
    if PATIENT.fullmatch(text) or EXTENDED.fullmatch(text):
        return text
    return None


def set_record(values, unparsed=None):
    record = {"count": len(values), "sha256": set_sha256(values)}
    if unparsed is not None:
        record["unparsed"] = unparsed
    return record


def overlap_gdc(gdc_ids, portal_ids):
    both = gdc_ids & portal_ids
    return {
        "count": len(both),
        "sha256": set_sha256(both),
        "gdc_only": len(gdc_ids - portal_ids),
        "gdc_only_sha256": set_sha256(gdc_ids - portal_ids),
        "portal_only": len(portal_ids - gdc_ids),
        "portal_only_sha256": set_sha256(portal_ids - gdc_ids),
    }


def assert_public(value, where):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_KEYS:
                raise FetchError(f"Refusing to store an identifier field in {where}.")
            assert_public(item, where)
    elif isinstance(value, list):
        for item in value:
            assert_public(item, where)
    elif isinstance(value, str):
        if EMAIL.search(value) or BARCODE.search(value):
            raise FetchError(f"Refusing to store contact data or a TCGA barcode in {where}.")


def gdc_url(endpoint, filters=None, facets=None, size=0, extra=None):
    params = [("pretty", "false"), ("size", str(size))]
    if filters is not None:
        params.append(("filters", json.dumps(filters, separators=(",", ":"))))
    if facets:
        params.append(("facets", ",".join(facets)))
    if extra:
        for key, value in extra.items():
            params.append((key, value))
    return GDC + endpoint + "?" + urllib.parse.urlencode(params)


def get_bytes(url):
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urllib.request.build_opener(_NoRedirect()).open(request, timeout=180) as response:
            if response.status != 200:
                raise FetchError("Unexpected HTTP status.")
            body = response.read()
    except FetchError:
        raise
    except Exception as exc:
        raise FetchError("Request failed.") from exc
    return body


def get_json(url):
    body = get_bytes(url)
    try:
        return body, json.loads(body)
    except ValueError as exc:
        raise FetchError("Response was not JSON.") from exc


def write_json(path, payload):
    assert_public(payload, path.name)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_raw(path, body):
    payload = json.loads(body)
    assert_public(payload, path.name)
    path.write_bytes(body)


def paged_list(base_url, page_size=1000):
    rows = []
    requests = []
    for page in range(50):
        join = "&" if "?" in base_url else "?"
        url = f"{base_url}{join}pageSize={page_size}&pageNumber={page}"
        body, payload = get_json(url)
        if not isinstance(payload, list):
            raise FetchError("Expected a JSON list.")
        requests.append({
            "url": url, "role": "identifier_page", "sha256": hashlib.sha256(body).hexdigest(),
            "bytes": len(body), "retained": False, "reason": "identifier body reduced to a count and SHA-256",
            "row_count": len(payload),
        })
        rows.extend(payload)
        if len(payload) < page_size:
            break
    else:
        raise FetchError("Pagination did not end.")
    return rows, requests


def collect_codes(rows, field, parser):
    found = set()
    unparsed = 0
    for row in rows:
        code = parser(row.get(field))
        if code is None:
            unparsed += 1
        else:
            found.add(code)
    return found, unparsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--output", type=Path, default=RESULT)
    args = parser.parse_args()
    output = args.output
    snapshot = output / "snapshot"
    if snapshot.exists() and any(snapshot.iterdir()) and not args.force:
        raise SystemExit("Snapshot already exists. Refusing to overwrite.")
    snapshot.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    files = []
    ephemeral = []

    def keep_raw(name, role, url, body, **extra):
        write_raw(snapshot / name, body)
        item = {"path": f"snapshot/{name}", "role": role, "kind": "raw", "url": url}
        item.update(extra)
        files.append(item)

    status_url = GDC + "/status"
    status_body, status = get_json(status_url)
    keep_raw("gdc-status.json", "gdc_status", status_url, status_body)

    project_url = gdc_url(
        "/projects/TCGA-OV",
        facets=None,
        size=0,
        extra={"expand": "summary,summary.data_categories,summary.experimental_strategies"},
    )
    # size=0 is ignored for a single project document; the URL still records it.
    project_body, project_envelope = get_json(project_url)
    keep_raw("gdc-project-tcga-ov.json", "gdc_project", project_url, project_body)

    cases_url = gdc_url(
        "/cases", CASE_FILTER,
        ["disease_type", "primary_site", "samples.sample_type", "samples.tissue_type"],
    )
    cases_body, _cases = get_json(cases_url)
    keep_raw("gdc-cases-facets.json", "gdc_cases_facets", cases_url, cases_body)

    open_url = gdc_url(
        "/files", OPEN_FILE_FILTER,
        ["data_category", "data_type", "experimental_strategy"],
    )
    open_body, _open = get_json(open_url)
    keep_raw("gdc-files-open-facets.json", "gdc_files_open_facets", open_url, open_body)

    access_url = gdc_url("/files", FILE_PROJECT_FILTER, ["access"])
    access_body, _access = get_json(access_url)
    keep_raw("gdc-files-access-facets.json", "gdc_files_access_facets", access_url, access_body)

    info_url = CBIO + "/info"
    info_body, info = get_json(info_url)
    projected_info = {key: info[key] for key in INFO_KEEP if key in info}
    projected_info["omitted_fields"] = [key for key in INFO_OMIT if key in info]
    projected_info["omission_reason"] = (
        "Commit message and author fields were dropped before storage because they "
        "can contain a personal name, an email address, or a session URL."
    )
    projected_info["source_response_sha256"] = hashlib.sha256(info_body).hexdigest()
    write_json(snapshot / "cbioportal-info.json", projected_info)
    files.append({
        "path": "snapshot/cbioportal-info.json",
        "role": "cbioportal_info",
        "kind": "projected",
        "url": info_url,
        "source_response_sha256": projected_info["source_response_sha256"],
    })

    case_page_url = gdc_url(
        "/cases", CASE_FILTER, size=2000,
        extra={"fields": "submitter_id,samples.sample_type,samples.tissue_type"},
    )
    case_page_body, case_page = get_json(case_page_url)
    ephemeral.append({
        "url": case_page_url, "role": "gdc_case_identifiers",
        "sha256": hashlib.sha256(case_page_body).hexdigest(), "bytes": len(case_page_body),
        "retained": False, "reason": "case barcodes reduced to a count and SHA-256",
    })
    hits = case_page["data"]["hits"]
    if case_page["data"]["pagination"]["total"] != len(hits):
        raise FetchError("Case identifier page did not contain every case.")
    gdc_cases = set()
    primary_tumor = set()
    tumor_tissue = set()
    unparsed_cases = 0
    for hit in hits:
        code = patient_barcode(hit.get("submitter_id"))
        if code is None:
            unparsed_cases += 1
            continue
        gdc_cases.add(code)
        types = {str(sample.get("sample_type") or "").casefold() for sample in hit.get("samples") or []}
        tissues = {str(sample.get("tissue_type") or "").casefold() for sample in hit.get("samples") or []}
        if "primary tumor" in types:
            primary_tumor.add(code)
        if "tumor" in tissues:
            tumor_tissue.add(code)

    by_category = {}
    by_type = {}
    by_strategy = {}
    files_read = 0
    files_without_case = 0
    files_unparsed = 0
    offset = 0
    page_size = 5000
    while True:
        page_url = gdc_url(
            "/files", OPEN_FILE_FILTER, size=page_size,
            extra={
                "from": str(offset),
                "fields": "cases.submitter_id,data_category,data_type,experimental_strategy,access",
            },
        )
        page_body, page = get_json(page_url)
        ephemeral.append({
            "url": page_url, "role": "gdc_open_file_metadata",
            "sha256": hashlib.sha256(page_body).hexdigest(), "bytes": len(page_body),
            "retained": False, "reason": "open-file case barcodes reduced to counts and SHA-256",
        })
        page_hits = page["data"]["hits"]
        total = page["data"]["pagination"]["total"]
        for hit in page_hits:
            if hit.get("access") != "open":
                raise FetchError("Open-file filter returned a non-open record.")
            files_read += 1
            codes = []
            for case in hit.get("cases") or []:
                code = patient_barcode(case.get("submitter_id"))
                if code is None:
                    files_unparsed += 1
                else:
                    codes.append(code)
            if not codes:
                files_without_case += 1
                continue
            category = hit.get("data_category") or "_missing"
            data_type = hit.get("data_type") or "_missing"
            strategy = hit.get("experimental_strategy") or "_missing"
            for code in codes:
                by_category.setdefault(category, set()).add(code)
                by_type.setdefault(data_type, set()).add(code)
                by_strategy.setdefault(strategy, set()).add(code)
        offset += len(page_hits)
        if offset >= total or not page_hits:
            break
        if offset > 100000:
            raise FetchError("Open-file pagination did not end.")

    def category_set(name):
        found = set()
        for key, values in by_category.items():
            if key.casefold() == name:
                found |= values
        return found

    open_snv = category_set("simple nucleotide variation")
    open_cna = category_set("copy number variation")
    any_open = set()
    for values in by_category.values():
        any_open |= values
    open_wxs = set()
    for key, values in by_strategy.items():
        if key.casefold() == "wxs":
            open_wxs |= values

    def records_for(mapping):
        return {key: set_record(values) for key, values in sorted(mapping.items())}

    outside = any_open - gdc_cases
    digests = {
        "schema_version": 1,
        "id_rule": (
            "Patient values are the uppercase 12-character TCGA participant barcode. "
            "A longer TCGA sample barcode contributes only that participant portion. "
            "Sample values keep the full uppercase sample barcode. "
            "SHA-256 covers the sorted unique values, one UTF-8 line each, including the final newline. "
            "The identifiers themselves are not stored."
        ),
        "gdc_cases": set_record(gdc_cases, unparsed_cases),
        "gdc_primary_tumor_cases": set_record(primary_tumor),
        "gdc_tumor_tissue_cases": set_record(tumor_tissue),
        "gdc_cases_without_tumor_tissue": set_record(gdc_cases - tumor_tissue),
        "open_file_cases": {
            "any": set_record(any_open),
            "outside_gdc_case_set": len(outside),
            "by_data_category": records_for(by_category),
            "by_data_type": records_for(by_type),
            "by_experimental_strategy": records_for(by_strategy),
            "open_snv": set_record(open_snv),
            "open_cna": set_record(open_cna),
            "open_snv_and_cna": set_record(open_snv & open_cna),
            "gdc_cases_without_open_snv": set_record(gdc_cases - open_snv),
            "open_wxs": set_record(open_wxs),
            "files_read": files_read,
            "files_without_case": files_without_case,
            "files_with_unparsed_case": files_unparsed,
        },
        "studies": {},
    }

    for study_id in STUDIES:
        study_url = f"{CBIO}/studies/{study_id}"
        study_body, study = get_json(study_url)
        keep_raw(f"cbioportal-study-{study_id}.json", "cbioportal_study", study_url, study_body, study_id=study_id)
        profile_url = f"{CBIO}/studies/{study_id}/molecular-profiles"
        profile_body, _profiles = get_json(profile_url)
        keep_raw(
            f"cbioportal-profiles-{study_id}.json", "cbioportal_profiles",
            profile_url, profile_body, study_id=study_id,
        )
        patients, patient_requests = paged_list(f"{CBIO}/studies/{study_id}/patients")
        samples, sample_requests = paged_list(f"{CBIO}/studies/{study_id}/samples")
        for item in patient_requests + sample_requests:
            item["study_id"] = study_id
        ephemeral.extend(patient_requests)
        ephemeral.extend(sample_requests)
        patient_ids, unparsed_patients = collect_codes(patients, "patientId", patient_barcode)
        sample_ids, unparsed_samples = collect_codes(samples, "sampleId", identity_code)
        sample_patients, _unparsed_sample_patients = collect_codes(samples, "patientId", patient_barcode)
        index_url = f"{CBIO}/studies/{study_id}/sample-lists"
        index_body, index = get_json(index_url)
        ephemeral.append({
            "url": index_url, "role": "sample_list_index", "study_id": study_id,
            "sha256": hashlib.sha256(index_body).hexdigest(), "bytes": len(index_body),
            "retained": False, "reason": "replaced by projected lists with sampleIds removed",
        })
        projected_lists = []
        for entry in index:
            list_id = entry["sampleListId"]
            list_url = f"{CBIO}/sample-lists/{urllib.parse.quote(list_id, safe='')}"
            list_body, payload = get_json(list_url)
            ephemeral.append({
                "url": list_url, "role": "sample_list", "study_id": study_id,
                "sha256": hashlib.sha256(list_body).hexdigest(), "bytes": len(list_body),
                "retained": False, "reason": "sampleIds removed after counting",
            })
            sample_ids_in_list = payload.get("sampleIds") or []
            if payload.get("sampleCount") != len(sample_ids_in_list):
                raise FetchError(f"{list_id} sampleCount differed from sampleIds length.")
            projected_lists.append({
                "sampleListId": payload["sampleListId"],
                "category": payload.get("category"),
                "name": payload.get("name"),
                "description": payload.get("description") or "",
                "sampleCount": payload["sampleCount"],
                "sample_id_count": len(sample_ids_in_list),
                "source_response_sha256": hashlib.sha256(list_body).hexdigest(),
            })
        projected = {"study_id": study_id, "lists": projected_lists}
        list_name = f"cbioportal-sample-lists-{study_id}.json"
        write_json(snapshot / list_name, projected)
        files.append({
            "path": f"snapshot/{list_name}",
            "role": "cbioportal_sample_lists",
            "kind": "projected",
            "url": index_url,
            "study_id": study_id,
        })
        digests["studies"][study_id] = {
            "patients": set_record(patient_ids, unparsed_patients),
            "samples": set_record(sample_ids, unparsed_samples),
            "patients_with_a_sample": set_record(sample_patients),
            "patients_without_a_sample": set_record(patient_ids - sample_patients),
            "overlap_patients_with_gdc_cases": overlap_gdc(gdc_cases, patient_ids),
            "overlap_sample_patients_with_gdc_cases": overlap_gdc(gdc_cases, sample_patients),
        }
        print(
            f"{study_id} samples={len(sample_ids)} patients={len(patient_ids)} "
            f"overlap={digests['studies'][study_id]['overlap_patients_with_gdc_cases']['count']}"
        )

    write_json(snapshot / "set-digests.json", digests)
    files.append({
        "path": "snapshot/set-digests.json",
        "role": "set_digests",
        "kind": "derived",
        "url": None,
        "note": "Counts and SHA-256 values computed in memory from identifier responses that were not stored.",
    })
    manifest = {
        "schema_version": 1,
        "retrieved_started_utc": started,
        "retrieved_completed_utc": datetime.now(timezone.utc).isoformat(),
        "gdc_api": GDC,
        "cbioportal_api": CBIO,
        "gdc_data_release": status.get("data_release"),
        "gdc_tag": status.get("tag"),
        "note": (
            "Aggregate and projected JSON only. Identifier bodies were hashed in memory and not stored. "
            "No controlled-access file content was requested. Counts are data availability, not a biological "
            "conclusion and not clinical guidance."
        ),
        "files": files,
        "ephemeral_requests": ephemeral,
    }
    assert_public(manifest, "manifest")
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"gdc_cases={len(gdc_cases)} primary_tumor={len(primary_tumor)} "
        f"open_snv={len(open_snv)} open_cna={len(open_cna)} files_read={files_read}"
    )
    print(f"release={status.get('data_release')}")


if __name__ == "__main__":
    main()
