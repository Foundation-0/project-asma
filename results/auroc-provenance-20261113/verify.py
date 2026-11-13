#!/usr/bin/env python3
"""Offline re-check of the discovery AUROC provenance certificate.

Replays the fraction, rounding, DeLong interval, and bootstrap percentile
from frozen aggregates. Confirms the printed-sentence record and the
repository occurrence inventory. Does not read the workbooks and does not
treat discrimination as clinical utility.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

RESULT = Path(__file__).resolve().parent
ROOT = RESULT.parents[1]
sys.path.insert(0, str(RESULT))

from arithmetic import (
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    PRINTED_DISCOVERY_AUC,
    TOLERANCE,
    bootstrap_interval,
    delong_interval,
    half_up,
)

CERTIFICATE = RESULT / "certificate.json"
DOC = ROOT / "docs/auroc-provenance-20261113.md"
SUMS = RESULT / "SHA256SUMS"
INVENTORY = RESULT / "occurrences.json"
BEGIN = "<!-- BEGIN GENERATED AUROC PROVENANCE -->"
END = "<!-- END GENERATED AUROC PROVENANCE -->"
TOKEN = re.compile(r"0\.80885\d*|(?<![\d.])0\.83(?!\d)")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
SKIP_FILES = {"results/integrity-audit-2026-11-13/audit.json"}
SKIP_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".xlsx", ".pyc"}
FORBIDDEN = (
    "as K07 in the claims ledger",
    "Paper supplementary locations S95/S99",
)
EMAIL = re.compile(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_certificate() -> dict:
    return json.loads(CERTIFICATE.read_text(encoding="utf-8"))


def render(cert: dict) -> str:
    cohort = cert["cohort"]
    readers = cert["readers"]
    rounding = cert["rounding"]
    delong = cert["delong_95"]
    boot = cert["bootstrap_95"]
    lines = [
        f"sheet_n: {cohort['n']}",
        f"refractory: {cohort['refractory']}",
        f"sensitive: {cohort['sensitive']}",
        f"pairs: {cohort['pairs']}",
        f"concordant: {cohort['concordant']}",
        f"discordant: {cohort['discordant']}",
        f"tied: {cohort['tied']}",
        f"pair_auc: {readers['pair_auc']['numerator']}/{readers['pair_auc']['denominator']}",
        f"rank_auc: {readers['rank_auc']['numerator']}/{readers['rank_auc']['denominator']}",
        f"half_up_2dp: {rounding['half_up_2dp']}",
        f"half_up_3dp: {rounding['half_up_3dp']}",
        f"printed_discovery_auc: {rounding['printed_discovery_auc']}",
        f"two_decimal_half_up_equals_printed: {str(rounding['two_decimal_half_up_equals_printed']).lower()}",
        (
            "absolute_difference: "
            f"{rounding['absolute_difference']['numerator']}/{rounding['absolute_difference']['denominator']}"
        ),
        f"difference_exceeds_0_02: {str(rounding['difference_exceeds_0_02']).lower()}",
        f"delong_95: {delong['lower']:.10f} {delong['upper']:.10f}",
        f"bootstrap_95: {boot['lower']:.10f} {boot['upper']:.10f}",
        f"bootstrap_seed: {boot['seed']}",
        f"bootstrap_resamples: {boot['resamples']}",
        f"mmc1_sha256: {cert['inputs']['clinical']['sha256']}",
        f"mmc4_sha256: {cert['inputs']['scores']['sha256']}",
        "discrimination_only: true",
        "clinical_utility: false",
        "clinical_guidance: false",
    ]
    return "\n".join(lines)


def marked(text: str) -> str:
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("Generated provenance markers are missing or duplicated.")
    return text.split(BEGIN, 1)[1].split(END, 1)[0].strip("\n")


def check_arithmetic(cert: dict) -> None:
    cohort = cert["cohort"]
    if cohort["refractory"] * cohort["sensitive"] != cohort["pairs"]:
        raise ValueError("Class product disagrees with the pair count.")
    if cohort["concordant"] + cohort["discordant"] + cohort["tied"] != cohort["pairs"]:
        raise ValueError("Pair partition disagrees with the pair count.")
    if cohort["n"] != cohort["refractory"] + cohort["sensitive"]:
        raise ValueError("Class counts disagree with n.")
    auc = Fraction(2 * cohort["concordant"] + cohort["tied"], 2 * cohort["pairs"])
    pair = cert["readers"]["pair_auc"]
    rank = cert["readers"]["rank_auc"]
    if Fraction(pair["numerator"], pair["denominator"]) != auc:
        raise ValueError("Stored pair AUROC disagrees with the pair counts.")
    if Fraction(rank["numerator"], rank["denominator"]) != auc:
        raise ValueError("Stored rank AUROC disagrees with the pair counts.")
    if not cert["readers"]["agree"]:
        raise ValueError("Readers are recorded as disagreeing.")
    if half_up(auc, 2) != cert["rounding"]["half_up_2dp"]:
        raise ValueError("Two-decimal half-up rounding disagrees.")
    if half_up(auc, 3) != cert["rounding"]["half_up_3dp"]:
        raise ValueError("Three-decimal half-up rounding disagrees.")
    if cert["rounding"]["half_up_2dp"] == cert["rounding"]["printed_discovery_auc"]:
        raise ValueError("Two-decimal rounding matches the printed discovery AUC.")
    if cert["rounding"]["two_decimal_half_up_equals_printed"]:
        raise ValueError("Certificate says the printed value is the two-decimal rounding.")
    difference = abs(auc - PRINTED_DISCOVERY_AUC)
    stored = cert["rounding"]["absolute_difference"]
    if Fraction(stored["numerator"], stored["denominator"]) != difference:
        raise ValueError("Stored absolute difference disagrees.")
    if (difference > TOLERANCE) != cert["rounding"]["difference_exceeds_0_02"]:
        raise ValueError("Tolerance flag disagrees.")
    s10 = Fraction(cert["delong_95"]["s10"]["numerator"], cert["delong_95"]["s10"]["denominator"])
    s01 = Fraction(cert["delong_95"]["s01"]["numerator"], cert["delong_95"]["s01"]["denominator"])
    interval = delong_interval(
        auc, s10, s01, cert["delong_95"]["positive_n"], cert["delong_95"]["negative_n"]
    )
    for key in ("lower", "upper", "standard_error", "z_975"):
        if interval[key] != cert["delong_95"][key]:
            raise ValueError(f"DeLong field {key} does not replay.")
    if interval["contains_printed_0_83"] != cert["delong_95"]["contains_printed_0_83"]:
        raise ValueError("DeLong containment flag does not replay.")
    boot = cert["bootstrap_95"]
    if boot["seed"] != BOOTSTRAP_SEED or boot["resamples"] != BOOTSTRAP_RESAMPLES:
        raise ValueError("Bootstrap seed or resample count changed.")
    numerators = boot["numerators"]
    if len(numerators) != boot["resamples"]:
        raise ValueError("Bootstrap numerator list has the wrong length.")
    digest = sha256(",".join(str(value) for value in numerators).encode("ascii"))
    if digest != boot["numerators_sha256"]:
        raise ValueError("Bootstrap numerator digest disagrees.")
    replay = bootstrap_interval(numerators, boot["denominator"])
    for key in ("lower", "upper", "mean"):
        if replay[key] != boot[key]:
            raise ValueError(f"Bootstrap field {key} does not replay.")
    if replay["contains_printed_0_83"] != boot["contains_printed_0_83"]:
        raise ValueError("Bootstrap containment flag does not replay.")
    if not (cert["discrimination_only"] and cert["clinical_utility"] is False and cert["clinical_guidance"] is False):
        raise ValueError("Certificate does not keep discrimination separate from clinical utility.")
    if cert["scores_retained"] or cert["identifiers_retained"] or cert["model_refit"]:
        raise ValueError("Certificate records retained scores, identifiers, or a refit.")
    for name, digest in cert["code_sha256"].items():
        path = ROOT / name if name.startswith("tools/") else RESULT / name
        if sha256(path.read_bytes()) != digest:
            raise ValueError(f"Producing-code hash changed for {name}.")


def check_sources(cert: dict) -> None:
    article = cert["primary_sources"]["article"]
    sentence = article["auc_sentence"]
    if "AUC of 0.83 (95% CI: 0.77\u20130.90)" not in sentence:
        raise ValueError("Stored article sentence does not contain the printed discovery AUC.")
    if "0.80885" in sentence:
        raise ValueError("Stored article sentence contains the sheet decimal.")
    if article["auc_sentence_count_in_xml"] != 1 or article["sheet_decimal_present_in_xml"]:
        raise ValueError("Article occurrence flags disagree with the 2026-11-13 read.")
    if article["figure_caption_restates_0_83"]:
        raise ValueError("Figure caption flag disagrees with the 2026-11-13 read.")
    figure = cert["primary_sources"]["figure"]
    if "0.83" not in figure["ocr_row"] or "n=135" not in figure["ocr_row"]:
        raise ValueError("Figure OCR record does not contain the discovery label.")
    if "0.81" not in figure["ocr_row"] or "n=27" not in figure["ocr_row"]:
        raise ValueError("Figure OCR record does not contain the frozen-overlap label.")
    code = cert["primary_sources"]["author_code"]
    if code["annotation"] != 'label="AUC = 0.83"' or not code["annotation_is_literal"]:
        raise ValueError("Author-code annotation record changed.")
    if code["files_containing_n_equals_135"] != 0 or code["files_searched"] != 42:
        raise ValueError("Author-code search record changed.")
    correction = cert["primary_sources"]["correction"]
    if correction["mentions_auc"] or correction["mentions_0_83"]:
        raise ValueError("Correction record says it mentions the AUC.")
    for digest in (
        article["xml_sha256"],
        figure["sha256"],
        code["sha256"],
        correction["xml_sha256"],
        cert["inputs"]["clinical"]["sha256"],
        cert["inputs"]["scores"]["sha256"],
    ):
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("A recorded SHA-256 is not 64 hex characters.")


def scan_occurrences() -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        relative = str(path.relative_to(ROOT))
        if path.resolve() == INVENTORY.resolve() or relative in SKIP_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            continue
        hits = sum(1 for line in text.splitlines() if TOKEN.search(line))
        if hits:
            counts[str(path.relative_to(ROOT))] = hits
    return counts


def check_inventory() -> None:
    fresh = scan_occurrences()
    stored = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if stored.get("token") != TOKEN.pattern:
        raise ValueError("Occurrence token pattern changed.")
    if stored.get("files") != fresh:
        raise ValueError("Occurrence inventory does not match a fresh scan.")
    required = {
        "CLAIMS.md",
        "docs/auroc-provenance-20261113.md",
        "docs/pilot-001-score-verification-result.md",
        "paper/manuscript.md",
        "results/auroc-provenance-20261113/certificate.json",
    }
    if not required <= set(fresh):
        raise ValueError("A required file dropped out of the occurrence inventory.")
    if any(name.startswith("index.html") or name.startswith("assets/") for name in fresh):
        raise ValueError("The site assets now contain an AUROC token this inventory did not expect.")


def check_wording() -> None:
    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "CLAIMS.md",
            ROOT / "docs/google-bio-convergence-2026-11-11.md",
            DOC,
        )
    )
    for phrase in FORBIDDEN:
        if phrase in corpus:
            raise ValueError(f"Wrong citation remains: {phrase}")
    doc = DOC.read_text(encoding="utf-8")
    for phrase in (
        "Paragraph P33",
        "n=135",
        "literal string",
        "clinical utility",
        "frozen-overlap",
        "0.8088507877664504",
    ):
        if phrase not in doc:
            raise ValueError(f"Provenance note is missing {phrase!r}.")
    if marked(doc) != render(load_certificate()):
        raise ValueError("Provenance note count block disagrees with the certificate.")


def check_sums() -> None:
    if not SUMS.is_file():
        raise ValueError("SHA256SUMS is missing.")
    seen = set()
    for line in SUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split("  ", 1)
        if name in seen:
            raise ValueError("Duplicate SHA256SUMS path.")
        seen.add(name)
        target = ROOT / name if name.startswith(("results/", "docs/", "tools/")) else RESULT / name
        if sha256(target.read_bytes()) != digest:
            raise ValueError(f"SHA256SUMS mismatch for {name}.")
    for name in ("certificate.json", "occurrences.json", "verify.py", "arithmetic.py", "recompute.py"):
        if name not in seen and f"results/auroc-provenance-20261113/{name}" not in seen:
            raise ValueError(f"SHA256SUMS does not cover {name}.")


def check_no_identifiers() -> None:
    for path in sorted(RESULT.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".md", ".py"}:
            continue
        text = path.read_text(encoding="utf-8")
        if EMAIL.search(text):
            raise ValueError(f"Email address remains in {path.name}.")


def write_inventory() -> None:
    fresh = scan_occurrences()
    payload = {"token": TOKEN.pattern, "files": fresh, "hit_count": sum(fresh.values())}
    INVENTORY.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    args = set(argv if argv is not None else sys.argv[1:])
    try:
        if "--write-inventory" in args:
            write_inventory()
        cert = load_certificate()
        check_arithmetic(cert)
        check_sources(cert)
        check_inventory()
        check_wording()
        check_sums()
        check_no_identifiers()
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: discovery AUROC provenance arithmetic, locators, inventory, and pins.")
    print("This check replays frozen aggregates. It does not re-read the workbooks.")
    print("The AUROC is discrimination of released scores. It is not clinical utility.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
