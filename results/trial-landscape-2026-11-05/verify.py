#!/usr/bin/env python3
"""Offline integrity of a frozen metadata aggregate, not source reconstruction."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools import audit_trial_landscape as audit

RESULT = Path(__file__).resolve().parent
CERTIFICATE = RESULT / 'certificate.json'
REPORT = ROOT / 'docs/trial-landscape-2026-11-05.md'
BEGIN = '<!-- BEGIN GENERATED TRIAL COUNTS -->'
END = '<!-- END GENERATED TRIAL COUNTS -->'
PINNED = [
    'protocols/trial-landscape-keywords-v1.json',
    'tools/audit_trial_landscape.py',
    'results/trial-landscape-2026-11-05/certificate.json',
    'results/trial-landscape-2026-11-05/verify.py',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-manifest', action='store_true',
                        help='deliberately pin current validated artifact/code/spec bytes')
    args = parser.parse_args()
    snapshot = audit._read_snapshot(CERTIFICATE)
    expected = ''.join(hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                       + '  ' + name + '\n' for name in PINNED)
    manifest = RESULT / 'SHA256SUMS'
    report = REPORT.read_text(encoding='utf-8')
    if report.count(BEGIN) != 1 or report.count(END) != 1:
        raise ValueError('Generated report table markers missing or duplicated.')
    table = report.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    if table != audit.render_report_table(snapshot).strip():
        raise ValueError('Report table differs from frozen certificate.')
    if args.write_manifest:
        manifest.write_text(expected, encoding='utf-8')
    if manifest.read_text(encoding='utf-8') != expected:
        raise ValueError('Frozen artifact/code/spec manifest differs.')
    print('PASS: frozen aggregate schema, arithmetic, provenance, code/spec hashes and report table.')
    print('This offline check cannot reconstruct historical classifications or validate trial claims.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('FAIL: frozen trial-landscape verification; inspect local artifacts.', file=sys.stderr)
        sys.exit(1)
