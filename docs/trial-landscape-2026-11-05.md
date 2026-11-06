# Recruiting ovarian-cancer trial language: a frozen registry snapshot

**Direction 8 · issue [#58](https://github.com/Foundation-0/project-asma/issues/58).**
This is a descriptive audit of public ClinicalTrials.gov registry text, not a
review of trial results, an eligibility assessment or enrollment/treatment advice.
The report date uses **America/Chicago**; execution also records UTC explicitly.

## Question and evidence class

Which phase categories and prespecified language buckets occur among records
returned by the specified recruiting/interventional ovarian-cancer query?

**VERIFIED** below means finite counting of the retrieved metadata under the
stated rules. It does not validate a study, a biomarker or a clinical inference.
**KNOWN** statements describe the cited registry documentation and terms.
There are no PROVEN biological claims, novelty claims or proposed treatment
choices in this result. Registry text is not trial results.

## Rules fixed before acquisition

The machine-readable [protocol](../protocols/trial-landscape-keywords-v1.json)
was committed before any trial response was requested. The initial commit was
`476a6c5`; documentation-only corrections before acquisition removed unsupported
NCTId sorting (`eba6549`) and clarified that later pages may omit totalCount
(`5a50983`). No keyword list or text field was selected after inspecting results.
The commit identifiers here refer to the original local history. Publication
used the connected GitHub API because command-line Git/GitHub credentials were
unavailable. API publication creates new commit IDs and timestamps; each commit
message retains the original local ID and timestamp, while tree/file bytes and
the execution's code/protocol SHA-256 pins remain unchanged. Thus publication
time is distinct from local prespecification and acquisition time.

These are original descriptive-audit rules; no existing locked Pilot checker
was changed. The issue requests this new script and its result in one PR.

The query is exactly:

```text
query.cond=Ovarian Cancer
filter.overallStatus=RECRUITING
query.term=AREA[StudyType]INTERVENTIONAL
```

Request JSON with `pageSize=1000`, `countTotal=true`, no explicit sort, and these
leaf fields only: `NCTId,BriefTitle,OfficialTitle,OverallStatus,StudyType,Phase,
Condition,Keyword,BriefSummary,EligibilityCriteria`. Follow every returned
`nextPageToken` with otherwise unchanged parameters. NCT IDs exist only in
memory for uniqueness checks; they are not published. Results, contacts,
locations, enrollment counts and participant data are not requested.

**KNOWN — search boundary (S126):** the condition query uses the registry's
ConditionSearch expression, including synonyms and fields beyond the literal
condition list. It is a search-defined set that may include basket studies,
multiple cancers and differing histotypes. No manual ovarian-only or
histotype restriction is applied. The recruiting filter refers to the registry's
overall status, not confirmation of any individual site's availability.

### Text corpus and literal keyword lists

Match each brief title, official title, brief summary, condition list item,
keyword list item and eligibility-criteria string **separately**. Do not join
fields or list items into new phrases. Exclude detailed descriptions,
intervention text, result fields and all contact/location information.

| Bucket | Exact alternatives after normalization |
| --- | --- |
| Generic biomarker language | `biomarker`; `biomarkers` |
| BRCA language | `brca`; `brca1`; `brca2`; `brca1/2` |
| HRD language | `hrd`; `homologous recombination deficiency`; `homologous recombination deficient` |
| Folate-receptor-alpha language | `folr1`; `fralpha`; `fr alpha`; `folate receptor alpha` |
| Platinum-resistant language | `platinum resistant`; `platinum resistance` |
| Platinum-refractory language | `platinum refractory`; `platinum refractoriness` |

Normalize Unicode with NFKC, casefold, replace Greek `α` with `alpha`, replace
Unicode dash punctuation and ASCII hyphens with spaces, and collapse whitespace.
Use literal phrases bounded by Unicode word boundaries. No stemming, fuzzy
matching, inferred synonyms or semantic classification. For example,
`platinum-resistant` matches the resistant bucket; `non-BRCA` still mentions
BRCA. No negation or inclusion/exclusion distinction is inferred.

The first four buckets form **any biomarker bucket**; the last two form
**any platinum bucket**. A study counts at most once per bucket. Buckets overlap;
adding their counts does not yield a study total. Also report the union,
complement, and four mutually exclusive biomarker/platinum overlap cells.
For each bucket, also count presence in eligibility text and in the other
selected text. These source-presence counts overlap: a study can appear in both;
do not add them to obtain the whole-corpus count.

Missing/null/empty optional text contributes no match and is counted in the
missingness table; malformed non-null types stop the audit.

These are deliberately limited dictionaries, not all biomarkers or all ways
of describing resistance. An unlisted marker, abbreviation or paraphrase can
be missed. Direct phrases may miss shared-head wording such as
“platinum resistant/refractory.” A mention can describe exclusion or background,
not an enrolled cohort. Refractory wording does not establish **primary**
platinum-refractory disease, and neither resistance bucket is a Pilot 001 cohort.

### Phase, completeness and retention

A study enters exactly one canonical phase-combination category. Preserve
combined phases rather than selecting the highest or counting a study twice.
Keep `NA` (not applicable) separate from `NOT_REPORTED` (absent/null/empty).
Reject unknown or duplicate phase values, and `NA` mixed with another phase.
**KNOWN (S126):** the API permits phase arrays including combined phases.

Require the first-page integer `totalCount`, unique study IDs, no repeated page
tokens, terminal pagination and exact agreement of retrieved unique count with
the advertised total. Any later `totalCount` must agree; the documented API can
omit it on later pages. Empty intermediate pages are allowed when a next token
exists. Validate every record's recruiting/interventional status and type.
Read API version and data-processing timestamp before and after retrieval and
require equality. Failures emit no response bodies, identifiers or partial
result artifact. Response size and page limits bound acquisition.

Only aggregate JSON, request URLs, whole-response hashes and execution provenance
are retained. No record list, trial-level classification, narrative excerpt,
patient-like row, study matrix or private Asma material is saved. Source response
hashes identify received bytes, not scientific validity. The count/version
checks detect some drift; they do not guarantee an atomic historical database
snapshot. A later live query can legitimately return different counts.

## Executed result

**VERIFIED (V29): 592 unique registry records** matched the live
query; the returned `totalCount` was also **592**. This is a new
retrieval, not reuse of the historical direction-8 number. The prior proposal's
590 is dated 2026-11-04; this audit does not identify which records changed or
infer that a count difference represents newly opened trials.

**VERIFIED (V29):** **155** records
matched at least one of the four biomarker buckets, **120**
matched at least one platinum bucket, and **50**
matched both groups. **111** matched
platinum-resistant language and **53**
matched platinum-refractory language; those buckets overlap and are not cohorts.
**367** matched none of this limited dictionary, which does not
mean those studies lack biomarkers or resistance-related relevance.

The [aggregate certificate](../results/trial-landscape-2026-11-05/certificate.json)
is the authoritative output; [the result record](../results/trial-landscape-2026-11-05/PROOF.md)
states the verifier's obligations and limits.

**VERIFIED execution provenance:**

| Field | Observed value |
| --- | --- |
| Retrieval, America/Chicago | `2026-11-05T22:52:35.477181-06:00` to `2026-11-05T22:52:38.957746-06:00` |
| Retrieval, UTC | `2026-11-06T04:52:35.477181+00:00` to `2026-11-06T04:52:38.957746+00:00` |
| ClinicalTrials.gov processing timestamp | `2026-11-05T10:00:06` **UTC**, unchanged before/after |
| API version | `2.0.5`, unchanged before/after |
| Runtime | Python `3.12.14`; Unicode data `15.0.0` |
| Study-response pages | `1`, terminal, with `592` distinct IDs reconciled in memory |
| Implementation SHA-256 | `d8c66078363c7a70d9223d0eca7daed2a7e865c793bb7882e33aa341a25d1440` |
| Prespecified protocol SHA-256 | `986804b5f30c3ca244df9f0e83f450880415b27c6cc884f867154c56874ba8b6` |

**KNOWN (S126):** the API documents `dataTimestamp` as UTC even though the raw
string has no timezone suffix. It is the registry processing timestamp, not the
last-update date of every individual record. The local retrieval date is
**2026-11-05** despite the execution's **2026-11-06 UTC** date.

Exact study request actually executed (response hash is in the certificate):

```text
https://clinicaltrials.gov/api/v2/studies?query.cond=Ovarian+Cancer&filter.overallStatus=RECRUITING&query.term=AREA%5BStudyType%5DINTERVENTIONAL&format=json&pageSize=1000&countTotal=true&fields=NCTId%2CBriefTitle%2COfficialTitle%2COverallStatus%2CStudyType%2CPhase%2CCondition%2CKeyword%2CBriefSummary%2CEligibilityCriteria
```

All counts in the following generated table are **VERIFIED (V29)**. Phase
categories are mutually exclusive; keyword/source buckets overlap as specified.
Only observed phase categories appear. The missingness rows count fields that
are absent, null, empty or whitespace-only in the selected corpus.

<!-- BEGIN GENERATED TRIAL COUNTS -->
| Measure | Count |
| --- | ---: |
| Total studies | 592 |
| API total count | 592 |
| API study pages | 1 |
| Any dictionary bucket | 225 |
| No dictionary bucket | 367 |
| phase_counts: EARLY_PHASE1 | 7 |
| phase_counts: NA | 172 |
| phase_counts: PHASE1 | 127 |
| phase_counts: PHASE1+PHASE2 | 91 |
| phase_counts: PHASE2 | 123 |
| phase_counts: PHASE2+PHASE3 | 11 |
| phase_counts: PHASE3 | 55 |
| phase_counts: PHASE4 | 6 |
| bucket_counts: biomarker_generic | 46 |
| bucket_counts: brca | 85 |
| bucket_counts: folate_receptor_alpha | 32 |
| bucket_counts: hrd | 48 |
| bucket_counts: platinum_refractory | 53 |
| bucket_counts: platinum_resistant | 111 |
| group_counts: any_biomarker_bucket | 155 |
| group_counts: any_platinum_bucket | 120 |
| biomarker_platinum_overlap: biomarker_only | 105 |
| biomarker_platinum_overlap: both | 50 |
| biomarker_platinum_overlap: neither | 367 |
| biomarker_platinum_overlap: platinum_only | 70 |
| missing_text_fields: brief_summary | 0 |
| missing_text_fields: brief_title | 0 |
| missing_text_fields: conditions | 0 |
| missing_text_fields: eligibility | 0 |
| missing_text_fields: keywords | 219 |
| missing_text_fields: official_title | 1 |
| eligibility_bucket_counts: biomarker_generic | 26 |
| eligibility_bucket_counts: brca | 78 |
| eligibility_bucket_counts: folate_receptor_alpha | 27 |
| eligibility_bucket_counts: hrd | 41 |
| eligibility_bucket_counts: platinum_refractory | 48 |
| eligibility_bucket_counts: platinum_resistant | 92 |
| other_text_bucket_counts: biomarker_generic | 22 |
| other_text_bucket_counts: brca | 25 |
| other_text_bucket_counts: folate_receptor_alpha | 17 |
| other_text_bucket_counts: hrd | 26 |
| other_text_bucket_counts: platinum_refractory | 6 |
| other_text_bucket_counts: platinum_resistant | 71 |
| Page 1 retrieved studies | 592 |
<!-- END GENERATED TRIAL COUNTS -->


## Reuse, attribution and source limits

**KNOWN (S127–S128):** source **ClinicalTrials.gov**, U.S. National Library of
Medicine. Its [terms](https://clinicaltrials.gov/about-site/terms-conditions)
apply across acquisition formats. They call for source attribution, current data,
a displayed processing date, and disclosure of modifications; they prohibit
proprietary claims over the database. International and third-party copyrights
may apply. This record does not assign CC0 or the repository's license to the
source database. The [disclaimer](https://clinicaltrials.gov/about-site/disclaimer)
places responsibility for study information with sponsors/investigators and
warns that listing does not mean government approval of safety or science.

Terms and official API documentation were inspected on **2026-11-06 UTC**, before
bulk retrieval. The terms page's rendered content was read through its official
site asset; the canonical page remains the reference. All modifications here
are disclosed above: field projection, text normalization, literal matching,
phase categorization and aggregation. The output is explicitly historical, not
a continually updated enrollment directory. Keeping a dated analytical result
is our implementation judgment, not a claimed exemption from the terms' update
recommendation. Re-query for any new snapshot and preserve this one as dated.

Primary methodology sources:

- [Official API v2 OpenAPI specification](https://clinicaltrials.gov/api/oas/v2)
  and [API documentation](https://clinicaltrials.gov/data-api/api) — query,
  pagination, projection, phase and version semantics (S126).
- [Search areas](https://clinicaltrials.gov/api/v2/studies/search-areas),
  [field metadata](https://clinicaltrials.gov/api/v2/studies/metadata), and
  [enumerations](https://clinicaltrials.gov/api/v2/studies/enums) — search scope
  and field contracts (S126).
- [Terms](https://clinicaltrials.gov/about-site/terms-conditions) (S127) and
  [disclaimer](https://clinicaltrials.gov/about-site/disclaimer) (S128).

## Reproduction and validation

Run from the repository root with Python 3.10+ and its standard library. The
observed run used the runtime above; Python's Unicode version can affect text
normalization and must be recorded for comparisons.

```sh
# Offline: verify the frozen artifact, code/protocol hashes and report numbers.
python3 results/trial-landscape-2026-11-05/verify.py
python3 tools/audit_trial_landscape.py --check-snapshot results/trial-landscape-2026-11-05/certificate.json

# Offline: print every reported aggregate count from the frozen certificate.
python3 tools/audit_trial_landscape.py --render-report-table results/trial-landscape-2026-11-05/certificate.json

# Live: same pinned query and rules; stdout contains aggregate JSON only.
python3 tools/audit_trial_landscape.py

# Live: fail if current aggregate counts or source version differ from this snapshot.
# Does not overwrite the frozen artifact. Byte-identical response order is not required.
python3 tools/audit_trial_landscape.py --compare results/trial-landscape-2026-11-05/certificate.json

# Offline software checks, including the new artificial-data tests.
python3 -m unittest tests.test_trial_landscape -v
make verify
```

**VERIFIED software checks:** 40 new artificial-data tests pass. They cover
Unicode/boundary/negation examples, independent field matching, overlapping
buckets, combined/missing phases, invalid shapes, pagination failures, count and
source-version drift, safe error output, and atomic output preservation.
Repository-wide `make verify` passed: **350 Python tests**, source/link
validation, implementation-hash checks (including previously documented allowed
drift), tracked-study-source checks, and the existing educational JavaScript/model
checks. A second live `--compare` run at **2026-11-06T04:54:00.143268+00:00**
to **2026-11-06T04:54:03.151445+00:00** reproduced every aggregate count and
the source version. Its whole study-response SHA-256 also matched. This is
a repeated query to the same service, not independent scientific validation.
These checks exercise software properties, not clinical or semantic accuracy.

The implementation was committed as `e355220` after those tests and before the
live run. There were no failed live acquisitions and no post-retrieval keyword,
corpus or counting changes. Earlier API-documentation corrections are recorded
above. Independent Astra method review found no material counting defect;
internal review is not external scientific review.

`make verify-trial-landscape` checks this result only. `make verify-fast` and
`make verify` run the repository's offline Python, metadata-hash and educational
JavaScript/model checks; they do not run network audits or the separate pinned
container/R pipeline. `make certificates` deliberately regenerates only byte
integrity pins after validation; it does not re-fetch or replace the snapshot.
Future checker changes require separate review, not silent regeneration to
obtain agreement with a desired result.

A live re-query can test the same method on the currently served registry.
Because raw trial records are deliberately not archived, offline checks can
reproduce the published aggregate tables and check their consistency, but cannot
independently reconstruct the historical classifications. Do not describe a
hash or an offline arithmetic check as independent verification of registry text.

## Interpretation and continuation

No systematic evidence review or search for research novelty was performed.
This snapshot describes where selected words occur in registry text. It cannot
rank treatment promise, establish biomarker requirements, distinguish all
resistance definitions, measure recruitment access, or reveal an unstudied
biological mechanism. Zero matches would mean only no match under this corpus
and dictionary. It would not mean no trials or no existing research.

A future comparison would need a separately fixed question, consistent corpus
and dictionary, and another dated acquisition. Any manual validation of
classification meanings would be a separate protocol; it was not performed here.
This work leaves Pilot 001 execution gates and the parallel biology track
[#57](https://github.com/Foundation-0/project-asma/pull/57) unchanged.

## AI assistance

Prepared with OpenAI Codex under human direction, with **GPT-6 Astra** agents
for independent method/terms review, implementation and synthetic-test review.
The coordinating agent integrates the report and checks. This is internal
software/method review, not external scientific or clinical peer review.
