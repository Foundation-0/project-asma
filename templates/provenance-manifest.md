# Provenance and patient-overlap manifest specification

**Proposed specification only; no patient rows or data files are included.**
Create future manifests in authorized storage outside Git. A pseudonymous key
can still be sensitive. Do not publish linkage keys, row-level labels, or paths
that identify participants. Publish only reviewed aggregate flow/overlap counts.

| Private record | Required fields |
| --- | --- |
| File provenance | Dataset ID, source URL, release/version, retrieval timestamp, file identifier/name, SHA-256, byte count, access tier, terms review/date, authorized storage location |
| Transform | Input checksums, code commit, command, parameters/seed, environment, output checksum, reason and date |
| Patient/assay relationships | Local patient key, source case key, specimen and aliquot keys, assay, preservation, site/batch, collection/treatment timing, primary/metastatic relation, dataset/cohort |
| Endpoint | Label source/version, refractory/sensitive definition, observation window, missingness, eligibility and exclusion reason |
| Evaluation | Patient group, discovery/validation role, overlap status (independent/overlapping/unresolved), evidence for linkage, split assignment, whether used for alignment or any fitting |

Before fitting, reconcile file/sample/patient counts; identify repeated aliquots,
matched FFPE/frozen tissue and different tumors from one patient. Check collisions
and unmapped keys. Missing overlap evidence is **unresolved**, not independent.
Ensure no patient enters training and the independent test set, including through
preprocessing/alignment. Record any published overlap separately from the revised
evaluation. Do not create example patient rows that could be mistaken for data.
