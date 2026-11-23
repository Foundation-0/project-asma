#!/usr/bin/env python3
"""Export counts from the frozen ClinicalTrials.gov v2 ovarian-trial pages.

Reads pinned response bytes and the keyword map. Does not fetch.
Registration counts are not efficacy and not treatment guidance.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "protocols/trial-landscape-keywords-v2.json"
CHECKER = "export"
NCT_ID = re.compile(r"NCT[0-9]{8}\Z")
NCT_SCAN = re.compile(r"NCT[0-9]{8}")
TOKEN = re.compile(r"[A-Z0-9_]+\Z")


class CountError(ValueError):
    """Fixed failure for a malformed frozen page or spec. No row text."""


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
    except (ValueError, UnicodeError, RecursionError):
        raise CountError("Invalid JSON document.") from None


def load_spec(path=SPEC_PATH):
    spec = decode_json(Path(path).read_bytes())
    _require(spec.get("schema_version") == 1, "Invalid keyword specification.")
    _require(spec.get("phase_order") == [
        "EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4", "NA"
    ], "Invalid phase specification.")
    return spec


def normalize_text(text):
    _require(isinstance(text, str), "Text field has invalid type.")
    text = unicodedata.normalize("NFKC", text).casefold().replace("α", "alpha")
    text = "".join(" " if character == "-" or unicodedata.category(character) == "Pd" else character
                   for character in text)
    return " ".join(text.split())


def _patterns(spec):
    compiled = {}
    for name, terms in spec["classes"].items():
        compiled[name] = [
            re.compile(r"(?<!\w)" + re.escape(normalize_text(term)) + r"(?!\w)")
            for term in terms
        ]
    return compiled


def canonical_phase(phases, spec):
    if phases is None:
        return spec["missing_phase_label"]
    _require(isinstance(phases, list), "Phase field has invalid type.")
    if phases == []:
        return spec["missing_phase_label"]
    allowed = spec["phase_order"]
    _require(all(isinstance(item, str) and item in allowed for item in phases),
             "Unknown or malformed phase value.")
    _require(len(set(phases)) == len(phases), "Duplicate phase value.")
    _require("NA" not in phases or len(phases) == 1, "NA mixed with real phases.")
    return "+".join(item for item in allowed if item in phases)


def _strings(value, label):
    if value is None:
        return []
    _require(isinstance(value, list), label)
    _require(all(isinstance(item, str) for item in value), label)
    return value


def _module(protocol, name):
    value = protocol.get(name)
    if value is None:
        return {}
    _require(isinstance(value, dict), "Protocol module has invalid type.")
    return value


def record_from_study(study, spec):
    """Reduce one API study object to the fields the classifier reads."""
    _require(isinstance(study, dict), "Study has invalid type.")
    protocol = study.get("protocolSection")
    _require(isinstance(protocol, dict), "Missing protocol section.")
    identification = _module(protocol, "identificationModule")
    identifier = identification.get("nctId")
    _require(isinstance(identifier, str) and NCT_ID.fullmatch(identifier),
             "Missing or malformed registry identifier.")
    status = _module(protocol, "statusModule").get("overallStatus")
    _require(isinstance(status, str) and TOKEN.fullmatch(status), "Malformed overall status.")
    design = _module(protocol, "designModule")
    _require(design.get("studyType") == "INTERVENTIONAL", "Study type violates the fixed query.")
    description = _module(protocol, "descriptionModule")
    conditions = _module(protocol, "conditionsModule")
    raw_interventions = _module(protocol, "armsInterventionsModule").get("interventions")
    if raw_interventions is None:
        raw_interventions = []
    _require(isinstance(raw_interventions, list), "Intervention list has invalid type.")
    names = []
    types = []
    for item in raw_interventions:
        _require(isinstance(item, dict), "Intervention has invalid type.")
        if "name" in item and item["name"] is not None:
            _require(isinstance(item["name"], str), "Intervention name has invalid type.")
            names.append(item["name"])
        if "type" in item and item["type"] is not None:
            _require(isinstance(item["type"], str) and TOKEN.fullmatch(item["type"]),
                     "Intervention type has invalid type.")
            types.append(item["type"])
    title = identification.get("briefTitle")
    official = identification.get("officialTitle")
    summary = description.get("briefSummary")
    for label, value in (("brief title", title), ("official title", official), ("brief summary", summary)):
        _require(value is None or isinstance(value, str), f"{label} has invalid type.")
    return {
        "nct_id": identifier,
        "overall_status": status,
        "phase": canonical_phase(design.get("phases"), spec),
        "intervention_types": sorted(set(types)),
        "text": {
            "brief_title": title or "",
            "official_title": official or "",
            "brief_summary": summary or "",
            "conditions": _strings(conditions.get("conditions"), "Condition list has invalid type."),
            "keywords": _strings(conditions.get("keywords"), "Keyword list has invalid type."),
            "intervention_names": names,
        },
    }


def _blobs(record, spec):
    blobs = []
    for name in spec["text_fields"]:
        value = record["text"][name]
        items = value if name in spec["array_text_fields"] else [value]
        blobs.extend(normalize_text(item) for item in items)
    return blobs


def classes_for_record(record, spec, patterns=None):
    patterns = _patterns(spec) if patterns is None else patterns
    blobs = _blobs(record, spec)
    found = set()
    for name, expressions in patterns.items():
        if any(expression.search(blob) for blob in blobs for expression in expressions):
            found.add(name)
    adc = ("fralpha_adc_names" in found or (
        "folr1_language" in found and "fralpha_adc_context" in found
    ))
    if adc:
        found.add("fralpha_adc")
    return {name for name in spec["reported_classes"] if name in found}


def aggregate_records(records, spec):
    patterns = _patterns(spec)
    seen = set()
    status_counts = {}
    phase_counts = {}
    type_counts = {}
    class_counts = dict.fromkeys(spec["reported_classes"], 0)
    missing = dict.fromkeys(spec["text_fields"], 0)
    without_intervention = 0
    any_target = 0
    rows = []
    for record in records:
        identifier = record["nct_id"]
        _require(identifier not in seen, "Duplicate registry identifier.")
        seen.add(identifier)
        status_counts[record["overall_status"]] = status_counts.get(record["overall_status"], 0) + 1
        phase_counts[record["phase"]] = phase_counts.get(record["phase"], 0) + 1
        types = record["intervention_types"]
        if not types:
            without_intervention += 1
            label = spec["missing_intervention_label"]
            type_counts[label] = type_counts.get(label, 0) + 1
        else:
            for name in types:
                type_counts[name] = type_counts.get(name, 0) + 1
        matched = classes_for_record(record, spec, patterns)
        for name in matched:
            class_counts[name] += 1
        if matched.intersection(spec["target_classes"]):
            any_target += 1
        for name in spec["text_fields"]:
            value = record["text"][name]
            items = value if name in spec["array_text_fields"] else [value]
            if not any(normalize_text(item) for item in items):
                missing[name] += 1
        rows.append({"nct_id": identifier, "overall_status": record["overall_status"]})
    total = len(seen)
    _require(sum(status_counts.values()) == total, "Status counts do not sum to the cohort.")
    _require(sum(phase_counts.values()) == total, "Phase counts do not sum to the cohort.")
    rows.sort(key=lambda item: item["nct_id"])
    return {
        "total_studies": total,
        "status_counts": status_counts,
        "phase_counts": phase_counts,
        "intervention_type_counts": type_counts,
        "studies_without_intervention": without_intervention,
        "class_counts": class_counts,
        "any_target_class": any_target,
        "no_target_class": total - any_target,
        "missing_text_fields": missing,
        "nct_status": rows,
    }


def diff_against_prior(prior_text, nct_status):
    """Identifier diff only when the prior artifact actually lists NCT IDs."""
    found = sorted(set(NCT_SCAN.findall(prior_text)))
    current = {row["nct_id"]: row["overall_status"] for row in nct_status}
    if not found:
        return {
            "nct_level_diff": "not_reconstructable",
            "reason": "prior_artifact_has_no_nct_identifiers",
            "new_nct_ids": None,
            "removed_nct_ids": None,
            "status_changes": None,
        }
    prior_ids = set(found)
    new_ids = sorted(set(current) - prior_ids)
    removed_ids = sorted(prior_ids - set(current))
    return {
        "nct_level_diff": "identifier_overlap_only",
        "reason": "prior_artifact_lists_identifiers_without_a_status_map",
        "new_nct_ids": new_ids,
        "removed_nct_ids": removed_ids,
        "status_changes": None,
    }


def _page_paths(result_dir):
    pages = sorted((result_dir / "snapshot").glob("studies-page-*.json"))
    _require(pages, "Frozen study pages are missing.")
    return pages


def load_pages(result_dir, spec):
    records = []
    expected = None
    page_meta = []
    paths = _page_paths(result_dir)
    for index, path in enumerate(paths):
        raw = path.read_bytes()
        page = decode_json(raw)
        studies = page.get("studies")
        _require(isinstance(studies, list), "Registry page lacks a studies list.")
        if index == 0 or "totalCount" in page:
            total = page.get("totalCount")
            _require(type(total) is int and total >= 0, "Invalid registry totalCount.")
            if expected is None:
                expected = total
            _require(total == expected, "Registry totalCount changed across frozen pages.")
        token = page.get("nextPageToken")
        _require(token is None or (isinstance(token, str) and token.strip()),
                 "Malformed frozen pagination token.")
        _require(bool(token) == (index < len(paths) - 1), "Frozen page chain does not match tokens.")
        for study in studies:
            records.append(record_from_study(study, spec))
        page_meta.append({
            "path": f"snapshot/{path.name}",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "study_count": len(studies),
            "bytes": len(raw),
        })
    _require(expected is not None and len(records) == expected,
             "Frozen page count differs from registry totalCount.")
    archive = hashlib.sha256(b"".join(path.read_bytes() for path in paths)).hexdigest()
    return records, expected, page_meta, archive


def _version(path):
    raw = path.read_bytes()
    payload = decode_json(raw)
    _require(set(payload) == {"apiVersion", "dataTimestamp"}, "Invalid API version document.")
    _require(isinstance(payload["apiVersion"], str) and payload["apiVersion"], "Invalid API version.")
    _require(isinstance(payload["dataTimestamp"], str) and payload["dataTimestamp"],
             "Invalid API data timestamp.")
    return payload, hashlib.sha256(raw).hexdigest()


def derive(result_dir, spec=None, prior_path=None):
    spec = load_spec() if spec is None else spec
    result_dir = Path(result_dir)
    prior_path = ROOT / spec["prior_snapshot"]["path"] if prior_path is None else Path(prior_path)
    records, api_total, page_meta, archive = load_pages(result_dir, spec)
    counts = aggregate_records(records, spec)
    before, before_hash = _version(result_dir / "snapshot/version-before.json")
    after, after_hash = _version(result_dir / "snapshot/version-after.json")
    _require(before == after, "Frozen API version documents disagree.")
    comparison_raw = (result_dir / "snapshot/recruiting-query.json").read_bytes()
    comparison = decode_json(comparison_raw)
    comparison_total = comparison.get("totalCount")
    _require(type(comparison_total) is int and comparison_total >= 0,
             "Invalid recruiting-query totalCount.")
    prior_text = prior_path.read_text(encoding="utf-8")
    prior = decode_json(prior_text)
    prior_total = prior.get("counts", {}).get("total_studies")
    _require(type(prior_total) is int, "Prior certificate has no cohort total.")
    diff = diff_against_prior(prior_text, counts["nct_status"])
    identifier_digest = hashlib.sha256(
        json.dumps(counts["nct_status"], sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    recruiting_in_corpus = counts["status_counts"].get("RECRUITING", 0)
    return {
        "checker": CHECKER,
        "total_studies": counts["total_studies"],
        "api_total_count": api_total,
        "status_counts": counts["status_counts"],
        "phase_counts": counts["phase_counts"],
        "intervention_type_counts": counts["intervention_type_counts"],
        "studies_without_intervention": counts["studies_without_intervention"],
        "class_counts": counts["class_counts"],
        "any_target_class": counts["any_target_class"],
        "no_target_class": counts["no_target_class"],
        "missing_text_fields": counts["missing_text_fields"],
        "corpus_recruiting": recruiting_in_corpus,
        "same_query_recruiting_total": comparison_total,
        "prior_total_studies": prior_total,
        "aggregate_recruiting_delta": comparison_total - prior_total,
        "diff": diff,
        "api_version": before["apiVersion"],
        "data_timestamp": before["dataTimestamp"],
        "version_before_sha256": before_hash,
        "version_after_sha256": after_hash,
        "comparison_sha256": hashlib.sha256(comparison_raw).hexdigest(),
        "page_meta": page_meta,
        "archive_sha256": archive,
        "nct_status_sha256": identifier_digest,
        "nct_status_count": len(counts["nct_status"]),
        "efficacy_evidence": "none",
    }


def comparable(result):
    copied = json.loads(json.dumps(result))
    copied.pop("checker", None)
    return copied


def main():
    result = derive(ROOT / "results/trial-landscape-v2-2026-11-13")
    print(json.dumps(comparable(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
