"""Audit released PDC linkage metadata in memory; emit aggregate JSON only.

Exact case_id equality can establish observed overlap, but unequal identifiers
cannot establish patient independence. No clinical values, submitter identifiers,
data files, or analysis predictions are requested. Response hashes identify the
received metadata content; they are not proof of patient independence.
"""

import argparse
import datetime as dt
import hashlib
from itertools import combinations
import json
import sys
import urllib.request


ENDPOINT = "https://pdc.cancer.gov/graphql"
STUDY_IDS = ("PDC000360", "PDC000358", "PDC000362")
EXPECTED_VERSION = "1"
FAILURE_MESSAGE = "ERROR: metadata audit failed; no row-level details emitted."
MAX_RESPONSE_BYTES = 4 * 1024 * 1024

STUDY_QUERY = """query($id:String!){
  getPaginatedUIStudy(pdc_study_id:$id,source:"pdc"){
    total uiStudies{
      study_id pdc_study_id submitter_id_name cases_count aliquots_count
      embargo_date versions{number}
    }
  }
}"""
BIOSPECIMEN_QUERY = """query($id:String!){
  uiBiospecimenPerStudy(study_id:$id,source:"pdc"){
    case_id sample_id aliquot_id aliquot_is_ref pool project_name
  }
}"""
STUDY_FIELDS = {
    "study_id", "pdc_study_id", "submitter_id_name", "cases_count",
    "aliquots_count", "embargo_date", "versions",
}
ROW_FIELDS = {
    "case_id", "sample_id", "aliquot_id", "aliquot_is_ref", "pool", "project_name",
}
KEY_FIELDS = ("case_id", "sample_id", "aliquot_id")


class AuditError(ValueError):
    """A failed contract, deliberately without input values in its message."""


def require(condition):
    if not condition:
        raise AuditError(FAILURE_MESSAGE)


def nonempty_text(value):
    return isinstance(value, str) and bool(value) and value == value.strip()


def canonical_sha256(value):
    """Hash UTF-8 JSON with sorted object keys; preserve array ordering."""
    serialized = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def validate_studies(studies):
    require(isinstance(studies, dict) and set(studies) == set(STUDY_IDS))
    uuids = set()
    for study_id in STUDY_IDS:
        meta = studies[study_id]
        require(isinstance(meta, dict) and set(meta) == STUDY_FIELDS)
        require(meta["pdc_study_id"] == study_id)
        require(nonempty_text(meta["study_id"]))
        require(meta["study_id"] not in uuids)
        uuids.add(meta["study_id"])
        require(nonempty_text(meta["submitter_id_name"]))
        require(meta["versions"] == [{"number": EXPECTED_VERSION}])
        require(meta["embargo_date"] is None)
        for field in ("cases_count", "aliquots_count"):
            require(type(meta[field]) is int and meta[field] > 0)


def unique_counts(rows):
    return {field: len({row[field] for row in rows}) for field in KEY_FIELDS}


def summarize(studies, rows_by_study, studies_after):
    """Validate metadata and return counts without emitting any linkage key.

    The case_id field is the canonical PDC case identifier, not a submitter
    label. It must retain the same project context throughout the audit.
    Repeated aliquots across studies are allowed only with identical mapping
    and flags; duplicate aliquots inside a study are rejected. Pooled,
    non-reference aliquots remain in counts and are explicitly flagged.
    """
    validate_studies(studies)
    validate_studies(studies_after)
    require(studies == studies_after)
    require(isinstance(rows_by_study, dict) and set(rows_by_study) == set(STUDY_IDS))

    case_projects, sample_cases, aliquot_mappings = {}, {}, {}
    non_reference_cases, aggregates = {}, {}
    for study_id in STUDY_IDS:
        rows = rows_by_study[study_id]
        require(isinstance(rows, list) and bool(rows))
        seen_aliquots = set()
        non_reference = []
        for row in rows:
            require(isinstance(row, dict) and set(row) == ROW_FIELDS)
            require(all(nonempty_text(row[field]) for field in KEY_FIELDS))
            require(nonempty_text(row["project_name"]))
            require(row["aliquot_is_ref"] in ("Yes", "No"))
            require(row["pool"] in ("Yes", "No"))
            case, sample, aliquot = (row[field] for field in KEY_FIELDS)
            project = row["project_name"]
            require(aliquot not in seen_aliquots)
            seen_aliquots.add(aliquot)

            require(case not in case_projects or case_projects[case] == project)
            case_projects[case] = project
            sample_mapping = (case, project)
            require(sample not in sample_cases or sample_cases[sample] == sample_mapping)
            sample_cases[sample] = sample_mapping
            aliquot_mapping = (sample, case, project, row["aliquot_is_ref"], row["pool"])
            require(aliquot not in aliquot_mappings or aliquot_mappings[aliquot] == aliquot_mapping)
            aliquot_mappings[aliquot] = aliquot_mapping
            if row["aliquot_is_ref"] == "No":
                non_reference.append(row)

        all_counts = unique_counts(rows)
        require(all_counts["case_id"] == studies[study_id]["cases_count"])
        require(all_counts["aliquot_id"] == studies[study_id]["aliquots_count"])
        non_reference_cases[study_id] = {row["case_id"] for row in non_reference}
        aggregates[study_id] = {
            # Public study identifiers pin the queried release; these are not
            # patient, sample, or aliquot identifiers.
            "pdc_study_id": study_id,
            "study_id": studies[study_id]["study_id"],
            "study_version": studies[study_id]["versions"][0]["number"],
            "rows": len(rows),
            "reference_rows": len(rows) - len(non_reference),
            "non_reference_rows": len(non_reference),
            "pooled_non_reference_rows": sum(row["pool"] == "Yes" for row in non_reference),
            "unique_counts": {
                "all": all_counts,
                "non_reference": unique_counts(non_reference),
            },
        }

    overlap = []
    for a, b in combinations(STUDY_IDS, 2):
        a_cases, b_cases = non_reference_cases[a], non_reference_cases[b]
        overlap.append({
            "a": a,
            "b": b,
            "shared_non_reference_cases": len(a_cases & b_cases),
            "a_no_overlap_observed_cases": len(a_cases - b_cases),
            "b_no_overlap_observed_cases": len(b_cases - a_cases),
        })
    return {"studies": aggregates, "overlap": overlap}


def fetch_response(query, variables):
    """Fetch selected metadata in memory; never echo response/error bodies."""
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT, data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        require(response.geturl() == ENDPOINT)
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    require(len(raw) <= MAX_RESPONSE_BYTES)

    def invalid_constant(_value):
        raise AuditError(FAILURE_MESSAGE)

    result = json.loads(raw, parse_constant=invalid_constant)
    require(isinstance(result, dict) and not result.get("errors"))
    require(isinstance(result.get("data"), dict))
    return result


def study_from_response(response):
    require(isinstance(response, dict) and not response.get("errors"))
    data = response.get("data")
    require(isinstance(data, dict) and set(data) == {"getPaginatedUIStudy"})
    page = data["getPaginatedUIStudy"]
    require(isinstance(page, dict) and set(page) == {"total", "uiStudies"})
    # PDC currently returns total=null; one exact matching row is checked below.
    rows = page["uiStudies"]
    require(isinstance(rows, list) and len(rows) == 1)
    return rows[0]


def biospecimens_from_response(response):
    require(isinstance(response, dict) and not response.get("errors"))
    data = response.get("data")
    require(isinstance(data, dict) and set(data) == {"uiBiospecimenPerStudy"})
    rows = data["uiBiospecimenPerStudy"]
    require(isinstance(rows, list))
    return rows


def run_audit():
    before, after, biospecimens, provenance = {}, {}, {}, {}
    for study_id in STUDY_IDS:
        response = fetch_response(STUDY_QUERY, {"id": study_id})
        before[study_id] = study_from_response(response)
        provenance[study_id] = {"study_before_sha256": canonical_sha256(response)}
    validate_studies(before)

    for study_id in STUDY_IDS:
        response = fetch_response(BIOSPECIMEN_QUERY, {"id": before[study_id]["study_id"]})
        biospecimens[study_id] = biospecimens_from_response(response)
        provenance[study_id]["biospecimen_response_sha256"] = canonical_sha256(response)

    # Re-read every study after all linkage queries to detect release/count drift.
    for study_id in STUDY_IDS:
        response = fetch_response(STUDY_QUERY, {"id": study_id})
        after[study_id] = study_from_response(response)
        provenance[study_id]["study_after_sha256"] = canonical_sha256(response)

    result = summarize(before, biospecimens, after)
    result.update({
        "schema_version": 1,
        "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "endpoint": ENDPOINT,
        "study_version": EXPECTED_VERSION,
        "query_sha256": {
            "study": hashlib.sha256(STUDY_QUERY.encode("utf-8")).hexdigest(),
            "biospecimen": hashlib.sha256(BIOSPECIMEN_QUERY.encode("utf-8")).hexdigest(),
        },
        "response_sha256": provenance,
        "interpretation": (
            "Exact PDC case_id overlap among non-reference rows only. "
            "No overlap observed does not establish patient independence. "
            "Pooled non-reference rows are retained. Counts do not establish "
            "the paper's eligible analysis population. Response hashes identify "
            "received content, not patient independence."
        ),
    })
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Read released version-1 PDC metadata for PDC000360/358/362 in memory "
            "and print aggregate JSON. No patient identifiers or raw rows are "
            "written. This does not establish patient independence."
        ),
    )
    parser.parse_args(argv)
    try:
        result = run_audit()
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    except Exception:
        # Never include remote error text, exception repr, or a traceback: those
        # can contain row values. Nothing is printed until the complete audit passes.
        print(FAILURE_MESSAGE, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
