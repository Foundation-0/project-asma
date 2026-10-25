#!/usr/bin/env python3
"""Inspect pinned public supplements in memory; emit aggregate provenance only.

Requires permission for the scoped clinical-metadata inspection. It never writes
workbooks, patient identifiers, labels, prediction rows, or linkage maps to disk.
This audits published membership; it does not rerun models or establish that
patients were excluded from upstream preprocessing or assay alignment.
"""

import argparse
import collections
import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from xml.etree import ElementTree as ET


BASE = "https://pmc-oa-opendata.s3.us-east-1.amazonaws.com/PMC10414761.1/"
SOURCES = {
    "clinical": {
        "filename": "NIHMS1918576-supplement-MMC1.xlsx",
        "bytes": 41194360,
        "md5": "0255243711b1af3a3fab503d9abc725b",
        "sha256": "6e46fa0cb3023173a3643e95ce0360c44cfabb0ed737e9a05f70473dad552340",
    },
    "panel_and_scores": {
        "filename": "NIHMS1918576-supplement-MMC4.xlsx",
        "bytes": 591065,
        "md5": "7ea4df8e1008cd19aa67442fe6ea3556",
        "sha256": "f318ed9d2fac341097a8b1be3e034753f6d427bdeeb0cd2b92eb715cadadb6ab",
    },
}
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
LABEL_COLUMN = "Data Label 2 <data set>_<TMTplex>_<sample source>_<patient ID>_sample ID>"
CRITICAL = ["Patient ID", "Sample ID", "Neo-adjuvant", "Tumor response",
            "Tumor Location Group", "Sample type"]
SCORE_COHORT = {
    "FFPE_pred_scores": "FFPE_Discovery_clinical",
    "FFPE_valid_pred_scores": "FFPE_Pilot_clinical",
    "Frozen_nonoverlap_pred_scores": "Frozen_clinical",
    "Frozen_overlap_pred_scores": "Frozen_clinical",
}
ALLOWED_LOCATIONS = {"OM", "OV", "PT", "NA", "GI", "Mix", "LN", "UT", "GIOM"}
FAILURE_MESSAGE = "ERROR: published-cohort audit failed; no row-level details emitted."


class AuditError(ValueError):
    """A failed contract; messages must never include record values."""


def require(condition, message):
    if not condition:
        raise AuditError(message)


def identity(value):
    return isinstance(value, str) and bool(value) and value == value.strip() and value != "NA"


def classify_clinical(records):
    """Separate explicit clinical-NA rows without guessing identity or flags."""
    require(isinstance(records, list) and bool(records), "Missing clinical rows")
    biological, missing = [], []
    for row in records:
        require(isinstance(row, dict) and set(CRITICAL + [LABEL_COLUMN]) <= set(row),
                "Missing critical clinical field")
        require(isinstance(row[LABEL_COLUMN], str) and bool(row[LABEL_COLUMN]) and
                row[LABEL_COLUMN] == row[LABEL_COLUMN].strip(), "Missing exact clinical label")
        require(row["Tumor response"] in ("sensitive", "refractory", "NA"),
                "Unexpected response value")
        require(row["Neo-adjuvant"] in ("yes", "no", "NA"),
                "Unexpected raw neoadjuvant value")
        require(isinstance(row["Tumor Location Group"], str) and
                row["Tumor Location Group"] in ALLOWED_LOCATIONS,
                "Unexpected raw tumor-location group")
        if row["Tumor response"] == "NA":
            require(all(row[field] == "NA" for field in
                        ["Patient ID", "Sample ID", "Neo-adjuvant", "Sample type"]),
                    "Unresolved NA-row classification")
            missing.append(row)
        else:
            require(all(identity(row[field]) for field in
                        ["Patient ID", "Sample ID", "Sample type", LABEL_COLUMN]),
                    "Missing response-labelled critical field")
            require(row["Neo-adjuvant"] in ("yes", "no"), "Unresolved neoadjuvant annotation")
            biological.append(row)
    return biological, missing


def collapse_replicates(records):
    """Collapse Sample ID replicates only when every critical field agrees."""
    biological, missing = classify_clinical(records)
    require(not missing, "Clinical NA rows cannot enter replicate collapse")
    groups = collections.defaultdict(list)
    for row in biological:
        groups[row["Sample ID"]].append(row)
    require(all(all(len({row[field] for row in group}) == 1 for field in CRITICAL)
                for group in groups.values()), "Conflicting clinical fields across technical replicates")
    return [group[0] for group in groups.values()]


def eligible_samples(records):
    """Reconstruct the literal published membership rule, not clinical eligibility.

    Location NA remains unresolved and is retained by the literal != Mix test.
    The caller must verify equality to published score membership and report
    this missingness; NA is never interpreted as affirmative nonmixed tissue.
    """
    biological, missing = classify_clinical(records)
    require(not missing, "Clinical NA rows cannot enter eligibility")
    return [row for row in biological
            if row["Neo-adjuvant"] == "no" and row["Tumor Location Group"] != "Mix"]


def patient_keys(records):
    require(all(identity(row.get("Patient ID")) for row in records), "Missing patient key")
    return {row["Patient ID"] for row in records}


def sample_keys(records):
    require(all(identity(row.get("Sample ID")) for row in records), "Missing sample key")
    return {row["Sample ID"] for row in records}


def patient_overlap(records, reference):
    selected, compared = patient_keys(records), patient_keys(reference)
    return {"patient_keys_shared": len(selected & compared),
            "patient_keys_not_observed": len(selected - compared)}


def join_score_membership(keys, clinical_records):
    """Join exact published sample labels to one clinical row, without scores."""
    require(isinstance(keys, list) and bool(keys) and all(identity(key) for key in keys),
            "Missing score sample key")
    require(len(keys) == len(set(keys)), "Duplicate score sample key")
    classify_clinical(clinical_records)
    index = collections.defaultdict(list)
    for row in clinical_records:
        index[row[LABEL_COLUMN]].append(row)
    require(all(len(index[key]) == 1 for key in keys),
            "Incomplete or ambiguous exact score-to-clinical join")
    joined = [index[key][0] for key in keys]
    require(all(row["Tumor response"] != "NA" for row in joined), "Score key joins a clinical NA row")
    require(len(patient_keys(joined)) == len(keys) and len(sample_keys(joined)) == len(keys),
            "Published score records repeat a patient or sample key")
    return joined


class Workbook:
    def __init__(self, source):
        with urllib.request.urlopen(BASE + source["filename"], timeout=60) as response:
            body = response.read(source["bytes"] + 1)
        require(len(body) == source["bytes"], "Unexpected workbook size")
        for algorithm in ("md5", "sha256"):
            require(hashlib.new(algorithm, body).hexdigest() == source[algorithm],
                    "Workbook checksum mismatch")
        self.archive = zipfile.ZipFile(io.BytesIO(body))
        self.strings = ["".join(n.text or "" for n in item.findall(".//s:t", NS))
                        for item in self.xml("xl/sharedStrings.xml")]
        relationships = {item.get("Id"): item.get("Target")
                         for item in self.xml("xl/_rels/workbook.xml.rels")}
        self.sheets = {}
        for item in self.xml("xl/workbook.xml").findall("s:sheets/s:sheet", NS):
            key = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            target = relationships[item.get(key)]
            self.sheets[item.get("name")] = (target.lstrip("/") if target.startswith("/")
                                             else "xl/" + target)

    def xml(self, name):
        require(self.archive.getinfo(name).file_size <= 128 * 1024 * 1024,
                "Unexpected XML member size")
        data = self.archive.read(name)
        # Spreadsheet parts never carry a document type declaration. Reject one
        # before parsing so entity declarations cannot reach the XML parser.
        lowered = data.lower()
        require(b"<!doctype" not in lowered and b"<!entity" not in lowered,
                "Unexpected XML declaration in workbook part")
        return ET.fromstring(data)

    def value(self, cell):
        value = cell.find("s:v", NS)
        if cell.get("t") == "s":
            return self.strings[int(value.text)] if value is not None else ""
        if cell.get("t") == "inlineStr":
            return "".join(n.text or "" for n in cell.findall(".//s:t", NS))
        return value.text if value is not None else ""

    def rows(self, sheet, columns=None):
        # Headers remain available for schema checks. Score-sheet calls select
        # only column A after the header; numeric prediction values are unused.
        result = []
        for index, row in enumerate(self.xml(self.sheets[sheet]).findall("s:sheetData/s:row", NS)):
            result.append({re.sub(r"[0-9]", "", cell.get("r")): self.value(cell) for cell in row
                           if index == 0 or columns is None or
                           re.sub(r"[0-9]", "", cell.get("r")) in columns})
        return result


def counts(records, field):
    return dict(sorted(collections.Counter(row[field] for row in records).items()))


def run_audit():
    clinical_book = Workbook(SOURCES["clinical"])
    score_book = Workbook(SOURCES["panel_and_scores"])
    clinical, unique, eligible, cohort_summary = {}, {}, {}, {}
    for sheet in dict.fromkeys(SCORE_COHORT.values()):
        rows = clinical_book.rows(sheet)
        header = rows[0]
        require(len(set(header.values())) == len(header), "Duplicate clinical header")
        records = [{header[col]: value for col, value in row.items()} for row in rows[1:]]
        clinical[sheet] = records
        biological, missing = classify_clinical(records)
        unique[sheet] = collapse_replicates(biological)
        expected_unique = {"FFPE_Discovery_clinical": 158, "Frozen_clinical": 64, "FFPE_Pilot_clinical": 20}[sheet]
        require(len(unique[sheet]) == expected_unique, "Unexpected unique response-labelled sample count")
        require(len({row["Patient ID"] for row in unique[sheet]}) == expected_unique,
                "Response-labelled samples do not map one-to-one to patient keys in this cohort")
        eligible[sheet] = eligible_samples(unique[sheet])
        cohort_summary[sheet] = {
            "worksheet_rows_excluding_header": len(records),
            "rows_with_explicit_NA_clinical_fields": len(missing),
            "response_labelled_measurement_rows": len(biological),
            "unique_sample_keys": len(unique[sheet]),
            "unique_patient_keys": len({row["Patient ID"] for row in unique[sheet]}),
            "technical_replicate_critical_field_conflicts": 0,
            "class_counts": counts(unique[sheet], "Tumor response"),
            "neoadjuvant_yes": sum(row["Neo-adjuvant"] == "yes" for row in unique[sheet]),
            "location_group_Mix": sum(row["Tumor Location Group"] == "Mix" for row in unique[sheet]),
            "unique_sample_location_group_NA": sum(row["Tumor Location Group"] == "NA"
                                                     for row in unique[sheet]),
            "neoadjuvant_yes_and_Mix": sum(row["Neo-adjuvant"] == "yes" and
                                           row["Tumor Location Group"] == "Mix" for row in unique[sheet]),
            "eligible_samples": len(eligible[sheet]),
            "retained_score_cohort_location_group_NA": sum(row["Tumor Location Group"] == "NA"
                                                            for row in eligible[sheet]),
            "eligible_class_counts": counts(eligible[sheet], "Tumor response"),
        }

    panel = score_book.rows("64_protein_predictors")
    require(panel[0].get("A") == "Proteins", "Unexpected protein-panel header")
    symbols = [row.get("A", "") for row in panel[1:]]
    require(len(symbols) == 64 and len(set(symbols)) == 64 and
            all(symbol.strip() and "\n" not in symbol and "\r" not in symbol for symbol in symbols),
            "Invalid protein-panel identifiers")
    panel_hash = hashlib.sha256(("\n".join(symbols) + "\n").encode("utf-8")).hexdigest()
    require(panel_hash == "77329920b86dacaffc6778ed7e7c6b827683beed1aad7f2229b8bafe2f535144",
            "Protein-panel canonical checksum mismatch")

    joined, score_summary = {}, {}
    for sheet, cohort in SCORE_COHORT.items():
        rows = score_book.rows(sheet, columns={"A"})
        require(rows[0].get("A") == "Samples" and rows[0].get("B") == "Pred.scores",
                "Unexpected score-sheet header")
        keys = [row.get("A", "") for row in rows[1:]]
        joined[sheet] = join_score_membership(keys, clinical[cohort])
        expected_rows = {"FFPE_pred_scores": 135, "FFPE_valid_pred_scores": 20,
                         "Frozen_nonoverlap_pred_scores": 34, "Frozen_overlap_pred_scores": 27}[sheet]
        require(len(keys) == expected_rows, "Unexpected published score denominator")
        score_summary[sheet] = {
            "score_rows": len(keys), "duplicate_score_keys": 0,
            "unmatched_score_keys": 0, "ambiguous_score_keys": 0,
            "unique_patient_keys": len({row["Patient ID"] for row in joined[sheet]}),
            "unique_sample_keys": len({row["Sample ID"] for row in joined[sheet]}),
            "class_counts": counts(joined[sheet], "Tumor response"),
        }

    for sheet in ("FFPE_pred_scores", "FFPE_valid_pred_scores"):
        require(sample_keys(joined[sheet]) == sample_keys(eligible[SCORE_COHORT[sheet]]),
                "Published score membership differs from literal clinical rule")
    frozen_score_rows = joined["Frozen_nonoverlap_pred_scores"] + joined["Frozen_overlap_pred_scores"]
    require(sample_keys(frozen_score_rows) == sample_keys(eligible["Frozen_clinical"]),
            "Combined frozen score membership differs from literal clinical rule")
    require(len(frozen_score_rows) == len(sample_keys(frozen_score_rows)), "Frozen score subsets overlap")
    discovery_all = patient_keys(unique["FFPE_Discovery_clinical"])
    discovery_eligible = patient_keys(joined["FFPE_pred_scores"])
    frozen_all = patient_keys(unique["Frozen_clinical"])
    for sheet in ("Frozen_nonoverlap_pred_scores", "Frozen_overlap_pred_scores"):
        all_overlap = patient_overlap(joined[sheet], unique["FFPE_Discovery_clinical"])
        eligible_overlap = patient_overlap(joined[sheet], joined["FFPE_pred_scores"])
        score_summary[sheet].update({
            "patient_keys_shared_with_all_discovery": all_overlap["patient_keys_shared"],
            "patient_keys_shared_with_eligible_discovery": eligible_overlap["patient_keys_shared"],
            "patient_keys_not_observed_in_all_discovery": all_overlap["patient_keys_not_observed"],
            "patient_keys_not_observed_in_eligible_discovery": eligible_overlap["patient_keys_not_observed"],
        })
    output = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_files": {key: dict(value, url=BASE + value["filename"]) for key, value in SOURCES.items()},
        "scope": "In-memory published metadata/prediction-membership audit; no model execution or performance calculation",
        "exact_score_join": "score Samples equals clinical Data Label 2; no string normalization or name-based inference",
        "patient_linkage": "exact equality of explicit clinical Patient ID fields",
        "membership_reconstruction_rule": (
            "Fields named eligible describe reconstructed published score membership: "
            "literal Neo-adjuvant == no and Tumor Location Group != Mix, followed by "
            "exact equality to the published score sample sets. Literal location NA "
            "is retained by this comparison and reported as unresolved; it does not "
            "establish nonmixed tissue or verified clinical eligibility."
        ),
        "replicate_conflict_fields": CRITICAL,
        "clinical_cohorts": cohort_summary,
        "panel": {"sheet": "64_protein_predictors", "range": "A2:A65", "count": 64,
                  "canonical_sha256": panel_hash, "canonical_encoding": "UTF-8 source order, LF after every symbol"},
        "published_score_subsets": score_summary,
        "eligibility_membership_checks_passed": True,
        "frozen_patient_linkage": {
            "all_frozen": len(frozen_all),
            "all_frozen_shared_with_all_discovery": len(frozen_all & discovery_all),
            "all_frozen_not_observed_in_all_discovery": len(frozen_all - discovery_all),
            "eligible_frozen": len(patient_keys(frozen_score_rows)),
            "eligible_frozen_shared_with_eligible_discovery": len(patient_keys(frozen_score_rows) & discovery_eligible),
            "eligible_frozen_not_observed_in_eligible_discovery": len(patient_keys(frozen_score_rows) - discovery_eligible),
            "eligible_frozen_not_observed_in_all_discovery": len(patient_keys(frozen_score_rows) - discovery_all),
        },
        "limitations": ["No Patient ID overlap observed is not proof of exclusion from upstream preprocessing or alignment.",
                        "Location-group NA remains unresolved even when retained in reconstructed published score membership.",
                        "Published scores were inspected for membership only; models and reported performance were not reproduced.",
                        "Supplement file numbers are not assumed to equal article table numbers.",
                        "No patient-level records, identifiers, scores, or protein symbols are emitted or persisted."],
    }
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=(
        "Audit pinned public supplement membership in memory and print aggregate JSON. "
        "Requires authorization for clinical-metadata inspection; does not run models, "
        "calculate performance, or emit patient identifiers."
    ))
    parser.parse_args(argv)
    try:
        output = run_audit()
        print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
    except Exception:
        print(FAILURE_MESSAGE, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
