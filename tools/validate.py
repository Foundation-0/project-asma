"""Offline checks for this documentation scaffold; Python standard library only."""

import datetime as dt
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
COMMON = {"id", "title", "url", "checked_on"}
SOURCE_FIELDS = COMMON | {"kind", "verification", "reviewed_via", "locator", "takeaway", "limitations"}
DATA_FIELDS = COMMON | {
    "source_ids", "cohort", "preservation", "assay", "histotype", "pilot_role",
    "access_status", "terms_status", "download_status", "provenance_status",
    "release", "sha256", "overlap_status", "notes",
}
VERIFICATIONS = {"full_text_reviewed", "page_reviewed", "code_inspected", "metadata_reviewed", "partial"}
KINDS = {"paper", "regulatory_notice", "evidence_summary", "code", "data_documentation", "data_catalog", "correction"}


def https_url(value):
    try:
        parsed = urlsplit(value) if isinstance(value, str) else None
    except ValueError:
        return False
    return bool(parsed and parsed.scheme == "https" and parsed.netloc and not re.search(r"\s", value))


def load_rows(root, name, required, errors):
    try:
        data = json.loads((root / "registries" / f"{name}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"{name}: {exc}")
        return []
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        errors.append(f"{name}: expected schema_version 1")
        return []
    rows = data.get(name)
    if not isinstance(rows, list) or not rows:
        errors.append(f"{name}: expected a nonempty list")
        return []
    valid, seen = [], set()
    for index, row in enumerate(rows):
        label = f"{name}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label}: expected object")
            continue
        for key in sorted(required - row.keys()):
            errors.append(f"{label}: missing {key}")
        for key in required - {"source_ids", "release", "sha256"}:
            if not isinstance(row.get(key), str) or not row[key].strip():
                errors.append(f"{label}: {key} must be nonempty text")
        identifier = row.get("id")
        pattern = r"S\d{2,}" if name == "sources" else r"PDC\d{6}"
        if not isinstance(identifier, str) or not re.fullmatch(pattern, identifier):
            errors.append(f"{label}: invalid id")
        elif identifier in seen:
            errors.append(f"{label}: duplicate id {identifier}")
        else:
            seen.add(identifier)
        if not https_url(row.get("url")):
            errors.append(f"{label}: invalid HTTPS URL")
        try:
            value = row.get("checked_on")
            if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError
            dt.date.fromisoformat(value)
        except ValueError:
            errors.append(f"{label}: invalid checked_on date")
        valid.append(row)
    return valid


def registry_errors(root):
    errors = []
    sources = load_rows(root, "sources", SOURCE_FIELDS, errors)
    datasets = load_rows(root, "datasets", DATA_FIELDS, errors)
    source_ids = {row["id"] for row in sources if isinstance(row.get("id"), str)}
    for row in sources:
        label = str(row.get("id"))
        if (not isinstance(row.get("verification"), str) or row["verification"] not in VERIFICATIONS
                or not isinstance(row.get("kind"), str) or row["kind"] not in KINDS):
            errors.append(f"{label}: invalid source kind/verification")
        if not https_url(row.get("reviewed_via")):
            errors.append(f"{label}: invalid reviewed_via URL")
    allowed = {
        "cohort": {"discovery", "validation"}, "preservation": {"FFPE", "frozen"},
        "assay": {"proteome", "phosphoproteome"}, "histotype": {"HGSOC"},
        "pilot_role": {"candidate", "context_only"},
        "access_status": {"reported_open_file_access_unverified"},
        "terms_status": {"not_reviewed"}, "download_status": {"not_downloaded"},
        "provenance_status": {"study_metadata_only"},
        "overlap_status": {"unresolved_at_patient_level"},
    }
    for row in datasets:
        label = str(row.get("id"))
        refs = row.get("source_ids")
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) for ref in refs):
            errors.append(f"{label}: source_ids must be a nonempty list of IDs")
        elif len(set(refs)) != len(refs) or not set(refs) <= source_ids:
            errors.append(f"{label}: duplicate or unknown source reference")
        for field, choices in allowed.items():
            if not isinstance(row.get(field), str) or row[field] not in choices:
                errors.append(f"{label}: invalid {field}")
        if row.get("release") is not None or row.get("sha256") is not None:
            errors.append(f"{label}: pre-ingestion release/checksum must be null")
    return errors


def without_fences(text):
    return re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$", "", text)


def heading_ids(text):
    result, counts = set(), {}
    for title in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", without_fences(text)):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        result.add(f"{slug}-{count}" if count else slug)
        counts[slug] = count + 1
    return result


def local_link_errors(root):
    errors, root = [], root.resolve()
    for source in sorted(root.rglob("*.md")):
        if ".git" in source.relative_to(root).parts:
            continue
        text = without_fences(source.read_text(encoding="utf-8"))
        for dest in re.findall(r"\[[^\]]*\]\((<[^>]+>|[^\s)]+)\)", text):
            dest = dest.strip("<>")
            parsed = urlsplit(dest)
            if parsed.scheme or parsed.netloc:
                continue
            target = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source
            label = f"{source.relative_to(root)}: {dest}"
            if not target.is_relative_to(root):
                errors.append(f"{label}: link escapes repository")
            elif not target.exists():
                errors.append(f"{label}: missing local target")
            elif parsed.fragment and target.suffix == ".md":
                if unquote(parsed.fragment) not in heading_ids(target.read_text(encoding="utf-8")):
                    errors.append(f"{label}: missing heading")
    return errors


def validate(root=ROOT):
    return registry_errors(root) + local_link_errors(root)


if __name__ == "__main__":
    problems = validate()
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)
    print("PASS: source/dataset registries and local Markdown links (offline scaffold checks only).")
