#!/usr/bin/env python3
"""Verify one pinned public cell-line MGF and retain one linked experimental spectrum.

This is locator verification, not a peptide search or independent identification.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import ssl
import sys
import urllib.request

try:
    from .audit_cdr2l_source_psm import BASE, FILES, TARGET, require
except ImportError:
    from audit_cdr2l_source_psm import BASE, FILES, TARGET, require

NAME = 'F1202000304_PF_MDAMB231_IFN-positive_replicate_5_pool_6_Immunopeptidomics-classII.mgf'
SIZE = 72832889
SHA1 = '56fd6906ed468329c56962eb24a5429373265a60'
INDEX = 22949
LIMIT = 90_000_000
FORMAT_SOURCE = 'https://www.ebi.ac.uk/ols4/api/ontologies/ms/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMS_1000774'


def inspect_mgf(stream, *, expected_size, expected_sha1, index, limit=LIMIT):
    require(type(index) is int and index >= 0, 'index must be a nonnegative integer')
    sha1, sha256 = hashlib.sha1(), hashlib.sha256()
    count = spectra = 0
    inside = False
    selected = None
    for_line = 0
    while True:
        raw = stream.readline(1_000_001)
        if not raw:
            break
        count += len(raw)
        require(count <= limit, 'MGF byte cap exceeded')
        require(len(raw) <= 1_000_000, 'MGF line cap exceeded')
        sha1.update(raw); sha256.update(raw)
        line = raw.decode('utf-8').strip()
        for_line += 1
        if line == 'BEGIN IONS':
            require(not inside, 'nested MGF block')
            inside = True
            if spectra == index:
                selected = {'zero_based_index': index, 'one_based_ordinal': index + 1,
                            'metadata': {}, 'peaks': [], 'start_line': for_line}
        elif line == 'END IONS':
            require(inside, 'unmatched MGF end')
            if spectra == index:
                selected['end_line'] = for_line
            inside = False
            spectra += 1
        elif inside and spectra == index and line and not line.startswith(('#', ';', '!', '/')):
            if '=' in line:
                key, value = line.split('=', 1)
                require(key not in selected['metadata'], 'duplicate selected metadata')
                selected['metadata'][key] = value
            else:
                fields = line.split()
                require(len(fields) in (2, 3), 'unexpected selected peak columns')
                values = [Decimal(x) for x in fields[:2]]
                require(all(x.is_finite() and x >= 0 for x in values), 'invalid selected peak')
                require(values[0] > 0, 'invalid selected mass')
                selected['peaks'].append(fields)  # Preserve original decimal strings, optional charge.
                require(len(selected['peaks']) <= 100_000, 'selected peak cap exceeded')
    require(not inside, 'truncated MGF block')
    require(count == expected_size, 'MGF pinned size mismatch')
    require(sha1.hexdigest() == expected_sha1, 'MGF pinned SHA1 mismatch')
    require(selected is not None and 'end_line' in selected, 'selected spectrum absent')
    require(selected['peaks'], 'selected spectrum has no peaks')
    return {'bytes': count, 'sha1': sha1.hexdigest(), 'sha256': sha256.hexdigest(),
            'complete': True, 'total_spectra': spectra, 'selected_spectrum': selected}


def source_link(certificate):
    require(certificate.get('project') == 'PXD023044', 'unexpected identification project')
    require(certificate.get('assay_id') == 18456218 and certificate.get('target_sequence') == TARGET,
            'unexpected identification target or assay')
    require(certificate['all_three_pinned_files_complete'] is True, 'incomplete identification certificate')
    files = certificate['files']
    require(len(files) == len(FILES), 'missing or extra source files')
    for record, (name, size, checksum) in zip(files, FILES):
        require(record.get('file') == name and record.get('url') == BASE + name,
                'unexpected identification source file')
        require(record.get('sha1') == checksum and record.get('api_sha1') == checksum
                and record.get('expanded_bytes') == size and record.get('api_size') == size
                and record.get('xml_complete') is True
                and record.get('metadata_size_domain') == 'expanded_mzidentml'
                and record.get('metadata_checksum_domain') == 'served_gzip',
                'source identity pins do not match')
    results = [r for f in certificate['files'] for r in f['matching_results']]
    require(len(results) == 1, 'expected exactly one linked identification')
    result = results[0]
    require(result['attributes']['spectrumID'] == 'index=22949', 'unexpected spectrum index')
    require(result['spectra_data']['file_name'] == NAME, 'unexpected linked MGF')
    formats = result['spectra_data'].get('SpectrumIDFormat', [])
    require(len(formats) == 1 and formats[0]['accession'] == 'MS:1000774', 'unproved index convention')
    require(len(result['items']) == 1, 'ambiguous identification item')
    declarations = [p for f in files for p in f['matching_peptides']]
    require(len(declarations) == 1 and declarations[0]['modifications'] == [],
            'expected one unmodified target declaration')
    require(result['items'][0]['attributes']['peptide_ref'] == declarations[0]['id'],
            'identification does not reference target declaration')
    return result


def live(certificate_path):
    certificate_bytes = certificate_path.read_bytes()
    linked = source_link(json.loads(certificate_bytes))
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    context = ssl.create_default_context()
    if Path('/etc/ssl/cert.pem').is_file():
        context.load_verify_locations(cafile='/etc/ssl/cert.pem')
    opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=context))
    with opener.open(BASE + NAME, timeout=60) as response:
        require(response.status == 200, 'incomplete HTTP response')
        require(response.headers.get('Content-Encoding', 'identity') == 'identity', 'unexpected content encoding')
        require(int(response.headers['Content-Length']) == SIZE, 'HTTP length differs from pin')
        headers = {k: response.headers.get(k) for k in ('Content-Length', 'Last-Modified', 'ETag')}
        result = inspect_mgf(response, expected_size=SIZE, expected_sha1=SHA1, index=INDEX)
    metadata = result['selected_spectrum']['metadata']
    item = linked['items'][0]['attributes']
    require(metadata.get('TITLE') == linked['attributes']['spectrumID'],
            'selected TITLE does not match linked spectrumID')
    require(metadata.get('SCANS'), 'selected spectrum missing SCANS')
    require(metadata.get('PEPMASS'), 'selected spectrum missing PEPMASS')
    precursor = Decimal(metadata['PEPMASS'].split()[0])
    experimental = Decimal(item['experimentalMassToCharge'])
    charge_matches = metadata.get('CHARGE') == item['chargeState'] + '+'
    require(precursor == experimental,
            'selected PEPMASS does not match linked experimentalMassToCharge')
    require(charge_matches, 'selected CHARGE does not match linked chargeState')
    result.update(schema_version=1, project='PXD023044', source_license_metadata='CC0',
        url=BASE+NAME, file=NAME, http_metadata=headers,
        retrieved_utc=datetime.now(timezone.utc).isoformat(),
        identification_certificate_sha256=hashlib.sha256(certificate_bytes).hexdigest(),
        identification_link=linked, index_definition_source=FORMAT_SOURCE,
        index_definition='Spectrum number in the file, starting from 0 (MS:1000774)',
        precursor_comparison={'mgf': str(precursor), 'mzidentml_experimental': str(experimental),
            'difference_mz': str(precursor-experimental), 'exact_decimal_match': precursor == experimental,
            'charge_matches': charge_matches},
        independent_peptide_identification=False, spectrum_researched_or_rescored=False,
        implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    return result


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CERT = ROOT / 'registries/cdr2l-spectrum-locator-2026-11-06.json'
DEFAULT_ID = ROOT / 'registries/cdr2l-source-identification-2026-11-06.json'

# Hash of this file when the 2026-11-06 spectrum locator certificate was produced.
PRODUCING_SCRIPT_SHA256 = '41cf8988d1fbc6a7ccbda09a2cdbc80cbdbc8d099ead661a996536120be8a7c3'
PINNED_IDENTIFICATION_CERTIFICATE_SHA256 = (
    '943f25251323f288069bc03046dde569e46ddca88ca2cb1cd541d20f764be4cf'
)
PINNED_MGF_SHA256 = '19221e28bf764c2a1030ccafb1531150982e863f71ad6525b71215bd94c2f974'


def check_certificate(path: Path, identification: Path) -> None:
    require(path.is_file(), f'missing certificate {path}')
    require(identification.is_file(), f'missing identification certificate {identification}')
    report = json.loads(path.read_text(encoding='utf-8'))
    stored_impl = report.get('implementation_sha256')
    current_impl = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    require(stored_impl in {current_impl, PRODUCING_SCRIPT_SHA256}, 'implementation_sha256 mismatch')
    id_digest = hashlib.sha256(identification.read_bytes()).hexdigest()
    require(id_digest == PINNED_IDENTIFICATION_CERTIFICATE_SHA256, 'identification certificate drift')
    require(report.get('identification_certificate_sha256') == id_digest, 'identification digest mismatch')
    selected = report.get('selected_spectrum') or {}
    require(report.get('complete') is True and report.get('bytes') == SIZE and report.get('sha1') == SHA1,
            'source pin drift')
    require(report.get('sha256') == PINNED_MGF_SHA256, 'source pin drift')
    require(selected.get('zero_based_index') == INDEX, 'spectrum index mismatch')
    require(len(selected.get('peaks') or []) == 173, 'peak count mismatch')
    meta = selected.get('metadata') or {}
    require(meta.get('SCANS') == '23848' and meta.get('CHARGE') == '3+'
            and meta.get('PEPMASS') == '614.999', 'metadata mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--check', action='store_true', help='Verify the committed spectrum locator certificate offline')
    parser.add_argument('--certificate', type=Path, default=DEFAULT_CERT)
    parser.add_argument('--identification-certificate', type=Path, default=DEFAULT_ID)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.check:
        try:
            check_certificate(args.certificate, args.identification_certificate)
        except ValueError as error:
            print(f'FAIL: {error}', file=sys.stderr)
            return 1
        print('PASS: offline spectrum locator certificate digest and linkage')
        return 0
    if not args.live:
        parser.print_help(); return 0
    require(args.identification_certificate and args.output, 'certificate and new output required')
    require(not args.output.exists(), 'preserve existing output')
    result = live(args.identification_certificate)
    with args.output.open('x') as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
