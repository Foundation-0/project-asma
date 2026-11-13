#!/usr/bin/env python3
"""Inspect one public Atlas peptide page; retain aggregates, never donor rows.

Only the named IEDB lead is queried. Portal display metadata are not an
independently validated spectrum, peptide-specific HLA restriction or mechanism.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
import json
from pathlib import Path
import re

try:
    from .audit_cdr2l_sequences import IEDB_URL, canonical, get_json, request, require, sha, validate_assays
except ImportError:
    from audit_cdr2l_sequences import IEDB_URL, canonical, get_json, request, require, sha, validate_assays

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries/cdr2l-atlas-source-2026-11-06.json"
HEADERS = ["Donor", "Tissue", "HLA-DP", "HLA-DQ", "HLA-DRB1", "HLA-DRB3", "HLA-DRB4", "HLA-DRB5", "q-value"]
NO_PREDICTION = "There is no prediction based binding evidence for this peptide."
PEPTIDE_SHA256 = "e3f89dacbd675e575f9977b37d1377a7a1cd538fa7faf942fe22c64c588b19ea"
LIMITS = ["Source-association rows are not independent confirmations.",
          "Portal display metadata do not verify spectra, cell type or peptide-specific allotype.",
          "No donor IDs, sample linkage keys, genotypes or full page bodies are retained.",
          "Offline validation checks internal consistency, not unretained live source truth."]


class Tables(HTMLParser):
    """Minimal table reader; cells exist only in process memory."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.text = [], []
        self.table = self.row = self.cell = None
        self.heading = None
        self.headings, self.links = [], []
        self.ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "template"}:
            self.ignored += 1
        if self.ignored:
            return
        if tag == "h3":
            self.heading = []
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))
        if tag == "table":
            require(self.table is None, "Nested table unsupported")
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in {"th", "td"} and self.row is not None:
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append(" ")

    def handle_data(self, data):
        if self.ignored:
            return
        self.text.append(data)
        if self.heading is not None:
            self.heading.append(data)
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if self.ignored:
            if tag in {"script", "style", "template"}:
                self.ignored -= 1
            return
        if tag == "h3" and self.heading is not None:
            self.headings.append(re.sub(r"\s+", "", "".join(self.heading)))
            self.heading = None
        if tag in {"th", "td"} and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def summarize_portal(html):
    parser = Tables()
    parser.feed(html)
    require(parser.table is None and parser.row is None, "Incomplete table markup")
    candidates = [table for table in parser.tables if table and table[0] == HEADERS]
    require(len(candidates) == 1, "Expected one explicitly identified HLA-II table")
    rows = candidates[0][1:]
    require(0 < len(rows) <= 2000, "Unexpected source-association row count")
    counts, quality = Counter(), []
    for row in rows:
        require(len(row) == len(HEADERS), "HLA-II table column drift")
        # Deliberately never export donor or genotype columns.
        tissue, q = row[1], row[-1]
        require(bool(re.fullmatch(r"[A-Za-z][A-Za-z /()-]{0,80}", tissue)), "Unsupported tissue label")
        try:
            number = Decimal(q)
        except InvalidOperation:
            raise ValueError("Invalid displayed quality value") from None
        require(number.is_finite() and 0 <= number <= 1, "Invalid displayed quality value")
        counts[tissue] += 1
        quality.append(number)
    return {"hla_class": "II", "source_association_rows": len(rows),
            "tissue_counts": dict(sorted(counts.items())),
            "displayed_q_value_range": [str(min(quality)), str(max(quality))],
            "quality_label": "q-value", "quality_granularity": "unresolved",
            "explicit_no_binding_prediction": NO_PREDICTION in " ".join(" ".join(parser.text).split()),
            "peptide_specific_allotype": "unresolved", "original_spectrum_validation": "not_performed"}


def validate_page_identity(html, sequence):
    identity = Tables()
    identity.feed(html)
    require(identity.headings.count(sequence) == 1
            and [h for h in identity.headings if re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWY]{7,}", h)] == [sequence]
            and "http://www.iedb.org/epitope/1281771" in identity.links
            and "/protein/Q86X02" in identity.links,
            "Portal peptide/source identity mismatch")

def live_audit():
    rows, _ = get_json(IEDB_URL)
    row = next(r for r in validate_assays(rows) if r["elution_id"] == 11610866)
    require(row["structure_id"] == 1281771, "Epitope identity changed")
    url = "https://hla-ligand-atlas.org/peptide/" + row["linear_sequence"]
    status, _, raw = request(url)
    require(status == 200 and len(raw) <= 2_000_000, "Atlas request failed or exceeded bound")
    html = raw.decode("utf-8")
    validate_page_identity(html, row["linear_sequence"])
    report = {"schema_version": 1, "assay_id": 11610866, "epitope_id": 1281771,
              "pubmed_id": "33858848", "accessed_at_utc": datetime.now(timezone.utc).isoformat(),
              "source": "https://hla-ligand-atlas.org/", "page_route": "/peptide/{IEDB linear_sequence}",
              "peptide_sha256": sha(row["linear_sequence"].encode()),
              "portal_response_sha256_snapshot": sha(raw),
              "script_sha256": sha(Path(__file__).read_bytes()),
              "shared_request_module_sha256": sha((ROOT / "tools/audit_cdr2l_sequences.py").read_bytes()),
              "summary": summarize_portal(html),
              "limits": LIMITS}
    report["certificate_sha256"] = sha(canonical(report))
    check_report(report)
    return report


def check_report(report):
    require(set(report) == {"schema_version", "assay_id", "epitope_id", "pubmed_id", "accessed_at_utc",
                           "source", "page_route", "peptide_sha256", "portal_response_sha256_snapshot",
                           "script_sha256", "shared_request_module_sha256", "summary", "limits", "certificate_sha256"},
            "Unexpected retained field")
    require((report["schema_version"], report["assay_id"], report["epitope_id"], report["pubmed_id"])
            == (1, 11610866, 1281771, "33858848"), "Wrong source identity")
    require(sha(canonical({k: v for k, v in report.items() if k != "certificate_sha256"}))
            == report["certificate_sha256"], "Certificate digest changed")
    require(report["script_sha256"] == sha(Path(__file__).read_bytes())
            and report["shared_request_module_sha256"] == sha((ROOT / "tools/audit_cdr2l_sequences.py").read_bytes()),
            "Implementation changed")
    require(report["source"] == "https://hla-ligand-atlas.org/"
            and report["page_route"] == "/peptide/{IEDB linear_sequence}"
            and report["peptide_sha256"] == PEPTIDE_SHA256 and report["limits"] == LIMITS,
            "Source/retention contract changed")
    require(all(re.fullmatch(r"[0-9a-f]{64}", report[k]) for k in
                ("peptide_sha256", "portal_response_sha256_snapshot", "script_sha256",
                 "shared_request_module_sha256", "certificate_sha256")), "Invalid digest format")
    require(datetime.fromisoformat(report["accessed_at_utc"]).tzinfo is not None, "Missing timestamp timezone")
    summary = report["summary"]
    require(set(summary) == {"hla_class", "source_association_rows", "tissue_counts", "displayed_q_value_range",
                            "quality_label", "quality_granularity", "explicit_no_binding_prediction",
                            "peptide_specific_allotype", "original_spectrum_validation"}, "Unexpected retained field")
    require(summary["hla_class"] == "II" and summary["quality_label"] == "q-value"
            and summary["quality_granularity"] == "unresolved"
            and summary["peptide_specific_allotype"] == "unresolved"
            and summary["original_spectrum_validation"] == "not_performed", "Unsupported evidence promotion")
    require(type(summary["explicit_no_binding_prediction"]) is bool, "Invalid prediction status")
    require(type(summary["source_association_rows"]) is int and summary["source_association_rows"] > 0
            and all(type(n) is int and n > 0 and re.fullmatch(r"[A-Za-z][A-Za-z /()-]{0,80}", name)
                    for name, n in summary["tissue_counts"].items())
            and sum(summary["tissue_counts"].values()) == summary["source_association_rows"], "Invalid aggregate counts")
    require(len(summary["displayed_q_value_range"]) == 2, "Invalid quality range")
    low, high = map(Decimal, summary["displayed_q_value_range"])
    require(low.is_finite() and high.is_finite() and 0 <= low <= high <= 1, "Invalid quality range")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", type=Path, default=RESULT)
    args = parser.parse_args()
    if args.live:
        report = live_audit()
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        report = json.loads(args.output.read_text())
        check_report(report)
    print(json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
