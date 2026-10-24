# Pilot 001: source-clarification request

**Ready for the owner to send (2026-10-24).**
- **Authorization.** On 2026-10-24 the user explicitly authorized putting the
  [code-audit addendum](../docs/pilot-001-code-audit-addendum.md) questions to the
  authors. This consolidated request also carries the questions held since
  2026-10-23 (items 3 and 5, and the original parts of items 1–2). The owner
  confirms the full text before sending.
- **Superseded draft.** The request replaces the earlier held draft; the
  2026-10-23 text remains in git history, for example at commit `6489425`.
- **Destination.** A comment on the existing
  [upstream data-availability issue](https://github.com/WangLab-MSSM/CPTAC_Ovarian_Chemo_Response/issues/1)
  from the owner's own account, or an email to the corresponding author.
- **Who sends it.** GitHub rejected automated posting earlier (“Resource not
  accessible by integration”), and a 2026-10-24 access check was also refused.
  Automated sessions must not post, retry or email it. Send it only once the
  code-audit pull request is open, and record the date and link once sent.

No patient identifiers, labels, scores or linkage rows are included. Recruiting
collaborators or reviewers remains on hold.

---

We are preparing a research reproduction of the Figure 3D protein ensemble in
Chowdhury et al. (Cell, 2023), and thank you for making the code and processed
data public. We inspected commit `48357fd63ccbfe3954f38c8efc558b4f88bd6051` and
the public NLM supplements for PMC10414761.1. We recovered the 64-protein panel
from `NIHMS1918576-supplement-MMC4.xlsx`, worksheet `64_protein_predictors`, and
reconciled the published prediction denominators with the clinical annotations.

Could you clarify these remaining reproduction inputs?

1. **Inputs and terms.** Where are `balanced_folds.R` and the RData workspaces
   loaded by `Figure_3D_part2.R` / `Figure_3D_part3.R` available? Under what
   terms may they, the analysis code and the processed-data archive be reused?
   If the workspaces cannot be shared, is there a script specifying their
   construction from PDC files? It would need object names, sample/feature
   ordering, response coding (which class is coded 1), normalization, batch
   correction and imputation. How was `meta_genes.RData` built, and did it use
   response labels?
2. **Code and environment.** Which code and environment produced the reported
   result? We would like to distinguish intended implementations from
   transcription or version differences, rather than silently changing the
   reproduction.
   - The public scripts and methods differ in feature-selection frequency and in
     CV versus frozen model sizes. The XGBoost importance reducer uses
     `MeanDecreaseGini`, and the frozen alignment expression indexes rows of the
     coefficient matrix.
   - Part 3's cross-validation uses `data.nocb.coll.nopool` and `senref`, which
     the script does not define, after loading both the discovery and the
     FFPE-validation workspaces. Which workspace supplied them for Figure 3D?
     Were the scripts run in one session?
   - Which R and package versions, random-number settings and DreamAI commit
     were used? DreamAI's version string stays 0.1.0 across behaviour changes.
   - How were the supplementary prediction scores exported? The methods define
     the score as the probability of refractory disease, and the released
     discovery scores rank refractory tumours higher. Scripts that build labels
     from the clinical table code sensitive tumours as 1; we could not tell how
     the saved workspaces code them. For context, the AUROC computed directly
     from the released discovery scores (refractory as positive) is 0.81,
     compared with 0.83 in Figure 3D; we have not attributed a cause. Is that
     sheet the output of the Figure 3D cross-validation?
3. **Frozen subgroups.** Can you clarify the frozen subgroup definitions?
   - Joining each published score `Samples` key exactly to the clinical
     `Data Label 2` field, then comparing the explicit `Patient ID` field, gives
     six patient keys in the 34-row `Frozen_nonoverlap_pred_scores` sheet that
     also occur in the 135-row discovery score set.
   - All joins are unique, and the discovery membership matches the literal
     neoadjuvant/mixed-location exclusions. A missing location-group annotation
     is retained rather than inferred nonmixed.
   - This is a source-membership finding, not a claim about its effect on
     performance.

   Is another identifier mapping, exclusion or supplement version required?
   Which samples contributed to upstream alignment and preprocessing? Please also
   clarify the retained missing location annotation. Finally, was
   `data_nov.RData` built from an aligned frozen file, and if so, which one? The
   alignment script writes `…_Imput_v02_AlignedToFD.tsv`, and the Figure 6
   script reads `…_Imput_AlignedToFD_20210823.tsv`.
4. **Operating point and intervals.** How were the sensitivity at 98%
   specificity (0.35, 95% CI 0.19–0.52) and the AUC interval derived? The
   scripts draw a bootstrap sensitivity band but do not extract a value at 98%
   specificity. `roc(ci = TRUE)` defaults to a DeLong interval, while the methods
   describe a bootstrap.
5. **Corrected legends.** Which downloadable supplementary artifact incorporates
   the corrected legends associated with DOI `10.1016/j.cell.2024.01.016`?

Our reproducibility record and aggregate-only checking code are in the
[Project Asma pull requests](https://github.com/Foundation-0/project-asma/pulls).
The code-level questions above are documented in the code-audit addendum on
that list. Please do not share patient-level files or linkage rows publicly (for
example, in the GitHub issue); any restricted material would need an
appropriately authorized private route.
