# Ovarian cancer interventional trial landscape, 2026-11-13 UTC

**Not clinical advice.** This note counts public ClinicalTrials.gov registration
records. It is not a treatment recommendation, not a ranking of trials, and not
evidence that any intervention helps or harms a patient. A keyword hit is not efficacy.

## Question

How many interventional studies does the ClinicalTrials.gov API v2 return for
the condition query `Ovarian Cancer`, on the processing date below, when counted
by overall status, phase, intervention type, and a pinned keyword map? How does
the recruiting subset of that same condition query compare, in aggregate, with
the [2026-11-05 snapshot](trial-landscape-2026-11-05.md)?

The cohort is whatever the registry's condition search returns. It is not a
histotype-confirmed ovarian-cancer population. Basket trials and studies of
other diseases that the search expands into can remain.

## Query and clock

The machine-readable map is
[protocols/trial-landscape-keywords-v2.json](../protocols/trial-landscape-keywords-v2.json).
It was written before this retrieval. The studies request is:

`https://clinicaltrials.gov/api/v2/studies?query.cond=Ovarian+Cancer&query.term=AREA%5BStudyType%5DINTERVENTIONAL&format=json&pageSize=1000&countTotal=true&fields=NCTId%2CBriefTitle%2COfficialTitle%2COverallStatus%2CStudyType%2CPhase%2CCondition%2CKeyword%2CBriefSummary%2CInterventionType%2CInterventionName`

Retrieval started at **2026-11-13T04:57:57.835069+00:00** and finished at
**2026-11-13T04:58:02.241219+00:00**. In America/Chicago that interval is
**2026-11-12T22:57:57.835069-06:00** through **2026-11-12T22:58:02.241219-06:00**.
The directory name uses the UTC date. The API version documents before and
after the pull are identical: apiVersion `2.0.5`, dataTimestamp
`2026-11-12T10:00:05` (the API documents that timestamp as UTC). The observed
interpreter was CPython 3.12.3, Unicode 15.0.0.

Five projected API page bodies are stored under
[results/trial-landscape-v2-2026-11-13/snapshot/](../results/trial-landscape-v2-2026-11-13/manifest.json).
They are not untouched raw responses: contact email addresses matching
`user@domain.tld` in study-page bodies were replaced with the literal
`[email redacted]` (non-mailbox at-signs such as program names are unchanged).
The redaction list is pinned in `manifest.json` and `certificate.json`. Their
concatenated SHA-256 after redaction, with no separator, is `archive_sha256` in
the count block; the pre-redaction concatenated hash is `archive_as_fetched_sha256`.
Exact page URLs, including pagination tokens, are in
[manifest.json](../results/trial-landscape-v2-2026-11-13/manifest.json). The
projected fields are public registry text: identifiers, titles, status, phase,
conditions, keywords, brief summaries, and intervention names and types.
Eligibility criteria were not requested and are not archived. No participant-level
rows were requested or stored.

**Email redactions (NCT id, field):** NCT02834013, `descriptionModule.briefSummary`.

The recruiting comparison uses the 2026-11-05 query unchanged, with `pageSize=1`
and `countTotal=true`, and is frozen as `snapshot/recruiting-query.json`:

`https://clinicaltrials.gov/api/v2/studies?query.cond=Ovarian+Cancer&filter.overallStatus=RECRUITING&query.term=AREA%5BStudyType%5DINTERVENTIONAL&format=json&pageSize=1&countTotal=true&fields=NCTId%2COverallStatus%2CStudyType`

## Counts

Status counts and phase counts each partition the cohort. Intervention-type
counts are study-level presence: a study with two types is counted once in
each, so those columns overlap and are not a second headcount. Target classes
also overlap. `any_target_class` is the union of folate-receptor language,
FRα ADC name-or-phrase, PARP-inhibitor lexicon, CDR2/CDR2L, mesothelin, MUC16,
and immunotherapy lexicon. CA-125 language is reported and is **not** in that
union.

<!-- BEGIN GENERATED TRIAL LANDSCAPE V2 -->
total_studies: 4260
api_total_count: 4260
api_version: 2.0.5
data_timestamp: 2026-11-12T10:00:05
page_count: 5
archive_as_fetched_sha256: 73bb1e758985afc2762c9c1045d3cbba4ec9610ca9ada1b60dde94fa22c6cd41
archive_sha256: b494f83190d9b78cf7286b8ae09fb88d29a4bb2325b6b950e1366c8c4afe3258
same_query_recruiting_total: 591
corpus_recruiting: 591
prior_total_studies: 592
aggregate_recruiting_delta: -1
nct_level_diff: not_reconstructable
diff_reason: prior_artifact_has_no_nct_identifiers
new_nct_ids: null
removed_nct_ids: null
status_changes: null
any_target_class: 842
no_target_class: 3418
efficacy_evidence: none
nct_status_count: 4260
nct_status_sha256: 0852e91d698673411dd763f5f8128bc2807441f3661c2d2b3e78fd7057bd5c81
status: ACTIVE_NOT_RECRUITING 286
status: COMPLETED 2001
status: ENROLLING_BY_INVITATION 13
status: NOT_YET_RECRUITING 172
status: RECRUITING 591
status: SUSPENDED 15
status: TERMINATED 486
status: UNKNOWN 551
status: WITHDRAWN 145
phase: EARLY_PHASE1 91
phase: NA 1063
phase: PHASE1 915
phase: PHASE1+PHASE2 438
phase: PHASE2 1132
phase: PHASE2+PHASE3 61
phase: PHASE3 390
phase: PHASE4 170
intervention_type: BEHAVIORAL 261
intervention_type: BIOLOGICAL 570
intervention_type: COMBINATION_PRODUCT 30
intervention_type: DEVICE 120
intervention_type: DIAGNOSTIC_TEST 59
intervention_type: DIETARY_SUPPLEMENT 127
intervention_type: DRUG 2971
intervention_type: GENETIC 38
intervention_type: OTHER 637
intervention_type: PROCEDURE 537
intervention_type: RADIATION 69
class: biomarker_generic 267
class: brca 205
class: ca125_language 65
class: cdr2_cdr2l 0
class: folr1_language 53
class: fralpha_adc 39
class: hrd 67
class: immunotherapy 510
class: mesothelin 39
class: muc16 8
class: parp_inhibitor 324
class: platinum_refractory 68
class: platinum_resistant 447
missing_text: brief_summary 0
missing_text: brief_title 0
missing_text: conditions 0
missing_text: intervention_names 0
missing_text: keywords 1430
missing_text: official_title 37
<!-- END GENERATED TRIAL LANDSCAPE V2 -->

The pull returned 4260 unique interventional studies. The all-status pull
contains 591 studies with overall status RECRUITING, and the dedicated
recruiting query returned 591. The 2026-11-05 certificate recorded 592 for that
same recruiting query. The aggregate recruiting delta is therefore -1.

## Difference from the 2026-11-05 snapshot

The earlier certificate stores aggregate counts and response hashes. Its
protocol forbade NCT identifier lists, and the file contains none. An
identifier-level diff is **not reconstructable**. `new_nct_ids`,
`removed_nct_ids`, and `status_changes` are JSON null, not empty lists: null
means the lists cannot be produced, not that no study changed.

This snapshot retains every current NCT identifier and status inside the frozen
pages. Their canonical JSON digest is `nct_status_sha256` in the count block, so
a later snapshot that keeps the same digest rule can name additions, removals,
and status changes. This note does not guess which single recruiting record
accounts for the aggregate change from 592 to 591.

## What a class count is

Matching is Unicode NFKC, casefold, Greek alpha to the letters "alpha", dashes
to spaces, then a literal word-boundary phrase. There is no stemming and no
negation removal, so "not a PARP inhibitor" still counts. Fields searched are
the brief title, official title, brief summary, each condition, each keyword,
and each intervention name.

- **folr1_language** repeats the 2026-11-05 folate-receptor phrases.
- **fralpha_adc** counts a mirvetuximab / soravtansine / Elahere / IMGN853 name,
  or folate-receptor language together with an antibody-drug-conjugate phrase.
  The name list is the agent in this repository's FDA notice plus those spellings.
  It is not a complete ADC catalogue. Context words alone do not count.
- **parp_inhibitor** is a pinned lexicon of the phrase and of generic and brand
  names. It is not a formulary and not proof the study's primary question is
  that class.
- **cdr2_cdr2l** is `cdr2`, `cdr2l`, and anti-Yo phrasing. A zero is a zero on
  this lexicon and these fields, not a proof that no such study exists under
  another name.
- **mesothelin** is `mesothelin` or `msln`. **muc16** is `muc16` or `muc-16`.
- **ca125_language** is CA-125 phrasing. Most such phrases are laboratory-marker
  language. They are not counted as MUC16-directed interventions.
- **immunotherapy** is a pinned lexicon of the words and of common checkpoint-inhibitor
  and CAR-T phrases. It is incomplete and can match background or exclusion text.
- **biomarker, BRCA, HRD, and platinum phrases** repeat the 2026-11-05 dictionary
  on this narrower field set and this broader cohort. They are not a replay of
  that snapshot's eligibility-inclusive counts.

## Limits

Search expansion, synonyms, and basket trials are properties of the registry
query, not filters applied here. The pull is one processing timestamp, not an
atomic snapshot guarantee beyond the before/after version documents matching.
Keyword classes are not curated mechanism assignments. Registration is not
efficacy: outcome and adverse-event fields were not requested. Nothing in this
note selects, ranks, or recommends a trial or a drug.

Source terms remain those of ClinicalTrials.gov (S126–S128). This repository
does not claim a licence over the registry. The frozen pages are a dated,
field-projected copy with contact-email redaction and the transformations above
disclosed.

## Reproduction

From the repository root:

```sh
python3 results/trial-landscape-v2-2026-11-13/verify.py
python3 -m unittest tests.test_trial_landscape_v2 -v
```

`verify.py` reruns the export reader and the recompute reader on the frozen
pages. It fails if they disagree, if the certificate or the count block drifts,
or if a pinned hash changes. It does not call the network. A fresh retrieval,
which can return different studies, is:

```sh
python3 tools/fetch_trial_landscape_v2.py
```

That command refuses to overwrite an existing snapshot unless `--force` is
passed. Overwriting this dated result would discard the record. The
[result note](../results/trial-landscape-v2-2026-11-13/PROOF.md) states the
evidence label and what the offline check does not show.
