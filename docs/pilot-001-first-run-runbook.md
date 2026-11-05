# Pilot 001: first real-data run runbook

**Status:** preparation only. **No real study-data reconstruction has been executed** in this repository or by automated CI.

This runbook describes how the owner (or delegate) runs the gated first research execution on a **macOS** host in Canada after Gate 0, attestation, and grk-helix clearance on the Dropbox matrix. Linux CI and cloud agents perform **synthetic dry runs only**.

## Preconditions

1. [Gate 0](roadmap.md) scope and rights answered (issue **#31**).
2. Owner **dated attestation** of execution context in `registries/pilot-001-owner-attestations.json` (local only; never committed). Attestation reference format: `id:YYYY-MM-DD` in **America/Toronto** calendar date; valid only on the attested date.
3. grk-helix clearance recorded for the author Dropbox matrix on the Canadian Mac host.
4. `--gate0-signed` and `--dropbox-cleared` both required for real mode; both default **off**. `--dropbox-cleared` is accepted only when `--host macos` **and** macOS preflight passes in the **same** invocation.

## macOS install (owner host)

1. Install **Docker Desktop** (current stable for Apple Silicon or Intel as appropriate).
2. Set Docker Desktop **VM swap to 0 MiB** (preflight fails otherwise).
3. Pull/build the pinned runtime (same R 4.4.3 stack as Verify CI):

```bash
python3 tools/build_synthetic_runtime.py
python3 tools/build_source_adapter_runtime.py --accept-rebuilt-base
```

4. Record image digest:

```bash
docker image inspect asma-synthetic:4.4.3 --format '{{.Id}} {{.Architecture}}'
```

**Measured needs (linux-ci dry run, synthetic path):** image size is reported by `docker image inspect asma-synthetic:4.4.3 --format '{{.Size}}'` (bytes). Peak RSS of the dry-run orchestrator is printed as `peak_rss_kib` in the CI `pilot001-dry-run.json` artifact line (child process max RSS; not a clinical measurement).

**arm64 note:** Verify CI builds on `linux/amd64`. Before a real Mac run, confirm an **arm64** image with identical package versions exists, or run the documented cross-architecture synthetic equivalence check. If only amd64 is available, expect emulation and treat timing/RSS as non-transferable.

## Preflight (read-only)

```bash
python3 tools/pilot001_preflight.py --host macos --output-dir "$HOME/pilot001-first-run-out"
```

Non-zero exit prints a JSON report on stderr-safe aggregate fields only.

## Dry run (synthetic; safe on linux-ci)

```bash
python3 tools/run_pilot001_first_run.py --host linux-ci --output-dir /tmp/pilot001-out
```

Uses `--dry-run` container path with synthetic fixtures only. **Does not** pass `--gate0-signed`, `--dropbox-cleared`, or `--real`.

## Real run command (owner Mac only; not executed here)

```bash
python3 tools/run_pilot001_first_run.py \
  --host macos \
  --output-dir "$HOME/pilot001-first-run-out" \
  --real \
  --gate0-signed \
  --gate0-attestation-ref 'OWNER_ID:2026-11-05' \
  --dropbox-cleared \
  --image asma-synthetic:4.4.3
```

The attestation date must equal **today** in `America/Toronto`. Real fetch occurs **inside** the container only; host mounts only the aggregate output directory (see `tools/pilot001_first_run/runner.py`).

## Outputs on disk

After success, the output directory contains only:

- `pilot001-preflight-report.json`
- `pilot001-first-run-aggregate.json` (exploratory; not externally reviewed)

No row-level scores, matrices, or study files are written. Remove the output directory after review:

```bash
rm -rf "$HOME/pilot001-first-run-out"
```

## Abort conditions

- Preflight failure (core dump limit, forbidden output path, Docker swap ≠ 0, Time Machine–included paths, iCloud/Dropbox-synced output paths).
- Any aggregate failure code (`P001-FAIL-*`) from the entrypoint.
- Output validator detecting row-level or identifier-like content.
- Postflight showing leftover `pilot001-run-*` containers.

## What this repository proves without a real run

- Amendment 1 code paths (A1 distribution, A2 hist + seed block 101–200, A3 strict warnings/messages/console) on synthetic fixtures.
- Gating and grk-helix `--dropbox-cleared` rules in unit tests.
- CI dry run through the same orchestration entrypoint with flags default off and **no study bytes fetched**.
