#!/usr/bin/env python3
"""Offline agreement check for the 2026-11-13 ovarian trial landscape.

Replays two readers on the frozen pages. Registration counts are not efficacy
and not treatment guidance.
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
from tools import trial_landscape_v2_export as export_reader
from tools import trial_landscape_v2_recompute as recompute_reader

DOC = ROOT / "docs/trial-landscape-v2-2026-11-13.md"
CERTIFICATE = RESULT / "certificate.json"
SUMS = RESULT / "SHA256SUMS"
BEGIN = "<!-- BEGIN GENERATED TRIAL LANDSCAPE V2 -->"
END = "<!-- END GENERATED TRIAL LANDSCAPE V2 -->"
PINNED_CODE = (
    "protocols/trial-landscape-keywords-v2.json",
    "tools/trial_landscape_v2_export.py",
    "tools/trial_landscape_v2_recompute.py",
    "results/trial-landscape-v2-2026-11-13/verify.py",
)
ARCHIVE_AS_FETCHED_SHA256 = (
    "73bb1e758985afc2762c9c1045d3cbba4ec9610ca9ada1b60dde94fa22c6cd41"
)
EMAIL_ADDRESS = re.compile(
    r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
    r"(?![A-Za-z0-9.-])"
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def render(result):
    lines = [
        f"total_studies: {result['total_studies']}",
        f"api_total_count: {result['api_total_count']}",
        f"api_version: {result['api_version']}",
        f"data_timestamp: {result['data_timestamp']}",
        f"page_count: {len(result['page_meta'])}",
        f"archive_as_fetched_sha256: {ARCHIVE_AS_FETCHED_SHA256}",
        f"archive_sha256: {result['archive_sha256']}",
        f"same_query_recruiting_total: {result['same_query_recruiting_total']}",
        f"corpus_recruiting: {result['corpus_recruiting']}",
        f"prior_total_studies: {result['prior_total_studies']}",
        f"aggregate_recruiting_delta: {result['aggregate_recruiting_delta']}",
        f"nct_level_diff: {result['diff']['nct_level_diff']}",
        f"diff_reason: {result['diff']['reason']}",
        f"new_nct_ids: {json.dumps(result['diff']['new_nct_ids'])}",
        f"removed_nct_ids: {json.dumps(result['diff']['removed_nct_ids'])}",
        f"status_changes: {json.dumps(result['diff']['status_changes'])}",
        f"any_target_class: {result['any_target_class']}",
        f"no_target_class: {result['no_target_class']}",
        f"efficacy_evidence: {result['efficacy_evidence']}",
        f"nct_status_count: {result['nct_status_count']}",
        f"nct_status_sha256: {result['nct_status_sha256']}",
    ]
    for key, value in sorted(result["status_counts"].items()):
        lines.append(f"status: {key} {value}")
    for key, value in sorted(result["phase_counts"].items()):
        lines.append(f"phase: {key} {value}")
    for key, value in sorted(result["intervention_type_counts"].items()):
        lines.append(f"intervention_type: {key} {value}")
    for key, value in sorted(result["class_counts"].items()):
        lines.append(f"class: {key} {value}")
    for key, value in sorted(result["missing_text_fields"].items()):
        lines.append(f"missing_text: {key} {value}")
    return "\n".join(lines)


def marked(text):
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("Generated count markers are missing or duplicated.")
    return text.split(BEGIN, 1)[1].split(END, 1)[0].strip("\n")


def resolve_sum_path(name):
    if name.startswith(("protocols/", "tools/", "results/", "registries/")):
        return ROOT / name
    return RESULT / name


def check_no_contact_emails():
    for path in sorted((RESULT / "snapshot").glob("studies-page-*.json")):
        text = path.read_text(encoding="utf-8")
        if EMAIL_ADDRESS.search(text):
            raise ValueError(f"Contact email remains in {path.name}.")


def check_redaction_metadata(manifest, certificate):
    for key in ("redaction_rule", "archive_as_fetched_sha256", "email_redactions"):
        if manifest.get(key) != certificate.get(key):
            raise ValueError(f"Manifest and certificate disagree on {key}.")
    if manifest["archive_as_fetched_sha256"] != ARCHIVE_AS_FETCHED_SHA256:
        raise ValueError("Pinned as-fetched archive hash differs.")
    for entry in manifest["email_redactions"]:
        if set(entry) != {"field", "nct_id"}:
            raise ValueError("Malformed email_redactions entry.")


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
    required = {"manifest.json"}
    for item in manifest["files"]:
        required.add(item["path"])
    required.add("certificate.json")
    if not required <= seen:
        raise ValueError("SHA256SUMS does not cover the manifest and certificate.")
    return manifest


def main():
    exported = export_reader.derive(RESULT)
    recomputed = recompute_reader.derive(RESULT)
    if exported["checker"] == recomputed["checker"]:
        raise ValueError("Checkers did not keep independent labels.")
    if export_reader.comparable(exported) != recompute_reader.comparable(recomputed):
        raise ValueError("Export and recompute checkers disagree.")
    result = export_reader.comparable(exported)
    if sum(result["status_counts"].values()) != result["total_studies"]:
        raise ValueError("Status counts do not sum to the cohort.")
    if sum(result["phase_counts"].values()) != result["total_studies"]:
        raise ValueError("Phase counts do not sum to the cohort.")
    if result["any_target_class"] + result["no_target_class"] != result["total_studies"]:
        raise ValueError("Target-class partition does not sum to the cohort.")
    if result["efficacy_evidence"] != "none":
        raise ValueError("Efficacy field is not the required negative.")
    if result["diff"]["nct_level_diff"] != "not_reconstructable":
        raise ValueError("Prior snapshot unexpectedly exposed NCT identifiers.")
    if result["diff"]["new_nct_ids"] is not None or result["diff"]["status_changes"] is not None:
        raise ValueError("A named NCT diff was produced without prior identifiers.")
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    if certificate["counts"]["total_studies"] != result["total_studies"]:
        raise ValueError("Certificate cohort differs from the checkers.")
    for key in ("status_counts", "phase_counts", "intervention_type_counts", "class_counts",
                "missing_text_fields"):
        if certificate["counts"][key] != result[key]:
            raise ValueError(f"Certificate {key} differs from the checkers.")
    comparison = certificate["comparison_to_2026_11_05"]
    if comparison["same_query_recruiting_total"] != result["same_query_recruiting_total"]:
        raise ValueError("Certificate recruiting total differs.")
    if comparison["corpus_recruiting"] != result["corpus_recruiting"]:
        raise ValueError("Certificate corpus recruiting count differs.")
    if comparison["prior_total_studies"] != result["prior_total_studies"]:
        raise ValueError("Certificate prior total differs.")
    if comparison["aggregate_recruiting_delta"] != result["aggregate_recruiting_delta"]:
        raise ValueError("Certificate recruiting delta differs.")
    if comparison["diff"] != result["diff"]:
        raise ValueError("Certificate identifier diff differs.")
    if certificate["archive_as_fetched_sha256"] != ARCHIVE_AS_FETCHED_SHA256:
        raise ValueError("Certificate as-fetched archive hash differs.")
    if certificate["archive_sha256"] != result["archive_sha256"]:
        raise ValueError("Certificate archive hash differs.")
    if certificate["nct_status_sha256"] != result["nct_status_sha256"]:
        raise ValueError("Certificate identifier digest differs.")
    if certificate["efficacy_evidence"] != "none" or certificate["clinical_guidance"] != "none":
        raise ValueError("Certificate does not keep the non-guidance labels.")
    spec_hash = sha256((ROOT / "protocols/trial-landscape-keywords-v2.json").read_bytes())
    if certificate["specification"]["sha256"] != spec_hash:
        raise ValueError("Certificate specification hash differs.")
    for path in PINNED_CODE:
        if certificate["implementation_sha256"][path] != sha256((ROOT / path).read_bytes()):
            raise ValueError(f"Implementation hash differs for {path}.")
    check_no_contact_emails()
    manifest = check_sums()
    check_redaction_metadata(manifest, certificate)
    if manifest["archive_as_fetched_sha256"] != ARCHIVE_AS_FETCHED_SHA256:
        raise ValueError("Manifest as-fetched archive hash differs.")
    if manifest["archive_sha256"] != result["archive_sha256"]:
        raise ValueError("Manifest archive hash differs.")
    for page in certificate["provenance"]["pages"]:
        meta = next((item for item in result["page_meta"] if item["path"] == page["path"]), None)
        if meta is None or page["sha256"] != meta["sha256"]:
            raise ValueError(f"Certificate page hash differs for {page['path']}.")
    doc = DOC.read_text(encoding="utf-8")
    if marked(doc) != render(result):
        raise ValueError("Report count block differs from the checkers.")
    required_phrases = (
        "not clinical advice",
        "not a treatment recommendation",
        "not efficacy",
        "not reconstructable",
        f"{result['total_studies']} unique interventional studies",
        f"returned {result['same_query_recruiting_total']}",
        f"recorded {result['prior_total_studies']}",
    )
    lowered = doc.lower()
    for phrase in required_phrases:
        if phrase.lower() not in lowered:
            raise ValueError(f"Report is missing the required phrase: {phrase}")
    print("PASS: two offline readers agree on the frozen pages, certificate, hashes and report block.")
    print("This check does not establish efficacy, eligibility, or which studies changed since 2026-11-05.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
