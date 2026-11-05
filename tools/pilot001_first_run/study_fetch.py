"""Fetch pinned study bytes into container tmpfs with manifest integrity checks."""

from __future__ import annotations

import hashlib
import zlib
from pathlib import Path

import audit_author_archive as archive
import audit_published_cohorts as cohorts

from pilot001_first_run import failure_codes as codes
from pilot001_first_run.allowlisted_fetch import AllowlistedFetchError, fetch_byte_range, fetch_exact
from pilot001_first_run.config import InputPin


class StudyFetchError(OSError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _pin_by_role(pins: tuple[InputPin, ...], role: str) -> InputPin:
    for pin in pins:
        if pin.role == role:
            return pin
    raise StudyFetchError(codes.P001_FAIL_INTERNAL)


def _verify_pin(body: bytes, pin: InputPin) -> None:
    if len(body) != pin.bytes or hashlib.sha256(body).hexdigest() != pin.sha256:
        raise StudyFetchError(codes.P001_FAIL_INPUT_INTEGRITY)


def _archive_range_fetch(start: int, end: int) -> bytes:
    try:
        return fetch_byte_range(archive.URL, start, end, total_bytes=archive.ARCHIVE_BYTES)
    except AllowlistedFetchError as error:
        raise StudyFetchError(error.code) from None


def _fetch_compressed_member() -> bytes:
    start = archive.ARCHIVE_BYTES - archive.TAIL_BYTES
    tail = _archive_range_fetch(start, archive.ARCHIVE_BYTES - 1)
    name, directory = archive.inspect_directory(tail)

    def ranged_fetch(range_start: int, range_end: int) -> bytes:
        return _archive_range_fetch(range_start, range_end)

    data_offset = archive.member_data_offset(ranged_fetch, name)
    parts: list[bytes] = []
    consumed = 0
    for chunk in _member_chunks(data_offset):
        consumed += len(chunk)
        if consumed > archive.MEMBER_CONTRACT["compressed_bytes"]:
            raise StudyFetchError(codes.P001_FAIL_FETCH)
        parts.append(chunk)
    if consumed != archive.MEMBER_CONTRACT["compressed_bytes"]:
        raise StudyFetchError(codes.P001_FAIL_FETCH)
    repeated_name, repeated_directory = archive.inspect_directory(
        _archive_range_fetch(start, archive.ARCHIVE_BYTES - 1)
    )
    if name != repeated_name or directory != repeated_directory:
        raise StudyFetchError(codes.P001_FAIL_FETCH)
    return b"".join(parts)


def _member_chunks(data_offset: int):
    length = archive.MEMBER_CONTRACT["compressed_bytes"]
    end = data_offset + length - 1
    if data_offset < 0 or end >= archive.ARCHIVE_BYTES:
        raise StudyFetchError(codes.P001_FAIL_FETCH)
    consumed = 0
    while consumed < length:
        chunk_end = min(data_offset + consumed + 65536 - 1, end)
        chunk = _archive_range_fetch(data_offset + consumed, chunk_end)
        if not chunk:
            raise StudyFetchError(codes.P001_FAIL_FETCH)
        consumed += len(chunk)
        yield chunk


def _inflate_member(compressed: bytes) -> bytes:
    contract = archive.MEMBER_CONTRACT
    if len(compressed) != contract["compressed_bytes"]:
        raise StudyFetchError(codes.P001_FAIL_INPUT_INTEGRITY)
    inflater = zlib.decompressobj(-15)
    body = inflater.decompress(compressed, contract["uncompressed_bytes"] + 1)
    if not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:
        raise StudyFetchError(codes.P001_FAIL_INPUT_INTEGRITY)
    if len(body) != contract["uncompressed_bytes"]:
        raise StudyFetchError(codes.P001_FAIL_INPUT_INTEGRITY)
    if zlib.crc32(body) != contract["crc32"]:
        raise StudyFetchError(codes.P001_FAIL_INPUT_INTEGRITY)
    return body


HANDOFF_MEMBER = "member.compressed"
HANDOFF_CLINICAL = "clinical.xlsx"
HANDOFF_PANEL = "panel.xlsx"


HANDOFF_MEMBER = "member.compressed"
HANDOFF_CLINICAL = "clinical.xlsx"
HANDOFF_PANEL = "panel.xlsx"
ROLE_COMPRESSED = "author_dropbox_member_compressed"
ROLE_UNCOMPRESSED = "author_dropbox_member"


def fetch_for_handoff(pins: tuple[InputPin, ...]) -> tuple[bytes, bytes, bytes]:
    """Phase 1: download and verify compressed + workbook pins only (no inflate)."""
    compressed_pin = _pin_by_role(pins, ROLE_COMPRESSED)
    mmc1_pin = _pin_by_role(pins, "nlm_mmc1_clinical")
    mmc4_pin = _pin_by_role(pins, "nlm_mmc4_panel")

    compressed = _fetch_compressed_member()
    _verify_pin(compressed, compressed_pin)

    clinical_source = cohorts.SOURCES["clinical"]
    panel_source = cohorts.SOURCES["panel_and_scores"]
    clinical_url = cohorts.BASE + clinical_source["filename"]
    panel_url = cohorts.BASE + panel_source["filename"]
    try:
        clinical = fetch_exact(clinical_url, expected_bytes=clinical_source["bytes"])
        panel = fetch_exact(panel_url, expected_bytes=panel_source["bytes"])
    except AllowlistedFetchError as error:
        raise StudyFetchError(error.code) from None

    _verify_pin(clinical, mmc1_pin)
    _verify_pin(panel, mmc4_pin)
    return compressed, clinical, panel


def verify_uncompressed_member_for_analysis(
    compressed: bytes,
    pins: tuple[InputPin, ...],
) -> None:
    """Phase 2: inflate offline and verify uncompressed manifest pin."""
    compressed_pin = _pin_by_role(pins, ROLE_COMPRESSED)
    _verify_pin(compressed, compressed_pin)
    uncompressed = _inflate_member(compressed)
    uncompressed_pin = _pin_by_role(pins, ROLE_UNCOMPRESSED)
    _verify_pin(uncompressed, uncompressed_pin)
    del uncompressed


def fetch_and_verify_raw(pins: tuple[InputPin, ...]) -> tuple[bytes, bytes, bytes]:
    """Legacy name: full offline verify (used in tests with preloaded bytes)."""
    compressed, clinical, panel = fetch_for_handoff(pins)
    verify_uncompressed_member_for_analysis(compressed, pins)
    return compressed, clinical, panel


def write_raw_handoff(
    handoff_dir: Path,
    compressed: bytes,
    clinical: bytes,
    panel: bytes,
) -> None:
    handoff_dir.mkdir(parents=True, exist_ok=True)
    (handoff_dir / HANDOFF_MEMBER).write_bytes(compressed)
    (handoff_dir / HANDOFF_CLINICAL).write_bytes(clinical)
    (handoff_dir / HANDOFF_PANEL).write_bytes(panel)


def read_raw_handoff(handoff_dir: Path) -> tuple[bytes, bytes, bytes]:
    try:
        compressed = (handoff_dir / HANDOFF_MEMBER).read_bytes()
        clinical = (handoff_dir / HANDOFF_CLINICAL).read_bytes()
        panel = (handoff_dir / HANDOFF_PANEL).read_bytes()
    except OSError as error:
        raise StudyFetchError(codes.P001_FAIL_INTERNAL) from error
    if not compressed or not clinical or not panel:
        raise StudyFetchError(codes.P001_FAIL_INTERNAL)
    return compressed, clinical, panel


def fetch_to_tmpfs(
    pins: tuple[InputPin, ...],
    tmp_dir: Path,
) -> tuple[bytes, bytes, bytes]:
    """Test/legacy seam: verify and write under tmpfs."""
    payload = fetch_and_verify_raw(pins)
    write_raw_handoff(tmp_dir, *payload)
    return payload
