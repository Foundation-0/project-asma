"""Offline integrity checks for the source-adapter Python runtime builder."""

import gzip
import hashlib
import io
import json
import lzma
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_source_adapter_runtime as builder


class SourceAdapterRuntimeTests(unittest.TestCase):
    def source(self, body=b"abstract"):
        return {"filename": "abstract.tar.xz", "url": "https://www.python.org/abstract.tar.xz",
                "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}

    def python_archive(self):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w") as archive:
            member = tarfile.TarInfo("Abstract/LICENSE")
            member.size = len(b"abstract notice")
            archive.addfile(member, io.BytesIO(b"abstract notice"))
        tar = stream.getvalue()
        return lzma.compress(tar), tar, {"license_notice": {
            "path": "Abstract/LICENSE", "bytes": len(b"abstract notice"),
            "sha256": hashlib.sha256(b"abstract notice").hexdigest()}}

    def test_cache_requires_exact_content_and_length(self):
        record = self.source()
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            path = cache / record["filename"]
            path.write_bytes(b"abstract")
            self.assertEqual(builder.checked_download(record, cache), b"abstract")
            for changed in (b"corrupt!", b"abstractx"):
                path.write_bytes(changed)
                with self.assertRaises(ValueError):
                    builder.checked_download(record, cache)

    def test_network_read_is_bounded_and_rejects_truncation_or_extra_bytes(self):
        record = self.source()
        for body in (b"abstract", b"abstractx", b"abstrac"):
            response = io.BytesIO(body)
            response.geturl = lambda: record["url"]
            with mock.patch.object(builder.urllib.request, "urlopen", return_value=response):
                if body == b"abstract":
                    self.assertEqual(builder.checked_download(record), body)
                else:
                    with self.assertRaises(ValueError):
                        builder.checked_download(record)

    def test_disallows_other_hosts_credentials_paths_and_http(self):
        for changed in ({"url": "https://example.invalid/abstract"},
                        {"url": "http://www.python.org/abstract"},
                        {"url": "https://user:secret@www.python.org/abstract"},
                        {"filename": "../abstract"}):
            with self.assertRaises(ValueError):
                builder.checked_download(dict(self.source(), **changed))

    def test_redirect_must_remain_on_allowed_https_host(self):
        response = io.BytesIO(b"abstract")
        response.geturl = lambda: "https://example.invalid/abstract"
        with mock.patch.object(builder.urllib.request, "urlopen", return_value=response), self.assertRaises(ValueError):
            builder.checked_download(self.source())

    def test_verified_xz_converts_to_equivalent_gzip_without_host_extraction(self):
        body, tar, record = self.python_archive()
        converted = builder.checked_python_tar(body, record)
        self.assertEqual(gzip.decompress(converted), tar)
        self.assertEqual(builder.checked_python_tar(body, record), converted)

    def test_source_conversion_rejects_truncation_and_concatenated_streams(self):
        body, _, record = self.python_archive()
        for changed in (body[:-1], body + b"trailing", body + body):
            with self.assertRaises(ValueError):
                builder.checked_python_tar(changed, record)

    def test_source_conversion_checks_license_identity(self):
        body, _, record = self.python_archive()
        record["license_notice"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            builder.checked_python_tar(body, record)

    def test_source_conversion_caps_inflated_size(self):
        body, _, record = self.python_archive()
        with mock.patch.object(builder, "MAX_TAR_BYTES", 64), self.assertRaises(ValueError):
            builder.checked_python_tar(body, record)

    def test_wrong_local_base_image_stops_before_source_download_or_build(self):
        result = subprocess.CompletedProcess([], 0, json.dumps([{"Id": "sha256:" + "0" * 64}]), "")
        with mock.patch.object(builder.subprocess, "run", return_value=result) as run, \
                mock.patch.object(builder, "checked_download") as download, self.assertRaises(ValueError):
            builder.build()
        download.assert_not_called()
        self.assertEqual(run.call_count, 1)
        self.assertIn("--host=unix:///var/run/docker.sock", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
