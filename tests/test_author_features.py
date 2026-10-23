"""Synthetic integrity/annotation tests; no research records or measurements."""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_author_features as audit


def header():
    return ("\t".join(audit.ANNOTATIONS + tuple(f"abstract-column-{i}" for i in
                                             range(audit.COLUMN_COUNT - len(audit.ANNOTATIONS)))) + "\n").encode()


def row(symbol="ALPHA", accession="accession-alpha", index="feature-alpha", proteins="protein-alpha"):
    fields = [accession, symbol, "abstract-name", "abstract-location", index,
              "annotation-count", "annotation-count", proteins, "annotation-probability"]
    return ("\t".join(fields + ["discard-without-numeric-conversion"] *
                      (audit.COLUMN_COUNT - len(fields))) + "\n").encode()


def fixture(body):
    compressor = zlib.compressobj(wbits=-15)
    packed = compressor.compress(body) + compressor.flush()
    contract = {"compressed_bytes": len(packed), "uncompressed_bytes": len(body), "crc32": zlib.crc32(body)}
    return packed, contract


def inspect(body, panel=("ALPHA",), chunk_size=7):
    packed, contract = fixture(body)
    chunks = (packed[i:i + chunk_size] for i in range(0, len(packed), chunk_size))
    return audit.inspect_member(chunks, panel, contract, hashlib.sha256(header()).hexdigest())


class AuthorFeatureChecks(unittest.TestCase):
    def test_streaming_integrity_checks_full_member_and_does_not_use_abundance_strings(self):
        body = header() + row()
        result = inspect(body)
        self.assertEqual(result["integrity"]["sha256"], hashlib.sha256(body).hexdigest())
        self.assertEqual(result["integrity"]["crc32_hex"], f"{zlib.crc32(body):08x}")
        self.assertTrue(result["integrity"]["crc32_matches_pinned_directory"])
        self.assertTrue(result["features"]["all_panel_symbols_have_one_exact_row"])
        self.assertNotIn("discard-without", json.dumps(result))
        self.assertNotIn("abstract-column", json.dumps(result))
        self.assertNotIn("accession-alpha", json.dumps(result))

    def test_abundance_bytes_are_not_decoded_as_text(self):
        body = header() + row().replace(b"discard-without-numeric-conversion", b"\xff\xfe")
        result = inspect(body)
        self.assertEqual(result["features"]["panel_matching_rows"], 1)
        self.assertFalse(result["features"]["abundance_values_converted_or_used"])

    def test_exact_symbols_are_never_trimmed_split_or_case_folded(self):
        result = inspect(header() + row("alpha") + row(" ALPHA") + row("ALPHA;BETA"), ("ALPHA", "BETA"))
        counts = result["features"]
        self.assertEqual(counts["panel_symbols_absent"], 2)
        self.assertEqual(counts["symbol_rows_with_outer_whitespace"], 1)
        self.assertEqual(counts["symbol_rows_with_delimiter_markers"], 1)
        self.assertFalse(counts["all_panel_symbols_have_one_exact_row"])

    def test_duplicate_and_group_diagnostics_are_not_silently_collapsed(self):
        body = header() + row(proteins="first;second") + row(proteins="first;second") + row("BETA")
        counts = inspect(body, ("ALPHA", "BETA", "GAMMA"))["features"]
        self.assertEqual(counts["feature_rows"], 3)
        self.assertEqual(counts["panel_symbols_absent"], 1)
        self.assertEqual(counts["panel_symbols_with_one_exact_row"], 1)
        self.assertEqual(counts["panel_symbols_with_multiple_exact_rows"], 1)
        self.assertEqual(counts["duplicate_annotation_rows_beyond_first"], 1)
        self.assertEqual(counts["nonempty_accessions_repeated_across_rows"], 1)
        self.assertEqual(counts["panel_matching_rows_with_delimiter_markers_in_protein_annotations"], 2)

    def test_balanced_annotation_quoting_is_decoded_without_changing_symbol_identity(self):
        body = header() + row('"ALPHA"', proteins='"first ""quoted"" annotation"')
        counts = inspect(body)["features"]
        self.assertEqual(counts["panel_matching_rows"], 1)
        self.assertTrue(counts["all_panel_symbols_have_one_exact_row"])
        with self.assertRaises(ValueError):
            inspect(header() + row('"ALPHA"suffix'))

    def test_empty_feature_symbols_cannot_match_panel(self):
        counts = inspect(header() + row("") + row())["features"]
        self.assertEqual(counts["empty_symbol_rows"], 1)
        self.assertEqual(counts["panel_matching_rows"], 1)

    def test_rejects_wrong_crc_and_wrong_full_length(self):
        packed, contract = fixture(header() + row())
        for changed in (dict(contract, crc32=contract["crc32"] ^ 1),
                        dict(contract, uncompressed_bytes=contract["uncompressed_bytes"] + 1),
                        dict(contract, compressed_bytes=contract["compressed_bytes"] + 1)):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                audit.inspect_member([packed], ("ALPHA",), changed, hashlib.sha256(header()).hexdigest())

    def test_rejects_truncated_stream_trailing_data_and_concatenated_streams(self):
        packed, contract = fixture(header() + row())
        for changed in (packed[:-1], packed + b"x", packed + packed):
            changed_contract = dict(contract, compressed_bytes=len(changed))
            with self.subTest(length=len(changed)), self.assertRaises(ValueError):
                audit.inspect_member([changed], ("ALPHA",), changed_contract, hashlib.sha256(header()).hexdigest())

    def test_rejects_inflated_size_beyond_declared_bound(self):
        packed, contract = fixture(header() + row())
        contract["uncompressed_bytes"] = len(header()) + 1
        with self.assertRaises(ValueError):
            audit.inspect_member([packed], ("ALPHA",), contract, hashlib.sha256(header()).hexdigest())

    def test_requires_exact_header_fingerprint_and_annotation_schema(self):
        packed, contract = fixture(header() + row())
        with self.assertRaises(ValueError):
            audit.inspect_member([packed], ("ALPHA",), contract, "0" * 64)
        bad_header = header().replace(b"HGNC symbol", b"arbitrary-key")
        bad_packed, bad_contract = fixture(bad_header + row())
        with self.assertRaises(ValueError):
            audit.inspect_member([bad_packed], ("ALPHA",), bad_contract, hashlib.sha256(bad_header).hexdigest())

    def test_rejects_row_width_quote_and_line_boundary_ambiguity(self):
        for bad_row in (row().replace(b"\t", b"", 1), row("\"ALPHA"), row()[:-1], row("ALPHA\rBETA")):
            with self.subTest(length=len(bad_row)), self.assertRaises(ValueError):
                inspect(header() + bad_row)

    def test_line_and_row_resource_bounds(self):
        with mock.patch.object(audit, "MAX_LINE_BYTES", len(header()) + 1), self.assertRaises(ValueError):
            inspect(header() + row())
        with mock.patch.object(audit, "MAX_ROWS", 1), self.assertRaises(ValueError):
            inspect(header() + row() + row())

    def test_member_transfer_requires_exact_partial_response_and_length(self):
        def response(body=b"abcd", status=206, content_range=None, encoding="identity"):
            result = io.BytesIO(body)
            result.status = status
            result.headers = {"Content-Range": content_range or f"bytes 100-103/{audit.archive.ARCHIVE_BYTES}",
                              "Content-Encoding": encoding}
            result.geturl = lambda: "https://example.invalid/member"
            return result
        contract = dict(audit.archive.MEMBER_CONTRACT, compressed_bytes=4)
        with mock.patch.object(audit.archive, "MEMBER_CONTRACT", contract), \
                mock.patch.object(audit.urllib.request, "urlopen", return_value=response()):
            self.assertEqual(b"".join(audit.member_chunks(100)), b"abcd")
        for failed in (response(status=200), response(content_range="bytes 0-3/4"),
                       response(encoding="gzip"), response(body=b"abc"), response(body=b"abcde")):
            with mock.patch.object(audit.archive, "MEMBER_CONTRACT", contract), \
                    mock.patch.object(audit.urllib.request, "urlopen", return_value=failed), self.assertRaises(ValueError):
                list(audit.member_chunks(100))

    def test_cli_failure_emits_no_partial_aggregate_or_sensitive_exception(self):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(audit, "run_audit", side_effect=ValueError("sensitive field signed-token")), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(audit.main([]), 1)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), audit.FAILURE_MESSAGE + "\n")


if __name__ == "__main__":
    unittest.main()
