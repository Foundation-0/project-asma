#!/usr/bin/env python3
"""Recompute the released discovery-sheet AUROC from the pinned public workbooks.

Reads the NLM MMC1 and MMC4 workbooks in memory, checks their published
byte counts and checksums, and writes aggregate fractions only. Scores,
sample keys, and clinical rows are not retained. This is a discrimination
calculation on released scores. It is not a model refit and not clinical utility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import audit_published_cohorts as audit
import verify_published_auc as verify
from arithmetic import (
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    PRINTED_DISCOVERY_AUC,
    TOLERANCE,
    bootstrap_interval,
    delong_components,
    delong_interval,
    fraction_parts,
    half_up,
    pair_counts,
    rank_auc,
    stratified_bootstrap_numerators,
)

RESULT = Path(__file__).resolve().parent
FAILURE = "ERROR: AUROC provenance recompute failed; no row-level details emitted."


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_scores():
    clinical_book = audit.Workbook(audit.SOURCES["clinical"])
    score_book = audit.Workbook(audit.SOURCES["panel_and_scores"])
    rows = clinical_book.rows(verify.CLINICAL_SHEET)
    header = rows[0]
    records = [{header[col]: value for col, value in row.items()} for row in rows[1:]]
    score_rows = score_book.rows(verify.SCORE_SHEET, columns={"A", "B"})
    audit.require(
        score_rows and score_rows[0].get("A") == "Samples" and score_rows[0].get("B") == "Pred.scores",
        "Unexpected prediction header",
    )
    scores, labels, joined = verify.join_predictions(score_rows[1:], records)
    audit.require(
        len(scores) == 135 and labels.count(verify.POSITIVE) == 52 and labels.count(verify.NEGATIVE) == 83,
        "Unexpected discovery denominator",
    )
    biological, _missing = audit.classify_clinical(records)
    unique = audit.collapse_replicates(biological)
    reconstructed = audit.eligible_samples(unique)
    audit.require(
        audit.sample_keys(joined) == audit.sample_keys(reconstructed),
        "Published membership differs from the literal reconstruction rule",
    )
    parsed = [verify.probability(value) for value in scores]
    positives = [score for score, label in zip(parsed, labels) if label == verify.POSITIVE]
    negatives = [score for score, label in zip(parsed, labels) if label == verify.NEGATIVE]
    return positives, negatives


def build_payload(positives, negatives, started: str, timer: float) -> dict:
    counted = pair_counts(positives, negatives)
    ranked = rank_auc(positives, negatives)
    if counted["auc"] != ranked:
        raise audit.AuditError("Pair and rank readers disagree")
    theta, s10, s01 = delong_components(positives, negatives)
    if theta != counted["auc"]:
        raise audit.AuditError("DeLong placement mean disagrees with the pair AUROC")
    m = len(positives)
    n = len(negatives)
    interval = delong_interval(counted["auc"], s10, s01, m, n)
    denominator = 2 * m * n
    numerators = stratified_bootstrap_numerators(
        positives, negatives, BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED
    )
    bootstrap = bootstrap_interval(numerators, denominator)
    auc = counted["auc"]
    difference = abs(auc - PRINTED_DISCOVERY_AUC)
    return {
        "schema_version": 1,
        "kind": "released_discovery_sheet_auroc",
        "discrimination_only": True,
        "clinical_utility": False,
        "clinical_guidance": False,
        "scores_retained": False,
        "identifiers_retained": False,
        "model_refit": False,
        "retrieved_started_utc": started,
        "retrieved_completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.monotonic() - timer, 6),
        "python_version": platform.python_version(),
        "inputs": {
            "clinical": {
                "url": audit.BASE + audit.SOURCES["clinical"]["filename"],
                "filename": audit.SOURCES["clinical"]["filename"],
                "bytes": audit.SOURCES["clinical"]["bytes"],
                "md5": audit.SOURCES["clinical"]["md5"],
                "sha256": audit.SOURCES["clinical"]["sha256"],
                "sheet": verify.CLINICAL_SHEET,
            },
            "scores": {
                "url": audit.BASE + audit.SOURCES["panel_and_scores"]["filename"],
                "filename": audit.SOURCES["panel_and_scores"]["filename"],
                "bytes": audit.SOURCES["panel_and_scores"]["bytes"],
                "md5": audit.SOURCES["panel_and_scores"]["md5"],
                "sha256": audit.SOURCES["panel_and_scores"]["sha256"],
                "sheet": verify.SCORE_SHEET,
                "columns": ["Samples", "Pred.scores"],
            },
        },
        "cohort": {
            "marker": "64-protein ensemble score on the released FFPE discovery sheet",
            "comparison": "refractory versus sensitive; higher score is refractory",
            "n": m + n,
            "refractory": m,
            "sensitive": n,
            "pairs": counted["pairs"],
            "concordant": counted["concordant"],
            "discordant": counted["discordant"],
            "tied": counted["tied"],
        },
        "readers": {
            "pair_auc": fraction_parts(auc),
            "rank_auc": fraction_parts(ranked),
            "agree": True,
        },
        "rounding": {
            "decimal": format(float(auc), ".16f").rstrip("0"),
            "half_up_2dp": half_up(auc, 2),
            "half_up_3dp": half_up(auc, 3),
            "printed_discovery_auc": "0.83",
            "two_decimal_half_up_equals_printed": half_up(auc, 2) == "0.83",
            "absolute_difference": fraction_parts(difference),
            "difference_exceeds_0_02": difference > TOLERANCE,
        },
        "delong_95": {
            "s10": fraction_parts(s10),
            "s01": fraction_parts(s01),
            "positive_n": m,
            "negative_n": n,
            **interval,
        },
        "bootstrap_95": {
            "seed": BOOTSTRAP_SEED,
            "resamples": BOOTSTRAP_RESAMPLES,
            "design": "stratified with replacement within class",
            "percentile": "type 7, positions 0.025 and 0.975",
            "numerator_definition": "2*concordant + tied",
            "denominator": denominator,
            "numerators_sha256": hashlib.sha256(
                ",".join(str(value) for value in numerators).encode("ascii")
            ).hexdigest(),
            "numerators": numerators,
            **bootstrap,
        },
        "code_sha256": {
            "recompute.py": sha256_file(RESULT / "recompute.py"),
            "arithmetic.py": sha256_file(RESULT / "arithmetic.py"),
            "tools/audit_published_cohorts.py": sha256_file(Path(audit.__file__)),
            "tools/verify_published_auc.py": sha256_file(Path(verify.__file__)),
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="write aggregate certificate.json in this directory",
    )
    args = parser.parse_args(argv)
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    try:
        positives, negatives = load_scores()
        payload = build_payload(positives, negatives, started, timer)
        rendered = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.write_certificate:
            (RESULT / "certificate.json").write_text(rendered, encoding="utf-8")
            print(f"Wrote aggregate certificate ({payload['cohort']['n']} rows, scores not stored).")
        else:
            sys.stdout.write(rendered)
    except Exception:
        print(FAILURE, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
