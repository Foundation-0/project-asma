# Synthetic Soko-to-Asma Phase-Transition & Identifiability Unlocks (2026-11-13)

Research-scaffolding verification drop only:
- **Zero study or clinical patient data ingested** (`study_data_bytes = 0`, `patient_data_rows = 0`).
- **Zero clinical claims or decision recommendations**.
- Designed to drop cleanly onto [Foundation-0/project-asma](https://github.com/Foundation-0/project-asma) alongside [PR #77](https://github.com/Foundation-0/project-asma/pull/77), [PR #78](https://github.com/Foundation-0/project-asma/pull/78), [Issue #82](https://github.com/Foundation-0/project-asma/issues/82), [PR #86](https://github.com/Foundation-0/project-asma/pull/86), and [PR #87](https://github.com/Foundation-0/project-asma/pull/87).

## Quick Replay

```bash
python3 -m unittest discover -s tests -v
python3 tools/verify_soko_asma_unlocks.py
sha256sum -c results/soko-asma-unlocks-20261113/SHA256SUMS
```
