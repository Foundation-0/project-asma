"""Offline tests for the validation panel-coverage audit, on abstract tokens only.

The fake workbooks below mimic the shared loader's Workbook.sheets and
Workbook.rows. Every symbol is an invented "tok-" token, not a study symbol.
"""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_validation_panel_coverage as audit


PANEL = [f"tok-panel-{index:02d}" for index in range(64)]
PANEL_SHA = hashlib.sha256(("\n".join(PANEL) + "\n").encode("utf-8")).hexdigest()
SHEETS = {cohort: (sheet, header) for cohort, sheet, header in audit.COHORTS}


class FakeBook:
    """Header cells are always returned; data cells only for requested columns."""

    def __init__(self, sheets):
        self.data = sheets
        self.sheets = {name: name for name in sheets}
        self.calls = []

    def rows(self, sheet, columns=None):
        self.calls.append((sheet, None if columns is None else frozenset(columns)))
        return [dict(row) if index == 0 or columns is None else
                {key: value for key, value in row.items() if key in columns}
                for index, row in enumerate(self.data[self.sheets[sheet]])]


def feature_sheet(header, values):
    rows = [{"A": "abstract-statistic", "B": header}]
    for value in values:
        row = {"A": "tok-hidden-statistic"}
        if value is not None:
            row["B"] = value
        rows.append(row)
    return rows


def panel_book(panel=PANEL):
    return FakeBook({audit.PANEL_SHEET: [{"A": audit.PANEL_HEADER}] + [{"A": item} for item in panel]})


def without(token):
    return [item for item in PANEL if item != token]


# No cohort's set contains another's, so every intersection size differs from
# the sizes a wrong set expression would give. Each cohort lacks a different
# panel token (61 panel tokens are common to all three), has its own token, and
# shares tok-common with both others. tok-shared-df is in discovery and frozen
# only; tok-shared-fv-1 and tok-shared-fv-2 are in frozen and validation only.
COLUMNS = {
    # Also a repeated token, an empty cell, a missing cell, a padded token, a
    # numeric-looking cell and a cell that only starts like a number.
    "discovery": without("tok-panel-05") + [
        "tok-other-a", "tok-other-a", "tok-only-d", "tok-shared-df", "tok-common",
        "", None, " tok-padded", "1.5", "1.5x"],
    # Also one panel token repeated.
    "frozen": without("tok-panel-00") + [
        "tok-panel-01", "tok-only-f", "tok-shared-df", "tok-shared-fv-1",
        "tok-shared-fv-2", "tok-common"],
    "ffpe_validation": without("tok-panel-10") + [
        "tok-only-v", "tok-shared-fv-1", "tok-shared-fv-2", "tok-common"],
}


def feature_book(columns=COLUMNS):
    return FakeBook({SHEETS[cohort][0]: feature_sheet(SHEETS[cohort][1], values)
                     for cohort, values in columns.items()})


def books_for(feature, panel):
    def factory(source):
        return {"NIHMS1918576-supplement-MMC1.xlsx": feature,
                "NIHMS1918576-supplement-MMC4.xlsx": panel}[source["filename"]]
    return factory


def run(feature=None, panel=None):
    feature, panel = feature or feature_book(), panel or panel_book()
    with mock.patch.object(audit, "Workbook", side_effect=books_for(feature, panel)), \
            mock.patch.object(audit, "PANEL_SHA256", PANEL_SHA):
        return audit.run_audit()


class Counting(unittest.TestCase):
    def test_per_cohort_counts_and_intersections(self):
        output = run()
        cohorts = output["cohorts"]
        keys = ("data_rows", "empty_values", "distinct_nonempty_symbols",
                "symbols_repeated_across_rows", "duplicate_rows_beyond_first",
                "values_with_outer_whitespace", "numeric_like_values",
                "panel_symbols_present_exactly_once", "panel_symbols_absent",
                "panel_symbols_repeated")
        expected = {
            "discovery": (73, 2, 70, 1, 1, 1, 1, 63, 1, 0),
            "frozen": (69, 0, 68, 1, 1, 0, 0, 62, 1, 1),
            "ffpe_validation": (67, 0, 67, 0, 0, 0, 0, 63, 1, 0),
        }
        for cohort, values in expected.items():
            with self.subTest(cohort=cohort):
                self.assertEqual(tuple(cohorts[cohort][key] for key in keys), values)
                self.assertEqual((cohorts[cohort]["sheet"], cohorts[cohort]["column"]), SHEETS[cohort])
        self.assertEqual(output["intersections"], {
            "discovery_and_frozen": 64, "discovery_and_ffpe_validation": 63,
            "frozen_and_ffpe_validation": 65, "all_three": 62, "panel_symbols_in_all_three": 61})
        self.assertEqual(output["panel_symbols"], 64)

    def test_duplicates_empties_and_panel_multiplicity(self):
        summary, symbols = audit.summarize_column(
            ["", "  ", "tok-a", "tok-a", "tok-a", "tok-b"], ["tok-a", "tok-c"])
        self.assertEqual(symbols, {"tok-a", "tok-b"})
        self.assertEqual((summary["data_rows"], summary["empty_values"],
                          summary["distinct_nonempty_symbols"], summary["symbols_repeated_across_rows"],
                          summary["duplicate_rows_beyond_first"]), (6, 2, 2, 1, 2))
        self.assertEqual((summary["panel_symbols_present_exactly_once"], summary["panel_symbols_absent"],
                          summary["panel_symbols_repeated"]), (0, 1, 1))

    def test_matching_is_exact(self):
        summary, _ = audit.summarize_column(["TOK-A", " tok-a", "tok-a "], ["tok-a"])
        self.assertEqual((summary["panel_symbols_absent"], summary["values_with_outer_whitespace"]), (1, 2))

    def test_reads_only_the_named_columns(self):
        feature, panel = feature_book(), panel_book()
        run(feature, panel)
        self.assertEqual(panel.calls, [(audit.PANEL_SHEET, frozenset({"A"}))])
        for sheet, columns in feature.calls:
            self.assertIn(columns, (frozenset(), frozenset({"B"})))
        self.assertEqual({sheet for sheet, _ in feature.calls}, {sheet for sheet, _ in SHEETS.values()})


class Failures(unittest.TestCase):
    def assert_fails(self, feature=None, panel=None, sha=PANEL_SHA):
        with self.assertRaises(audit.AuditError):
            audit.audit_books(feature or feature_book(), panel or panel_book(), sha)

    def test_missing_sheet(self):
        columns = dict(COLUMNS)
        del columns["frozen"]
        self.assert_fails(feature_book(columns))

    def test_missing_renamed_or_repeated_column(self):
        for cohort in SHEETS:
            sheet, header = SHEETS[cohort]
            for variant in (header.upper(), header + " ", "abstract-other"):
                with self.subTest(cohort=cohort, header=variant):
                    book = feature_book()
                    book.data[sheet][0]["B"] = variant
                    self.assert_fails(book)
            with self.subTest(cohort=cohort, header="repeated"):
                book = feature_book()
                book.data[sheet][0]["A"] = header
                self.assert_fails(book)

    def test_panel_checksum_header_and_shape(self):
        self.assert_fails(sha="0" * 64)
        short = PANEL[:63]
        self.assert_fails(panel=panel_book(short),
                          sha=hashlib.sha256(("\n".join(short) + "\n").encode()).hexdigest())
        repeated = PANEL[:63] + PANEL[:1]
        self.assert_fails(panel=panel_book(repeated),
                          sha=hashlib.sha256(("\n".join(repeated) + "\n").encode()).hexdigest())
        book = panel_book()
        book.data[audit.PANEL_SHEET][0]["A"] = "abstract-other"
        self.assert_fails(panel=book)
        self.assert_fails(panel=FakeBook({"abstract-sheet": [{"A": audit.PANEL_HEADER}]}))

    def test_main_prints_only_the_fixed_message(self):
        columns = dict(COLUMNS)
        del columns["ffpe_validation"]
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(audit, "Workbook", side_effect=books_for(feature_book(columns), panel_book())), \
                mock.patch.object(audit, "PANEL_SHA256", PANEL_SHA), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(audit.main([]), 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), audit.FAILURE_MESSAGE + "\n")
        self.assertNotIn("tok-", stderr.getvalue())


class Output(unittest.TestCase):
    def main_output(self, feature):
        stdout = io.StringIO()
        with mock.patch.object(audit, "Workbook", side_effect=books_for(feature, panel_book())), \
                mock.patch.object(audit, "PANEL_SHA256", PANEL_SHA), contextlib.redirect_stdout(stdout):
            self.assertEqual(audit.main([]), 0)
        return stdout.getvalue()

    def test_no_symbols_or_cell_values_in_output(self):
        # The second fixture makes every cohort lack and repeat a panel token,
        # so a leak of absent or repeated symbols cannot print an empty list.
        sparse = feature_book({
            "discovery": PANEL[1:] + ["tok-panel-02"],
            "frozen": PANEL[:-1] + ["tok-panel-03"],
            "ffpe_validation": PANEL[2:] + ["tok-panel-04", "tok-other-d"],
        })
        for feature in (feature_book(), sparse):
            text = self.main_output(feature)
            self.assertNotIn("tok-", text)
            self.assertNotIn("abstract-statistic", text)
            self.assertTrue(text.isascii())
        output = json.loads(text)
        self.assertEqual(text, json.dumps(output, indent=2, sort_keys=True) + "\n")
        self.assertEqual(set(output["implementation_sha256"]),
                         {"audit_validation_panel_coverage.py", "audit_published_cohorts.py"})
        self.assertEqual(output["sources"]["feature_lists"]["sha256"],
                         audit.SOURCES["clinical"]["sha256"])
        self.assertEqual(output["sources"]["panel"]["sha256"],
                         audit.SOURCES["panel_and_scores"]["sha256"])
        for key in ("started_at_utc", "finished_at_utc"):
            self.assertTrue(output[key].endswith("+00:00"))

    def test_help_states_the_bounded_inspection_rule(self):
        completed = subprocess.run([sys.executable, str(ROOT / "tools/audit_validation_panel_coverage.py"),
                                    "--help"], capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(completed.returncode, 0)
        for phrase in ("Bounded-inspection rule", "in memory", "aggregate JSON only", "What is read",
                       "Why", "issue #9", "written to disk", "not show"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, completed.stdout)
        for _, sheet, header in audit.COHORTS:
            self.assertIn(sheet, completed.stdout)


class Fingerprint(unittest.TestCase):
    def test_sorted_distinct_utf8_with_lf_after_each(self):
        self.assertEqual(audit.fingerprint(["tok-b", "tok-a", "tok-a"]),
                         hashlib.sha256(b"tok-a\ntok-b\n").hexdigest())
        self.assertEqual(audit.fingerprint(["tok-a", "tok-b"]), audit.fingerprint(["tok-b", "tok-a"]))
        # Code-point order: uppercase sorts before lowercase.
        self.assertEqual(audit.fingerprint(["tok-a", "tok-B"]),
                         hashlib.sha256(b"tok-B\ntok-a\n").hexdigest())
        self.assertEqual(audit.fingerprint(["tok-é"]),
                         hashlib.sha256("tok-é\n".encode("utf-8")).hexdigest())
        self.assertNotEqual(audit.fingerprint(["tok-b", "tok-a"]),
                            audit.source_order_sha256(["tok-b", "tok-a"]))

    def test_rejects_symbols_that_break_the_encoding(self):
        for symbols in (["tok-a\ntok-b"], ["tok-a\r"], [""]):
            with self.subTest(symbols=symbols), self.assertRaises(audit.AuditError):
                audit.fingerprint(symbols)

    def test_cohort_fingerprint_covers_distinct_nonempty_symbols(self):
        summary, _ = audit.summarize_column(["tok-b", "", "tok-a", "tok-b", "  "], ["tok-a"])
        self.assertEqual(summary["sorted_distinct_symbol_sha256"],
                         hashlib.sha256(b"tok-a\ntok-b\n").hexdigest())


if __name__ == "__main__":
    unittest.main()
