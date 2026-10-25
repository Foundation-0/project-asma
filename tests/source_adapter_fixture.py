"""Full-shape abstract source files, generated only in memory for integration."""
import copy
import hashlib
import io
import math
import zlib
import zipfile
from xml.etree import ElementTree as ET

import source_data_adapter as adapter

MAIN = adapter.NS['s']
RELS = 'http://schemas.openxmlformats.org/package/2006/relationships'
OFFICE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def workbook(sheets):
    stream = io.BytesIO()
    book = ET.Element(f'{{{MAIN}}}workbook')
    sheet_list = ET.SubElement(book, f'{{{MAIN}}}sheets')
    relationships = ET.Element(f'{{{RELS}}}Relationships')
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        def write(name, value):
            # Fixed metadata makes fixture byte hashes reproducible.
            entry = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, ET.tostring(value, encoding='utf-8'))
        for index, (name, rows) in enumerate(sheets, 1):
            relation = f'rId{index}'
            ET.SubElement(sheet_list, f'{{{MAIN}}}sheet',
                          {'name': name, 'sheetId': str(index), f'{{{OFFICE}}}id': relation})
            ET.SubElement(relationships, f'{{{RELS}}}Relationship',
                          {'Id': relation, 'Target': f'worksheets/sheet{index}.xml',
                           'Type': OFFICE + '/worksheet'})
            sheet = ET.Element(f'{{{MAIN}}}worksheet')
            data = ET.SubElement(sheet, f'{{{MAIN}}}sheetData')
            for row_index, cells in enumerate(rows, 1):
                row = ET.SubElement(data, f'{{{MAIN}}}row', {'r': str(row_index)})
                for column, value in enumerate(cells):
                    cell = ET.SubElement(row, f'{{{MAIN}}}c',
                                         {'r': chr(65 + column) + str(row_index), 't': 'inlineStr'})
                    if value is None:
                        # A prediction formula deliberately cannot be interpreted
                        # by the selected-cell parser. Only membership A is used.
                        ET.SubElement(cell, f'{{{MAIN}}}f').text = 'UNUSED_PREDICTION_FORMULA()'
                    else:
                        inline = ET.SubElement(cell, f'{{{MAIN}}}is')
                        ET.SubElement(inline, f'{{{MAIN}}}t').text = value
            write(f'xl/worksheets/sheet{index}.xml', sheet)
        write('xl/workbook.xml', book)
        write('xl/_rels/workbook.xml.rels', relationships)
    return stream.getvalue()


def make_full_fixture():
    panel = [f'fixture-feature-{i:04d}' for i in range(1, 65)]
    clinical_rows = [adapter.CLINICAL_COLUMNS]
    measurements = []
    for sample in range(1, 159):
        for replicate in range(1, 4 if sample <= 5 else 2):
            label = f'fixture-measurement-{sample:03d}-{replicate}'
            measurements.append((label, sample, replicate))
            clinical_rows.append([
                label, f'fixture-patient-{sample:03d}', f'fixture-sample-{sample:03d}',
                'yes' if 136 <= sample <= 148 else 'no',
                'sensitive' if sample <= 83 else 'refractory',
                'NA' if sample == 135 else ('Mix' if sample >= 149 else 'OV'), 'fixture-type'])
    for control in range(1, 64):
        clinical_rows.append([f'fixture-control-{control:03d}'] + ['NA'] * 6)
    keys = [f'fixture-measurement-{sample:03d}-1' for sample in range(1, 136)]
    clinical_bytes = workbook([('FFPE_Discovery_clinical', clinical_rows)])
    panel_bytes = workbook([('64_protein_predictors', [['Proteins']] + [[item] for item in panel]),
                            ('FFPE_pred_scores', [['Samples', 'Pred.scores']] +
                             [[key, None] for key in reversed(keys)])])
    measurements.reverse()  # Source order differs from the canonical R order.
    header = ('\t'.join(list(adapter.features.ANNOTATIONS) +
                       [item[0] for item in measurements] + ['fixture-control-001']) + '\n').encode()
    body = io.BytesIO()
    body.write(header)
    for feature in range(8800, 0, -1):
        annotations = [f'fixture-accession-{feature}', f'fixture-feature-{feature:04d}',
                       'fixture-name', 'fixture-location', str(feature), '1', '1', 'fixture-group', '1']
        values = []
        for _, sample, replicate in measurements:
            if feature > 64:
                values.append('0')
            elif sample == 136:
                values.append('NA')  # Excluded values may remain missing.
            else:
                value = (math.sin(feature * sample * math.sqrt(2)) +
                         math.cos((feature + 1) * sample * math.sqrt(3)) +
                         math.sin((feature + 3) * (sample + 2) * math.sqrt(5)) / 3 +
                         ((replicate - 2) / 4 if sample <= 5 else 0))
                values.append(repr(value))
        body.write(('\t'.join(annotations + values + ['NA']) + '\n').encode())
    member = body.getvalue()
    compressor = zlib.compressobj(wbits=-15)
    packed = compressor.compress(member) + compressor.flush()
    contract = copy.deepcopy(adapter.DEFAULT_CONTRACT)
    contract['member'].update(compressed_bytes=len(packed), uncompressed_bytes=len(member),
                              crc32=zlib.crc32(member), sha256=hashlib.sha256(member).hexdigest(),
                              compressed_sha256=hashlib.sha256(packed).hexdigest())
    contract['matrix']['header_sha256'] = hashlib.sha256(header).hexdigest()
    contract['panel']['sha256'] = hashlib.sha256(('\n'.join(panel) + '\n').encode()).hexdigest()
    for key, value in [('clinical', clinical_bytes), ('panel_and_scores', panel_bytes)]:
        contract['workbooks'][key].update(bytes=len(value), sha256=hashlib.sha256(value).hexdigest(),
                                         md5=hashlib.md5(value).hexdigest())
    return packed, clinical_bytes, panel_bytes, contract
