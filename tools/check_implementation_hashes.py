"""Verify registry implementation_sha256 entries against files on disk.

Each pilot-001-* registry may record code fingerprints under
``implementation_sha256`` (object mapping repo-relative paths to SHA-256 hex,
or a single hex string for ``tools/analyze_validation_capacity.py``). Exit 0
when every entry matches; exit 1 and print mismatches otherwise.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRIES = ROOT / "registries"
CAPACITY_TOOL = ROOT / "tools" / "analyze_validation_capacity.py"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_implementation_path(key: str) -> Path:
    direct = ROOT / key
    if direct.is_file():
        return direct
    under_tools = ROOT / "tools" / key
    if under_tools.is_file():
        return under_tools
    raise FileNotFoundError(key)


def iter_implementation_entries():
    for registry_path in sorted(REGISTRIES.glob("pilot-001-*.json")):
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        impl = data.get("implementation_sha256")
        if impl is None:
            continue
        label = registry_path.name
        if isinstance(impl, str):
            yield label, str(CAPACITY_TOOL.relative_to(ROOT)), impl
        elif isinstance(impl, dict):
            for key, expected in impl.items():
                yield label, key, expected
        else:
            raise TypeError(f"{label}: implementation_sha256 must be object or string")


def check_implementation_hashes(root: Path | None = None) -> list[str]:
    global ROOT, REGISTRIES, CAPACITY_TOOL
    if root is not None:
        ROOT = Path(root)
        REGISTRIES = ROOT / "registries"
        CAPACITY_TOOL = ROOT / "tools" / "analyze_validation_capacity.py"

    errors: list[str] = []
    for registry, key, expected in iter_implementation_entries():
        if not isinstance(expected, str) or len(expected) != 64:
            errors.append(f"{registry}: invalid hash for {key!r}")
            continue
        try:
            path = resolve_implementation_path(key)
        except FileNotFoundError:
            errors.append(f"{registry}: missing file for {key!r}")
            continue
        observed = file_sha256(path)
        if observed != expected.lower():
            errors.append(
                f"{registry}: {key} expected {expected} observed {observed}"
            )
    return errors


def main(argv=None) -> int:
    _ = argv
    errors = check_implementation_hashes()
    if errors:
        print("implementation_sha256 mismatch:", file=sys.stderr)
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print("OK: all registry implementation_sha256 entries match files on disk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
