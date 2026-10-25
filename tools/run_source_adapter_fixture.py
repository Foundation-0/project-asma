#!/usr/bin/env python3
"""Exercise source parsing and model integration using generated fixtures only."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

from build_synthetic_runtime import ROOT, local_docker_env
from probe_execution_conditions import execution_options

FAILURE = 'ERROR: source-adapter fixture failed; no row-level details emitted.'
R_SCOPE = 'Synthetic source-adapter integration only'


def run_fixture():
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    image = json.loads((ROOT / 'registries/pilot-001-source-adapter-runtime.json').read_text())['environment']['runtime_image_id']
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', image):
        raise ValueError(FAILURE)
    docker = ['docker', '--host=unix:///var/run/docker.sock']
    environment = local_docker_env()
    name = 'asma-source-fixture-' + uuid.uuid4().hex
    launched = False
    try:
        identity = subprocess.run(docker + ['image', 'inspect', image, '--format', '{{.Id}}'],
                                  env=environment, check=True, capture_output=True, text=True, timeout=30)
        if identity.stdout.strip() != image or identity.stderr:
            raise ValueError(FAILURE)
        launched = True
        process = subprocess.run(docker + ['run', '--name', name, '--rm'] +
                                 execution_options() + [image, '/opt/python/bin/python3', '-I', '-B',
                                                        'tools/check_source_adapter.py'],
                                 env=environment, check=True, capture_output=True,
                                 text=True, timeout=300)
        if process.stderr:
            raise ValueError(FAILURE)
        observed = json.loads(process.stdout)
        if observed.get('scope') != R_SCOPE:
            raise ValueError(FAILURE)
    finally:
        if launched:
            # Only this synthetic invocation's UUID; no private payload in argv.
            subprocess.run(docker + ['rm', '--force', name], env=environment,
                           capture_output=True, timeout=30, check=False)
    files = ['tools/source_data_adapter.py', 'R/asma_source.R', 'R/asma_input.R',
             'R/asma_core.R', 'R/asma_models.R', 'tools/check_source_adapter.R',
             'tools/run_source_adapter_fixture.py', 'tools/check_source_adapter.py',
             'tools/build_source_adapter_runtime.py', 'runtime/Dockerfile.source-adapter',
             'runtime/source-adapter-python.json', 'registries/pilot-001-source-adapter-runtime.json',
             'tests/source_adapter_fixture.py',
             'tests/r/test_source.R', 'tests/r/synthetic_fixture.R',
             'tests/test_source_data_adapter.py', 'tests/test_source_adapter_runner.py',
             'tests/test_source_adapter_runtime.py',
             'tools/probe_execution_conditions.py', 'tools/build_synthetic_runtime.py',
             'tools/audit_author_archive.py', 'tools/audit_author_features.py',
             'tools/audit_matrix_headers.py', 'tools/audit_published_cohorts.py',
             'protocols/pilot-001-reconstruction-decisions.md']
    return {
        'schema_version': 1, 'scope': R_SCOPE,
        'started_at_utc': started, 'finished_at_utc': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': time.monotonic() - timer,
        'runtime_image_id': image,
        'parser_environment': observed['parser_environment'],
        'fixture_provenance': observed['fixture_provenance'],
        'r_validation': observed['r_validation'], 'transport': observed['transport'],
        'implementation_sha256': {file: hashlib.sha256((ROOT / file).read_bytes()).hexdigest()
                                  for file in files},
        'limitations': [
            'Generated XLSX and deflate bytes only; no source-study data were acquired or processed.',
            'Fixture contracts substitute artificial hashes; production defaults still require the pinned study bytes.',
            'One full fivefold repetition exercises the new input path; the earlier 100-repeat synthetic record is separate.',
            'Acquisition mocks do not establish current remote availability or validate real-source parsing.',
            'Python parsing, private transfer and R fitting share the tested container; live network acquisition is mocked and its controls remain unverified.',
            'No fixture predictions, artificial AUROC or models are retained; this is not scientific reproduction.'
        ]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    try:
        result = run_fixture()
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
        return 0
    except Exception:
        print(FAILURE, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
