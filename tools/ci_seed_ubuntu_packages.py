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
import hashlib
import json
from pathlib import Path
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "runtime/source-adapter-python.json"
LAUNCHPAD = "https://launchpad.net/ubuntu/+archive/primary/+files/"


def matches(body, record):
    return len(body) == record["bytes"] and hashlib.sha256(body).hexdigest() == record["sha256"]


def fetch(url, record):
    with urllib.request.urlopen(url, timeout=45) as response:
        body = response.read(record["bytes"] + 1)
    if not matches(body, record):
        raise ValueError("bytes do not match the pinned size and SHA256")
    return body


def seed_one(cache, record):
    name = record["filename"]
    if Path(name).name != name:
        raise ValueError(f"unsafe filename in lock: {name!r}")
    target = cache / name
    if target.is_file():
        if matches(target.read_bytes(), record):
            print(f"{name}: already cached")
            return True
        target.unlink()
    for url in (record["url"], LAUNCHPAD + urllib.parse.quote(name)):
        host = urllib.parse.urlsplit(url).hostname
        try:
            body = fetch(url, record)
        except Exception as error:
            print(f"{name}: {host} unavailable ({error})")
            continue
        partial = cache / (name + ".partial")
        partial.write_bytes(body)
        partial.replace(target)
        print(f"{name}: cached from {host} (size and SHA256 match the pin)")
        return True
    return False


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
