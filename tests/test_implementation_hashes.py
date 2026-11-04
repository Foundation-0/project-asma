"""Tests for registry implementation hash verification."""

import json
import tempfile
import unittest
from pathlib import Path

from tools.check_implementation_hashes import (
    STATUS_OK,
    STATUS_STALE,
    STATUS_UNKNOWN,
    check_entry,
    check_implementation_hashes,
    failures,
    file_sha256,
)


ROOT = Path(__file__).resolve().parents[1]


class ImplementationHashChecks(unittest.TestCase):
    def test_current_tree_passes(self):
        self.assertEqual(failures(check_implementation_hashes(ROOT)), [])

    def test_capacity_string_form_matches_analyze_script(self):
        observed = file_sha256(ROOT / "tools" / "analyze_validation_capacity.py")
        reg_path = ROOT / "registries" / "pilot-001-validation-capacity.json"
        recorded = json.loads(reg_path.read_text(encoding="utf-8"))[
            "implementation_sha256"
        ]
        self.assertEqual(observed, recorded)

    def test_unknown_hash_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "registries").mkdir()
            (root / "tools").mkdir()
            (root / "tools" / "example.py").write_text("v1\n", encoding="utf-8")
            payload = {
                "schema_version": 1,
                "implementation_sha256": {"example.py": "0" * 64},
            }
            (root / "registries" / "pilot-001-example.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            (root / ".git").mkdir()
            result = check_entry(
                root,
                "pilot-001-example.json",
                payload,
                "example.py",
                "0" * 64,
            )
            self.assertEqual(result.status, STATUS_UNKNOWN)

    def test_stale_hash_without_allowlist_fails(self):
        tool = ROOT / "tools" / "audit_published_cohorts.py"
        stale = "b0ab4ab1340139fb221346a14895526f8d62eb105eae098e46b7c4d1fa3f2b52"
        data = {"implementation_sha256": {"audit_published_cohorts.py": stale}}
        result = check_entry(
            ROOT,
            "pilot-001-stale-test.json",
            data,
            "audit_published_cohorts.py",
            stale,
        )
        self.assertEqual(result.status, STATUS_STALE)
        self.assertTrue(result.stale_commit)
        self.assertIn(failures([result]), [[result]])

    def test_stale_hash_with_allowlist_passes_failures_filter(self):
        stale = "b0ab4ab1340139fb221346a14895526f8d62eb105eae098e46b7c4d1fa3f2b52"
        data = {
            "implementation_sha256": {"audit_published_cohorts.py": stale},
            "implementation_hash_drift": {
                "audit_published_cohorts.py": {
                    "allowed_recorded_hash": stale,
                    "git_commit": "4fdfd530e9e8d519eebc699f5e0e8f6a6363a955",
                }
            },
        }
        result = check_entry(
            ROOT,
            "pilot-001-stale-allowed.json",
            data,
            "audit_published_cohorts.py",
            stale,
        )
        self.assertEqual(result.status, STATUS_STALE)
        self.assertEqual(failures([result]), [])

    def test_current_hash_is_ok(self):
        tool = ROOT / "tools" / "audit_published_cohorts.py"
        current = file_sha256(tool)
        data = {"implementation_sha256": {"audit_published_cohorts.py": current}}
        result = check_entry(
            ROOT,
            "pilot-001-current.json",
            data,
            "audit_published_cohorts.py",
            current,
        )
        self.assertEqual(result.status, STATUS_OK)


if __name__ == "__main__":
    unittest.main()
