#!/usr/bin/env python3
"""Count pinned panel symbols that R's make.names would alter; aggregate output only.

Reads only the `64_protein_predictors` worksheet of the hash-pinned MMC4 workbook,
in memory, through the shared loader. No score or clinical sheet is parsed, and
no symbol is printed or written. The result bears on name matching in the author
scripts (make.names and the formula interface); the reconstruction itself uses
the matrix interface.
"""

import argparse
import hashlib
import json
import re
import sys

from audit_published_cohorts import SOURCES, Workbook


PANEL_SHA256 = "77329920b86dacaffc6778ed7e7c6b827683beed1aad7f2229b8bafe2f535144"
FAILURE_MESSAGE = "ERROR: panel-name audit failed; no symbols emitted."

# R 4.4.3 make.names keeps an ASCII name unchanged exactly when it is
# syntactically valid and not reserved. "..." and "..1" are kept, so only these
# words count as reserved here; verified against R on the cases in the tests.
R_RESERVED = frozenset({
    "if", "else", "repeat", "while", "function", "for", "in", "next", "break",
    "TRUE", "FALSE", "NULL", "Inf", "NaN", "NA", "NA_integer_", "NA_real_",
    "NA_character_", "NA_complex_",
})
R_SYNTACTIC = re.compile(r"(?:[A-Za-z]|\.(?![0-9]))[A-Za-z0-9._]*")


def unchanged_by_make_names(name):
    """Return whether R's make.names(name) == name, for ASCII names only."""
    if not isinstance(name, str) or not name.isascii():
        raise ValueError("Only ASCII names are supported")
    return name not in R_RESERVED and R_SYNTACTIC.fullmatch(name) is not None


def summarize(symbols, expected_sha256=None):
    expected_sha256 = PANEL_SHA256 if expected_sha256 is None else expected_sha256
    canonical = ("\n".join(symbols) + "\n").encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != expected_sha256:
        raise ValueError("Panel checksum mismatch")
    if len(set(symbols)) != len(symbols) or not all(symbols):
        raise ValueError("Panel symbols must be unique and nonempty")
    changed = sum(not unchanged_by_make_names(symbol) for symbol in symbols)
    return {
        "schema_version": 1,
        "scope": "Pinned 64-protein panel symbols only; counts, no symbols",
        "panel_canonical_sha256": expected_sha256,
        "symbols": len(symbols),
        "altered_by_r_make_names": changed,
        "unchanged_by_r_make_names": len(symbols) - changed,
        "duplicate_symbols": 0,
        "limitations": [
            "Mirrors R 4.4.3 make.names for ASCII names; non-ASCII names are rejected.",
            "Unique symbols mean make.names(unique = TRUE) adds no suffixes.",
            "Says nothing about the row names inside the absent author workspaces.",
        ],
    }


def run_audit():
    rows = Workbook(SOURCES["panel_and_scores"]).rows("64_protein_predictors")
    if not rows or rows[0].get("A") != "Proteins":
        raise ValueError("Unexpected protein-panel header")
    return summarize([row.get("A", "") for row in rows[1:]])


def main(argv=None):
    parser = argparse.ArgumentParser(description=(
        "Count pinned panel symbols that R's make.names would alter. Reads only the "
        "panel worksheet in memory and prints aggregate JSON without symbols."
    ))
    parser.parse_args(argv)
    try:
        output = run_audit()
    except Exception:
        print(FAILURE_MESSAGE, file=sys.stderr)
        return 1
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
