"""Offline checks for this documentation scaffold; Python standard library only."""

import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
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
SCAFFOLD_STATE = {
    "access_status": "reported_open_file_access_unverified",
    "terms_status": "not_reviewed",
    "download_status": "not_downloaded",
    "provenance_status": "study_metadata_only",
    "overlap_status": "unresolved_at_patient_level",
    "release": None,
    "sha256": None,
}
METADATA_AUDITED_STATE = {
    "access_status": "open_processed_file_metadata_verified",
    "terms_status": "pdc_public_data_terms_reviewed",
    "download_status": "headers_inspected_in_memory",
    "provenance_status": "study_version_and_linkage_metadata_verified",
    "overlap_status": "catalog_overlap_measured_analysis_membership_unresolved",
    "release": "1",
    "sha256": None,
}
METADATA_AUDITED_IDS = {"PDC000358", "PDC000360", "PDC000362"}
METADATA_AUDIT_SOURCES = {"S12", "S13"}
# Created only by the owner, in the checkout that runs; never committed.
OWNER_ATTESTATIONS = "registries/pilot-001-owner-attestations.json"


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
        # A status is earned as a complete documented transition, not by mixing
        # individual values from the two states. Header inspection cannot earn
        # a checksum for an entire data file.
        metadata_audited = any(
            value is not None and row.get(field) == value
            for field, value in METADATA_AUDITED_STATE.items()
        )
        state = METADATA_AUDITED_STATE if metadata_audited else SCAFFOLD_STATE
        state_name = "metadata-audited" if metadata_audited else "scaffold"
        for field, expected in state.items():
            if row.get(field) != expected:
                errors.append(f"{label}: invalid {field} for {state_name} state")
        if metadata_audited:
            if (label not in METADATA_AUDITED_IDS or row.get("assay") != "proteome"
                    or row.get("pilot_role") != "candidate"):
                errors.append(f"{label}: not eligible for metadata-audited state")
            if (not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs)
                    or not METADATA_AUDIT_SOURCES <= set(refs)):
                errors.append(f"{label}: metadata-audited state requires source references S12 and S13")
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


def attestation_errors(root):
    """Fail if Git tracks or stages the owner's attestation file, in any letter case."""
    reason = ""
    try:
        # No pathspec: under GIT_LITERAL_PATHSPECS, which `git --literal-pathspecs` exports to hooks,
        # a magic pathspec would match nothing and the check would pass. LC_ALL=C keeps Git's
        # messages in English for the check below.
        listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, timeout=60,
                                env={**os.environ, "LC_ALL": "C", "LANGUAGE": "C"})
        if listed.returncode != 0:
            reason = next(iter(listed.stderr.decode("utf-8", "replace").strip().splitlines()), "")
    except (OSError, subprocess.SubprocessError) as error:
        listed, reason = None, str(error)
    if listed is None or listed.returncode != 0:
        # A tree outside any repository, e.g. an export, has nothing to commit. Git decides that, not
        # the lack of a .git entry in root: a parent repository can track root too.
        outside = listed is None or reason.startswith("fatal: not a git repository")
        if outside and not (root / ".git").exists():
            return []
        return [f"{OWNER_ATTESTATIONS}: cannot check whether Git tracks it"
                + (f" (git: {reason})" if reason else "")]
    tracked = listed.stdout.decode("utf-8", "replace").split("\0")
    if any(name.casefold() == OWNER_ATTESTATIONS.casefold() for name in tracked):
        return [f"{OWNER_ATTESTATIONS}: owner-only file is tracked or staged; remove it from Git"]
    return []


def validate(root=ROOT):
    return registry_errors(root) + local_link_errors(root) + attestation_errors(root)


if __name__ == "__main__":
    problems = validate()
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)
    print("PASS: source/dataset registries, local Markdown links and untracked owner attestations "
          "(offline scaffold checks only).")
