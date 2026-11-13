# Provenance for the 2026-11-13 Soko-to-Asma unlocks drop

Landed from the gem-nexus Drive vault file `2026-11-13_soko-to-project-asma-unlocks.zip`
(id `1V4skuztYCAFVtvcIxDJ64XoE_1OWvvIK`, 10906 bytes,
sha256 `72c9cf06e2e5db6e0a7039b7a22f0015bfe00fc364fa8f9fa87924fa65f450d4`).

The four payload files match the zip's `SHA256SUMS`, checked from the repository root:

- `tools/verify_soko_asma_unlocks.py` `e31f7f0f52b7260886a073e0b1d105c10f7c86c88dd0380e3ef6e7ec69f89429`
- `tests/test_soko_asma_unlocks.py` `a3417060229fa193b4871249dc916e40605a59fc609eb81fae7e6895abf5efd6`
- `results/soko-asma-unlocks-20261113/README.md` `e20c9ed595650a5134d206e3a504723eb47d2d5578949b2d9a807d762a09d92b`
- `results/soko-asma-unlocks-20261113/certificate.json` `8e48ffdeb3965f4b01cd3d21eee46a5054608d76c543821f13092b5725bb2ba7`

`SHA256SUMS` itself is `b653bd5724020a1ce6144df42e87012dc97e5e8a60cb24e5aa308c2989b7b935`.

The checker, tests, README, certificate, and `SHA256SUMS` are the vault payload, kept byte-identical. Numbers and status words inside those files are unreproduced Carbon claims, pending independent review. The four design ceilings restated under `pinned_s16_lh_bounds` already appear on main from #87.

Replay from the repository root:

```bash
python3 -m unittest tests.test_soko_asma_unlocks -v
python3 tools/verify_soko_asma_unlocks.py
sha256sum -c results/soko-asma-unlocks-20261113/SHA256SUMS
```
