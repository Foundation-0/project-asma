"""Verified-byte helpers for pinned Ubuntu build inputs (no study data)."""

from __future__ import annotations

import hashlib
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "runtime/pinned-build-inputs"
LAUNCHPAD = "https://launchpad.net/ubuntu/+archive/primary/+files/"
ALLOWED_HOSTS = frozenset(
    {"www.python.org", "snapshot.ubuntu.com", "changelogs.ubuntu.com", "launchpad.net"}
)


def _matches(body: bytes, record: dict) -> bool:
    return len(body) == record["bytes"] and hashlib.sha256(body).hexdigest() == record["sha256"]


def mirror_urls(record: dict) -> list[str]:
    urls = [record["url"]]
    filename = record.get("filename")
    if isinstance(filename, str) and filename.endswith(".deb"):
        urls.append(LAUNCHPAD + urllib.parse.quote(filename))
    return urls


def vendor_path(record: dict, platform: str | None) -> Path | None:
    filename = record.get("filename")
    if not isinstance(filename, str) or Path(filename).name != filename:
        return None
    if platform:
        candidate = VENDOR / platform.replace("/", "-") / filename
        if candidate.is_file():
            return candidate
    for relative in (filename, record.get("license_notice", {}).get("filename")):
        if not relative:
            continue
        shared = VENDOR / "shared" / relative
        if shared.is_file():
            return shared
    direct = VENDOR / filename
    return direct if direct.is_file() else None


def read_verified(record: dict, cache: Path | None = None, platform: str | None = None) -> bytes:
    filename = record.get("filename") or record["url"].rstrip("/").split("/")[-1]
    if Path(filename).name != filename:
        raise ValueError("unsafe filename in record")

    if cache is not None:
        cached = cache / filename
        if cached.is_file():
            body = cached.read_bytes()
            if _matches(body, record):
                return body
            cached.unlink()

    vendor = vendor_path(record, platform)
    if vendor is not None:
        body = vendor.read_bytes()
        if _matches(body, record):
            return body

    last_error: Exception | None = None
    for url in mirror_urls(record):
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password:
            continue
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                final = urllib.parse.urlsplit(response.geturl())
                if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
                    raise ValueError("redirect left allowlist")
                body = response.read(record["bytes"] + 1)
        except Exception as error:
            last_error = error
            continue
        if not _matches(body, record):
            raise ValueError("bytes do not match the pinned size and SHA256")
        if cache is not None:
            partial = cache / (filename + ".partial")
            partial.write_bytes(body)
            partial.replace(cache / filename)
        return body

    if last_error is not None:
        raise last_error
    raise ValueError("no fetch URL for record")
