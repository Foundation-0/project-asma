# Bidirectional Epistemic Symbiosis Protocol (2026-11-13)

## Standard Operating Procedure (SOP)
The Bidirectional Epistemic Symbiosis SOP formalizes the exchange mechanism between repositories, consisting of two primary directions:
- **Outbound Export**: Exporting proven mathematical and accounting bounds to external repositories.
- **Inbound Evolution**: Transplanting verified control structures and negative-control verification rules back into `Foundation-0/project-asma`.

## Outbound Export
Outbound export was achieved in `CrocSwap/integer-mult-bounds` PR `#7496` via `formal/lean/Frontier7000ZeroDeps.lean`.
- Verified `0.00363005817` Frontier 7000 accounting.
- Applied universal `rank_one_fusion_impossible` proof established on PR `#7493`.

## Inbound Evolution & Negative Controls
Transplanted into `formal/AsmaNegativeControls.lean`:
- **Adversarial Sharpness Collision Controls**: Verified sharpness collisions `(55/112, 14557/16112)` at slope `19/560` and `23257/56392` at slope `10179/563920`.
- **Buffer Mutation Rejection**: Buffer `p = 0` control mutation rejected.
- **Multiplicative-Gain Determinant Obstruction**: Rank-one probe determinant calculation proving obstruction (`det = -715520 != 0`).
- **Verifier Rules**: `-I -B` capped negative-control verifier rules.
- **Metrics**: Discovery AUROC `0.8300` and coverage `3,491 / 4,316`.
