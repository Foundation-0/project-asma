# Registries

- [sources.json](sources.json): dated primary-source metadata, claim locators,
  takeaways, verification route, and limits. S01–S14 are stable local IDs.
- [datasets.json](datasets.json): six candidate/context PDC studies and provenance
  gaps. These are catalog records, not downloaded datasets or patient manifests.
- [pilot-001-linkage-summary.json](pilot-001-linkage-summary.json): executed,
  aggregate-only comparison of public version-1 PDC metadata. Regenerate with
  `python3 tools/audit_pdc_metadata.py`; no row-level identifiers are emitted.
- [pilot-001-supplement-summary.json](pilot-001-supplement-summary.json): pinned
  public workbook provenance, recovered-panel checksum, clinical eligibility
  counts and exact prediction-membership joins. Regenerate with
  `python3 tools/audit_published_cohorts.py`; source workbooks stay in memory.

The source and dataset registries use `schema_version: 1` and a list under
`sources` or `datasets`.
IDs must be unique; dataset `source_ids` must resolve to source IDs. URLs use
HTTPS; `checked_on` is an ISO date. `null` release/checksum means not established,
not missing data to be guessed. A verified `release: "1"` refers to the PDC study
version, not a reproduction environment or verified full-file checksum. Public
study UUIDs and request/response fingerprints are in the aggregate summary.

Source verification states: `full_text_reviewed`, `page_reviewed`,
`code_inspected`, `metadata_reviewed`, or `partial`. Read `limitations` and
`reviewed_via`; a mirror review is not a successful fetch from the original URL.
S09 documentation remains partial. S11 correction text was verified through
NCBI BioC after publisher/PMC routes failed. The code was inspected, not run.
PDC ID/name mappings were verified through read-only metadata queries
and the [official publication listing](https://pdc.cancer.gov/pdc/publications).

Context-only phosphoproteome records retain the original unreviewed states.
The three proteome candidates now have a coherent metadata-audited state: open
processed-file metadata verified, PDC public-data terms reviewed, headers
inspected in memory, study version/linkage metadata checked, and catalog overlap
measured while analysis membership still needs source reconciliation. This state
requires S12/S13 evidence, `release: "1"` and `sha256: null`; it does not claim a
full data download, a verified matrix checksum or independent patients. The
[resolution report](../docs/pilot-001-input-resolution.md) defines its limits.
Private patient relationships still belong in an authorized
[manifest](../templates/provenance-manifest.md), never in the public catalog.

Run `python3 tools/validate.py` from the root after edits. The current validator
enforces the original scaffold state and this specific metadata-audited state;
intentionally extend its rules and tests for later authorized stages. It checks required fields,
types, ID/reference/date/status rules, and simple inline local Markdown file and
heading links. It skips fenced code, external URLs, and reference-style links.
It does not verify external availability, source accuracy, access terms, data
integrity, patient overlap, or scientific validity. Keep links simple and review
external sources manually before making new claims.
