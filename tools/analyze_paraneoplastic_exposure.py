"""Exact synthetic experiment: what neural injury records about tumor antigen.

Every quantity is an invented arbitrary unit. Python standard library only; no
network, study values, patient records, random numbers or third-party code.
This is not a model of any person, a treatment selector or a clinical claim.
See docs/research/paraneoplastic-exposure-observability.md for assumptions.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = "docs/research/paraneoplastic-exposure-observability.md"
OUTPUT = "registries/paraneoplastic-exposure-results.json"


def rational(value, name="value"):
    if isinstance(value, bool) or not isinstance(value, (int, F)) or value < 0:
        raise ValueError(f"{name} must be a nonnegative exact rational")
    return F(value)


def retention(value, name="retention"):
    value = rational(value, name)
    if value > 1:
        raise ValueError(f"{name} must not exceed one")
    return value


# --- A. Antigen exposure along a schedule of commuting operations -----------

def run_schedule(initial, operations, intervals=None):
    """Apply instantaneous operations, each followed by a holding interval.

    operations: sequence of ("surgery"|"chemo", retained fraction). Burden is
    constant between operations (no growth or decay: the commuting null case).
    Surgery removes burden from the body; chemotherapy kills it in place.
    """
    burden = rational(initial, "initial burden")
    operations = tuple(operations)
    intervals = tuple(F(1) for _ in operations) if intervals is None else tuple(intervals)
    if not operations or len(intervals) != len(operations) or any(rational(d) <= 0 for d in intervals):
        raise ValueError("need one positive holding interval per operation")
    steps, burden_auc, killed, removed = [], F(0), F(0), F(0)
    for (kind, keep), interval in zip(operations, intervals):
        keep = retention(keep)
        if kind == "surgery":
            removed += (1 - keep) * burden
        elif kind == "chemo":
            killed += (1 - keep) * burden
        else:
            raise ValueError("operation must be surgery or chemo")
        before, burden = burden, keep * burden
        burden_auc += burden * F(interval)
        steps.append({"operation": kind, "before": before, "after": burden,
                      "released_in_body": (before - burden) if kind == "chemo" else F(0)})
    return {"final": burden, "burden_auc": burden_auc, "killed_in_body": killed,
            "removed_surgically": removed, "steps": steps}


def surgery_position_sweep(initial, surgery_keep, chemo_keep, cycles):
    """Exposure for every surgery position among identical chemotherapy cycles."""
    rows = []
    for position in range(cycles + 1):
        ops = [("chemo", chemo_keep)] * cycles
        ops.insert(position, ("surgery", surgery_keep))
        result = run_schedule(initial, ops)
        rows.append({"surgery_position": position, **{k: result[k] for k in
                     ("final", "burden_auc", "killed_in_body", "removed_surgically")}})
    return rows


def effector_sums(drive, retain, alpha, initial_effector=F(0)):
    """Exact discrete effector E[k+1] = r E[k] + alpha u[k]; return sums.

    The window sum of E[0..n-1] plus the geometric tail after drive stops
    equals (E[0] + alpha * sum(u)) / (1 - r): the discrete exposure identity.
    """
    r, alpha = retention(retain, "effector retention"), rational(alpha, "alpha")
    if r == 1:
        raise ValueError("effector must decay")
    effector, window = rational(initial_effector, "initial effector"), F(0)
    for u in drive:
        window += effector
        effector = r * effector + alpha * rational(u, "drive")
    tail = effector / (1 - r)
    return {"window_sum": window, "end_effector": effector, "tail_sum": tail,
            "total_sum": window + tail,
            "identity_total": (rational(initial_effector) + alpha * sum(map(F, drive))) / (1 - r)}


def compare_orders(initial, surgery_keep, chemo_keep, cycles, early, late, retain, alpha, kappa):
    """Two orders of the same operations: equal tumor endpoint, unequal neural exposure."""
    sweep = surgery_position_sweep(initial, surgery_keep, chemo_keep, cycles)
    first, second = sweep[early], sweep[late]
    out = {"tumor_endpoint_equal": first["final"] == second["final"], "final_burden": first["final"]}
    for label, key in (("burden_driven", "burden_auc"), ("death_driven", "killed_in_body")):
        drives = []
        for position in (early, late):
            ops = [("chemo", chemo_keep)] * cycles
            ops.insert(position, ("surgery", surgery_keep))
            steps = run_schedule(initial, ops)["steps"]
            drives.append([s["after"] if label == "burden_driven" else s["released_in_body"] for s in steps])
        sums = [effector_sums(d, retain, alpha) for d in drives]
        for s in sums:
            if s["total_sum"] != s["identity_total"]:
                raise AssertionError("discrete exposure identity failed")
        difference = kappa * (sums[1]["total_sum"] - sums[0]["total_sum"])
        predicted = kappa * alpha * (second[key] - first[key]) / (1 - retain)
        out[label] = {"exposure_early": first[key], "exposure_late": second[key],
                      "cumulative_hazard_difference_late_minus_early": difference,
                      "predicted_kappa_alpha_delta_exposure_over_1_minus_r": predicted,
                      "identity_holds": difference == predicted}
    return out


def ascending_order_minimizes(retentions, intervals):
    """Brute-force exchange check: most-effective-first minimizes burden AUC."""
    best = None
    for order in set(permutations(retentions)):
        auc = run_schedule(F(100), [("chemo", r) for r in order], intervals)["burden_auc"]
        best = auc if best is None or auc < best else best
    ascending = run_schedule(F(100), [("chemo", r) for r in sorted(retentions)], intervals)["burden_auc"]
    return ascending == best


# --- B. State versus rate ----------------------------------------------------

def marker_at(losses, sample_step, decay):
    """Injury-rate marker: each loss decays by `decay` per later step."""
    decay = retention(decay, "marker retention")
    return sum(F(loss) * decay ** (sample_step - step) for step, loss in losses if step <= sample_step)


def deficit_at(losses, sample_step):
    return sum(F(loss) for step, loss in losses if step <= sample_step)


# --- D. Antigen-driven versus autonomous injury after antigen removal --------

def regime_trajectory(drive, steps_after, retain, alpha, kappa, seed_rate, autonomous_keep, kappa_cns):
    """Exact discrete trajectory: loss per step = N * (kappa*E + kappa_cns*C).

    E is antigen-driven and decays by `retain`; C is CNS-resident effector seeded
    by E and retained by `autonomous_keep` (1 = self-sustaining, 0 = absent).
    Drive is followed by `steps_after` steps with zero antigen.
    """
    effector, cns, neurons = F(0), F(0), F(1)
    losses, hazards, effector_at_removal = [], [], None
    for step, u in enumerate(list(drive) + [F(0)] * steps_after):
        if step == len(drive):
            effector_at_removal = effector
        hazard = kappa * effector + kappa_cns * cns
        if hazard > 1:
            raise ValueError("per-step hazard exceeds one; reduce kappa")
        loss = neurons * hazard
        losses.append(loss)
        hazards.append(hazard)
        neurons -= loss
        effector, cns = retain * effector + alpha * F(u), autonomous_keep * cns + seed_rate * effector
    return {"losses": losses, "hazards": hazards, "remaining": neurons,
            "effector_at_removal": effector_at_removal, "final_effector": effector, "final_cns": cns}


def presentation_hazards(initial, operations, turnover, release, retain, alpha, kappa):
    """Hazard before and after each operation, starting at the pre-treatment steady state.

    Drive = turnover * burden (spontaneous in-body death, proportional to burden)
    plus, if `release`, the burden killed in the body by chemotherapy. Burden-driven
    presentation is release=False; death-driven presentation is release=True.
    """
    turnover, r = retention(turnover, "turnover"), retention(retain, "effector retention")
    effector = alpha * turnover * F(initial) / (1 - r)
    hazards = [kappa * effector]
    for s in run_schedule(initial, operations)["steps"]:
        drive = turnover * s["after"] + (s["released_in_body"] if release else F(0))
        effector = r * effector + alpha * drive
        hazards.append(kappa * effector)
    return hazards


def approx(value):
    return format(float(value), ".6g")


def text(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {k: text(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [text(v) for v in value]
    return value


def build_result():
    # A1. Worked comparison: surgery first versus three cycles, surgery, three cycles.
    worked = {}
    for name, q in (("effective_surgery", F(1, 10)), ("less_effective_surgery", F(3, 4))):
        worked[name] = {"surgery_keep": q, "chemo_keep": F(1, 2), **compare_orders(
            F(100), q, F(1, 2), 6, early=0, late=3, retain=F(1, 2), alpha=F(1), kappa=F(1, 100))}

    # A2. Grid of surgery positions: endpoint invariance and the two optimal orders.
    grid, disagreements = [], 0
    qs = (F(1, 100), F(1, 10), F(1, 4), F(1, 2), F(3, 4), F(1))
    chemo = (F(1, 10), F(1, 4), F(1, 2), F(3, 4), F(9, 10))
    for q, a in product(qs, chemo):
        sweep = surgery_position_sweep(F(100), q, a, 6)
        finals = {row["final"] for row in sweep}
        burden = [row["burden_auc"] for row in sweep]
        death = [row["killed_in_body"] for row in sweep]
        balance = all(row["killed_in_body"] == 100 - row["final"] - row["removed_surgically"] for row in sweep)
        steps_ok = all(burden[p + 1] - burden[p] == 100 * a ** p * (a - q) for p in range(6))
        best_b = [p for p, v in enumerate(burden) if v == min(burden)]
        best_d = [p for p, v in enumerate(death) if v == min(death)]
        disagree = best_b[0] != 0 and best_d == [0]
        disagreements += disagree
        grid.append({"surgery_keep": q, "chemo_keep": a, "endpoint_invariant": len(finals) == 1,
                     "mass_balance_holds": balance, "adjacent_step_formula_holds": steps_ok,
                     "burden_driven_best_positions": best_b, "death_driven_best_positions": best_d,
                     "hypotheses_disagree_on_best_position": disagree})

    exchange_cases = [((F(1, 10), F(1, 4), F(1, 2), F(3, 4)), (F(1),) * 4),
                      ((F(1, 10), F(1, 4), F(1, 2), F(3, 4)), (F(3), F(1), F(2), F(1, 2))),
                      ((F(1, 5), F(1, 5), F(2, 3), F(9, 10)), (F(1, 3), F(4), F(1), F(2)))]
    exchange = [{"retentions": r, "intervals": d, "ascending_is_minimum": ascending_order_minimizes(r, d)}
                for r, d in exchange_cases]

    # B1. Two visits, identical deficits; attack ended early versus continuing.
    ended = [(1, F(3, 10))]
    ongoing = [(s, F(3, 40)) for s in (1, 2, 3, 4)]
    state_rate = {
        "visits": [0, 4], "marker_retention_per_step": F(1, 2),
        "deficit_at_visits_ended": [deficit_at(ended, v) for v in (0, 4)],
        "deficit_at_visits_ongoing": [deficit_at(ongoing, v) for v in (0, 4)],
        "marker_at_second_visit_ended": marker_at(ended, 4, F(1, 2)),
        "marker_at_second_visit_ongoing": marker_at(ongoing, 4, F(1, 2)),
    }
    state_rate["marker_ratio_ongoing_to_ended"] = (state_rate["marker_at_second_visit_ongoing"]
                                                   / state_rate["marker_at_second_visit_ended"])
    # B2. Equal injury rate, different attack intensity (rate / remaining target).
    intensity = [{"remaining_fraction": n, "per_capita_hazard": p, "loss_rate": n * p}
                 for n, p in ((F(9, 10), F(1, 90)), (F(1, 20), F(1, 5)))]

    # C. Aggregate tumor marker versus antigen drive across two lesions.
    w, v = (F(1), F(1)), (F(1), F(3))
    before, after = (F(10), F(2)), (F(4), F(5))
    dot = lambda x, y: sum(a * b for a, b in zip(x, y))
    marker_case = {"marker_weights": w, "drive_weights": v, "lesions_before": before, "lesions_after": after,
                   "marker_before": dot(w, before), "marker_after": dot(w, after),
                   "drive_before": dot(v, before), "drive_after": dot(v, after)}
    vectors = [x for x in product(range(4), repeat=2) if any(x)]
    deltas = list(product(range(-3, 4), repeat=2))
    iff_ok = True
    for wv, vv in product(vectors, vectors):
        if wv[0] * vv[1] != wv[1] * vv[0]:
            # Witness from the proof: strict Cauchy-Schwarz for non-parallel vectors.
            vw, ww, vvv = dot(vv, wv), dot(wv, wv), dot(vv, vv)
            witness = tuple((vw + ww) * b - (vw + vvv) * a for a, b in zip(wv, vv))
            iff_ok &= dot(wv, witness) < 0 < dot(vv, witness)
        else:
            # Positive multiple: the two weighted changes always share a sign.
            iff_ok &= all((dot(wv, d) > 0) == (dot(vv, d) > 0) and (dot(wv, d) < 0) == (dot(vv, d) < 0)
                          for d in deltas)

    # D1. Regimes after complete antigen removal (drive stops after three steps).
    drive = [F(4), F(4), F(4)]
    regimes = {}
    for name, keep in (("antigen_driven", F(0)), ("autonomous_cns", F(1))):
        t = regime_trajectory(drive, 9, F(1, 2), F(1), F(1, 100), F(1, 4) if keep else F(0), keep, F(1, 200))
        after = t["losses"][len(drive):]
        hazards_after = t["hazards"][len(drive):]
        row = {"loss_per_step_after_removal": after,
               "loss_per_step_after_removal_approx": [approx(x) for x in after],
               "late_to_early_loss_ratio": after[-1] / after[1],
               "late_to_early_loss_ratio_approx": approx(after[-1] / after[1]),
               "remaining_fraction_at_end_approx": approx(t["remaining"])}
        if name == "antigen_driven":
            tail = F(1, 100) * t["final_effector"] / (1 - F(1, 2))
            bound = F(1, 100) * t["effector_at_removal"] / (1 - F(1, 2))
            row["effector_at_removal"] = t["effector_at_removal"]
            row["committed_hazard_bound"] = bound
            row["observed_hazard_after_removal_plus_exact_tail"] = sum(hazards_after) + tail
            row["committed_bound_exact"] = sum(hazards_after) + tail == bound
        regimes[name] = row

    # D2. No-rise theorem and chemotherapy-cycle signature from steady state.
    signature = {"cases": 0, "burden_driven_never_rises": 0, "death_driven_rises_after_surgery": 0,
                 "chemo_first_cases": 0, "death_driven_rises_after_first_chemo_from_steady_state": 0,
                 "surgery_first_cases": 0, "death_driven_rises_after_first_chemo_following_surgery": 0}
    for q, a, d, position in product((F(1, 10), F(1, 2), F(3, 4)), (F(1, 4), F(1, 2), F(3, 4)),
                                     (F(1, 20), F(1, 5)), range(4)):
        ops = [("chemo", a)] * 3
        ops.insert(position, ("surgery", q))
        burden_h = presentation_hazards(F(100), ops, d, False, F(1, 2), F(1, 25), F(1, 100))
        death_h = presentation_hazards(F(100), ops, d, True, F(1, 2), F(1, 25), F(1, 100))
        first_chemo = next(i for i, (kind, _) in enumerate(ops) if kind == "chemo")
        signature["cases"] += 1
        signature["burden_driven_never_rises"] += all(y <= x for x, y in zip(burden_h, burden_h[1:]))
        rose = death_h[first_chemo + 1] > death_h[first_chemo]
        if position == 0:
            signature["surgery_first_cases"] += 1
            signature["death_driven_rises_after_first_chemo_following_surgery"] += rose
        else:
            signature["chemo_first_cases"] += 1
            signature["death_driven_rises_after_first_chemo_from_steady_state"] += rose
        signature["death_driven_rises_after_surgery"] += death_h[position + 1] > death_h[position]
    example_ops = [("surgery", F(1, 2)), ("chemo", F(1, 2)), ("chemo", F(1, 2))]
    signature["example_operations"] = [k for k, _ in example_ops]
    signature["example_burden_driven_hazards"] = presentation_hazards(
        F(100), example_ops, F(1, 10), False, F(1, 2), F(1, 25), F(1, 100))
    signature["example_death_driven_hazards"] = presentation_hazards(
        F(100), example_ops, F(1, 10), True, F(1, 2), F(1, 25), F(1, 100))

    # A3. Mixed presentation: turnover d times burden AUC plus in-body release.
    mixture = {"cases": 0, "best_position_is_first_or_last": 0, "criterion_predicts_first": 0}
    for q, a, d in product(qs, chemo, (F(0), F(1, 20), F(1, 5), F(1), F(5))):
        sweep = surgery_position_sweep(F(100), q, a, 6)
        values = [d * row["burden_auc"] + row["killed_in_body"] for row in sweep]
        best = [p for p, v in enumerate(values) if v == min(values)]
        criterion = d * (a - q) + (1 - q) * (1 - a)
        mixture["cases"] += 1
        mixture["best_position_is_first_or_last"] += best[0] in (0, 6) or len(best) == 7
        mixture["criterion_predicts_first"] += (best[0] == 0) == (criterion >= 0)

    return {
        "schema_version": 1,
        "status": "executed_synthetic_exact_arithmetic_not_study_analysis",
        "document": DOC,
        "implementation": "tools/analyze_paraneoplastic_exposure.py",
        "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "units": "invented_arbitrary_units", "randomness": "none",
        "study_data_or_patient_records_used": False,
        "A_worked_order_comparison": text(worked),
        "A_surgery_position_grid": {
            "cases": len(grid), "endpoint_invariant": sum(c["endpoint_invariant"] for c in grid),
            "mass_balance_holds": sum(c["mass_balance_holds"] for c in grid),
            "adjacent_step_formula_holds": sum(c["adjacent_step_formula_holds"] for c in grid),
            "hypotheses_disagree_on_best_position": disagreements, "rows": text(grid)},
        "A_exchange_checks": text(exchange),
        "B_state_versus_rate": text(state_rate),
        "B_intensity_needs_state_and_rate": text(intensity),
        "C_aggregate_marker_counterexample": text(marker_case),
        "C_opposed_sign_iff_not_nonnegative_multiple_on_grid": iff_ok,
        "A_mixed_presentation_criterion": text(mixture),
        "D_regimes_after_antigen_removal": text(regimes),
        "D_steady_state_signature": text(signature),
        "unsupported_claims": [
            "any patient's mechanism, course or treatment choice",
            "that either antigen-presentation hypothesis is true",
            "that neurofilament light is validated for anti-Yo disease",
            "clinical benefit of any sequence, timing or immunotherapy",
            "parameter values for tumor, effector, neuron or marker kinetics"],
    }


if __name__ == "__main__":
    print(json.dumps(build_result(), indent=2, sort_keys=True))
