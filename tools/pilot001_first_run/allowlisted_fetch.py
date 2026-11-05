"""HTTPS fetch restricted to Pilot 001 first-run network allowlist."""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request

from pilot001_first_run import failure_codes as codes

# Initial URLs use www.dropbox.com or PMC S3; Dropbox byte ranges redirect to CDN hosts.
ALLOWED_HOSTS = frozenset(
    {
        "www.dropbox.com",
        "pmc-oa-opendata.s3.us-east-1.amazonaws.com",
    }
)
DROPBOX_CDN_SUFFIX = ".dl.dropboxusercontent.com"
MAX_REDIRECTS = 8


class AllowlistedFetchError(OSError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def host_allowed(netloc: str) -> bool:
    if not netloc or "@" in netloc:
        return False
    host = netloc.rsplit(":", 1)[0].lower().rstrip(".")
    if host in ALLOWED_HOSTS:
        return True
    return host.endswith(DROPBOX_CDN_SUFFIX)


def _require_https(url: str) -> urllib.parse.SplitResult:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not host_allowed(parsed.netloc):
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH_HOST)
    if not parsed.path:
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
    return parsed


class _AllowlistedRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _require_https(newurl)
        redirected = urllib.request.Request(
            newurl,
            data=req.data,
            headers=dict(req.header_items()),
            origin_req_host=urllib.request.Request(newurl).host,
            unverifiable=True,
        )
        return redirected


def _allowlisted_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(_AllowlistedRedirectHandler())


def _open(request: urllib.request.Request):
    return _allowlisted_opener().open(request, timeout=120)


def fetch_byte_range(url: str, start: int, end: int, *, total_bytes: int) -> bytes:
    if not isinstance(start, int) or not isinstance(end, int):
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
    if start < 0 or end < start or end >= total_bytes:
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH)
    _require_https(url)
    request = urllib.request.Request(
        url,
        headers={
            "Range": f"bytes={start}-{end}",
            "Accept-Encoding": "identity",
        },
    )
    try:
        with _open(request) as response:
            _require_https(response.geturl())
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
    except (OSError, urllib.error.HTTPError, urllib.error.URLError):
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH) from None


def fetch_exact(url: str, *, expected_bytes: int) -> bytes:
    _require_https(url)
    request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    try:
        with _open(request) as response:
            _require_https(response.geturl())
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
    except (OSError, urllib.error.HTTPError, urllib.error.URLError):
        raise AllowlistedFetchError(codes.P001_FAIL_FETCH) from None
