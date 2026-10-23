# Pilot 001: independent source and reconstruction progress

**Checked:** 2026-10-23. **Evidence class:** public-source inspection and
in-memory metadata diagnostics. External outreach remains on hold. These checks
do not replace scientific review or complete model reproduction.

**A new public input was recovered:** the author-released imputed discovery
matrix's header matches all 168 response-labelled measurement rows and all 135
published discovery-score sample keys by exact equality. This closes candidate
input naming, while full matrix integrity, feature coverage and original
workspace generation remain open. The existing supplied-score AUROC **0.8088507878**
is retained unchanged. No alternative scores, cohorts or tolerances were tried
to improve agreement with the printed 0.83.

## Score provenance: the target is identifiable, its export is not

All code observations below refer to author commit
`48357fd63ccbfe3954f38c8efc558b4f88bd6051`. Code was read, not executed or copied
into this repository.

In [Figure_3D_part3.R, lines 105–127](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L105-L127),
the discovery calculation averages held-out ElasticNet, XGBoost and random-forest
probabilities within a repetition, then averages across 100 repetitions.
`y.pred.avg.pool1.all` supplies the scores for `roc.all1`. This identifies the
intended repeated-CV output object; it does not recover its values or inputs.

The script contains no prediction export linking that object to the published
workbook. A targeted scan of all **42 R/r/Rmd files** at the pinned commit found
no references to any of the four published score-sheet names or `Pred.scores`.
All 42 files were retrieved. This is a bounded negative search, not proof that
an export never existed.

The same script also creates discovery predictions after fitting models to the
full discovery set for frozen-cohort evaluation
([lines 154–175](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L154-L175)).
Those in-sample predictions are distinct from the repeated-CV output. There is
no evidence that the workbook uses either family. Matching the 135 discovery
sample keys therefore cannot, by itself, establish out-of-fold score provenance.

The paper's methods (section S99, paragraph P183) specify fivefold discovery CV
and threefold FFPE-validation CV. Part 3 loads both workspaces
([lines 5–9](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L5-L9)),
but its helper call and outer loop use five folds unconditionally
([lines 23–45](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Protein_prediction_refractoriness/Figure_3D_part3.R#L23-L45)).
A future reconstruction must explicitly select the cohort and documented fold
count. Choosing new package versions or implementing the missing fold helper
would define a reconstruction, not recover the original runtime.

## Matrix naming: a missing annotation bridge

The author [preprocessing function, lines 3–22](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocessing.R#L3-L22)
renames matrix columns using an earlier data-label field and an expanded
`Data Label 2` field from a separate sample annotation table. It uses substring
comparison and requires identical vector order before replacement.
The [calling document, lines 42–54](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/blob/48357fd63ccbfe3954f38c8efc558b4f88bd6051/Data_preprocessing/preprocess_markdown.Rmd#L42-L54)
loads the absent `samples_FFPE_Aug19.csv` and calls this function after reading
the matrix with R's default name checking.

The pinned clinical workbook supplies expanded `Data Label 2`, patient/sample
keys and TMT annotations, but not the earlier data-label field or `Process.ID`
required by that function. Consequently, an exact comparison to the expanded
labels is a diagnostic of available inputs, not a faithful implementation of
the author's naming conversion. We do not infer patient identity from column
substrings, vector position, matching cohort totals or similar-looking names.

The new [header diagnostic](../tools/audit_matrix_headers.py) tested exact
whole-string equality against those expanded clinical labels. Its
[aggregate run record](../registries/pilot-001-matrix-header-summary.json)
reports:

| Cohort | Matrix header columns | Clinical rows | Exact label matches | Matches with response-labelled patient/sample keys |
| --- | ---: | ---: | ---: | ---: |
| Discovery | 237 | 231 | 41 | **0** |
| FFPE validation | 28 | 22 | 0 | **0** |
| Frozen validation | 94 | 88 | 0 | **0** |

All 41 discovery matches are rows with explicit missing clinical annotations;
they are not patient links. Missing clinical annotations alone also do not
establish that these rows are controls or reference channels. Unmatched matrix
columns include annotation fields; the counts are not counts of unmatched
patients. The tool does not infer which columns are measurements from position
or naming patterns. Nonmatches do not prove the files are unrelated.

The live run read only the first header line of each matrix (4,573 / 524 / 1,691
bytes), checked HTTP 206 and the declared byte range/file size, and validated
unchanged version-1 study/file metadata before and after. Headers and the pinned
clinical workbook stayed in memory. Full matrix bodies were not downloaded;
catalog MD5s remain unverified against those bodies. The run took 4.82 seconds.

```sh
python3 tools/audit_matrix_headers.py
```

A separate exploratory probe of PDC's `uiStudyExperimentalDesign` queried explicit
plex/channel-to-aliquot annotations. It returned 21 / 2 / 8 design records and
210 / 20 / 80 channel assignments for discovery / FFPE / frozen. No matrix header
matched a whole-string run-metadata ID, run submitter ID, plex dataset name,
decimal experiment number, aliquot ID, aliquot-run ID or aliquot submitter ID.
Clinical `TMT Plex` values also did not exactly match the queried design scalar
fields; clinical `Label` values did not exactly equal the standard channel
vocabulary. This rejects only the tested exact-equality routes. A source-backed
composite mapping or naming transformation could still resolve the gap.
This probe is not part of the retained runnable header audit. Its query used
`source: "pdc"` and all ten channels from `tmt_126` through `tmt_131`; its
one-line query SHA-256 was
`2dbcfe3c3c9be9579a5c192664f93b260d826ee1941c2ba5cfdbbf482223497c`.
The decoded full-response fingerprints (sorted-key compact UTF-8 JSON,
array order preserved) were:

| Study | Exploratory design-response SHA-256 |
| --- | --- |
| PDC000360 | `01533d8b2a1fe0c52b54d2853eacec79dc6b40f30ba2f44a30d10cbb7b206c08` |
| PDC000358 | `e3460aee7394b125f9fe28de76098367242b508f0d2d4202deea360e8802a606` |
| PDC000362 | `6c182726daa856beb7933e6fa621130c182be60df6fc1af76b8191f86e1f2dde` |

## Correction provenance: a content mismatch, not just a timestamp

The correction says supplemental figure legends contained errors and omissions
and that corrected legends are online. Its NLM XML supplies neither a
panel-specific change list nor supplementary attachments. The available NLM
Figure S3 caption conflicts with the article's own references:

| Subject | NLM supplement, PDF page 6 | Article XML locator and reference |
| --- | --- | --- |
| 64-protein panel details | No corresponding caption item | P32: S3C |
| RNA–protein correlations | No corresponding caption item | P32: S3D |
| Phosphoproteomic ROC | S3D/E | P36: S3E/F |
| MRM assay ROC | No corresponding caption item | P35: S3G |
| Joint proteogenomic models | S3F/G | P37: S3I/J |

The pinned S3 legend is therefore unsuitable as the authoritative source for
these panel assignments. Use explicitly located main-text/methods passages for
the limited source audit, while retaining corrected-artifact verification as
open. This mismatch does not establish a change to Figure 3D or explain the
supplied-score AUROC discrepancy.

The publisher's search-indexed S3 caption has assignments consistent with the
article XML. Direct publisher retrieval returned HTTP 403, so that indexed
text is corroboration, not a pinned corrected artifact. A complete NLM public
listing for the original article prefix returned 20 objects, all under version
`.1`; it does not establish that no other corrected copy exists elsewhere.

| Public source | Bytes | SHA-256 |
| --- | ---: | --- |
| [Article XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC10414761.1/PMC10414761.1.xml) | 449,678 | `1d88848c7b3dcda6f6b7734922f2f75b0ddeb0796d682d900d68cc2ffddd187b` |
| [Figure supplement](https://pmc-oa-opendata.s3.amazonaws.com/PMC10414761.1/NIHMS1918576-supplement-1.pdf) | 13,076,963 | `7726253a4b85e7f1aae49b4bc68ed882004b56b3bd54678053d98dbdfec26c0c` |
| [Correction XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC10935576.1/PMC10935576.1.xml) | 13,637 | `a59fe5c54438570ba767e5e1548cfb13385fca03e5b73d1f13f559bd4248bd71` |

These sources were rechecked on 2026-10-23. Only provenance and short analytical
descriptions are retained; source publications are linked rather than redistributed.

## A new public input lead from the readiness screen

The bounded screen identified [Kilim et al., 2025](https://doi.org/10.1038/s41698-025-00808-w)
as the closest follow-up. Its [pinned README](https://github.com/csabaiBio/HGSOC_platinum_response/blob/962aaa8aa855ae9dfa50a27dd69baa9b0e7e45d7/README.md)
explicitly names `FFPE_discovery_globalprotein_imputed.tsv` in the original
paper's Dropbox `processed_data.zip`. This supplied a specific new source lead
instead of repeating the earlier missing-file search.

The original archive is accessible by bounded HTTP 206 requests. Its central
directory contains the named global-protein matrix: compressed 7,993,706 bytes,
uncompressed 18,498,831 bytes. The 70,138,965-byte archive has 42 directory entries;
central-directory SHA-256 is
`5dd3db7c674ab2952a148af474da6604c1daf88a4e2cf2ff45d939f7530ae5a0`.
This establishes that the earlier LC-MRM description did not capture the archive's
full contents. It does not establish matrix-body integrity, transformation
equivalence or the contents of the missing prediction workspaces.

The archive's `ReadMe_PTRC_data.docx` separately describes imputed global and
phosphoproteomic files and batch-corrected files before imputation. It does not
establish the exact generation chain between them, the imputation parameters or
an explicit archive reuse grant. The 13,991-byte README was recovered by bounded
ranges and verified against its ZIP CRC32; SHA-256 is
`e51beb676c7b8705ed655d108da8034e891ecbe5a5b5f77788fd3427943e941a`.
Neither PDC's nor the downstream Figshare release's license is automatically
assigned to this separate archive.

The [archive-header audit](../tools/audit_author_archive.py) then verified the
pinned ZIP directory and member metadata, retrieved a bounded compressed prefix,
and stopped inflation at the first newline. Its
[aggregate result](../registries/pilot-001-author-archive-summary.json) establishes:

| Discovery imputed matrix header check | Result |
| --- | ---: |
| Header columns / bytes | 178 / 4,433 |
| Exact response-labelled measurement matches | **168 / 168** |
| Unique annotated sample / patient keys represented | **158 / 158** |
| Exact published discovery-score key matches | **135 / 135** |
| Matched clinical-NA rows | 0 |
| Header columns without an exact clinical label | 10, not classified as patients or measurements |

Every score key joined to its explicit clinical row; the score cohort also
equalled the previously reconstructed exclusions. No substring matching,
positional assignment or replicate averaging was used. This resolves naming for
the recovered imputed input, not for the differently named raw PDC matrix.

```sh
python3 tools/audit_author_archive.py
```

Only 69,770 archive bytes were fetched, including 4,096 compressed member bytes.
Decompression stopped at the header newline; no abundance values were inspected.
Header SHA-256:
`e39ef0ffaafaa92ca6dd7351ed578856be22f4e03b2cf26111106790bd7521c9`.
The 10.77-second run retains source and implementation hashes. Neither the full
member CRC/checksum nor full archive integrity was verified. The source workbook
hashes were verified in memory; only aggregate outputs are retained.

The downstream paper also provides these distinct releases:

| Source | Verified metadata / inspection |
| --- | --- |
| [Figshare clinical/proteomics v1](https://doi.org/10.6084/m9.figshare.26954422.v1) | CC BY 4.0; `HGSOC_TCGA_main.csv`, file 49045213, 76,182,376 bytes; catalog MD5 `048815738fc104416d65ebf3fdc638dc`. Only the 47,315-byte header was read (HTTP 206), with 7,632 unique columns. Header SHA-256 `71ffec1892bcdaebf77bfaf7b9eb1ad180ae56979c81b9f65a3e949fc369adc2`. |
| [Figshare protein groupings v1](https://doi.org/10.6084/m9.figshare.27441231.v1) | CC BY 4.0; `proteomics_combinations.json`, file 50137041, 126,949 bytes. Full non-patient feature file verified against MD5 `def077e4a543b667a21028503b7e0956`; SHA-256 `6c275ca89e70858957c1a365468e4a210754937d55b470055c846d5a22a5fbbe`. |

The [downstream setup script](https://github.com/csabaiBio/HGSOC_platinum_response/blob/962aaa8aa855ae9dfa50a27dd69baa9b0e7e45d7/HGSOC_platinum_responce/HGSOC_TCGA_tasks_data_setup.py)
(lines 87–118 and 227–269) transforms the imputed matrix, joins clinical metadata
using substrings, standardizes values and intersects HGSOC/TCGA features before
writing the combined CSV. Its header has `case_id`, `slide_id` and `label`, but
not the original measurement-level patient/sample/neoadjuvant schema. These
derived identifiers cannot simply be adopted as the missing original mapping.

A possible **separate** reproduction target is the 2025 Table 1 primary-tissue
proteomics result, PTRC → TCGA: published AUROC **0.61 ± 0.05**. This is a reference,
not our result. It uses 60 shared proteins and labels sensitive as 1, versus the
current pilot's 64 proteins and refractory-positive direction. The paper's
158/127 overall patient totals are not verified primary-only denominators.
Its test scores average five trained models per patient; CV entries average
fold AUROCs. These procedures must not be interchanged. The ± notation describes
bootstrap variability, not an established 95% confidence interval.

This candidate is not yet ready to run: full input/split correspondence, feature
version, exact environment and model randomness remain unresolved. The Figshare
feature file differs from the repository copy. The method does not establish
training-only preprocessing, and its treatment-naive statement needs
reconciliation with a figure mentioning neoadjuvant treatment. Public code
availability and data licensing do not supply an explicit repository code-license
grant. The article XML was pinned at 262,653 bytes, SHA-256
`e26c5f7f6e11638fbe82a6afe1258f31dab5eab72a6036ba2e7c81ff0130c099`.

The screen prioritized this directly relevant lead; other candidates were not
advanced to execution. Inspect the original matrix before considering a separate
downstream target. No new performance result or replacement target is adopted.

## Independent continuation

The [reconstruction contract](../protocols/pilot-001-independent-reconstruction.md)
now fixes the intended discovery cohort, panel, score direction, fivefold/
100-repeat aggregation, input requirements and failure rules. It separates
future replacement helper/environment choices from recovery of the original
analysis. Model fitting has not started.

| Work | Disposition |
| --- | --- |
| Direct PDC matrix-to-clinical labels and PDC design route | Executed; exact equality does not supply patient linkage. |
| Original author imputed discovery matrix | Recovered header links all 168 measurement rows and all 135 score keys exactly; full matrix contents and workspace generation remain unverified. |
| Discovery score-generation lineage | Located; export to released score workbook remains absent from inspected code. |
| Corrected S3 interpretation | Concrete mismatch documented; authoritative corrected artifact still needed. |
| Public-input reconstruction | Specified prospectively; candidate naming bridge recovered; needs full integrity, feature/transform contracts and frozen implementation before fitting. |
| Original predictions, independent validation and scientific review | Unresolved; no completion or clinical-performance claim. |

The next independent work is to establish applicable matrix reuse terms, verify
the recovered member's full integrity and protein coverage, and document its
transformation/collapse history. Then freeze the reconstruction implementation
before fitting. The downstream 2025 result remains a separate fallback with its
own unresolved contracts. No external contact is scheduled.

The 21 new offline tests exercise exact joins, separation of clinical-NA rows,
duplicate/conflicting annotations, bounded HTTP/ZIP/header reads, metadata drift,
decompression limits, complete score-key coverage and generic error handling.
All 72 repository tests pass. These checks validate software contracts, not the
missing biological or historical relationships.

PDC aggregate checks use the version-1 records for PDC000360, PDC000358 and
PDC000362 and change their presentation into counts. Credit: PDC and
[Chowdhury et al.](https://doi.org/10.1016/j.cell.2023.07.004), under PDC's stated
[CC BY 4.0 terms](https://creativecommons.org/licenses/by/4.0/).
Data used in this publication were generated by the National Cancer Institute
Clinical Proteomic Tumor Analysis Consortium (CPTAC). The NLM supplement terms
are distinct, as recorded in the [input report](pilot-001-input-resolution.md).
