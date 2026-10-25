#!/usr/bin/env python3
"""Declared reconstruction contracts for Pilot 001; Python standard library only.

These functions fix the parts of the prospective discovery reconstruction that
the author sources leave unavailable or unverified: patient-grouped, stratified
fold assignment replacing the absent ``balanced_folds.R``; exact panel-row
location and order; replicate collapse by explicit sample key; strict held-out
prediction coverage; exact two-stage score averaging; and the AUROC definition
shared with the executed published-score check. They consume abstract tokens in
tests or private in-memory records in an authorized run. Nothing here reads
abundance files, fits a model or uses the network. Equivalence to the original
author procedure is not claimed; see docs/pilot-001-reconstruction-decisions.md.
"""

import argparse
import collections
import hashlib
import json
import platform
import re
import sys
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path

import verify_published_auc as verify


ROOT = Path(__file__).resolve().parents[1]
DECISION_RECORD = "docs/pilot-001-reconstruction-decisions.md"
RECONSTRUCTION_CONTRACT = "protocols/pilot-001-independent-reconstruction.md"
FOLDS = 5
REPETITIONS = tuple(range(1, 101))
MODELS = ("elastic_net", "xgboost", "random_forest")
POSITIVE = verify.POSITIVE
NEGATIVE = verify.NEGATIVE
EXPECTED_COHORT = {"patients": 135, "positives": 52, "negatives": 83}
PANEL_SIZE = 64
NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")
FAILURE_MESSAGE = "ERROR: reconstruction contract check failed; no row-level details emitted."


class ContractError(ValueError):
    """A violated declared contract; messages never carry record values."""


def require(condition, message):
    if not condition:
        raise ContractError(message)


def token(value):
    """An explicit, nonempty, untrimmed key; never NA and never positional."""
    return isinstance(value, str) and bool(value) and value == value.strip() and value != "NA"


def number(value):
    """Parse an exact decimal string; never coerce floats, trim or impute."""
    require(isinstance(value, str) and NUMBER.fullmatch(value) is not None, "Malformed numeric value")
    try:
        parsed = Decimal(value)
    except InvalidOperation:
        raise ContractError("Malformed numeric value") from None
    require(parsed.is_finite(), "Nonfinite numeric value")
    return Fraction(parsed)


def fingerprint(values):
    """SHA-256 of ordered text values, LF after every value, for freeze records."""
    require(isinstance(values, (list, tuple)) and all(isinstance(value, str) for value in values),
            "Fingerprint input must be text values")
    return hashlib.sha256("".join(f"{value}\n" for value in values).encode("utf-8")).hexdigest()


def patient_labels(measurements):
    """Group measurement entries by explicit patient key with one consistent label.

    ``measurements`` holds (measurement_key, patient_key, label) entries. The
    result maps each patient to its label and reports measurements per patient,
    so every patient can receive one fold and never straddle training and test.
    """
    labels, sizes, seen = {}, collections.Counter(), set()
    for entry in measurements:
        require(isinstance(entry, (tuple, list)) and len(entry) == 3, "Malformed measurement entry")
        measurement, patient, label = entry
        require(token(measurement) and token(patient), "Missing measurement or patient key")
        require(label in (POSITIVE, NEGATIVE), "Unexpected response label")
        require(measurement not in seen, "Duplicate measurement key")
        seen.add(measurement)
        require(labels.setdefault(patient, label) == label, "Conflicting labels within one patient")
        sizes[patient] += 1
    require(labels, "No measurements")
    return labels, dict(sizes)


def ordering_key(seed, value):
    """Deterministic pseudo-random order, reproducible in any language via SHA-256."""
    return hashlib.sha256(f"{seed}\x1f{value}".encode("utf-8")).hexdigest()


def assign_folds(labels, seed, folds=FOLDS):
    """Assign one fold per patient, stratified by response, for one repetition.

    This replaces the unavailable ``balanced.folds.vec`` helper with a declared
    convention: within each class, patients are ordered by the SHA-256 of the
    repetition seed and patient key, then dealt round-robin from a seed-derived
    starting fold. Each fold's count of every class is within one of every
    other fold's. The original fold assignments are not recovered.
    """
    require(type(seed) is int and seed >= 1, "Repetition seed must be a positive integer")
    require(type(folds) is int and folds >= 2, "Fold count must be an integer of at least 2")
    require(isinstance(labels, dict) and bool(labels), "Missing patient labels")
    require(all(token(key) for key in labels), "Missing patient key")
    require(all(label in (POSITIVE, NEGATIVE) for label in labels.values()), "Unexpected response label")
    assignment = {}
    for label in (POSITIVE, NEGATIVE):
        members = sorted((key for key, value in labels.items() if value == label),
                         key=lambda key: (ordering_key(seed, key), key))
        require(len(members) >= folds, "A class has fewer patients than folds")
        start = int(ordering_key(seed, label), 16) % folds
        for position, key in enumerate(members):
            assignment[key] = (position + start) % folds + 1
    for fold in range(1, folds + 1):
        held_out = {labels[key] for key, value in assignment.items() if value == fold}
        require(held_out == {POSITIVE, NEGATIVE}, "Class-empty fold")
    return assignment


def panel_rows(symbols, panel):
    """Locate each fixed panel symbol exactly once by whole-string equality.

    Returns matrix row positions in matrix order, mirroring the author script's
    ``which(rownames(...) %in% panel)`` selection; the symbols at those
    positions form the declared, fingerprintable feature order. No trimming,
    case folding, alias substitution or protein-group interpretation occurs.
    """
    require(isinstance(panel, (list, tuple)) and bool(panel) and all(token(symbol) for symbol in panel),
            "Malformed panel")
    require(len(set(panel)) == len(panel), "Duplicate panel symbol")
    require(isinstance(symbols, (list, tuple)) and all(isinstance(symbol, str) for symbol in symbols),
            "Malformed symbol list")
    index = collections.defaultdict(list)
    for position, symbol in enumerate(symbols):
        index[symbol].append(position)
    require(all(len(index[symbol]) == 1 for symbol in panel), "Missing or multiply matched panel symbol")
    return sorted(index[symbol][0] for symbol in panel)


def collapse_measurements(sample_of, values):
    """Average replicate measurement columns per explicit sample key, exactly.

    ``sample_of`` maps each measurement column to its explicit sample key and
    ``values`` maps each column to its feature values as decimal strings in one
    shared feature order. Every value must be present: there is no ``na.rm``
    behaviour. Returns ``{sample_key: [Fraction, ...]}`` and group-size counts.
    """
    require(isinstance(sample_of, dict) and bool(sample_of) and
            all(token(column) and token(sample) for column, sample in sample_of.items()),
            "Malformed column-to-sample map")
    require(isinstance(values, dict) and set(values) == set(sample_of), "Values do not match the declared columns")
    require(all(isinstance(column, (list, tuple)) and bool(column) for column in values.values()),
            "Empty or malformed feature values")
    require(len({len(column) for column in values.values()}) == 1, "Unequal feature counts across columns")
    groups = collections.defaultdict(list)
    for column, sample in sample_of.items():
        groups[sample].append(column)
    collapsed = {}
    for sample, columns in groups.items():
        parsed = [[number(value) for value in values[column]] for column in sorted(columns)]
        collapsed[sample] = [sum(row) / len(columns) for row in zip(*parsed)]
    sizes = collections.Counter(len(columns) for columns in groups.values())
    return collapsed, {"samples": len(groups), "columns": len(sample_of),
                       "group_sizes": {str(size): count for size, count in sorted(sizes.items())}}


def aggregate_predictions(records, assignments, labels, models=MODELS, repetitions=REPETITIONS):
    """Average held-out probabilities within each repetition, then across repetitions.

    ``records`` holds mappings with ``repetition``, ``fold``, ``model``,
    ``patient`` and ``probability`` (a decimal string in [0, 1]);
    ``assignments`` maps each repetition to its patient-to-fold assignment.
    Every patient needs exactly one held-out prediction per model per
    repetition. Nothing is skipped, imputed or averaged over missing values.
    """
    require(isinstance(labels, dict) and bool(labels) and all(token(key) for key in labels), "Missing patient labels")
    require(all(label in (POSITIVE, NEGATIVE) for label in labels.values()), "Unexpected response label")
    require(isinstance(models, tuple) and bool(models) and len(set(models)) == len(models), "Malformed model list")
    declared = tuple(repetitions)
    require(bool(declared) and len(set(declared)) == len(declared) and
            all(type(repetition) is int for repetition in declared), "Malformed repetition list")
    require(isinstance(assignments, dict) and set(assignments) == set(declared),
            "Assignments do not cover the declared repetitions")
    require(all(isinstance(assignment, dict) and set(assignment) == set(labels)
                for assignment in assignments.values()), "An assignment does not cover the cohort")
    held_out = {}
    for record in records:
        require(isinstance(record, dict) and
                {"repetition", "fold", "model", "patient", "probability"} <= set(record),
                "Malformed prediction record")
        repetition, fold, model, patient = (record[key] for key in ("repetition", "fold", "model", "patient"))
        require(type(repetition) is int and repetition in assignments, "Prediction from an undeclared repetition")
        require(model in models, "Prediction from an undeclared model")
        require(token(patient) and patient in labels, "Prediction for a patient outside the cohort")
        require(type(fold) is int and fold == assignments[repetition][patient],
                "Prediction fold disagrees with the assignment")
        key = (repetition, model, patient)
        require(key not in held_out, "Duplicate held-out prediction")
        value = number(record["probability"])
        require(0 <= value <= 1, "Probability outside [0, 1]")
        held_out[key] = value
    require(len(held_out) == len(declared) * len(models) * len(labels), "Incomplete held-out prediction coverage")
    within = {(repetition, patient): sum(held_out[(repetition, model, patient)] for model in models) / len(models)
              for repetition in declared for patient in labels}
    final = {patient: sum(within[(repetition, patient)] for repetition in declared) / len(declared)
             for patient in labels}
    return final, {"repetitions": len(declared), "models": len(models), "patients": len(labels),
                   "held_out_predictions": len(held_out), "predictions_per_patient": len(declared) * len(models)}


def auroc(final_scores, labels):
    """Exact AUROC of final per-patient scores: refractory positive, ties half credit."""
    require(isinstance(final_scores, dict) and bool(final_scores) and set(final_scores) == set(labels),
            "Scores do not cover the cohort")
    require(all(isinstance(value, Fraction) and 0 <= value <= 1 for value in final_scores.values()),
            "Final score outside [0, 1]")
    require(all(label in (POSITIVE, NEGATIVE) for label in labels.values()), "Unexpected response label")
    ordered = sorted(final_scores)
    positives = [final_scores[patient] for patient in ordered if labels[patient] == POSITIVE]
    negatives = [final_scores[patient] for patient in ordered if labels[patient] == NEGATIVE]
    require(bool(positives) and bool(negatives), "AUROC requires both classes")
    concordant = sum(positive > negative for positive in positives for negative in negatives)
    tied = sum(positive == negative for positive in positives for negative in negatives)
    total = len(positives) * len(negatives)
    result = Fraction(2 * concordant + tied, 2 * total)
    rank_result = verify.rank_auc([final_scores[patient] for patient in ordered],
                                  [labels[patient] for patient in ordered])
    require(result == rank_result, "Independent AUROC calculations disagree")
    return result, {"positive_negative_pairs": total, "concordant_pairs": concordant,
                    "tied_pairs": tied, "discordant_pairs": total - concordant - tied}


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def declared_contract():
    """Describe the declared conventions and pin their documents; no data access."""
    for relative in (DECISION_RECORD, RECONSTRUCTION_CONTRACT):
        require((ROOT / relative).is_file(), "Missing reconstruction document")
    return {
        "scope": "Declared offline conventions for a prospective discovery reconstruction; no abundance values, model fitting or network access",
        "documents": {relative: file_sha256(ROOT / relative) for relative in (DECISION_RECORD, RECONSTRUCTION_CONTRACT)},
        "implementation_sha256": {"reconstruction_contracts.py": file_sha256(Path(__file__)),
                                  "verify_published_auc.py": file_sha256(Path(verify.__file__))},
        "cohort": dict(EXPECTED_COHORT, positive_class=POSITIVE, negative_class=NEGATIVE,
                       membership="published 135-key discovery score set; exact clinical joins; location NA retained"),
        "panel": {"size": PANEL_SIZE, "match": "whole-string HGNC symbol equality, exactly one row each",
                  "feature_order": "matrix row order among matched rows, fingerprinted before fitting"},
        "replicates": {"stage": "after imputation, before eligibility exclusion",
                       "rule": "exact arithmetic mean per explicit Sample ID; any missing value stops the run"},
        "folds": {"count": FOLDS, "unit": "explicit patient key", "stratification": "response label",
                  "order": "SHA-256 of repetition seed and patient key; round-robin from a seed-derived start",
                  "repetition_seeds": {"first": REPETITIONS[0], "last": REPETITIONS[-1], "count": len(REPETITIONS)},
                  "claims": "a declared replacement for the absent balanced_folds.R, not a recovery of original folds"},
        "models": list(MODELS),
        "aggregation": "mean of the three held-out probabilities within a repetition, then mean over repetitions per patient; complete coverage required, no missing-value removal",
        "metric": {"name": "AUROC", "higher_score_means": POSITIVE,
                   "tie_rule": "exact equality receives one-half credit", "independent_rank_check": True},
        "environment": {"python_implementation": platform.python_implementation(),
                        "python_version": platform.python_version(), "dependencies": "Python standard library only"},
        "limitations": [
            "These conventions are new declared choices; they do not recover the original helper, folds, workspaces or environment.",
            "No abundance values are read, no model is fitted and no performance result exists for this reconstruction.",
            "Reuse and retention conditions for the author archive and external scientific review remain open gates.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Print the declared reconstruction conventions with document and implementation hashes. "
                    "Offline; reads no data and fits nothing. The functions in this module are exercised by "
                    "tests with abstract tokens and are meant for a future authorized, private execution.",
        epilog=f"Decision record: {DECISION_RECORD}. Command: python3 tools/reconstruction_contracts.py",
    )
    parser.parse_args(argv)
    try:
        print(json.dumps(declared_contract(), indent=2, sort_keys=True, allow_nan=False))
    except Exception:
        print(FAILURE_MESSAGE, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
