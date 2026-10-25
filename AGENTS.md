# Agent guidance

This repository is a research scaffold, not clinical decision support.

- Inspect current instructions and Git status; preserve concurrent work. Keep
  changes in a branch/PR. Do not merge, deploy, change permissions/settings,
  enable auto-merge, or use paid services without explicit authorization.
- Read the [pilot](protocols/pilot-001.md) and
  [data rules](docs/reproducibility-and-data.md) before research changes.
- Use primary sources; check corrections and access dates. Separate published
  reference values, hypotheses, proposed work, and executed results. Never invent
  results, citations, patient records, or a license grant.
- Preserve distinctions between primary refractory disease, later platinum
  resistance, histotypes, assay types, and independent versus overlapping patients.
  Fit learned preprocessing only inside training folds for honest evaluation.
- Do not ingest patient data/datasets, run third-party analysis code, train models,
  contact collaborators, or publish row-level outputs in a scaffold task. Future
  ingestion needs verified rights and appropriate authorization. Bounded,
  in-memory inspection of the pinned study sources, including rerunning the
  recorded network audits, is part of autonomous research (owner decision,
  2026-10-25): record what was read and why, keep only aggregates, and never
  persist row-level data, identifiers or linkage keys. Live acquisition of study
  files, a real-source input check or fitting on study values needs the owner's
  dated attestation of the execution context and a new explicit instruction; a
  session's own checks never satisfy it.
- Outreach (owner decision, 2026-10-25): the consolidated
  [source request](templates/pilot-001-source-request.md) is authorized as a
  draft only. The owner alone decides whether and when to send it, from their
  own account. Automated sessions must never post, retry posting, email or
  otherwise send it, or contact authors by any route; the earlier automated
  posting attempts should not have happened. Do not recruit
  collaborators/reviewers without a new explicit instruction.
- Keep this workspace lean. Prefer standard-library checks over new dependencies
  or empty architecture. Do not create CI or issue backlogs without need.
- Run `python3 tools/validate.py` and
  `python3 -m unittest discover -s tests -v` on the final tree. Report what these
  checks cannot establish. Review staged files for data, secrets, and private text.

Owner decisions and scientific review gates are in the [roadmap](docs/roadmap.md).
