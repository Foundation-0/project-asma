#!/usr/bin/env python3
"""Bounded public-catalog audit; full sequences/responses remain in memory.

Checks two existing IEDB leads, not study spectra or patient observations.
Live mode checks three explicitly named public protein entries locally. Optional
--search also queries UniProt peptide search for each peptide/mode. Default mode checks the retained
aggregate certificate only; it cannot replay unretained source bytes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import ssl
import urllib.error
import urllib.request
import time
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries/cdr2l-sequence-audit-2026-11-06.json"
ASSAYS = {11610866: ("33858848", 445, 464), 18456218: ("33968037", 432, 446)}
FIELDS = ("elution_id,structure_id,linear_sequence,curated_source_antigen,"
          "pubmed_id,mhc_class,mhc_allele_name,mhc_allele_resolution,"
          "mhc_allele_evidence,qualitative_measure,parent_source_antigen_iri")
IEDB_URL = ("https://query-api.iedb.org/mhc_search?elution_id=in.(11610866,18456218)"
            "&mhc_class=eq.II&select=" + FIELDS + "&limit=3")
SEARCH = "https://peptidesearch.uniprot.org/asyncrest/"
ACCESSION = re.compile(r"[A-Z0-9]+(?:-[1-9][0-9]*)?\Z")
AMINO = re.compile(r"[ACDEFGHIKLMNPQRSTVWY]+\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def positions(sequence: str, peptide: str, il_equivalent: bool = False) -> list[int]:
    """All overlapping, 1-based exact matches; optional symmetric I/L collapse."""
    require(bool(AMINO.fullmatch(sequence)) and bool(AMINO.fullmatch(peptide)),
            "Noncanonical or empty amino-acid input")
    if il_equivalent:
        sequence, peptide = sequence.replace("I", "L"), peptide.replace("I", "L")
    return [i + 1 for i in range(len(sequence) - len(peptide) + 1)
            if sequence[i:i + len(peptide)] == peptide]


def request(url, *, form=None):
    """Verified TLS, bounded in-memory response, no automatic redirects."""
    require(url.startswith("https://"), "HTTPS required")
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    context = ssl.create_default_context()
    # python.org macOS builds may lack CA installation; add the OS trust bundle.
    system_ca = Path("/etc/ssl/cert.pem")
    if system_ca.is_file():
        context.load_verify_locations(cafile=str(system_ca))
    opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=context))
    query = urllib.request.Request(url, data=urlencode(form).encode() if form is not None else None)
    for attempt in range(3):
        try:
            response = opener.open(query, timeout=15)
            break
        except urllib.error.HTTPError as error:
            response = error
            break
        except (TimeoutError, urllib.error.URLError):
            if attempt == 2:
                raise
            time.sleep(1)
    with response:
        raw = response.read(5_000_001)
        require(len(raw) <= 5_000_000, "Catalog response exceeds bound")
        return response.status, {k.lower(): v for k, v in response.headers.items()}, raw


def get_json(url):
    status, headers, raw = request(url)
    require(status == 200, "Catalog request failed")
    return json.loads(raw), headers


def validate_assays(rows):
    require(isinstance(rows, list) and len(rows) == 2, "Unexpected assay count")
    require({r["elution_id"] for r in rows} == set(ASSAYS), "Assay set changed")
    for row in rows:
        pmid, start, end = ASSAYS[row["elution_id"]]
        source = row["curated_source_antigen"]
        require(row["pubmed_id"] == pmid and row["mhc_class"] == "II"
                and row["parent_source_antigen_iri"] == "UNIPROT:Q86X02"
                and row["qualitative_measure"] == "Positive", "Assay identity changed")
        require(source["accession"] == "Q86X02.2"
                and source["starting_position"] == start and source["ending_position"] == end,
                "Curated source coordinates changed")
        require(bool(AMINO.fullmatch(row["linear_sequence"]))
                and len(row["linear_sequence"]) == end - start + 1, "Peptide length mismatch")
    return sorted(rows, key=lambda r: r["elution_id"])


def peptide_search(peptide, il_equivalent):
    form = {"peps": peptide, "taxIds": "9606"}
    if il_equivalent:
        form["lEQi"] = "on"
    status, headers, _ = request(SEARCH, form=form)
    require(status == 202, "Peptide search not accepted")
    location = headers.get("location", "")
    require(bool(re.fullmatch(r"https?://peptidesearch\.uniprot\.org/asyncrest/jobs/PM[0-9A-Za-z]+", location)),
            "Unexpected peptide-search location")
    # The service advertises HTTP; always use HTTPS for the same host/path.
    job = location.replace("http://", "https://", 1)
    for _ in range(30):
        status, _, raw = request(job)
        if status == 200:
            break
        require(status in (202, 303), "Peptide search failed")
        time.sleep(2)
    else:
        raise ValueError("Peptide search timed out")
    accessions = raw.decode().strip().split(",") if raw.strip() else []
    require(accessions and len(accessions) <= 50 and len(accessions) == len(set(accessions))
            and all(ACCESSION.fullmatch(x) for x in accessions), "Invalid or excessive match set")
    status, _, raw_params = request(job + "/parameters")
    require(status == 200, "Search parameters unavailable")
    parameters = dict(line.split(":", 1) for line in raw_params.decode().strip().splitlines())
    require(parameters == {"QueryPetides": peptide, "TaxonIds": "9606",
                           "lEqi": "Y" if il_equivalent else "N", "swissProtOnly": "N"},
            "Search did not honor submitted scope")
    return {"job_url": job, "il_equivalent": il_equivalent,
            "taxon_id": 9606, "reviewed_only": False, "accessions": sorted(accessions)}


def live_audit(search_database=False):
    rows, _ = get_json(IEDB_URL)
    rows = validate_assays(rows)
    proteins = {}
    releases = set()

    def protein(accession):
        if accession not in proteins:
            # This audit requires complete entries, not guessed isoform JSON routes.
            require("-" not in accession, "Isoform result requires separate adjudication")
            item, headers = get_json(f"https://rest.uniprot.org/uniprotkb/{accession}.json")
            require(item["primaryAccession"] == accession and item["organism"]["taxonId"] == 9606,
                    "Protein identity mismatch")
            require(bool(AMINO.fullmatch(item["sequence"]["value"])), "Unsupported protein sequence")
            proteins[accession] = item
            releases.add(headers.get("x-uniprot-release", "not supplied"))
        return proteins[accession]

    leads = []
    for row in rows:
        sequence = row["linear_sequence"]
        searches = [peptide_search(sequence, mode) for mode in (False, True)] if search_database else []
        accession_set = {a for search in searches for a in search["accessions"]} | {"Q01850", "Q86X02", "A0ACI8RKQ2"}
        matches = {}
        for accession in sorted(accession_set):
            source_seq = protein(accession)["sequence"]["value"]
            matches[accession] = {"exact_positions": positions(source_seq, sequence),
                                  "il_positions": positions(source_seq, sequence, True)}
        require(matches["Q86X02"]["exact_positions"] == [ASSAYS[row["elution_id"]][1]],
                "Canonical CDR2L coordinate check failed")
        for search in searches:
            key = "il_positions" if search["il_equivalent"] else "exact_positions"
            require(all(matches[a][key] for a in search["accessions"]), "Search/local sequence mismatch")
            require("Q86X02" in search["accessions"], "Expected parent absent from search")
            require(set(search["accessions"]) == {a for a, m in matches.items() if m[key]},
                    "Search omitted a locally verified candidate")
        require(not searches or set(searches[0]["accessions"]) <= set(searches[1]["accessions"]),
                "I/L search omitted an exact hit")
        leads.append({"assay_id": row["elution_id"], "epitope_id": row["structure_id"],
                      "pubmed_id": row["pubmed_id"], "peptide_sha256": sha(sequence.encode()),
                      "peptide_length": len(sequence), "curated_start": ASSAYS[row["elution_id"]][1],
                      "curated_end": ASSAYS[row["elution_id"]][2],
                      "mhc_allele_name": row["mhc_allele_name"],
                      "mhc_allele_resolution": row["mhc_allele_resolution"],
                      "mhc_allele_evidence": row["mhc_allele_evidence"],
                      "searches": searches, "local_matches": matches})
    summaries = {}
    for accession, item in sorted(proteins.items()):
        sequence = item["sequence"]["value"]
        summaries[accession] = {"entry_type": item["entryType"], "taxon_id": 9606,
            "genes": sorted(g["geneName"]["value"] for g in item.get("genes", []) if "geneName" in g),
            "length": len(sequence), "sequence_sha256": sha(sequence.encode()),
            "entry_version": item["entryAudit"]["entryVersion"],
            "sequence_version": item["entryAudit"]["sequenceVersion"]}
    report = {"schema_version": 1, "accessed_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_scope": "catalog_sequence_adjudication_not_spectrum_or_receptor_validation",
        "iedb_query": IEDB_URL, "uniprot_rest_releases": sorted(releases),
        "search_database_release": "not exposed by peptide-search service",
        "database_search_status": "completed" if search_database else "not_run",
        "candidate_universe": ["A0ACI8RKQ2", "Q01850", "Q86X02"],
        "script_sha256": sha(Path(__file__).read_bytes()), "leads": leads, "proteins": summaries,
        "limits": ["Remote search completeness and database synchronization are not independently proved.",
                   "No spectra, allele-specific binding, receptor recognition or injury were assessed.",
                   "Full sequences and response bodies were not retained; offline checks are internal consistency only."]}
    report["certificate_sha256"] = sha(canonical(report))
    check_report(report)
    return report


def check_report(report):
    require(report["schema_version"] == 1 and report["claim_scope"] ==
            "catalog_sequence_adjudication_not_spectrum_or_receptor_validation", "Wrong report scope")
    payload = {k: v for k, v in report.items() if k != "certificate_sha256"}
    require(sha(canonical(payload)) == report["certificate_sha256"], "Certificate digest mismatch")
    require(report["script_sha256"] == sha(Path(__file__).read_bytes()), "Implementation changed")
    require({r["assay_id"] for r in report["leads"]} == set(ASSAYS)
            and len(report["leads"]) == 2, "Wrong lead set")
    require(report["candidate_universe"] == ["A0ACI8RKQ2", "Q01850", "Q86X02"], "Candidate universe changed")
    require(set(report["candidate_universe"]) <= set(report["proteins"]), "Missing explicit comparator")
    for accession, protein in report["proteins"].items():
        require(bool(ACCESSION.fullmatch(accession)) and protein["taxon_id"] == 9606,
                "Invalid protein identity")
        require(all(type(protein[k]) is int and protein[k] > 0
                    for k in ("length", "entry_version", "sequence_version")), "Invalid protein metadata")
        require(bool(re.fullmatch(r"[0-9a-f]{64}", protein["sequence_sha256"])), "Invalid sequence digest")
    for row in report["leads"]:
        pmid, start, end = ASSAYS[row["assay_id"]]
        require((row["pubmed_id"], row["curated_start"], row["curated_end"]) == (pmid, start, end),
                "Retained assay identity changed")
        require(row["local_matches"]["Q86X02"]["exact_positions"] == [start],
                "Canonical source mismatch")
        require({"Q01850", "Q86X02"} <= set(row["local_matches"]), "Missing comparator result")
        for accession, matches in row["local_matches"].items():
            require(accession in report["proteins"], "Missing matched protein")
            for key in ("exact_positions", "il_positions"):
                sites = matches[key]
                require(isinstance(sites, list) and all(type(i) is int and i > 0
                        and i + row["peptide_length"] - 1 <= report["proteins"][accession]["length"]
                        for i in sites) and sites == sorted(set(sites)), "Invalid match coordinates")
            require(set(matches["exact_positions"]) <= set(matches["il_positions"]),
                    "I/L matching lost exact positions")
        require(row["peptide_length"] == row["curated_end"] - row["curated_start"] + 1,
                "Invalid peptide coordinates")
        require(report["database_search_status"] in {"completed", "not_run"}, "Invalid search status")
        if report["database_search_status"] == "completed":
            require(len(row["searches"]) == 2 and {s["il_equivalent"] for s in row["searches"]} == {False, True},
                    "Missing sequence sensitivity search")
        else:
            require(row["searches"] == [] and set(row["local_matches"]) == set(report["candidate_universe"]),
                    "Unperformed search has results or candidate drift")
        for search in row["searches"]:
            key = "il_positions" if search["il_equivalent"] else "exact_positions"
            require(search["taxon_id"] == 9606 and search["reviewed_only"] is False, "Wrong search universe")
            require("Q86X02" in search["accessions"] and len(search["accessions"]) == len(set(search["accessions"])),
                    "Invalid retained search hits")
            require(set(search["accessions"]) == {a for a, m in row["local_matches"].items() if m[key]},
                    "Retained search/local mismatch")
            for accession in search["accessions"]:
                require(accession in report["proteins"] and row["local_matches"][accession][key],
                        "Unverified search hit")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Run bounded public catalog requests")
    parser.add_argument("--search", action="store_true", help="Also request live database searches; fails if service unavailable")
    parser.add_argument("--output", type=Path, default=RESULT)
    args = parser.parse_args()
    if args.live:
        report = live_audit(args.search)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        report = json.loads(args.output.read_text())
        check_report(report)
    print(json.dumps({"assays": len(report["leads"]), "protein_entries": len(report["proteins"]),
                      "mode": "live catalog audit" if args.live else "offline internal consistency",
                      "clinical_or_mechanistic_validation": False}, sort_keys=True))


if __name__ == "__main__":
    main()
