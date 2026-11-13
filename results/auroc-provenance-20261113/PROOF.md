# Discovery AUROC provenance

**Evidence labels: K44 and K45 are KNOWN citations. V44 is a VERIFIED finite
check of released scores. C26 is a CONJECTURE. No mathematical proof and no
clinical claim is made.**

The [dated note](../../docs/auroc-provenance-20261113.md) states where 0.83 is
printed, where 0.8088507877664504 is calculated, and the difference between
discrimination and clinical utility. `certificate.json` holds the aggregate
arithmetic and the source locators. Scores and identifiers are not stored.

```sh
python3 results/auroc-provenance-20261113/verify.py
```

The checker replays the pair fraction, the half-up rounding, the DeLong
interval from the frozen variance components, and the bootstrap percentile from
the frozen numerators. It checks the SHA-256 manifest and the repository
occurrence inventory. It does not re-read the workbooks.

**An AUROC is discrimination of scores. It is not clinical utility and not a
treatment rule.**
