# Barry Rosen: gynecologic oncology research survey

**Initial assessment: 2026-11-04 (UTC). Draft for research review.**
**Follow-up:** [2026-11-05 identity and recall audit](#2026-11-05-identity-reassessment-and-targeted-recall-audit).
The initial dated assessment below is preserved; see the follow-up for current counts.

**Project use: candidate** literature curation and research-question design;
no adoption, study-data analysis, clinical validation or treatment recommendation.
[Living issue #40](https://github.com/Foundation-0/project-asma/issues/40).

This survey maps a research body across hereditary risk and prevention, molecular
biology, treatment and surgical outcomes, survivorship, information needs, and
care delivery. Its strongest immediate contribution to Project Asma is a more
precise evidence map: endpoints, histotypes, time horizons, shared cohorts and
access restrictions. The most tractable additional data lead verified here is
**GSE51831**, an ascites-associated HGSOC expression study. It is not a new
primary-refractory validation cohort.

The [bibliography](barry-rosen-bibliography.md) supplies primary links and DOIs.
The [screening snapshot](../../registries/barry-rosen-bibliography.json) is the
canonical item-level metadata, identity rationale, disposition, search and notice
record. This document is the canonical synthesis. Other project links are
navigation only. Bibliographic metadata and short original assessments are
retained; no full texts, source supplements, datasets or patient rows are included.

## Identity and attribution

**KNOWN — institutional history.** The UHN [2015 annual report, printed pages
25–27](https://www.uhn.ca/PrincessMargaret/Documents/Princess_Margaret_annual_report_2015.pdf)
identifies the former Toronto/UHN gynecologic oncology head and records his June
2015 move to Beaumont and Oakland University. It describes hereditary ovarian
cancer research, clinical databases and synoptic reporting. Its historical
publication count is not a current corpus count. Toronto's [AMPATH program
page, Leadership team](https://obgyn.utoronto.ca/ampath-u-t-program) independently
connects Barry Rosen to Beaumont and the Moi collaboration. These establish the
institutional bridge used in screening, not the authorship of every search hit.

**KNOWN — article-level bridges.** [PMID 28861459](https://pubmed.ncbi.nlm.nih.gov/28861459/)
links Rosen, Itsura, Tonui, Covens and Orang'o with an Oakland/Beaumont affiliation.
[PMID 35710751](https://pubmed.ncbi.nlm.nih.gov/35710751/) links Rosen at Beaumont
to Kotsopoulos, McLaughlin, Risch and Narod. [PMID 38473333](https://pubmed.ncbi.nlm.nih.gov/38473333/)
uses **Rosen BP** with Toronto/UHN gynecologic oncology affiliations and that
same survival-research network. Middle initial **P is not an exclusion rule**.

The [FIU institutional profile](https://case.fiu.edu/about/directory/affiliated-profiles/rosen-barry.html)
describes a different Barry P. Rosen in heavy-metal transport/arsenic
biochemistry, with Wayne State history. FIU/Wayne State biochemistry, arsenic
subjects and that coauthor network distinguish those papers; a cancer-related
title alone does not establish the clinician's identity. For example,
[PMID 24070612](https://pubmed.ncbi.nlm.nih.gov/24070612/) concerns INPP4B but its
Rosen author metadata carries the biochemist's ORCID and Packianathan network;
it is excluded, rather than imported as ovarian-oncology evidence. There are
also other Barry, Benjamin, Brittany and Bruce Rosens. The Advocate breast
surgeon's publications are excluded by affiliation/network, not by specialty
keywords alone. Aggregated profile bibliographies and counts were not used.

**Uncertainty:** older records often lack author-specific affiliations. Inclusion
there uses multiple established coauthors, or a gynecologic topic plus a linked
coauthor, with selected manual continuity checks. This is provisional attribution,
not ORCID-level verification for every item. The 2026 cervical paper prints
Rosen's affiliation as “University of Michigan, Michigan, AL”; the source's
inconsistent geography is not silently corrected. Its Itsura/Tonui/Covens network
supports inclusion, while that affiliation requires clarification from public
sources. No authors have been contacted.

## Search method and coverage

Executed 2026-11-04 against Europe PMC's public literature API, using `resultType=core`,
`format=json`, `pageSize=1000`, `cursorMark=*` and every returned next cursor until
the hit count was exhausted. These are literature/author metadata and accessible
article reads, not study-data acquisition.

| Query | Returned / retrieved | Pages |
| --- | --- | --- |
| `AUTHOR:"Rosen B" AND SRC:MED` | 2,022 / 2,022 | 3 |
| `AUTHOR:"Rosen BP"` | 383 / 383 | 1 |
| `AUTHOR:"Rosen Barry"` | 412 / 412 | 1 |
| `(AUTHOR:"Rosen B" OR AUTHOR:"Rosen BP") AND (ovarian OR cervical OR endometrial OR gynecologic OR gynaecologic OR BRCA OR vulvar OR vulval OR Kenya)` | 314 / 314 | 1 |
| Same author pair AND `(Toronto OR Beaumont OR Oakland OR Covens OR Narod OR Murphy OR Itsura OR Tonui OR Orang'o OR Bernardini OR Laframboise OR Kotsopoulos OR Colgan OR Diamandis)` | 306 / 306 | 1 |
| `EXT_ID:(16835424 OR 16137750 OR 24567435 OR 21324516 OR 19135709 OR 23257159 OR 26556769 OR 28208158 OR 35710751 OR 38473333 OR 28861459) AND SRC:MED` | 11 / 11 | 1 |

Replay with Python standard library, substituting any exact query above:

```python
import json, urllib.parse, urllib.request
query = 'AUTHOR:"Rosen BP"'
cursor = '*'
while True:
    params = dict(query=query, format='json', resultType='core',
                  pageSize=1000, cursorMark=cursor)
    url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=120) as response:
        result = json.load(response)
    print(result['hitCount'], len(result['resultList']['result']))
    following = result.get('nextCursorMark')
    if not following or following == cursor:
        break
    cursor = following
```

Offline count replay (checks the saved dispositions, not their scientific correctness):

```sh
python3 -c 'import json,collections; d=json.load(open("registries/barry-rosen-bibliography.json")); print(dict(collections.Counter(r["screening"] for r in d["records"])))'
```

Results were deduplicated by source plus identifier: **2,046** records. Screening
provisionally attributes **215** entries: **212 MED records, two abstract
collections and one linked preprint**. Of the remaining records, **1,622** were
excluded and **209** remain uncertain. These numbers describe a dated search
and screening process, not Rosen's publication count. Included material spans
**1989–2026**. Eight included articles were inspected in relevant sections through accessible full-text XML,
23 through abstracts, and 184 at metadata level. Depth is explicit per entry;
metadata screening does not mean the article's methods or conclusions were assessed.
The additional 2025 HIPEC lead is outside those 215 entries and remains metadata only.

Selection order: identify exact Rosen B/BP entries in structured author metadata;
exclude explicit conflicting given names and incompatible institutional/network
identities; seek author-specific gynecologic/Beaumont/Oakland/Princess Margaret
affiliation; otherwise require topic/coauthor continuity. Keep unresolved identity
separate. Retain corrections, reviews, preprints and abstract collections with their
type; a retracted article remains bibliographic history and cannot support a finding.
The JSON stores the basis for each disposition, primary URLs, DOI or null, date,
publication types, linked notices and canonicalized response hashes for each query.
The broad initial search also finds prefix matches such as Rosen BR/BD, which are
not attributed to the target. Queries using unsupported `AUTH_FULL` or
`AUTH_LAST_NAME` fields yielded empty results during initial diagnostics and were
abandoned; they are not evidence of an empty corpus.

Additional primary routes: publisher-deposited Crossref metadata for the HIPEC DOI;
UHN/Toronto/FIU institutional pages; publisher abstract/data-availability pages;
Europe PMC full-text XML for open articles; and the **GEO series metadata only**
for GSE51831. Web discovery queries included `Barry Rosen gynecologic oncology
Toronto research`, the exact HIPEC DOI, and exact molecular-paper titles plus
`GSE`/`GEO`. Search snippets did not establish findings or data provenance.

**Coverage limits:** this is an extensive scoping bibliography, not an exhaustive
systematic review or a complete verified lifetime CV. No paid Scopus/Web of Science
search, complete conference-abstract archive, books/chapter search, author-confirmed
CV, full citation-network snowball, or independent human screening was performed.
Recent/indexing changes, alternate spellings, consortium-only authorship and
nonindexed regional journals can be missed. Some by-name hits lack enough evidence
to include. The bibliography includes broader hereditary breast research only
where continuity supports the target identity. Full-text access failures are
explicit; no paywall was bypassed. PubMed/PMC HTML frequently returned browser
checks; several Europe PMC fullTextXML routes returned HTTP 500. In those cases,
metadata/abstract review remains the stated ceiling. Re-run searches and examine
original methods before designing a study.

## Corrections and related records

**KNOWN — bibliographic notices, not allegations.** All included core records were
checked for publication types and linked corrections/retractions. A separate
`EXT_ID:(25153679 OR 27668327 OR 22184492 OR 28256319) AND SRC:MED` metadata request
verified the notice identities:

- [PMID 23748177](https://pubmed.ncbi.nlm.nih.gov/23748177/), the 2013 MSI risk-factor
  paper, is tagged **Retracted Publication**, linked to [retraction PMID
  25153679](https://pubmed.ncbi.nlm.nih.gov/25153679/), DOI
  [10.1097/IGC.0000000000000255](https://doi.org/10.1097/IGC.0000000000000255).
  Excluded from supporting evidence. The same-title [2014 record PMID
  24755492](https://pubmed.ncbi.nlm.nih.gov/24755492/) has a different DOI; its
  relationship was not established from notice text and it is also context only.
  Do not count these as two independent studies or infer a retraction reason.
- [PMID 25868966](https://pubmed.ncbi.nlm.nih.gov/25868966/), genetic-testing timing,
  has [corrigendum PMID 28256319](https://pubmed.ncbi.nlm.nih.gov/28256319/).
- [PMID 27240134](https://pubmed.ncbi.nlm.nih.gov/27240134/), surgery timing, has
  [correction PMID 27668327](https://pubmed.ncbi.nlm.nih.gov/27668327/).
- [PMID 21969808](https://pubmed.ncbi.nlm.nih.gov/21969808/), progression-free
  survival review, has [erratum PMID 22184492](https://pubmed.ncbi.nlm.nih.gov/22184492/).
- [PMID 16648044](https://pubmed.ncbi.nlm.nih.gov/16648044/) has a linked author-name
  erratum noted in core metadata. Comments and preprint relationships are retained
  separately from corrections. PPR98726 is linked to PMID 34161278 and is not an
  independent confirmation.

Notice bodies were not recovered here. A missing linked notice is not a guarantee
that a paper is current; a publisher/Crossmark check remains necessary for any
paper selected for a protocol. No supplied seed had a retraction flag in the
examined metadata. This does not validate the seed findings.

## Thematic timeline and study findings

All findings below are **KNOWN: reported in the cited studies**, not results
reproduced by Project Asma. The limitations column includes our methodological
assessment. Historical claims are not current clinical recommendations.

| Period / theme | Reported findings and primary evidence | Limitations and project implication |
| --- | --- | --- |
| **1989–2002: clinical methods, information and preferences** | Early vulvar/cervical treatment work precedes ovarian decision and information studies. [Elit et al., 1996, PMID 8812525](https://pubmed.ncbi.nlm.nih.gov/8812525/) tested a decision board in small volunteer/patient samples; presentation of survival information influenced preferences. [Stewart et al., 2000, PMID 10831342](https://pubmed.ncbi.nlm.nih.gov/10831342/) surveyed 105 women; over 80% wanted detailed information, and about 60% preferred shared decisions. | Abstract review only. Small, selected historical samples and historical treatment options; this does not validate a present-day decision tool. Supports assessing readability, uncertainty communication and desired participation separately from model accuracy. |
| **1994–2014: hereditary risk, occult disease and prevention** | Population genetics and BRCA carrier cohorts underpin prevention research. [Finch et al., PMID 16137750](https://pubmed.ncbi.nlm.nih.gov/16137750/) found seven occult cancers in 159 prophylactic operations, including three involving tubes without ovaries. [Finch et al., JAMA 2006, PMID 16835424](https://pubmed.ncbi.nlm.nih.gov/16835424/) studied 1,828 carriers and reported an adjusted cancer-incidence HR of 0.20 after oophorectomy. [Zhang et al., 2011, PMID 21324516](https://pubmed.ncbi.nlm.nih.gov/21324516/) reported BRCA mutation frequency of 13.3% in 1,342 unselected Ontario cases. [Finch et al., JCO 2014, PMID 24567435](https://pubmed.ncbi.nlm.nih.gov/24567435/) followed 5,783 carriers and reported HR 0.20 for ovarian/tubal/peritoneal cancer. | Abstract review for these anchors. These are different populations/estimands: occult pathology yield, germline prevalence and observational prevention associations. Carrier cohorts may overlap across releases; no pooling. None establishes how to predict failure of first platinum therapy in an established HGSOC tumor. |
| **2002–2018: molecular origins, biomarkers and histotypes** | [Bernardini et al., 2005, PMID 16036111](https://pubmed.ncbi.nlm.nih.gov/16036111/) profiled 26 serous tumors with aCGH and an expression subset, reporting associations with chemotherapy response. [Tone et al., 2008, PMID 18593983](https://pubmed.ncbi.nlm.nih.gov/18593983/) compared nonmalignant fallopian epithelium from 12 carriers and 12 controls with 13 serous cancers. [Gortzak-Uzan et al., PMID 18076136](https://pubmed.ncbi.nlm.nih.gov/18076136/) reported over 2,500 ascites proteins and an 80-biomarker shortlist. [May et al., 2013, PMID 23253401](https://pubmed.ncbi.nlm.nih.gov/23253401/) reanalyzed public expression profiles separating low- and high-grade serous disease. | Abstracts only; small discovery studies, multiple testing, tissue/cell composition and assay differences. Candidate associations are not validated predictive markers. Old “serous” labels require pathology reconciliation with modern HGSOC definitions. Do not treat ascites fluid, tumor RNA and tumor proteins as interchangeable. |
| **2006–2021: treatment sequence, residual disease and tolerability** | [Chin et al., 2009, PMID 19135709](https://pubmed.ncbi.nlm.nih.gov/19135709/) prospectively evaluated an outpatient IP/IV program in 47 patients. [Bouchard-Fortier et al., 2016, PMID 26546964](https://pubmed.ncbi.nlm.nih.gov/26546964/) retrospectively compared IP regimens in 141 patients. [Rosen et al., 2014, PMID 25026637](https://pubmed.ncbi.nlm.nih.gov/25026637/) studied 326 advanced serous cases, linking residual disease and treatment sequence to survival; [Kim et al., 2021, PMID 33326624](https://pubmed.ncbi.nlm.nih.gov/33326624/) provides longer-term follow-up. [May et al., 2018, PMID 29621126](https://pubmed.ncbi.nlm.nih.gov/29621126/) examined 852 advanced HGSC cases. | Abstracts reviewed. Selection for surgery/NACT, burden of disease, fitness and treatment era confound observational comparisons. Abstracts do not consistently resolve denominators for every completion rate; no completion percentage is rederived here. Treatment sequence and residual disease could confound a response signature, but these studies do not establish the signature's causal or clinical utility. Cohort independence between follow-ups is unverified. |
| **2013–2024: time-dependent survival and epidemiology** | [McLaughlin et al., PMID 23257159](https://pubmed.ncbi.nlm.nih.gov/23257159/) followed 1,626 women, reporting an early BRCA-associated survival advantage that did not persist at ten years. [Kotsopoulos et al., PMID 26556769](https://pubmed.ncbi.nlm.nih.gov/26556769/) examined 1,421 cases; [PMID 35710751](https://pubmed.ncbi.nlm.nih.gov/35710751/) examined 1,422 and 12 susceptibility genes, emphasizing residual disease over BRCA for long-term survival. [Kim et al., 2017, PMID 28208158](https://pubmed.ncbi.nlm.nih.gov/28208158/) and [2024, PMID 38473333](https://pubmed.ncbi.nlm.nih.gov/38473333/) relate prediagnostic exposures to survival, with the latter stratifying time intervals. | 2017/2024 full texts examined; others abstract/public availability page. Ontario recruitment periods and author networks recur: these are a cohort family, not independent replications. Outcome horizons, left truncation, competing death, histotype, confounding and sparse rare-gene subgroups matter. A survival association does not supply a primary-refractory response label or evidence that changing a lifestyle exposure changes survival. |
| **2011–2019: prevention-related quality of life and long-term burden** | [Finch et al., PMID 21913283](https://pubmed.ncbi.nlm.nih.gov/21913283/) reports less cancer-specific worry after surgery but persistent distress in a subset. [Hall et al., PMID 30414741](https://pubmed.ncbi.nlm.nih.gov/30414741/) examines menopause/sexual-function outcomes. [Kotsopoulos et al., 2019, PMID 31390031](https://pubmed.ncbi.nlm.nih.gov/31390031/) studied 95 women with paired bone-density measurements and reported greater postoperative losses among those premenopausal at surgery. | Bone paper full text; others abstracts. Small cohorts, self-report, short follow-up and selection into follow-up measurements limit interpretation. Prevention-carrier outcomes must not be generalized to recurrent cancer. Quality of life, symptoms and function deserve separate endpoints rather than being inferred from tumor response. |
| **2014–2021: ascites biology and mathematical modeling** | [Feigenberg et al., PMID 24982872](https://pubmed.ncbi.nlm.nih.gov/24982872/) compared expression in ten high-volume and nine low-volume ascites HGSOC tumors, reporting immune-related expression differences and examining clinical associations in a larger cohort. It deposits GSE51831. [Gu et al., 2021, PMID 34161278](https://pubmed.ncbi.nlm.nih.gov/34161278/) models resistant-cell dynamics and treatment sequence with clinical-cohort comparisons. | Ascites full text; model abstract only. The ascites paper notes small discovery numbers and inability to find an external dataset with suitable ascites metadata. Immune admixture and surgery selection are alternatives to intrinsic tumor mechanisms. Model predictions depend on assumptions/calibration and are not randomized evidence or a prescribing system. Model code and source data rights remain unverified. |
| **2010–2026: care systems, training and access** | [Rosen et al., 2017, PMID 28861459](https://pubmed.ncbi.nlm.nih.gov/28861459/) describes a Kenya-led fellowship and integrated data collection. [Tong et al., 2022, PMID 35521812](https://pubmed.ncbi.nlm.nih.gov/35521812/) describes the East Africa HPV/HIV consortium. [Shaffi et al., 2024, PMID 38379666](https://pubmed.ncbi.nlm.nih.gov/38379666/) reviews 1,541 cervical cases and documents late presentation and treatment gaps. [Ouma et al., 2026, PMID 41796282](https://pubmed.ncbi.nlm.nih.gov/41796282/) reports 38 trimodal-therapy completers among 62 eligible after surgery, with nonsignificant HIV-group survival differences. | Full texts examined. Program descriptions do not establish causal survival improvement. Retrospective incomplete records and care selection limit comparisons. Cervical cancer/HIV is outside Pilot 001. In the 2026 paper, binary database categories omit mid-treatment discontinuation, and missing HIV/pathology variables complicate inference. Data-system ideas can transfer; disease-effect estimates cannot. |
| **2025: HIPEC lead** | [Seawright et al., DOI 10.1016/j.ygyno.2025.04.342](https://doi.org/10.1016/j.ygyno.2025.04.342), meeting supplement, addresses postoperative outcomes and quality of life; publisher-deposited metadata lists Rosen with Gadzinski and Al-Wahab. | Publisher abstract could not be read. Title/authors/DOI verified through Crossref; no sample size, efficacy, toxicity or quality-of-life finding claimed. Conference abstract is not a full trial report. |

The ten supplied seeds are all individually represented in the bibliography and
above. PMID 16137750 was published online in 2005 but belongs to the 2006 issue;
PMID 26556769 was indexed in 2015 with a 2016 issue. Such dates are not conflicting
paper identities. Thematic periods overlap because these research programs overlap.

## Data, code and reuse: observed availability

No dataset or third-party analysis code was acquired or executed. “Not located”
means not found through the stated reads, not that a resource does not exist.
Article licenses apply to the article's covered material, not automatically to
participant datasets, instrument text, third-party assets or external software.

| Resource / evidence examined | Observed access and rights | Disposition |
| --- | --- | --- |
| **GSE51831**, linked from the Feigenberg full text, methods §2.1 | [GEO series metadata](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE51831&targ=self&form=text&view=brief) retrieved successfully: public since 2014-10-01, PMID 24982872, GPL10558, raw archive and non-normalized text file listed. Metadata/title/publication match verified; no matrix or sample rows downloaded. The paper states Creative Commons Attribution; a separate dataset-specific license/consent scope was not established from this metadata. | **Candidate** metadata/feasibility work. Verify file-specific rights, sample design, availability, overlap and covariates before any gated acquisition. Public listings do not establish byte integrity, current file accessibility or training rights. |
| **Ontario survival cohorts**, especially 2024 PMID 38473333 | Full-text data statement says data are request-only and not public due to privacy/ethical restrictions. The [2022 publisher page](https://www.nature.com/articles/s41416-022-01840-4), Data availability, mentions authors or dbGaP without a verified accession/access tier. | **Deferred** reanalysis. No open independent outcome dataset established; do not treat the word “publicly” in article text as open-tier permission. No request sent. |
| **Kenya 2026 cohort**, PMID 41796282 | Publisher/full text: data on reasonable request; article **CC BY 4.0**, with third-party exclusions. Supplements listed but not downloaded. | **Deferred** data analysis; **candidate** missingness/denominator methods using artificial examples. Request-only is not open data or permission to ingest. |
| **Consortium 2022**, PMID 35521812 | Full text article **CC BY 4.0**; data on reasonable request. Describes reproducibility archives and data infrastructure, not a verified public software repository. | Cite program/data-management design; no claim that its analysis code is available or licensed for reuse. |
| **2017 epidemiology**, PMID 28208158 | Full-text rights state **CC BY-NC-SA 4.0** after the initial embargo. No open participant dataset verified. | Link/cite; any copying or adaptation must observe noncommercial/share-alike conditions. Does not grant dataset or model-training permission. |
| **2017 training** and **2024 cervical-care report**, PMIDs 28861459 / 38379666 | Open full texts state **CC BY-NC-ND 4.0**. | Short original paraphrase and links retained. Do not redistribute adapted full texts or assume source datasets inherit a reuse grant. |
| **2019 bone study**, PMID 31390031; **2024 survival trajectories**, PMID 38473333 | Full texts state **CC BY 4.0**. Source datasets not established as openly reusable. | Attribution for any future covered-text/figure reuse; current assessment includes original summaries only. |
| **2005 genomic-response**, **2008 ascites proteome**, **2008 fallopian expression**, **2013 histotype reanalysis**, **2021 mathematical model** | Abstract/metadata reviewed. Model has a supporting-information indication; no verified executable repository, pinned code version, usable accession/terms for these specific studies was established. Full-text XML failed or absent. | **Unresolved**, not “no code/data.” Do not substitute a dataset from a citing paper, or a generic publisher GitHub footer, for a source release. |
| **HIPEC 2025 abstract** | Crossref metadata contains Elsevier TDM-license links, not an established open article/data/code grant. | **Deferred** findings assessment until readable primary abstract/full report and rights are verified. |

Credit the actual article authors, journal, year, DOI and the source data submitter
for any later reuse; cite the specific release and required notices. Discovery
credit: the seed list and two recent leads were supplied for this task; an earlier
public discovery pointer is unknown. Newly recovered literature was found through
the searches above. This assessment does not claim discovery of the underlying
science. Repository MIT/CC BY terms cover original repository contributions under
[LICENSE](../../LICENSE); third-party content retains its own terms under
[NOTICE](../../NOTICE). A bibliography grants no dataset, full-text,
redistribution, commercial-use or training rights. No legal clearance is implied.

## Ranked Project Asma research-fit questions

These are **CONJECTURE / proposed work**. Ranking weighs relevance to the
[active pilot](../../protocols/pilot-001.md), existing [candidate directions](../directions.md),
feasibility under the [data rules](../reproducibility-and-data.md), and ability to
produce a useful negative result. The scientific endpoint and owner gates remain
those in the [roadmap](../roadmap.md). Existing issue #31 owns execution decisions;
this literature issue does not replace that ownership. No empirical track below
has been executed or adopted.

| Rank / status | Concrete question, evidence and intended contribution | Feasible next artifact, alternatives and stop rule |
| --- | --- | --- |
| **1 — candidate: endpoint/confounding map for Pilot 001** | Which Rosen-network response, treatment-sequence and survival papers measure **primary platinum refractoriness**, and which measure later relapse, survival or prevention? Use PMIDs 16036111, 25026637, 33326624, 23257159, 35710751 and 38473333 to distinguish response labels from long-term prognosis and examine treatment/residual-disease confounding. | Produce a citation-level table of population, histotype, treatment era, index time, endpoint, residual disease, NACT/PDS, assays, cohort family and accessible methods. Compare against Pilot 001's already frozen definitions; do not change labels to obtain agreement. Stop before declaring a study comparable if endpoint or cohort eligibility cannot be recovered. High value, low compute; requires scientific review of interpretation. |
| **2 — candidate: ascites/immune-mixture feasibility** | Does the **GSE51831** low/high-ascites expression design support a reproducible immune/stromal contrast, and can that contrast inform an alternative explanation for bulk-expression associations? Grounded in PMID 24982872 and the project's existing stroma/open-data directions. | First a metadata-only protocol/rights assessment, then, only after Gate 0, a fixed preprocessing/contrast and aggregate gene-set replication with uncertainty. Compare tumor-composition explanation with intrinsic resistance, and an established public HGSOC expression resource with better metadata. Stop if permitted inputs or ascites labels cannot be established, if groups cannot be separated, or if independent validation is absent for the proposed claim. It cannot validate the 64-protein panel's refractory endpoint. |
| **3 — candidate: time-horizon and cohort-family evidence resource** | How do BRCA-survival associations differ across follow-up windows, and how much of the apparent evidence is repeated follow-up of the same Ontario cohort? Grounded in PMIDs 23257159, 26556769, 28208158, 35710751 and 38473333. | Build a publication-level recruitment/follow-up/estimand map and an original artificial-data illustration of time-varying hazards/left truncation. Compare evidence curation with attempting request-only reanalysis; curation is currently more feasible. Stop any meta-analysis until participant overlap is resolved. Do not sum sample sizes across these papers or infer a treatment effect from prognosis. |
| **4 — candidate: completeness and outcome-denominator specification** | Can the project's provenance tools explicitly distinguish treatment eligible, initiated, completed, discontinued and missing outcomes? Inspired by the synoptic-reporting institutional history and PMIDs 38379666/41796282. | Write a small disease-agnostic data dictionary and artificial fixture examples; compare with current manifest/held-out-evaluation contracts before adding code. Include censoring, loss to follow-up and reasons for missingness. Stop any real-cohort test without rights/owner gate. Cervical/HIV effects cannot be transferred to HGSOC; no clinical system or service is proposed. |
| **5 — candidate: patient-important evidence communication** | Which survivorship and information outcomes are missing when an evidence summary focuses only on response or survival? PMIDs 8812525, 10831342, 21913283, 30414741 and 31390031 anchor different settings and measures. | Produce a source-linked outcome taxonomy: symptoms, function, menopause/sexual effects, bone health, uncertainty and participation preference. Compare a literature resource with a patient application; only the former is proposed. Stop before reusing questionnaire/decision-board text without instrument rights and modern validation. No patient recruitment, recommendations or claims of improved comprehension. |
| **6 — deferred: mechanistic treatment-sequence model reconstruction** | Which assumptions in Gu et al. (PMID 34161278) drive the predicted resistant-cell and surgery-sequence effects, and can alternative parameter sets fit the same aggregate course? | Recover readable methods, equations, source release and rights first; then propose an original synthetic sensitivity/identifiability study with comparator assumptions and preregistered outputs. Compare continuing Pilot 001 with this new endpoint; avoid scope drift. Stop if model specification or benchmark aggregates cannot be verified. No therapy optimization claim for an individual. |
| **7 — deferred: HIPEC burden/QOL evidence assessment** | Does the 2025 Seawright abstract lead to a complete report with interpretable postoperative burden and quality-of-life measures? | Recover the primary abstract/full report; identify design, denominators, comparator, timepoints and data/code terms. Stop at metadata if it remains inaccessible. No HIPEC efficacy or safety inference is currently supported by this lead. |

The immediate recommendation is **1**, with **2** as the best newly verified
public metadata lead and **3–5** as useful literature/methods work. The broader
mission remains open-ended, but reading a paper or accepting a record is not
adoption. Any future prototype/adoption needs its actual implementation evidence
and date; none is claimed here.

## Repository provenance and continuation

Read as of base commit `2d0c847cbdf47c68fa1018359a6a8b09ee18ed01`: README,
AGENTS, CONTRIBUTING, mission, data policy, pilot, directions, roadmap, templates,
registry guidance, claims, credit and CI configuration. No repository `.agents`
skills directory was present. Foundation-0's repository standard was read.
Open issues #31/#8 and PR #39 were checked; no existing Rosen issue/PR was found.
PR #39's broader research preservation remains a separate concurrent contribution.
This branch does not rewrite or duplicate its records or scientific work.

The accessible aska-digital/ingestion README, CONTRIBUTING, source-record template,
source tree, a sample canonical record and Foundation-0 navigation index were
inspected. Searches for Rosen issues/PRs found none. Its source-centered pattern is
applied here with **one canonical project assessment and item registry**, and
navigation-only README/registry links. No second canonical assessment is created
in ingestion; no ingestion write was needed to make the requested Project Asma
assessment usable. A future cross-project index should point here rather than
copying the findings.

**Next review work:** independently verify uncertain/legacy identities; inspect
full methods for priority 1; recover correction/retraction notice bodies without
speculating about reasons; resolve the same-title MSI records; inspect the HIPEC
abstract; verify GSE51831 reuse and independent replication options; and append
any corrections or new decisions below and to issue #40. No reviewer has been
recruited or assigned. No study dataset, author code, private context, outreach,
merge or deployment is part of this survey.

## Decision and outcome history

- **2026-11-04:** initial dated assessment and screening snapshot prepared as a
  candidate research resource for issue #40. Bibliographic screening executed;
  studies not reproduced. Proposed research uses remain candidate/deferred.
  Later corrections and outcomes should append to this record, preserving the
  initial assessment and recording their supporting evidence.

## 2026-11-05 identity reassessment and targeted recall audit

This is a **dated follow-up**, preserving the 2026-11-04 assessment above and the
original counts in `initial_snapshot_counts` in the
[registry](../../registries/barry-rosen-bibliography.json). The original 209
uncertain records were **broad-name ambiguities**, not 209 likely missing ovarian
oncology papers. None of their titles explicitly says “ovarian” or
“immunotherapy”; natural-killer-cell, leukemia, breast-cancer, gynecologic and
patient-information papers nevertheless warranted individual attention. Many
other records concern bacterial transport, psychiatry, imaging or health systems.

**Executed screening result:** 79 of those 209 records are now excluded from
attribution to the target clinician: **39** have a different given name in
publisher-deposited metadata, **six** have a direct primary author-name or
contributor-affiliation mapping, and **34** have a combined institutional,
biochemical-topic and coauthor basis. The last group is explicitly labelled
**identity inference**, not individual author-affiliation verification. No entry
was excluded solely for a P initial. **130 remain uncertain**, and the **215
provisionally attributed entries remain unchanged**. Current totals in the same
2,046-record universe are 215 included, 1,701 excluded and 130 uncertain. Exclusion
from this bibliography is not an assertion that a paper lacks scientific value.

All 209 unresolved titles were triaged; Crossref DOI metadata requests were made
for the 184 with a DOI. **152** succeeded and **32** failed. The examined fields
were `message.title`, author given/family names and affiliations, with the DOI
matched to the existing record. For example, [PMID 8529954's publisher-deposited
record](https://api.crossref.org/works/10.1159/000292334) gives **Bruce**, not Barry.
Other resolved names include Bernard, Barbara, Boaz, Beth, Betty, Barney, Benson,
Baruch and Brenda. These are author-metadata checks, not scientific reviews.
The 35 attempted Europe PMC XML routes recovered four usable author mappings;
most other routes returned HTTP 500. Nine additional triaged records had no PMC
identifier to attempt. No failed retrieval was treated as an identity decision.
Every changed record retains its old disposition, dated new basis, evidence
level and primary URLs in `screening_history` and `identity_evidence`.

### High-value cross-checks

| Record | Evidence actually inspected | Dated disposition and limit |
| --- | --- | --- |
| **MED:6374239**, natural killer cells / radiation-induced leukemogenesis | The [publisher's publicly returned author/abstract page](https://academic.oup.com/jnci/article-pdf/72/6/1397/3168949/72-6-1397.pdf) (redirects to a minimal article page) names **Boas Rosen**, mapped to the Biological Therapeutics Branch, NCI-Frederick. | **Excluded**, direct primary name/institution evidence. The source spells the given name “Boas”; it is not silently normalized from an aggregated profile. This is not evidence of Toronto ovarian immunotherapy work. Only public author/abstract metadata was inspected, not the subscription PDF. |
| **PPR:PPR1164615**, glutaminase / triple-negative breast cancer | The [preprint's front matter](https://www.preprints.org/manuscript/202603.0868/v1/download) gives FIU Cellular and Molecular Medicine as the author-group affiliation. Its [journal counterpart XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13204110/fullTextXML) specifically maps Rosen to that FIU affiliation. | **Excluded**, direct primary affiliation evidence. A cancer-related title does not identify the gynecologic oncologist. The two versions are not independent studies; no anticancer efficacy finding is imported into Asma. The preprint states CC BY 4.0, which does not establish a dataset or training grant. |
| **MED:15336539**, AQP9 / leukemia drug sensitivity | [Primary bibliographic metadata](https://pubmed.ncbi.nlm.nih.gov/15336539/) lists Wayne State Biochemistry and Molecular Biology and Bhattacharjee/Carbrey/Mukhopadhyay with Rosen BP. A [separate primary article](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC1241237/fullTextXML) maps Rosen and Mukhopadhyay to Wayne State biochemistry; the FIU institutional career account supports the same network. | **Excluded by combined institutional/topic/coauthor inference**. The old item's affiliation is article-level, not independently mapped to each author. Its publisher route could not be inspected. This qualified exclusion must not be reported as direct author-affiliation verification. |
| **MED:20861301**, yeast selenite transport | [Article XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2982120/fullTextXML), Rosen contributor `xref aff2`, identifies FIU. Oakland belongs to another author affiliation in the same article. | **Excluded**, direct mapping. Merely finding “Oakland” anywhere in an article would have been misleading, despite its role in the clinician's institutional history. |
| **MED:22968824 / MED:22020067**, mouse resource / malaria genetics | [Mouse-resource XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3463800/fullTextXML) maps Rosen to Sanger (`Aff1`); [malaria-genetics XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3431185/fullTextXML) does likewise (`A1`). The [IMPC consortium page](https://www.mousephenotype.org/about-impc/about-ikmc/eucommtools/), Participants, independently lists Barry Rosen with the Sanger Bradley/Skarnes/Bushell/Iyer group. | **Excluded**, direct primary affiliation plus institutional/coauthor cross-check. Identical “Barry Rosen” names do not justify pooling different professional networks. |
| **MED:24316947**, colorectal internet patient information | [Publisher-deposited Crossref metadata](https://api.crossref.org/works/10.1097/DCR.0000000000000011) still gives only “B. Rosen”, without an author-specific affiliation. The bibliographic record includes Toronto/Northwestern institutions but does not map Rosen to them. Publisher retrieval failed. | **Still uncertain**. Its topic could inform the existing evidence-communication question, but it is not attributed to this clinician or used as supporting evidence here. Toronto in an article-wide affiliation list is insufficient. |
| **MED:8416443**, IUD location/failure | [PubMed](https://pubmed.ncbi.nlm.nih.gov/8416443/) gives B Rosen and an article-level Hadassah affiliation. Indexed Ovid metadata suggests Bruno Rosen, but the direct abstract returned payment-required and other direct publisher routes failed. | **Still uncertain**, with an explicit verification lead. A search snippet was not promoted to a resolved identity. No full text was purchased or copied. |
| **MED:8345054**, athlete MRI | Crossref still gives B; the related 1995 paper resolves to Bruce. | **Still uncertain**. Similar titles and coauthors suggest a route to resolve it, but that item's affiliation/name was not independently recovered. |

**Identifier caution:** the Europe PMC author metadata and the public ORCID works
response for `0000-0002-5230-4271` span FIU biochemical and Sanger genetics
records. We inspected the [ORCID works response](https://pub.orcid.org/v3.0/0000-0002-5230-4271/works)
but did not use it to assign the clinician's identity or automatically resolve
any record. The directly inspected institutional mappings take precedence. This
observation identifies a cross-cluster ambiguity in the available metadata; it
is not an adjudication of who introduced an erroneous identifier or whether every
cross-cluster assignment is erroneous. The original INPP4B exclusion should be
read with its topic/coauthor evidence, not as a rule that this ORCID alone proves
every attribution.

### Targeted ovarian and immune recall

These additional Europe PMC queries ran on **2026-11-05**, `resultType=core`,
`format=json`, `pageSize=1000`; each returned fewer than 1,000 entries and the
entire returned page was examined. Exact request URLs and new-record triage are
in `identity_followup.recall_queries` in the registry. These query results are
separate from the original 2,046-record universe, not silently added to its counts.

| Exact query | Hits | Records absent from the initial universe |
| --- | --- | --- |
| `(AUTHOR:"Rosen B" OR AUTHOR:"Rosen BP") AND (immunotherapy OR lymphocyte OR immune OR interleukin OR checkpoint OR vaccine OR adoptive)` | 231 | 20 |
| `(AUTHOR:"Rosen B" OR AUTHOR:"Rosen BP") AND (ovarian OR tubo-ovarian OR fallopian OR serous OR ascites)` | 222 | 0 |
| `"Barry Rosen" AND (ovarian OR immunotherapy OR lymphocyte)` | 160 | 16 |
| `(AUTHOR:Rosen) AND (AUTHOR:Oza OR AUTHOR:Bernardini OR AUTHOR:Ohashi OR AUTHOR:Hiranoj OR AUTHOR:Hirano OR AUTHOR:Nguyen) AND (ovarian OR immunotherapy OR lymphocyte)` | 267 | 248 |

The last query deliberately broadens recall and contains the literal `Hiranoj`
variant as entered; its many unrelated ADNI/neuroimaging and other-Rosen matches
are not ovarian publications. New exact B/BP matches in these queries had other
given names or incompatible affiliations, or lacked evidence for attribution;
none warranted a new target inclusion. Full-name text searches also match
references and acknowledgements, which must not be confused with authorship.
“No additional target inclusion in these searches” is not a completeness claim.

The [primary registry record for NCT01883297](https://clinicaltrials.gov/api/v2/studies/NCT01883297)
was inspected as an ovarian adoptive-cell-therapy recall lead. It names UHN as
sponsor and Marcus Butler as principal investigator; no Rosen is named in the
examined officials. Its last posted update was 2026-07-07 and status was
`ACTIVE_NOT_RECRUITING` at this read. It establishes a related research program,
not Rosen authorship, efficacy or a dataset available for Asma. The suggested
[2015 conference PDF](https://plone.bcgsc.ca/about/ccic-2015/CCIC2015_Abstracts_all.pdf)
could not be recovered (web 502; executor proxy tunnel 403). No conference
attribution or finding is asserted from that inaccessible document.

### Remaining coverage and next discriminating work

The 130 remaining records include many older transport, imaging, psychiatry and
health-system publications with initials or missing affiliation metadata, plus
the explicitly unresolved clinical records above. Some are likely other authors,
but evidence strength has not earned a resolved disposition. Thirty-four of the
new exclusions also remain **inferences** rather than direct person-level
verification. Do not call the full corpus verified by subtracting uncertain rows.

The most useful next identity work is a readable primary author header for
MED:24316947, MED:8416443 and MED:8345054; recovery of the conference source through
an authorized accessible primary route; and author-specific mapping for any
inferred item that might materially change an Asma question. Newly accessible
conference proceedings, consortium-only credits and records absent from the
literature indexes can still change recall. This follow-up adds no scientific
validation, study-data analysis, code execution, adoption or treatment claim.
The ranked questions above retain their candidate/deferred status.

- **2026-11-05 outcome:** 79 uncertainty-to-exclusion decisions, explicit evidence
  levels and preserved history; no new target inclusions; four targeted recall
  queries and a primary trial-registry check. Independent screening and the
  listed access/identity gaps remain open in issue #40.
