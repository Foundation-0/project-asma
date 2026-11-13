#!/usr/bin/env python3
"""Synthetic offline verifiers bridging discrete gate/flow laws to project-asma.

Research-scaffolding verifier only:
- Ingests zero clinical or patient study data (study_data_bytes = 0, patient_data_rows = 0).
- Makes zero clinical claims or clinical decision recommendations.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
import json
import math
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ScaffoldGateState:
    walls: int
    mobile_sw: int
    reserve_mob: int
    active_hold: int
    crossed: bool
    crushed: bool


def step_scaffold_gate(
    state: ScaffoldGateState,
    action: str,
    *,
    switch_req: int = 9,
    pull_aura: int = 3,
    sticky_relaxation: bool = False,
) -> Optional[ScaffoldGateState]:
    if state.crushed or state.crossed:
        return None
    w, ms, mr, h = state.walls, state.mobile_sw, state.reserve_mob, state.active_hold
    if action == "engage_hold":
        return ScaffoldGateState(w, ms, mr, h + 1, False, False) if h < 2 else None
    if action == "lock_on_switch":
        return ScaffoldGateState(w + 1, ms - 1, mr, h, False, False) if (ms > 0 and w < switch_req) else None
    if action == "deploy_and_lock_reserve":
        return ScaffoldGateState(w + 1, ms, mr - 1, h, False, False) if (mr > 0 and w + ms < switch_req) else None
    if action == "cross_gate":
        if (w + ms + h) < switch_req:
            return None
        ms_after = max(0, ms - pull_aura)
        if sticky_relaxation or (w + ms_after) >= switch_req:
            return ScaffoldGateState(w, ms_after, mr, 0, True, False)
        return ScaffoldGateState(w, ms_after, mr, 0, False, True)
    raise ValueError(f"Unknown action: {action}")


def solve_and_audit_scaffold_gate(
    initial_walls: int,
    initial_mobile_sw: int,
    initial_reserve: int,
    *,
    switch_req: int = 9,
    pull_aura: int = 3,
    sticky_relaxation: bool = False,
) -> Dict[str, object]:
    start = ScaffoldGateState(initial_walls, initial_mobile_sw, initial_reserve, 0, False, False)
    dist: Dict[ScaffoldGateState, int] = {start: 0}
    parent: Dict[ScaffoldGateState, Tuple[ScaffoldGateState, str]] = {}
    q: deque[ScaffoldGateState] = deque([start])
    actions = ("engage_hold", "lock_on_switch", "deploy_and_lock_reserve", "cross_gate")
    best_goal: Optional[ScaffoldGateState] = None

    while q:
        cur = q.popleft()
        d = dist[cur]
        if cur.crossed and not cur.crushed and best_goal is None:
            best_goal = cur
        for act in actions:
            nxt = step_scaffold_gate(
                cur, act, switch_req=switch_req, pull_aura=pull_aura, sticky_relaxation=sticky_relaxation
            )
            if nxt is not None and nxt not in dist:
                dist[nxt] = d + 1
                parent[nxt] = (cur, act)
                q.append(nxt)

    bellman_violations = 0
    edges_audited = 0
    for u, du in dist.items():
        for act in actions:
            v = step_scaffold_gate(
                u, act, switch_req=switch_req, pull_aura=pull_aura, sticky_relaxation=sticky_relaxation
            )
            if v is not None:
                edges_audited += 1
                if dist[v] > du + 1:
                    bellman_violations += 1

    trace: List[str] = []
    if best_goal is not None:
        cur = best_goal
        while cur in parent:
            prev, act = parent[cur]
            trace.append(act)
            cur = prev
        trace.reverse()

    survives_true_gate = False
    crushed_at_step: Optional[int] = None
    if best_goal is not None:
        sim = start
        for idx, act in enumerate(trace, start=1):
            nxt = step_scaffold_gate(
                sim, act, switch_req=switch_req, pull_aura=pull_aura, sticky_relaxation=False
            )
            assert nxt is not None
            sim = nxt
            if sim.crushed:
                crushed_at_step = idx
                break
        survives_true_gate = sim.crossed and not sim.crushed

    return {
        "initial_walls": initial_walls,
        "sticky_relaxation": sticky_relaxation,
        "reachable_states": len(dist),
        "edges_audited": edges_audited,
        "bellman_violations": bellman_violations,
        "optimal_steps": dist[best_goal] if best_goal is not None else None,
        "final_walls": best_goal.walls if best_goal is not None else None,
        "optimal_trace": trace,
        "survives_true_crushing_gate": survives_true_gate,
        "crushed_at_step_on_true_gate": crushed_at_step,
    }


@dataclass(frozen=True)
class ClonalGateState:
    v_s: int
    v_r: int
    w_mhc: int
    crushed: bool


def solve_clonal_schedule(
    *,
    sticky_gate: bool,
    allow_wall_transmutation: bool,
    mhc_switch_req: int = 7,
    v_crit: int = 4,
) -> Dict[str, object]:
    start = ClonalGateState(v_s=6, v_r=2, w_mhc=1, crushed=False)
    dist: Dict[ClonalGateState, int] = {start: 0}
    parent: Dict[ClonalGateState, Tuple[ClonalGateState, str]] = {}
    q: deque[ClonalGateState] = deque([start])
    actions = ["cytotoxic_pulse"] + (
        ["lock_mhc_wall", "resensitized_clearance"] if allow_wall_transmutation else []
    )

    def step(u: ClonalGateState, act: str) -> Optional[ClonalGateState]:
        if u.crushed or (u.v_s == 0 and u.v_r == 0):
            return None
        vs, vr, wm = u.v_s, u.v_r, u.w_mhc
        if act == "cytotoxic_pulse":
            vs_n = max(0, vs - 3)
            vr_n = max(0, vr - 1) if sticky_gate and vs == 0 else vr
            wm_n = wm
        elif act == "lock_mhc_wall":
            if wm >= mhc_switch_req:
                return None
            vs_n, vr_n, wm_n = vs, vr, wm + 2
        elif act == "resensitized_clearance":
            if wm < mhc_switch_req:
                return None
            vs_n, vr_n, wm_n = max(0, vs - 3), max(0, vr - 2), wm
        else:
            return None
        if not sticky_gate and vr_n > 0 and (vs_n + wm_n) < mhc_switch_req:
            return ClonalGateState(vs_n, v_crit, wm_n, True)
        return ClonalGateState(vs_n, vr_n, wm_n, vr_n >= v_crit)

    best_goal: Optional[ClonalGateState] = None
    while q:
        cur = q.popleft()
        d = dist[cur]
        if not cur.crushed and cur.v_s == 0 and cur.v_r == 0 and best_goal is None:
            best_goal = cur
        for act in actions:
            nxt = step(cur, act)
            if nxt is not None and nxt not in dist:
                dist[nxt] = d + 1
                parent[nxt] = (cur, act)
                q.append(nxt)

    bellman_violations = 0
    edges_audited = 0
    for u, du in dist.items():
        for act in actions:
            v = step(u, act)
            if v is not None:
                edges_audited += 1
                if dist[v] > du + 1:
                    bellman_violations += 1

    trace: List[str] = []
    if best_goal is not None:
        cur = best_goal
        while cur in parent:
            prev, act = parent[cur]
            trace.append(act)
            cur = prev
        trace.reverse()

    return {
        "sticky_gate": sticky_gate,
        "allow_wall_transmutation": allow_wall_transmutation,
        "reachable_states": len(dist),
        "edges_audited": edges_audited,
        "bellman_violations": bellman_violations,
        "optimal_steps": dist[best_goal] if best_goal is not None else None,
        "optimal_trace": trace,
    }


def _dinic_bipartite_unit(num_left: int, num_right: int, edges: List[Tuple[int, int]]) -> int:
    sink = num_left + num_right + 1
    adj: List[List[List[int]]] = [[] for _ in range(sink + 1)]

    def add_edge(u: int, v: int, cap: int) -> None:
        adj[u].append([v, cap, len(adj[v])])
        adj[v].append([u, 0, len(adj[u]) - 1])

    for i in range(num_left):
        add_edge(0, 1 + i, 1)
    for j in range(num_right):
        add_edge(1 + num_left + j, sink, 1)
    for i, j in edges:
        add_edge(1 + i, 1 + num_left + j, 1)

    flow = 0
    while True:
        level = [-1] * (sink + 1)
        level[0] = 0
        q = deque([0])
        while q:
            u = q.popleft()
            for v, cap, _ in adj[u]:
                if cap > 0 and level[v] < 0:
                    level[v] = level[u] + 1
                    q.append(v)
        if level[sink] < 0:
            break
        it = [0] * (sink + 1)

        def dfs(u: int, pushed: int) -> int:
            if pushed == 0 or u == sink:
                return pushed
            while it[u] < len(adj[u]):
                idx = it[u]
                v, cap, rev = adj[u][idx]
                if cap > 0 and level[v] == level[u] + 1:
                    tr = dfs(v, min(pushed, cap))
                    if tr > 0:
                        adj[u][idx][1] -= tr
                        adj[v][rev][1] += tr
                        return tr
                it[u] += 1
            return 0

        while True:
            p = dfs(0, 10**9)
            if p == 0:
                break
            flow += p
    return flow


def evaluate_ms2_static_vs_causal() -> Dict[str, object]:
    res_true = [113, 128, 147, 115, 129, 174]
    res_swap = [113, 128, 115, 147, 129, 174]
    proton, water = 1, 18

    def build_ions(residues: List[int]) -> List[Tuple[str, int, int, bool]]:
        ions: List[Tuple[str, int, int, bool]] = []
        ln, total = len(residues), sum(residues)
        for k in range(1, ln):
            ions.append((f"b{k}", k, sum(residues[:k]) + proton, False))
            ions.append((f"y{ln-k}", k, total - sum(residues[:k]) + proton, False))
        ions.append(("b3-H2O", 3, sum(residues[:3]) + proton - water, True))
        return ions

    true_ions = build_ions(res_true)
    swap_ions = build_ions(res_swap)
    observed_peaks: List[Tuple[int, bool]] = [(mz, True) for _, _, mz, _ in true_ions]
    observed_peaks.extend([(357, False), (451, False), (339, True)])
    m_plus_2h = sum(res_true) + 2 * proton

    def score(ions: List[Tuple[str, int, int, bool]]) -> Dict[str, object]:
        static_edges = [
            (i, j) for i, (_, _, mu, _) in enumerate(ions) for j, (mz, _) in enumerate(observed_peaks) if mz == mu
        ]
        static_flow = _dinic_bipartite_unit(len(ions), len(observed_peaks), static_edges)
        intact_peaks = [(idx, mz) for idx, (mz, intact) in enumerate(observed_peaks) if intact]
        conserved_rungs = set()
        for k in range(1, 6):
            b_mu = [mu for lbl, rk, mu, loss in ions if rk == k and not loss and lbl.startswith("b")][0]
            y_mu = [mu for lbl, rk, mu, loss in ions if rk == k and not loss and lbl.startswith("y")][0]
            b_hits = [idx for idx, mz in intact_peaks if mz == b_mu]
            y_hits = [idx for idx, mz in intact_peaks if mz == y_mu]
            for bi in b_hits:
                for yi in y_hits:
                    if bi != yi and (observed_peaks[bi][0] + observed_peaks[yi][0]) == m_plus_2h:
                        conserved_rungs.add(k)

        causal_edges: List[Tuple[int, int]] = []
        cnf_blocked = 0
        for i, (_, rk, mu, is_loss) in enumerate(ions):
            if is_loss and rk not in conserved_rungs:
                if any(mz == mu for _, mz in intact_peaks):
                    cnf_blocked += 1
                continue
            for j, mz in intact_peaks:
                if mz == mu:
                    causal_edges.append((i, j))

        return {
            "total_theoretical_ions": len(ions),
            "static_p01_flow": static_flow,
            "conserved_backbone_rungs": sorted(conserved_rungs),
            "cnf_blocked_orphan_losses": cnf_blocked,
            "causal_p01_plus_flow": _dinic_bipartite_unit(len(ions), len(observed_peaks), causal_edges),
            "diagnostic_rung_3_conserved": 3 in conserved_rungs,
        }

    return {
        "intensity_bytes_retained": 0,
        "true_target_candidate": score(true_ions),
        "dipeptide_swap_chimera_decoy": score(swap_ions),
    }


def q_total_resistant(p: Fraction, r: Fraction, c: Fraction) -> Fraction:
    return (r * p + c * (1 - p)) / (r * p + (1 - p))


def u_newly_converted(p: Fraction, r: Fraction, c: Fraction) -> Fraction:
    return (c * (1 - p)) / (r * p + (1 - p))


def lh_contrast_eps_star(p_low: Fraction, p_high: Fraction, r_c: Fraction, c_val: Fraction) -> Fraction:
    d_low = q_total_resistant(p_low, r_c, c_val) - q_total_resistant(p_low, Fraction(16, 1), Fraction(0, 1))
    d_high = q_total_resistant(p_high, Fraction(16, 1), Fraction(0, 1)) - q_total_resistant(p_high, r_c, c_val)
    return (d_low + d_high) / 4


def verify_floating_rs_continuum_impossibility() -> Dict[str, object]:
    lh_legacy_c25 = lh_contrast_eps_star(Fraction(1, 10), Fraction(2, 5), Fraction(11, 1), Fraction(1, 4))
    lh_legacy_c50 = lh_contrast_eps_star(Fraction(1, 10), Fraction(2, 5), Fraction(6, 1), Fraction(1, 2))
    lh_opt_c25 = lh_contrast_eps_star(Fraction(1, 20), Fraction(3, 8), Fraction(11, 1), Fraction(1, 4))
    lh_opt_c50 = lh_contrast_eps_star(Fraction(1, 20), Fraction(3, 8), Fraction(6, 1), Fraction(1, 2))

    factorization_ok = True
    for num in range(1, 21):
        p = Fraction(num, 20)
        lhs = q_total_resistant(p, Fraction(19, 1), Fraction(0, 1)) - q_total_resistant(
            p, Fraction(11, 1), Fraction(1, 4)
        )
        rhs = (14 * p - 1) * (1 - p) / (4 * (18 * p + 1) * (10 * p + 1))
        if lhs != rhs or abs(lhs) / 2 >= Fraction(1, 60):
            factorization_ok = False

    discriminant = (-169) * (-169) - 4 * 570 * 17
    edge_at_1_20 = abs(
        q_total_resistant(Fraction(1, 20), Fraction(19, 1), Fraction(0, 1))
        - q_total_resistant(Fraction(1, 20), Fraction(11, 1), Fraction(1, 4))
    ) / 2

    p_fail, p_pass = Fraction(1, 25), Fraction(1, 26)
    quad_1_25 = 125 * p_fail * p_fail + 328 * p_fail - 13
    quad_1_26 = 125 * p_pass * p_pass + 328 * p_pass - 13

    def curve_minimax_with_anchor(p_low: Fraction) -> float:
        k1, k0 = float(p_low / (1 - p_low)), 0.25
        y1, y0 = float(q_total_resistant(p_low, Fraction(11, 1), Fraction(1, 4))), 0.8
        s_val = y1 + y0
        a_c, b_c, c_c = (2.0 - s_val) * k1 * k0, (1.0 - s_val) * (k1 + k0), -s_val
        rs_star = (-b_c + math.sqrt(b_c * b_c - 4.0 * a_c * c_c)) / (2.0 * a_c)
        return round((y1 - (k1 * rs_star / (k1 * rs_star + 1.0))) / 2.0, 6)

    two_ch_margin = u_newly_converted(Fraction(1, 20), Fraction(11, 1), Fraction(1, 4)) / 2
    return {
        "pinned_s16_lh_bounds": {
            "legacy_1_10_2_5_C25": f"{lh_legacy_c25.numerator}/{lh_legacy_c25.denominator}",
            "legacy_1_10_2_5_C50": f"{lh_legacy_c50.numerator}/{lh_legacy_c50.denominator}",
            "optimal_1_20_3_8_C25": f"{lh_opt_c25.numerator}/{lh_opt_c25.denominator}",
            "optimal_1_20_3_8_C50": f"{lh_opt_c50.numerator}/{lh_opt_c50.denominator}",
        },
        "floating_rs_impossibility_on_1_20_to_1": {
            "witness_r_S": 19,
            "algebraic_factorization_verified": factorization_ok,
            "edge_eps_at_1_20": f"{edge_at_1_20.numerator}/{edge_at_1_20.denominator}",
            "positivity_quadratic_discriminant": discriminant,
            "continuum_sup_strictly_below_1_over_60": discriminant < 0 and edge_at_1_20 < Fraction(1, 60),
        },
        "cure_a_single_channel_threshold_with_p0_1_5": {
            "at_p_1_25_quadratic_val": f"{quad_1_25.numerator}/{quad_1_25.denominator}",
            "at_p_1_25_eps_star": curve_minimax_with_anchor(p_fail),
            "at_p_1_26_quadratic_val": f"{quad_1_26.numerator}/{quad_1_26.denominator}",
            "at_p_1_26_eps_star": curve_minimax_with_anchor(p_pass),
        },
        "cure_b_two_channel_farkas_at_p_1_20": {
            "rs_invariant_eps_star_fraction": f"{two_ch_margin.numerator}/{two_ch_margin.denominator}",
            "ratio_vs_1_over_60_ceiling": round(float(two_ch_margin / Fraction(1, 60)), 4),
        },
    }


def build_full_certificate() -> Dict[str, object]:
    return {
        "schema_version": "1.1.0",
        "scope": "synthetic_offline_research_scaffolding_only",
        "study_data_bytes": 0,
        "patient_data_rows": 0,
        "unlock_1_crushing_gate_phase_transition": {
            "low_wall_w2_sticky_mirage": solve_and_audit_scaffold_gate(2, 5, 2, sticky_relaxation=True),
            "low_wall_w2_true_crushing_gate": solve_and_audit_scaffold_gate(2, 5, 2, sticky_relaxation=False),
            "high_wall_w8_true_crushing_gate": solve_and_audit_scaffold_gate(8, 1, 0, sticky_relaxation=False),
            "clonal_schedule_sticky_monotherapy_mirage": solve_clonal_schedule(
                sticky_gate=True, allow_wall_transmutation=False
            ),
            "clonal_schedule_true_monotherapy_unsat": solve_clonal_schedule(
                sticky_gate=False, allow_wall_transmutation=False
            ),
            "clonal_schedule_true_with_wall_transmutation": solve_clonal_schedule(
                sticky_gate=False, allow_wall_transmutation=True
            ),
        },
        "unlock_2_ms2_causal_rung_and_cnf": evaluate_ms2_static_vs_causal(),
        "unlock_3_floating_rs_impossibility_and_farkas_cures": verify_floating_rs_continuum_impossibility(),
    }


if __name__ == "__main__":
    print(json.dumps(build_full_certificate(), indent=2, sort_keys=True))
