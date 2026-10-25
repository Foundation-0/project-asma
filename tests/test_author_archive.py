"""Bounded archive/header checks with abstract labels; no patient records."""

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest import mock
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_author_archive as audit


def record(number):
    return {audit.clinical.LABEL_COLUMN: f"label-{number}", "Patient ID": f"abstract-person-{number}",
            "Sample ID": f"abstract-specimen-{number}", "Neo-adjuvant": "no", "Tumor response": "sensitive",
            "Tumor Location Group": "OV", "Sample type": "abstract-type"}


def compressed(body):
    stream = zlib.compressobj(wbits=-15)
    raw = stream.compress(body) + stream.flush()
    return raw + b"\x00" * (audit.COMPRESSED_CHUNK_BYTES - len(raw))


def directory_fixture():
    name = b"folder/" + audit.MEMBER.encode()
    contract = audit.MEMBER_CONTRACT
    fields = (b"PK\x01\x02", 20, 20, contract["flags"], 8, 0, 0, contract["crc32"],
              contract["compressed_bytes"], contract["uncompressed_bytes"], len(name), 0, 0, 0, 0, 0,
              contract["local_offset"])
    central = struct.pack("<4s6H3I5H2I", *fields) + name
    offset = audit.ARCHIVE_BYTES - len(central) - 22
    eocd = struct.pack("<4s4H2IH", b"PK\x05\x06", 0, 0, 1, 1, len(central), offset, 0)
    tail = b"\x00" * (audit.TAIL_BYTES - len(central) - 22) + central + eocd
    return name, central, tail


class AuthorArchiveChecks(unittest.TestCase):
    def test_directory_requires_hash_identity_and_complete_single_disk_table(self):
        name, central, tail = directory_fixture()
        with mock.patch.object(audit, "ENTRY_COUNT", 1), \
                mock.patch.object(audit, "CENTRAL_SHA256", hashlib.sha256(central).hexdigest()):
            observed, provenance = audit.inspect_directory(tail)
            self.assertEqual(observed, name)
            self.assertEqual(provenance["entries"], 1)
            changed = bytearray(tail)
            changed[-23] ^= 1
            with self.assertRaises(ValueError):
                audit.inspect_directory(bytes(changed))
            changed = bytearray(tail)
            changed[-18] = 1  # Nonzero disk number.
            with self.assertRaises(ValueError):
                audit.inspect_directory(bytes(changed))
            with self.assertRaises(ValueError):
                audit.inspect_directory(tail[:-1])

    def test_member_metadata_must_match_pinned_contract_even_with_matching_directory_hash(self):
        _, central, tail = directory_fixture()
        changed = dict(audit.MEMBER_CONTRACT, crc32=1)
        with mock.patch.object(audit, "ENTRY_COUNT", 1), \
                mock.patch.object(audit, "CENTRAL_SHA256", hashlib.sha256(central).hexdigest()), \
                mock.patch.object(audit, "MEMBER_CONTRACT", changed), self.assertRaises(ValueError):
            audit.inspect_directory(tail)

    def test_local_header_validates_name_flags_and_descriptor_placeholders(self):
        name = b"folder/" + audit.MEMBER.encode()
        header = struct.pack("<4s5H3I2H", b"PK\x03\x04", 20, 8, 8, 0, 0, 0, 0, 0, len(name), 0)
        fetch = mock.Mock(side_effect=[header, name])
        offset = audit.member_data_offset(fetch, name)
        self.assertEqual(offset, audit.MEMBER_CONTRACT["local_offset"] + 30 + len(name))
        with self.assertRaises(ValueError):
            audit.member_data_offset(mock.Mock(side_effect=[header, b"X" * len(name)]), name)
        changed = bytearray(header)
        changed[6] = 1  # Encryption/flag change.
        with self.assertRaises(ValueError):
            audit.member_data_offset(mock.Mock(return_value=bytes(changed)), name)

    def test_inflation_stops_exactly_at_header_newline(self):
        expected = b"Index\tlabel-alpha\n"
        fetch = mock.Mock(return_value=compressed(expected + b"unread-abundance-values\n"))
        header, count = audit.inflate_header(fetch, 100)
        self.assertEqual(header, expected)
        self.assertEqual(count, audit.COMPRESSED_CHUNK_BYTES)
        fetch.assert_called_once_with(100, 100 + audit.COMPRESSED_CHUNK_BYTES - 1)

    def test_inflation_rejects_missing_terminator_or_output_bomb(self):
        for body in (b"no-terminator", b"x" * (audit.MAX_HEADER_BYTES + 1) + b"\n"):
            with self.subTest(length=len(body)), self.assertRaises(ValueError):
                audit.inflate_header(mock.Mock(return_value=compressed(body)), 100)

    def test_inflation_has_a_compressed_byte_budget(self):
        fetch = mock.Mock(return_value=b"\x00\x00\x00\xff\xff")  # Empty non-final deflate block.
        with mock.patch.object(audit, "COMPRESSED_CHUNK_BYTES", 5), \
                mock.patch.object(audit, "MAX_COMPRESSED_HEADER_BYTES", 10), self.assertRaises(ValueError):
            audit.inflate_header(fetch, 100)
        self.assertLessEqual(fetch.call_count, 2)

    def test_exact_score_membership_requires_all_135_labels(self):
        rows = [record(number) for number in range(135)]
        keys = [row[audit.clinical.LABEL_COLUMN] for row in rows]
        header = ("Index\t" + "\t".join(keys) + "\n").encode()
        summary = audit.summarize_header(header, rows, keys)
        self.assertEqual(summary["published_score_keys_matching_header"], 135)
        self.assertEqual(summary["published_score_sample_keys_mapped"], 135)
        self.assertEqual(summary["published_score_patient_keys_mapped"], 135)
        self.assertNotIn("label-", json.dumps(summary))
        for bad_header in (header.replace(b"label-0\t", b"LABEL-0\t"), header.replace(b"label-0\t", b"")):
            with self.assertRaises(ValueError):
                audit.summarize_header(bad_header, rows, keys)
        with self.assertRaises(ValueError):
            audit.summarize_header(header, rows, keys[:-1])
        with self.assertRaises(ValueError):
            audit.summarize_header(header, rows, keys[:-1] + [keys[0]])
        with self.assertRaises(ValueError):
            audit.summarize_header(header, rows + [copy.deepcopy(rows[0])], keys)

    def test_range_response_must_be_partial_exact_length_and_identity_encoded(self):
        def fake_response(status=206, content_range=None, body=b"1234", encoding="identity"):
            stream = io.BytesIO(body)
            stream.status = status
            stream.headers = {"Content-Range": content_range or f"bytes 10-13/{audit.ARCHIVE_BYTES}",
                              "Content-Encoding": encoding}
            stream.geturl = lambda: "https://example.invalid/redirect"
            return stream
        with mock.patch.object(audit.urllib.request, "urlopen", return_value=fake_response()):
            self.assertEqual(audit.fetch_range(10, 13), b"1234")
        failures = (fake_response(status=200), fake_response(content_range="bytes 0-3/4"),
                    fake_response(body=b"123"), fake_response(body=b"12345"), fake_response(encoding="gzip"))
        for stream in failures:
            with mock.patch.object(audit.urllib.request, "urlopen", return_value=stream), self.assertRaises(ValueError):
                audit.fetch_range(10, 13)
        with mock.patch.object(audit.urllib.request, "urlopen") as fetch:
            with self.assertRaises(ValueError):
                audit.fetch_range(0, audit.TAIL_BYTES)
            fetch.assert_not_called()

    def test_cli_failure_never_exposes_identifiers_or_redirect_credentials(self):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(audit, "run_audit", side_effect=RuntimeError("private-key signed-url-token")), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(audit.main([]), 1)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), audit.FAILURE_MESSAGE + "\n")


if __name__ == "__main__":
    unittest.main()
