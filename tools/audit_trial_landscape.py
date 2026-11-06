#!/usr/bin/env python3
"""Bounded, memory-only ClinicalTrials.gov language audit; aggregate output only.

The committed specification is the sole source of query, fields and dictionary.
No registry rows, identifiers, matched text or response bodies are written.
Offline verification checks internal consistency and current code/spec hashes;
it cannot reconstruct counts from the deliberately unretained source responses.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "protocols/trial-landscape-keywords-v1.json"
SCRIPT_PATH = Path(__file__).resolve()
CHICAGO = ZoneInfo("America/Chicago")
TIMEOUT_SECONDS = 30
HEX256 = re.compile(r"[0-9a-f]{64}\Z")
NCT_ID = re.compile(r"NCT[0-9]{8}\Z")
BUCKET_NAMES = (
    "biomarker_generic", "brca", "hrd", "folate_receptor_alpha",
    "platinum_resistant", "platinum_refractory",
)


class AuditError(ValueError):
    """A fixed, nonsensitive audit failure message, never source content."""


def _require(condition, message):
    if not condition:
        raise AuditError(message)


def _strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "Duplicate JSON object key.")
        result[key] = value
    return result


def _reject_constant(value):
    raise AuditError("Nonfinite JSON value.")


def _decode_json(raw):
    try:
        return json.loads(raw, object_pairs_hook=_strict_pairs,
                          parse_constant=_reject_constant)
    except (ValueError, UnicodeError, RecursionError):
        raise AuditError("Invalid JSON document.") from None


def _canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _integer(value, message):
    _require(type(value) is int and value >= 0, message)
    return value


def _keys(value, expected, message):
    _require(isinstance(value, dict) and set(value) == set(expected), message)


def load_spec():
    """Read only the repository's prespecified dictionary and request plan."""
    try:
        spec = _decode_json(SPEC_PATH.read_bytes())
    except OSError:
        raise AuditError("Cannot read audit specification.") from None
    _require(isinstance(spec, dict) and spec.get("schema_version") == 1,
             "Invalid audit specification.")
    _keys(spec.get("buckets"), BUCKET_NAMES, "Invalid bucket specification.")
    _require(spec.get("phase_order") == ["EARLY_PHASE1", "PHASE1", "PHASE2",
             "PHASE3", "PHASE4", "NA"], "Invalid phase specification.")
    _require(spec.get("missing_phase_label") == "NOT_REPORTED",
             "Invalid missing-phase specification.")
    return spec


def normalize_text(text):
    """NFKC/casefold/alpha/dash/whitespace normalization fixed in the spec."""
    _require(isinstance(text, str), "Text field has invalid type.")
    text = unicodedata.normalize("NFKC", text).casefold().replace("α", "alpha")
    text = "".join(" " if c == "-" or unicodedata.category(c) == "Pd" else c
                   for c in text)
    return " ".join(text.split())


def canonical_phase(phases, spec=None):
    """Return one mutually exclusive, canonical combined-phase category."""
    spec = load_spec() if spec is None else spec
    if phases is None or phases == []:
        return spec["missing_phase_label"]
    _require(isinstance(phases, list), "Phase field has invalid type.")
    _require(all(isinstance(p, str) and p in spec["phase_order"] for p in phases),
             "Unknown or malformed phase value.")
    _require(len(set(phases)) == len(phases), "Duplicate phase value.")
    _require("NA" not in phases or len(phases) == 1, "NA mixed with real phases.")
    return "+".join(p for p in spec["phase_order"] if p in phases)


def _field(protocol, path):
    value = protocol
    for component in path.split("."):
        if value is None:
            return None
        _require(isinstance(value, dict), "Protocol module has invalid type.")
        value = value.get(component)
    return value


def _protocol(study):
    _require(isinstance(study, dict), "Study has invalid type.")
    protocol = study.get("protocolSection")
    _require(isinstance(protocol, dict), "Missing or malformed protocol section.")
    identifier = _field(protocol, "identificationModule.nctId")
    _require(isinstance(identifier, str) and NCT_ID.fullmatch(identifier) is not None,
             "Missing or malformed registry identifier.")
    _require(_field(protocol, "statusModule.overallStatus") == "RECRUITING",
             "Study status violates fixed query.")
    _require(_field(protocol, "designModule.studyType") == "INTERVENTIONAL",
             "Study type violates fixed query.")
    return protocol, identifier


def _patterns(spec):
    return {bucket: [re.compile(r"(?<!\w)" + re.escape(normalize_text(term)) +
                                r"(?!\w)") for term in terms]
            for bucket, terms in spec["buckets"].items()}


def classify_study(study, spec=None):
    """Classify one in-memory record without returning its ID or source text."""
    spec = load_spec() if spec is None else spec
    return _classify_study(study, spec, _patterns(spec))


def _classify_study(study, spec, patterns):
    protocol, _ = _protocol(study)
    missing = set()
    eligibility = set()
    other = set()
    for name, path in spec["text_fields"].items():
        value = _field(protocol, path)
        if value is None:
            items = []
        elif name in spec["array_text_fields"]:
            _require(isinstance(value, list), "Text array has invalid type.")
            _require(all(isinstance(item, str) for item in value),
                     "Text array item has invalid type.")
            items = value
        else:
            _require(isinstance(value, str), "Text field has invalid type.")
            items = [value]
        normalized = [normalize_text(item) for item in items]
        if not any(normalized):
            missing.add(name)
        hits = eligibility if name == "eligibility" else other
        for bucket, expressions in patterns.items():
            if any(expression.search(item) for item in normalized
                   for expression in expressions):
                hits.add(bucket)
    buckets = eligibility | other
    groups = {name for name, members in spec["groups"].items()
              if buckets.intersection(members)}
    return {"phase": canonical_phase(_field(protocol, "designModule.phases"), spec),
            "buckets": buckets, "groups": groups, "missing_text_fields": missing,
            "eligibility_buckets": eligibility, "other_buckets": other}


def _empty_counts(spec):
    return {
        "total_studies": 0, "phase_counts": {},
        "bucket_counts": dict.fromkeys(spec["buckets"], 0),
        "group_counts": dict.fromkeys(spec["groups"], 0),
        "any_keyword": 0, "no_keyword": 0,
        "biomarker_platinum_overlap": dict.fromkeys(
            ("both", "biomarker_only", "platinum_only", "neither"), 0),
        "missing_text_fields": dict.fromkeys(spec["text_fields"], 0),
        "eligibility_bucket_counts": dict.fromkeys(spec["buckets"], 0),
        "other_text_bucket_counts": dict.fromkeys(spec["buckets"], 0),
    }


def _add(counts, result):
    counts["total_studies"] += 1
    phases = counts["phase_counts"]
    phases[result["phase"]] = phases.get(result["phase"], 0) + 1
    for output, source in (("bucket_counts", "buckets"), ("group_counts", "groups"),
                           ("missing_text_fields", "missing_text_fields"),
                           ("eligibility_bucket_counts", "eligibility_buckets"),
                           ("other_text_bucket_counts", "other_buckets")):
        for key in result[source]:
            counts[output][key] += 1
    counts["any_keyword" if result["buckets"] else "no_keyword"] += 1
    bio = "any_biomarker_bucket" in result["groups"]
    platinum = "any_platinum_bucket" in result["groups"]
    cell = ("both" if bio and platinum else "biomarker_only" if bio else
            "platinum_only" if platinum else "neither")
    counts["biomarker_platinum_overlap"][cell] += 1


def aggregate_studies(studies, spec=None):
    """Aggregate a synthetic or memory-only iterable; reject duplicate IDs."""
    spec = load_spec() if spec is None else spec
    counts, seen, patterns = _empty_counts(spec), set(), _patterns(spec)
    for study in studies:
        _, identifier = _protocol(study)
        _require(identifier not in seen, "Duplicate registry identifier.")
        seen.add(identifier)
        _add(counts, _classify_study(study, spec, patterns))
    return counts


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise AuditError("Unexpected registry redirect.")


def fetch_json(url, max_bytes):
    """One bounded request; failures never contain bodies, URLs or row text."""
    request = urllib.request.Request(url, headers={"Accept": "application/json",
        "User-Agent": "ProjectAsma-AggregateTrialLanguageAudit/1"})
    try:
        with urllib.request.build_opener(_NoRedirect()).open(
                request, timeout=TIMEOUT_SECONDS) as response:
            _require(response.status == 200, "Unexpected registry HTTP status.")
            raw = response.read(max_bytes + 1)
    except AuditError:
        raise
    except Exception:
        raise AuditError("Registry request failed.") from None
    _require(len(raw) <= max_bytes, "Registry response exceeds byte limit.")
    return _decode_json(raw), _sha(raw)


def _request_plan(spec):
    return {key: spec[key] for key in
            ("endpoint", "version_endpoint", "query", "request_options", "fields")}


def _study_url(spec, token=None):
    parameters = dict(spec["query"])
    parameters.update(spec["request_options"])
    parameters["fields"] = ",".join(spec["fields"])
    if token is not None:
        parameters["pageToken"] = token
    return spec["endpoint"] + "?" + urllib.parse.urlencode(parameters)


def _version(response):
    _keys(response, ("apiVersion", "dataTimestamp"), "Invalid API version response.")
    _require(isinstance(response["apiVersion"], str) and
             re.fullmatch(r"[A-Za-z0-9._+-]{1,64}", response["apiVersion"]),
             "Invalid API version value.")
    value = response["dataTimestamp"]
    _require(isinstance(value, str) and
             re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}", value),
             "Invalid API data timestamp.")
    try:
        # The API documents this suffix-free value as UTC.
        datetime.fromisoformat(value)
    except ValueError:
        raise AuditError("Invalid API data timestamp.") from None
    return dict(response)


def _implementation_hashes():
    return {"tools/audit_trial_landscape.py": _sha(SCRIPT_PATH.read_bytes())}


def _payload_hash(snapshot):
    return _sha(_canonical_bytes({k: v for k, v in snapshot.items()
                                  if k != "aggregate_payload_sha256"}))


def fetch_audit(fetch_json=None):
    """Fetch fixed-query pages with injectable transport for offline tests."""
    spec = load_spec()
    specification_hash = _sha(SPEC_PATH.read_bytes())
    implementation_hashes = _implementation_hashes()
    transport = globals()["fetch_json"] if fetch_json is None else fetch_json
    max_bytes = spec["limits"]["max_response_bytes"]
    started = datetime.now(timezone.utc)
    before, before_hash = transport(spec["version_endpoint"], max_bytes)
    before = _version(before)
    counts, seen, tokens, pages = _empty_counts(spec), set(), set(), []
    patterns = _patterns(spec)
    token, expected_total = None, None
    for page_index in range(spec["limits"]["max_pages"]):
        url = _study_url(spec, token)
        response, response_hash = transport(url, max_bytes)
        _require(isinstance(response, dict), "Registry page has invalid type.")
        studies = response.get("studies")
        _require(isinstance(studies, list), "Registry page lacks a studies list.")
        if page_index == 0 or "totalCount" in response:
            total = _integer(response.get("totalCount"), "Invalid registry totalCount.")
            if expected_total is None:
                expected_total = total
            _require(total == expected_total, "Registry totalCount changed during audit.")
        else:
            total = None
        for study in studies:
            _, identifier = _protocol(study)
            _require(identifier not in seen, "Duplicate registry identifier.")
            seen.add(identifier)
            _add(counts, _classify_study(study, spec, patterns))
        _require(counts["total_studies"] <= expected_total,
                 "Retrieved count exceeds registry totalCount.")
        next_token = response.get("nextPageToken")
        _require(next_token is None or isinstance(next_token, str),
                 "Malformed registry pagination token.")
        _require(next_token is None or bool(next_token.strip()),
                 "Malformed registry pagination token.")
        pages.append({"url": url, "response_sha256": response_hash,
                      "study_count": len(studies), "total_count": total,
                      "has_next_page": bool(next_token)})
        if not next_token:
            break
        _require(next_token not in tokens, "Repeated registry pagination token.")
        tokens.add(next_token)
        token = next_token
    else:
        raise AuditError("Registry pagination exceeded page limit.")
    _require(counts["total_studies"] == expected_total,
             "Terminal retrieved count differs from registry totalCount.")
    after, after_hash = transport(spec["version_endpoint"], max_bytes)
    after = _version(after)
    _require(before == after, "Registry version changed during audit.")
    _require(_sha(SPEC_PATH.read_bytes()) == specification_hash,
             "Specification changed during audit.")
    _require(_implementation_hashes() == implementation_hashes,
             "Implementation changed during audit.")
    completed = datetime.now(timezone.utc)
    snapshot = {
        "schema_version": 1,
        "specification": {"path": "protocols/trial-landscape-keywords-v1.json",
                          "name": spec["name"], "sha256": specification_hash},
        "request_plan": _request_plan(spec),
        "implementation_sha256": implementation_hashes,
        "provenance": {
            "started_at_utc": started.isoformat(),
            "completed_at_utc": completed.isoformat(),
            "started_at_chicago": started.astimezone(CHICAGO).isoformat(),
            "completed_at_chicago": completed.astimezone(CHICAGO).isoformat(),
            "chicago_date": started.astimezone(CHICAGO).date().isoformat(),
            "timezone": "America/Chicago",
            "runtime": {"python_version": platform.python_version(),
                        "unicode_version": unicodedata.unidata_version},
            "api_version_before": {"url": spec["version_endpoint"],
                                   "response_sha256": before_hash, "response": before},
            "api_version_after": {"url": spec["version_endpoint"],
                                  "response_sha256": after_hash, "response": after},
            "api_total_count": expected_total,
            "page_count": len(pages), "pages": pages,
        },
        "counts": counts,
    }
    snapshot["aggregate_payload_sha256"] = _payload_hash(snapshot)
    check_snapshot(snapshot)
    return snapshot


def _check_counts(counts, spec):
    _keys(counts, _empty_counts(spec), "Unexpected aggregate count fields.")
    total = _integer(counts["total_studies"], "Invalid aggregate total.")
    for name, value in counts.items():
        if isinstance(value, dict):
            for count in value.values():
                _integer(count, "Invalid aggregate count.")
                _require(count <= total, "Aggregate count exceeds total.")
        else:
            _integer(value, "Invalid aggregate count.")
    for name in ("bucket_counts", "eligibility_bucket_counts", "other_text_bucket_counts"):
        _keys(counts[name], spec["buckets"], "Unexpected bucket count fields.")
    _keys(counts["group_counts"], spec["groups"], "Unexpected group count fields.")
    _keys(counts["missing_text_fields"], spec["text_fields"],
          "Unexpected missing-text count fields.")
    phases = counts["phase_counts"]
    _require(isinstance(phases, dict), "Invalid phase counts.")
    for phase, count in phases.items():
        _require(isinstance(phase, str), "Invalid phase category.")
        values = None if phase == spec["missing_phase_label"] else phase.split("+")
        _require(canonical_phase(values, spec) == phase and count > 0,
                 "Invalid canonical phase count.")
    _require(sum(phases.values()) == total, "Phase counts do not sum to total.")
    _require(counts["any_keyword"] + counts["no_keyword"] == total,
             "Keyword partition does not sum to total.")
    cells = counts["biomarker_platinum_overlap"]
    _keys(cells, ("both", "biomarker_only", "platinum_only", "neither"),
          "Unexpected overlap count fields.")
    _require(sum(cells.values()) == total and cells["neither"] == counts["no_keyword"],
             "Overlap partition does not reconcile.")
    groups, buckets = counts["group_counts"], counts["bucket_counts"]
    _require(groups["any_biomarker_bucket"] == cells["both"] + cells["biomarker_only"]
             and groups["any_platinum_bucket"] == cells["both"] + cells["platinum_only"],
             "Group counts do not reconcile with overlap cells.")
    for group, members in spec["groups"].items():
        _require(max(buckets[m] for m in members) <= groups[group] <=
                 min(total, sum(buckets[m] for m in members)),
                 "Group union violates bucket bounds.")
    for bucket in buckets:
        eligibility = counts["eligibility_bucket_counts"][bucket]
        other = counts["other_text_bucket_counts"][bucket]
        _require(max(eligibility, other) <= buckets[bucket] <= eligibility + other,
                 "Text-origin counts violate bucket union bounds.")
    return total


def check_snapshot(snapshot):
    """Offline schema/arithmetic/provenance integrity; no network requests."""
    spec = load_spec()
    _keys(snapshot, ("schema_version", "specification", "request_plan",
                    "implementation_sha256", "provenance", "counts",
                    "aggregate_payload_sha256"), "Unexpected snapshot fields.")
    _require(type(snapshot["schema_version"]) is int and snapshot["schema_version"] == 1,
             "Unsupported snapshot schema.")
    expected_spec = {"path": "protocols/trial-landscape-keywords-v1.json",
                     "name": spec["name"], "sha256": _sha(SPEC_PATH.read_bytes())}
    _require(snapshot["specification"] == expected_spec, "Specification hash mismatch.")
    _require(snapshot["request_plan"] == _request_plan(spec), "Fixed request plan mismatch.")
    _require(snapshot["implementation_sha256"] == _implementation_hashes(),
             "Implementation hash mismatch.")
    total = _check_counts(snapshot["counts"], spec)
    provenance = snapshot["provenance"]
    _keys(provenance, ("started_at_utc", "completed_at_utc", "started_at_chicago",
                      "completed_at_chicago", "chicago_date", "timezone", "runtime",
                      "api_version_before", "api_version_after", "api_total_count",
                      "page_count", "pages"), "Unexpected provenance fields.")
    _require(provenance["timezone"] == "America/Chicago", "Invalid local timezone.")
    runtime = provenance["runtime"]
    _keys(runtime, ("python_version", "unicode_version"), "Unexpected runtime fields.")
    for value in runtime.values():
        _require(isinstance(value, str) and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value),
                 "Invalid runtime version.")
    dates = []
    for stem in ("started", "completed"):
        value = provenance[stem + "_at_utc"]
        _require(isinstance(value, str), "Invalid execution timestamp.")
        try:
            instant = datetime.fromisoformat(value)
        except ValueError:
            raise AuditError("Invalid execution timestamp.") from None
        _require(instant.tzinfo is not None and instant.utcoffset().total_seconds() == 0,
                 "Execution timestamp is not UTC.")
        _require(provenance[stem + "_at_chicago"] == instant.astimezone(CHICAGO).isoformat(),
                 "Local execution timestamp mismatch.")
        dates.append(instant)
    _require(dates[0] <= dates[1] and provenance["chicago_date"] ==
             dates[0].astimezone(CHICAGO).date().isoformat(), "Invalid execution interval.")
    for name in ("api_version_before", "api_version_after"):
        entry = provenance[name]
        _keys(entry, ("url", "response_sha256", "response"), "Unexpected version fields.")
        _require(entry["url"] == spec["version_endpoint"], "Version request URL mismatch.")
        _check_hash(entry["response_sha256"])
        _version(entry["response"])
    _require(provenance["api_version_before"]["response"] ==
             provenance["api_version_after"]["response"], "Registry source version drift.")
    _integer(provenance["api_total_count"], "Invalid registry total count.")
    _require(provenance["api_total_count"] == total, "API total disagrees with aggregate.")
    pages = provenance["pages"]
    _require(isinstance(pages, list) and 1 <= len(pages) <= spec["limits"]["max_pages"],
             "Invalid aggregate page count.")
    _integer(provenance["page_count"], "Invalid aggregate page count.")
    _require(provenance["page_count"] == len(pages), "Aggregate page count mismatch.")
    urls, retrieved = set(), 0
    for index, page in enumerate(pages):
        _keys(page, ("url", "response_sha256", "study_count", "total_count", "has_next_page"),
              "Unexpected page provenance fields.")
        url = page["url"]
        _require(isinstance(url, str), "Invalid page request URL.")
        if index == 0:
            _require(url == _study_url(spec), "First page request URL mismatch.")
        else:
            try:
                query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query,
                                              keep_blank_values=True, strict_parsing=True)
            except ValueError:
                raise AuditError("Invalid page request URL.") from None
            token = query.get("pageToken")
            _require(isinstance(token, list) and len(token) == 1 and bool(token[0].strip()),
                     "Invalid continuation request token.")
            _require(url == _study_url(spec, token[0]), "Continuation request URL mismatch.")
        _require(url not in urls, "Repeated page request URL.")
        urls.add(url)
        _check_hash(page["response_sha256"])
        retrieved += _integer(page["study_count"], "Invalid page study count.")
        if index == 0 or page["total_count"] is not None:
            _integer(page["total_count"], "Invalid page total count.")
            _require(page["total_count"] == total, "Page total count drift.")
        _require(type(page["has_next_page"]) is bool and
                 page["has_next_page"] == (index < len(pages) - 1),
                 "Invalid terminal page provenance.")
    _require(retrieved == total, "Page study counts do not sum to total.")
    _check_hash(snapshot["aggregate_payload_sha256"])
    _require(snapshot["aggregate_payload_sha256"] == _payload_hash(snapshot),
             "Aggregate payload hash mismatch.")


def _check_hash(value):
    _require(isinstance(value, str) and HEX256.fullmatch(value) is not None,
             "Malformed response or payload hash.")


def render_report_table(snapshot):
    """Deterministic Markdown table of every retained aggregate count."""
    check_snapshot(snapshot)
    counts = snapshot["counts"]
    lines = ["| Measure | Count |", "| --- | ---: |"]
    for label, value in (("Total studies", counts["total_studies"]),
                         ("API total count", snapshot["provenance"]["api_total_count"]),
                         ("API study pages", snapshot["provenance"]["page_count"]),
                         ("Any dictionary bucket", counts["any_keyword"]),
                         ("No dictionary bucket", counts["no_keyword"])):
        lines.append(f"| {label} | {value} |")
    for group in ("phase_counts", "bucket_counts", "group_counts",
                  "biomarker_platinum_overlap", "missing_text_fields",
                  "eligibility_bucket_counts", "other_text_bucket_counts"):
        for label, value in sorted(counts[group].items()):
            lines.append(f"| {group}: {label} | {value} |")
    for index, page in enumerate(snapshot["provenance"]["pages"], 1):
        lines.append(f"| Page {index} retrieved studies | {page['study_count']} |")
    return "\n".join(lines) + "\n"


def _read_snapshot(path):
    try:
        with Path(path).open("rb") as source:
            raw = source.read(4 * 1024 * 1024 + 1)
    except OSError:
        raise AuditError("Cannot read aggregate snapshot.") from None
    _require(len(raw) <= 4 * 1024 * 1024, "Aggregate snapshot exceeds size limit.")
    snapshot = _decode_json(raw)
    check_snapshot(snapshot)
    return snapshot


def _atomic_write(path, text):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".trial-aggregate-", delete=False) as output:
            temporary = output.name
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        temporary = None
    except OSError:
        raise AuditError("Cannot write aggregate output.") from None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument("--check-snapshot", metavar="PATH", help="verify a saved aggregate offline")
    operation.add_argument("--render-report-table", metavar="PATH", help="render saved aggregate numbers offline")
    operation.add_argument("--compare", metavar="PATH", help="fetch live and fail on count or source-version drift")
    parser.add_argument("--output", metavar="PATH", help="atomically write aggregate JSON or rendered Markdown")
    args = parser.parse_args(argv)
    try:
        if args.check_snapshot:
            _require(args.output is None, "Output is not supported for snapshot checks.")
            _read_snapshot(args.check_snapshot)
            text = "Aggregate snapshot checks passed.\n"
        elif args.render_report_table:
            text = render_report_table(_read_snapshot(args.render_report_table))
        else:
            previous = _read_snapshot(args.compare) if args.compare else None
            snapshot = fetch_audit()
            if previous is not None:
                _require(snapshot["counts"] == previous["counts"] and
                         snapshot["provenance"]["api_version_before"]["response"] ==
                         previous["provenance"]["api_version_before"]["response"],
                         "Live comparison found count or source-version drift.")
            text = json.dumps(snapshot, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        if args.output:
            _atomic_write(args.output, text)
        else:
            sys.stdout.write(text)
        return 0
    except AuditError as error:
        # Only these literal diagnostics may cross the CLI output boundary.
        # Even an injected transport's AuditError must not disclose its text.
        safe_messages = {
            "Registry totalCount changed during audit.",
            "Registry version changed during audit.",
            "Live comparison found count or source-version drift.",
            "Implementation hash mismatch.", "Specification hash mismatch.",
            "Specification changed during audit.", "Implementation changed during audit.",
        }
        reason = str(error) if str(error) in safe_messages else "Validation, request or output failure."
        print("Trial landscape audit failed: " + reason, file=sys.stderr)
        return 1
    except Exception:
        # Fail closed even on an unforeseen malformed-input or transport error.
        # A traceback could contain registry text or a URL with identifiers.
        print("Trial landscape audit failed: unexpected processing error.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
