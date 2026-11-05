# Pilot 001: first real-data run runbook

**Status:** preparation only. **No real study-data reconstruction has been executed** in this repository or by automated CI.

This runbook describes how the owner (or delegate) runs the gated first research execution on a **macOS** host in Canada after Gate 0, attestation, and grk-helix clearance on the Dropbox matrix. Linux CI and cloud agents perform **synthetic dry runs only**.

## Preconditions

1. [Gate 0](roadmap.md) scope and rights answered (issue **#31**).
2. Owner **dated attestation** of execution context in `registries/pilot-001-owner-attestations.json` (local only; never committed). Attestation reference format: `id:YYYY-MM-DD` in **America/Toronto** calendar date; valid only on the attested date.
3. grk-helix clearance recorded for the author Dropbox matrix on the Canadian Mac host.
4. `--gate0-signed` and `--dropbox-cleared` both required for real mode; both default **off**. `--dropbox-cleared` is accepted only when `--host macos` **and** macOS preflight passes in the **same** invocation.

---

## Mac install footprint — read before any Mac command

**Do not run build, preflight, or first-run commands on the owner Mac until you have read this section end-to-end.** Nothing below assumes a probe has already been taken on **Ahrazs-MacBook-Pro** (Docker Desktop version, disk headroom, and local image digests on that host are **not recorded here**).

Measured reference (GitHub Actions Verify run [42095416191](https://github.com/Foundation-0/project-asma/actions/runs/42095416191) on branch head `d84be451`, `linux/amd64` CI runner — **not transferable** to Apple Silicon under amd64 emulation; refresh `Size` / `peak_rss_kib` after you rebuild locally):

| Metric | CI value |
| --- | --- |
| `asma-synthetic:4.4.3` image `Size` (bytes) | `444544832` |
| Dry-run orchestrator `peak_rss_kib` | `29584` |

### (1) Host prerequisites

| Requirement | Detail |
| --- | --- |
| **Docker Desktop** | Required for builds and for the container pipeline. Install current stable for your Mac (Apple Silicon or Intel). |
| **VM swap** | Docker Desktop **Resources → Advanced → Swap** must be **0 MiB**. macOS preflight reads `~/Library/Group Containers/group.com.docker/settings.json` (`swapMiB`) and **fails** otherwise. |
| **Core dumps** | Host `ulimit -c` must be `0` (preflight checks). |
| **Output path** | Must not live under iCloud Drive, Dropbox-synced folders, or Time Machine–included paths (preflight uses `tmutil isexcluded` on macOS). |
| **Repo checkout** | Owner-chosen path **outside** iCloud/Dropbox/Time Machine backup targets; this tree is bind-mounted read-only into the container. |
| **Ahrazs-MacBook-Pro** | Docker version, disk space, and image IDs on that machine were **not probed** in CI. **First command on the Mac** (after reading this list) should be step **0** below — not a build or run. |

**Step 0 — first probe (one line):**

```bash
docker version --format 'Client={{.Client.Version}} Server={{.Server.Version}} Arch={{.Server.Arch}}' ; uname -m
```

Record the output with the attestation notes. On Apple Silicon (`uname -m` = `arm64`), build and run the **linux/arm64** synthetic tag; keep the amd64 tag available as the recorded reference pair for equivalence.

### Apple Silicon (arm64 Mac) before `--real`

1. Build both synthetic images (step **2** twice with `--platform linux/amd64` and `--platform linux/arm64`).
2. Run cross-arch equivalence and write the pass artifact beside other first-run outputs:

```bash
python3 tools/run_cross_arch_equivalence.py --run-docker \
  --write-pass "$HOME/pilot001-first-run-out/pilot001-cross-arch-equivalence-pass.json"
```

3. Use `--image asma-synthetic:4.4.3-arm64` and keep `--reference-image asma-synthetic:4.4.3` on the real-run command. The orchestrator refuses `--real` on arm64 hosts unless the pass record matches both image IDs.

Expect `Arch=arm64` from step **0** when Docker runs the native arm64 image (not amd64 emulation).

### (2) Images and layers

| Layer / tag | Identity | Notes |
| --- | --- | --- |
| **Base R image** | `rocker/r-ver@sha256:3dae5d2eeddf74f10e0a81fb6b7ae350295e288000304f438b844b2c1e00fe2c` from **docker.io** | Declared in [runtime/synthetic-packages.json](../runtime/synthetic-packages.json); R **4.4.3** on **linux/amd64**. |
| **Synthetic runtime** | Tag `asma-synthetic:4.4.3` · platform **linux/amd64** · Tag `asma-synthetic:4.4.3-arm64` · platform **linux/arm64** (same CRAN package pins) | Rebuild amd64: `python3 tools/build_synthetic_runtime.py --platform linux/amd64`. Rebuild arm64: `python3 tools/build_synthetic_runtime.py --platform linux/arm64`. On Apple Silicon, prefer the **native arm64** tag over amd64 emulation. |
| **Cross-arch equivalence** | Required before `--real` on **macOS arm64** | After both images exist locally, run `python3 tools/run_cross_arch_equivalence.py --run-docker --write-pass "$HOME/pilot001-first-run-out/pilot001-cross-arch-equivalence-pass.json"`. CI runs the same comparator in [`.github/workflows/cross-arch-equivalence.yml`](../.github/workflows/cross-arch-equivalence.yml) (QEMU + buildx). Tolerances: [`registries/pilot-001-cross-arch-equivalence-tolerance.json`](../registries/pilot-001-cross-arch-equivalence-tolerance.json). |
| **Source-adapter runtime** | Tag `asma-source-adapter:3.12.14-4.4.3` · Id `sha256:abe1ad546d148230e624ecf8d0a75ea8a0b50308f98b816582e7b6bc406e9300` (Verify CI; **size not teed** in workflow) | Rebuild: `python3 tools/build_source_adapter_runtime.py --accept-rebuilt-base`. Builder sets `base_rebuilt: true` when the live synthetic base differs from the **recorded** synthetic Id `sha256:ffc2f55117d54c3978eaa6d0bb242e6d5526e1667a70e78c724b2a59f3789e35` in [runtime/source-adapter-python.json](../runtime/source-adapter-python.json); both Ids are printed in the build JSON line. |
| **CPython (adapter only)** | **3.12.14** pin | [runtime/source-adapter-python.json](../runtime/source-adapter-python.json) (`Python-3.12.14.tar.xz`). |

**R packages** installed from source in the synthetic image ([runtime/synthetic-packages.json](../runtime/synthetic-packages.json)):

| Package | Version |
| --- | --- |
| Rcpp | 1.0.14 |
| RcppEigen | 0.3.4.0.2 |
| iterators | 1.0.14 |
| foreach | 1.5.2 |
| shape | 1.4.6.1 |
| data.table | 1.17.0 |
| jsonlite | 1.9.1 |
| glmnet | 4.1-8 |
| randomForest | 4.7-1.2 |
| xgboost | 1.7.8.1 |

**Base/recommended pins on the rocker digest** (not separately installed from CRAN in the lockfile): Matrix **1.7-2**, survival **3.8-3**, lattice **0.22-6**, codetools **0.2-20**.

After local builds, refresh inspect output (sizes change with rebuild):

```bash
docker image inspect asma-synthetic:4.4.3 --format 'Id={{.Id}} Size={{.Size}} Arch={{.Architecture}}'
docker image inspect asma-source-adapter:3.12.14-4.4.3 --format 'Id={{.Id}} Size={{.Size}} Arch={{.Architecture}}'
```

### (3) Host write paths

| Location | What writes there |
| --- | --- |
| **Repository checkout** | Git only. **Dry run / analyze** mount the repo at `/work` read-only. **Fetch phase** mounts only `tools/` and the input manifest (not the owner attestation registry). Choose a path outside iCloud/Dropbox/TM. |
| **`$HOME/pilot001-first-run-out`** (or owner-chosen equivalent) | **Only** allow-listed aggregates: `pilot001-preflight-report.json`, `pilot001-first-run-aggregate.json`. Bind-mounted to `/output`. Preflight **refuses** iCloud/Dropbox/TM-backed output paths. |
| **Docker Desktop `Docker.raw`** | Image layers and container writable layers (not controlled by this repo). |
| **Container `/tmp`** | Dry-run: **tmpfs 512m**. Real **analyze** phase: tmpfs for R caches and ephemeral adapter→R JSON (under `/tmp/pilot001-study`); never bind-mounted to the host output directory. |
| **Study handoff volume** | Real mode **`pilot001-handoff-*` tmpfs Docker volume** (`docker volume create --opt type=tmpfs --opt device=tmpfs --opt o=size=512m,mode=0700 …`) holds **compressed** Dropbox member bytes plus workbook bytes between phase 1 and phase 2. Removed by orchestrator postflight. Docker may still store volume **metadata** on the Desktop VM disk even when the volume driver is tmpfs. |

### (4) Network

**Image build time (host downloads, then `docker build --network=none`):**

| Host / purpose | Used for |
| --- | --- |
| **docker.io** | Pull `rocker/r-ver@sha256:3dae5d2e…` |
| **cran.r-project.org** | Pinned R source tarballs in `runtime/synthetic-packages.json` |
| **www.python.org** | CPython **3.12.14** source for adapter image |
| **snapshot.ubuntu.com** | Pinned `.deb` build deps for adapter (`runtime/source-adapter-python.json`) |
| **Launchpad / Ubuntu changelogs** | License notice fetches documented in the adapter lockfile |

**Real first-run study fetches (gated `--real` on owner Mac only):**

| Host | Role |
| --- | --- |
| **www.dropbox.com** | Author `processed_data.zip` compressed member ranges (**compressed** bytes pinned in manifest for phase 1; **uncompressed** member pinned for phase 2 after offline inflate) |
| **pmc-oa-opendata.s3.us-east-1.amazonaws.com** | MMC1 / MMC4 workbooks for Pilot 001 |

**Policy:** Study bytes stay in **container tmpfs only** — never written under the host `/output` bind mount or synced folders.

**Two-phase real mode (phase separation, not a kernel firewall):**

| Phase | Container | Network | Work |
| --- | --- | --- | --- |
| **1 — fetch** | `fetch_container.py` | **`bridge`** (egress for allowlisted HTTPS only) | Download, verify **compressed-byte** manifest pin (+ workbook pins), write **compressed** member and workbooks to **tmpfs handoff volume**. No inflate, adapter, R, or row-level matrices. |
| **2 — analyze** | `analyze_container.py` | **`none`** | Read-only handoff → offline inflate + **uncompressed** manifest pin → `parse_sources()` → R → aggregate JSON on **stdout** (host validates and writes `/output`). |

**Fetch allowlist:** `www.dropbox.com`, `pmc-oa-opendata.s3.us-east-1.amazonaws.com`, `dl.dropboxusercontent.com`, and `*.dl.dropboxusercontent.com` CDN hosts. `allowlisted_fetch.py` disables urllib auto-redirects and validates **each hop** (HTTPS only; no downgrade) before following.

**Handoff volume (tmpfs):** Payload bytes live in a **512 MiB tmpfs** Docker volume (`mode=0700`). Docker Desktop may still record the volume name and driver options on the VM disk until **`docker volume rm`**. Postflight fails if any `pilot001-handoff-*` volume remains; macOS preflight requires **Docker swap = 0 MiB**.

**Integrity:** [registries/pilot-001-first-run-input-manifest.json](../registries/pilot-001-first-run-input-manifest.json) pins **both** the Dropbox member on the wire (`author_dropbox_member_compressed`: SHA-256 + bytes) and after offline inflate (`author_dropbox_member`: SHA-256 + bytes). Phase **1** checks compressed (+ workbook) pins before handoff; phase **2** re-checks compressed, inflates, then checks the uncompressed pin before parse.

**Attestation:** The host runs the full attestation gate **before** phase 1. Phase **2** bind-mounts `registries/pilot-001-owner-attestations.json` (when present locally) for `parse_sources()` authorization. Phase **1** does not mount that file.

**Native linux/arm64 synthetic builds and amd64↔arm64 equivalence checks** are intentionally **out of scope** (sibling PR).

### (5) Exact approved command sequence

Run from the **repository root** after step **0**. Replace attestation ref and dates with the owner’s valid Gate 0 attestation.

| Step | Action | Command |
| --- | --- | --- |
| **0** | First probe (see **(1)**) | `docker version --format 'Client={{.Client.Version}} Server={{.Server.Version}} Arch={{.Server.Arch}}' ; uname -m` |
| **1** | Configure Docker Desktop | **Swap = 0 MiB**; confirm Docker is running. |
| **2** | Build synthetic images | `python3 tools/build_synthetic_runtime.py --platform linux/amd64` then `python3 tools/build_synthetic_runtime.py --platform linux/arm64` |
| **2b** | Cross-arch equivalence (Apple Silicon / before `--real`) | `python3 tools/run_cross_arch_equivalence.py --run-docker --write-pass "$HOME/pilot001-first-run-out/pilot001-cross-arch-equivalence-pass.json"` |
| **3** | Build source-adapter image | `python3 tools/build_source_adapter_runtime.py --accept-rebuilt-base` |
| **4** | Record image ids (optional) | `docker image inspect asma-synthetic:4.4.3 --format '{{.Id}} {{.Architecture}}'` |
| **5** | Preflight (read-only) | `python3 tools/pilot001_preflight.py --host macos --output-dir "$HOME/pilot001-first-run-out"` |
| **6** | Optional dry run (synthetic; same gates as CI) | `python3 tools/run_pilot001_first_run.py --host macos --output-dir "$HOME/pilot001-first-run-out" --image asma-synthetic:4.4.3` — **no** `--real`, **no** `--gate0-signed`, **no** `--dropbox-cleared` |
| **7** | Real run (owner Mac only; gated) | Command below — uses **`asma-source-adapter:3.12.14-4.4.3`** automatically unless `--image` overrides the synthetic default |

**Real run command (documented target; not executed in repo/CI):**

```bash
python3 tools/run_pilot001_first_run.py \
  --host macos \
  --output-dir "$HOME/pilot001-first-run-out" \
  --real \
  --gate0-signed \
  --gate0-attestation-ref 'OWNER_ID:2026-11-05' \
  --dropbox-cleared \
  --reference-image asma-synthetic:4.4.3 \
  --image asma-synthetic:4.4.3-arm64
```

The attestation date must equal **today** in `America/Toronto`. Phase 1 writes verified **compressed** study bytes to a **tmpfs handoff volume** (not the host output directory). Phase 2 parses and models offline with **`--network=none`**; the host promotes validated aggregate JSON to the output bind mount from container stdout.

Non-zero preflight exit prints a JSON report with aggregate-safe fields only.

### (6) Uninstall, cleanup, and postflight

After review (success or abort):

```bash
rm -rf "$HOME/pilot001-first-run-out"
docker rm -f $(docker ps -aq --filter 'name=pilot001-run-') 2>/dev/null || true
docker rmi asma-synthetic:4.4.3 asma-source-adapter:3.12.14-4.4.3
docker ps -a --filter 'name=pilot001-run-'
docker volume ls --filter name=pilot001-handoff-
```

Expect **no** `pilot001-run-*` containers and no run-specific volumes. The entrypoint’s postflight also fails with **`P001-FAIL-POSTFLIGHT`** if any `pilot001-run-*` container remains.

To reclaim Docker disk space after removing tags, use Docker Desktop **Troubleshoot → Clean / Purge data** only if you accept deleting **all** local images.

---

## Dry run (synthetic; safe on linux-ci)

```bash
python3 tools/run_pilot001_first_run.py --host linux-ci --output-dir /tmp/pilot001-out
```

Uses the `--dry-run` container path with synthetic fixtures only. **Does not** pass `--gate0-signed`, `--dropbox-cleared`, or `--real`.

CI invokes the same orchestration via `python3 tools/run_pilot001_dry_run.py` after building `asma-synthetic:4.4.3`.

## Outputs on disk

After success, the output directory contains only:

- `pilot001-preflight-report.json`
- `pilot001-first-run-aggregate.json` (exploratory; not externally reviewed)

No row-level scores, matrices, or study files are written.

## Abort conditions

- Preflight failure (core dump limit, forbidden output path, Docker swap ≠ 0, Time Machine–included paths, iCloud/Dropbox-synced output paths).
- Any aggregate failure code (`P001-FAIL-*`) from the entrypoint.
- Output validator detecting row-level or identifier-like content.
- Postflight showing leftover `pilot001-run-*` containers.
- **`P001-FAIL-INPUT-INTEGRITY`**, **`P001-FAIL-FETCH-HOST`**, or other **`P001-FAIL-*`** codes from fetch, adapter, or reconstruction.

## What this repository proves without a real run

- Amendment 1 code paths (A1 distribution, A2 hist + seed block 101–200, A3 strict warnings/messages/console) on synthetic fixtures.
- Gating and grk-helix `--dropbox-cleared` rules in unit tests.
- CI dry run through the same orchestration entrypoint with flags default off and **no study bytes fetched**.
