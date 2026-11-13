"""Manifest digest replay and failure modes."""

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_sha256_manifests as manifests


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


if __name__ == "__main__":
    unittest.main()
