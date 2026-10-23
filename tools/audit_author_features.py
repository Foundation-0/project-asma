#!/usr/bin/env python3
"""Audit one author matrix member in memory; emit integrity/feature aggregates.

Run only within the documented, authorized bounded inspection scope. The full
compressed member is transferred and decompressed for CRC/SHA-256 checks.
Abundance fields are transient bytes, never converted to numbers or retained.
Only the nine explicitly named annotation fields are decoded. This is neither
model execution nor a general data/code reuse or redistribution permission.
"""

import argparse
import collections
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import urllib.parse
import urllib.request
import zlib

import audit_author_archive as archive
import audit_published_cohorts as clinical

HEADER_SHA256 = "e39ef0ffaafaa92ca6dd7351ed578856be22f4e03b2cf26111106790bd7521c9"
PANEL_SHA256 = "77329920b86dacaffc6778ed7e7c6b827683beed1aad7f2229b8bafe2f535144"
ANNOTATIONS = ("uniprot", "HGNC symbol", "HGNC name", "HGNC Location", "Index",
               "NumberPeptide", "NumberPSM", "Proteins", "MaxPepProb")
COLUMN_COUNT = 178
CHUNK_BYTES = 65536
MAX_LINE_BYTES = 65536
MAX_ROWS = 100000
FAILURE_MESSAGE = "ERROR: author-feature audit failed; no row-level details emitted."


def require(condition):
    if not condition:
        raise ValueError(FAILURE_MESSAGE)


def member_chunks(data_offset):
    """Read one fixed-size HTTP range, bounded in both transfer and memory."""
    length = archive.MEMBER_CONTRACT["compressed_bytes"]
    end = data_offset + length - 1
    require(type(data_offset) is int and 0 <= data_offset <= end < archive.ARCHIVE_BYTES)
    request = urllib.request.Request(archive.URL, headers={
        "Range": f"bytes={data_offset}-{end}", "Accept-Encoding": "identity"})
    with urllib.request.urlopen(request, timeout=60) as response:
        require(urllib.parse.urlsplit(response.geturl()).scheme == "https")
        require(response.status == 206)
        require(response.headers.get("Content-Range") ==
                f"bytes {data_offset}-{end}/{archive.ARCHIVE_BYTES}")
        require(response.headers.get("Content-Encoding", "identity") == "identity")
        consumed = 0
        while consumed < length:
            chunk = response.read(min(CHUNK_BYTES, length - consumed))
            require(bool(chunk))
            consumed += len(chunk)
            require(consumed <= length)
            yield chunk
        require(response.read(1) == b"")


class FeatureSummary:
    """Store feature-annotation counters, never measurement fields or labels."""

    def __init__(self, panel):
        require(bool(panel) and len(panel) == len(set(panel)))
        require(all(isinstance(item, str) and item and item == item.strip() for item in panel))
        self.panel = set(panel)
        self.header_seen = False
        self.rows = 0
        self.symbols = collections.Counter()
        self.accessions = collections.Counter()
        self.indices = collections.Counter()
        self.annotation_rows = collections.Counter()
        self.empty_symbols = 0
        self.padded_symbols = 0
        self.delimiter_symbols = 0
        self.panel_annotation_delimiters = 0

    def consume(self, line, expected_header_sha256=HEADER_SHA256):
        require(line.endswith(b"\n") and len(line) <= MAX_LINE_BYTES)
        if not self.header_seen:
            require(hashlib.sha256(line).hexdigest() == expected_header_sha256)
            fields = line.rstrip(b"\r\n").split(b"\t")
            require(len(fields) == COLUMN_COUNT)
            require(fields[:len(ANNOTATIONS)] == [item.encode() for item in ANNOTATIONS])
            self.header_seen = True
            return
        row = line[:-1]
        if row.endswith(b"\r"):
            row = row[:-1]
        require(row.count(b"\t") == COLUMN_COUNT - 1 and b"\n" not in row and b"\r" not in row)
        require(b"\x00" not in row)
        # Decode only annotation fields, permitting standard balanced TSV
        # quotes and doubled quote escapes. Embedded tabs/newlines are rejected.
        annotation_bytes = row.split(b"\t", len(ANNOTATIONS))[:len(ANNOTATIONS)]
        for item in annotation_bytes:
            if item.startswith(b'"'):
                require(len(item) >= 2 and item.endswith(b'"'))
                require(b'"' not in item[1:-1].replace(b'""', b''))
            else:
                require(b'"' not in item)
        values = tuple(next(csv.reader([b"\t".join(annotation_bytes).decode("utf-8")],
                                       delimiter="\t", strict=True)))
        require(len(values) == len(ANNOTATIONS))
        accession, symbol, _, _, index, _, _, proteins, _ = values
        self.rows += 1
        require(self.rows <= MAX_ROWS)
        self.annotation_rows[values] += 1
        self.symbols[symbol] += 1
        if accession:
            self.accessions[accession] += 1
        if index:
            self.indices[index] += 1
        self.empty_symbols += int(not symbol)
        self.padded_symbols += int(symbol != symbol.strip())
        self.delimiter_symbols += int(any(mark in symbol for mark in (";", ",", "|")))
        if symbol in self.panel:
            self.panel_annotation_delimiters += int(any(mark in value for value in
                                                       (accession, proteins) for mark in (";", ",", "|")))

    def result(self):
        require(self.header_seen and self.rows > 0)
        multiplicities = [self.symbols[symbol] for symbol in self.panel]
        return {
            "annotation_fields": list(ANNOTATIONS), "matrix_columns": COLUMN_COUNT,
            "feature_rows": self.rows, "nonempty_distinct_symbols": len(set(self.symbols) - {""}),
            "empty_symbol_rows": self.empty_symbols, "symbol_rows_with_outer_whitespace": self.padded_symbols,
            "symbol_rows_with_delimiter_markers": self.delimiter_symbols,
            "symbols_repeated_across_rows": sum(count > 1 for symbol, count in self.symbols.items() if symbol),
            "nonempty_accessions_repeated_across_rows": sum(count > 1 for count in self.accessions.values()),
            "nonempty_indices_repeated_across_rows": sum(count > 1 for count in self.indices.values()),
            "duplicate_annotation_rows_beyond_first": sum(count - 1 for count in self.annotation_rows.values()),
            "panel_symbols": len(self.panel), "panel_symbols_absent": multiplicities.count(0),
            "panel_symbols_with_one_exact_row": multiplicities.count(1),
            "panel_symbols_with_multiple_exact_rows": sum(count > 1 for count in multiplicities),
            "panel_matching_rows": sum(multiplicities),
            "panel_matching_rows_with_delimiter_markers_in_protein_annotations": self.panel_annotation_delimiters,
            "all_panel_symbols_have_one_exact_row": all(count == 1 for count in multiplicities),
            "abundance_values_converted_or_used": False,
        }


def inspect_member(chunks, panel, contract=None, expected_header_sha256=HEADER_SHA256):
    """Verify the complete deflate stream before returning aggregate results."""
    contract = archive.MEMBER_CONTRACT if contract is None else contract
    require(0 < contract["compressed_bytes"] <= archive.MEMBER_CONTRACT["compressed_bytes"])
    require(0 < contract["uncompressed_bytes"] <= archive.MEMBER_CONTRACT["uncompressed_bytes"])
    compressed_hash, body_hash = hashlib.sha256(), hashlib.sha256()
    inflater, features = zlib.decompressobj(-15), FeatureSummary(panel)
    compressed_bytes, body_bytes, crc = 0, 0, 0
    pending_line = bytearray()
    for chunk in chunks:
        require(isinstance(chunk, bytes) and 0 < len(chunk) <= CHUNK_BYTES and not inflater.eof)
        compressed_bytes += len(chunk)
        require(compressed_bytes <= contract["compressed_bytes"])
        compressed_hash.update(chunk)
        pending = chunk
        while True:
            output = inflater.decompress(pending, min(CHUNK_BYTES, contract["uncompressed_bytes"] - body_bytes + 1))
            pending = inflater.unconsumed_tail
            require(not inflater.unused_data)
            body_bytes += len(output)
            require(body_bytes <= contract["uncompressed_bytes"])
            body_hash.update(output)
            crc = zlib.crc32(output, crc)
            pending_line.extend(output)
            while b"\n" in pending_line:
                position = pending_line.index(b"\n") + 1
                require(position <= MAX_LINE_BYTES)
                features.consume(bytes(pending_line[:position]), expected_header_sha256)
                del pending_line[:position]
            require(len(pending_line) < MAX_LINE_BYTES)
            if not pending and len(output) < CHUNK_BYTES:
                break
            require(bool(output) or bool(pending))
    require(compressed_bytes == contract["compressed_bytes"] and inflater.eof)
    require(not inflater.unused_data and not inflater.unconsumed_tail and not pending_line)
    require(body_bytes == contract["uncompressed_bytes"] and crc == contract["crc32"])
    return {
        "integrity": {"compressed_bytes": compressed_bytes, "uncompressed_bytes": body_bytes,
                      "compressed_sha256": compressed_hash.hexdigest(), "sha256": body_hash.hexdigest(),
                      "crc32_hex": f"{crc:08x}", "crc32_matches_pinned_directory": True,
                      "deflate_stream_complete": True, "header_sha256": expected_header_sha256,
                      "sha256_is_new_observation_not_publisher_reference": True},
        "features": features.result(),
    }


def load_panel():
    book = clinical.Workbook(clinical.SOURCES["panel_and_scores"])
    rows = book.rows("64_protein_predictors", columns={"A"})
    require(rows[0].get("A") == "Proteins")
    symbols = [row.get("A", "") for row in rows[1:]]
    require(len(symbols) == 64 and len(set(symbols)) == 64)
    require(hashlib.sha256(("\n".join(symbols) + "\n").encode()).hexdigest() == PANEL_SHA256)
    return symbols


def run_audit():
    started, timer = datetime.now(timezone.utc).isoformat(), time.monotonic()
    fetched = 0

    def fetch(start, end):
        nonlocal fetched
        body = archive.fetch_range(start, end)
        fetched += len(body)
        return body

    name, directory = archive.inspect_directory(fetch(archive.ARCHIVE_BYTES - archive.TAIL_BYTES,
                                                       archive.ARCHIVE_BYTES - 1))
    offset = archive.member_data_offset(fetch, name)
    panel = load_panel()
    result = inspect_member(member_chunks(offset), panel)
    # Recheck the pinned directory after the body, rejecting metadata drift.
    archive.inspect_directory(fetch(archive.ARCHIVE_BYTES - archive.TAIL_BYTES, archive.ARCHIVE_BYTES - 1))
    result.update({
        "schema_version": 1, "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": time.monotonic() - timer,
        "scope": "Complete member integrity and exact protein annotation coverage; no abundance analysis",
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "archive": {"url": archive.URL, "bytes": archive.ARCHIVE_BYTES, "central_directory": directory,
                    "bytes_fetched": fetched + result["integrity"]["compressed_bytes"],
                    "whole_archive_checksum_verified": False},
        "member_basename": archive.MEMBER,
        "panel": {"sheet": "64_protein_predictors", "range": "A2:A65", "canonical_sha256": PANEL_SHA256,
                  "source": dict(clinical.SOURCES["panel_and_scores"],
                                 url=clinical.BASE + clinical.SOURCES["panel_and_scores"]["filename"])},
        "implementation_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in
                                  (Path(__file__), Path(archive.__file__), Path(clinical.__file__))},
        "limitations": [
            "The full compressed member was transferred and decompressed in memory; abundance fields were discarded without numeric conversion or analysis.",
            "No matrix, measurement keys, abundance rows, annotations or row-level outputs are written; only aggregate counts and fingerprints are emitted.",
            "CRC verifies agreement with the pinned ZIP metadata; observed SHA-256 is not an independent publisher checksum.",
            "Whole-archive integrity, preprocessing history, replicate collapse, model-workspace equivalence and general reuse rights remain unestablished.",
            "Exact HGNC symbol equality does not resolve protein groups, isoforms, alias mappings or biological specificity; delimiter counts are diagnostics only.",
            "Duplicate annotation rows do not establish duplicate abundance rows; no measurement fields are compared.",
        ],
    })
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    try:
        print(json.dumps(run_audit(), indent=2, sort_keys=True, allow_nan=False))
    except Exception:
        print(FAILURE_MESSAGE, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
