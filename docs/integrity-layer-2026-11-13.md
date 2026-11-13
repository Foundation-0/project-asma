# Integrity layer, 2026-11-13

This note records an offline bookkeeping layer for the public claims ledger. It is not scientific review, not clinical validation, and not a substitute for rerunning network audits on study sources.

## Components

1. **Claims ledger export** — `tools/export_claims_ledger.py` writes `registries/claims-ledger.json` with one record per labelled claim (identifier, label, statement, cited source ids, re-check commands, linked certificate paths, canonical SHA-256). `python3 tools/export_claims_ledger.py --check` fails when the committed export is stale.
2. **SHA-256 manifests** — `tools/check_sha256_manifests.py` replays every `SHA256SUMS` under `results/` and recomputes digest-bound `certificate_sha256` fields in registry JSON.
3. **Checker audit** — `tools/audit_checkers.py` walks VERIFIED claims in the ledger export, runs deduplicated offline re-check commands, and probes digest-bound certificates for tamper sensitivity. The frozen report is `results/integrity-audit-2026-11-13/audit.json`; `results/integrity-audit-2026-11-13/verify.py` replays it.

## V37 and V38 offline replay

`tools/audit_cdr2l_source_psm.py --check` and `tools/audit_cdr2l_spectrum_locator.py --check` verify committed certificates against pinned producing-code `implementation_sha256` (and the current tool hash where it differs), identification match fields, and MGF byte pins without `--live` network retrieval.

## Audit coverage (40 VERIFIED rows)

- **24** rows name at least one offline re-check command (`runs_offline: true`).
- **23** of those first commands replay with exit 0 inside the audit; **V02** (`python3 -m unittest discover -s tests -v`) is listed under `skipped_heavy_recheck` and is not executed in the audit (CI still runs the full suite). The added offline row is V42, the frozen 2026-11-13 trial-landscape recount.
- **16** rows have no offline checker (`no_offline_checker` in the audit summary):
  - **Doc-only (no command):** V03, V04, V05, V20, V21, V24, V27, V35.
  - **Network-only (commands filtered):** V08, V10, V11, V12, V13, V14, V15, V16.
- **`tamper_misses`** counts digest-bound certificates where a tamper probe did not fail (target 0). This is not the same as lacking an offline checker.

## Limits

- Network metadata audits are not replayed in this layer.
- Tamper probes cover certificates with `certificate_sha256` or a string `implementation_sha256` on digest-bound tools only.

Prepared with AI assistance (Cursor cloud agent, Composer 2.5) under human direction.
