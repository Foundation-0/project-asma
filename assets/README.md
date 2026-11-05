# Site assets

| File | Source | Terms |
|---|---|---|
| `f0.css`, `f0.js` | `docs/assets/` in [Foundation-0/f0](https://github.com/Foundation-0/f0) at commit [`e41f7be`](https://github.com/Foundation-0/f0/tree/e41f7be8705c86232e0c2a0abc56574869be1e50/docs/assets), the head of its `main` when the copy was taken on 2026-10-23. Trimmed on 2026-10-25; each file's header lists what was removed. | [Apache License 2.0](https://github.com/Foundation-0/f0/blob/e41f7be8705c86232e0c2a0abc56574869be1e50/LICENSE) |
| `favicon.svg` | Same commit, unchanged (byte-identical). | Apache License 2.0, as above |
| `og.png` | Drawn for this site. | CC BY 4.0, under the current repository LICENSE |

The copies were matched to the source by Git blob hash: the files first added on
this branch (`3420bce`) are identical to those at `e41f7be`. The Apache License 2.0
covers only the files taken from `f0`; it grants nothing for the rest of this
repository.

## Educational playground, 2026-11-05

- `research-lab.js` and `molecular-viewer.js`: original Project Asma code, MIT.
- `vendor/three.module.min.js`: locally bundled Three.js 0.170.0 subset, MIT;
  exact package version, build entry and hashes are in [vendor/README.md](vendor/README.md),
  with the complete [upstream licence](vendor/THREE-LICENSE.txt).
- `models/insulin.json` and `models/dna.json`: selected, derived RCSB/wwPDB
  reference coordinates and minimal metadata, CC0. Source citations, hashes,
  conversion rules and omissions: [structure record](../docs/site-structure-sources.md).
  The static insulin projection is original site artwork based on those coordinates.
- The existing Apache-licensed `f0.js` additionally closes its compact navigation
  after an anchor selection. Original attribution remains in its header.

All viewer dependencies and coordinate files are served from this site. Clicking
source links visits external primary records; the site itself does not request
external fonts, analytics, molecule services or CDN scripts. The 3D renderer
rotates a static reference: it is not molecular dynamics or a virtual patient.
