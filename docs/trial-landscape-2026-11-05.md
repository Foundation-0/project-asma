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

_Result table and observed provenance will be inserted after the reviewed script runs._

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

_Commands and observed checks will be inserted after execution._

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
