# Integrity layer, 2026-11-13

This note records an offline bookkeeping layer for the public claims ledger. It is not scientific review, not clinical validation, and not a substitute for rerunning network audits on study sources.

## Components

1. **Claims ledger export** — `tools/export_claims_ledger.py` writes `registries/claims-ledger.json` with one record per labelled claim (identifier, label, statement, cited source ids, re-check commands, linked certificate paths, canonical SHA-256). `python3 tools/export_claims_ledger.py --check` fails when the committed export is stale.
2. **SHA-256 manifests** — `tools/check_sha256_manifests.py` replays every `SHA256SUMS` under `results/` and recomputes digest-bound `certificate_sha256` fields in registry JSON.
3. **Checker audit** — `tools/audit_checkers.py` walks VERIFIED claims in the ledger export, runs deduplicated offline re-check commands, and probes digest-bound certificates for tamper sensitivity. The frozen report is `results/integrity-audit-2026-11-13/audit.json`; `results/integrity-audit-2026-11-13/verify.py` replays it.

## V37 and V38 offline replay

`tools/audit_cdr2l_source_psm.py --check` and `tools/audit_cdr2l_spectrum_locator.py --check` now verify committed certificates against tool `implementation_sha256` and pinned identity fields without `--live` network retrieval.

## Limits

- Doc-only re-checks (synthetic validation write-ups, IEDB prose replay commands without a ledger command) are reported as lacking offline CLI in the audit.
- Network metadata audits are not replayed in this layer.
- Tamper probes cover certificates with `certificate_sha256` or a string `implementation_sha256` on digest-bound tools only.

Prepared with AI assistance (Cursor cloud agent, Composer 2.5) under human direction.
