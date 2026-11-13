"""Synthetic, nonclinical fixtures for bounded source-identification inspection."""
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
import xml.sax

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_cdr2l_source_psm import inspect_stream, TARGET, check_certificate, PRODUCING_SCRIPT_SHA256

ROOT = Path(__file__).resolve().parents[1]
IDENT_CERT = ROOT / "registries/cdr2l-source-identification-2026-11-06.json"


def fixture(sequence=TARGET):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<MzIdentML xmlns="http://psidev.info/psi/pi/mzIdentML/1.1">
<SequenceCollection><DBSequence id="db1" accession="SYNTHETIC" searchDatabase_ref="db"/>
<Peptide id="p1"><PeptideSequence>{sequence}</PeptideSequence></Peptide>
<PeptideEvidence id="ev1" peptide_ref="p1" dBSequence_ref="db1" start="1" end="15" isDecoy="false"/>
</SequenceCollection><AnalysisProtocolCollection><SpectrumIdentificationProtocol id="protocol">
<Threshold><cvParam accession="TEST:threshold" name="synthetic threshold" value="1"/></Threshold>
</SpectrumIdentificationProtocol></AnalysisProtocolCollection><DataCollection>
<Inputs><SpectraData id="sd1" location="synthetic.mgf"/></Inputs>
<AnalysisData><SpectrumIdentificationList><SpectrumIdentificationResult id="sir1" spectrumID="index=7" spectraData_ref="sd1">
<SpectrumIdentificationItem id="sii1" peptide_ref="p1" chargeState="2" rank="1" passThreshold="true">
<PeptideEvidenceRef peptideEvidence_ref="ev1"/><cvParam accession="TEST:score" name="synthetic score" value="12.3"/>
</SpectrumIdentificationItem></SpectrumIdentificationResult></SpectrumIdentificationList></AnalysisData>
</DataCollection></MzIdentML>'''.encode()


def inspect(xml, **kwargs):
    blob = gzip.compress(xml, mtime=0)
    return inspect_stream(io.BytesIO(blob), expected_size=len(blob),
                          expected_sha1=hashlib.sha1(blob).hexdigest(), **kwargs)


class SourcePSMTests(unittest.TestCase):
    def test_target_ids_scores_reference_and_complete_hash(self):
        xml = fixture()
        result = inspect(xml)
        self.assertTrue(result['xml_complete'])
        self.assertEqual(result['expanded_bytes'], len(xml))
        self.assertEqual(result['sha256'], hashlib.sha256(gzip.compress(xml, mtime=0)).hexdigest())
        r = result['matching_results'][0]
        self.assertEqual(r['attributes']['spectrumID'], 'index=7')
        self.assertEqual(r['spectra_data']['file_name'], 'synthetic.mgf')
        self.assertEqual(r['items'][0]['parameters'][0]['value'], '12.3')
        self.assertEqual(r['items'][0]['attributes']['passThreshold'], 'true')
        self.assertEqual(r['items'][0]['protein_evidence'][0]['protein']['accession'], 'SYNTHETIC')
        self.assertEqual(result['protocols'][0]['threshold_parameters'][0]['value'], '1')

    def test_substitution_is_retained_not_reported_as_unmodified(self):
        xml = fixture().replace(b'</PeptideSequence>', b'</PeptideSequence><SubstitutionModification originalResidue="S" replacementResidue="T" location="1" monoisotopicMassDelta="14.01565"/>')
        modifications = inspect(xml)['matching_peptides'][0]['modifications']
        self.assertEqual(modifications[0]['element'], 'SubstitutionModification')
        self.assertEqual(modifications[0]['replacementResidue'], 'T')

    def test_spectrum_id_format_and_file_format_retained(self):
        xml = fixture().replace(b'location="synthetic.mgf"/>', b'location="synthetic.mgf"><FileFormat><cvParam accession="MS:1001062" name="Mascot MGF format"/></FileFormat><SpectrumIDFormat><cvParam accession="MS:1000774" name="multiple peak list nativeID format"/></SpectrumIDFormat></SpectraData>')
        spectra = inspect(xml)['matching_results'][0]['spectra_data']
        self.assertEqual(spectra['SpectrumIDFormat'][0]['accession'], 'MS:1000774')
        self.assertEqual(spectra['FileFormat'][0]['accession'], 'MS:1001062')

    def test_expanded_payload_can_match_manifest_with_wrapper_difference_explicit(self):
        xml = fixture()
        blob = gzip.compress(xml, mtime=0)
        result = inspect_stream(io.BytesIO(blob), expected_size=len(xml),
                                expected_sha1=hashlib.sha1(blob).hexdigest(), served_size=len(blob),
                                metadata_contract="gzip_sha1_expanded_size")
        self.assertEqual(result['metadata_size_domain'], 'expanded_mzidentml')
        self.assertEqual(result['metadata_checksum_domain'], 'served_gzip')
        self.assertTrue(result['served_size_differs_from_api'])
        self.assertEqual(result['expanded_sha256'], hashlib.sha256(xml).hexdigest())
        with self.assertRaises(ValueError):
            inspect_stream(io.BytesIO(blob), expected_size=len(xml),
                           expected_sha1=hashlib.sha1(blob).hexdigest(), served_size=len(blob)+1,
                           metadata_contract="gzip_sha1_expanded_size")

    def test_mixed_contract_rejects_bad_hash_size_and_wrong_compression(self):
        xml = fixture()
        blob = gzip.compress(xml, mtime=0)
        for size, digest in [(len(xml)+1, hashlib.sha1(blob).hexdigest()), (len(xml), '0'*40)]:
            with self.subTest(size=size), self.assertRaises(ValueError):
                inspect_stream(io.BytesIO(blob), expected_size=size, expected_sha1=digest,
                               metadata_contract="gzip_sha1_expanded_size")
        with self.assertRaises(gzip.BadGzipFile):
            inspect_stream(io.BytesIO(xml), expected_size=len(xml), expected_sha1=hashlib.sha1(xml).hexdigest())

    def test_late_source_failure_emits_no_partial_artifact(self):
        from unittest import mock
        import tempfile
        import audit_cdr2l_source_psm as module
        xml = fixture()
        blob = gzip.compress(xml, mtime=0)
        class Response(io.BytesIO):
            status = 200
            headers = {"Content-Length": str(len(blob))}
        opener = mock.Mock()
        opener.open.side_effect = [Response(blob), Response(blob), Response(blob[:-8])]
        files = tuple((f"synthetic{i}.gz", len(xml), hashlib.sha1(blob).hexdigest()) for i in range(3))
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)/"result.json"
            with mock.patch.object(module, 'FILES', files), mock.patch.object(module.urllib.request, 'build_opener', return_value=opener), mock.patch.object(sys, 'argv', ['audit', '--live', '--output', str(output)]), mock.patch('sys.stderr', io.StringIO()):
                self.assertEqual(module.main(), 1)
            self.assertEqual(opener.open.call_count, 3)
            self.assertFalse(output.exists())

    def test_complete_absent_sequence_is_retained_as_absent(self):
        result = inspect(fixture('AAAAAAAAAAAAAAA'))
        self.assertEqual(result['matching_results'], [])
        self.assertEqual(result['total_identification_items'], 1)
        self.assertTrue(result['xml_complete'])

    def test_source_directory_is_not_retained(self):
        result = inspect(fixture().replace(b'location="synthetic.mgf"', b'location="file:/private/author%20directory/synthetic.mgf"'))
        source = result['matching_results'][0]['spectra_data']
        self.assertEqual(source['file_name'], 'synthetic.mgf')
        self.assertNotIn('private', str(source))
        self.assertEqual(source['source_location_sha256'], hashlib.sha256(b'file:/private/author%20directory/synthetic.mgf').hexdigest())

    def test_false_threshold_and_decoy_are_not_promoted(self):
        result = inspect(fixture().replace(b'passThreshold="true"', b'passThreshold="false"').replace(b'isDecoy="false"', b'isDecoy="true"'))
        item = result['matching_results'][0]['items'][0]
        self.assertEqual(item['attributes']['passThreshold'], 'false')
        self.assertEqual(item['protein_evidence'][0]['attributes']['isDecoy'], 'true')

    def test_wrong_hash_and_size_refused(self):
        blob = gzip.compress(fixture(), mtime=0)
        for size, digest in [(len(blob)-1,hashlib.sha1(blob).hexdigest()), (len(blob),'0'*40)]:
            with self.subTest(size=size,digest=digest), self.assertRaises(ValueError):
                inspect_stream(io.BytesIO(blob), expected_size=size, expected_sha1=digest)

    def test_truncated_gzip_and_xml_refused(self):
        blob = gzip.compress(fixture(), mtime=0)[:-8]
        with self.assertRaises((EOFError, OSError, ValueError)):
            inspect_stream(io.BytesIO(blob), expected_size=len(blob), expected_sha1=hashlib.sha1(blob).hexdigest())
        with self.assertRaises(xml.sax.SAXException):
            inspect(fixture()[:-12])

    def test_caps_enforced(self):
        with self.assertRaises(ValueError): inspect(fixture(), compressed_cap=10)
        with self.assertRaises(ValueError): inspect(fixture(), expanded_cap=10)

    def test_dtd_and_wide_encoding_refused(self):
        with self.assertRaises(ValueError):
            inspect(fixture().replace(b'<MzIdentML',b'<!DOCTYPE x [<!ENTITY e "x">]><MzIdentML',1))
        with self.assertRaises(ValueError): inspect(fixture().decode().encode('utf-16'))

    def test_wrong_document_refused(self):
        with self.assertRaises(ValueError): inspect(b'<notmzid/>')

    def test_duplicate_identity_refused(self):
        with self.assertRaises(ValueError):
            inspect(fixture().replace(b'</SequenceCollection>',b'<Peptide id="p1"><PeptideSequence>OTHER</PeptideSequence></Peptide></SequenceCollection>'))

    def test_missing_or_mismatched_source_reference_refused(self):
        for old,new in [(b'spectraData_ref="sd1"',b'spectraData_ref="absent"'),
                        (b'peptideEvidence_ref="ev1"',b'peptideEvidence_ref="absent"'),
                        (b'dBSequence_ref="db1"',b'dBSequence_ref="absent"')]:
            with self.subTest(old=old),self.assertRaises(ValueError):inspect(fixture().replace(old,new))


    def test_offline_certificate_check_passes(self):
        code = subprocess.run(
            [sys.executable, str(ROOT / 'tools/audit_cdr2l_source_psm.py'), '--check'],
            check=False,
        ).returncode
        self.assertEqual(code, 0)

    def test_producing_implementation_hash_passes_and_arbitrary_hash_fails(self):
        report = json.loads(IDENT_CERT.read_text(encoding='utf-8'))
        report['implementation_sha256'] = PRODUCING_SCRIPT_SHA256
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as handle:
            json.dump(report, handle)
            path = Path(handle.name)
        try:
            check_certificate(path)
        finally:
            path.unlink()
        bad = copy.deepcopy(report)
        bad['implementation_sha256'] = '0' * 64
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as handle:
            json.dump(bad, handle)
            path = Path(handle.name)
        try:
            with self.assertRaises(ValueError):
                check_certificate(path)
        finally:
            path.unlink()

    def test_offline_check_binds_recorded_identification_match(self):
        report = json.loads(IDENT_CERT.read_text(encoding='utf-8'))
        import tempfile
        for mutate in (
            lambda r: r.update(assay_id=0),
            lambda r: r['files'][2]['matching_results'][0]['attributes'].update(spectrumID='index=0'),
            lambda r: r['files'][2]['matching_results'][0]['items'][0]['protein_evidence'][0]['attributes'].update(start='1'),
        ):
            changed = copy.deepcopy(report)
            mutate(changed)
            with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as handle:
                json.dump(changed, handle)
                path = Path(handle.name)
            try:
                with self.assertRaises(ValueError):
                    check_certificate(path)
            finally:
                path.unlink()


if __name__ == '__main__': unittest.main()
