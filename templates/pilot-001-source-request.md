# Pilot 001: source-clarification request

**Draft only — not sent.** Proposed destination: the existing
[upstream data-availability issue](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/issues/1).
No patient identifiers, labels, scores or linkage rows are included. Posting
this message requires explicit authorization to contact the authors.

---

We are preparing a research reproduction of the Figure 3D protein ensemble in
Chowdhury et al. (Cell, 2023). We inspected commit
`48357fd63ccbfe3954f38c8efc558b4f88bd6051` and the public NLM supplements for
PMC10414761.1. We recovered the 64-protein panel from
`NIHMS1918576-supplement-MMC4.xlsx`, worksheet `64_protein_predictors`, and
reconciled the published prediction denominators with the clinical annotations.

Could you clarify these remaining reproduction inputs?

1. Where are `balanced_folds.R` and the RData workspaces loaded by
   `Figure_3D_part2.R` / `Figure_3D_part3.R` available, with applicable reuse
   terms? If the workspaces cannot be shared, is there a script specifying their
   construction from PDC files, including object names, sample/feature ordering,
   response coding, normalization, batch correction and imputation?
2. Which code/environment produced the reported result? The public scripts and
   methods differ in feature-selection frequency and CV versus frozen model
   sizes. The XGBoost importance reducer uses `MeanDecreaseGini`, and the frozen
   alignment expression indexes rows of the coefficient matrix. We would like
   to distinguish the intended implementations from transcription/version
   differences rather than silently changing the reproduction.
3. Can you clarify the frozen subgroup definitions? Joining each published score
   `Samples` key exactly to the clinical `Data Label 2` field, then comparing the
   explicit `Patient ID` field, gives six patient keys in the 34-row
   `Frozen_nonoverlap_pred_scores` sheet that also occur in the 135-row discovery
   score set. All joins are unique, and the discovery membership matches the
   literal neoadjuvant/mixed-location exclusions, with a missing location-group
   annotation retained rather than inferred nonmixed. This is a source-membership
   finding, not a claim about its effect on performance. Is another identifier
   mapping, exclusion or supplement version required? Which samples contributed
   to upstream alignment and preprocessing? Please also clarify the retained
   missing location annotation.
4. Which downloadable supplementary artifact incorporates the corrected legends
   associated with DOI `10.1016/j.cell.2024.01.016`?

Our reproducibility record and aggregate-only checking code are available in
[Project Asma PR #2](https://github.com/Foundation-0/project-asma/pull/2).
Please do not post patient-level files or linkage rows in this issue; any
restricted material would need an appropriately authorized private route.
