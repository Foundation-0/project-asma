"""Manifest digest replay and failure modes.

Each must-fail control asserts the refusal message, so deleting one guard in
tools/check_sha256_manifests.py fails the control that names it, even where the
bad input would still be refused later with a different message.
"""

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_sha256_manifests as manifests


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class CheckSha256ManifestsTests(unittest.TestCase):
    def test_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            sums = base / "SHA256SUMS"
            sums.write_text("0" * 64 + "  missing.json\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                manifests.parse_sums(sums)

    def test_tampered_digest_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            body_path = base / "body.json"
            body_path.write_text("{}", encoding="utf-8")
            wrong = "f" * 64
            sums = base / "SHA256SUMS"
            sums.write_text(f"{wrong}  body.json\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                manifests.parse_sums(sums)

    def test_repository_manifests_pass(self):
        manifests.check_tree()


class SumsFileControls(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        (self.base / "body.json").write_text("{}", encoding="utf-8")
        self.digest = sha256_text("{}")

    def refusal(self, text):
        sums = self.base / "SHA256SUMS"
        sums.write_text(text, encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            manifests.parse_sums(sums)
        return str(caught.exception)

    def test_well_formed_sums_pass(self):
        sums = self.base / "SHA256SUMS"
        sums.write_text(f"{self.digest}  body.json\n\n", encoding="utf-8")
        self.assertEqual(manifests.parse_sums(sums), {"body.json": self.digest})

    def test_malformed_line(self):
        self.assertIn(":1: malformed SHA256SUMS line", self.refusal(f"{self.digest} body.json\n"))

    def test_uppercase_or_short_digest(self):
        for digest in (self.digest.upper(), self.digest[:-1]):
            with self.subTest(digest=digest):
                self.assertIn(":1: invalid digest", self.refusal(f"{digest}  body.json\n"))

    def test_duplicate_path(self):
        line = f"{self.digest}  body.json\n"
        self.assertIn(":2: duplicate path body.json", self.refusal(line + line))


class ResultManifestControls(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.result = Path(temp.name)
        (self.result / "snapshot.json").write_text("{}", encoding="utf-8")

    def write_manifest(self, text):
        (self.result / "manifest.json").write_text(text, encoding="utf-8")
        (self.result / "SHA256SUMS").write_text(f"{sha256_text(text)}  manifest.json\n", encoding="utf-8")

    def refusal(self, files):
        self.write_manifest(json.dumps({"files": files}))
        with self.assertRaises(ValueError) as caught:
            manifests.check_result_manifest(self.result)
        return str(caught.exception)

    def test_well_formed_manifest_passes(self):
        self.write_manifest(json.dumps({"files": [{"path": "snapshot.json", "source_zip_sha256": "a" * 64}]}))
        self.assertIsNone(manifests.check_result_manifest(self.result))

    def test_non_object_or_pathless_entry(self):
        for entry in ("snapshot.json", {"name": "snapshot.json"}):
            with self.subTest(entry=entry):
                self.assertTrue(self.refusal([entry]).endswith("manifest.json: invalid file entry"))

    def test_missing_snapshot(self):
        self.assertTrue(self.refusal([{"path": "absent.json"}]).endswith("missing snapshot absent.json"))

    def test_invalid_source_zip_sha256(self):
        for digest in ("A" * 64, "a" * 63, ""):
            with self.subTest(digest=digest):
                message = self.refusal([{"path": "snapshot.json", "source_zip_sha256": digest}])
                self.assertTrue(message.endswith("invalid source_zip_sha256 for snapshot.json"))

    def test_duplicate_manifest_key(self):
        self.write_manifest('{"files": [], "files": [{"path": "absent.json"}]}')
        with self.assertRaises(ValueError) as caught:
            manifests.check_result_manifest(self.result)
        self.assertTrue(str(caught.exception).endswith("manifest.json: duplicate JSON key 'files'"))


class RegistryCertificateControls(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "registry.json"
        self.payload = {"schema_version": 1, "value": "abstract"}
        canonical = json.dumps(self.payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.digest = sha256_text(canonical)

    def refusal(self, text):
        self.path.write_text(text, encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            manifests.check_registry_certificate(self.path)
        return str(caught.exception)

    def test_matching_certificate_passes(self):
        self.path.write_text(json.dumps({**self.payload, "certificate_sha256": self.digest}), encoding="utf-8")
        self.assertIsNone(manifests.check_registry_certificate(self.path))

    def test_invalid_certificate_sha256(self):
        message = self.refusal(json.dumps({**self.payload, "certificate_sha256": self.digest.upper()}))
        self.assertTrue(message.endswith("registry.json: invalid certificate_sha256"))

    def test_certificate_sha256_mismatch(self):
        message = self.refusal(json.dumps({**self.payload, "value": "changed", "certificate_sha256": self.digest}))
        self.assertTrue(message.endswith("registry.json: certificate_sha256 mismatch"))

    def test_duplicate_key_is_refused_before_hashing(self):
        # json.loads keeps the last "value", which would hash to the recorded digest.
        text = ('{"schema_version": 1, "value": "shown first", "value": "abstract", '
                f'"certificate_sha256": "{self.digest}"}}')
        self.assertTrue(self.refusal(text).endswith("registry.json: duplicate JSON key 'value'"))


class TreeControls(unittest.TestCase):
    def test_zero_checks_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = (Path(tmp) / "results", Path(tmp) / "registries")
            empty[0].mkdir()
            stderr = io.StringIO()
            with mock.patch.object(manifests, "SCAN_ROOTS", empty), contextlib.redirect_stderr(stderr):
                with self.assertRaises(ValueError) as caught:
                    manifests.check_tree()
                code = manifests.main([])
        self.assertEqual(str(caught.exception), "no manifest checks discovered")
        self.assertEqual((code, stderr.getvalue()), (1, "FAIL: no manifest checks discovered\n"))


if __name__ == "__main__":
    unittest.main()
