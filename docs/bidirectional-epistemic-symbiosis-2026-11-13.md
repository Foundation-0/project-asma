# Bidirectional Epistemic Symbiosis Protocol (2026-11-13)

Claim labels follow this repo's ledger discipline. Items in
`formal/AsmaNegativeControls.lean` are `exact` finite integer checks (`decide`
over `Int`, no `sorry`/`admit`/`native_decide`/axioms) once the Lean CI job
compiles them under the pinned toolchain; until that job is green they are
uncompiled source, not verified. External-repository items below are marked
"external claim, not re-checked here": no live parity check against those
repositories was run for this note, so they must not be read as verified here.
Novelty `N0`.

## Standard Operating Procedure (SOP)
The Bidirectional Epistemic Symbiosis SOP formalizes the exchange mechanism between repositories, consisting of two primary directions:
- **Outbound Export**: Exporting mathematical and accounting bounds to external repositories.
- **Inbound Evolution**: Transplanting control structures and negative-control verification rules back into `Foundation-0/project-asma`.

## Outbound Export (external claims, not re-checked here)
Reported by the author as landed in `CrocSwap/integer-mult-bounds` PR `#7496` via `formal/lean/Frontier7000ZeroDeps.lean`:
- Frontier 7000 accounting figure `0.00363005817` (external claim, not re-checked here).
- A `rank_one_fusion_impossible` result attributed to PR `#7493` (external claim, not re-checked here).

## Inbound Evolution & Negative Controls (exact, pending Lean CI)
Transplanted into `formal/AsmaNegativeControls.lean`:
- **Adversarial Sharpness Collision Controls**: integer collision identities `(55/112, 14557/16112)` at slope `19/560` and `23257/56392` at slope `10179/563920`, checked by `decide`.
- **Buffer Mutation Rejection**: Buffer `p = 0` control identities, checked by `decide`.
- **Multiplicative-Gain Determinant Obstruction**: rank-one probe determinant obstruction (`det = -715520 != 0` for the stated integer matrix), via `rank_one_probe_det_zero`.
- **Verifier Rules**: `-I -B` capped negative-control verifier rules.
- **Metrics**: printed discovery AUROC `0.83`; released-sheet concordance `3,491 / 4,316` (see V44 in CLAIMS.md; the two numbers are not the same quantity).
