# Registries

- [sources.json](sources.json): dated primary-source metadata, claim locators,
  takeaways, verification route, and limits. S01–S11 are stable local IDs.
- [datasets.json](datasets.json): six candidate/context PDC studies and provenance
  gaps. These are catalog records, not downloaded datasets or patient manifests.

Both files use `schema_version: 1` and a list under `sources` or `datasets`.
IDs must be unique; dataset `source_ids` must resolve to source IDs. URLs use
HTTPS; `checked_on` is an ISO date. `null` release/checksum means not established,
not missing data to be guessed. Study IDs do not pin a particular data release.

Source verification states: `full_text_reviewed`, `page_reviewed`,
`code_inspected`, `metadata_reviewed`, or `partial`. Read `limitations` and
`reviewed_via`; a mirror review is not a successful fetch from the original URL.
S09 documentation remains partial. S11 correction text was verified through
NCBI BioC after publisher/PMC routes failed. The code was inspected, not run.
PDC ID/name mappings were verified through read-only metadata queries
and the [official publication listing](https://pdc.cancer.gov/pdc/publications).

Dataset statuses are deliberately conservative: `reported_open_file_access_unverified`,
`not_reviewed` terms, `not_downloaded`, `study_metadata_only`, and
`unresolved_at_patient_level`. The Open catalog label is not an ingestion or
redistribution authorization. Update these fields with evidence when the gates
are met; never infer patient independence from different study IDs. File checksums
and patient relationships belong in an authorized
[private manifest](../templates/provenance-manifest.md), not this public catalog.

Run `python3 tools/validate.py` from the root after edits. The current validator
enforces this scaffold's pre-ingestion states; intentionally extend its rules
and tests when a later authorized stage changes them. It checks required fields,
types, ID/reference/date/status rules, and simple inline local Markdown file and
heading links. It skips fenced code, external URLs, and reference-style links.
It does not verify external availability, source accuracy, access terms, data
integrity, patient overlap, or scientific validity. Keep links simple and review
external sources manually before making new claims.
