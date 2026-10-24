# Pilot 001 code-audit addendum

**Status:** completed static inspection (2026-10-23), reconciled with the earlier
pilot records on 2026-10-24. It informs proposed work only. No author or
third-party code was executed, no data were accessed, and nothing was reproduced.
Research only; not clinical advice.

## Scope and relation to earlier records

This addendum extends the [feasibility audit](pilot-001-feasibility-audit.md),
[input resolution](pilot-001-input-resolution.md),
[independent progress](pilot-001-independent-progress.md),
[preprocessing provenance](pilot-001-preprocessing-provenance.md) and
[score-verification result](pilot-001-score-verification-result.md). It repeats
nothing those records establish. Each item below states what it adds.

It covers the author code (S08) at commit
`48357fd63ccbfe3954f38c8efc558b4f88bd6051`: [part 2][p2], [part 3][p3],
[preprocessing notebook][rmd], [helpers][pre], [alignment][align] and
[Figure 3C][f3c]. Line numbers refer to that commit. Package behaviour was read in
source at named tags (S18–S21). Five static reviews by AI agents produced 89
candidate findings. Two further reviews tried to refute each one, and three more
checked the written text. A final comparison classified every item against the
earlier records and adjudicated the ten that conflicted. Paper quotes were
rechecked in the pinned article XML (SHA-256 `1d88848c…`, as in the independent
progress report). No human expert has reviewed this yet.

## Which objects feed the plotted cross-validation

Feasibility finding 1 says the run is not unambiguously selected. This adds the
evidence chain and a different risk direction.

- Part 3's cross-validation uses `data.nocb.coll.nopool` and `senref` (lines 11,
  27). It loads the discovery `noneo` files and then the `UM_Pilot` files
  (lines 5–9), and `load()` replaces same-named objects silently.
- Elsewhere the same `noneo` files are read for *suffixed* names: Figure 3C
  lines 59–62 and part 3 lines 137–149 use `data.nocb.coll.nopool1` and `senref1`.
  If those files define only suffixed names, then in a fresh top-to-bottom run
  the cross-validation takes its objects from the FFPE-validation files, or stops
  if neither file defines them. The reconstruction contract guards against the
  validation workspace overwriting discovery objects. The opposite risk, depending
  on it, is also possible.
- If part 2 ran first in the same session, its `primmets` objects (part 2 lines
  11–14) would be used. Supplement counts (158 samples; 13 neoadjuvant and 10
  mixed-site, disjoint) give 135 only when both exclusions apply. Part 2's
  hard-coded 135 therefore suggests the `primmets` set already excludes
  neoadjuvant samples, so it may equal the `noneo` set. This is an inference.
- Evidence for the intended cohort: the paper specifies 5-fold discovery and
  3-fold FFPE-validation cross-validation (S99), and part 3 always uses 5 folds.
- The frozen block loads frozen labels (line 136) and then reloads the `noneo`
  files (137–138). If those define `senref`, the frozen labels would be replaced.

None of this explains the 0.809 versus printed 0.83 discrepancy, and no cause is
attributed. A private object inventory should record which names each file
defines and compare `primmets` and `noneo` membership by aggregate counts.

## Orientation and operating points

- All three learners output the probability of the class coded 1 (glmnet
  response, xgboost `binary:logistic`, random-forest `prob[, 2]`). The forced
  `direction = "<"` (line 127) makes that class the ROC case, and pROC will not
  flip it.
- Every `senref` vector built in the repository codes sensitive as 1 (Figure 3C,
  Figure 1G, Figure S1L and the TGF-β script). Figure 3C replaces its own vector
  with labels loaded from the absent workspace (`senref1`, lines 62, 72) before
  its ROC. The convention therefore does not show how the workspace files code
  labels.
- The paper defines the score as the probability of refractory disease (S95) and
  reports detecting "~35% refractory tumors" at 98% specificity (P54, P58). The
  released discovery scores rank refractory tumours higher (AUROC 0.809, or 0.191
  reversed). If that sheet is part 3's output, then one of three holds: (a) the
  Figure 3D labels code refractory as 1, the only option consistent with all of
  the above but not established; (b) the scores were transformed on export, though
  no export code was found; or (c) the sheet comes from another run or code path.
- AUROC is unchanged when score and positive class flip together, so the open
  question concerns operating points only. The printed 0.35 cannot settle it:
  18/52 and 29/83 both round to 0.35.
- No line computes sensitivity at 98% specificity. The only related computation is
  an unseeded 2,000-replicate stratified `ci.se` bootstrap over a grid that
  includes 0.98. It is drawn as the plotted band (lines 129–132, 189). In an
  uninterrupted run its random state follows the last `set.seed(1000000)` and the
  final forest's draws, so a piecewise run changes the band. If 0.35 (0.19–0.52)
  came from it, the middle value is a bootstrap median.
- `roc(ci = TRUE)` gives a DeLong AUC interval by default (S19), while the paper
  describes bootstrap AUC intervals (S99). This answers the code-level question
  left open by feasibility finding 4.

## Panel provenance

- Part 2 implements only the metabolic-pathway branch of the paper's selection
  (P177). That branch is frequency selection among 492 genes over 500 subsamples
  of 80%, which matches 100 repeats × 5 training folds. Per-learner lists are
  combined by union. The paper's ≥50% cutoff versus the code's > 40% is already
  recorded. No code exists for the other branches: the Hypoxia and NF-κB set
  selection by cross-validated AUC, the four genome-wide FDR markers, and the
  removal of eight markers undetected in validation data. Even a working part 2
  yields at most the metabolic subset, not the 64-protein panel.
- Part 2 cannot reach its union (line 179) in a top-to-bottom run. Its summary
  helper reads `MeanDecreaseGini`, which xgboost importance tables lack, so it
  stops at line 148, before the random-forest summary (152). It would also
  replace feature names with row positions (lines 134–137).
- Per-learner criteria are: a nonzero elastic-net coefficient at `lambda.min`
  (alpha 0.1, default 10 inner folds); random-forest `MeanDecreaseGini` > 0.9, an
  absolute and scale-dependent cutoff; and an apparently intended xgboost
  Gain > 1e-6 (commented line 132).
- `meta_genes.RData` has no generator in any commit. P177 suggests the candidate
  list for this branch is the 492-gene metabolic union, chosen using cell-line and
  PDX data, but this is unverified.
- Every discovery sample is in the training set for 400 of the 500 fits. If part
  2's logic was used, the metabolic markers depend on every discovery label.

## Frozen block and alignment

- A search of all 42 R files finds nothing that assigns `data.nocb.rib.Frozen`.
- The frozen block computes ROC objects for the elastic net, xgboost and the
  ensemble, but none for the random forest. None is plotted or printed. The
  published frozen results are separate 34- and 27-row score sheets, and no
  subgroup-scoring code is in the repository.
- The frozen block's 500 rounds and 1,000 trees match the paper (S95). The
  cross-validation block's 100 rounds and 100 trees are the departure.
- Alignment (feasibility finding 5): line 28 multiplies by row 2 and adds row 1
  of the proteins-by-2 coefficient matrix. R recycles those two-element vectors
  across all values, so no protein receives its own intercept and slope.
- `read.delim2` defaults to a decimal comma (lines 2–6). With full-stop decimals
  under R < 4.0, the coefficient inputs (lines 11–15) become factor codes, while
  the application step (line 28) parses values. The two would then be on
  inconsistent scales.
- The alignment script writes `…_Imput_v02_AlignedToFD.tsv` (line 37). The
  Figure 6 immune script reads `…_Imput_AlignedToFD_20210823.tsv` (line 32).
  Part 3 reads neither, and whether they come from different runs is unknown.
- The overlap vectors `FD.sampleOverlap` and `FZ.sampleOverlap`, used by the
  Figure 5 and Figure 6 scripts, are never assigned in any commit. The supplements
  are the only available membership source.

## Names, failures and random-number streams

- **Names.** Part 2 selects rows through an absent `genes` vector and then applies
  `make.names(unique = TRUE)` (lines 14–15). Part 3 matches the panel against
  unmodified row names (line 11). The frozen block renames only the FFPE side
  (142) before ordering by match to frozen names (146).
  - glmnet predicts by position.
  - xgboost 1.x stops on name mismatch.
  - The random forest's formula interface fails ("object not found") on
    non-syntactic names.

  Whether `make.names` would alter any of the 64 pinned symbols can be checked
  from the panel alone, as an aggregate count.
- **Failures.** Only `cv.glmnet` is wrapped in `try()`. A failure breaks the fold
  loop, so that fold and all later folds of the repeat get no predictions from any
  model (lines 51–56). The per-repeat mean has no `na.rm` (line 107); the mean
  over repeats does (line 123). pROC then drops samples that were never predicted.
  The `stop` flag is unused, and failures are not counted. The released sheet has
  135 finite scores, so if it is this output no sample was lost entirely; thinning
  across repeats would be undetectable.
- **Unused results.** A stacked logistic model is fitted on in-sample training
  predictions (lines 93–100). It and the per-learner pools are unused.
- **Random streams.** `set.seed(1000000)` before every forest (line 79) means the
  inner `cv.glmnet` folds of outer folds 2–5 follow that fixed stream, advanced
  by the previous forest's draws. `set.seed(j)` governs only the fold draw and
  fold 1. The frozen-block forest is unseeded and depends on how many draws
  `cv.glmnet` and xgboost consumed. Preserving seeds 1–100 alone therefore does
  not reproduce the original stream structure.

## Upstream details not in earlier records

- ComBat is called with batch only and no outcome covariate.
- Plex membership is positional: 21 consecutive blocks of 8 columns in the
  outlier t-tests and in ComBat's batch vector. The helpers return transformed
  matrices only, so a training-fold version needs reimplementation with explicit
  plex labels and separate fit and apply steps.
- In the notebook, `eval = FALSE` is set for every chunk (line 11). DreamAI is
  never attached (25–26). `icc.vec` is plotted while `icc` is stored (100–101).
  The write statements sit outside code chunks (133–142).
- TMT outlier removal loops over `1:dim(m)[1]` ([helpers][pre] 127–134), which
  fails when no outlier is found. The risk in small training-fold subsets depends
  on the unresolved threshold (10^-7 in the paper, 10^-10 in the code).
- The discovery reconstruction starts from the released post-imputation matrix
  (S17). A leakage-controlled track built on it can control selection, tuning,
  thresholds and grouping, but not whole-cohort preprocessing. It should be
  described as partially leakage-controlled.

## Dependencies and version sensitivity

| Component | Notes (sources S18–S21) |
| --- | --- |
| R | 3.6.0 changed `sample()`'s default, which changes folds, inner folds and bootstrap draws for the same seed; record `RNGkind()`. 4.0.0 made `stringsAsFactors = FALSE` the default, which matters for the alignment input. |
| glmnet | Inner folds drawn with `sample()` unless `foldid` is given; prediction is positional; 3.0-1 and later need R ≥ 3.6.0; the binomial solver moved to C++ in 4.1-4. |
| xgboost | 1.x: exact method, intercept 0.5, draws from R's random stream, checks feature names. Upstream 2.0: histogram default and estimated intercept. CRAN went from 1.7.11.1 (2025-05-15) to 3.1.2.1 (2025-12-03) with a new interface that rejects the authors' calls and drops `ntreelimit`. |
| randomForest | 4.7-1 and later need R ≥ 4.1.0. |
| pROC | DeLong AUC interval by default; `ci.se` uses 2,000 stratified replicates; `ggroc` needs ≥ 1.10.0. |
| DreamAI (S18) | Method names, ensemble averaging and seeding changed across commits under version 0.1.0. "Brinn" was accepted only before 2020-09-21 or from 2020-10-07 to 2021-10-27. Relevant only if imputation is re-run. |

Any chosen set is a new environment, not the authors'. Fix exact versions, plus
one alternative configuration for sensitivity, before execution.

## Rights

No license file exists at any of the 69 commits. That is an observation, not a
legal determination. At its inspected head, DreamAI's top-level LICENSE is
Apache-2.0, added on 2020-05-21; one revision on 2020-05-22 used MIT text. Its
DESCRIPTION says GPL (>= 2), and bundled libFM sources carry GPL-3 text. This
matters only if DreamAI is installed or run.

## Follow-ups this addendum proposes

- **Protocol and contract (made in this change):**
  - Restrict the frozen comparison to independent patients.
  - Make refractory the asserted positive class, with re-orientation recorded as a
    deviation.
  - Pre-specify the frozen harmonisation strategy.
  - Add freeze-list items for RNG kind, the forest reseed, the xgboost version,
    missing values, name checks and per-repeat AUCs.
- **Wording clarifications in earlier records (not made here):**
  - Call the located score lineage the *intended* discovery calculation.
  - Note that the 64/64 panel coverage covers the discovery member only.
  - Write "figure-panel assignments" where Figure S3 letters are meant.
- **Aggregate checks that need no abundance values:**
  - Count how many pinned symbols `make.names` would change.
  - Check panel coverage in the frozen and FFPE-validation feature annotations.

## Limits

Static reading cannot show what was executed; the authors may have run code that
differs from the published scripts. The reviews were run by AI agents, and expert
review is still needed. Package behaviour refers to the inspected tags and was not
tested.

[p2]: https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part2.R
[p3]: https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R
[rmd]: https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocess_markdown.Rmd
[pre]: https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocessing.R
[align]: https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/FZ_data_alignment.r
[f3c]: https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Genetic_prediction_refractoriness/Figure_3C.R
