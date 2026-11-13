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

**Counts (2026-11-13):** PROVEN **0** · VERIFIED **42** · KNOWN **49** · CONJECTURE **27**

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
| V02 | The full Python `unittest` suite passes with no failures in a **git checkout** (`457` cases, all run). Without a matching git top level (source archive without ``.git``, or the same tree nested inside another repository), the same command still passes but **skips 3** cases that need this project's git history: owner-attestation tracking (`test_validate`) and **2** stale-hash checker tests (`test_implementation_hashes`) | `python3 -m unittest discover -s tests -v` |
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
| V27 | The nine-assay IEDB class-II batch replay (manifest [accessed_at_utc](registries/cdr2-hla-ii-evidence-map-2026-11-06.json)) returns seven CDR2 and two CDR2L rows whose **assay IDs**, **parent_source_antigen_iri** (UNIPROT:Q01850 / Q86X02), **pubmed_id**, **mhc_class**, **mhc_allele_name**, **mhc_allele_evidence**, and **qualitative_measure** match `expected_rows` — not raw HTTP SHA-256 | Identity replay in [evidence map](docs/cdr2-hla-ii-evidence-map-2026-11-06.md#machine-checkable-reproduction); optional `response_sha256_snapshot` is point-in-time only; metadata check, not ligand or anti-Yo receptor validation |
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
| K01 | Discovery fivefold-CV AUC **0.83** (95% CI 0.77–0.90) for primary refractory HGSOC | Chowdhury et al., *Cell* 2023, paragraph P33 and Figure 3 panel D3, https://doi.org/10.1016/j.cell.2023.07.004 ; S174. The released-sheet AUROC is V44 |
| K02 | Six PDC PTRC HGSOC studies in the catalog: **PDC000358/360/362** proteome (pilot candidates) and **PDC000357/359/361** phosphoproteome (context only); PDC open-data terms **CC BY 4.0** | [datasets.json](registries/datasets.json); PDC GraphQL `submitter_id_name` rechecked 2026-11-04 |
| K03 | NLM supplemental MMC1 (clinical) and MMC4 (panel/membership) associated with **CC BY-NC-ND 4.0** | Article version record cited in [data-use](docs/pilot-001-data-use.md) |
| K04 | Publisher correction to supplemental legend text | Chowdhury et al., *Cell* **187**, 1016 (2024), https://doi.org/10.1016/j.cell.2024.01.016 (S11 in [sources.json](registries/sources.json)) |
| K05 | Author analysis scripts exist at inspected commit; not executed here | WangLab-MSSM/CPTAC_Ovarian_Chemo_Response commit `48357fd…` (see [pilot 001](protocols/pilot-001.md)) |
| K06 | Primary refractory vs later platinum-resistant recurrence are distinct endpoints | Stated in protocol from primary literature review ([feasibility audit](docs/pilot-001-feasibility-audit.md)) |
| K07 | Published discovery score sheet row counts and class balance (135 rows; 52 refractory / 83 sensitive) | Paragraphs P177 and P183 print 83 sensitive and 52 refractory. Paragraph P179 defines the score as the probability the tumour is refractory. The numeral 135 is their sum, the public sheet row count, and the Figure 3 discovery-panel label. S174. [Score verification protocol](protocols/pilot-001-score-verification.md) |
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

## Recruiting trial-landscape snapshot, 2026-11-05 America/Chicago

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V29 | VERIFIED | The live fixed ClinicalTrials.gov query returned 592 unique recruiting/interventional records; 155 matched at least one prespecified biomarker bucket, 120 at least one platinum bucket and 50 both | [Report and exact request](docs/trial-landscape-2026-11-05.md); [aggregate certificate](results/trial-landscape-2026-11-05/certificate.json); `python3 results/trial-landscape-2026-11-05/verify.py`. Retrieved 2026-11-05 America/Chicago (2026-11-06 UTC); finite metadata counting, not trial outcomes or eligibility. Offline verification cannot reconstruct unretained source classifications; live reruns may differ. |
| K33 | KNOWN | ClinicalTrials.gov documents search expansion, projected fields, pagination and a UTC processing timestamp; source terms require attribution and describe modification/update obligations and copyright limits; listing does not mean government approval of study safety/science | Primary API documentation, terms and disclaimer, S126–S128; [source and reuse assessment](docs/trial-landscape-2026-11-05.md#reuse-attribution-and-source-limits). No blanket source-license or clinical-validity claim. |

## CDR2 HLA-II evidence map, 2026-11-06

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| K29 | KNOWN | Nine curated IEDB class-II MS assay joins link human CDR2 (seven records, five source systems in the map) and CDR2L (two records); none establish anti-Yo CD4 receptor recognition or neural injury from that ligand evidence alone | [Evidence map](docs/cdr2-hla-ii-evidence-map-2026-11-06.md); identity-field IEDB replay [V27](docs/cdr2-hla-ii-evidence-map-2026-11-06.md#machine-checkable-reproduction); parent audit [V20](docs/antigen-discovery-round2-2026-11-05.md#what-was-actually-checked) |

## CDR2L named-sequence audit, 2026-11-06

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V30 | VERIFIED | Both selected IEDB CDR2L HLA-II peptides match canonical Q86X02 at curated coordinates and the explicitly checked unreviewed CDR2L entry A0ACI8RKQ2; neither matches the explicitly checked CDR2 entry Q01850, including I/L-equivalent comparison | [Executed named-candidate result](docs/cdr2l-sequence-adjudication-2026-11-06.md), [aggregate certificate](registries/cdr2l-sequence-audit-2026-11-06.json), `python3 tools/audit_cdr2l_sequences.py`. Three named reference sequences only; remote database search unavailable, no global uniqueness claim, no spectra/allotype/receptor/injury validation. Sources S129–S131 and earlier source map. |

## Convergence-note extract, 2026-11-11

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V31 | VERIFIED | One-sided 95% lower specificity bounds for eight stated sensitive denominators, at 0, 1 and 2 false positives, match the binomial tail. The bound reaches 98% at n = 149 with 0 false positives and at n = 236 with 1. Two-sided 95% intervals for 9/26, 163/166, 7/20 and 78/80 match the intervals written in the 11 November notes | `python3 tools/check_stated_specificity_bounds.py --check`; [extract](docs/google-bio-convergence-2026-11-11.md#specificity-bounds-on-stated-denominators). Arithmetic on stated fractions. Not a cohort audit and not measured performance. The audited discovery split remains 83 sensitive by 52 refractory |
| V32 | VERIFIED | Of six sensitive/refractory pairs written in the 11 November notes, only 83 and 52 match a class-count pair in the supplement summary on both numbers. The summary has no class-count pair 10/11, 22/20, 44/42, 115/83 or 13/8 | `python3 tools/check_stated_specificity_bounds.py --check`. [Cohort table](docs/google-bio-convergence-2026-11-11.md#stated-cohort-pairs-against-the-supplement-audit). Comparison with the existing audit. Not a new workbook read. The 13/8 split remains the one already recorded as K31 |
| K34 | KNOWN | Europe PMC titles and DOIs checked on 2026-11-11 name the ER-sheet papers and four further papers cited beside the notes | [Title table](docs/google-bio-convergence-2026-11-11.md#papers-named-in-the-notes). Titles and DOIs. Residue sentences and abstracts are K36. The AlphaGenome record and the CDR2L span are K37 |
| K35 | KNOWN | Europe PMC titles on 2026-11-11 identify the 2018 anti-Yo HLA association paper (PMID 29306402) and AlphaMissense (PMID 37733863) | Same title table. The HLA abstract odds ratios are in K36. AlphaMissense scores in the notes were not re-extracted |
| K36 | KNOWN | On 2026-11-11 the PMC page for the 2025 kinectin paper and four abstracts were read. Matched residue spans, the 11-protein complex count, exon 5 anchoring, HLA odds ratios 5.4 and 0, and 22/22 CDR2L alterations in the breast-cancer abstract are stated on the extract. The notes' span 23-145, range 5.4-8.87, splicing fractions and prevalence range were not adopted | [Checked sentences](docs/google-bio-convergence-2026-11-11.md#sentences-checked-in-the-named-papers). Passages read that day. Not a re-extraction of binding constants or occupancy |
| K37 | KNOWN | PMC12851941 is Avsec and colleagues, Nature, 2026, PMID 41606153, DOI 10.1038/s41586-025-10014-0. NCBI Gene 30850 (GRCh38.p14, 1-based) places human CDR2L at 74,987,632-75,005,800 on NC_000017.11, band 17q25.1. The notes' base interval differs | [AlphaGenome and CDR2L span](docs/google-bio-convergence-2026-11-11.md#alphagenome-record-and-the-cdr2l-span). PubMed, the PMC page and the gene record. The paper's 1 Mb input does not include the notes' windows |
| C23 | CONJECTURE | HLA pocket chemistry, EEF1D splicing, chromosome 17 co-location and a multi-analyte blood index may deserve a later bounded protocol | [Unrun proposals](docs/google-bio-convergence-2026-11-11.md#proposals-that-were-not-re-run). The named simulator files were not in the commit. No regimen is proposed |

## CDR2L original-source adjudication, 2026-11-06

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V35 | VERIFIED | A subsequent completed UniProt service search returns only Q86X02 and A0ACI8RKQ2 for both selected peptides in human exact and I/L-equivalent queries, including unreviewed entries; returned sequences were locally rechecked | [Executed follow-up](docs/cdr2l-source-adjudication-2026-11-06.md), [new certificate](registries/cdr2l-database-search-2026-11-06.json). Service completeness/synchronization not proved; the historical V30 search limitation is preserved. |
| V36 | VERIFIED | The official Atlas peptide page for IEDB 11610866 displays one cerebellum source-association row, q-value 0.00189334 and no prediction-based binding evidence | [Aggregate certificate](registries/cdr2l-atlas-source-2026-11-06.json), `python3 tools/audit_cdr2l_atlas.py`, [source interpretation](docs/cdr2l-source-adjudication-2026-11-06.md). Portal metadata, not independently validated identification, source cell type, allotype or mechanism. |
| V37 | VERIFIED | Complete integrity-checked streaming inspection of three original PXD023044 class-II identification files finds the exact breast-cell-line CDR2L 15mer once in r3, non-decoy Q86X02 residues 432–446, native spectrum `index=22949` | `python3 tools/audit_cdr2l_source_psm.py --check`; [Original identification result](docs/cdr2l-source-identification-2026-11-06.md), [certificate](registries/cdr2l-source-identification-2026-11-06.json). Search-output provenance, not independent spectrum validation, peptide-specific FDR, HLA allotype or receptor recognition. |
| V38 | VERIFIED | The completely checksum-verified source MGF links documented zero-based `index=22949` to scan 23848, charge 3+, precursor m/z 614.999, exactly agreeing with the original submitted identification; 173 experimental peaks retained | `python3 tools/audit_cdr2l_spectrum_locator.py --check`; [Executed peak-list locator](docs/cdr2l-spectrum-locator-2026-11-06.md), [certificate](registries/cdr2l-spectrum-locator-2026-11-06.json). Source linkage and metadata agreement, not independent identification, FDR calibration, RAW acquisition verification or biological replication. |

## CDR2/CDR2L public evidence atlas, 2026-11-13

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V39 | VERIFIED | Repeating the 2026-11-05 IEDB parent procedure returns 7 CDR2 (Q01850) and 2 CDR2L (Q86X02) positive class-II mass-spectrometry assay rows, 3 and 2 references, the same assay ids as that audit. Parent elution-id lists are 383 and 45. The 7 ids added to CDR2 are class I, PMID 42653321. CDR2L antigen, parent-card and class-II bytes match the 2026-11-05 hashes; the CDR2 antigen body does not. Two independent readers agree | `python3 results/cdr2-cdr2l-evidence-atlas-2026-11-13/verify.py`. Pinned responses only. Assay rows are not patients, peptides, or anti-Yo receptor evidence. |
| V40 | VERIFIED | Pinned UniProt bytes give reviewed human CDR2 Q01850 (454 amino acids, GeneID 1039, HGNC:1799, ENSG00000140743.9) and CDR2L Q86X02 (465 amino acids, GeneID 30850, HGNC:29999, ENSG00000109089.8). Pinned Human Protein Atlas version 26.0 extracts give the nTPM and ovarian IHC patient counts in the atlas count block, including cerebellum 16.1 and 58.8 nTPM and 12 patients in each ovarian IHC row | Same command. Consensus nTPM is the Atlas maximum of HPA and GTEx and has no donor count in the file. IHC bins are patient counts, not an effect size. TCGA 349 is the Human Protein Atlas version 26.0 RNA cohort size for ovary serous cystadenocarcinoma, not the GDC TCGA-OV case count and not the 2011 analysed-sample count, and not a gene-level result. |
| K38 | KNOWN | The cited abstracts report the case-series and serum counts in the atlas literature table: Peterson 52/55 malignancies, Eichler 36/42 dual-positive Yo sera, 5/179 and 4/114 without PNS, 0/100 donors, and Raspotnig 16/16 ovarian cancers expressing both proteins | [Atlas literature table](docs/cdr2-cdr2l-evidence-atlas-2026-11-13.md#primary-literature-counts), S149–S156. Abstracts only. Authors' causal and management sentences are not adopted. No new odds ratio was calculated. |
| K39 | KNOWN | Human Protein Atlas version 26.0 defines consensus nTPM as the maximum of HPA and GTEx across 51 tissues, and cancer IHC columns as patient counts in staining bins | S141–S143. A definition and a file layout, not a measured anti-Yo effect. |
| K40 | KNOWN | PMID 42653321 (PMC13513872) is a psoriatic-arthritis MHC class I immunopeptidome paper. The seven CDR2 parent ids added since 2026-11-05 are class I rows from that paper | S140 and S157. Catalog context for the parent-list change. Not an anti-Yo class-II finding. |
| C24 | CONJECTURE | The class-II ligands and the expression patterns may still be worth comparing with anti-Yo receptor specificity, but this atlas does not decide that comparison | Open question carried forward from the evidence map. Expression in antibody-negative tumours is a reason not to treat presence as specific. |

## Integrity layer, 2026-11-13

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V41 | VERIFIED | Offline integrity layer: exported claims ledger matches CLAIMS.md; SHA-256 manifests under results/ and digest-bound registry certificates match; checker audit lists 42 VERIFIED rows, 26 offline checkers, 25 first offline commands replayed with exit 0 (V02 skipped as heavy), 4 digest-bound tamper checks yes, 0 tamper misses; 16 rows have no offline checker (V03, V04, V05, V20, V21, V24, V27, V35 doc-only; V08, V10, V11, V12, V13, V14, V15, V16 network-only) | `python3 tools/export_claims_ledger.py --check`; `python3 tools/check_sha256_manifests.py`; `python3 tools/audit_checkers.py --check`; `python3 results/integrity-audit-2026-11-13/verify.py`; [record](docs/integrity-layer-2026-11-13.md), [audit](results/integrity-audit-2026-11-13/audit.json). Software bookkeeping, not scientific replication or clinical performance. Network audits and doc-only re-checks remain outside this layer. |

## Ovarian interventional trial landscape, 2026-11-13 UTC

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V42 | VERIFIED | The frozen ClinicalTrials.gov API v2 pull started 2026-11-13T04:57:57Z (2026-11-12 22:57 America/Chicago; dataTimestamp 2026-11-12T10:00:05) returned 4260 unique interventional studies for condition query Ovarian Cancer. Status and phase counts each sum to 4260. The same recruiting query as 2026-11-05 returned 591, against 592 in that certificate. The earlier certificate has no NCT identifiers, so new, removed, and status-changed NCT IDs are not reconstructable. Corpus status RECRUITING is also 591. Two independent readers agree. Target-class hits: folr1 language 53, FRα ADC name or phrase 39, PARP-inhibitor lexicon 324, CDR2/CDR2L 0, mesothelin 39, MUC16 8, immunotherapy lexicon 510; 842 studies hit at least one target class. CA-125 language is 65 and is not an MUC16-directed class. These are registration counts, not efficacy or treatment guidance | [Report and exact requests](docs/trial-landscape-v2-2026-11-13.md); [certificate](results/trial-landscape-v2-2026-11-13/certificate.json); `python3 results/trial-landscape-v2-2026-11-13/verify.py`. S126, S127, S128, S158, S159. Pinned pages only. Not clinical advice, not eligibility, and not a measure of benefit. |

## TCGA-OV cohort reconciliation, 2026-11-13 UTC

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| V43 | VERIFIED | On 2026-11-13T06:03:12Z to 2026-11-13T06:03:41Z, GDC Data Release 46.0 (tag 8.5.0, API version 1) returns 608 TCGA-OV cases, 32891 project files, 14519 open files and 18372 controlled-access file records. Open simple-nucleotide-variation files cover 419 cases and open copy-number files cover 601 cases; their case intersection is 417. cBioPortal ov_tcga_pub has 489 samples, 316 sequenced samples, and 492 patients, all 492 inside the GDC case set, with 116 GDC cases outside. ov_tcga has 617 samples and 600 patients (overlap 600). ov_tcga_pan_can_atlas_2018 has 585 samples and 585 patients (overlap 585). Two independent readers agree. These are catalog counts, not a biological conclusion and not clinical guidance | `python3 results/tcga-ov-cohort-reconciliation-20261113/verify.py`. [Report](docs/tcga-ov-cohort-reconciliation-20261113.md); [certificate](results/tcga-ov-cohort-reconciliation-20261113/certificate.json). S160, S161, S162, S163, S164, S165, S166, S167, S168, S169, S170, S171, S172, S173. Identifier sets were hashed and not stored. Controlled-access file contents were not downloaded. The ov_tcga_pub description sentence that says whole exome sequencing of 489 conflicts with sequencedSampleCount 316 and with PMID 21720365. |
| K41 | KNOWN | PMID 21720365 (DOI 10.1038/nature10166) says the TCGA project analyzed mRNA expression, miRNA expression, promoter methylation, and DNA copy number in 489 high-grade serous ovarian adenocarcinomas and the DNA sequences of exons from coding genes in 316 of these tumors | S160. PMC3163504 summary first sentence, read 2026-11-13. A published cohort definition, not a current GDC case count and not clinical guidance. |
| K42 | KNOWN | GDC documents that some data is open access, needing no authentication or authorization, and other data is controlled access, needing dbGaP authorization and eRA Commons authentication. The API facets parameter provides aggregate information for a specified field. Authentication is required for downloading controlled-access data and for data submission | S161, S162, S163. Access class and facet documentation. Not a finding about any tumour and not a licence grant. |
| K43 | KNOWN | cBioPortal provides a public REST API, described with Swagger/OpenAPI, for programmatic access to the same data as the website | S169. API documentation. A study description on the portal is portal text, not a re-derivation of PMID 21720365. |
| C25 | CONJECTURE | Why 116 GDC TCGA-OV cases are absent from the ov_tcga_pub patient set, and why 3 ov_tcga_pub patients have no sample, is not established by these catalog counts | Open. The overlap counts are V43. The cause is not identified. Not a claim that those cases lack a tumour or a sequencing file. |

## Discovery AUROC provenance, 2026-11-13

| ID | Label | Statement | Evidence and boundary |
| --- | --- | --- | --- |
| K44 | KNOWN | Chowdhury et al., Cell 2023, print one discovery AUC of 0.83 (95% CI 0.77–0.90) for the 64-protein ensemble on FFPE discovery proteomic data, five-fold cross-validation. The sentence is paragraph P33. Figure 3 panel D3 prints AUC = 0.83 and n=135. The figure caption does not restate 0.83. Paragraphs P177 and P183 print 83 sensitive and 52 refractory tumours. Paragraph P183 says the AUC intervals were calculated by bootstrap. The article XML does not contain 0.80885. The same figure’s 0.81 is the frozen-overlap panel, n=27. The 2024 correction does not mention this AUC. These are discrimination numbers | S174, S175, S11. [Provenance note](docs/auroc-provenance-20261113.md). JATS pages 3476–3498.e35; the Figure 3 JPEG comment says 3476-3498.e36. Paragraph P33 has no page of its own in the author-manuscript XML. Not clinical utility. |
| K45 | KNOWN | At commit 48357fd, Figure_3D_part3.R line 184 draws the literal string AUC = 0.83. The string does not read or round roc.all1. None of the 42 R or Rmd files in that commit contains n=135. The n=135 on the published figure is an image label | S176. [Provenance note](docs/auroc-provenance-20261113.md). The unrounded roc.all1 value is not in the script. Not clinical utility. |
| V44 | VERIFIED | On public MMC1 and MMC4, FFPE_pred_scores joined to FFPE_Discovery_clinical has 135 rows, 52 refractory and 83 sensitive. Pair and rank readers agree: the Mann–Whitney AUROC with half credit for ties is 3491/4316 = 0.8088507877664504. Half-up rounding is 0.81 to two decimals and 0.809 to three decimals. The absolute difference from the printed 0.83 is 1141/53950, which exceeds 0.02. The DeLong 95% interval is 0.7347956138 to 0.8829059617. A stratified bootstrap of 2000 resamples with seed 20261113 has 95% percentile interval 0.7309951344 to 0.8760484245. Both intervals contain 0.83. This is discrimination of released scores | `python3 results/auroc-provenance-20261113/verify.py`. [Note](docs/auroc-provenance-20261113.md); [certificate](results/auroc-provenance-20261113/certificate.json). S14, S174. Workbook SHA-256 values are in the certificate. Scores were not stored. Offline replay uses the frozen aggregates and does not re-read the workbooks. Not a refit, not clinical utility, and not evidence that the sheet is the Figure 3D prediction vector. |
| C26 | CONJECTURE | The unrounded five-fold CV AUC that the authors displayed as 0.83 is absent from the public article, the public score sheet, and the pinned scripts. Whether 0.83 displays some other unrounded ROC, and whether the released sheet is that ROC’s input, remains open | C20 already records the sheet-versus-figure gap. This row adds that the plot label is a literal and that the unrounded roc.all1 value was not found. It does not assert that the paper misquoted 0.80885. |

## What this ledger does not claim

- Clinical validity, diagnostic accuracy, treatment benefit, or individual patient guidance.
- Peer review, regulatory clearance, or institutional ethics approval.
- Complete patient independence across cohorts (overlap remains partially unresolved).
- That software fixture success implies study-data model performance.
- That the AUROC discrepancy proves an error in Chowdhury et al.
- A project-wide license grant for third-party study files (see [NOTICE](NOTICE)).

Update this file when README, mission, or protocol statements change.
