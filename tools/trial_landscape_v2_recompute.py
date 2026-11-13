#!/usr/bin/env python3
"""Recompute the ovarian-trial landscape from the same frozen pages.

This reader does not import the export checker. Agreement is the check.
Counts are of registered studies, not of benefit or a recommended regimen.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "protocols/trial-landscape-keywords-v2.json"
CHECKER = "recompute"
IDENTIFIER = re.compile(r"NCT[0-9]{8}\Z")
IDENTIFIER_SCAN = re.compile(r"NCT[0-9]{8}")
STATUS_TOKEN = re.compile(r"[A-Z0-9_]+\Z")


class RecountError(ValueError):
    """Frozen-page or specification failure. The message stays generic."""


def demand(ok, message):
    if not ok:
        raise RecountError(message)


def strict_object(pairs):
    obj = {}
    for key, value in pairs:
        demand(key not in obj, "Duplicate JSON object key.")
        obj[key] = value
    return obj


def reject_nonfinite(value):
    raise RecountError("Nonfinite JSON value.")


def read_json(raw):
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    try:
        return json.loads(raw, object_pairs_hook=strict_object, parse_constant=reject_nonfinite)
    except (ValueError, UnicodeError, RecursionError):
        raise RecountError("Invalid JSON document.") from None


def load_spec(path=SPEC_PATH):
    spec = read_json(Path(path).read_bytes())
    demand(spec.get("schema_version") == 1, "Invalid keyword specification.")
    demand(spec.get("missing_phase_label") == "NOT_REPORTED", "Invalid missing-phase label.")
    demand(spec.get("missing_intervention_label") == "NOT_REPORTED",
           "Invalid missing-intervention label.")
    return spec


def fold_text(text):
    demand(isinstance(text, str), "Text field has invalid type.")
    folded = unicodedata.normalize("NFKC", text).casefold().replace("α", "alpha")
    folded = "".join(
        " " if char == "-" or unicodedata.category(char) == "Pd" else char
        for char in folded
    )
    return " ".join(folded.split())


def phrase_table(spec):
    table = {}
    for bucket, phrases in spec["classes"].items():
        table[bucket] = [
            re.compile(r"(?<!\w)" + re.escape(fold_text(phrase)) + r"(?!\w)")
            for phrase in phrases
        ]
    return table


def phase_label(raw_phases, spec):
    if raw_phases is None or raw_phases == []:
        return spec["missing_phase_label"]
    demand(isinstance(raw_phases, list), "Phase field has invalid type.")
    order = spec["phase_order"]
    demand(all(isinstance(item, str) and item in order for item in raw_phases),
           "Unknown or malformed phase value.")
    demand(len(set(raw_phases)) == len(raw_phases), "Duplicate phase value.")
    demand("NA" not in raw_phases or len(raw_phases) == 1, "NA mixed with real phases.")
    return "+".join(item for item in order if item in set(raw_phases))


def optional_module(protocol, key):
    module = protocol.get(key, {})
    if module is None:
        return {}
    demand(isinstance(module, dict), "Protocol module has invalid type.")
    return module


def string_list(value, message):
    if value is None:
        return []
    demand(isinstance(value, list) and all(isinstance(item, str) for item in value), message)
    return list(value)


def study_to_record(study, spec):
    demand(isinstance(study, dict), "Study has invalid type.")
    protocol = study.get("protocolSection")
    demand(isinstance(protocol, dict), "Missing protocol section.")
    identity = optional_module(protocol, "identificationModule")
    nct = identity.get("nctId")
    demand(isinstance(nct, str) and IDENTIFIER.fullmatch(nct),
           "Missing or malformed registry identifier.")
    status = optional_module(protocol, "statusModule").get("overallStatus")
    demand(isinstance(status, str) and STATUS_TOKEN.fullmatch(status), "Malformed overall status.")
    design = optional_module(protocol, "designModule")
    demand(design.get("studyType") == "INTERVENTIONAL", "Study type violates the fixed query.")
    summary = optional_module(protocol, "descriptionModule").get("briefSummary")
    condition_module = optional_module(protocol, "conditionsModule")
    arm_module = optional_module(protocol, "armsInterventionsModule")
    raw_arms = arm_module.get("interventions", [])
    if raw_arms is None:
        raw_arms = []
    demand(isinstance(raw_arms, list), "Intervention list has invalid type.")
    agent_names = []
    agent_types = []
    for arm in raw_arms:
        demand(isinstance(arm, dict), "Intervention has invalid type.")
        agent = arm.get("name")
        kind = arm.get("type")
        if agent is not None:
            demand(isinstance(agent, str), "Intervention name has invalid type.")
            agent_names.append(agent)
        if kind is not None:
            demand(isinstance(kind, str) and STATUS_TOKEN.fullmatch(kind),
                   "Intervention type has invalid type.")
            agent_types.append(kind)
    title = identity.get("briefTitle") or ""
    official = identity.get("officialTitle") or ""
    synopsis = summary or ""
    for value in (title, official, synopsis):
        demand(isinstance(value, str), "Text field has invalid type.")
    return {
        "nct_id": nct,
        "overall_status": status,
        "phase": phase_label(design.get("phases"), spec),
        "intervention_types": sorted(set(agent_types)),
        "text": {
            "brief_title": title,
            "official_title": official,
            "brief_summary": synopsis,
            "conditions": string_list(condition_module.get("conditions"),
                                      "Condition list has invalid type."),
            "keywords": string_list(condition_module.get("keywords"),
                                    "Keyword list has invalid type."),
            "intervention_names": agent_names,
        },
    }


def normalized_pieces(record, spec):
    pieces = []
    text = record["text"]
    for field in spec["text_fields"]:
        raw = text[field]
        if field in spec["array_text_fields"]:
            pieces.extend(fold_text(item) for item in raw)
        else:
            pieces.append(fold_text(raw))
    return pieces


def matched_classes(record, spec, table=None):
    table = phrase_table(spec) if table is None else table
    pieces = normalized_pieces(record, spec)
    hits = set()
    for bucket, expressions in table.items():
        for expression in expressions:
            if any(expression.search(piece) for piece in pieces):
                hits.add(bucket)
                break
    name_hit = "fralpha_adc_names" in hits
    context_hit = "folr1_language" in hits and "fralpha_adc_context" in hits
    if name_hit or context_hit:
        hits.add("fralpha_adc")
    return {name for name in spec["reported_classes"] if name in hits}


def tally(records, spec):
    table = phrase_table(spec)
    seen = []
    by_status = {}
    by_phase = {}
    by_type = {}
    by_class = {name: 0 for name in spec["reported_classes"]}
    blank_fields = {name: 0 for name in spec["text_fields"]}
    no_intervention = 0
    in_target = 0
    roster = []
    for record in records:
        nct = record["nct_id"]
        demand(nct not in seen, "Duplicate registry identifier.")
        seen.append(nct)
        by_status[record["overall_status"]] = by_status.get(record["overall_status"], 0) + 1
        by_phase[record["phase"]] = by_phase.get(record["phase"], 0) + 1
        kinds = record["intervention_types"]
        if kinds:
            for kind in kinds:
                by_type[kind] = by_type.get(kind, 0) + 1
        else:
            no_intervention += 1
            missing = spec["missing_intervention_label"]
            by_type[missing] = by_type.get(missing, 0) + 1
        labels = matched_classes(record, spec, table)
        for label in labels:
            by_class[label] += 1
        if any(label in spec["target_classes"] for label in labels):
            in_target += 1
        pieces = normalized_pieces(record, spec)
        # Pieces follow text_fields order, expanding arrays. Recount blanks from the record.
        for field in spec["text_fields"]:
            raw = record["text"][field]
            values = raw if field in spec["array_text_fields"] else [raw]
            if not any(fold_text(value) for value in values):
                blank_fields[field] += 1
        roster.append((nct, record["overall_status"]))
        del pieces
    total = len(seen)
    demand(sum(by_status.values()) == total, "Status counts do not sum to the cohort.")
    demand(sum(by_phase.values()) == total, "Phase counts do not sum to the cohort.")
    roster.sort()
    return {
        "total_studies": total,
        "status_counts": by_status,
        "phase_counts": by_phase,
        "intervention_type_counts": by_type,
        "studies_without_intervention": no_intervention,
        "class_counts": by_class,
        "any_target_class": in_target,
        "no_target_class": total - in_target,
        "missing_text_fields": blank_fields,
        "nct_status": [{"nct_id": nct, "overall_status": status} for nct, status in roster],
    }


def diff_against_prior(prior_text, nct_status):
    mentioned = sorted(set(IDENTIFIER_SCAN.findall(prior_text)))
    if not mentioned:
        return {
            "nct_level_diff": "not_reconstructable",
            "reason": "prior_artifact_has_no_nct_identifiers",
            "new_nct_ids": None,
            "removed_nct_ids": None,
            "status_changes": None,
        }
    current_ids = {row["nct_id"] for row in nct_status}
    prior_ids = set(mentioned)
    return {
        "nct_level_diff": "identifier_overlap_only",
        "reason": "prior_artifact_lists_identifiers_without_a_status_map",
        "new_nct_ids": sorted(current_ids - prior_ids),
        "removed_nct_ids": sorted(prior_ids - current_ids),
        "status_changes": None,
    }


def iter_page_files(result_dir):
    folder = Path(result_dir) / "snapshot"
    pages = sorted(folder.glob("studies-page-*.json"))
    demand(pages, "Frozen study pages are missing.")
    return pages


def ingest_pages(result_dir, spec):
    collected = []
    declared = None
    meta = []
    pages = iter_page_files(result_dir)
    last = len(pages) - 1
    for index, path in enumerate(pages):
        body = path.read_bytes()
        page = read_json(body)
        studies = page.get("studies")
        demand(isinstance(studies, list), "Registry page lacks a studies list.")
        if index == 0 or "totalCount" in page:
            total = page.get("totalCount")
            demand(type(total) is int and not isinstance(total, bool) and total >= 0,
                   "Invalid registry totalCount.")
            declared = total if declared is None else declared
            demand(total == declared, "Registry totalCount changed across frozen pages.")
        token = page.get("nextPageToken")
        demand(token is None or (isinstance(token, str) and token.strip()),
               "Malformed frozen pagination token.")
        demand((token is not None and bool(token.strip() if isinstance(token, str) else token)) == (index != last),
               "Frozen page chain does not match tokens.")
        for study in studies:
            collected.append(study_to_record(study, spec))
        meta.append({
            "path": f"snapshot/{path.name}",
            "sha256": hashlib.sha256(body).hexdigest(),
            "study_count": len(studies),
            "bytes": len(body),
        })
    demand(declared is not None and len(collected) == declared,
           "Frozen page count differs from registry totalCount.")
    archive = hashlib.sha256(b"".join(path.read_bytes() for path in pages)).hexdigest()
    return collected, declared, meta, archive


def read_version(path):
    body = Path(path).read_bytes()
    document = read_json(body)
    demand(set(document) == {"apiVersion", "dataTimestamp"}, "Invalid API version document.")
    demand(isinstance(document["apiVersion"], str) and document["apiVersion"], "Invalid API version.")
    demand(isinstance(document["dataTimestamp"], str) and document["dataTimestamp"],
           "Invalid API data timestamp.")
    return document, hashlib.sha256(body).hexdigest()


def derive(result_dir, spec=None, prior_path=None):
    spec = load_spec() if spec is None else spec
    result_dir = Path(result_dir)
    if prior_path is None:
        prior_path = ROOT / spec["prior_snapshot"]["path"]
    records, api_total, page_meta, archive = ingest_pages(result_dir, spec)
    counts = tally(records, spec)
    opened, opened_hash = read_version(result_dir / "snapshot/version-before.json")
    closed, closed_hash = read_version(result_dir / "snapshot/version-after.json")
    demand(opened == closed, "Frozen API version documents disagree.")
    comparison_body = (result_dir / "snapshot/recruiting-query.json").read_bytes()
    comparison = read_json(comparison_body)
    comparison_total = comparison.get("totalCount")
    demand(type(comparison_total) is int and not isinstance(comparison_total, bool)
           and comparison_total >= 0, "Invalid recruiting-query totalCount.")
    prior_text = Path(prior_path).read_text(encoding="utf-8")
    prior = read_json(prior_text)
    prior_total = prior.get("counts", {}).get("total_studies")
    demand(type(prior_total) is int and not isinstance(prior_total, bool),
           "Prior certificate has no cohort total.")
    diff = diff_against_prior(prior_text, counts["nct_status"])
    digest = hashlib.sha256(json.dumps(
        counts["nct_status"], sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()
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
        "corpus_recruiting": counts["status_counts"].get("RECRUITING", 0),
        "same_query_recruiting_total": comparison_total,
        "prior_total_studies": prior_total,
        "aggregate_recruiting_delta": comparison_total - prior_total,
        "diff": diff,
        "api_version": opened["apiVersion"],
        "data_timestamp": opened["dataTimestamp"],
        "version_before_sha256": opened_hash,
        "version_after_sha256": closed_hash,
        "comparison_sha256": hashlib.sha256(comparison_body).hexdigest(),
        "page_meta": page_meta,
        "archive_sha256": archive,
        "nct_status_sha256": digest,
        "nct_status_count": len(counts["nct_status"]),
        "efficacy_evidence": "none",
    }


def comparable(result):
    payload = json.loads(json.dumps(result))
    payload.pop("checker", None)
    return payload


def main():
    print(json.dumps(comparable(derive(ROOT / "results/trial-landscape-v2-2026-11-13")),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
