#!/usr/bin/env python3
"""Add pinned CPython to the validated local R image; no study data are fetched."""

import argparse
import gzip
import hashlib
import io
import json
import lzma
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request

from build_synthetic_runtime import ROOT, local_docker_env

sys.path.insert(0, str(ROOT))

from pilot001_first_run.cross_arch_equivalence import compute_synthetic_build_identity  # noqa: E402

LOCKS = {
    "linux/amd64": ROOT / "runtime/source-adapter-python.json",
    "linux/arm64": ROOT / "runtime/source-adapter-python-arm64.json",
}
VALIDATION = {
    "linux/amd64": ROOT / "registries/pilot-001-synthetic-validation.json",
    "linux/arm64": ROOT / "registries/pilot-001-synthetic-validation-arm64.json",
}
FAILURE = "ERROR: source-adapter runtime build failed; no study data were accessed."
MAX_SOURCE_BYTES = 32 * 1024**2
MAX_TAR_BYTES = 150 * 1024**2
ALLOWED_HOSTS = {"www.python.org", "snapshot.ubuntu.com", "changelogs.ubuntu.com"}


def checked_download(record, cache=None):
    name = record["filename"]
    if Path(name).name != name or not 0 < record["bytes"] <= MAX_SOURCE_BYTES:
        raise ValueError(FAILURE)
    url = urllib.parse.urlsplit(record["url"])
    if url.scheme != "https" or url.hostname not in ALLOWED_HOSTS or url.username or url.password:
        raise ValueError(FAILURE)
    path = None if cache is None else cache / name
    if path is not None and path.is_file():
        if path.stat().st_size != record["bytes"]:
            raise ValueError(FAILURE)
        body = path.read_bytes()
    else:
        with urllib.request.urlopen(record["url"], timeout=60) as response:
            final = urllib.parse.urlsplit(response.geturl())
            if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
                raise ValueError(FAILURE)
            body = response.read(record["bytes"] + 1)
    if len(body) != record["bytes"] or hashlib.sha256(body).hexdigest() != record["sha256"]:
        raise ValueError(FAILURE)
    return body


def checked_python_tar(body, record):
    inflater = lzma.LZMADecompressor()
    tar = inflater.decompress(body, max_length=MAX_TAR_BYTES + 1)
    if len(tar) > MAX_TAR_BYTES or not inflater.eof or inflater.unused_data:
        raise ValueError(FAILURE)
    with tarfile.open(fileobj=io.BytesIO(tar), mode="r:") as archive:
        member = archive.getmember(record["license_notice"]["path"])
        if not member.isfile() or member.size != record["license_notice"]["bytes"]:
            raise ValueError(FAILURE)
        notice = archive.extractfile(member).read()
    if hashlib.sha256(notice).hexdigest() != record["license_notice"]["sha256"]:
        raise ValueError(FAILURE)
    # The image lacks xz tools. Convert verified bytes in the host's memory;
    # nothing is extracted on the host, and no source-study data are involved.
    return gzip.compress(tar, compresslevel=1, mtime=0)


def build(cache=None, accept_rebuilt_base=False, platform="linux/amd64"):
    lock_file = LOCKS[platform]
    record = json.loads(lock_file.read_text())
    validation_path = VALIDATION[platform]
    prior = json.loads(validation_path.read_text()) if validation_path.is_file() else None
    dockerfile = ROOT / "runtime/Dockerfile.source-adapter"
    identity_pin = record.get("base_synthetic_build_identity")
    expected_base = record.get("base_image_id")
    if platform == "linux/arm64":
        if not identity_pin or compute_synthetic_build_identity(platform) != identity_pin:
            raise ValueError(FAILURE)
        if prior and prior.get("synthetic_build_identity") != identity_pin:
            raise ValueError(FAILURE)
    elif prior and expected_base and expected_base != prior["environment"]["runtime_image_id"]:
        raise ValueError(FAILURE)
    if (record["schema_version"] != 1 or record["platform"] != platform or
            dockerfile.read_text().splitlines()[0] != "FROM " + record["base_image_tag"]):
        raise ValueError(FAILURE)
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    environment = local_docker_env()
    def inspect(tag):
        result = subprocess.run(docker + ["image", "inspect", tag], env=environment,
                                check=True, capture_output=True, text=True, timeout=60)
        return json.loads(result.stdout)[0]
    base = inspect(record["base_image_tag"])
    if platform == "linux/arm64":
        rebuilt = False
    else:
        # Image IDs are local to the daemon that built them. A rebuilt base needs an
        # explicit opt-in; every other check still applies, and the output is marked.
        rebuilt = base["Id"] != expected_base if expected_base else True
        if rebuilt and not (accept_rebuilt_base and re.fullmatch(r"sha256:[0-9a-f]{64}", base["Id"])):
            raise ValueError(FAILURE)
    source = checked_download(record["cpython"], cache)
    converted = checked_python_tar(source, record["cpython"])
    with tempfile.TemporaryDirectory(prefix="asma-source-adapter-build-") as location:
        context = Path(location)
        (context / "development").mkdir()
        (context / "notices").mkdir()
        (context / "python-source.tar.gz").write_bytes(converted)
        for package in record["development_packages"]:
            (context / "development" / package["filename"]).write_bytes(checked_download(package, cache))
            notice = package["license_notice"]
            (context / "notices" / notice["filename"]).write_bytes(checked_download(notice, cache))
        shutil.copyfile(dockerfile, context / "Dockerfile")
        subprocess.run(docker + ["build", "--pull=false", "--network=none", "--platform=" + platform,
                                 "-t", record["image_tag"], str(context)],
                       env=environment, check=True, timeout=1800)
    image = inspect(record["image_tag"])
    if (inspect(record["base_image_tag"])["Id"] != base["Id"] or
            image["RootFS"]["Layers"][:len(base["RootFS"]["Layers"])] != base["RootFS"]["Layers"]):
        raise ValueError(FAILURE)
    output = {"image_id": image["Id"], "base_image_id": base["Id"],
              "scope": "Source-adapter software runtime only; no study data"}
    if rebuilt:
        output.update(base_rebuilt=True, recorded_base_image_id=expected_base,
                      status="Rebuilt base: record and validate as a new runtime; "
                             "never substitute it for the recorded image")
    print(json.dumps(output, sort_keys=True))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cache", type=Path, help="Optional verified CPython/Ubuntu archive cache")
    parser.add_argument("--accept-rebuilt-base", action="store_true",
                        help="Allow a locally rebuilt base whose image ID differs from the recorded one; "
                             "the result is a new runtime to record and validate")
    parser.add_argument(
        "--platform",
        choices=sorted(LOCKS),
        default="linux/amd64",
        help="Target platform for the pinned source-adapter runtime",
    )
    arguments = parser.parse_args(argv)
    try:
        build(arguments.source_cache, arguments.accept_rebuilt_base, arguments.platform)
        return 0
    except Exception:
        print(FAILURE, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
