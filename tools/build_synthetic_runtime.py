#!/usr/bin/env python3
"""Build the pinned R runtime for synthetic fixtures; never fetch study data."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "runtime/synthetic-packages.json"
MAX_SOURCE_BYTES = 20_000_000
FAILURE = "ERROR: synthetic runtime build failed; no research data were accessed."


def checked_archive(record, source_cache=None):
    name = f"{record['package']}_{record['version']}.tar.gz"
    if Path(name).name != name or not 0 < record["bytes"] < MAX_SOURCE_BYTES:
        raise ValueError(FAILURE)
    cached = None if source_cache is None else source_cache / name
    if cached is not None and cached.is_file():
        if cached.stat().st_size != record["bytes"]:
            raise ValueError(FAILURE)
        body = cached.read_bytes()
    else:
        parsed = urllib.parse.urlsplit(record["url"])
        if parsed.scheme != "https" or parsed.hostname != "cran.r-project.org":
            raise ValueError(FAILURE)
        with urllib.request.urlopen(record["url"], timeout=60) as response:
            if urllib.parse.urlsplit(response.geturl()).scheme != "https":
                raise ValueError(FAILURE)
            body = response.read(record["bytes"] + 1)
    if len(body) != record["bytes"] or hashlib.sha256(body).hexdigest() != record["sha256"]:
        raise ValueError(FAILURE)
    return name, body


def local_docker_env():
    environment = os.environ.copy()
    for name in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"):
        environment.pop(name, None)
    return environment


def build(tag, source_cache=None):
    lock = json.loads(LOCK.read_text())
    dockerfile = ROOT / "runtime/Dockerfile.synthetic"
    if lock["schema_version"] != 1 or dockerfile.read_text().splitlines()[0] != "FROM " + lock["base_image"]:
        raise ValueError(FAILURE)
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    env = local_docker_env()
    subprocess.run(docker + ["info", "--format", "{{.ServerVersion}}"], env=env, check=True)
    with tempfile.TemporaryDirectory(prefix="asma-synthetic-build-") as location:
        context = Path(location)
        (context / "packages").mkdir()
        for record in lock["packages_in_install_order"]:
            name, body = checked_archive(record, source_cache)
            (context / "packages" / name).write_bytes(body)
        shutil.copyfile(dockerfile, context / "Dockerfile")
        shutil.copyfile(ROOT / "runtime/install.R", context / "install.R")
        subprocess.run(docker + ["build", "--network=none", "--platform=" + lock["platform"],
                                 "-t", tag, str(context)], env=env, check=True, timeout=3600)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="asma-synthetic:4.4.3")
    parser.add_argument("--source-cache", type=Path, help="Optional directory of already downloaded package archives")
    args = parser.parse_args(argv)
    try:
        build(args.tag, args.source_cache)
    except Exception:
        print(FAILURE, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
