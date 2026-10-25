# Registries

- [sources.json](sources.json): dated primary-source metadata, claim locators,
  takeaways, verification route, and limits. S01–S25 are stable local IDs.
- [datasets.json](datasets.json): six candidate/context PDC studies and provenance
  gaps. These are catalog records, not downloaded datasets or patient manifests.

The first six records below (linkage, supplement, score verification, matrix
header, author archive and author feature) come from network audits that read
study files or patient-level metadata in memory. Regenerating them follows the
bounded-inspection rule in the [agent guidance](../AGENTS.md): in memory,
aggregates only, recording what was read and why.

- [pilot-001-linkage-summary.json](pilot-001-linkage-summary.json): executed,
  aggregate-only comparison of public version-1 PDC metadata. Regenerate with
  `python3 tools/audit_pdc_metadata.py`; no row-level identifiers are emitted.
- [pilot-001-supplement-summary.json](pilot-001-supplement-summary.json): pinned
  public workbook provenance, recovered-panel checksum, clinical eligibility
  counts and exact prediction-membership joins. Regenerate with
  `python3 tools/audit_published_cohorts.py`; source workbooks stay in memory.
- [pilot-001-score-verification.json](pilot-001-score-verification.json): executed
  preliminary discovery AUROC, exact comparisons, source/implementation/protocol
  hashes and environment. The [result report](../docs/pilot-001-score-verification-result.md)
  records the discrepancy and pending external review. No patient-level scores
  are retained; this is not model regeneration or independent validation.
- [pilot-001-matrix-header-summary.json](pilot-001-matrix-header-summary.json):
  executed exact matrix-header/clinical-label diagnostic, with bounded header
  hashes and source/catalog provenance. Regenerate with
  `python3 tools/audit_matrix_headers.py`. Clinical-NA matches are separated from
  response-labelled patient links; whole-matrix checksums remain unverified.
- [pilot-001-author-archive-summary.json](pilot-001-author-archive-summary.json):
  recovered author discovery-matrix header linkage to all 168 response-labelled
  measurements and 135 published score keys. Regenerate with
  `python3 tools/audit_author_archive.py`. The ZIP directory/member metadata and
  header are pinned. This historical header-only artifact is unchanged; the
  following artifact extends the inspection to the complete selected member.
- [pilot-001-author-feature-summary.json](pilot-001-author-feature-summary.json):
  complete-member CRC verification, newly observed SHA-256 and exact coverage of
  all 64 panel symbols, once each, among 8,800 feature rows. Regenerate under the
  bounded source-inspection contract with `python3 tools/audit_author_features.py`.
  Abundance fields are discarded without numerical conversion or analysis; full
  archive integrity, transformation history and later reuse terms remain open.
- [pilot-001-panel-name-summary.json](pilot-001-panel-name-summary.json): count of
  pinned panel symbols that R's `make.names` would alter (0 of 64), with source
  and tool hashes. Regenerate with `python3 tools/audit_panel_names.py`; it prints
  counts only, no symbols.
- [pilot-001-reconstruction-runtime.json](pilot-001-reconstruction-runtime.json):
  selected R 4.4.3, glmnet 4.1-8, randomForest 4.7-1.2 and XGBoost 1.7.8.1 source
  archives, computed hashes and declared license metadata. This historical
  selection record predates execution and remains unchanged.
- [pilot-001-synthetic-validation.json](pilot-001-synthetic-validation.json):
  executed synthetic-only assertions and full model-run coverage, installed
  package/toolchain inventory, runtime identity and implementation hashes.
  [Source pins](../runtime/synthetic-packages.json) include dependencies and
  license metadata; the [report](../docs/pilot-001-synthetic-validation.md) gives
  commands and limits. No fixture predictions, model weights or clinical metrics
  are retained.

- [pilot-001-source-adapter-runtime.json](pilot-001-source-adapter-runtime.json):
  executed build and inventory for the combined CPython/R image, including required
  modules, preserved R versions, missing optional modules and source/notice pins.
- [pilot-001-source-adapter-validation.json](pilot-001-source-adapter-validation.json):
  generated XLSX/deflate fixtures parsed into the R pipeline, 18 bridge assertions,
  a complete fivefold model repetition, observed parser environment and source
  hashes. Input fingerprints under `fixture_provenance` belong to artificial fixtures.
- [pilot-001-execution-conditions.json](pilot-001-execution-conditions.json):
  40 observed combined-runtime controls, limited outer-executor observations and
  explicit unresolved context. It is not research-use clearance. See the
  [source-adapter report](../docs/pilot-001-source-adapter.md).

Recorded implementation hashes describe the code that ran. Five records (score
verification, matrix header, author archive, author feature and source-adapter
validation) name the shared loader `tools/audit_published_cohorts.py` at SHA-256
`b0ab4ab1340139fb221346a14895526f8d62eb105eae098e46b7c4d1fa3f2b52`. After those
runs, its `Workbook.xml` gained a pre-parse expat pass that rejects workbook
parts carrying a document type or entity declaration, in any encoding expat
reads, and reports unreadable XML with a fixed audit error. Accepted parts parse
unchanged, so the current file's hash differs while the records keep the hash
that ran. A rerun records the new hash.

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
NCBI BioC and rechecked in byte-pinned NLM XML after publisher/PMC routes failed.
The pinned NLM S3 legend conflicts with the article's panel references; the
[independent report](../docs/pilot-001-independent-progress.md) records the
content evidence and remaining corrected-artifact gap. The code was inspected, not run.
S18–S21 record the dependency sources read for the
[code-audit addendum](../docs/pilot-001-code-audit-addendum.md); S19 and S21 are
unofficial mirrors. S22–S25 record the data-use and runtime-selection sources
for the reconstruction; they were numbered S18–S21 on their original branch.
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
