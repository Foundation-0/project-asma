"""Synthetic spectra only; no network in tests."""
import hashlib
import io
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_cdr2l_spectrum_locator import inspect_mgf, source_link, NAME

BLOCK = b'BEGIN IONS\nTITLE=synthetic\nPEPMASS=614.9990\nCHARGE=3+\n100.000 20.0\n200 0\nEND IONS\n'


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

    def test_source_format_is_required_not_inferred_from_precursor(self):
        result = {'attributes': {'spectrumID': 'index=22949'}, 'spectra_data': {'file_name': NAME}, 'items': [{}]}
        cert = {'all_three_pinned_files_complete': True, 'files': [{'matching_results': [result]}]}
        with self.assertRaises(ValueError): source_link(cert)
        result['spectra_data']['SpectrumIDFormat'] = [{'accession': 'MS:1000774'}]
        self.assertIs(source_link(cert), result)
        result['attributes']['spectrumID'] = 'scan=22949'
        with self.assertRaises(ValueError): source_link(cert)


if __name__ == '__main__': unittest.main()
