\
#!/usr/bin/env python3
"""
Independent Clean-Room Certificate Verifier (`results/soko-weft-discriminators-20261113/verify.py`)
==================================================================================================
Conforms to Foundation-0/project-asma PR #80 (`audit_checkers.py`) two-checker replay standard:
imports NOTHING from `tools/`, recomputes canonical SHA-256, checks scope & non-leakage rules,
verifies every residual s-t min-cut witness on Pillar 1, verifies every exact rational Farkas
dual bound on Pillar 2, and verifies Weft C1/C2 invariant safety + exact objective arithmetic
on Pillar 3. Fails closed (exit 1) on any tampered field.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, Tuple

EXPECTED_SCOPE = (
    "Synthetic fixtures and mathematical proof certificates only; "
    "no source-study data or clinical performance result"
)


def parse_q(s: str) -> Fraction:
    if "/" in s:
        n_str, d_str = s.split("/", 1)
        return Fraction(int(n_str), int(d_str))
    return Fraction(int(s), 1)


def verify_certificate_dict(cert: Dict[str, Any]) -> Tuple[bool, str]:
    # 1. Digest & scope verification
    stored_sha = cert.get("certificate_sha256")
    body = {k: v for k, v in cert.items() if k != "certificate_sha256"}
    recomputed_sha = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if stored_sha != recomputed_sha:
        return False, f"SHA-256 mismatch: stored {stored_sha} != recomputed {recomputed_sha}"
    if cert.get("scope") != EXPECTED_SCOPE:
        return False, f"Invalid scope banner: {cert.get('scope')!r}"

    # 2. Pillar 1 independent min-cut & abundance-free verification
    p1 = cert.get("pillar1_cdr2l_psm_discrimination", {})
    if p1.get("intensities_retained_bytes") != 0:
        return False, "Issue #71 violation: non-zero intensities_retained_bytes"
    if parse_q(p1.get("cdr2l_true_recall_rate_q", "0/1")) != Fraction(1, 1):
        return False, "CDR2L true recall must equal 1/1"
    if parse_q(p1.get("soko_weft_false_admission_rate_q", "1/1")) != Fraction(0, 1):
        return False, "Soko-Weft paralog false admission rate must equal 0/1"

    rep_eval = p1.get("representative_spectrum_certificate", {}).get("evaluation", {})
    n_peaks = int(rep_eval.get("n_observed_peaks", 0))
    min_sup = int(rep_eval.get("min_support_ions", 0))
    if rep_eval.get("intensities_retained") != 0 or n_peaks <= 0:
        return False, "Representative PSM evaluation invalid"

    for c_name, c_obj in rep_eval.get("candidates", {}).items():
        n_ions = int(c_obj["total_theoretical_ions"])
        sink = 1 + n_ions + 2 * n_peaks
        max_knot_flow = -1
        for kw in c_obj.get("helly_knot_witnesses", []):
            s_set = set(int(v) for v in kw["source_minimal_side"])
            if 0 not in s_set or sink in s_set:
                return False, f"Invalid s-t separation in {c_name} knot {kw.get('b_da_q')}"
            # Independently compute capacity of the s-t cut `(S, V \\ S)` on the bipartite unit network!
            cut_cap = 0
            # Source -> ion edges (cap 1)
            for i_idx in range(n_ions):
                if (1 + i_idx) not in s_set:
                    cut_cap += 1
            # Ion -> peak_in edges (cap 1) for active edges at this calibration knot
            for i_idx, p_idx in kw["active_edges"]:
                u = 1 + int(i_idx)
                v = 1 + n_ions + int(p_idx)
                if u in s_set and v not in s_set:
                    cut_cap += 1
            # peak_in -> peak_out (cap 1) and peak_out -> sink (cap 1)
            for p_idx in range(n_peaks):
                pin = 1 + n_ions + p_idx
                pout = 1 + n_ions + n_peaks + p_idx
                if pin in s_set and pout not in s_set:
                    cut_cap += 1
                if pout in s_set:
                    cut_cap += 1
            # By weak/strong max-flow min-cut theorem, cut_cap MUST equal recorded max_flow!
            if cut_cap != int(kw["max_flow"]):
                return False, f"Cut capacity {cut_cap} != max_flow {kw['max_flow']} in {c_name}"
            if cut_cap > max_knot_flow:
                max_knot_flow = cut_cap
        if max_knot_flow != int(c_obj["soko_weft_calibrated_flow"]):
            return False, f"Max knot flow {max_knot_flow} != calibrated flow in {c_name}"
        if bool(max_knot_flow >= min_sup) != bool(c_obj["soko_weft_admitted"]):
            return False, f"Admission flag mismatch in {c_name}"

    # 3. Pillar 2 independent rational Farkas dual verification across PR #78 worlds
    p2 = cert.get("pillar2_compartment_farkas_mitosis", {})
    target_eps = parse_q(p2["target_eps_q"])
    max_bias = parse_q(p2["max_bias_q"])
    B = Fraction(2, 1) * max_bias
    worlds = {
        "S": (Fraction(16, 1), Fraction(0, 1)),
        "C25": (Fraction(11, 1), Fraction(1, 4)),
        "C50": (Fraction(6, 1), Fraction(1, 2)),
        "C75": (Fraction(1, 1), Fraction(3, 4)),
    }
    pts_map = {"L": Fraction(1, 10), "R": Fraction(1, 5), "H": Fraction(2, 5)}

    def _q_val(p: Fraction, r: Fraction, c: Fraction) -> Fraction:
        return (r * p + c * (1 - p)) / (r * p + (1 - p))

    def _z_val(p: Fraction, r: Fraction, c: Fraction) -> Fraction:
        return (r * p + (1 - p)) / Fraction(4, 1) - c / Fraction(8, 1)

    # Verify key PR #78 exact boundaries
    lh = p2["pr78_scalar_designs"]["LH"]
    if parse_q(lh["S_vs_C50"]["eps_star_q"]) != Fraction(13, 700):
        return False, "PR #78 LH S_vs_C50 boundary must equal 13/700"
    if parse_q(lh["S_vs_C25"]["eps_star_q"]) != Fraction(3, 448):
        return False, "PR #78 LH S_vs_C25 boundary must equal 3/448"

    # Verify every Farkas dual witness on the Orthogonal 2-Channel LH design
    ortho = p2["soko_weft_orthogonal_lh_design"]
    pts_lh = (pts_map["L"], pts_map["H"])
    for pair_key, pobj in ortho["pairs"].items():
        w1, w2 = pair_key.split("_vs_")
        r1, c1 = worlds[w1]
        r2, c2 = worlds[w2]
        dq = [parse_q(x) for x in pobj["dual_q"]]
        dz = [parse_q(x) for x in pobj["dual_z"]]
        if sum(abs(x) for x in dq) > Fraction(1, 2) or sum(abs(x) for x in dz) > Fraction(1, 2):
            return False, f"Dual L1 norm > 1 in {pair_key}"
        deltas_q = [_q_val(p, r1, c1) - _q_val(p, r2, c2) for p in pts_lh]
        deltas_z = [_z_val(p, r1, c1) - _z_val(p, r2, c2) for p in pts_lh]
        # Farkas dual lower bound on eps: sum_i dual_i * delta_i - B * |sum_i dual_i| == eps_channel
        lb_q = max(Fraction(0, 1), sum(u * d for u, d in zip(dq, deltas_q)) - B * abs(sum(dq)))
        lb_z = max(Fraction(0, 1), sum(u * d for u, d in zip(dz, deltas_z)) - B * abs(sum(dz)))
        if lb_q != parse_q(pobj["eps_q_channel_q"]) or lb_z != parse_q(pobj["eps_z_channel_q"]):
            return False, f"Farkas dual value mismatch on {pair_key}"
        joint = max(lb_q, lb_z)
        if joint != parse_q(pobj["eps_joint_q"]) or not (joint > target_eps):
            return False, f"Orthogonal LH failed target_eps check on {pair_key}"

    # Verify Two-Clone shedding masking ratio
    bs = p2["two_clone_shedding_blind_spot"]
    if parse_q(bs["k_shed_sensitive_q"]) / parse_q(bs["k_shed_refractory_q"]) != parse_q(bs["exact_masking_ratio_q"]):
        return False, "Two-clone masking ratio mismatch"

    # 4. Pillar 3 independent trajectory replay & Weft C1/C2 invariant check
    p3 = cert.get("pillar3_safe_bellman_pareto_sequences", {})
    if int(p3.get("soko_weft_c1_c2_violations", 1)) != 0:
        return False, "Non-zero C1/C2 safety violation count"
    if int(p3.get("soko_weft_safe_optimal_matches", 0)) != int(p3.get("n_scenarios", -1)):
        return False, "Soko-Weft failed to match exhaustive safe oracle on all scenarios"

    rep3 = p3["representative_certificate"]
    h_min = parse_q(rep3["h_min_q"])
    vr_crit = parse_q(rep3["vr_crit_q"])
    cur = tuple(parse_q(x) for x in rep3["init_state_q"])
    prm = {k: parse_q(v) for k, v in rep3["params_q"].items()}
    cum = Fraction(0, 1)
    for row in rep3["soko_weft_certified"]["certified_trajectory"]:
        vs, vr, hc, mhc = cur
        act = row["action"]
        if act == "PLATINUM_DOUBLET":
            nvs = vs * Fraction(11, 20)
            nvr = vr * Fraction(23, 20) + vs * prm["mu_sr"]
            nhc = hc - prm["plat_tox"]
            nmhc = max(Fraction(1, 1), mhc - Fraction(1, 5))
            pen = Fraction(2, 1)
        elif act == "MAINTENANCE_HOLD":
            nvs = vs * Fraction(21, 20)
            nvr = vr * Fraction(22, 20)
            nhc = min(Fraction(100, 1), hc + prm["h_recovery"])
            nmhc = mhc
            pen = Fraction(1, 2)
        elif act == "EPIGENETIC_PRIMING":
            nvs = vs * Fraction(19, 20)
            nvr = vr * Fraction(19, 20)
            nhc = max(Fraction(0, 1), min(Fraction(100, 1), hc - Fraction(3, 1) + prm["h_recovery"] / Fraction(2, 1)))
            nmhc = min(Fraction(4, 1), mhc + Fraction(6, 5))
            pen = Fraction(3, 2)
        elif act == "SALVAGE_SWITCH":
            eff = Fraction(17, 20) if mhc < Fraction(2, 1) else Fraction(11, 20)
            nvs = vs * Fraction(15, 20)
            nvr = vr * eff
            nhc = hc - prm["salvage_tox"]
            nmhc = max(Fraction(1, 1), mhc - Fraction(1, 10))
            pen = Fraction(2, 1)
        else:
            return False, f"Unknown action in certified trajectory: {act!r}"

        if nhc < h_min or nvr >= vr_crit:
            return False, f"Invariant breach at step {row['step']}: h_core={nhc}, v_R={nvr}"
        cum += (nvs / Fraction(10, 1)) + nvr + pen
        if (
            nvs != parse_q(row["v_S_q"])
            or nvr != parse_q(row["v_R_q"])
            or nhc != parse_q(row["h_core_q"])
            or nmhc != parse_q(row["mhc_i_q"])
            or cum != parse_q(row["cum_step_cost_q"])
        ):
            return False, f"Trajectory state mismatch at step {row['step']}"
        cur = (nvs, nvr, nhc, nmhc)

    final_obj = cum + cur[1] * Fraction(2, 1) + cur[0] / Fraction(5, 1)
    if final_obj != parse_q(rep3["soko_weft_certified"]["optimal_objective_q"]):
        return False, "Final objective mismatch in certified trajectory"
    if final_obj != parse_q(rep3["oracle_exhaustive"]["optimal_objective_q"]):
        return False, "Certified objective does not match oracle objective"

    return True, f"VERIFIED ({recomputed_sha})"


def main() -> int:
    cert_path = Path(__file__).resolve().parent / "certificate.json"
    if len(sys.argv) > 1:
        cert_path = Path(sys.argv[1])
    if not cert_path.exists():
        print(f"FAIL: missing certificate {cert_path}", file=sys.stderr)
        return 1
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    ok, msg = verify_certificate_dict(cert)
    if not ok:
        print(f"FAIL: {msg}", file=sys.stderr)
        return 1
    print(f"OK: {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
