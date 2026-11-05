#!/usr/bin/env python3
"""Offline integrity checks for the site's two educational coordinate subsets.

Run: python3 tools/check_site_models.py
No network access or source downloads. Full conversion replay and independent
archive-format comparison remain the manual procedure in site-structure-sources.md.
"""
import collections
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / 'assets' / 'models'
EXPECTED = {
    'insulin': {'accession': '1TRZ', 'atoms': 399, 'bonds': 410, 'contacts': 0,
                'guides': 49, 'residues': 51, 'guide': 'CA',
                'pin': 'c09212b60ec05abc195ded6a30f630877eb00ee186b797133543c2d34aef3b45',
                'sequences': {'A': 'GIVEQCCTSICSLYQLENYCN', 'B': 'FVNQHLCGSHLVEALYLVCGERGFFYTPKT'}},
    'dna': {'accession': '1BNA', 'atoms': 486, 'bonds': 544, 'contacts': 32,
            'guides': 22, 'residues': 24, 'guide': "C4'",
            'pin': '76d550f32963de46f4f3c63caacb530f91a24f333fbc4312766d240b14e8cf30',
            'sequences': {'A': 'CGCGAATTCGCG', 'B': 'CGCGAATTCGCG'}},
}
AA = dict(zip('GLY ILE VAL GLU GLN CYS THR SER LEU TYR ASN PHE HIS ALA ARG PRO LYS'.split(),
              'GIVEQCTSLYNFHARPK'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def component_sizes(atom_count, links):
    neighbours = [set() for _ in range(atom_count)]
    for link in links:
        neighbours[link['a']].add(link['b'])
        neighbours[link['b']].add(link['a'])
    todo, sizes = set(range(atom_count)), []
    while todo:
        stack, count = [todo.pop()], 0
        while stack:
            current = stack.pop()
            count += 1
            for following in neighbours[current] & todo:
                todo.remove(following)
                stack.append(following)
        sizes.append(count)
    return sorted(sizes)


def check_model(name, model):
    expected = EXPECTED[name]
    atoms, bonds = model['atoms'], model['bonds']
    meta = model['metadata']
    require(model['id'] == name and model['accession'] == expected['accession'], 'identity')
    require(model['unit'] == 'angstrom', 'coordinate units')
    require(meta['coordinateSha256'] == expected['pin'], 'source hash pin')
    require(meta['coordinateUrl'] == f'https://files.rcsb.org/download/{expected["accession"]}.cif', 'coordinate source')
    require(meta['license'] == 'CC0-1.0' and meta['licenseUrl'] == 'https://www.rcsb.org/pages/usage-policy', 'reuse metadata')
    require(meta['selectedAuthorChains'] == ['A', 'B'] and meta['selectedModel'] == 1, 'selection metadata')
    require(len(atoms) == meta['atomCount'] == expected['atoms'], 'atom count')
    require(len(bonds) == meta['bondCount'] == expected['bonds'], 'bond count')
    require(len(model['contacts']) == meta['hydrogenContactCount'] == expected['contacts'], 'contact count')
    require(len(model['backbone']) == expected['guides'], 'guide count')
    require(meta['sequences'] == expected['sequences'], 'sequence metadata')
    residues, lookup = {}, {}
    for i, atom in enumerate(atoms):
        require(type(atom['id']) is int and atom['id'] == i, 'atom identity/index')
        require(atom['element'] in ('C', 'N', 'O', 'S', 'P'), 'unexpected element')
        require(atom['chain'] in ('A', 'B'), 'unexpected chain')
        require(all(type(atom[c]) in (int, float) and math.isfinite(atom[c]) for c in 'xyz'), 'non-finite coordinate')
        key = (atom['chain'], atom['residueNumber'], atom['name'])
        require(key not in lookup, 'duplicate atom key')
        lookup[key] = i
        residue_key = (atom['chain'], atom['residueNumber'])
        residue_value = (atom['residue'], atom['sequenceNumber'])
        require(residues.get(residue_key, residue_value) == residue_value, 'inconsistent residue')
        residues[residue_key] = residue_value
    require(len(residues) == meta['residueCount'] == expected['residues'], 'residue count')
    for chain in ('A', 'B'):
        chain_residues = sorted((number, data) for (ch, number), data in residues.items() if ch == chain)
        start = 13 if name == 'dna' and chain == 'B' else 1
        require([number for number, _ in chain_residues] == list(range(start, start + len(chain_residues))), 'author numbering')
        require([data[1] for _, data in chain_residues] == list(range(1, len(chain_residues) + 1)), 'sequence numbering')
        observed = ''.join(AA[data[0]] if name == 'insulin' else data[0][1] for _, data in chain_residues)
        require(observed == expected['sequences'][chain], 'coordinate residue sequence')
    for field in ('bonds', 'contacts', 'backbone'):
        seen = set()
        for link in model[field]:
            require(all(type(link[k]) is int and 0 <= link[k] < len(atoms) for k in ('a', 'b')), 'endpoint bounds')
            pair = tuple(sorted((link['a'], link['b'])))
            require(pair[0] != pair[1] and pair not in seen, 'self/duplicate connection')
            seen.add(pair)
            a, b = (atoms[link[k]] for k in ('a', 'b'))
            distance = math.dist([a[c] for c in 'xyz'], [b[c] for c in 'xyz'])
            if field == 'bonds':
                require(link['kind'] in ('covalent', 'disulfide'), 'invalid bond class')
                require(1.0 < distance < 2.2, 'implausible covalent geometry')
                require(link['source'] in ('chemical-component', 'polymer-sequence', 'deposited-struct_conn'), 'bond provenance')
                if link['kind'] == 'covalent':
                    require(a['chain'] == b['chain'], 'cross-chain ordinary covalent bond')
            elif field == 'contacts':
                require(link['kind'] == 'hydrogen' and link['source'] == 'deposited-struct_conn', 'contact provenance')
                require(a['chain'] != b['chain'] and a['residueNumber'] + b['residueNumber'] == 25, 'DNA pairing registry')
                require(2.0 < distance < 3.6, 'implausible hydrogen-contact geometry')
            else:
                require(a['name'] == b['name'] == expected['guide'], 'guide atom type')
                require(a['chain'] == b['chain'] and b['residueNumber'] == a['residueNumber'] + 1, 'guide sequence order')
    disulfides = {
        tuple((atoms[b[k]]['chain'], atoms[b[k]]['residueNumber'], atoms[b[k]]['name']) for k in ('a', 'b'))
        for b in bonds if b['kind'] == 'disulfide'
    }
    if name == 'insulin':
        require(component_sizes(len(atoms), bonds) == [399], 'insulin connectivity')
        require(disulfides == {(('A', 6, 'SG'), ('A', 11, 'SG')), (('A', 7, 'SG'), ('B', 7, 'SG')),
                                (('A', 20, 'SG'), ('B', 19, 'SG'))}, 'insulin disulfide mapping')
        for residue, missing in ((29, ('CG', 'CD', 'CE', 'NZ')), (30, ('OG1', 'CG2'))):
            require(all(('B', residue, atom) not in lookup for atom in missing), 'invented unresolved side-chain atom')
    else:
        require(not disulfides, 'unexpected DNA disulfide')
        require(component_sizes(len(atoms), bonds) == [243, 243], 'DNA covalent components')
        require(component_sizes(len(atoms), bonds + model['contacts']) == [486], 'DNA contact connectivity')
        contact_counts = collections.Counter(atoms[b['a']]['residueNumber'] for b in model['contacts'])
        require(contact_counts == {n: (2 if 5 <= n <= 8 else 3) for n in range(1, 13)}, 'DNA pair contact counts')


def main():
    for name in EXPECTED:
        check_model(name, json.loads((MODELS / (name + '.json')).read_text()))
        print(f'{name}: coordinate/model integrity PASS')
    for name, expected in EXPECTED.items():
        svg = ET.parse(MODELS / (name + '-preview.svg')).getroot()
        ns = {'s': 'http://www.w3.org/2000/svg'}
        require(svg.attrib.get('viewBox') == '0 0 600 440', 'fallback dimensions')
        require(len(svg.findall('s:circle', ns)) == expected['atoms'], 'fallback atom symbols')
        require(len(svg.findall('s:path', ns)) == 2 * expected['bonds'] + expected['contacts'], 'fallback connection segments')
        require(len(svg.findall('s:path[@data-kind="hydrogen"]', ns)) == expected['contacts'], 'fallback hydrogen-contact class')
        require(expected['pin'] in (svg.findtext('s:metadata', namespaces=ns) or ''), 'fallback provenance')
        require(not svg.findall('.//s:script', ns), 'unexpected SVG script')
        print(f'{name} preview: dimensions, provenance and primitive counts PASS')
    print('Offline checks do not replay the archived conversion or validate biological/clinical efficacy.')


if __name__ == '__main__':
    try:
        main()
    except (KeyError, TypeError, ValueError, OSError, ET.ParseError) as error:
        print(f'Molecular reference check FAILED: {error}', file=sys.stderr)
        sys.exit(1)
