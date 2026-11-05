"""HTTPS fetch restricted to Pilot 001 first-run network allowlist."""

from __future__ import annotations

import urllib.parse
import urllib.request

from pilot001_first_run import failure_codes as codes

ALLOWED_HOSTS = frozenset(
    {
        "www.dropbox.com",
        "pmc-oa-opendata.s3.us-east-1.amazonaws.com",
    }
)


class AllowlistedFetchError(OSError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _require_https(url: str) -> urllib.parse.SplitResult:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc not in ALLOWED_HOSTS:
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH_HOST)
    if not parsed.path:
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
    return parsed


def _response_url_allowed(response, expected: urllib.parse.SplitResult) -> None:
    actual = urllib.parse.urlsplit(response.geturl())
    if actual.scheme != "https" or actual.netloc not in ALLOWED_HOSTS:
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH_HOST)
    if actual.netloc != expected.netloc or actual.path != expected.path:
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH)


def fetch_byte_range(url: str, start: int, end: int, *, total_bytes: int) -> bytes:
    if not isinstance(start, int) or not isinstance(end, int):
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
    if start < 0 or end < start or end >= total_bytes:
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
    expected = _require_https(url)
    request = urllib.request.Request(
        url,
        headers={
            "Range": f"bytes={start}-{end}",
            "Accept-Encoding": "identity",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            _response_url_allowed(response, expected)
            if (
                response.status != 206
                or response.headers.get("Content-Range") != f"bytes {start}-{end}/{total_bytes}"
                or response.headers.get("Content-Encoding", "identity") != "identity"
            ):
                raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
            body = response.read(end - start + 1)
            if len(body) != end - start + 1 or response.read(1):
                raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
            return body
    except AllowlistedFetchError:
        raise
    except OSError:
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH) from None


def fetch_exact(url: str, *, expected_bytes: int) -> bytes:
    expected = _require_https(url)
    request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            _response_url_allowed(response, expected)
            if (
                response.status != 200
                or response.headers.get("Content-Encoding", "identity") != "identity"
            ):
                raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
            body = response.read(expected_bytes + 1)
            if len(body) != expected_bytes:
                raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
            if response.read(1):
                raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
            return body
    except AllowlistedFetchError:
        raise
    except OSError:
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH) from None
