"""Synthetic spectra and committed public provenance metadata; no test network."""
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import audit_cdr2l_spectrum_locator as locator
from audit_cdr2l_spectrum_locator import inspect_mgf, source_link, NAME

ROOT = Path(__file__).resolve().parents[1]
BLOCK = b'BEGIN IONS\nTITLE=synthetic\nPEPMASS=614.9990\nCHARGE=3+\n100.000 20.0\n200 0\nEND IONS\n'
LINKED_BLOCK = (b'BEGIN IONS\nTITLE=index=22949\nPEPMASS=614.999\nCHARGE=3+\nSCANS=23848\n'
                b'100.000 20.0\nEND IONS\n')
CERTIFICATE = ROOT / 'registries/cdr2l-source-identification-2026-11-06.json'


def run_live(data):
    class Response(io.BytesIO):
        status = 200
        headers = {'Content-Length': str(len(data))}
    opener = mock.Mock()
    opener.open.return_value = Response(data)
    with mock.patch.object(locator, 'SIZE', len(data)), \
            mock.patch.object(locator, 'SHA1', hashlib.sha1(data).hexdigest()), \
            mock.patch.object(locator, 'INDEX', 0), \
            mock.patch.object(locator.urllib.request, 'build_opener', return_value=opener):
        return locator.live(CERTIFICATE)


def inspect(data, **kw):
    args = dict(expected_size=len(data), expected_sha1=hashlib.sha1(data).hexdigest(), index=0)
    args.update(kw)
    return inspect_mgf(io.BytesIO(data), **args)


class SpectrumLocatorTests(unittest.TestCase):
    def test_zero_based_selection_and_exact_strings(self):
        data = BLOCK + BLOCK.replace(b'synthetic', b'second')
        result = inspect(data, index=1)
        self.assertEqual(result['selected_spectrum']['metadata']['TITLE'], 'second')
        self.assertEqual(result['selected_spectrum']['one_based_ordinal'], 2)
        self.assertEqual(result['selected_spectrum']['peaks'][0], ['100.000', '20.0'])
        self.assertEqual(result['total_spectra'], 2)
        self.assertEqual(result['sha256'], hashlib.sha256(data).hexdigest())

    def test_bad_pins_reject_after_selected_block(self):
        for kw in ({'expected_size': len(BLOCK)+1}, {'expected_sha1': '0'*40}):
            with self.subTest(kw=kw), self.assertRaises(ValueError): inspect(BLOCK, **kw)

    def test_late_truncation_and_bad_blocks_refused(self):
        for data in (BLOCK+b'BEGIN IONS\n', BLOCK+b'END IONS\n', b'BEGIN IONS\n'+BLOCK):
            with self.subTest(data=data), self.assertRaises(ValueError): inspect(data)

    def test_caps_and_absent_index(self):
        for kw in ({'limit': len(BLOCK)-1}, {'index': 1}, {'index': -1}, {'index': True}):
            with self.subTest(kw=kw), self.assertRaises(ValueError): inspect(BLOCK, **kw)
        with self.assertRaises(ValueError): inspect(b'X'*1_000_001)

    def test_malformed_selected_spectrum(self):
        for data in (BLOCK.replace(b'100.000', b'NaN'), BLOCK.replace(b'20.0', b'-1'),
                     BLOCK.replace(b'CHARGE=3+', b'CHARGE=3+\nCHARGE=2+'),
                     BLOCK.replace(b'100.000 20.0', b'100'),
                     b'BEGIN IONS\nEND IONS\n'):
            with self.subTest(data=data), self.assertRaises(ValueError): inspect(data)

    def test_source_certificate_identity_and_format_required(self):
        import copy
        import json
        cert = json.loads((Path(__file__).resolve().parents[1] / 'registries/cdr2l-source-identification-2026-11-06.json').read_text())
        self.assertEqual(source_link(cert)['attributes']['spectrumID'], 'index=22949')
        mutations = [
            lambda c: c.update(project='OTHER'),
            lambda c: c.update(target_sequence='OTHER'),
            lambda c: c.update(assay_id=0),
            lambda c: c['files'].pop(),
            lambda c: c['files'][0].update(sha1='0'*40),
            lambda c: c['files'][0].update(expanded_bytes=1),
            lambda c: c['files'][2]['matching_results'][0]['spectra_data'].pop('SpectrumIDFormat'),
            lambda c: c['files'][2]['matching_results'][0]['attributes'].update(spectrumID='scan=22949'),
            lambda c: c['files'][2]['matching_results'][0]['items'][0]['attributes'].update(peptide_ref='OTHER'),
            lambda c: c['files'][2]['matching_peptides'][0].update(modifications=[{'element': 'SubstitutionModification'}]),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(cert)
            mutate(changed)
            with self.subTest(mutation=mutate), self.assertRaises((ValueError, KeyError)):
                source_link(changed)

    def test_live_accepts_matching_linked_spectrum(self):
        comparison = run_live(LINKED_BLOCK)['precursor_comparison']
        self.assertEqual(comparison['mgf'], '614.999')
        self.assertEqual(comparison['mzidentml_experimental'], '614.9990')
        self.assertTrue(comparison['exact_decimal_match'])
        self.assertTrue(comparison['charge_matches'])

    def test_live_rejects_spectrum_disagreeing_with_linked_identification(self):
        variants = {
            'pepmass': LINKED_BLOCK.replace(b'PEPMASS=614.999', b'PEPMASS=999.999'),
            'charge': LINKED_BLOCK.replace(b'CHARGE=3+', b'CHARGE=2+'),
            'title': LINKED_BLOCK.replace(b'TITLE=index=22949', b'TITLE=wrong-title'),
            'scans': LINKED_BLOCK.replace(b'SCANS=23848\n', b''),
        }
        for name, data in variants.items():
            with self.subTest(variant=name), self.assertRaises(ValueError):
                run_live(data)

    def test_package_import(self):
        completed = subprocess.run(
            [sys.executable, '-c', 'from tools import audit_cdr2l_spectrum_locator'],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == '__main__': unittest.main()
