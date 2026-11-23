#!/usr/bin/env python3
"""Fetch the pinned ClinicalTrials.gov v2 pages and store the response bytes.

Writes snapshot files only. Counts are computed later by the offline checkers.
Refuses to replace an existing snapshot unless --force is passed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "protocols/trial-landscape-keywords-v2.json"
RESULT = ROOT / "results/trial-landscape-v2-2026-11-13"
USER_AGENT = (
    "ProjectAsma-TrialLandscapeV2/2026-11-13 "
    "(public aggregate metadata; https://github.com/Foundation-0/project-asma)"
)


class FetchError(RuntimeError):
    pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise FetchError("Unexpected registry redirect.")


def _get(url, max_bytes):
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urllib.request.build_opener(_NoRedirect()).open(request, timeout=120) as response:
            if response.status != 200:
                raise FetchError("Unexpected registry HTTP status.")
            raw = response.read(max_bytes + 1)
    except FetchError:
        raise
    except Exception as exc:
        raise FetchError("Registry request failed.") from exc
    if len(raw) > max_bytes:
        raise FetchError("Registry response exceeds byte limit.")
    return raw


def _url(spec, query, options, fields, token=None):
    parameters = dict(query)
    parameters.update(options)
    parameters["fields"] = ",".join(fields)
    if token is not None:
        parameters["pageToken"] = token
    return spec["endpoint"] + "?" + urllib.parse.urlencode(parameters)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="replace an existing snapshot")
    parser.add_argument("--output", type=Path, default=RESULT)
    args = parser.parse_args()
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    output = args.output
    snapshot = output / "snapshot"
    if snapshot.exists() and any(snapshot.iterdir()) and not args.force:
        raise SystemExit("Snapshot already exists. Refusing to overwrite.")
    snapshot.mkdir(parents=True, exist_ok=True)
    max_bytes = spec["limits"]["max_response_bytes"]
    started = datetime.now(timezone.utc).isoformat()
    version_url = spec["version_endpoint"]
    before = _get(version_url, max_bytes)
    (snapshot / "version-before.json").write_bytes(before)
    pages = []
    token = None
    for index in range(spec["limits"]["max_pages"]):
        url = _url(spec, spec["query"], spec["request_options"], spec["fields"], token)
        raw = _get(url, max_bytes)
        name = f"studies-page-{index:02d}.json"
        (snapshot / name).write_bytes(raw)
        page = json.loads(raw)
        pages.append({
            "path": f"snapshot/{name}",
            "url": url,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "study_count": len(page.get("studies") or []),
            "total_count": page.get("totalCount"),
        })
        token = page.get("nextPageToken")
        if not token:
            break
    else:
        raise SystemExit("Pagination exceeded the pinned page limit.")
    after = _get(version_url, max_bytes)
    (snapshot / "version-after.json").write_bytes(after)
    comparison_url = _url(
        spec, spec["comparison_query"], spec["comparison_request_options"], spec["comparison_fields"]
    )
    comparison = _get(comparison_url, max_bytes)
    (snapshot / "recruiting-query.json").write_bytes(comparison)
    archive = hashlib.sha256(b"".join((snapshot / f"studies-page-{i:02d}.json").read_bytes()
                                      for i in range(len(pages)))).hexdigest()
    manifest = {
        "schema_version": 1,
        "retrieved_started_utc": started,
        "retrieved_completed_utc": datetime.now(timezone.utc).isoformat(),
        "specification": "protocols/trial-landscape-keywords-v2.json",
        "endpoint": spec["endpoint"],
        "query": spec["query"],
        "request_options": spec["request_options"],
        "fields": spec["fields"],
        "comparison_query": spec["comparison_query"],
        "comparison_url": comparison_url,
        "version_url": version_url,
        "archive_sha256": archive,
        "archive_rule": "SHA-256 of the raw study-page bodies concatenated in page order, with no separator.",
        "note": "Projected public registry fields only. No eligibility text and no participant-level data. Registration metadata is not efficacy or treatment guidance.",
        "files": [
            {
                "path": "snapshot/version-before.json",
                "role": "api_version_before",
                "kind": "raw",
                "url": version_url,
            },
            {
                "path": "snapshot/version-after.json",
                "role": "api_version_after",
                "kind": "raw",
                "url": version_url,
            },
            {
                "path": "snapshot/recruiting-query.json",
                "role": "recruiting_comparison_query",
                "kind": "raw",
                "url": comparison_url,
            },
        ],
    }
    for page in pages:
        manifest["files"].append({
            "path": page["path"],
            "role": "studies_page",
            "kind": "raw",
            "url": page["url"],
            "bytes": page["bytes"],
            "study_count": page["study_count"],
            "total_count": page["total_count"],
        })
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"pages={len(pages)} archive_sha256={archive}")


if __name__ == "__main__":
    main()
