# TCGA-OV cohort reconciliation, 2026-11-13 UTC

**Evidence label: VERIFIED, finite catalog count. No mathematical, biological,
or clinical proof is claimed.**

The [dated report](../../docs/tcga-ov-cohort-reconciliation-20261113.md) states
what 608 and 489 count, the exact requests, the overlap counts, and the limits.
`certificate.json` is the aggregate result. The `snapshot/` files are open
metadata responses and projections. Identifier bodies were not stored. No
controlled-access file contents were downloaded.

```sh
python3 results/tcga-ov-cohort-reconciliation-20261113/verify.py
```

The checker requires the export reader and the recompute reader to agree, the
certificate and the report count block to match that agreement, the SHA-256
manifest to match the stored files, and no email address or TCGA barcode to
remain in the frozen JSON. Offline replay checks facet sums and overlap
arithmetic. It does not rebuild the identifier sets.

**Not clinical guidance and not a biological conclusion.** A case count is a
data-availability denominator. It does not say who should be treated, how a
tumour behaves, or which catalog is the right one for a later scientific question.
