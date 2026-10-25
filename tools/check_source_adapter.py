#!/usr/bin/env python3
"""Container-only synthetic fixture worker; no live-source execution option."""
import json
from pathlib import Path
import platform
import pyexpat
import subprocess
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
from source_data_adapter import parse_sources
from source_adapter_fixture import make_full_fixture

FAILURE = 'ERROR: source-adapter fixture worker failed; no row-level details emitted.'
SCOPE = 'Synthetic source-adapter integration only'


def run_fixture_worker():
    # Flags disable user initialization paths and bytecode caches explicitly.
    if (sys.version_info[:3] != (3, 12, 14) or not sys.flags.isolated or
            not sys.flags.no_user_site or not sys.dont_write_bytecode or len(sys.argv) != 1):
        raise ValueError(FAILURE)
    packed, clinical, panel, contract = make_full_fixture()
    payload = parse_sources(packed, clinical, panel, contract=contract)
    encoded = json.dumps(payload, separators=(',', ':'), allow_nan=False)
    if len(encoded.encode()) > 4 * 1024**2:
        raise ValueError(FAILURE)
    result = subprocess.run(['Rscript', '--vanilla', '--no-save', '--no-restore',
                             'tools/check_source_adapter.R'],
                            input=encoded, capture_output=True, text=True, check=True, timeout=240)
    if result.stderr:
        raise ValueError(FAILURE)
    observed = json.loads(result.stdout)
    if observed.get('scope') != SCOPE:
        raise ValueError(FAILURE)
    return {
        'scope': SCOPE, 'fixture_provenance': payload['provenance'], 'r_validation': observed,
        'parser_environment': {
            'python': platform.python_version(), 'implementation': platform.python_implementation(),
            'platform': platform.platform(), 'zlib_runtime': zlib.ZLIB_RUNTIME_VERSION,
            'expat': pyexpat.EXPAT_VERSION, 'float_mantissa_bits': sys.float_info.mant_dig,
            'isolated_mode': bool(sys.flags.isolated),
            'user_site_disabled': bool(sys.flags.no_user_site),
            'bytecode_writes_disabled': bool(sys.dont_write_bytecode),
            'scope': 'Python parsing and its R child execute inside the same isolated container.'
        },
        'transport': {'channel': 'in-memory stdin pipe inside the container; no payload file or command argument',
                      'docker_log_driver': 'none', 'container_network': 'none', 'timeout_seconds': 300}
    }


def main():
    try:
        print(json.dumps(run_fixture_worker(), sort_keys=True, allow_nan=False))
        return 0
    except Exception:
        print(FAILURE, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
