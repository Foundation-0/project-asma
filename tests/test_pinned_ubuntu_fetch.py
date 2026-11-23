"""Offline checks for pinned Ubuntu fetch helpers."""

import hashlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pinned_ubuntu_fetch as fetch


class PinnedUbuntuFetchTests(unittest.TestCase):
    def record(self, body=b"abstract"):
        return {
            "url": "https://snapshot.ubuntu.com/ubuntu/pool/main/z/zlib/abstract.deb",
            "filename": "abstract.deb",
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
        }

    def test_deb_tries_launchpad_after_primary_failure(self):
        body = b"abstract deb"
        record = self.record(body)
        calls = []

        def urlopen(url, timeout=60):
            calls.append(url)
            if url.startswith("https://snapshot.ubuntu.com"):
                raise OSError("snapshot down")
            response = io.BytesIO(body)
            response.geturl = lambda: url
            return response

        with mock.patch.object(fetch.urllib.request, "urlopen", side_effect=urlopen):
            self.assertEqual(fetch.read_verified(record), body)
        self.assertEqual(len(calls), 2)
        self.assertIn("launchpad.net", calls[1])

    def test_vendor_is_preferred_over_network(self):
        body = b"abstract deb"
        record = self.record(body)
        with tempfile.TemporaryDirectory() as directory:
            vendor = Path(directory)
            path = vendor / "linux-amd64" / record["filename"]
            path.parent.mkdir(parents=True)
            path.write_bytes(body)
            with mock.patch.object(fetch, "VENDOR", vendor), mock.patch.object(
                fetch.urllib.request, "urlopen"
            ) as urlopen:
                self.assertEqual(fetch.read_verified(record, platform="linux/amd64"), body)
            urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
