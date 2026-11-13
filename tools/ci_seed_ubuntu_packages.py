#!/usr/bin/env python3
"""CI only: pre-fill the build cache with the pinned Ubuntu development packages.

snapshot.ubuntu.com is intermittently unavailable. Each package is fetched from
its pinned URL and, failing that, from Launchpad's copy of the same file. A file
is cached only when its size and SHA256 match runtime/source-adapter-python.json,
and tools/build_source_adapter_runtime.py re-checks both when it reads the cache,
so the fallback host cannot change the bytes that are built. This script never
fails the job: if no source works, the build step retries the pinned URL itself.
No study data are involved.
"""

import argparse
import json
import time
from pathlib import Path

from pinned_ubuntu_fetch import read_verified

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "runtime/source-adapter-python.json"


def seed_one(cache, record):
    name = record["filename"]
    try:
        read_verified(record, cache, "linux/amd64")
    except Exception as error:
        print(f"{name}: unavailable ({error})")
        return False
    print(f"{name}: cached (size and SHA256 match the pin)")
    return True


def seed(cache, rounds=3, pause=20):
    cache.mkdir(parents=True, exist_ok=True)
    pending = json.loads(LOCK.read_text())["development_packages"]
    for round_number in range(1, rounds + 1):
        pending = [record for record in pending if not seed_one(cache, record)]
        if not pending:
            return
        if round_number < rounds:
            time.sleep(pause * round_number)
    for record in pending:
        print(f"{record['filename']}: not cached; the build step will retry the pinned URL")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cache", type=Path, help="Directory passed to the builder as --source-cache")
    seed(parser.parse_args(argv).cache)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
