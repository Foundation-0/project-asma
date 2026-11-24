"""Fail if a bare assert statement appears in non-test Python.

python3 -O removes assert statements. A check written as a bare assert then
stops running, and a verifier can print OK and exit 0 on input it should
reject. This guard follows contract R4 (optimizer parity) in the sibling
repository aletheia (spec/LAWS_AND_GATES.md) and Gate 7 R4 in cave-expedition
(verification/PROTOCOL.md). Write such checks as explicit raises.

Scope: Python files under tools/, results/, assets/ and studies/ that Git
tracks, plus files there that are untracked but not ignored, so a new file is
checked before it is staged. Git-ignored local files are not read. A second
test fails if Git tracks a Python file outside tests/ and those four
directories, so a new location needs a scope decision. tests/ is exempt:
unittest checks are method calls, which -O keeps.
"""

import ast
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNED = ("tools", "results", "assets", "studies")
EXEMPT = ("tests",)
GIT_CHECKOUT = bool(shutil.which("git")) and (ROOT / ".git").exists()


def bare_asserts(source, name="<source>"):
    """Return the line numbers of assert statements in Python source."""
    tree = ast.parse(source, filename=name)
    return sorted(node.lineno for node in ast.walk(tree) if isinstance(node, ast.Assert))


def git_python_files(*arguments):
    listed = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z", *arguments],
        capture_output=True,
        check=True,
    )
    return sorted(name for name in listed.stdout.decode("utf-8").split("\0") if name.endswith(".py"))


class DetectorTest(unittest.TestCase):
    def test_finds_assert_statements_only(self):
        self.assertEqual(bare_asserts("x = 1\nassert x == 1, 'message'\n"), [2])
        self.assertEqual(bare_asserts("def f(x):\n    if x:\n        assert x\n"), [3])
        self.assertEqual(bare_asserts("if not ok:\n    raise AssertionError('message')\n"), [])
        self.assertEqual(bare_asserts("self.assertTrue(x)\nassertion = 1\n"), [])


@unittest.skipUnless(GIT_CHECKOUT, "no Git checkout to list files from")
class RepositoryTest(unittest.TestCase):
    maxDiff = None  # list every offending file:line

    def test_no_bare_assert_in_scanned_directories(self):
        files = git_python_files("--cached", "--others", "--exclude-standard", "--", *SCANNED)
        self.assertIn("tools/verify_identifiability_and_c20.py", files)
        found = []
        for name in files:
            path = ROOT / name
            if path.is_file():  # skip a tracked file deleted from the work tree
                found += [f"{name}:{line}" for line in bare_asserts(path.read_bytes(), name)]
        self.assertEqual(found, [], "python3 -O drops these checks; raise explicitly instead")

    def test_tracked_python_is_scanned_or_exempt(self):
        outside = [name for name in git_python_files("--cached") if name.split("/", 1)[0] not in SCANNED + EXEMPT]
        self.assertEqual(outside, [], "add the directory to SCANNED or record why it is exempt")


if __name__ == "__main__":
    unittest.main()
