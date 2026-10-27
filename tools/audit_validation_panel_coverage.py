#!/usr/bin/env python3
"""Count 64-panel coverage in published per-cohort feature lists; aggregates only.

Why: issue #9 asks whether all 64 panel symbols occur in the frozen and
FFPE-validation feature lists, not only in the discovery member.

What is read: the hash-pinned MMC1 and MMC4 supplement workbooks, downloaded
into memory through the shared loader in tools/audit_published_cohorts.py.
From MMC1 it decodes one column, located by exact header name, from each of
three per-cohort protein association sheets, located by exact sheet name:

  discovery        Assoc_test_FFPE_protein          column "symbol"
  frozen           Assoc_test_Frozen(all)_protein   column "symbol"
  FFPE validation  Assoc_test_FFPE_valid_protein    column "HGNC.symbol"

From MMC4 it decodes column A of 64_protein_predictors and checks the panel's
canonical SHA-256. The loader also decodes each workbook's shared-string
table, which holds text from every sheet, clinical sheets included; nothing
else from it is used.

Bounded-inspection rule (AGENTS.md): workbooks stay in memory and are never
written to disk. Output is aggregate JSON only: counts, set sizes and SHA-256
fingerprints. No symbols, rows, identifiers or values are printed, and any
failure prints one fixed message.

Limit: these lists are the features the authors tested for association. They
do not show that the archive members or the prediction workspaces hold the
same rows.
"""

import argparse
import collections
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import sys
import time

import audit_published_cohorts
from audit_published_cohorts import BASE, SOURCES, Workbook


PANEL_SHA256 = "77329920b86dacaffc6778ed7e7c6b827683beed1aad7f2229b8bafe2f535144"
PANEL_SHEET, PANEL_HEADER, PANEL_SIZE = "64_protein_predictors", "Proteins", 64
COHORTS = (
    ("discovery", "Assoc_test_FFPE_protein", "symbol"),
    ("frozen", "Assoc_test_Frozen(all)_protein", "symbol"),
    ("ffpe_validation", "Assoc_test_FFPE_valid_protein", "HGNC.symbol"),
)
NUMERIC = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")
FAILURE_MESSAGE = "ERROR: validation panel-coverage audit failed; no symbols or rows emitted."


class AuditError(ValueError):
    """A failed contract; messages are fixed and never carry cell values."""


def require(condition, message):
    if not condition:
        raise AuditError(message)


def source_order_sha256(symbols):
    """Panel encoding: UTF-8, source order, LF after every symbol."""
    return hashlib.sha256("".join(symbol + "\n" for symbol in symbols).encode("utf-8")).hexdigest()


def fingerprint(symbols):
    """SHA-256 of the distinct symbols in code-point order, UTF-8, LF after each."""
    distinct = set(symbols)
    require(all(isinstance(item, str) and item and "\n" not in item and "\r" not in item
                for item in distinct), "Symbol cannot be fingerprinted")
    return source_order_sha256(sorted(distinct))


def load_panel(book, expected_sha256=None):
    """Return the pinned panel after the canonical checksum and shape checks."""
    expected_sha256 = PANEL_SHA256 if expected_sha256 is None else expected_sha256
    require(PANEL_SHEET in book.sheets, "Missing panel sheet")
    rows = book.rows(PANEL_SHEET, columns={"A"})
    require(bool(rows) and rows[0].get("A") == PANEL_HEADER, "Unexpected panel header")
    symbols = [row.get("A", "") for row in rows[1:]]
    require(source_order_sha256(symbols) == expected_sha256, "Panel checksum mismatch")
    require(len(symbols) == PANEL_SIZE and len(set(symbols)) == PANEL_SIZE and all(symbols),
            "Panel symbols must be 64, unique and nonempty")
    return symbols


def read_column(book, sheet, header):
    """Return one column's data cells, by exact sheet name and exact header name."""
    require(sheet in book.sheets, "Missing sheet")
    head = book.rows(sheet, columns=set())
    require(bool(head), "Empty sheet")
    letters = [letter for letter, value in head[0].items() if value == header]
    require(len(letters) == 1, "Missing or repeated column header")
    rows = book.rows(sheet, columns={letters[0]})
    require(len(rows) == len(head), "Inconsistent sheet reads")
    values = [row.get(letters[0], "") for row in rows[1:]]
    require(all(isinstance(value, str) for value in values), "Non-text cell value")
    return values


def summarize_column(values, panel):
    """Count rows, empties, duplicates and panel matches; return counts and the set."""
    require(isinstance(values, list) and all(isinstance(value, str) for value in values),
            "Column values must be text")
    require(len(set(panel)) == len(panel) and all(panel), "Panel symbols must be unique and nonempty")
    counts = collections.Counter(value for value in values if value.strip())
    multiplicities = [counts[symbol] for symbol in panel]
    summary = {
        "data_rows": len(values),
        "empty_values": sum(not value.strip() for value in values),
        "distinct_nonempty_symbols": len(counts),
        "symbols_repeated_across_rows": sum(count > 1 for count in counts.values()),
        "duplicate_rows_beyond_first": sum(count - 1 for count in counts.values()),
        "values_with_outer_whitespace": sum(value != value.strip() for value in counts.elements()),
        "numeric_like_values": sum(NUMERIC.fullmatch(value.strip()) is not None
                                   for value in counts.elements()),
        "panel_symbols_present_exactly_once": multiplicities.count(1),
        "panel_symbols_absent": multiplicities.count(0),
        "panel_symbols_repeated": sum(count > 1 for count in multiplicities),
        "sorted_distinct_symbol_sha256": fingerprint(counts),
    }
    return summary, set(counts)


def audit_books(feature_book, panel_book, panel_sha256=None):
    """Aggregate coverage from the two in-memory workbooks; no symbols returned."""
    panel = load_panel(panel_book, panel_sha256)
    cohorts, sets = {}, {}
    for cohort, sheet, header in COHORTS:
        summary, sets[cohort] = summarize_column(read_column(feature_book, sheet, header), panel)
        cohorts[cohort] = dict(summary, sheet=sheet, column=header)
    discovery, frozen, validation = (sets[cohort] for cohort, _, _ in COHORTS)
    all_three = discovery & frozen & validation
    return {
        "panel_symbols": len(panel),
        "cohorts": cohorts,
        "intersections": {
            "discovery_and_frozen": len(discovery & frozen),
            "discovery_and_ffpe_validation": len(discovery & validation),
            "frozen_and_ffpe_validation": len(frozen & validation),
            "all_three": len(all_three),
            "panel_symbols_in_all_three": len(set(panel) & all_three),
        },
    }


def source_record(key, **read):
    source = SOURCES[key]
    return dict({name: source[name] for name in ("filename", "bytes", "md5", "sha256")},
                url=BASE + source["filename"], **read)


def run_audit():
    started, timer = datetime.now(timezone.utc).isoformat(), time.monotonic()
    panel_book = Workbook(SOURCES["panel_and_scores"])
    feature_book = Workbook(SOURCES["clinical"])
    output = audit_books(feature_book, panel_book)
    output.update({
        "schema_version": 1,
        "scope": ("Exact coverage of the pinned 64-protein panel in three published MMC1 "
                  "per-cohort protein association feature lists; counts and fingerprints, no symbols"),
        "question": "Issue #9: do all 64 panel symbols occur in the frozen and FFPE-validation feature lists?",
        "matching": "Exact string equality; no case folding, trimming, alias or accession mapping",
        "panel_canonical_sha256": PANEL_SHA256,
        "fingerprint_encoding": ("SHA-256 of the distinct nonempty symbols sorted by Unicode code point, "
                                 "UTF-8, LF after every symbol"),
        "sources": {
            "feature_lists": source_record("clinical", sheets_and_columns=[
                {"sheet": sheet, "column": header} for _, sheet, header in COHORTS]),
            "panel": source_record("panel_and_scores", sheets_and_columns=[
                {"sheet": PANEL_SHEET, "column": "A"}]),
        },
        "data_handling": ("Both workbooks were downloaded into memory, checked against pinned MD5 and "
                          "SHA-256, and never written to disk. Each workbook's shared-string table was "
                          "decoded by the loader; only the cells named under sources were used. "
                          "Only aggregate counts and fingerprints are emitted."),
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": time.monotonic() - timer,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "implementation_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in (Path(__file__), Path(audit_published_cohorts.__file__))},
        "limitations": [
            "These are the features the authors tested for association in each cohort. They do not show that the archive members or the prediction workspaces hold the same rows.",
            "Exact symbol equality does not resolve aliases, protein groups, isoforms or annotation-version differences between cohorts.",
            "Fingerprints are new observations from the pinned workbook, not publisher reference values.",
            "Coverage of 64/64 is expected by construction: the article says markers not detected in other tumor proteomics data sets such as the frozen and FFPE-validation data were filtered away (pinned article XML, P177 last sentence; P178 gives the final 64). This record corroborates that statement at supplement level; it is not an independent discovery.",
        ],
    })
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
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
