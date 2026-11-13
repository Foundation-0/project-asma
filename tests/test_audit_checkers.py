"""Integrity audit behaviour with fast, isolated probes."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_checkers as audit


class AuditCheckersTests(unittest.TestCase):
    def test_skip_run_structure(self):
        report = audit.build_audit(run_checks=False)
        self.assertEqual(report["summary"]["verified_claims"], 41)

    def test_stale_audit_fails_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "audit.json"
            path.write_text(json.dumps({"schema_version": 0}) + "\n", encoding="utf-8")
            original = audit.AUDIT_JSON
            audit.AUDIT_JSON = path
            try:
                self.assertEqual(audit.main(["--check", "--skip-run"]), 1)
            finally:
                audit.AUDIT_JSON = original

    def test_committed_audit_replays(self):
        code = subprocess.run(
            [sys.executable, str(ROOT / "tools/audit_checkers.py"), "--check"],
            cwd=ROOT,
            check=False,
        ).returncode
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
