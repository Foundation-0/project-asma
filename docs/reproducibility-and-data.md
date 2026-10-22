# Reproducibility and data protection

## Evidence and execution

Label each assertion as established clinical evidence, experimental evidence,
hypothesis, proposed work, or executed result. Cite primary sources with date,
population, endpoint, and limits. Check corrections and distinguish a paper's
claim from our inference. A successful local validator is not a successful
scientific reproduction.

For any future analysis, retain a protocol version, exact source commit and
input release/checksums, patient-grouped splits, fitted preprocessing scope,
dependency lock/environment information, seeds, commands, compute/time record,
and exclusions/deviations. Record failure and null results. Start with a small
authorized feasibility run; do not download large datasets or train models as
part of preparing this scaffold.

## Data boundaries

This public repository stores documentation, code, metadata registries, and
reviewed aggregate results only. Do not commit patient records, clinical rows,
identifiers or linkage keys (including pseudonymous ones), raw or processed
research datasets, controlled genomic files, credentials, or unpublished/private
project context. Do not send such material to external AI services.

Before future ingestion, confirm each file's access tier, consent and permitted
uses, current portal terms, attribution/publication obligations, institutional
review requirements, and appropriate storage. An Open portal label is not a
blanket redistribution license. Controlled genomic data require appropriate
authorization and, where applicable, dbGaP approval; an open proteomics entry
does not authorize linked genomics access.

Store authorized data in institution-approved storage outside the checkout, with
access controls appropriate to the terms. Keep participant/aliquot overlap maps
there. Public reports should contain only reviewed aggregate counts, avoiding
small-cell disclosure. Never try to re-identify participants or link data beyond
the approved research purpose.

The [.gitignore](../.gitignore) reduces accidental tracking; it is not a security
boundary and cannot remove previously committed material. Review staged paths
and contents before every commit. If sensitive data are found, stop publication
and follow the responsible institution's incident process without reposting them
in a public issue.

## Rights and publication

No repository license exists yet. The owner must decide licensing before reuse
expectations are set; do not invent a grant or copy third-party code/data without
checking their terms. Link papers rather than redistributing full texts. Do not
present exploratory signatures as diagnostic tools, treatment selectors, or
evidence of improved survival. Obtain scientific review before such work advances
beyond this research scaffold.
