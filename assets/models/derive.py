#!/usr/bin/env python3
"""Rebuild the two educational JSON models from hash-pinned public mmCIF files.

Usage: python3 assets/models/derive.py /path/to/rcsb-cif-files
No network requests, third-party imports, or study/patient data are used.
The small category reader intentionally supports only the inspected loop tables.
"""
import hashlib
import json
import math
from pathlib import Path
import shlex
import sys

SOURCES = {
    'insulin': ('1TRZ', 'c09212b60ec05abc195ded6a30f630877eb00ee186b797133543c2d34aef3b45'),
    'dna': ('1BNA', '76d550f32963de46f4f3c63caacb530f91a24f333fbc4312766d240b14e8cf30'),
}


def write_preview(model, target):
    """Orthographic scientific diagram: rotate deposited points, never invent them."""
    atoms = model['atoms']
    centre = [sum(a[c] for a in atoms) / len(atoms) for c in 'xyz']
    rotated = []
    # Fixed proper rotations preserve handedness and all interatomic distances.
    insulin = model['id'] == 'insulin'
    ax, ay, az = (math.radians(v) for v in ((-20, 25, -25) if insulin else (-20, 65, -15)))
    for atom in atoms:
        x, y, z = [atom[c] - centre[i] for i, c in enumerate('xyz')]
        y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
        x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
        x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
        rotated.append((x, y, z))
    bounds = [(min(p[i] for p in rotated), max(p[i] for p in rotated)) for i in range(3)]
    scale = min(480 / (bounds[0][1] - bounds[0][0]), 330 / (bounds[1][1] - bounds[1][0]))
    points = [(300 + (x - sum(bounds[0]) / 2) * scale,
               215 - (y - sum(bounds[1]) / 2) * scale, z) for x, y, z in rotated]
    colours = {'A': '#e8ba72', 'B': '#69d1d1'}
    drawing = []
    for bond in model['bonds']:
        a, b = points[bond['a']], points[bond['b']]
        middle = [(a[i] + b[i]) / 2 for i in range(3)]
        for index, end in ((bond['a'], a), (bond['b'], b)):
            colour = '#f8e8ae' if bond['kind'] == 'disulfide' else colours[atoms[index]['chain']]
            width = 2.6 if bond['kind'] == 'disulfide' else 1.65
            drawing.append(((end[2] + middle[2]) / 2,
                f'<path d="M{end[0]:.3f},{end[1]:.3f} L{middle[0]:.3f},{middle[1]:.3f}" '
                f'fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round"/>'))
    for atom, point in zip(atoms, points):
        radius = 3.3 if atom['element'] == 'S' else 2.35
        drawing.append((point[2], f'<circle cx="{point[0]:.3f}" cy="{point[1]:.3f}" r="{radius}" '
                       f'fill="{colours[atom["chain"]]}" stroke="#10242b" stroke-width="0.7"/>'))
    for contact in model['contacts']:
        a, b = points[contact['a']], points[contact['b']]
        drawing.append(((a[2] + b[2]) / 2,
            f'<path data-kind="hydrogen" d="M{a[0]:.3f},{a[1]:.3f} L{b[0]:.3f},{b[1]:.3f}" '
            'fill="none" stroke="#abc6cc" stroke-width="1" stroke-dasharray="2 3"/>'))
    title = 'Human insulin: two folded chains from PDB 1TRZ' if insulin else 'DNA double helix: two synthetic strands from PDB 1BNA'
    description = (
        'Original projection of 399 deposited heavy-atom coordinates. Chain A, gold, has 21 amino acids; chain B, cyan, has 30. Sticks show chemical connections, including three sulfur-to-sulfur bonds. Six unresolved side-chain atoms and hydrogens are absent. One molecule is selected from a crystal hexamer; water, ions and other chains are omitted. Symbols are illustrative, not measured surfaces. Coordinate data: RCSB PDB 1TRZ, CC0; Ciszak and Smith, 1994, doi:10.1021/bi00172a030.'
        if insulin else
        'Original projection of 486 deposited heavy-atom coordinates. Chain A is gold and chain B cyan. Each synthetic strand contains 12 nucleotides, the repeating chemical units of DNA; together they form 12 base pairs. Solid sticks show covalent connections within each strand; dashed lines show 32 deposited hydrogen-bond contacts between strands. Water, symmetry neighbours and hydrogens are absent. Symbols are illustrative, not measured surfaces. This fragment is not a patient genome or tumour sample. Coordinate data: RCSB PDB 1BNA, CC0; Drew and colleagues, 1981, doi:10.1073/pnas.78.4.2179.'
    )
    a_label = '21 AMINO ACIDS' if insulin else '12 DNA UNITS'
    b_label = '30 AMINO ACIDS' if insulin else '12 DNA UNITS'
    key = 'Atoms are shown as dots; sticks show chemical connections.' if insulin else 'Dots: atoms. Solid: covalent bonds. Dashed: hydrogen contacts.'
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="440" viewBox="0 0 600 440" role="img" aria-labelledby="title desc">',
        f'<title id="title">{title}</title>',
        f'<desc id="desc">{description}</desc>',
        f'<metadata>Source: https://files.rcsb.org/download/{model["accession"]}.cif; SHA-256: '
        + model['metadata']['coordinateSha256'] + '; retrieved 2026-11-05. Deterministic projection generated by assets/models/derive.py.</metadata>',
        '<g font-family="system-ui,sans-serif" font-size="12" letter-spacing="0.3">',
        f'<text x="30" y="26" fill="#e8ba72">CHAIN A · {a_label}</text>',
        f'<text x="570" y="26" text-anchor="end" fill="#69d1d1">CHAIN B · {b_label}</text>',
        '</g>',
    ]
    lines.extend(markup for _, markup in sorted(drawing, key=lambda item: item[0]))
    lines.extend([
        f'<text x="300" y="410" text-anchor="middle" fill="#c0d0d0" font-family="system-ui,sans-serif" font-size="12">{len(atoms)} deposited heavy atoms · PDB {model["accession"]} · static projection</text>',
        f'<text x="300" y="429" text-anchor="middle" fill="#8ba4aa" font-family="system-ui,sans-serif" font-size="11">{key}</text>',
        '</svg>',
    ])
    target.write_text('\n'.join(lines) + '\n')


def category(text, name):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(name + '.'))
    assert lines[start - 1].strip() == 'loop_', name
    keys, values = [], []
    for line in lines[start:]:
        if line.startswith('#'):
            break
        if line.startswith(name + '.'):
            keys.append(line.strip().split('.', 1)[1])
        else:
            values.extend(shlex.split(line, comments=False))
    assert len(values) % len(keys) == 0, name
    return [dict(zip(keys, values[i:i + len(keys)])) for i in range(0, len(values), len(keys))]


def derive(model_id, directory):
    accession, digest = SOURCES[model_id]
    raw = (directory / (accession + '.cif')).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest, 'Source changed; review before updating pins'
    text = raw.decode('utf-8')
    raw_atoms = category(text, '_atom_site')
    candidates = [a for a in raw_atoms if a['group_PDB'] == 'ATOM'
                  and a['auth_asym_id'] in ('A', 'B')
                  and a['pdbx_PDB_model_num'] == '1' and a['type_symbol'] not in ('H', 'D')]
    selected = {}
    for a in candidates:
        assert a['pdbx_PDB_ins_code'] in ('?', '.'), 'Insertion code requires review'
        key = (a['auth_asym_id'], int(a['auth_seq_id']), a['label_atom_id'])
        preference = (float(a['occupancy']), a['label_alt_id'] == '.', a['label_alt_id'] == 'A')
        if key not in selected or preference > selected[key][0]:
            selected[key] = (preference, a)
    rows = sorted((x[1] for x in selected.values()), key=lambda a: int(a['id']))
    atoms = [{
        'id': i, 'element': a['type_symbol'], 'name': a['label_atom_id'],
        'residue': a['label_comp_id'], 'residueNumber': int(a['auth_seq_id']),
        'sequenceNumber': int(a['label_seq_id']), 'chain': a['auth_asym_id'],
        'x': float(a['Cartn_x']), 'y': float(a['Cartn_y']), 'z': float(a['Cartn_z']),
    } for i, a in enumerate(rows)]
    lookup = {(a['chain'], a['residueNumber'], a['name']): a['id'] for a in atoms}
    residues = {}
    for a in atoms:
        residues.setdefault((a['chain'], a['residueNumber']), {})[a['name']] = a['id']
    component_bonds = category(text, '_chem_comp_bond')
    bonds, contacts, backbone = [], [], []
    for (chain, number), names in residues.items():
        residue = atoms[next(iter(names.values()))]['residue']
        for bond in component_bonds:
            a, b = bond['atom_id_1'], bond['atom_id_2']
            if bond['comp_id'] == residue and a in names and b in names:
                bonds.append({'a': names[a], 'b': names[b], 'kind': 'covalent',
                              'order': bond['value_order'].lower(), 'source': 'chemical-component'})
    guide_atom = 'CA' if model_id == 'insulin' else "C4'"
    join_a, join_b = ('C', 'N') if model_id == 'insulin' else ("O3'", 'P')
    for chain in ('A', 'B'):
        numbers = sorted(number for ch, number in residues if ch == chain)
        for number, following in zip(numbers, numbers[1:]):
            assert following == number + 1
            a, b = lookup[(chain, number, join_a)], lookup[(chain, following, join_b)]
            distance = math.dist([atoms[a][c] for c in 'xyz'], [atoms[b][c] for c in 'xyz'])
            assert 1.1 < distance < 1.9, ('Unexpected polymer link', chain, number, distance)
            bonds.append({'a': a, 'b': b, 'kind': 'covalent', 'order': 'sing', 'source': 'polymer-sequence'})
            backbone.append({'a': lookup[(chain, number, guide_atom)],
                             'b': lookup[(chain, following, guide_atom)]})
    for conn in category(text, '_struct_conn'):
        if conn['conn_type_id'] not in ('disulf', 'hydrog'):
            continue
        keys = [(conn[f'ptnr{i}_auth_asym_id'], int(conn[f'ptnr{i}_auth_seq_id']),
                 conn[f'ptnr{i}_label_atom_id']) for i in (1, 2)]
        if not all(k in lookup for k in keys):
            continue
        assert all(conn[f'ptnr{i}_symmetry'] == '1_555' for i in (1, 2))
        link = {'a': lookup[keys[0]], 'b': lookup[keys[1]],
                'kind': 'disulfide' if conn['conn_type_id'] == 'disulf' else 'hydrogen',
                'source': 'deposited-struct_conn'}
        (bonds if conn['conn_type_id'] == 'disulf' else contacts).append(link)
    if model_id == 'insulin':
        title = 'Human insulin'
        subtitle = 'Two protein chains, folded into one molecular signal'
        paragraphs = [
            'A protein is built from chains of small chemical units called amino acids. This insulin molecule has two chains: 21 units in chain A and 30 in chain B. Switch between a guide to the folded chains and the individual atoms and their chemical connections.',
            'A sequence is more than a list. Its atoms fold into a three-dimensional arrangement. Three sulfur-to-sulfur bonds help hold insulin together: one within chain A and two joining A to B. Rotate the model to see how distant parts of the sequence meet in space.',
            'These coordinates come from an X-ray crystal structure, not a movie inside a person. We show one A/B insulin molecule from a larger zinc-containing assembly. It teaches how sequence and shape connect; it does not establish an ovarian-cancer target or predict a treatment response.',
        ]
        limits = 'One A/B insulin molecule selected from a crystal hexamer; water, ions, other chains and crystal neighbours are omitted. Six unresolved side-chain atoms and hydrogens are absent. A static reference structure is not a simulation of a living cell or evidence of treatment benefit.'
        organism = 'Homo sapiens sequence; crystalline biosynthetic human insulin'
        sequence = {'A': 'GIVEQCCTSICSLYQLENYCN', 'B': 'FVNQHLCGSHLVEALYLVCGERGFFYTPKT'}
        omission = 'All HETATM records (including water, zinc, chloride and sodium), author chains C/D, and crystallographic symmetry copies. The deposit lacks LYS B29 CG/CD/CE/NZ and THR B30 OG1/CG2 side-chain atoms; these and hydrogens are not added.'
        citation = {'authors': 'Ciszak E; Smith GD', 'year': 1994, 'title': 'Crystallographic evidence for dual coordination around zinc in the T3R3 human insulin hexamer.', 'doi': '10.1021/bi00172a030'}
        resolution, deposited, released, revised = 1.6, '1993-11-19', '1994-01-31', '2024-11-06'
        assert len(atoms) == 399 and len(residues) == 51
        assert sum(b['kind'] == 'disulfide' for b in bonds) == 3
    else:
        title = 'DNA double helix'
        subtitle = 'Two complementary strands, carrying an ordered sequence'
        paragraphs = [
            'DNA is built from repeating units called nucleotides. Each has a sugar, a base and, along the chain, a phosphate connection. The bases are named A, T, G and C. Here two synthetic strands each contain the sequence CGCGAATTCGCG, read in their own 5′ to 3′ direction.',
            'The two strands run in opposite directions. A pairs with T; G pairs with C. Strong chemical links, called covalent bonds, connect each strand. Weaker attractions, called hydrogen bonds, join matching bases across the gap. Stacking the flat bases also helps stabilize the helix. The deposited atom positions show a real, slightly irregular shape rather than a perfect mathematical spiral.',
            'This is a short DNA crystal reference, not a person’s genome, a tumour sample or a whole chromosome. It helps explain molecular structure. It cannot show which genes a cancer cell uses or establish whether a treatment works.',
        ]
        limits = 'Synthetic 12-base-pair DNA crystal fragment; water is omitted. This is neither a human genome sample nor a whole chromosome. Static coordinates cannot establish gene activity, tumour behaviour or treatment benefit.'
        organism = 'Synthetic DNA; no source organism assigned'
        sequence = {'A': 'CGCGAATTCGCG', 'B': 'CGCGAATTCGCG'}
        omission = 'All HETATM records (water) and crystallographic symmetry copies. Hydrogens and absent terminal phosphates are not added.'
        citation = {'authors': 'Drew HR; Wing RM; Takano T; Broka C; Tanaka S; Itakura K; Dickerson RE', 'year': 1981, 'title': 'Structure of a B-DNA dodecamer: conformation and dynamics.', 'doi': '10.1073/pnas.78.4.2179'}
        resolution, deposited, released, revised = 1.9, '1981-01-26', '1981-05-21', '2024-02-07'
        assert len(atoms) == 486 and len(residues) == 24 and len(contacts) == 32
    metadata = {
        'claimStatus': 'VERIFIED reference-coordinate derivation; not a Project Asma experimental result',
        'retrieved': '2026-11-05', 'coordinateUrl': f'https://files.rcsb.org/download/{accession}.cif',
        'coordinateSha256': digest, 'license': 'CC0-1.0',
        'licenseUrl': 'https://www.rcsb.org/pages/usage-policy', 'citation': citation,
        'method': 'X-ray diffraction', 'resolutionAngstrom': resolution,
        'depositionDate': deposited, 'releaseDate': released, 'entryRevisionDate': revised,
        'organism': organism, 'engineered': True,
        'mutationNote': 'Entry is engineered/synthetic; RCSB polymer-entity metadata reports zero mutations. This does not mean it is an unmodified biological sample.',
        'sequences': sequence, 'selectedAuthorChains': ['A', 'B'], 'selectedModel': 1,
        'atomCount': len(atoms), 'residueCount': len(residues), 'bondCount': len(bonds),
        'hydrogenContactCount': len(contacts), 'omissions': omission,
        'alternateLocations': {'policy': 'Highest occupancy for each atom; ties prefer blank then A; preserve file order thereafter.',
                               'candidateAtoms': len(candidates), 'discardedAlternates': len(candidates) - len(atoms)},
        'coordinates': 'Deposited Cartesian coordinates retained without reflection, smoothing, relaxation or rescaling. Units are angstroms (1 Å = 0.1 nm).',
        'stereochemistry': 'Inherited from deposited coordinates and residue identity; no stereocentres, missing atoms, hydrogens or protonation states are generated.',
        'bonds': 'Within-residue connectivity and order from deposited _chem_comp_bond; sequential polymer C–N or O3′–P links added by known chain order and checked for plausible length. Disulfides and hydrogen contacts come from deposited _struct_conn. No distance-only bond inference.',
        'bondDrawing': 'A single stick indicates connectivity; displayed stick count need not encode deposited bond order. Atom spheres are illustrative, not measured surfaces.',
        'backbone': f'Guide links between successive {guide_atom} atoms in each chain. These are not direct chemical bonds or measured surfaces.',
        'contacts': 'Deposited donor/acceptor heavy-atom pairs for Watson–Crick hydrogen bonds; not hydrogen-atom coordinates and not covalent interstrand bonds.',
    }
    model = {'id': model_id, 'title': title, 'subtitle': subtitle, 'accession': accession,
             'sourceUrl': f'https://www.rcsb.org/structure/{accession}',
             'description': paragraphs[0], 'explanation': paragraphs, 'limits': limits,
             'unit': 'angstrom', 'atoms': atoms, 'bonds': bonds, 'contacts': contacts,
             'backbone': backbone, 'metadata': metadata}
    target = Path(__file__).resolve().parent / (model_id + '.json')
    target.write_text(json.dumps(model, ensure_ascii=False, separators=(',', ':')) + '\n')
    write_preview(model, target.with_name(model_id + '-preview.svg'))
    print(f'{target.name}: {len(atoms)} atoms; {len(bonds)} bonds; {len(contacts)} hydrogen contacts; {target.stat().st_size} bytes')


if __name__ == '__main__':
    source_directory = Path(sys.argv[1])
    for identifier in SOURCES:
        derive(identifier, source_directory)
