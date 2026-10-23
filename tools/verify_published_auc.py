#!/usr/bin/env python3
"""Verify one published-score AUROC after the required scientific scope review.

Only the pinned discovery scores and exact clinical joins are consumed. Raw
workbooks, identifiers, responses, and scores remain in memory. This is an
arithmetic check of released predictions, not model or cross-validation refitting.
"""

import argparse
import hashlib
import itertools
import json
import platform
import re
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path

import audit_published_cohorts as audit


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "protocols/pilot-001-score-verification.md"
CLINICAL_SHEET = "FFPE_Discovery_clinical"
SCORE_SHEET = "FFPE_pred_scores"
POSITIVE = "refractory"
NEGATIVE = "sensitive"
REFERENCE_AUC = Fraction(83, 100)
MODEL_TOLERANCE = Fraction(2, 100)
FAILURE_MESSAGE = "ERROR: published-score AUROC verification failed; no row-level details emitted."


def probability(value):
    """Parse an unrounded XLSX numeric string; never coerce or impute a score."""
    audit.require(isinstance(value, str) and
                  re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", value),
                  "Malformed prediction score")
    try:
        parsed = Decimal(value)
    except InvalidOperation:
        raise audit.AuditError("Malformed prediction score") from None
    audit.require(parsed.is_finite() and Decimal(0) <= parsed <= Decimal(1),
                  "Prediction score outside finite probability range")
    return parsed


def join_predictions(score_rows, clinical_records):
    """Keep each score paired with its own exact key, irrespective of row order."""
    audit.require(isinstance(score_rows, list) and bool(score_rows) and
                  all(isinstance(row, dict) for row in score_rows), "Missing prediction rows")
    keys = [row.get("A", "") for row in score_rows]
    joined = audit.join_score_membership(keys, clinical_records)
    scores = [row.get("B", "") for row in score_rows]
    # Validate here as well as in the metric entry point so an incomplete row
    # cannot pass a join-only caller's contract.
    for value in scores:
        probability(value)
    return scores, [row["Tumor response"] for row in joined], joined


def rank_auc(scores, labels):
    """Independent average-rank calculation on already validated Decimal scores."""
    ordered = sorted(zip(scores, labels), key=lambda pair: pair[0])
    rank_start, positive_rank_sum = 1, Fraction(0)
    for _, group in itertools.groupby(ordered, key=lambda pair: pair[0]):
        rows = list(group)
        average_rank = Fraction(2 * rank_start + len(rows) - 1, 2)
        positive_rank_sum += average_rank * sum(label == POSITIVE for _, label in rows)
        rank_start += len(rows)
    positives = labels.count(POSITIVE)
    negatives = labels.count(NEGATIVE)
    return (positive_rank_sum - Fraction(positives * (positives + 1), 2)) / (positives * negatives)


def compute_auc(scores, labels):
    """Return an exact, fixed-direction AUROC and aggregate pair counts."""
    audit.require(isinstance(scores, list) and isinstance(labels, list) and
                  len(scores) == len(labels) and bool(scores), "Mismatched metric inputs")
    audit.require(all(label in (POSITIVE, NEGATIVE) for label in labels), "Unexpected metric class")
    parsed = [probability(value) for value in scores]
    positive_scores = [score for score, label in zip(parsed, labels) if label == POSITIVE]
    negative_scores = [score for score, label in zip(parsed, labels) if label == NEGATIVE]
    audit.require(bool(positive_scores) and bool(negative_scores), "AUROC requires both classes")
    concordant = sum(positive > negative for positive in positive_scores for negative in negative_scores)
    tied = sum(positive == negative for positive in positive_scores for negative in negative_scores)
    total = len(positive_scores) * len(negative_scores)
    result = Fraction(2 * concordant + tied, 2 * total)
    audit.require(result == rank_auc(parsed, labels), "Independent AUROC calculations disagree")
    return result, {"positive_negative_pairs": total, "concordant_pairs": concordant,
                    "tied_pairs": tied, "discordant_pairs": total - concordant - tied}


def fraction_json(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def comparison(result):
    """Compare without altering cohort, polarity, scores, or declared tolerance."""
    difference = abs(result - REFERENCE_AUC)
    rounded_hundredths = (200 * result.numerator + result.denominator) // (2 * result.denominator)
    rounded = f"{rounded_hundredths // 100}.{rounded_hundredths % 100:02d}"
    return {
        "published_reference_auc": float(REFERENCE_AUC),
        "absolute_difference": float(difference),
        "absolute_difference_exact": fraction_json(difference),
        "model_reproduction_comparison_tolerance": float(MODEL_TOLERANCE),
        "within_0_02_model_tolerance": difference <= MODEL_TOLERANCE,
        "rounded_auc_2dp_half_up": rounded,
        "reproduces_displayed_0_83": rounded == "0.83",
        "interpretation": "These arithmetic comparisons do not establish model reproduction or close Gate 2.",
    }


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_verification():
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    audit.require((ROOT / CONTRACT).is_file(), "Missing scientific scope contract")
    contract_sha256 = file_sha256(ROOT / CONTRACT)
    tool_sha256 = file_sha256(Path(__file__))
    helper_sha256 = file_sha256(Path(audit.__file__))
    clinical_book = audit.Workbook(audit.SOURCES["clinical"])
    score_book = audit.Workbook(audit.SOURCES["panel_and_scores"])
    rows = clinical_book.rows(CLINICAL_SHEET)
    audit.require(bool(rows), "Missing clinical worksheet")
    header = rows[0]
    audit.require(len(set(header.values())) == len(header), "Duplicate clinical header")
    records = [{header[col]: value for col, value in row.items()} for row in rows[1:]]
    biological, missing = audit.classify_clinical(records)
    unique = audit.collapse_replicates(biological)
    audit.require(len(unique) == 158 and len(audit.patient_keys(unique)) == 158,
                  "Unexpected discovery clinical denominator")
    reconstructed = audit.eligible_samples(unique)

    score_rows = score_book.rows(SCORE_SHEET, columns={"A", "B"})
    audit.require(bool(score_rows) and score_rows[0].get("A") == "Samples" and
                  score_rows[0].get("B") == "Pred.scores", "Unexpected prediction header")
    scores, labels, joined = join_predictions(score_rows[1:], records)
    audit.require(len(scores) == 135 and labels.count(POSITIVE) == 52 and labels.count(NEGATIVE) == 83,
                  "Unexpected discovery prediction denominator or class counts")
    audit.require(audit.sample_keys(joined) == audit.sample_keys(reconstructed),
                  "Published membership differs from the literal reconstruction rule")
    location_na = sum(row["Tumor Location Group"] == "NA" for row in unique)
    retained_na = sum(row["Tumor Location Group"] == "NA" for row in joined)
    audit.require(location_na == 2 and retained_na == 1, "Unexpected discovery location missingness")

    result, pair_counts = compute_auc(scores, labels)
    return {
        "scope": "Arithmetic verification of AUROC from released discovery predictions; no model refit or cross-validation reconstruction",
        "review_contract": {"path": CONTRACT,
                            "sha256": contract_sha256,
                            "requirement": "Required scientific scope review must be recorded before a live run; this tool does not attest its completion."},
        "sources": {key: dict(value, url=audit.BASE + value["filename"])
                    for key, value in audit.SOURCES.items()},
        "selection": {
            "clinical_sheet": CLINICAL_SHEET, "prediction_sheet": SCORE_SHEET, "prediction_range": "A2:B136",
            "exact_join": "prediction Samples equals clinical Data Label 2; no normalization or row-position join",
            "published_prediction_rows": len(scores), "unique_patient_keys": len(audit.patient_keys(joined)),
            "unique_sample_keys": len(audit.sample_keys(joined)),
            "positive_class": POSITIVE, "negative_class": NEGATIVE,
            "positive_count": labels.count(POSITIVE), "negative_count": labels.count(NEGATIVE),
            "clinical_response_NA_rows": len(missing), "unique_response_labelled_clinical_samples": len(unique),
            "unique_sample_location_group_NA": location_na, "retained_score_cohort_location_group_NA": retained_na,
            "membership_rule": "Literal Neo-adjuvant == no and Tumor Location Group != Mix, then exact equality to published score membership; location NA remains unresolved and is retained, not classified as known nonmixed tissue.",
        },
        "metric": {"name": "AUROC", "higher_score_means": POSITIVE,
                   "direction_source": "Paper STAR Methods S95: probability of being refractory",
                   "tie_rule": "Exact source-number equality receives one-half credit; no score rounding",
                   "auc": float(result), "auc_exact": fraction_json(result),
                   "pair_counts": pair_counts, "independent_average_rank_check_passed": True,
                   "comparison": comparison(result), "confidence_interval": None,
                   "confidence_interval_status": "Not calculated; original interval procedure is unresolved"},
        "execution": {"started_at_utc": started, "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                      "elapsed_seconds": round(time.monotonic() - timer, 6),
                      "python_implementation": platform.python_implementation(), "python_version": platform.python_version(),
                      "os": platform.system(), "os_release": platform.release(), "architecture": platform.machine(),
                      "tool_sha256": tool_sha256, "membership_helper_sha256": helper_sha256,
                      "command": "python3 tools/verify_published_auc.py", "dependencies": "Python standard library only",
                      "random_seed": None, "stochastic_procedure": False},
        "limitations": [
            "Score provenance as the original averaged out-of-fold Figure 3D predictions is not established by this arithmetic check.",
            "Original model objects, fold assignments, preprocessing, corrected legends, and execution environment remain unresolved.",
            "An AUC discrepancy is reported unchanged; the tool never reverses direction or changes membership to improve agreement.",
            "No inference about patient independence, clinical validity, treatment benefit, or a cancer cure follows from this check.",
            "Raw workbooks, identifiers, response labels, prediction scores, and linkage rows are never emitted or persisted.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify discovery AUROC from pinned public scores in memory; emit aggregate JSON only. "
                    "Read the proposed scope contract and complete the required scientific review before a live run. "
                    "No refit, automatic direction choice, or confidence interval.",
        epilog=f"Contract: {CONTRACT}. Command after review: python3 tools/verify_published_auc.py",
    )
    parser.parse_args(argv)
    try:
        print(json.dumps(run_verification(), indent=2, sort_keys=True, allow_nan=False))
    except Exception:
        print(FAILURE_MESSAGE, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
