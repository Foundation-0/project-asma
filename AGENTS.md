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
  ingestion needs verified rights and appropriate authorization. A real-source
  input check or fitting on study values also needs the owner's dated attestation
  of the execution context and a new explicit instruction; a session's own checks
  never satisfy it.
- On 2026-10-24 the user explicitly authorized putting the code-audit questions
  to the authors through the consolidated
  [source request](templates/pilot-001-source-request.md). The owner confirms its
  full text and sends it from their own account. Automated sessions must not
  post, retry posting or email it. Do not contact authors beyond that request, or
  recruit collaborators/reviewers, without a new explicit instruction. The
  2026-10-25 reconstruction records, prepared without this record, describe
  outreach as on hold; until the owner reconciles the two, treat the request as
  unsent and on hold.
- Keep this workspace lean. Prefer standard-library checks over new dependencies
  or empty architecture. Do not create CI or issue backlogs without need.
- Run `python3 tools/validate.py` and
  `python3 -m unittest discover -s tests -v` on the final tree. Report what these
  checks cannot establish. Review staged files for data, secrets, and private text.

Owner decisions and scientific review gates are in the [roadmap](docs/roadmap.md).
