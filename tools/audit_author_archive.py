#!/usr/bin/env python3
"""Inspect a pinned author-archive directory and discovery-matrix header only.

The ZIP is accessed with bounded HTTP ranges. Inflation stops at the first
newline, before abundance values. Clinical and published-score keys stay in
memory; output contains only aggregate linkage counts and provenance.
"""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
import urllib.parse
import urllib.request
import zlib

import audit_matrix_headers as matrix
import audit_published_cohorts as clinical


URL = "https://www.dropbox.com/s/7zul3j1vyrxo40c/processed_data.zip?e=1&dl=1"
ARCHIVE_BYTES = 70138965
CENTRAL_SHA256 = "5dd3db7c674ab2952a148af474da6604c1daf88a4e2cf2ff45d939f7530ae5a0"
ENTRY_COUNT = 42
MEMBER = "FFPE_discovery_globalprotein_imputed.tsv"
MEMBER_CONTRACT = {"compressed_bytes": 7993706, "uncompressed_bytes": 18498831,
                   "crc32": 0x9F713751, "local_offset": 40809592, "method": 8, "flags": 8}
TAIL_BYTES = 65557  # Maximum ordinary ZIP EOCD record plus comment.
MAX_HEADER_BYTES = 65536
MAX_COMPRESSED_HEADER_BYTES = 65536
COMPRESSED_CHUNK_BYTES = 4096
FAILURE_MESSAGE = "ERROR: author-archive header audit failed; no row-level details emitted."


def require(condition):
    if not condition:
        raise ValueError(FAILURE_MESSAGE)


def fetch_range(start, end):
    require(type(start) is int and type(end) is int and 0 <= start <= end < ARCHIVE_BYTES)
    require(end - start + 1 <= TAIL_BYTES)
    request = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{end}",
                                                  "Accept-Encoding": "identity"})
    with urllib.request.urlopen(request, timeout=40) as response:
        require(urllib.parse.urlsplit(response.geturl()).scheme == "https")
        require(response.status == 206)
        require(response.headers.get("Content-Range") == f"bytes {start}-{end}/{ARCHIVE_BYTES}")
        require(response.headers.get("Content-Encoding", "identity") == "identity")
        body = response.read(end - start + 2)
    require(len(body) == end - start + 1)
    return body


def inspect_directory(tail):
    """Validate ordinary single-disk ZIP metadata without reading member data."""
    require(len(tail) == TAIL_BYTES)
    position = tail.rfind(b"PK\x05\x06")
    require(0 <= position <= len(tail) - 22)
    end = struct.unpack_from("<4s4H2IH", tail, position)
    require(position + 22 + end[-1] == len(tail))
    require(end[1:5] == (0, 0, ENTRY_COUNT, ENTRY_COUNT))
    size, offset = end[5:7]
    start = offset - (ARCHIVE_BYTES - len(tail))
    require(0 <= start and start + size == position)
    directory = tail[start:start + size]
    require(hashlib.sha256(directory).hexdigest() == CENTRAL_SHA256)
    entries, cursor = [], 0
    while cursor < len(directory):
        require(cursor + 46 <= len(directory))
        fields = struct.unpack_from("<4s6H3I5H2I", directory, cursor)
        require(fields[0] == b"PK\x01\x02" and fields[13] == 0)
        name_length, extra_length, comment_length = fields[10:13]
        next_cursor = cursor + 46 + name_length + extra_length + comment_length
        require(next_cursor <= len(directory))
        name = directory[cursor + 46:cursor + 46 + name_length]
        entries.append((name, fields))
        cursor = next_cursor
    require(cursor == len(directory) and len(entries) == ENTRY_COUNT)
    selected = [(name, fields) for name, fields in entries
                if name.rsplit(b"/", 1)[-1] == MEMBER.encode("utf-8")]
    require(len(selected) == 1)
    name, fields = selected[0]
    metadata = dict(zip(("compressed_bytes", "uncompressed_bytes", "crc32", "local_offset", "method", "flags"),
                        (fields[8], fields[9], fields[7], fields[16], fields[4], fields[3])))
    require(metadata == MEMBER_CONTRACT)
    require(metadata["local_offset"] + 30 + metadata["compressed_bytes"] < offset)
    return name, {"bytes": size, "offset": offset, "sha256": CENTRAL_SHA256, "entries": len(entries)}


def member_data_offset(fetch, name):
    offset = MEMBER_CONTRACT["local_offset"]
    header = fetch(offset, offset + 29)
    fields = struct.unpack("<4s5H3I2H", header)
    require(fields[0] == b"PK\x03\x04" and fields[2] == MEMBER_CONTRACT["flags"] and fields[3] == 8)
    # This pinned member uses a data descriptor; zero placeholders are valid.
    require(all(actual in (0, MEMBER_CONTRACT[key]) for actual, key in
                zip(fields[6:9], ("crc32", "compressed_bytes", "uncompressed_bytes"))))
    name_length, extra_length = fields[-2:]
    require(name_length == len(name) and 0 < name_length + extra_length <= MAX_HEADER_BYTES)
    extra = fetch(offset + 30, offset + 29 + name_length + extra_length)
    require(extra[:name_length] == name)
    data_offset = offset + 30 + name_length + extra_length
    require(data_offset + MEMBER_CONTRACT["compressed_bytes"] < ARCHIVE_BYTES - TAIL_BYTES)
    return data_offset


def inflate_header(fetch, data_offset):
    """Limit both compressed input and output; never inflate beyond newline."""
    inflater = zlib.decompressobj(-15)
    header, consumed = bytearray(), 0
    while consumed < MAX_COMPRESSED_HEADER_BYTES:
        length = min(COMPRESSED_CHUNK_BYTES, MAX_COMPRESSED_HEADER_BYTES - consumed,
                     MEMBER_CONTRACT["compressed_bytes"] - consumed)
        require(length > 0)
        pending = fetch(data_offset + consumed, data_offset + consumed + length - 1)
        require(len(pending) == length)
        consumed += length
        while True:
            item = inflater.decompress(pending, 1)
            pending = inflater.unconsumed_tail
            if not item:
                require(not inflater.eof and not inflater.unused_data and not pending)
                break
            header.extend(item)
            require(len(header) <= MAX_HEADER_BYTES)
            if item == b"\n":
                return bytes(header), consumed
    raise ValueError(FAILURE_MESSAGE)


def summarize_header(header, records, score_keys):
    require(header.endswith(b"\n") and len(header) <= MAX_HEADER_BYTES)
    fields = next(csv.reader([header.decode("utf-8-sig").rstrip("\r\n")], delimiter="\t", strict=True))
    result = matrix.summarize_labels(fields, records)
    joined = clinical.join_score_membership(score_keys, records)
    require(len(joined) == 135)
    biological, _ = clinical.classify_clinical(records)
    eligible = clinical.eligible_samples(clinical.collapse_replicates(biological))
    require(clinical.sample_keys(eligible) == clinical.sample_keys(joined))
    field_set = set(fields)
    require(set(score_keys) <= field_set)
    mapped = [row for row in biological if row[clinical.LABEL_COLUMN] in field_set]
    result.update({
        "published_score_rows": len(score_keys),
        "published_score_keys_matching_header": len(set(score_keys) & field_set),
        "published_score_sample_keys_mapped": len(clinical.sample_keys(joined) & clinical.sample_keys(mapped)),
        "published_score_patient_keys_mapped": len(clinical.patient_keys(joined) & clinical.patient_keys(mapped)),
        "published_score_membership_equals_reconstructed_exclusions": True,
        "header_bytes": len(header), "header_sha256": hashlib.sha256(header).hexdigest(),
    })
    return result


def run_audit():
    started, timer = datetime.now(timezone.utc).isoformat(), time.monotonic()
    fetched = 0

    def fetch(start, end):
        nonlocal fetched
        body = fetch_range(start, end)
        fetched += len(body)
        return body

    name, directory = inspect_directory(fetch(ARCHIVE_BYTES - TAIL_BYTES, ARCHIVE_BYTES - 1))
    data_offset = member_data_offset(fetch, name)
    header, compressed_bytes = inflate_header(fetch, data_offset)
    clinical_book = clinical.Workbook(clinical.SOURCES["clinical"])
    rows = clinical_book.rows("FFPE_Discovery_clinical")
    columns = rows[0]
    require(len(set(columns.values())) == len(columns))
    records = [{columns[key]: value for key, value in row.items()} for row in rows[1:]]
    score_book = clinical.Workbook(clinical.SOURCES["panel_and_scores"])
    rows = score_book.rows("FFPE_pred_scores", columns={"A"})
    require(rows[0].get("A") == "Samples" and rows[0].get("B") == "Pred.scores")
    summary = summarize_header(header, records, [row.get("A", "") for row in rows[1:]])
    require(summary["matrix_header_columns"] == 178 and summary["matched_response_labelled_rows"] == 168)
    require(summary["matched_unique_sample_keys"] == summary["matched_unique_patient_keys"] == 158)
    return {
        "schema_version": 1, "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": time.monotonic() - timer,
        "scope": "Public author ZIP central directory and discovery header; exact clinical and score-membership joins only",
        "archive": {"url": URL, "bytes": ARCHIVE_BYTES, "bytes_fetched": fetched,
                    "central_directory": directory, "full_archive_checksum_verified": False},
        "member": dict(MEMBER_CONTRACT, basename=MEMBER, crc32_hex=f"{MEMBER_CONTRACT['crc32']:08x}",
                       compressed_header_bytes_fetched=compressed_bytes, full_member_crc_verified=False,
                       full_member_checksum_verified=False, full_member_downloaded=False),
        "linkage": summary,
        "source_workbooks": {key: dict(source, url=clinical.BASE + source["filename"])
                             for key, source in clinical.SOURCES.items()},
        "implementation_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in (Path(__file__), Path(matrix.__file__), Path(clinical.__file__))},
        "limitations": [
            "Only the ZIP directory and first matrix line were verified; CRC and whole-file content integrity remain unverified.",
            "Exact header linkage establishes available column labels, not matrix values, protein coverage, preprocessing or model equivalence.",
            "Repeated measurement columns remain distinct; no replicate averaging or matrix reconstruction was performed.",
            "Published score membership is checked without reading numeric scores; source score provenance and patient independence remain unresolved.",
            "Public availability does not by itself establish reuse rights, approved retention or authority to execute third-party code.",
            "No abundance values, patient/sample keys, workbooks or raw headers are emitted or retained; only aggregate results are output.",
        ],
    }


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
