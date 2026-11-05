# Molecular reference models used on the site

**VERIFIED — educational reference-coordinate derivation, 2026-11-05.**
These two models support the mission's evidence-literacy deliverable: visitors can
inspect how a sequence becomes a three-dimensional structure and distinguish an
experimental reference from a proposed biological simulation. Neither molecule is
presented as a Project Asma ovarian-cancer target, patient sample, digital patient,
clinical result or treatment recommendation. No study-data analysis or model
training was performed.

## Primary sources and reuse

The coordinates and chemical descriptions come from the public wwPDB archive,
served by RCSB PDB. The [RCSB usage policy](https://www.rcsb.org/pages/usage-policy),
accessed **2026-11-05**, states that archive data files and programmatic API data
are available under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
This grant applies to the coordinate data used here; it is not a claim about all
articles or illustrations on the RCSB website. We retain derived coordinates,
minimal factual metadata, original explanations and citations. We do not copy
paper text, figures, molecular illustrations or third-party software. Original
site code and prose retain the repository's terms; third-party coordinates retain
CC0. Attribution to the depositors and RCSB PDB is provided below and in each JSON.

| Model | Insulin | DNA |
| --- | --- | --- |
| Source | [RCSB PDB 1TRZ](https://www.rcsb.org/structure/1TRZ) | [RCSB PDB 1BNA](https://www.rcsb.org/structure/1BNA) |
| Coordinate file | [1TRZ.cif](https://files.rcsb.org/download/1TRZ.cif) | [1BNA.cif](https://files.rcsb.org/download/1BNA.cif) |
| Organism / preparation | Human sequence; crystalline biosynthetic insulin, marked synthetic/engineered | Synthetic DNA oligonucleotide; no source organism assigned |
| Experimental method | X-ray diffraction, 1.60 Å reported resolution | X-ray diffraction, 1.90 Å reported resolution |
| Deposited / released | 1993-11-19 / 1994-01-31 | 1981-01-26 / 1981-05-21 |
| Latest entry revision observed | 2024-11-06, version 1.4 | 2024-02-07, version 1.3 |
| Display selection | Model 1, author chains A/B; one 51-amino-acid insulin molecule | Model 1, author chains A/B; two 12-nucleotide strands |
| JSON | [insulin.json](../assets/models/insulin.json) | [dna.json](../assets/models/dna.json) |
| Retained heavy atoms | 399 | 486 |
| Covalent connections | 407 ordinary + 3 disulfide | 544 |
| Separate hydrogen contacts | None retained | 32 deposited Watson–Crick donor/acceptor pairs |
| Sequence-guide segments | 49 Cα-to-Cα | 22 C4′-to-C4′ |

**Original structure publications:**

- Ciszak E, Smith GD. “Crystallographic evidence for dual coordination around
  zinc in the T3R3 human insulin hexamer.” *Biochemistry* 33:1512–1517 (1994).
  [doi:10.1021/bi00172a030](https://doi.org/10.1021/bi00172a030).
- Drew HR, Wing RM, Takano T, Broka C, Tanaka S, Itakura K, Dickerson RE.
  “Structure of a B-DNA dodecamer: conformation and dynamics.”
  *PNAS* 78:2179–2183 (1981).
  [doi:10.1073/pnas.78.4.2179](https://doi.org/10.1073/pnas.78.4.2179).

Entry metadata was checked using the primary
[1TRZ entry API](https://data.rcsb.org/rest/v1/core/entry/1TRZ) and
[1BNA entry API](https://data.rcsb.org/rest/v1/core/entry/1BNA).
Identity/sequence checks also used
[1TRZ entity 1](https://data.rcsb.org/rest/v1/core/polymer_entity/1TRZ/1),
[1TRZ entity 2](https://data.rcsb.org/rest/v1/core/polymer_entity/1TRZ/2), and
[1BNA entity 1](https://data.rcsb.org/rest/v1/core/polymer_entity/1BNA/1).
Their polymer metadata report zero mutations and no nonstandard monomers.
“Engineered” therefore must not be paraphrased as “mutated”; equally, these are
prepared experimental samples, not observations of molecules inside a person.
The current entry revision histories were inspected; this is not an independent
reassessment of the original diffraction experiments or publications.

## Selections and scientifically important limits

### Insulin: an experimental fold, not the whole assembly

Author chain A is `GIVEQCCTSICSLYQLENYCN` (21 amino acids); chain B is
`FVNQHLCGSHLVEALYLVCGERGFFYTPKT` (30 amino acids). The entry describes a **T3R3
zinc-containing insulin hexamer**. We select just one A/B molecule from the
crystal asymmetric unit; chains C/D and crystallographic symmetry copies are not
shown. This selection does not depict the complete crystal or biological assembly.
All HETATM records, including water, zinc, chloride and sodium, are omitted.
Thus the viewer does not explain zinc coordination from the source paper.

The deposited disulfide records connect cysteine sulfur atoms A6–A11, A7–B7 and
A20–B19. Their coordinate-derived distances are 2.0032, 2.0308 and 2.0495 Å,
respectively. These are sulfur-to-sulfur covalent bonds, not direct bonds between
backbone guide points. The entire 51-residue backbone is retained. Six terminal
side-chain atoms are absent in the deposit: LYS B29 CG/CD/CE/NZ and THR B30
OG1/CG2, also listed in deposited missing-atom records. We do not reconstruct
them. The model therefore must not be called a complete all-atom insulin model.
Hydrogens are not added.

### DNA: a synthetic fragment, not a genome

Each strand has sequence `CGCGAATTCGCG`, read in its own 5′→3′ direction.
The two complementary strands run antiparallel. Author residue numbering is
A1–A12 and B13–B24; each chain's local sequence numbering is 1–12. Both schemes
are retained in the JSON. The fragment contains 12 base pairs, not 24 base pairs.
It is the synthetic Drew–Dickerson B-DNA dodecamer, not a human genome fragment,
tumour DNA or chromosome. Water and symmetry neighbours are omitted; no missing
terminal phosphates or hydrogens are fabricated.

The 32 hydrogen-contact records are the deposit's Watson–Crick donor/acceptor
heavy-atom pairs. They are stored separately from covalent bonds. They do not
provide hydrogen coordinates, bond energies, binding affinities or a complete
account of helix stability. Base stacking also contributes to stability.

## Deterministic transformation and JSON contract

[derive.py](../assets/models/derive.py) uses only Python's standard library and
accepts a directory containing the two mmCIF files. It verifies source hashes
before parsing the inspected loop tables. Download the linked public files into
a temporary directory outside the checkout, then run:

```sh
python3 assets/models/derive.py /path/to/temporary-cif-directory
```

This command rebuilds the two JSON files; it performs no network request.
It also creates the original [static insulin diagram](../assets/models/insulin-preview.svg)
for the site's non-interactive fallback. This transparent 600×440 SVG applies
fixed rotations of −20°, 25° and −25° around the x, y and z axes, then an
orthographic projection, to the same 399 deposited atom positions. Its 410
chemical connections are drawn as two coloured half-segments each, with depth
ordering; chain A is gold and chain B cyan. The 399 dots are graphical symbols,
not atom-radius measurements. No coordinate, missing atom or connection is
invented, and no backbone-guide segment is substituted for a chemical bond.
The image includes source attribution and the incomplete-model limitation in
its accessible description; the surrounding page provides the fuller limits.
The matching [DNA fallback](../assets/models/dna-preview.svg) uses rotations
of −20°, 65° and −15°, the same projection method, all 486 deposited atoms,
544 covalent connections and 32 dashed hydrogen-contact lines. It preserves the
same chain colours and identifies the synthetic fragment and display limits.
If an upstream file changes, the command stops. Review the revision and diff
before changing its hash. Full source downloads, API payloads and usage-policy
HTML are not committed. No original structure files are needed at site runtime.

- Keep ATOM records from model 1, author chains A/B, excluding H/D. Cartesian
  coordinates remain in Å (1 Å = 0.1 nm) at deposited precision. No reflection,
  coordinate fitting, smoothing, relaxation or rescaling is applied to the data.
  Viewer camera rotation and centring are display operations.
- Atom keys are author chain, author residue number and deposited atom name.
  For an alternate location, select highest occupancy; ties prefer blank then A,
  then original file order. **Neither selected model actually has alternate
  locations**, so no atoms are dropped by that policy. Insertion codes are absent;
  the converter stops if one unexpectedly appears.
- Within a residue, read connectivity and bond order from `_chem_comp_bond` and
  retain only connections whose two atoms are present. Add standard C–N peptide
  or O3′–P nucleotide links between successive residues in the same chain. Check
  those link lengths for plausible geometry; distance is a check, not a method
  for inventing connections. Read disulfides and DNA hydrogen contacts from
  `_struct_conn`, accepting only the selected, untransformed symmetry identity.
- Preserve deposited three-dimensional handedness. No stereocentres, protonation
  states, missing atoms or hydrogen positions are generated. A rendered sphere
  is a graphical marker, not a measured atom surface. A single drawn stick may
  summarize connectivity without encoding the stored single/double bond order.
- `atoms[i].id == i`; every `a`/`b` endpoint is a zero-based atom-array index.
  `residueNumber` is author numbering; `sequenceNumber` is chain-local numbering.
  `bonds[].kind` is `covalent` or `disulfide`; `contacts[].kind` is `hydrogen`.
  `backbone` links successive Cα or C4′ positions for orientation. These guides
  **are not direct chemical bonds**, experimental surfaces or additional atoms.
- `description`, three `explanation` paragraphs, `limits` and `metadata` provide
  plain-language context, accession, citation, source hash, reuse rights and
  display omissions. Neither reference establishes an ovarian-cancer target,
  gene activity, cellular dynamics, treatment response or patient benefit.

Source-file SHA-256 values, retrieved 2026-11-05:

```text
1TRZ.cif c09212b60ec05abc195ded6a30f630877eb00ee186b797133543c2d34aef3b45
1BNA.cif 76d550f32963de46f4f3c63caacb530f91a24f333fbc4312766d240b14e8cf30
```

## Verification scope

Run `python3 tools/check_site_models.py` for the standalone, standard-library
offline check. It checks source/licence pins, finite coordinates, atom indices,
sequences and residue numbering, connection lengths and components, exact
disulfide mapping, DNA contact pairing, unresolved-atom omissions and SVG
primitive counts/provenance. It makes no network request and does not substitute
for replaying the hash-pinned conversion or the independent archive-format
comparison described below.

The derivation checks pinned source identity, atom/residue/contact counts, valid
polymer links and required disulfides. A separate read of the RCSB legacy PDB
files checked the selected coordinates and sequences against the generated JSON;
endpoint bounds, duplicate bonds, finite coordinates, graph connectivity and
expected disulfide pairs were also checked. The insulin graph is one connected
component; DNA has two covalently connected components and one component when
its separately labelled hydrogen contacts are included.

These checks verify the conversion and display inputs. They do not validate a
clinical model, reproduce the original crystallography, simulate molecular
motion, certify an inferred interaction or establish biological benefit.
