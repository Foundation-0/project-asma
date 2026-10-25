# Pilot 001: open questions, 2026-10-25

**Date:** 2026-10-25. All sources below were accessed on that date unless a
line says otherwise. **Evidence class:** public-source reading, static code
reading and bounded in-memory aggregate checks. No model was fitted. **No new
performance result was computed.** No author or third-party code was executed.
No one was contacted.

This report covers five investigations run on 2026-10-25. Each had an
independent skeptic review. Only confirmed findings, or the skeptic's corrected
wording, are used here. Refuted claims are left out.

Each section separates:

- **Published:** values printed in a paper or supplement. These are reference
  values, not results of this project.
- **Established:** checked against a pinned source or code text today.
- **Likely:** a reasoned inference that is not proven.
- **Open:** not settled; the section says what would settle it.

Registry IDs (S01, S26, …) point to [sources.json](../registries/sources.json).
No patient or sample keys, identifiers, linkage maps, scores or abundance values
appear here. All counts are aggregates.

## 1. The missing fold helper: likely origin and contract

The Figure 3D and 3C scripts source `balanced_folds.R` and call
`balanced.folds.vec(senref, 5)`. The file is absent from the author repository
(S08). This section asks where it could come from and whether the original
folds can be rebuilt.

### Established

- **A public definition exists, in a later repository by the same GitHub
  account.** `Shrabanti87/CASPEN`, `R/utils.R`, defines
  `balanced.folds.vec <- function(y, k.folds)` at lines 103–109 (S26). The same
  file defines `balanced.folds` (10–44), `cv.folds` (48–51), `resample`
  (55–61), `permute.rows` (65–69) and `permute.vector` (73–75). The header
  (lines 3–6) says it "returns an integer vector of fold assignments of length
  `length(y)`". The helper block is identical in every commit from `410c32a`
  (2026-07-14) to `3f8c8f4` (2026-07-16).
- **The wrapper draws no random numbers.** It unlists the fold list from
  `balanced.folds` and orders fold labels by sample position.
- **CASPEN reuses the Figure 3D loop idioms.** `R/training_functions.R` lines
  63–70 at `3f8c8f4` repeat `set.seed(j)`, `cv.fold <-balanced.folds.vec(outcome,nfold)`
  (same unusual spacing) and the `y.pred.avg.pool.all <- NULL` initialisers.
  Compare `Figure_3D_part3.R` lines 19–27 and 44–45 at `48357fd`.
- **pamr does not export `balanced.folds`.** Its NAMESPACE at 1.54–1.57 has no
  export or export pattern for it (S19, S27). A script that calls it must define
  it or reach into pamr's namespace.
- **Algorithm lineage** (S27, S28):
  - pamr `balanced.folds` with a `runif`-based `permute.rows`; the file is
    identical from 1.54 to 1.57.
  - randomSurvivalForest 3.6.0 (2009-12-21) and randomForestSRC 1.0.0
    (2012-10-31) to 3.9.0 copy it, add NA-label imputation and keep the
    `runif` variant.
  - SubgrpID 0.10 (2017-02-28) is functionally the same, but `permute.rows`
    permutes each row with `sample()`. CASPEN matches this variant.
  - MCRestimate (`R/MCRestimate.R` lines 103–115, since 2008-01-07) wraps pamr's
    internal `balanced.folds` and returns a length-n fold vector. c060's
    `balancedFolds` says it was taken from MCRestimate.
  - rda 1.2-1 also carries an unexported pamr-style copy. CMA uses its own
    stratification. No CRAN package searched defines `balanced.folds.vec`.
- **Input/output contract from the author scripts** (S08, commit `48357fd`):
  - `Figure_3D_part3.R` line 13 sources the helper; lines 26–27 call
    `set.seed(j)` and then the helper; line 29 tabulates `cv.fold` against
    `senref`; lines 44–45 split on `cv.fold != i` and `== i`.
  - `Figure_3C.R` lines 83, 96–99 and 114–115 do the same.
  - `Figure_3D_part2.R` lines 59–61 and 100–101 replace the helper with
    `sample(rep(1:5, c(27,27,27,27,27)), 135, replace=FALSE)`, next to the
    commented helper call. That drop-in is unstratified, with exactly 27 per
    fold.
  - So the helper takes the label vector and K and returns a fold-label vector
    of `length(senref)`, labels 1..K, aligned to sample positions.
- **Fold geometry differs from this project's declared rule.** Under the
  pamr-family block rule with 83 sensitive / 52 refractory and K=5:
  - per-fold class counts are 16–17 and 10–11;
  - fold sizes are all 27 with probability 1/10, (28,27,27,27,26) with 6/10, and
    (28,28,27,26,26) with 3/10, so training sizes are 107–109.
  - The [decision record](../protocols/pilot-001-reconstruction-decisions.md)
    rule always gives 27 per fold (folds 1–3 at 17/10, folds 4–5 at 16/11). Its
    `rep(27,5)` geometry check would reject about 90% of block-rule draws.
  - For 10/10 with K=3 the block rule gives (7,7,6) with 2/3 and (8,6,6) with
    1/3. For 10/10 with K=5 both rules give 4 per fold.
  - These probabilities were enumerated exactly on synthetic class counts. No
    study data were used.
- **Random-number use, from source text** (S21, S27):
  - pamr-family `sample(yids[[i]])` makes the same internal call as
    `sample.int(class_size)`.
  - After the 135 class-permutation draws, the pamr/randomForestSRC variant
    takes `runif(170)` (34 blocks of 5). The SubgrpID/CASPEN variant takes 170
    index draws. The project's rule takes none.
  - The NA-imputation path draws nothing when no label is missing.
  - Class order follows sorted label levels. Every `senref` built inside the
    repository codes sensitive as 1. If the workspace labels use the same
    coding, refractory (52) is permuted first, while the project's rule
    permutes class 0 (sensitive, 83) first. Then even the first 135 draws would
    not line up with the project's rule.
- **The helper's draws also reach the model fits.** The stream is reset only by
  `set.seed(j)` before the helper and by `set.seed(1000000)` before each forest
  (part 3 line 79). In outer fold 1 of every repeat, the inner `cv.glmnet` fold
  draw and the xgboost fit use the stream left by the helper. So two helper
  variants that gave identical folds would still change the fold-1 elastic-net
  and xgboost fits. The [code-audit addendum](pilot-001-code-audit-addendum.md)
  already records that `set.seed(j)` governs the fold draw and fold 1; the new
  point is that the helper variant's draw count matters too.
- **The paper names no R or package versions.** The key resources table lists
  pamr, XGBoost and RandomForest without versions. pamr is cited only for
  the subtype classifier (article XML, PMC10414761.1).

### Likely

- The 2023 helper was a pamr-family `balanced.folds` behind a vector wrapper
  taking `(y, k)`. Three shapes are plausible:
  1. a SubgrpID/CASPEN-style copy, where `permute.rows` uses `sample()`;
  2. a pamr/randomForestSRC-style copy, where `permute.rows` uses `runif`;
  3. an MCRestimate/c060-style wrapper over pamr's internal function, with the
     same draws as shape 2.
- The evidence for a local definition is that pamr does not export the function
  and that the scripts source a file. Missing `library()` calls are not
  evidence: part 3 also calls glmnet, xgboost and randomForest without them.
- The four variant × `sample.kind` combinations almost certainly give different
  folds for the same seed. This was not executed; R is not installed here.

### Open

- **Exact original folds cannot be rebuilt from public material.** Four things
  are unknown:
  1. the `senref` values in the missing workspace's column order, and their
     coding;
  2. which helper shape the 2023 file used;
  3. the R version, which sets `sample.kind` (Rounding before R 3.6.0,
     Rejection after);
  4. the RNG kind (Mersenne-Twister is presumed).
- **What would close it:** the workspace that holds `senref1` (or its order and
  coding), the 2023 `balanced_folds.R` or the authors' statement of which shape
  it was, and the R version and `RNGkind()` output. Even then, no per-repeat or
  per-fold output is public. Checking a candidate would need a full-pipeline
  match to the published averaged scores, which also depends on package
  versions and the fold-1 stream.
- The part 2 feature-selection folds are a special case. They do not depend on
  `senref`, so their labels are computable from the seed and `sample.kind`
  alone. Mapping them to patients still needs the workspace column order.
- `Figure_3C.R` overwrites its fold-relevant `senref` from the workspace at line
  72, so its coding is not verified.
- The link between the 2023 scripts and CASPEN rests on the GitHub handle and
  first-author name. CASPEN post-dates the paper by about three years. It is a
  likely stand-in, not proof of the 2023 text.
- **Licence caution.** CASPEN states "MIT + file LICENSE". Its helper is
  functionally identical to GPL-licensed package code (pamr, randomForestSRC,
  SubgrpID) and carries no attribution. Do not assume an MIT grant for that
  text. Any project implementation should stay independent, as the decision
  record already requires.
- **Out-of-scope lead, not opened.** CASPEN ships example data documented as
  "Derived from internal study datasets", with README examples on high-grade
  serous ovarian cancer and platinum resistance. Only file names and sizes in a
  git tree listing were seen. Provenance and rights are unknown. Under
  [AGENTS.md](../AGENTS.md), any use needs verified rights and the owner's
  authorization. A future clone should use `--filter=blob:none` or a
  path-limited fetch so the small outcome file is not pulled.
- A closer **sensitivity analysis** is possible: the block rule in independent
  project code, both `permute.rows` variants and both `sample.kind` values. It
  would be labelled "not the original folds" and needs an owner decision and a
  dated amendment. It conflicts with the frozen 27-per-fold rule.

Sources: S08, S19, S21, S26, S27, S28; article XML PMC10414761.1 (S01).
Searches: all 22 WangLab-MSSM repositories and all 12 Shrabanti87 repositories
were cloned and grepped; only call sites were found outside CASPEN. Web search
did not index CASPEN.

## 2. The 2024 correction

### Published

The correction (Cell 2024;187(4):1016; doi
[10.1016/j.cell.2024.01.016](https://doi.org/10.1016/j.cell.2024.01.016);
PMID 38364782; PMC10935576; NIHMS1968879; S11) reads in full:

> In the version of this article that was originally published on August 3,
> 2023, the supplemental figure legends were incorrect in many places, with
> some of the supplemental figure panels in the article lacking legends
> entirely. The proper supplemental figure legends now appear with the article
> online. The authors regret these errors and apologize for any inconvenience
> or confusion caused.

Source: the body paragraph of
[PMC10935576.1.xml](https://pmc-oa-opendata.s3.amazonaws.com/PMC10935576.1/PMC10935576.1.xml),
13,637 bytes, SHA-256
`a59fe5c54438570ba767e5e1548cfb13385fca03e5b73d1f13f559bd4248bd71` (equal to the
existing pin). The TXT and PDF companions carry the same text.

### Established

- **Scope.** The notice names only the supplemental figure legends. It lists no
  panels and attaches no files. Its XML has `article-type="correction"`, a
  `corrected-article` link to PMC10414761 and `pmc-prop-has-supplement = no`.
  NLM dates: submitted 2024-03-03, released 2024-03-13, last changed 2024-06-15.
- **Figure 3D is outside the stated scope.** The notice says nothing about
  Figure 3D, the main text, the tables (MMC1–7) or the data. The Figure 3
  caption is a main-figure legend. A notice is not always a full change log,
  so a silent publisher change elsewhere cannot be ruled out from NLM files.
- **NLM holds no later version, as of 2026-10-25.** The bucket's documented
  version query returns only `PMC10414761.1/` and `PMC10935576.1/`. A full
  listing of the article prefix returns 20 keys, all under `.1`. The figure
  supplement is byte-identical to the pin (13,076,963 bytes, SHA-256
  `7726253a…6c26`), and its MD5 `3a749718f8525e7d814e69536fe69f03` equals the MD5
  in NLM's own version metadata. The bucket README (§6) says objects inside an
  existing version can be replaced in place, so this is a dated observation,
  not a permanent fact.
- **Legend–image contradictions in the pinned supplement.** Panel letters seen
  in the figure images, letters in the pinned legends, and letters cited by the
  article body:

  | Figure | Image | Pinned legend | Article cites | Consistent? |
  | --- | --- | --- | --- | --- |
  | S1 | A–L | A–L | A–L | Letters agree |
  | S2 | A–L | A–J | A–L | No; legend items shifted (article S2F/G/H–I/J/K/L = legend E/F/G/H/J/I) |
  | S3 | A–K | A–H | A–J | No |
  | S4 | A–H | A–F | A–H | No |
  | S5 | A–E | A–F | A–E | No; legend (C) has no matching panel |
  | S6 | A–G | A–D | A–G | No |
  | S7 | A–G | A–G | A–G | Letters agree |

  Five of seven figures contradict their images. This is a lower bound: S1 and
  S7 were checked only by letter count.
- **Figure S3 panel assignments can be read from the figure image.** The
  printed titles and n settle them without the corrected legend:

  | Panel | Printed content | Pinned legend item |
  | --- | --- | --- |
  | A | nTAI/wGII/nLOH by Chr17-LOH | (A), by elimination |
  | B | Amplification/deletion/LOH frequency by Chr17-LOH | (B), by elimination |
  | C | Peptides detected and average peptide correlation, 64 predictors | none |
  | D | RNA–protein correlation vs mean protein abundance | none |
  | E | FFPE Discovery, phosphoproteomics: AUC 0.78, n=135 | (D) |
  | F | FFPE Validation, phosphoproteomics: AUC 0.76, n=20 | (E) |
  | G | FFPE Discovery, global proteomics (MRM): AUC 0.76, n=102 | none |
  | H | FFPE Validation, BRCA+clinical 0.61 and +Chr17-LOH 0.66, n=20 | (C) |
  | I | FFPE Discovery, three models 0.69/0.73/0.87, n=135 | (F) |
  | J | FFPE Validation, three models 0.61/0.66/0.98, n=20 | (G) |
  | K | FFPE Discovery, per-cluster AUC 0.66/0.85/0.80/0.84/0.91, n=28/30/30/23/24 | (H) |

  AUCs and n are published values printed in the figure. No S3 panel shows a
  frozen cohort. The article body cites S3C–S3J consistently with the image
  letters (P31, P32, P35–P37, P184–P185) and never cites S3K. The MRM cluster
  sizes in the Figure 5F legend (P258) sum to 102, matching panel G.
- **Panel K's n match public files.** The 135 keys of MMC4 `FFPE_pred_scores`
  join exactly (135/135) to MMC3 `FFPE_global_clustering`. Matched cluster sizes
  are 28/30/30/23/24, as printed. The full 158-row sizes, 33/31/38/26/30, are the
  paper's pathway-based clusters. The protein-abundance clustering (S4F/S5E,
  sizes 15/40/51/28/24) cannot give these n. Only counts were computed; score
  values were not read.

### Likely

- **The pinned NLM supplement is the pre-correction version.** The NIHMS
  manuscript was submitted 2023-08-05. The PDF's modification date is
  2023-08-09, and its pages are Cell's typeset supplemental figures, re-saved
  with a third-party PDF tool. The correction followed six months later and NLM
  holds no later version. The legend–image contradictions show the defect the
  notice describes.
- Panel K uses the 64-protein model and the same score version as MMC4. This
  rests on the mislettered legend item (H) and on the matching n.

### Open

- **The corrected legends are not pinned.** The notice says they "now appear
  with the article online", but every publisher and index host was refused on
  2026-10-25 (see the blocked-host list below). Web-search result pages named
  candidate locations: the cell.com and ScienceDirect article pages for PII
  S0092-8674(23)00737-7 and an eScholarship record (item 72s3z4rr). The PII
  mapping and the eScholarship version were not verifiable here. A
  search-engine summary of a corrected S3 (C) item matched the panel C image
  but could not be found again; it is unverified.
- The owner, not an automated session, could retrieve and pin the publisher's
  corrected S3 legend from a network that can reach those hosts.
- **Proposed only:** a pre-declared check of the released discovery scores
  against the five printed S3K per-cluster AUCs. It could help tell whether the
  released score sheet is the version behind the figures. It needs a
  protocol with a fixed tolerance and the owner's explicit instruction. It was
  not run.

Sources: S01, S11, S14; NLM bucket README.

## 3. Validation-panel coverage and the author archive

### Established

- **Supplement-level coverage of the 64-panel.** MMC1 holds per-cohort protein
  association tables. All 64 panel symbols occur exactly once in each:
  discovery (8,800 features), frozen (8,272) and FFPE validation (8,237). All 64
  also lie in the 7,359-symbol three-way intersection. Exact string equality
  was used; only counts were kept. Another agent is adding the repeatable audit
  [tools/audit_validation_panel_coverage.py](https://github.com/Foundation-0/project-asma/blob/main/tools/audit_validation_panel_coverage.py)
  and its record
  [registries/pilot-001-validation-panel-coverage.json](https://github.com/Foundation-0/project-asma/blob/main/registries/pilot-001-validation-panel-coverage.json)
  on a sibling branch. Those links resolve once that branch is merged; the
  record there is authoritative for set fingerprints.
- **64/64 is expected by construction.** The article says: "In the end, we
  filtered away 8 protein markers not detected in the other proteomics data
  sets from human tumors such as the Frozen and FFPE validation datasets" (last
  sentence of P177) and "The final marker panel then consisted of 64 proteins"
  (P178). The check confirms this at feature-list level; it is not an
  independent discovery.
- **These are association-test feature lists.** They are not the archive
  members' row sets or the prediction workspaces' rows.
- **The archive host was refused today.** One HTTP Range request for the
  central directory of `processed_data.zip` (S17) at 2026-10-25T14:56:11Z got
  CONNECT 403 from the egress proxy; 0 bytes were received. The proxy log shows
  another session refused at 15:25:30Z. It was not retried or routed around.
  ProTrack (`ptrc.cptac-data-view.org`) was also refused.
- **The minimal metadata read is 5,716 bytes.** From the pinned registry values
  the archive has no ZIP comment and no ZIP64 records. So one range,
  bytes 70,133,249–70,138,964, covers the whole central directory and end record.
- **The frozen replicate sheets hold four triplicate blocks.** This matches P129
  and the clinical sheet (72 rows over 64 keys). The MMC1 table-of-contents
  wording "5 samples" for the frozen sheets is a copy error.
- **Open [PR #18](https://github.com/Foundation-0/project-asma/pull/18) records
  a member inventory** (branch `claude/magical-wright-frdz8u`, commit `e28ce4a`,
  unmerged on 2026-10-25). Its `docs/pilot-001-reconstruction-decisions.md`
  lines 327–358 describe a metadata-only listing, made earlier on 2026-10-25,
  that matched the pinned central-directory SHA-256. It lists 42 entries: 1
  directory, 20 files and 21 macOS resource forks. The files are a README, a
  `.DS_Store` and 18 tables: global protein and phosphoprotein for each cohort,
  each as imputed and as batch-corrected before imputation, plus discovery and
  FFPE-validation CNV, LOH and RNA-seq. **This session could not re-verify the
  listing**, because the host was refused.

### Likely

- If the PR #18 listing holds, the archive contains two preprocessing stages
  (batch-corrected before imputation, and DreamAI-imputed). It holds no raw or
  normalised matrix, no replicate-averaged matrix, no prediction RData and no
  LC-MRM member. A discovery-aligned frozen file is absent unless the frozen
  imputed member is itself aligned. The key-resources label "Processed
  LC-MRM-MS data" does not describe those contents.
- The MMC1 lists are probably each cohort's batch-corrected, filtered feature
  universe. Expected member rows: frozen 8,272 (if not aligned to discovery) and
  FFPE validation 8,237; phospho 2,648 / 17,446 / 3,076. For discovery the match
  is count-level only (8,800 = 8,800). The archive and MMC1 use different
  annotation schemas, so set equality is not shown.

### Open

- **What a member-level check would add:**
  - the actual row sets of `Frozen_globalprotein_imputed.tsv` and
    `FFPE_validation_globalprotein_imputed.tsv`, not only feature lists;
  - whether the frozen member is aligned to discovery. `FZ_data_alignment.r`
    line 17 keeps only proteins shared with discovery, so an aligned file would
    have at most 7,879 rows, not 8,272;
  - set fingerprints of both symbols and UniProt accessions, because the two
    symbol columns come from different annotation schemas;
  - a calibration: the same fingerprint on the already-audited discovery
    member.
- **Preconditions.** [Issue #9](https://github.com/Foundation-0/project-asma/issues/9)
  says archive members beyond the discovery one are outside the current
  bounded-inspection authorization, and those members are not individually
  pinned here. The owner should say whether the 2026-10-25 rule in
  [AGENTS.md](../AGENTS.md) covers them. The central directory must be re-read
  and matched to its pin first. The existing archive and feature audits
  hard-code the discovery member's contract and nine-field layout and would
  need per-member parameters. This report changes no tool.
- The paper's own counts in P177–P178 imply 7 removed markers, not 8.
- The two FFPE-validation members differ by 20,487 bytes although at most 60
  cells can be missing. They differ in more than imputation.

Sources: S14, S17; article XML PMC10414761.1; MMC1 and MMC4 (S14).

## 4. "Non-overlapping" frozen tumours and patient independence

### Published definitions

Quotes from article XML PMC10414761.1 (paragraph IDs):

- P145 (alignment methods): "Between frozen and FFPE cohorts, there are 29
  overlapping samples. In addition, there are 14 other FFPE-Frozen pairs of
  samples coming from different tumors (primary and metastasis) of the same
  patients. We thus utilized all 43 common samples between these two
  experiments to align the two proteomic data sets."
- P14 (results): "…64 HGSOC tumors (44 sensitive, 20 refractory) (Figure 1A),
  of which 29 overlapped with the FFPE discovery cohort to assess replicability
  between biospecimen types (i.e., paired frozen and FFPE biospecimens from the
  same patient)."
- P68 (cohorts): "And 29 of these 64 tumors were from overlapping patients from
  the FFPE Discovery cohort."
- P183 (prediction methods): "…an independent validation cohort of Frozen
  Cohort tumors (±29 overlapping samples with the FFPE discovery cohort). Note
  that from the Frozen cohort too we removed the samples with neo-adjuvant
  therapy and got 34 in the independent set and 27 in the overlapping set."
- P33 (results): "…using two independent patient cohorts (frozen and FFPE
  validation)… For the frozen validation cohort, we separately considered the
  subsets of tumors that are independent of vs. overlapping with the FFPE
  discovery cohort." P3 (abstract) and P10 also say "validated in two
  independent patient cohorts".
- P195: "In the Frozen-independent Validation cohort (n=35)…". P198: ssGSEA
  scores aligned "using only the overlapping samples (n = 29)". P264 (Figure 6D
  legend) gives counts for the "frozen validation (non-overlapping) cohort".
- Published metrics (P33): frozen-independent AUC 0.79 (95% CI 0.63–0.96),
  sensitivity 0.25 at 98% specificity; frozen-overlapping AUC 0.81, sensitivity
  0.43.

### Established

- **"Overlapping" means the 29 designed FFPE–frozen pairs from the same
  patient. "Independent" or "non-overlapping" means the other 35 frozen
  tumours.** It is not patient independence: 14 of the 35 come from discovery
  patients (P145). Sentences that call the frozen cohort an "independent
  patient cohort" (P3, P10, P33) conflict with P145.
- **The authors' own pair list.** MMC1 `FFPEFrozen_overlap_corr_protein` holds 29
  pairs. Its table of contents calls them "the overlapping samples in FFPE
  discovery and Frozen protein data". Each pair joins exactly to one patient,
  with the same tumour-location group and primary/metastatic type. The published
  overlap score sheet (27) is that list minus 2 neoadjuvant exclusions. The
  nonoverlap score sheet (34) shares no patient with it.
- **The 43 shared patients split exactly as P145 says:** 43 = 29 pairs + 14
  others. Of the 14, 13 are in the 34-row nonoverlap sheet and 1 was excluded
  as neoadjuvant. Response labels agree across cohorts for all 43.
- **The six keys on main are explained.** They are the part of those 13 whose
  discovery tumour passed discovery eligibility. In all six the discovery
  specimen is a metastatic omental tumour and the frozen one a primary ovarian
  tumour. They overlap at patient level, not tumour level. Their labels
  (identical in both cohorts) were in the 135-sample set used to train the model
  that scored the frozen cohort (P183; part 3 lines 136–175). The other 7 had
  discovery specimens annotated "Mix", which discovery excluded.
- **The published frozen-independent metrics used the 34 tumours, including the
  13 same-patient ones.** P183's "34 in the independent set" is the main
  evidence. The sensitivity is consistent: 0.25 = 3/12 on the sheet's 12
  refractory tumours, and no sensitivity of 0.25 is possible with 13. This
  arithmetic is corroboration only.
- **Denominators differ by analysis: 34 for prediction, 35 for clustering.**
  MMC6 `FZ_Validation_PAM` (129,182 bytes, SHA-256
  `41a3b1caf4cdbbed675b3bdad29f93f4478dbf9eba922068556be689cece8e78`) joins to all
  64 frozen patients. Restricted to the 35 non-pair tumours, its cluster-by-
  response counts reproduce the Figure 6D legend (P264) exactly; the 34-row
  prediction set does not. So the Figure 6D and S6B "non-overlapping" set
  includes the neoadjuvant-treated patient left out of prediction.
- **Candidate patient-independent subsets** (class counts sensitive/refractory):
  - strictly independent, with no discovery record of any kind: **21 (13/8)**,
    all inside the nonoverlap sheet;
  - not in eligible discovery: **28 (17/11)**. The 7 beyond the 21 had "Mix"
    discovery specimens and took part in discovery-wide preprocessing and the
    alignment.
- **No site independence.** All 64 frozen patients and all 43 shared patients
  come from one institution (Fred Hutchinson; P68). Discovery has 62 patients
  from that institution, with 50 from Mayo and 46 from UAB. The frozen test is
  at best a same-institution, cross-preservation test.
- **Pooled reference.** P129: the frozen cohort's common reference, an equal
  mix of every frozen tumour, "was also included in each TMT 11-plex group of
  the FFPE Discovery experiment". This includes the 21. P142 removes "the
  reference bridge samples from every TMT" before normalisation, so only their
  role in upstream TMT quantification is unverified.

### Likely

- **The alignment pairs specimens by patient.** `FZ_data_alignment.r` (lines
  7–9 at `48357fd`) keeps columns whose 8th–12th label characters match across
  cohorts. Applied to the published clinical labels, that window gives exactly
  the 43 same-patient keys. So the frozen values of the 13 scored "independent"
  same-patient tumours, and of the 27 overlap tumours, entered the alignment
  transform applied to the test data. The 21 did not. The real input headers
  are unpublished, so this is consistent with the rule, not proof.
- **Same lesion is not shown for the 29, and "different tumour" is clear for
  only 6 of the 14.** At least 2 of the 29 pairs are annotated as opposite
  ovaries. For 8 of the 14, the discovery specimen is "Mix". The annotations
  support "same patient, same tumour category and location group" versus
  "different category".

### Open

- Lesion identity of the 29 pairs.
- PDC sample-level descriptors that would confirm the 29 + 14 split. PDC hosts
  were refused today.
- What `data_nov.RData` contains. MMC1 uses "NOV" for "non-overlapping (with
  FFPE)", but part 3 line 140 comments "For both non-overlapping and overlapping
  samples in Frozen". `FZ.sampleOverlap`, `data_nov` and `senref_nov` are never
  defined in the inspected scripts.
- Whether the released score sheets are the exact inputs to the printed frozen
  metrics. The released discovery sheet already misses the printed 0.83.
- **No subset metric was computed.** An AUROC on the 21 (8 refractory) or the
  28 (11 refractory) would be a new performance result. It would need a
  pre-specified protocol, as in the
  [score-verification protocol](../protocols/pilot-001-score-verification.md),
  and the owner's explicit decision. The 21 are outside the alignment fit, but
  they are not untouched: panel markers were filtered on detection in the
  validation data (P177), and their material is in the pooled reference run in
  every discovery plex.

Data note: one investigation's schema-listing call printed the header cells of
four replicate-correlation sheets, which are sample data labels, into transient
session output. They were not written to any file and are not reproduced here.

Sources: S01, S08, S10, S14; MMC1, MMC4 and MMC6 (S14).

## 5. Readiness of the 2025 fallback (Kilim et al.)

The candidate is Table 1, primary-tissue proteomics, "HGSOC Train / TCGA
Validation": **0.61 ± 0.05** (published), with "Patients* 158:127" (S15). It is
not adopted. Nothing was run.

**Verdict: NOT READY.** Top blockers, most serious first:

1. **Endpoint and case-spectrum mismatch.** Training labels are Chowdhury's
   primary refractory versus ≥2-year progression-free sensitive. Test labels are
   the TCGA `PlatinumStatus` field from Zhang et al. 2016 (S31). Its exact
   definition was not verified from a primary source.
2. **The published 0.61 ± 0.05 is not produced by the checked-in code or
   results** (S29).
3. **Not independent of Chowdhury.** The PTRC training cohort is Chowdhury's
   FFPE discovery cohort, on which the 64-panel was selected.
4. **Rights unresolved.** Elsevier supplement terms for Kilim's exact TCGA
   table, no licence for the Dropbox archive, no code licence. The TCGA MS data
   were also deposited at the CPTAC Data Coordinating Center, under terms not
   checked.
5. **Whole-cohort preprocessing, an unseeded random forest and no environment
   lock.**

### Established

- **The PTRC cohort is Chowdhury's FFPE discovery cohort.** Kilim Par10 and
  Par55–57 cite Chowdhury; the code README names
  `FFPE_discovery_globalprotein_imputed.tsv`; Chowdhury P68 describes "158 HGOC
  tissue biopsies … from three institutes". It is a superset of the 135 Figure
  3D patients. Chowdhury P177 says the markers were selected on "83 sensitive
  and 52 refractory" FFPE tumours. So TCGA→PTRC (published 0.755) and the PTRC
  5-fold CV (published 0.696) carry feature-selection leakage. Only PTRC→TCGA is
  clean of panel selection. Chowdhury's frozen and FFPE-validation cohorts are
  not used.
- **Exact target.** The value appears identically in medRxiv preprint v1 Table
  1 and in Supplementary Table 1 (S30). It has two decimals while neighbouring
  cells have three. The table note describes a five-fold-model, patient-level
  ensemble with a 1,000-sample bootstrap.
- **The repository gives a different number by a different procedure** (S29,
  commit `962aaa8`). `tables/main_tables/primary.tex` reports 0.585 ± 0.033,
  which equals the mean and population SD of five per-fold, slide-level test
  AUCs in `classical_results_stratified.json`. Earlier checked-in runs average
  0.6027 and 0.5988. There is no bootstrap or resampling code. The deep-model
  "ensemble" averages three backbones within a fold, not five fold models.
- **The published t-tests are paired tests over five per-fold AUCs.** All six
  t/p pairs reproduce as two-sided Student t with 4 degrees of freedom.
- **The per-fold test AUCs imply a 155-row TCGA test set** with one class of
  131. That fits neither the 158 slides in the split files nor the 159 WSIs
  (118/41) in Supplementary Table 7. The cause is open.
- **Splits.** 174 primary train+validation slides, disjoint from 174 metastatic
  ones; one 158-slide TCGA test set shared by all folds. `GroupKFold` by
  `case_id` without stratification, although Par77 says "stratified".
- **Different label definitions.** PTRC labels come from Chowdhury's
  refractory/sensitive response; TCGA labels from `PlatinumStatus`. For the same
  CPTAC-2016/TCGA tumours, Chowdhury used survival proxies instead (P167).
- **Features.** The code uses 60 of the 64 panel symbols; it omits CARMIL1,
  CCDC167, CDKN1A and SENP1. Group sizes and the 1,539-protein set hold for the
  repository JSON only.
- **Preprocessing is fitted on whole cohorts and differs from the article.**
  TCGA is scaled and KNN-imputed on all tumours before the clinical merge. PTRC
  is scaled on all samples, with no log transform or imputation. Par58 says both
  were imputed, log-normalised and scaled.
- **Code state.** The only ref is `master` at `962aaa8` (2024-05-27; 20
  commits), before submission (2024-06-03) and acceptance (2025-01-11). No tags, no root licence, no
  environment file, private absolute paths. Committed joblib pickles of
  processed patient-level tables were never loaded. Of the classical models only
  the random forest is unseeded.
- **Data links.** Article licence CC BY-NC-ND 4.0. The article's Figshare link
  ends `file=4904521`, while the registry records file 49045213 (S16).

### Likely

- The published methods text (logistic regression + RF + XGBoost) probably does
  not describe the model behind 0.61. The preprint says ElasticNet + RF +
  XGBoost; the code is a `VotingRegressor` of RF, ElasticNet and XGBoost
  regressors at defaults.
- Several published cells nearly equal checked-in values, so Table 1 looks like
  a rerun of the same pipeline and splits with changed TCGA-test aggregation.
- `PlatinumStatus` is probably a 6-month platinum-free-interval construct. Its
  "Resistant" class would include refractory cases and its "Sensitive" class
  intermediate responders.
- The 158 PTRC patients probably include the 13 neoadjuvant and 10 "Mix"
  patients that Chowdhury excluded; the code applies no such filter.
- Histotype, stage and assay are not controlled in the TCGA arm (174 tumours,
  169 HGSC; iTRAQ against a pooled reference across two centres). Rows are
  joined by substring; AUCs are computed per slide while Table 1 says per
  patient.
- No correction is linked at NLM as of the latest object (2026-06-27).
  Publisher-side notices were not reachable.

### Open

- The operational definition of `PlatinumStatus` (Zhang mmc2, on ScienceDirect).
- Same-patient overlap between TCGA-OV and the PTRC Mayo sub-cohort. TCGA 2011
  lists Mayo Clinic tissue-source staff (S32). There is no evidence of overlap,
  but published statements cannot exclude it.
- Whether the paper-cited Figshare grouping file matches Par72/Par79.
- Which PTRC matrix column the setup script drops; how dual-centre TCGA tumours
  are handled; whether a later medRxiv version exists.

Sources: S15, S16, S17, S29, S30, S31, S32; Chowdhury article XML (S01).

## What was read and why

All accesses were on 2026-10-25 by the five investigations, their skeptic
reviews and the session that drafted this report. Reads served only the
questions above. Python that read downloads ran with `-I`. Downloads went into
separate scratch directories outside the checkout. Only aggregates were kept.
The drafting session re-read the retained public article XML and correction
text to check every quote here.

**NLM public distribution** (`pmc-oa-opendata.s3.amazonaws.com`):

| File | Bytes | SHA-256 (prefix where the full value is registered elsewhere) | Handling |
| --- | ---: | --- | --- |
| `README.txt` | 14,524 | `257a001b400485176702ed49ca7607d73cd83c581bffb6dd3c9be127a2e42634` | Disk; public, kept in scratch |
| `PMC10414761.1.xml` (article) | 449,678 | `1d88848c…187b` | Disk; most copies deleted, one public copy kept in scratch for quote checks |
| `PMC10414761.1.json` | 2,395 | `804de66c4ca5e78af3b73530445b192132c53fff416a5ed6ee87d25bf6703bec` | Disk; public, kept in scratch |
| `PMC10935576.1.xml` / `.txt` / `.pdf` / `.json` (correction) | 13,637 / 2,264 / 34,586 / 719 | `a59fe5c5…` / `ac940709577cd10b9456120297d980142a9c7371d129197c2712a579e0b675d1` / `9ff4dbf592a8dd6547ca8f57395047231b7790d8af0d906eb52a2088fa478338` / `06a253f2e3e0aef17f3019c57b4e14e22cef7ada42c01431761c526779cb94f1` | Disk; public, kept in scratch |
| `NIHMS1918576-supplement-1.pdf` | 13,076,963 | `7726253a…6c26` | Disk; text extracted, 7 pages rendered and viewed; PDF and renders deleted |
| `NIHMS1918576-supplement-MMC1.xlsx` | 41,194,360 | `6e46fa0cb3023173a3643e95ce0360c44cfabb0ed737e9a05f70473dad552340` | Memory only, via the repository's hash-checking loader |
| `…-MMC3.xlsx` | 3,304,491 | `18e5bebe052e1a28abecb3927d93f1f30b83ab91c11f5c157e10ca16a6021fe1` | Disk briefly for one cluster-count join; deleted |
| `…-MMC4.xlsx` | 591,065 | `f318ed9d…` | Memory in most runs; disk briefly in some; deleted |
| `…-MMC6.xlsx` | 129,182 | `41a3b1ca…` | Memory only |
| `…-MMC2`, `MMC5`, `MMC7.xlsx` | — | prefixes `cbaf4d1a`, `78c236b2`, `ae5056cc` | Memory only; table of contents read |
| `PMC11762732.1.xml` / `.json` (Kilim) | 262,653 / 1,296 | `e26c5f7f…` / `f5784c3ab09da239b9b3664d71fbad45683bfcbf43b6031a2364077598f263af` | Disk; deleted |
| `41698_2025_808_MOESM1_ESM.pdf` (Kilim supplement) | 31,754,080 | `b76e7ac6739bf6ebfef2e46b334f8adceba2d9e5688a5860eaec6fe78dcb8d20` | Disk; deleted |
| `PMC11177907.1.xml` (Kilim preprint) | 100,640 | `ee842678f04e8c1ca81c86d99ac12863fbf4b2a6e757706ab8aa78fb649d8c82` | Disk; deleted |
| `PMC4967013.1.xml` (Zhang 2016) | 130,050 | `a2a8d112…` | Disk; deleted |
| `PMC3163504.1.xml` (TCGA 2011) | 109,160 | `490eba6e…` | Disk; deleted |

Also from the same host: version and prefix listings (`list-type=2`) for both
Chowdhury records and both Kilim records; `?versions` returned 403. The drafting
session fetched the five small version-metadata JSON files (PMC10935576.1,
PMC11177907.1, PMC11762732.1, PMC4967013.1, PMC3163504.1; 610–2,848 bytes) to
confirm titles and DOIs for the registry, then deleted them.

**Code, read as text and never executed:**

- `WangLab-MSSM/CPTAC_Ovarian_Chemo_Response` at `48357fd` and the author fork
  (no-checkout clones); all 22 WangLab-MSSM repositories and 12 Shrabanti87
  repositories (bare clones, grepped for the helper). About 690 MB of clones in
  total, all deleted.
- `Shrabanti87/CASPEN`, all 9 commits. Its example-data blobs sat unopened inside
  the bare clone's pack until deletion. The drafting session re-fetched
  `DESCRIPTION` at `3f8c8f4` (1,728 bytes) and `R/utils.R` at `410c32a` (43,994
  bytes, hash as in S26) to confirm citations, then deleted them.
- CRAN mirrors under `github.com/cran`: pamr (1.12, 1.54–1.57), superpc,
  randomForestSRC, randomSurvivalForest, SubgrpID, c060, rda and about 20 other
  packages searched for `balanced.folds.vec`. Bioconductor mirrors
  `github.com/bioc/MCRestimate` and `github.com/bioc/CMA`. The drafting session
  re-fetched pamr 1.57 `R/balanced.folds.R`, SubgrpID 0.10
  `R/cross_validation_functions.R` and MCRestimate `R/MCRestimate.R`; all hashes
  matched S27 and S28; files deleted.
- `wch/r-source`: `src/library/base/R/sample.R` (1,470 bytes, `c49fc7e2…`),
  `src/main/random.c` (14,065 bytes, `5d4fd9f7…`) and `src/main/RNG.c` (26,427
  bytes, `043e06ca…`) at R-4-2-3; `src/main/RNG.c` at R-3-5-3 (23,657 bytes,
  `601ef3c4…`); `doc/NEWS.Rd` at R-3-6-0 (367,564 bytes, `455173a9…`).
- pROC 1.19.1 `R/ci.se.R`, for the bootstrap-median point.
- `csabaiBio/HGSOC_platinum_response` at `962aaa8` (no-checkout clone, about
  161 MB pack). Code, result JSON, LaTeX tables and `README.md` (4,664 bytes,
  `c88cce8aca64c1a86d35c7a948c37d88a9140fe77d0de44a814790e5a8cc47d5`) were read
  as text. The 60 split CSVs were read in memory for counts and set relations
  only. The committed pickles were never loaded. The pack was deleted.
- This repository: issue #9, the open pull-request list and PR #18's state
  through the GitHub REST API, and the PR #18 branch read locally. No GitHub API call touched any
  other repository; GitHub code search was not used.

**Network attempts that received nothing:**

- `www.dropbox.com`: one 5,716-byte Range request for archive metadata, refused.
- `ptrc.cptac-data-view.org`: refused (HTTPS) and unresolved (HTTP).

**Hosts refused by the egress proxy today** (CONNECT 403, connection rejected,
or DNS failure through WebFetch; none was retried or routed around):

- Literature and corrections: doi.org, api.crossref.org, data.crossref.org,
  www.cell.com, www.sciencedirect.com, ars.els-cdn.com,
  pdf.sciencedirectassets.com, linkinghub.elsevier.com, api.elsevier.com,
  europepmc.org, www.ebi.ac.uk, www.ncbi.nlm.nih.gov, pmc.ncbi.nlm.nih.gov,
  pubmed.ncbi.nlm.nih.gov, eutils.ncbi.nlm.nih.gov, ftp.ncbi.nlm.nih.gov,
  escholarship.org, www.researchgate.net, core.ac.uk, api.core.ac.uk,
  api.unpaywall.org, api.openalex.org, api.semanticscholar.org,
  www.semanticscholar.org, www.nature.com, link.springer.com,
  www.springernature.com, www.medrxiv.org, api.medrxiv.org, www.biorxiv.org,
  institutional repositories (scholars.mssm.edu, experts.umn.edu,
  mayoclinic.elsevierpure.com, digitalcommons.library.tmc.edu).
- Archives: web.archive.org, archive.org, scholar.archive.org,
  archive.softwareheritage.org.
- Data hosts: www.dropbox.com, ptrc.cptac-data-view.org, pdc.cancer.gov,
  pdc-docs.cancer.gov, proteomics.cancer.gov, api.gdc.cancer.gov,
  api.figshare.com, figshare.com, ndownloader.figshare.com, zenodo.org,
  api.datacite.org, www.cancerimagingarchive.net,
  services.cancerimagingarchive.net.
- Code indexes and package sites: grep.app, searchcode.com, sourcegraph.com,
  cran.r-project.org, cloud.r-project.org, cran.rstudio.com, CRAN mirrors,
  r-universe.dev, rdrr.io, rdocumentation.org, search.r-project.org,
  bioconductor.org, git.bioconductor.org, code.bioconductor.org,
  github.com HTML pages through curl, codeload.github.com.
- Nomenclature: www.genenames.org, rest.genenames.org, www.uniprot.org,
  rest.uniprot.org. Search: www.google.com.
- GitHub REST API for other organisations: 403 (session bound to its own
  repositories).

**Retained after the session:** small analysis scripts with no data, aggregate
result files and public article/correction files, all in the session scratch
directory outside the checkout. No row-level data, identifiers or linkage keys
were kept.

## What this changes

Mapping to the open items in
[What remains before numerical reproduction](pilot-001-input-resolution.md#what-remains-before-numerical-reproduction)
and the [roadmap](roadmap.md). The same change narrows those bullets and adds a
dated roadmap paragraph; item names below give the wording before that edit.

| Finding | Existing open item | Effect |
| --- | --- | --- |
| §1 fold helper: likely origin (CASPEN, pamr family), contract, geometry, RNG use | Input resolution: "Recover `balanced_folds.R`…"; roadmap Gate 2 | **Narrowed, still open.** A likely algorithm family and the call contract are known. The exact original folds need four unknowns (workspace label order and coding, helper shape, R version, RNG kind). The declared new-fold rule stays; any source-family sensitivity analysis needs an owner decision. |
| §1 helper draws reach outer-fold-1 fits | Roadmap Gate 2; addendum "Random streams" | **Adds a condition:** a full-pipeline check against published scores also depends on the helper variant's draw count. |
| §2 correction scope and NLM state | Input resolution: "Confirm which available supplements incorporate the corrected legends" (now "Pin the publisher's corrected supplemental legends"); roadmap "corrected legend provenance" | **Narrowed, still open.** The NLM copy is the pre-correction supplement, and NLM held no later version on 2026-10-25. Publisher corrected legends remain unpinned. S3 panel assignments can be read from the image. Figure 3D is outside the stated scope. |
| §2 S3K per-cluster targets | Roadmap "Score export … remain unresolved" | **Proposal only.** Five more published targets for the released scores; a check needs a protocol and the owner's instruction. |
| §3 supplement-level panel coverage | Roadmap paragraph on feature availability; issue #9 | **Partly answered** at feature-list level (64/64 in each cohort), expected by construction. Member-level coverage stays open and needs an owner decision on scope. |
| §3 archive inventory | Input resolution: "Obtain the actual prediction-workspace inputs…" | **Unchanged.** PR #18's unverified listing suggests the archive holds no prediction workspace. |
| §4 overlap definition and the six keys | Input resolution: "Resolve why six published `nonoverlap` patient keys occur…"; protocol step 1; roadmap Gate 1 | **Cause explained:** the paper defines overlap by tumour, not patient. Still open: lesion identity, PDC confirmation, which samples entered preprocessing, and the missing location annotation. The input-resolution "Main finding" and protocol step 1 wording predate this explanation and are not edited here. |
| §4 patient-independent subset (21; 13/8) | Roadmap Gate 3; protocol step 4 | **Candidate set identified, not evaluated.** No subset metric was computed. It needs a pre-specified protocol and the owner's decision. Site independence is absent. |
| §5 fallback readiness | Roadmap "The 2025 fallback remains unadopted"; independent-progress readiness paragraph | **Assessed: NOT READY.** Its PTRC cohort is Chowdhury's FFPE discovery cohort, so it cannot serve as independent validation of Figure 3D. |

What these checks cannot establish: the content of the missing 2023 helper and
workspaces, the publisher's corrected legends, patient independence beyond the
published annotations, or any model performance.
