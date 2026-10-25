#!/usr/bin/env python3
"""Compare public matrix headers with pinned clinical labels, in memory only.

This diagnostic tests exact equality, not a reconstructed naming convention.
Only aggregate counts and provenance are emitted; no matrix values are read.
"""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.request

import audit_pdc_metadata as pdc
import audit_published_cohorts as clinical


FAILURE_MESSAGE = "ERROR: matrix-header audit failed; no row-level details emitted."
MAX_HEADER_BYTES = 65536
CATEGORY = "Alternate Processing Pipeline"
# Public study/file metadata, not patient identifiers or matrix-column labels.
FILES = {
    "PDC000360": ("97332d25-b8bb-4094-8bed-92290c729599", "d55dbe94-e6d3-4c84-9c25-d966be2112a9",
                  "FD_GLBL_MI_FFPEbridge_Abund_20201002.tsv", "39939461", "e39caac97df93de256dd84c13b6c3bbc"),
    "PDC000358": ("a729bd45-38c5-4144-b340-ee6f51a5d6d7", "b7c7e777-e112-42cd-b9a0-039ca68e6987",
                  "FP_GLBL_MI_FPbridge_Abund_20201002.tsv", "4229172", "bbe675964cb46fc2aa6c08ceecfcda63"),
    "PDC000362": ("196aabca-0e36-46ca-9096-339aee1471da", "55c9f866-4d3c-4cfa-91a4-5cfdb98169e6",
                  "FZ_GLBL_MI_FZbridge_Abund_20201002.tsv", "14577262", "fe16f14794d24076f2ff1554cc02c751"),
}
SHEETS = {"PDC000360": "FFPE_Discovery_clinical", "PDC000358": "FFPE_Pilot_clinical",
          "PDC000362": "Frozen_clinical"}
FILE_QUERY = """query($name:String!){
  getPaginatedUIFile(study_name:$name,study_version:"1",
    data_category:"Alternate Processing Pipeline",offset:0,limit:100){
    total uiFiles{study_id pdc_study_id file_id file_name data_category access
      file_size md5sum downloadable embargo_date} pagination{count total pages}
  }
}"""
URL_QUERY = """query($name:String!,$study:String!){
  uiFilesPerStudy(file_name:$name,study_id:$study){file_id file_name signedUrl{url}}
}"""


def require(condition):
    if not condition:
        raise ValueError(FAILURE_MESSAGE)


def file_from_response(response, study_id, study):
    page = response["data"]["getPaginatedUIFile"]
    require(page["total"] == 1 and page["pagination"] == {"count": 1, "total": 1, "pages": 1})
    require(isinstance(page["uiFiles"], list) and len(page["uiFiles"]) == 1)
    record = page["uiFiles"][0]
    expected = dict(zip(("study_id", "file_id", "file_name", "file_size", "md5sum"), FILES[study_id]))
    expected.update(pdc_study_id=study_id, data_category=CATEGORY, access="Open",
                    downloadable="Yes", embargo_date=None)
    require(record == expected and record["study_id"] == study["study_id"])
    return record


def verify_snapshot(before_studies, before_files, after_studies, after_files):
    pdc.validate_studies(before_studies)
    pdc.validate_studies(after_studies)
    require(before_studies == after_studies and before_files == after_files)


def read_header(response, file_size):
    """Reject a full response before reading; consume at most one bounded line."""
    require(response.status == 206)
    match = re.fullmatch(r"bytes 0-([0-9]+)/([0-9]+)", response.headers.get("Content-Range", ""))
    require(match is not None)
    end, total = map(int, match.groups())
    require(total == file_size and end == min(MAX_HEADER_BYTES, file_size) - 1)
    require(response.headers.get("Content-Encoding", "identity") == "identity")
    line = response.readline(MAX_HEADER_BYTES + 1)
    require(0 < len(line) <= end + 1 and line.endswith(b"\n"))
    fields = next(csv.reader([line.decode("utf-8-sig").rstrip("\r\n")], delimiter="\t", strict=True))
    require(len(fields) > 1 and len(set(fields)) == len(fields))
    return fields, {"header_bytes_read": len(line), "header_sha256": hashlib.sha256(line).hexdigest(),
                    "http_status": 206, "content_range_verified": True}


def fetch_header(record):
    result = pdc.fetch_response(URL_QUERY, {"name": record["file_name"], "study": record["study_id"]})
    rows = result["data"]["uiFilesPerStudy"]
    require(isinstance(rows, list) and len(rows) == 1)
    row = rows[0]
    require(row["file_id"] == record["file_id"] and row["file_name"] == record["file_name"])
    url = row["signedUrl"]["url"]
    parsed = urllib.parse.urlsplit(url)
    require(parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password)
    request = urllib.request.Request(url, headers={"Range": f"bytes=0-{MAX_HEADER_BYTES - 1}",
                                                  "Accept-Encoding": "identity"})
    with urllib.request.urlopen(request, timeout=40) as response:
        require(urllib.parse.urlsplit(response.geturl()).scheme == "https")
        return read_header(response, int(record["file_size"]))


def summarize_labels(headers, records):
    """Count exact full-label matches without inferring links from fragments.

    A matched clinical-NA row is not an identified patient. Literal NA cannot be
    a linkage key. Matrix annotation columns remain in the unmatched count; the
    diagnostic does not guess which unmatched columns represent measurements.
    """
    require(isinstance(headers, list) and bool(headers) and all(isinstance(x, str) for x in headers))
    require(len(headers) == len(set(headers)))
    biological, missing = clinical.classify_clinical(records)
    if biological:
        clinical.collapse_replicates(biological)  # Detect conflicting annotations.
    labelled = [r for r in records if clinical.identity(r[clinical.LABEL_COLUMN])]
    labels = [r[clinical.LABEL_COLUMN] for r in labelled]
    require(len(labels) == len(set(labels)))
    header_set = set(headers)
    matched_bio = [r for r in biological if r[clinical.LABEL_COLUMN] in header_set]
    matched_na = [r for r in missing if clinical.identity(r[clinical.LABEL_COLUMN])
                  and r[clinical.LABEL_COLUMN] in header_set]
    matches = len(matched_bio) + len(matched_na)
    return {
        "matrix_header_columns": len(headers), "clinical_rows": len(records),
        "response_labelled_clinical_rows": len(biological), "clinical_NA_rows": len(missing),
        "clinical_rows_without_linkable_label": len(records) - len(labelled),
        "exact_label_matches": matches, "matched_response_labelled_rows": len(matched_bio),
        "matched_clinical_NA_rows": len(matched_na),
        "matched_unique_sample_keys": len({r["Sample ID"] for r in matched_bio}),
        "matched_unique_patient_keys": len({r["Patient ID"] for r in matched_bio}),
        "unmatched_response_labelled_rows": len(biological) - len(matched_bio),
        "unmatched_linkable_clinical_labels": len(labelled) - matches,
        "matrix_columns_without_exact_clinical_label": len(headers) - matches,
        "duplicate_matrix_headers": 0, "duplicate_linkable_clinical_labels": 0,
        "all_response_labelled_rows_mapped": len(matched_bio) == len(biological),
    }


def run_audit():
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    studies, files, provenance = {}, {}, {}
    for sid in FILES:
        response = pdc.fetch_response(pdc.STUDY_QUERY, {"id": sid})
        studies[sid] = pdc.study_from_response(response)
        provenance[sid] = {"study_before_sha256": pdc.canonical_sha256(response)}
    pdc.validate_studies(studies)
    for sid in FILES:
        response = pdc.fetch_response(FILE_QUERY, {"name": studies[sid]["submitter_id_name"]})
        files[sid] = file_from_response(response, sid, studies[sid])
        provenance[sid]["file_before_sha256"] = pdc.canonical_sha256(response)
    book = clinical.Workbook(clinical.SOURCES["clinical"])
    cohorts = {}
    for sid, sheet in SHEETS.items():
        rows = book.rows(sheet)
        header = rows[0]
        require(len(set(header.values())) == len(header))
        records = [{header[col]: value for col, value in row.items()} for row in rows[1:]]
        fields, header_provenance = fetch_header(files[sid])
        cohorts[sid] = summarize_labels(fields, records)
        cohorts[sid].update(clinical_sheet=sheet, **header_provenance)
    after_studies, after_files = {}, {}
    for sid in FILES:
        response = pdc.fetch_response(pdc.STUDY_QUERY, {"id": sid})
        after_studies[sid] = pdc.study_from_response(response)
        provenance[sid]["study_after_sha256"] = pdc.canonical_sha256(response)
        response = pdc.fetch_response(FILE_QUERY, {"name": after_studies[sid]["submitter_id_name"]})
        after_files[sid] = file_from_response(response, sid, after_studies[sid])
        provenance[sid]["file_after_sha256"] = pdc.canonical_sha256(response)
    verify_snapshot(studies, files, after_studies, after_files)
    return {
        "schema_version": 1, "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": time.monotonic() - timer,
        "scope": "Exact matrix-header to clinical-label diagnostic; no matrix values or predictions read",
        "join": "Unmodified matrix column equals clinical Data Label 2; literal NA is never a key",
        "cohorts": cohorts, "matrix_catalog_files": files, "study_version": "1",
        "clinical_source": dict(clinical.SOURCES["clinical"],
                                url=clinical.BASE + clinical.SOURCES["clinical"]["filename"]),
        "query_sha256": {name: hashlib.sha256(query.encode()).hexdigest()
                         for name, query in (("study", pdc.STUDY_QUERY), ("file", FILE_QUERY), ("url", URL_QUERY))},
        "response_sha256": provenance, "metadata_unchanged_after_header_reads": True,
        "implementation_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in (Path(__file__), Path(pdc.__file__), Path(clinical.__file__))},
        "full_matrices_downloaded": False, "matrix_full_file_checksums_verified": False,
        "limitations": [
            "Header hashes identify only the inspected first line; catalog MD5 values were not verified against matrix bodies.",
            "Unmatched columns include annotation fields; this audit does not identify measurement columns by position or pattern.",
            "Clinical-NA row matches do not establish patient links; nonmatches do not prove files are unrelated.",
            "Exact equality is only the tested mapping rule. Authoritative naming transformations may require missing annotations.",
            "No patient independence, abundance transformation history, score provenance or model performance is established.",
            "Clinical workbooks and raw matrix headers remain in memory; no identifiers, signed URLs or row-level records are emitted.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    try:
        result = run_audit()
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    except Exception:
        print(FAILURE_MESSAGE, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
