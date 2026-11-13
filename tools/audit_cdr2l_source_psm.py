#!/usr/bin/env python3
"""Bounded, memory-only inspection of three public cell-line mzIdentML results.

This reads original identification records, not raw spectra; it does not rerun
searches, estimate FDR, validate spectra, or assign an HLA allotype.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import ssl
import sys
import urllib.request
from urllib.parse import unquote, urlsplit
import xml.sax
from xml.sax.handler import ContentHandler, feature_external_ges, feature_external_pes

TARGET = "SQPEYKALFKEIFSR"
PROJECT = "PXD023044"
BASE = "https://ftp.pride.ebi.ac.uk/pride/data/archive/2021/05/PXD023044/"
FILES = (
    ("peptides_1_1_0_CII_r1.mzid.gz", 85957996, "7567a487a3d6f8e2bc2a725cf98de59914dfe457"),
    ("peptides_1_1_0_CII_r2.mzid.gz", 55563417, "3c50729db24b4660db5aa29a83f16b9682b85292"),
    ("peptides_1_1_0_CII_r3.mzid.gz", 85287597, "77acfe2d87f608859e47dbe249a6c594c224cad3"),
)
COMPRESSED_LIMIT = 90_000_000
TOTAL_LIMIT = 230_000_000
EXPANDED_LIMIT = 2_000_000_000


class SourceIntegrityError(ValueError):
    def __init__(self, metadata):
        super().__init__("pinned source size/SHA1 do not match the explicit byte-domain contract")
        self.metadata = metadata


def require(value, reason):
    if not value:
        raise ValueError(reason)


class CountedReader:
    def __init__(self, stream, limit):
        self.stream, self.limit, self.count = stream, limit, 0
        self.sha1, self.sha256 = hashlib.sha1(), hashlib.sha256()

    def read(self, n=-1):
        if n < 0:
            n = 65536
        data = self.stream.read(min(n, 65536))
        self.count += len(data)
        require(self.count <= self.limit, "compressed byte cap exceeded")
        self.sha1.update(data)
        self.sha256.update(data)
        return data


class IdentificationHandler(ContentHandler):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.stack = []
        self.root_seen = False
        self.root_closed = False
        self.peptide_ids, self.evidence_ids, self.result_ids = set(), set(), set()
        self.proteins, self.spectra, self.matched_peptides, self.evidence = {}, {}, {}, {}
        self.results, self.protocols = [], []
        self.peptide = self.result = self.item = self.protocol = None
        self.sequence = []
        self.current_spectra = None
        self.item_count = 0

    def startElement(self, name, attrs):
        name = name.split(":")[-1]
        a = dict(attrs)
        parent = self.stack[-1] if self.stack else None
        if not self.stack:
            require(name == "MzIdentML", "not an mzIdentML document")
            self.root_seen = True
        self.stack.append(name)
        if name == "DBSequence":
            require(a["id"] not in self.proteins, "duplicate protein identifier")
            self.proteins[a["id"]] = {k: a[k] for k in ("accession", "searchDatabase_ref") if k in a}
        elif name == "Peptide":
            require(a["id"] not in self.peptide_ids, "duplicate peptide identifier")
            self.peptide_ids.add(a["id"])
            self.peptide = {"id": a["id"], "modifications": []}
            self.sequence = []
        elif name in ("Modification", "SubstitutionModification") and self.peptide is not None:
            self.peptide["modifications"].append({"element": name, **a})
        elif name == "PeptideEvidence":
            require(a["id"] not in self.evidence_ids, "duplicate peptide-evidence identifier")
            self.evidence_ids.add(a["id"])
            if a["peptide_ref"] in self.matched_peptides:
                self.evidence[a["id"]] = a
        elif name == "SpectraData":
            require(a["id"] not in self.spectra, "duplicate spectra identifier")
            location = a.get("location", "")
            filename = unquote(urlsplit(location).path).replace("\\", "/").rsplit("/", 1)[-1]
            require(bool(filename), "spectra location has no filename")
            self.spectra[a["id"]] = {"id": a["id"], "file_name": filename,
                "source_location_sha256": hashlib.sha256(location.encode()).hexdigest()}
            self.current_spectra = self.spectra[a["id"]]
        elif name == "SpectrumIdentificationResult":
            require(a["id"] not in self.result_ids, "duplicate result identifier")
            self.result_ids.add(a["id"])
            self.result = {"attributes": a, "parameters": [], "items": []}
        elif name == "SpectrumIdentificationItem":
            self.item_count += 1
            self.item = ({"attributes": a, "parameters": [], "evidence_refs": []}
                         if a["peptide_ref"] in self.matched_peptides else None)
        elif name == "PeptideEvidenceRef" and self.item is not None:
            self.item["evidence_refs"].append(a["peptideEvidence_ref"])
        elif name == "SpectrumIdentificationProtocol":
            self.protocol = {"attributes": a, "threshold_parameters": []}
        elif name in ("cvParam", "userParam"):
            if self.current_spectra is not None and parent in ("SpectrumIDFormat", "FileFormat"):
                self.current_spectra.setdefault(parent, []).append(a)
            if self.item is not None and parent == "SpectrumIdentificationItem":
                self.item["parameters"].append(a)
            if self.result is not None and parent == "SpectrumIdentificationResult":
                self.result["parameters"].append(a)
            if self.protocol is not None and parent == "Threshold":
                self.protocol["threshold_parameters"].append(a)
            if self.peptide is not None and parent == "Modification":
                self.peptide["modifications"][-1].setdefault("parameters", []).append(a)

    def characters(self, content):
        if self.stack and self.stack[-1] == "PeptideSequence":
            self.sequence.append(content)
            require(sum(map(len, self.sequence)) <= 10000, "peptide text exceeds bound")

    def endElement(self, name):
        name = name.split(":")[-1]
        if name == "SpectraData":
            self.current_spectra = None
        elif name == "Peptide":
            if "".join(self.sequence).strip() == self.target:
                self.matched_peptides[self.peptide["id"]] = self.peptide
            self.peptide = None
            self.sequence = []
        elif name == "SpectrumIdentificationItem":
            if self.item is not None:
                require(self.result is not None, "item outside identification result")
                self.result["items"].append(self.item)
            self.item = None
        elif name == "SpectrumIdentificationResult":
            if self.result["items"]:
                self.results.append(self.result)
            self.result = None
        elif name == "SpectrumIdentificationProtocol":
            self.protocols.append(self.protocol)
            self.protocol = None
        elif name == "MzIdentML":
            self.root_closed = True
        self.stack.pop()

    def finish(self):
        require(self.root_seen and self.root_closed and not self.stack, "incomplete XML document")
        for result in self.results:
            source = result["attributes"]["spectraData_ref"]
            require(source in self.spectra, "unresolved spectra reference")
            result["spectra_data"] = self.spectra[source]
            for item in result["items"]:
                require(item["evidence_refs"], "matching identification lacks protein evidence")
                item["protein_evidence"] = []
                for ref in item["evidence_refs"]:
                    require(ref in self.evidence, "unresolved peptide evidence")
                    ev = self.evidence[ref]
                    require(ev["peptide_ref"] == item["attributes"]["peptide_ref"], "peptide evidence mismatch")
                    protein = ev["dBSequence_ref"]
                    require(protein in self.proteins, "unresolved protein reference")
                    item["protein_evidence"].append({"attributes": ev, "protein": self.proteins[protein]})
        return {"matching_peptides": list(self.matched_peptides.values()), "matching_results": self.results,
                "protocols": self.protocols, "total_identification_items": self.item_count,
                "total_identification_results": len(self.result_ids), "xml_complete": True}


def inspect_stream(stream, *, expected_size, expected_sha1, target=TARGET,
                   compressed_cap=COMPRESSED_LIMIT, expanded_cap=EXPANDED_LIMIT, served_size=None, metadata_contract="served_gzip"):
    counted = CountedReader(stream, compressed_cap)
    handler = IdentificationHandler(target)
    parser = xml.sax.make_parser()
    parser.setFeature(feature_external_ges, False)
    parser.setFeature(feature_external_pes, False)
    parser.setContentHandler(handler)
    expanded, tail = 0, b""
    expanded_sha1, expanded_sha256 = hashlib.sha1(), hashlib.sha256()
    with gzip.GzipFile(fileobj=counted, mode="rb") as decompressed:
        while block := decompressed.read(65536):
            expanded += len(block)
            expanded_sha1.update(block)
            expanded_sha256.update(block)
            require(expanded <= expanded_cap, "expanded byte cap exceeded")
            require(b"\0" not in block, "only UTF-8 XML supported")
            probe = (tail + block).upper()
            require(b"<!DOCTYPE" not in probe and b"<!ENTITY" not in probe, "DTD/entities forbidden")
            tail = probe[-16:]
            parser.feed(block)
    parser.close()
    if served_size is not None:
        require(counted.count == served_size, "HTTP body length mismatch")
    require(metadata_contract in ("served_gzip", "gzip_sha1_expanded_size"), "unknown metadata byte contract")
    size_domain = "served_gzip" if metadata_contract == "served_gzip" else "expanded_mzidentml"
    size_matches = (counted.count if size_domain == "served_gzip" else expanded) == expected_size
    checksum_matches = counted.sha1.hexdigest() == expected_sha1
    if not size_matches or not checksum_matches:
        raise SourceIntegrityError({"expected_size": expected_size, "expected_sha1": expected_sha1,
            "metadata_size_domain": size_domain, "metadata_checksum_domain": "served_gzip",
            "served_gzip_size": counted.count, "served_gzip_sha1": counted.sha1.hexdigest(),
            "served_gzip_sha256": counted.sha256.hexdigest(), "expanded_size": expanded,
            "expanded_sha1": expanded_sha1.hexdigest(), "expanded_sha256": expanded_sha256.hexdigest(),
            "xml_complete": handler.root_closed, "scientific_attribution": "withheld"})
    output = handler.finish()
    output.update(compressed_bytes=counted.count, expanded_bytes=expanded,
                  sha1=counted.sha1.hexdigest(), sha256=counted.sha256.hexdigest(),
                  expanded_sha1=expanded_sha1.hexdigest(), expanded_sha256=expanded_sha256.hexdigest(),
                  api_size=expected_size, api_sha1=expected_sha1, metadata_size_domain=size_domain, metadata_checksum_domain="served_gzip",
                  served_size_differs_from_api=counted.count != expected_size)
    return output


def live_inspection():
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    context = ssl.create_default_context()
    if Path("/etc/ssl/cert.pem").is_file():
        context.load_verify_locations(cafile="/etc/ssl/cert.pem")
    opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=context))
    started = datetime.now(timezone.utc).isoformat()
    compressed, expanded, results = 0, 0, []
    for filename, size, checksum in FILES:
        url = BASE + filename
        print("Inspecting pinned class-II result " + filename, file=sys.stderr, flush=True)
        with opener.open(url, timeout=60) as response:
            require(response.status == 200, "source HTTP response not complete")
            content_length = response.headers.get("Content-Length")
            served_size = None if content_length is None else int(content_length)
            if served_size is not None:
                require(served_size <= COMPRESSED_LIMIT, "HTTP body exceeds compressed cap")
            http_metadata = {key: response.headers.get(key) for key in ("Content-Length", "Last-Modified", "ETag")}
            record = inspect_stream(response, expected_size=size, expected_sha1=checksum,
                compressed_cap=min(COMPRESSED_LIMIT, TOTAL_LIMIT - compressed),
                expanded_cap=EXPANDED_LIMIT - expanded, served_size=served_size,
                metadata_contract="gzip_sha1_expanded_size")
        compressed += record["compressed_bytes"]
        expanded += record["expanded_bytes"]
        results.append({"file": filename, "url": url, "http_metadata": http_metadata, **record})
        print("Verified file; matching results: " + str(len(record["matching_results"])), file=sys.stderr, flush=True)
    return {"schema_version": 1, "project": PROJECT, "target_sequence": TARGET,
            "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
            "runtime": sys.version.split()[0],
            "metadata_contract": "API checksum matches served gzip SHA1; API size matches expanded XML bytes",
            "contract_basis": "Observed independently on all three files; not asserted as documented API semantics",
            "initial_rejected_assumption": "API checksum and size describe one byte representation",
            "assay_id": 18456218, "source_license_metadata": "CC0", "files": results,
            "all_three_pinned_files_complete": len(results) == len(FILES),
            "compressed_bytes": compressed, "expanded_bytes": expanded,
            "spectra_reanalyzed": False, "allotype_assigned": False}


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CERT = ROOT / "registries/cdr2l-source-identification-2026-11-06.json"

# Hash of this file when the 2026-11-06 identification certificate was produced.
# Committed certificates pin producing code; later fail-closed edits accept this
# hash alongside the current file hash without rewriting the receipt.
PRODUCING_SCRIPT_SHA256 = "a41313a61ab0be74157792efa45d047ee3cb68a429da22aa088e24d18d5a79c2"

MATCH_FILE = "peptides_1_1_0_CII_r3.mzid.gz"
MATCH_ASSAY_ID = 18456218
MATCH_SPECTRUM_ID = "index=22949"
MATCH_RESIDUE_START = "432"
MATCH_RESIDUE_END = "446"
MATCH_CHARGE = "3"
MATCH_EXPERIMENTAL_MZ = "614.9990"


def check_certificate(path: Path) -> None:
    require(path.is_file(), f"missing certificate {path}")
    report = json.loads(path.read_text(encoding="utf-8"))
    stored_impl = report.get("implementation_sha256")
    current_impl = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    require(stored_impl in {current_impl, PRODUCING_SCRIPT_SHA256}, "implementation_sha256 mismatch")
    require(report.get("project") == PROJECT and report.get("target_sequence") == TARGET, "identity drift")
    require(report.get("assay_id") == MATCH_ASSAY_ID, "assay identity drift")
    require(report.get("all_three_pinned_files_complete") is True, "incomplete certificate")
    require(len(report.get("files", [])) == len(FILES), "wrong file count")
    match_file = None
    for record in report["files"]:
        require(record.get("xml_complete") is True, f"incomplete xml: {record.get('file')}")
        if record.get("matching_results"):
            require(match_file is None, "expected one file with a target identification")
            match_file = record
    require(match_file is not None, "expected one file with a target identification")
    require(match_file.get("file") == MATCH_FILE, "unexpected matching file")
    result = match_file["matching_results"][0]
    require(result["attributes"]["spectrumID"] == MATCH_SPECTRUM_ID, "spectrum index drift")
    item = result["items"][0]
    attrs = item["attributes"]
    require(attrs.get("chargeState") == MATCH_CHARGE, "charge state drift")
    require(attrs.get("experimentalMassToCharge") == MATCH_EXPERIMENTAL_MZ, "precursor drift")
    evidence = item["protein_evidence"][0]["attributes"]
    require(evidence.get("start") == MATCH_RESIDUE_START and evidence.get("end") == MATCH_RESIDUE_END,
            "residue span drift")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Inspect exactly the three pinned public result files")
    parser.add_argument("--check", action="store_true", help="Verify the committed identification certificate offline")
    parser.add_argument("--certificate", type=Path, default=DEFAULT_CERT, help="Certificate JSON for --check")
    parser.add_argument("--output", type=Path, help="Write compact target-only identification metadata after all files verify")
    args = parser.parse_args()
    if args.check:
        try:
            check_certificate(args.certificate)
        except ValueError as error:
            print(f"FAIL: {error}", file=sys.stderr)
            return 1
        print("PASS: offline identification certificate digest and identity")
        return 0
    if not args.live:
        parser.print_help()
        return 0
    try:
        result = live_inspection()
        result["implementation_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            require(not args.output.exists(), "output exists; preserve prior results")
            with args.output.open("x") as handle:
                handle.write(payload)
        else:
            print(payload, end="")
    except (OSError, EOFError, ValueError, KeyError, xml.sax.SAXException) as error:
        print("Source identification inspection failed: " + type(error).__name__, file=sys.stderr)
        if isinstance(error, ValueError):
            print(str(error), file=sys.stderr)
        if isinstance(error, SourceIntegrityError):
            print(json.dumps(error.metadata, sort_keys=True), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
