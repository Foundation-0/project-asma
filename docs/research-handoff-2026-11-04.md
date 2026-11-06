# Research exploration handoff: 2026-11-04

**Status: proposed research directions; public-source review completed.** This
selective review preserves candidate work under the expanded [mission](mission.md).
It supplements the [ranked directions](directions.md) and the earlier
[frontier snapshot](frontier-2026-10-22.md); it does not adopt a new protocol or
change [Pilot 001](../protocols/pilot-001.md). No study-data acquisition, analysis,
model fitting, clinical evaluation, or third-party outreach was performed for
this review. Source access dates below are **2026-11-04**.

Claims labelled **KNOWN** describe cited external evidence, not findings reproduced
by this project. **CONJECTURE** labels proposed questions, expected usefulness,
and prioritization judgments. Nothing in this document is a proof, a new
biomarker discovery, a treatment recommendation, or a claim of clinical benefit
from Project Asma. The searches were selective; failure to find an existing
analysis cannot establish novelty.

## Recommendation and decision rationale

**CONJECTURE — broader-team handoff:** prioritize a bounded study of treatment
response over time among these avenues, with
explicit separation between a circulating marker, a tumor target, and a causal
resistance mechanism. Longitudinal resistance has a strong fit with the mission,
but its data and execution requirements are less immediately tractable than
evidence curation and synthetic software benchmarks. Preserve both routes rather
than committing to a new clinical predictor. The current focused frontier
exploration is recorded separately in the [continuation record](research-continuation.md).

| Candidate | Small-team feasibility now | Scientific opportunity | First reviewable deliverable |
| --- | --- | --- | --- |
| Longitudinal CA-125 and clonal resistance | High for source/endpoint audit; conditional for study analysis | Test whether discordant measurements provide information beyond tumor burden | Evidence map, permitted-input inventory, and synthetic time-series benchmark |
| Spatial immune exclusion and perturbation | Medium for metadata/code review; conditional for analysis | Separate cell-state associations from experimentally supported mechanisms | One proposed replication target with patient/site/platform split rules |
| Functional organoids | High for evidence synthesis; low for new experiments without partners | Evaluate when dynamic drug response adds information to static molecular assays | Cross-study validation and failure-reporting table |
| Evidence and trial navigation | High for public-registry and synthetic-case work | Reduce unsupported eligibility claims and missed relevant evidence | Ovarian-specific benchmark with explicit unknown states |
| Symptoms, function and communication | High for evidence review; conditional for clinical evaluation | Study outcomes meaningful independently of tumor response | Workflow evaluation protocol with clinician response and accessibility measures |

These rankings are judgments, not measured feasibility results. They do not
replace the existing [direction shortlist](directions.md), whose TCGA, CPTAC,
DepMap/PRISM and GEO candidates may offer simpler first analyses. Compare those
options at the next protocol decision. Preserve the pilot's existing
[score discrepancy](pilot-001-score-verification-result.md),
[independence limits](pilot-001-input-resolution.md), and
[validation capacity](pilot-001-validation-capacity.md) rather than repeating
their numerical results here.

## 1. Longitudinal biomarkers and acquired resistance

**KNOWN — human longitudinal evidence:** Williams et al. followed clonal
evolution in 18 patients with HGSOC using CloneSeq-SV. Resistance commonly
involved expansion of a subset of clones present at diagnosis. The observations
motivate adaptive-treatment research; they do not establish that such treatment
improves survival. [H01](https://doi.org/10.1038/s41586-025-09580-0)

**KNOWN — secondary biomarker analysis:** the GOG-0218 KELIM validation assessed
1,662 participants with at least three CA-125 measurements during the first
100 chemotherapy days. It evaluated associations with benefit from first-line
bevacizumab. This setting must not be silently transferred to later recurrence,
different treatment regimens, or an individual treatment decision.
[H02](https://pubmed.ncbi.nlm.nih.gov/36252167/)

**KNOWN — randomized intervention evidence:** MRC OV05/EORTC 55955 found no
overall-survival benefit from starting relapse chemotherapy on a CA-125 rise
alone rather than waiting for clinical recurrence: HR 0.98, 95% CI 0.80–1.20.
This tests a particular historical intervention strategy, not every future
monitoring or treatment strategy. Earlier detection and a useful intervention
are separate hypotheses. [H03](https://pubmed.ncbi.nlm.nih.gov/20888993/)

**CONJECTURE — proposed contribution:** assess whether disagreement between
CA-125 trajectories, total circulating tumor DNA and resistant-clone abundance
adds information beyond total disease burden. Begin with definitions and
synthetic examples. A later protocol must freeze the population, treatment line,
sampling window, endpoint and comparator before outcomes are examined. A simple
kinetics or burden model is the baseline; complexity must earn its place.

The authors' [figure repository](https://github.com/shahcompbio/spectrum_cfdna_figures)
points to processed data in Synapse `syn66399325` and describes R analyses.
The README was read; study files and analysis scripts were not acquired or run.
Synapse access and reuse conditions remain unresolved for this project. A request
for the repository's root `LICENSE` returned 404; that does not prove no license
exists elsewhere. Do not copy or execute the code on that basis.

**Next tasks:** inventory sampling times and permitted open-tier fields from
metadata; specify missingness/assay-change handling; compare marker-only and
combined hypotheses; create synthetic leakage and censoring examples. Group
repeated samples by patient, and prevent post-outcome measurements from entering
prediction. Evaluate calibration, uncertainty and lead-time effects, not only
discrimination.

**Stop rules:** stop a proposed performance analysis if outcome definitions,
treatment timing, assay identity, patient separation or use conditions cannot be
resolved. Do not infer a tumor target from an elevated circulating marker. Do
not claim treatment benefit from a predictive association.

**Addendum, 2026-11-05:** a circulating marker is a weighted sum over lesions.
The [exposure record](research/paraneoplastic-exposure-observability.md#4-a-circulating-marker-cannot-certify-the-antigen-that-matters)
proves it cannot certify another lesion-weighted quantity, such as the antigen
driving an immune response, unless the weightings are proportional.

## 2. Spatial immune exclusion and functional perturbation

**KNOWN — human profiling plus preclinical experiments:** Yeh et al. profiled
approximately 2.5 million cells across 130 tumors from 94 patients. Spatial
cell-state associations were combined with perturbational experiments; PTPN1
and ACTR8 knockouts and PTPN1/PTPN2 inhibition sensitized ovarian cancer cells
to immune-cell killing. These are mechanistic leads, not demonstrated survival
benefits in ovarian cancer patients.
[H04](https://doi.org/10.1038/s41590-024-01943-5)

**CONJECTURE — proposed contribution:** reproduce one spatial immune-exclusion
association and test whether it survives patient, anatomical-site, treatment and
platform variation. A subsequent question could examine whether target expression
and an immune-excluding environment jointly explain response variation, but
that question needs its own prior-art and feasibility review. RNA expression
must not be reported as direct protein measurement.

The [Zenodo version-3 record](https://zenodo.org/records/12613839) lists processed
spatial/perturbation data and clinical annotations, totaling 11.7 GB. Only the
landing-page metadata were read. The
[code license](https://github.com/Jerby-Lab/HGSC_SpatialPerturbational/blob/main/LICENSE)
is BSD-3-Clause. Code, data, article text and third-party material have separate
rights; the article's noncommercial/no-derivatives license is not a substitute
for a dataset-specific use assessment.

**Next tasks:** choose one figure/association, inspect code dependencies without
execution, locate a small permitted input route, and specify patient-level
replication and batch sensitivity checks. **Stop rules:** stop if the intended
claim depends on inaccessible outcome labels, unresolvable repeated-patient
overlap, or treating thousands of cells as independent patients. Do not promote
an expression association to a causal or clinical target claim.

## 3. Functional organoids and treatment-induced cell states

**KNOWN — small prospective correlation study:** Wang et al. established
organoids from 21 of 30 patients. Their chemotherapy-response evaluation used
12 evaluable cases, with exclusions and wide uncertainty. These findings support
further validation; they do not demonstrate that choosing treatment with the
assay improves outcomes. [H05](https://doi.org/10.1186/s12967-025-07112-y)

**KNOWN — small preclinical study:** Newtson et al. reported altered secondary
drug sensitivity after chemotherapy exposure in organoid models from four
patients, without detected genomic changes in their analysis. This motivates
research into dynamic cell states; it neither excludes undetected genetic
effects nor establishes a general clinical resistance mechanism. The publisher
page identifies this as an accepted early article subject to further edits.
[H06](https://doi.org/10.1186/s13048-026-02268-7)

**CONJECTURE — proposed contribution:** create a cross-study benchmark schema
that records culture failures as well as successful assays, histotype,
pretreatment, specimen type, turnaround, tested exposure, blinding, comparator
and concordance with outcomes. Separate predicting the treatment actually
received from showing benefit after assay-directed selection.

**Next tasks:** extract study-level aggregate validation information into an
evidence table; inspect whether public releases support any independent
benchmark; specify a blinded evaluation before proposing data analysis.
Clinical data in H05 are not generally public according to its availability
statement. Do not plan a public-data replication that assumes access to them.

**Stop rules:** stop an analysis if culture failures or exclusions cannot be
accounted for, outcome labels are inaccessible, or models pool incompatible
histotypes. New organoid work needs a separate approved collaboration and
resources; no such collaboration is arranged here. Culture selection and loss
of immune/stromal context limit translation.

## 4. Evidence and trial navigation

**KNOWN — workflow benchmark evidence:** TrialGPT reported 87.3% criterion-level
matching accuracy and a 42.6% reduction in screening time in a pilot user study.
These results establish neither improved enrollment nor survival.
[H07](https://doi.org/10.1038/s41467-024-53081-z)
The [NCBI FAQ](https://www.ncbi.nlm.nih.gov/research/trialgpt/faq/) describes an
experimental research system whose outputs require human verification; only
the study team can determine eligibility. The
[repository license](https://github.com/ncbi-nlp/TrialGPT/blob/main/LICENSE)
contains an NCBI public-domain notice. Dependencies and any reused benchmark
data still require their own checks.

**CONJECTURE — proposed contribution:** extend the existing
[trial-landscape direction](directions.md) with a small synthetic ovarian-case
benchmark. Require criterion-level citations, explicit unknown states, histotype
and treatment-line distinctions, geographic constraints and date-stamped
recruitment status. Measure false exclusions and unsupported eligibility claims,
alongside retrieval recall, citation fidelity and reviewer time. Compare against
simple registry filters and structured manual rules.

**Next tasks:** define original synthetic cases and expected evidence states;
pin public trial-record versions; record evaluation failures and uncertainty.
**Stop rules:** stop claims of clinical utility without a separate clinician-led
evaluation. Never resolve missing facts by inventing them, treat stale registry
status as current, or submit identifiable health information to a public demo.

## 5. Symptoms, function and communication

**KNOWN — randomized clinical evidence:** the PRO-TECT trial enrolled 1,191
patients with metastatic cancers. Electronic symptom monitoring improved
function, symptom and quality-of-life outcomes and reduced emergency visits;
overall survival did not differ. The intervention included clinical response
workflows. A standalone application cannot inherit those effects, and the mixed
cancer population does not establish ovarian-specific benefit.
[H08](https://doi.org/10.1038/s41591-025-03507-y)

**CONJECTURE — proposed contribution:** define an evaluation focused on whether
symptom information reaches a responsible clinical team and receives a timely,
appropriate response. Include accessibility, telephone/non-web options,
caregiver burden and alert burden. Do not make survival the implied benefit of
a communication tool without evidence.

**Next tasks:** build a study-level evidence map and a proposed workflow protocol;
check questionnaire rights and data-access requirements; choose patient-reported
outcomes and response-time measures before any pilot deployment. **Stop rules:**
do not initiate patient collection or deployment without clinical ownership,
appropriate review and a safe response pathway. Do not substitute automated
advice for that pathway.

**Addendum, 2026-11-05:** for paraneoplastic neurological symptoms, a functional
score is a state and cannot show whether injury is ongoing. The
[exposure record](research/paraneoplastic-exposure-observability.md#3-state-versus-rate)
explains why a rate measurement is also needed, and why serum neurofilament light
needs a comparator when patients have surgery or neurotoxic chemotherapy.

## Source and review record

| ID | Exact primary citation | Review scope and remaining limits |
| --- | --- | --- |
| H01 | Williams et al., *Nature* 647, 757–765 (2025), [10.1038/s41586-025-09580-0](https://doi.org/10.1038/s41586-025-09580-0), online 2025-10-01 | Abstract, indexed primary-paper passages and author README reviewed; direct publisher/PMC retrieval intermittently failed. Source datasets, supplements and code execution unreviewed. Existing registry S02 covers the paper. |
| H02 | You et al., *Journal of Clinical Oncology* 40, 3965–3974 (2022), [10.1200/JCO.22.01207](https://doi.org/10.1200/JCO.22.01207) | PubMed abstract and indexed primary-paper methods/discussion reviewed; no patient data or calculator submissions. |
| H03 | Rustin et al., *Lancet* 376, 1155–1163 (2010), [10.1016/S0140-6736(10)61268-8](https://doi.org/10.1016/S0140-6736(10)61268-8) | Primary abstract/results reviewed through PubMed and publisher indexing; historical treatment context retained. |
| H04 | Yeh et al., *Nature Immunology* 25, 1943–1958 (2024), [10.1038/s41590-024-01943-5](https://doi.org/10.1038/s41590-024-01943-5) | Publisher text, Zenodo metadata and code license reviewed; no data files downloaded. Existing registry S03 covers the paper. |
| H05 | Wang et al., *Journal of Translational Medicine* 24, 55 (2026), [10.1186/s12967-025-07112-y](https://doi.org/10.1186/s12967-025-07112-y), published 2026-01-06 | Publisher methods/results and availability statement reviewed; supplements and individual data not acquired. |
| H06 | Newtson et al., *Journal of Ovarian Research* (2026), [10.1186/s13048-026-02268-7](https://doi.org/10.1186/s13048-026-02268-7), published 2026-09-18 | Publisher accepted-article page and abstract reviewed; full experimental/supplemental audit not completed. Recheck version before protocol adoption. |
| H07 | Jin et al., *Nature Communications* 15, 9074 (2024), [10.1038/s41467-024-53081-z](https://doi.org/10.1038/s41467-024-53081-z) | Primary abstract/indexed methods, NCBI FAQ and repository license reviewed; code/data not executed or benchmarked here. |
| H08 | Basch et al., *Nature Medicine* 31, 1225–1232 (2025), [10.1038/s41591-025-03507-y](https://doi.org/10.1038/s41591-025-03507-y), published 2025-02-07 | Primary abstract/indexed results reviewed; no participant data acquired; ovarian-specific effects not established here. |

Searches covered ovarian longitudinal resistance and spatial biology,
organoid clinical concordance, KELIM validation, CA-125-triggered intervention,
trial matching and symptom monitoring. Exact-DOI searches with `correction
retraction` for H01–H08 did not locate a notice in the returned
results. This is a bounded search, not evidence that no correction exists.
Complete the publisher/PubMed correction and version check for every selected
source before freezing a protocol. Current web indexing and article publication dates were distinguished;
no source after 2026-11-04 was used.

The already-recorded molecular frontier and public-data directions remain
context, not individual target assignments. This review does not update their
regulatory status. FDA notices in the [earlier frontier](frontier-2026-10-22.md)
describe **United States** indications on their stated dates; they must not be
read as approvals in Canada or another jurisdiction, or as current authority for
a different indication. None of the proposed tools or analyses here is presented
as a regulated or clinically validated product.

## Continuation contract

Before executing a selected direction, prepare a
[research question](../templates/research-question.md) and protocol PR with its
population, endpoint, baseline, permitted inputs, uncertainty, compute bound and
stop rules. Complete the applicable [Gate 0](roadmap.md) decisions, rights and
execution-context assessment. Publicly accessible metadata do not authorize
study-file acquisition or model fitting. Controlled-access cohorts are not
planned under this handoff; they require a separate access process and owner
decision.

Retain aggregate results and reproducible failure records only, under the
[data rules](reproducibility-and-data.md). Update the source registry and
[claims ledger](../CLAIMS.md) with promoted evidence claims, exact source
versions and the finite checks actually performed. Software tests establish
software behavior only; literature review establishes neither replication nor
clinical benefit. A justified stop or narrower question is an acceptable result.
