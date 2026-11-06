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

**Counts (2026-11-06):** PROVEN **0** · VERIFIED **27** · KNOWN **35** · CONJECTURE **23**

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
| V02 | The full Python `unittest` suite passes with no failures in a **git checkout** (`259` cases, all run). Without a matching git top level (source archive without ``.git``, or the same tree nested inside another repository), the same command still passes but **skips 3** cases that need this project's git history: owner-attestation tracking (`test_validate`) and **2** stale-hash checker tests (`test_implementation_hashes`) | `python3 -m unittest discover -s tests -v` |
| V03 | **181** R test assertions pass on **synthetic fixtures** (41 input, 88 core, 52 model) | [Synthetic validation commands](docs/pilot-001-synthetic-validation.md#commands) |
| V04 | Full **100-repeat** synthetic model pipeline completes on abstract fixtures | Same synthetic validation doc (pinned container) |
| V05 | Source-adapter **19** R bridge assertions pass on **generated XLSX/matrix fixtures** | [Source-adapter commands](docs/pilot-001-source-adapter.md#commands-and-continuation) |
| V06 | **40** combined-runtime execution-condition checks observed on rebuilt image (2026-11-04 rerun) | Source-adapter doc; `python3 -m unittest tests.test_execution_conditions -v` covers probe logic offline |
| V07 | Registry `implementation_sha256` entries match **current** file bytes, or a **documented stale** hash (`implementation_hash_drift`) tied to a verifiable git revision | `python3 tools/check_implementation_hashes.py` (**git checkout** with top level equal to the repository root; exits **1** with an error otherwise; reports OK / STALE / UNKNOWN when history is available) |
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
| V19 | Original synthetic two-state counterexamples, a hypothetical selection-bound calculation, exact sign-flip enumeration and a missing-clone sampling example give the values in the [identifiability record](docs/compartment-identifiability.md) | `python3 tools/analyze_compartment_identifiability.py`; invented inputs, not study analysis or a new biological result |
| V20 | The dated, canonical-parent IEDB metadata queries return 7 CDR2 and 2 CDR2L positive HLA-II MS assay annotations across 3 and 2 references respectively | [Recorded replay command and limits](docs/antigen-discovery-round2-2026-11-05.md#what-was-actually-checked), [query manifest](registries/antigen-metadata-audit-2026-11-05.json); metadata only, not unique ligand validation or anti-Yo receptor recognition |
| V23 | Pilot 001 discovery AUROC discrepancy candidates (a)–(e) on released scores: ties=0; polarity reverse=0.191; Mann–Whitney=trapezoidal=0.80885; DeLong and stratified bootstrap 95% CIs both contain printed 0.83 while the point estimate remains 0.80885; fold-wise mean AUC not testable from public material | `python3 tools/analyze_auc_discrepancy.py` (network); `python3 -m unittest tests.test_auc_discrepancy -v`; [analysis](docs/pilot-001-auc-discrepancy.md); [registry](registries/pilot-001-auc-discrepancy.json) |

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
| K90 | Institutional history and article affiliations distinguish the Toronto/Beaumont gynecologic oncologist from the FIU biochemist; P is not an exclusion rule | [Rosen survey identity evidence](docs/research/barry-rosen.md#identity-and-attribution), S90–S91 |
| K91 | GSE51831 public series metadata links PMID 24982872 and lists expression files; data reuse and model-training rights remain unresolved | [Rosen resource assessment](docs/research/barry-rosen.md#data-code-and-reuse-observed-availability), S92–S93 |
| K93 | The NK leukemogenesis paper names Boas Rosen at NCI-Frederick; the glutaminase preprint/journal maps Rosen to FIU, so neither establishes the clinician’s ovarian immunotherapy work | [2026-11-05 primary identity checks](docs/research/barry-rosen.md#high-value-cross-checks), S96–S97 |
| K92 | The 2013 MSI risk-factor paper has an indexed retraction; retained as bibliography only | [Notice checks](docs/research/barry-rosen.md#corrections-and-related-records) |
| K14 | Mission tribute: project honours Asma Ansari | [README](README.md) opening — biographical, not a research cohort claim |
| K15 | Petitpré study methods/access qualifications and review history are documented in the [source audit](docs/anti-yo-frontier-2026-11-04.md#source-audit) | S37–S38; exact PDF pages and hashes in [sources.json](registries/sources.json) |
| K16 | Anti-Yo antigen biology, HLA associations and context-dependent immune responses have substantial prior art | S39–S45, S48, S50–S51, S76; [frontier prior-art table](docs/anti-yo-frontier-2026-11-04.md#prior-art-and-the-remaining-gap) and molecular handoff |
| K17 | ALS compartment methods and the ROHHAD AEGIS preprint are cross-disease precedents, not anti-Yo validation | S46–S47; AEGIS is explicitly a preprint; [frontier](docs/anti-yo-frontier-2026-11-04.md) |
| K18 | Longitudinal clone tracking, KELIM and CA125-triggered intervention studies address different evidence questions | S02, S52–S53; [handoff](docs/research-handoff-2026-11-04.md) H01–H03 |
| K19 | Spatial/perturbational profiling and small organoid studies motivate further evaluation without establishing assay-guided clinical benefit | S03, S54–S55; handoff H04–H06 |
| K20 | TrialGPT workflow findings and PRO-TECT clinical workflow outcomes do not establish benefit from a new standalone application | S56–S57; handoff H07–H08 |
| K21 | Anti-Yo checkpoint-inhibitor case evidence is a limited safety research signal | S49; five selected cases, no incidence estimate or individual treatment inference |
| K22 | FDA notices describe dated, assay/context-specific US indications; target-heterogeneity studies are separate evidence | S04–S05, S59–S62; [molecular handoff](docs/molecular-research-handoff-2026-11-04.md) |
| K23 | MUC16, replication-stress, adaptive-resistance, ADC and ascites leads span preclinical, observational and prospective evidence | S58, S63–S64, S66–S69; molecular handoff; no new target validation |
| K24 | Reviewed code licenses and catalog pointers have source-specific limits | S65, S70–S75; handoffs and registry record what was inspected; no dataset-use grant inferred |

---

## CONJECTURE

| ID | Statement | Notes |
| --- | --- | --- |
| C01 | Full Figure 3D model reproduction is achievable with permitted inputs | [Pilot 001](protocols/pilot-001.md) target; Gate 0 partially closed (2026-11-05); Gates 1–2 open |
| C02 | Independent reconstruction will agree with published metrics within ≤0.02 AUC when fairly compared | Predeclared tolerance; not tested on study data |
| C03 | Author-released matrix can support the selected reconstruction after transformation gaps close | Naming/feature coverage improved; workspace provenance open |
| C04 | Conditional Canadian fair-dealing route applies to a future narrow research run on the owner's MacBook in Ontario | Condition (a) attestation met for **2026-11-05 only**; still needs macOS preflight (b), no row-level leakage (c), and fresh attestation for later run dates ([data-use](docs/pilot-001-data-use.md#assessment-for-owner-macbook-in-canada-gate-0-q1-update-2026-11-05)) |
| C05 | The owner's consolidated [source request](templates/pilot-001-source-request.md) may resolve missing inputs | Sent by owner; canonical [sending record](docs/pilot-001-source-request-handoff.md); answers and research gates remain open |
| C06 | Future confirmatory validation could meet a 98% specificity lower bound | Requires ~149 independent sensitive patients ([validation capacity](docs/pilot-001-validation-capacity.md)) |
| C07 | Independent evaluation could eventually inform research decisions with appropriate review | Mission aspiration; no current clinical result |
| C90 | The ranked Rosen-survey questions may yield useful research artifacts | [Candidate/deferred questions](docs/research/barry-rosen.md#ranked-project-asma-research-fit-questions); not executed or adopted |
| C08 | Prior-art searches listed in audits did not locate a corrected MMC4 artifact | Documented as "not found", **not** "novel" |
| C09 | Validated receptor/antigen/presenter evidence would help resolve competing anti-Yo CD4 explanations | Proposed H1–H5 matrix in the [frontier proposal](docs/anti-yo-frontier-2026-11-04.md); untested |
| C10 | Presenting context may separate tumor response from neural injury | Mechanistic comparison proposed, no separation or safe intervention demonstrated |
| C11 | Antigen processing may uncouple abundance from immune recognition | Conditional hypothesis; no empirical chain established here |
| C12 | Synthetic identifiability checks and proposed annotation/control sensitivities can improve the next study's design | Calculations executed; their practical research value is a judgment; no study reanalysis |
| C13 | Broader longitudinal, spatial, organoid, navigation and symptom avenues merit the ranked next tasks | [Research handoff](docs/research-handoff-2026-11-04.md); prioritization is not measured benefit or novelty |
| C14 | Assay-aware molecular, perturbation and adaptive-resistance work may contribute to the expanded mission | [Molecular handoff](docs/molecular-research-handoff-2026-11-04.md); proposals and stop rules, no individual target assignment |
| C20 | The printed discovery 0.83 may be a mean of fold-wise AUCs or may use predictions that are not identical to the released `FFPE_pred_scores` sheet | Leading open explanation after VERIFIED rejection of ties/polarity/ordinary rounding; see [discrepancy analysis](docs/pilot-001-auc-discrepancy.md) |

---

## Discovery-round update, 2026-11-05

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| K25 | KNOWN | Public epitope-catalog annotations narrow the previous CDR2L HLA-II search gap; presentation is distinct from anti-Yo receptor specificity | [Antigen audit](docs/antigen-discovery-round2-2026-11-05.md); exact protein/class/reference joins and remaining validation limits |
| K26 | KNOWN | CDR adaptor biology, ovarian-knockout measurement limits and CMV-associated CD4 states provide relevant alternative explanations | [Tumor review](docs/tumor-discovery-round2-2026-11-05.md) and [causal review](docs/causal-discovery-round2-2026-11-05.md); model, preparation and disease transfers remain explicit |
| C15 | CONJECTURE | CDR2L dependence can arise from direct recognition, indirect antigen delivery or both | [Round-2 synthesis](docs/discovery-round2-2026-11-05.md); conceptual alternatives, no observed anti-Yo experiment |
| C16 | CONJECTURE | Linked recognition or historically antiviral cytotoxic cells could explain portions of the immune response without the assumed direct CDR2L pathway | Antigen and causal reviews; no anti-Yo demonstration, and helper function does not establish injury |
| C17 | CONJECTURE | Ligand/receptor mapping, source/presenter separation and independent injury measurements are the highest-value next comparisons | Round-2 priorities are research judgments, not discoveries or clinical recommendations |

## Evidence-graph update, 2026-11-05

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V21 | VERIFIED | An offline evidence graph matches 22 scoped requests against 24 curated assertions, retaining 15 unresolved requests and one scoped negative result | [Executed result](docs/evidence-graph-result-2026-11-05.md); regression expectations are manually specified, not an independent scientific accuracy benchmark |
| C18 | CONJECTURE | Separating ligand/source dependence from injury mechanism improves the next research comparison | Same result; direct CDR2L recognition and indirect injury can coexist, but neither has been established by the graph |

## Rosen treatment-sequence update, 2026-11-05

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V22 | VERIFIED | In 84 invented parameter cases, proportional surgery gives equal endpoints in both orders; capped fixed-residual surgery gives 54 chemo-first-higher and 30 equal endpoints, with equal final resistant fractions in all 84 | `python3 tools/analyze_treatment_sequence.py`; [protocol, exact algebra and results](docs/research/rosen-treatment-sequence-assumptions.md). Synthetic finite check, not clinical evidence or full Gu-model reproduction; growth and unequal-target reversals retained. |
| K27 | KNOWN | Fixed-fraction surgery and comparison of growth/cell-kill assumptions are explicit prior art for ovarian treatment-sequence modeling | Kohandel, Sivaloganathan and Oza (2006), DOI https://doi.org/10.1016/j.jtbi.2006.02.001, abstract inspected; S119. No novelty claim. |
| C19 | CONJECTURE | Quantitative pre/postoperative burden, anatomy, composition and timing may distinguish competing surgery response maps and improve subsequent model comparisons | [Prospective design and stop rule](docs/research/rosen-treatment-sequence-assumptions.md#the-next-discriminating-research-question). Not an adopted study, validated measurement system or causal treatment-policy estimate. |

## Pilot 001 Gate 0 update, 2026-11-05

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| K32 | KNOWN | Pilot 001 Gate 0 owner decisions recorded 2026-11-05 (Q1–Q5); study data on owner's MacBook in **Ontario**; shared cloud (AWS us-east-1) CI/artificial dry runs only; execution-context attestation verbatim on #31 **met condition (a) for 2026-11-05 only**; Ontario provincial note closed in data-use; Dropbox matrix **conditional go** when (b) preflight and (c) no row-level leakage met; Q4 **not externally reviewed**; Q5 exploratory cohort | [Roadmap Gate 0](docs/roadmap.md#pilot-001--gate-0-owner-decisions-2026-11-05); [#31 Gate 0](https://github.com/Foundation-0/project-asma/issues/31#issuecomment-6662111371), [#31 Q1](https://github.com/Foundation-0/project-asma/issues/31#issuecomment-6662169564), [#31 attestation](https://github.com/Foundation-0/project-asma/issues/31#issuecomment-6662220698) |

## Virtual Human vision and website update, 2026-11-05

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V24 | VERIFIED | The merged Virtual Human reaction/intervention increment passed 153 Python tests and JavaScript checks; its optional bridge matched twelve synthetic Asma operator outcomes within the declared absolute tolerance | [Dated vision/current-capability record](docs/virtual-human-vision.md#the-foundation-we-actually-have) links pinned reports and commands. Exact conservation and independent numerical comparisons establish bounded software properties, not a proof-assistant implementation, complete human model or clinical efficacy. |
| C21 | CONJECTURE | Connected biological models with explicit evidence, machine-checkable mathematical obligations and independent empirical validation could improve research, experiment/trial design, medicine development and understanding of the body | [Long-term vision](docs/virtual-human-vision.md). All applications are conditional aspirations. Formal correctness cannot establish biological completeness, empirical validity or patient benefit; synthesis/manufacturing and future personal models require separate capabilities and evidence. |

## Educational site update, 2026-11-05

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V25 | VERIFIED | The site's two reference-coordinate assets pass offline identity, topology and omission checks; derivation from pinned archive files is reproducible | [Structure provenance](docs/site-structure-sources.md); `python3 tools/check_site_models.py`. Checks establish the selected coordinate representation, not biological dynamics, original crystallographic accuracy or clinical performance. |
| V26 | VERIFIED | The browser assumption experiment obeys the exact toy-model boundaries across its 10,000 integer slider combinations | `node tools/test_research_lab.cjs`; [research experiment](docs/research/rosen-treatment-sequence-assumptions.md). Artificial material only; no patient parameters, treatment advice or full Gu-model reproduction. |
| K28 | KNOWN | RCSB entries 1TRZ and 1BNA describe a crystalline biosynthetic human-insulin assembly and a synthetic DNA dodecamer respectively; public archive/API data have CC0 terms | Sources S122–S124 and [selection/omission record](docs/site-structure-sources.md). Displayed insulin is one selected molecule; displayed DNA is not a human genome fragment. |

## Pilot 001 exploratory subset plan, 2026-11-06

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V28 | VERIFIED | For 8 refractory versus 13 sensitive patients, the exact Mann–Whitney null rejects AUROC = 0.5 one-sided at the 5% level only for U ≥ **76** of 104 pairs (AUROC ≥ 19/26 ≈ 0.7308; exact p = 0.04452, and 0.05210 at U = 75); for 11 versus 17 the region is U ≥ 130 of 187; two-sided 95% Clopper–Pearson intervals for every k/8 and j/13 are tabulated as correctly rounded roots of the exact binomial tails (exact rational sign tests, platform-independent bytes) | `python3 tools/plan_exploratory_subset_design.py --check`; `python3 -m unittest tests.test_exploratory_subset_design -v`; [design record](registries/pilot-001-exploratory-subset-design.json). Offline calculation on documented counts; no score was read and no model performance was measured |
| K30 | KNOWN | The paper's frozen "independent" prediction set holds 34 tumours after neoadjuvant exclusion (P183), 13 of them from discovery patients (P145 with the audit's exact joins); its printed metrics are AUC 0.79 (95% CI 0.63–0.96) and sensitivity 0.25 at 98% specificity (P33), consistent with 3 of the sheet's 12 refractory tumours | Chowdhury et al., *Cell* 2023 (S01) as quoted in [open-questions section 4](docs/pilot-001-open-questions.md); sheet class counts 22/12 in the [supplement audit](registries/pilot-001-supplement-summary.json). The released sheet is not established as the exact input to the printed metrics |
| K31 | KNOWN | Of those 34 patients, **21 (13 sensitive / 8 refractory)** appear in no discovery record of any kind, 28 (17/11) are outside the eligible discovery set, and the remaining 40 scored frozen patients (29/11: the 27 overlap-sheet patients plus 13) all have a discovery record | Registry fields `patient_keys_not_observed_in_all_discovery` (21) and `…_in_eligible_discovery` (28) in the [supplement audit](registries/pilot-001-supplement-summary.json); class splits from the 2026-10-25 bounded inspection in [open-questions section 4](docs/pilot-001-open-questions.md), inherited and not rerun. Membership facts; not proof of an untouched or independent evaluation set |
| C22 | CONJECTURE | Within that 21-patient subset, refractory-prediction scores rank refractory above sensitive tumours better than chance | [Pre-registered plan](protocols/pilot-001-exploratory-subset-plan.md): one-sided exact test at α = 0.05 with critical value U ≥ 76 of 104 (AUROC ≥ 19/26), patient bootstrap and DeLong intervals, threshold fixed on the other 40 patients. Not executed; exploratory only under Gate 0 Q5 (K32); neither outcome is validation, reproduction or a clinical result |

## What this ledger does not claim

- Clinical validity, diagnostic accuracy, treatment benefit, or individual patient guidance.
- Peer review, regulatory clearance, or institutional ethics approval.
- Complete patient independence across cohorts (overlap remains partially unresolved).
- That software fixture success implies study-data model performance.
- That the AUROC discrepancy proves an error in Chowdhury et al.
- A project-wide license grant for third-party study files (see [NOTICE](NOTICE)).

Update this file when README, mission, or protocol statements change.
