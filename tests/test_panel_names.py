"""Offline tests for the panel-name audit, using abstract tokens only."""

import hashlib
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_panel_names as audit


# Each expectation was checked against make.names(x) == x in R 4.4.3.
R_UNCHANGED = ["a1", "abc", "A.", ".a", ".", "..", "...", "..1", "..12", "...1",
               ".._", "._", "..a", "a_b", "a.b", "T", "F", "X"]
R_ALTERED = ["abc-d", "x2-1", "1a", "_a", ".2x", ".1", "a b", "a$b", "",
             "if", "else", "repeat", "while", "function", "for", "in", "next",
             "break", "TRUE", "FALSE", "NULL", "Inf", "NaN", "NA", "NA_integer_",
             "NA_real_", "NA_character_", "NA_complex_"]


def digest(symbols):
    return hashlib.sha256(("\n".join(symbols) + "\n").encode("utf-8")).hexdigest()


class PanelNameRule(unittest.TestCase):
    def test_matches_r_make_names_cases(self):
        for name in R_UNCHANGED:
            with self.subTest(name=name):
                self.assertTrue(audit.unchanged_by_make_names(name))
        for name in R_ALTERED:
            with self.subTest(name=name):
                self.assertFalse(audit.unchanged_by_make_names(name))

    def test_rejects_non_ascii_and_non_strings(self):
        for value in ["abcé", None, 3]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit.unchanged_by_make_names(value)


class PanelSummary(unittest.TestCase):
    def test_counts_without_symbols(self):
        symbols = ["abc", "abc-d", "x1"]
        summary = audit.summarize(symbols, digest(symbols))
        self.assertEqual((summary["symbols"], summary["altered_by_r_make_names"],
                          summary["unchanged_by_r_make_names"]), (3, 1, 2))
        text = repr(summary)
        for symbol in symbols:
            self.assertNotIn(f"'{symbol}'", text)

    def test_rejects_checksum_duplicates_and_blanks(self):
        with self.assertRaises(ValueError):
            audit.summarize(["abc"], "0" * 64)
        for symbols in (["abc", "abc"], ["abc", ""]):
            with self.subTest(symbols=symbols), self.assertRaises(ValueError):
                audit.summarize(symbols, digest(symbols))

    def test_main_reads_only_the_panel_sheet_and_hides_failures(self):
        symbols = ["abc", "x1"]
        book = mock.Mock()
        book.rows.return_value = [{"A": "Proteins"}] + [{"A": value} for value in symbols]
        with mock.patch.object(audit, "Workbook", return_value=book), \
                mock.patch.object(audit, "PANEL_SHA256", digest(symbols)):
            output = audit.run_audit()
        book.rows.assert_called_once_with("64_protein_predictors")
        self.assertEqual(output["altered_by_r_make_names"], 0)
        book.rows.return_value = [{"A": "Other"}]
        with mock.patch.object(audit, "Workbook", return_value=book), \
                mock.patch("sys.stdout"), mock.patch("sys.stderr") as stderr:
            self.assertEqual(audit.main([]), 1)
        written = "".join(call.args[0] for call in stderr.write.call_args_list)
        self.assertEqual(written.strip(), audit.FAILURE_MESSAGE)


if __name__ == "__main__":
    unittest.main()
