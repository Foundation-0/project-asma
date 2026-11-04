# Claims ledger

Every material statement in the public README, [mission](docs/mission.md), and
[pilot 001](protocols/pilot-001.md) is assigned one label:

| Label | Meaning |
| --- | --- |
| **PROVEN** | Written proof in this repository |
| **VERIFIED** | Finite check replayable with a recorded command (not a proof) |
| **KNOWN** | Cited from a primary source; exact citation given |
| **CONJECTURE** | Hypothesis, design target, or open question — not established here |

**Honesty:** "Not found in our searches" is never "new". Nothing here is peer
reviewed unless explicitly stated. Software checks on **synthetic or fixture inputs**
are VERIFIED for software behaviour only; they are **not** independently reproduced
on study data and do not establish clinical performance.

**Counts (2026-11-04):** PROVEN **0** · VERIFIED **18** · KNOWN **14** · CONJECTURE **8**

---

## PROVEN

*(None. This repository does not contain formal mathematical proofs of scientific claims.)*

---

## VERIFIED

Re-run from the repository root unless noted. Network audits read study sources in
memory and emit aggregates only; they require explicit authorization and appropriate
execution context where noted in [AGENTS.md](AGENTS.md).

| ID | Claim | Re-check |
| --- | --- | --- |
| V01 | Registry JSON schema and cross-references validate offline | `python3 tools/validate.py` |
| V02 | The full Python `unittest` suite passes on the committed tree | `python3 -m unittest discover -s tests -v` |
| V03 | **179** R test assertions pass on **synthetic fixtures** (41 input, 87 core, 51 model) | [Synthetic validation commands](docs/pilot-001-synthetic-validation.md#commands) |
| V04 | Full **100-repeat** synthetic model pipeline completes on abstract fixtures | Same synthetic validation doc (pinned container) |
| V05 | Source-adapter **19** R bridge assertions pass on **generated XLSX/matrix fixtures** | [Source-adapter commands](docs/pilot-001-source-adapter.md#commands-and-continuation) |
| V06 | **40** combined-runtime execution-condition checks observed on rebuilt image (2026-11-04 rerun) | Source-adapter doc; `python3 -m unittest tests.test_execution_conditions -v` covers probe logic offline |
| V07 | Registry `implementation_sha256` entries match **current** file bytes, or a **documented stale** hash (`implementation_hash_drift`) tied to a verifiable git revision | `python3 tools/check_implementation_hashes.py` (requires git; reports OK / STALE / UNKNOWN) |
| V08 | Published discovery-score AUROC **0.8088507878** vs printed **0.83**; tolerance **0.02** not met | `python3 tools/verify_published_auc.py` (network; reads pinned public workbooks in memory; see [result](docs/pilot-001-score-verification-result.md)) |
| V09 | Validation-capacity binomial bounds from documented cohort counts (e.g. 13 sensitive → 79.4% one-sided 95% LB if perfect) | `python3 tools/analyze_validation_capacity.py` and `python3 -m unittest tests.test_validation_capacity -v` |
| V10 | PDC catalog overlap aggregates match registry | `python3 tools/audit_pdc_metadata.py` (network) |
| V11 | Published workbook membership and panel joins match registry | `python3 tools/audit_published_cohorts.py` (network) |
| V12 | Matrix-header diagnostic aggregates match registry | `python3 tools/audit_matrix_headers.py` (network) |
| V13 | Author archive header linkage aggregates match registry | `python3 tools/audit_author_archive.py` (network) |
| V14 | Author feature member CRC and 64/64 panel coverage counts match registry | `python3 tools/audit_author_features.py` (network; bounded inspection) |
| V15 | Panel symbol `make.names` alteration count 0/64 | `python3 tools/audit_panel_names.py` (network) |
| V16 | MMC1 validation cohort feature lists contain all 64 panel symbols once each | `python3 tools/audit_validation_panel_coverage.py` (network) |
| V17 | Held-out evaluation helpers behave on **artificial** test cases | `python3 -m unittest tests.test_evaluate_heldout -v` |
| V18 | Git does not track or stage owner attestation file (when `git` available) | `python3 tools/validate.py` |

**PR #30 runtime summary (2026-11-04):** the **207** `unittest` cases, **179** R
assertions, and **40** execution controls are **VERIFIED only on synthetic or fixture
inputs** under the pinned runtime recorded in [roadmap](docs/roadmap.md) and linked
registries. They have **not** been independently reproduced outside that recorded run
and do **not** substitute for study-data execution.

---

## KNOWN

| ID | Claim | Citation |
| --- | --- | --- |
| K01 | Discovery fivefold-CV AUC **0.83** (95% CI 0.77–0.90) for primary refractory HGSOC | Chowdhury et al., *Cell* 2023, https://doi.org/10.1016/j.cell.2023.07.004 |
| K02 | Six PDC PTRC HGSOC studies in the catalog: **PDC000358/360/362** proteome (pilot candidates) and **PDC000357/359/361** phosphoproteome (context only); PDC open-data terms **CC BY 4.0** | [datasets.json](registries/datasets.json); PDC GraphQL `submitter_id_name` rechecked 2026-11-04 |
| K03 | NLM supplemental MMC1 (clinical) and MMC4 (panel/membership) associated with **CC BY-NC-ND 4.0** | Article version record cited in [data-use](docs/pilot-001-data-use.md) |
| K04 | Publisher correction to supplemental legend text | Chowdhury et al., *Cell* **187**, 1016 (2024), https://doi.org/10.1016/j.cell.2024.01.016 (S11 in [sources.json](registries/sources.json)) |
| K05 | Author analysis scripts exist at inspected commit; not executed here | WangLab-MSSM/CPTAC_Ovarian_Chemo_Response commit `48357fd…` (see [pilot 001](protocols/pilot-001.md)) |
| K06 | Primary refractory vs later platinum-resistant recurrence are distinct endpoints | Stated in protocol from primary literature review ([feasibility audit](docs/pilot-001-feasibility-audit.md)) |
| K07 | Published discovery score sheet row counts and class balance (135 rows; 52 refractory / 83 sensitive) | Paper supplementary locations S95/S99 as recorded in [score verification protocol](protocols/pilot-001-score-verification.md) |
| K08 | PDC processed-file metadata and version-1 study headers were readable on audited dates | [Input resolution](docs/pilot-001-input-resolution.md); registry summaries |
| K09 | Six frozen patient keys appear in both published frozen nonoverlap scores and eligible discovery scores | [Input resolution](docs/pilot-001-input-resolution.md) — membership fact, independence not proven |
| K10 | Recovered author discovery matrix header matches 168 response-labelled rows and 135 score keys | [Independent progress](docs/pilot-001-independent-progress.md); registry V13/V14 |
| K11 | 64 panel symbols appear once among 8,800 feature rows in pinned author member (bounded audit) | [Author feature registry](registries/pilot-001-author-feature-summary.json) |
| K12 | 64/64 panel symbols in published MMC1 association lists for three cohort feature sets | [Validation panel registry](registries/pilot-001-validation-panel-coverage.json) |
| K13 | Copyright Act s. 29 fair-dealing framework described for conditional Canadian research-use assessment | *CCH Canadian Ltd. v. Law Society of Upper Canada*, 2004 SCC 13 (quoted in [data-use](docs/pilot-001-data-use.md)) |
| K14 | Mission tribute: project honours Asma Ansari | [README](README.md) opening — biographical, not a research cohort claim |

---

## CONJECTURE

| ID | Statement | Notes |
| --- | --- | --- |
| C01 | Full Figure 3D model reproduction is achievable with permitted inputs | [Pilot 001](protocols/pilot-001.md) target; Gates 0–2 open |
| C02 | Independent reconstruction will agree with published metrics within ≤0.02 AUC when fairly compared | Predeclared tolerance; not tested on study data |
| C03 | Author-released matrix can support the selected reconstruction after transformation gaps close | Naming/feature coverage improved; workspace provenance open |
| C04 | Conditional Canadian fair-dealing route applies to a future narrow research run | Requires verified execution context ([data-use](docs/pilot-001-data-use.md)) |
| C05 | Consolidated [source request](templates/pilot-001-source-request.md) may resolve missing inputs if sent by owner | Draft only; no message sent |
| C06 | Future confirmatory validation could meet a 98% specificity lower bound | Requires ~149 independent sensitive patients ([validation capacity](docs/pilot-001-validation-capacity.md)) |
| C07 | Independent evaluation could eventually inform research decisions with appropriate review | Mission aspiration; no current clinical result |
| C08 | Prior-art searches listed in audits did not locate a corrected MMC4 artifact | Documented as "not found", **not** "novel" |

---

## What this ledger does not claim

- Clinical validity, diagnostic accuracy, treatment benefit, or individual patient guidance.
- Peer review, regulatory clearance, or institutional ethics approval.
- Complete patient independence across cohorts (overlap remains partially unresolved).
- That software fixture success implies study-data model performance.
- That the AUROC discrepancy proves an error in Chowdhury et al.
- A project-wide license grant for third-party study files (see [NOTICE](NOTICE)).

Update this file when README, mission, or protocol statements change.
