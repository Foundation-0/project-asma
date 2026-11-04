"""Tests for registry implementation hash verification."""

import json
import tempfile
import unittest
from pathlib import Path

from tools.check_implementation_hashes import check_implementation_hashes, file_sha256


class ImplementationHashChecks(unittest.TestCase):
    def test_current_tree_matches_registries(self):
        errors = check_implementation_hashes()
        self.assertEqual(errors, [], "\n".join(errors))

    def test_detects_single_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reg = root / "registries"
            reg.mkdir()
            tool = root / "tools"
            tool.mkdir()
            target = tool / "example.py"
            target.write_text("v1\n", encoding="utf-8")
            payload = {
                "schema_version": 1,
                "implementation_sha256": {"example.py": "0" * 64},
            }
            (reg / "pilot-001-example.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            errors = check_implementation_hashes(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("pilot-001-example.json", errors[0])

    def test_capacity_string_form_uses_analyze_script(self):
        observed = file_sha256(
            Path(__file__).resolve().parents[1] / "tools" / "analyze_validation_capacity.py"
        )
        reg_path = (
            Path(__file__).resolve().parents[1]
            / "registries"
            / "pilot-001-validation-capacity.json"
        )
        recorded = json.loads(reg_path.read_text(encoding="utf-8"))[
            "implementation_sha256"
        ]
        self.assertEqual(observed, recorded)


if __name__ == "__main__":
    unittest.main()
