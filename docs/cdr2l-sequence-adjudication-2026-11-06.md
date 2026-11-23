# Two CDR2L ligand leads: a named-sequence adjudication

**Executed 2026-11-06. VERIFIED: bounded public-catalog computation, not a
biological or clinical result.** This resolves part of the next desk step in the
[HLA-II evidence map](cdr2-hla-ii-evidence-map-2026-11-06.md): whether the two
curated CDR2L peptide leads match the reported CDR2L sequence and the explicitly
checked CDR2 comparator. It does not adjudicate spectra, peptide–HLA allotype,
receptor recognition, or injury.

## Result

Both IEDB peptide sequences occur at their reported coordinates in canonical
human CDR2L **Q86X02**, and neither occurs in the directly checked canonical human
CDR2 **Q01850**. Treating isoleucine and leucine as equivalent gives the same
matches in this finite comparison. Both also occur in an unreviewed human entry
annotated **CDR2L**, **A0ACI8RKQ2**. Two entries with the same gene annotation are
not independent biological confirmations or evidence for two distinct antigens.

Positions are one-based, inclusive. Only lengths, positions and sequence hashes
are retained; full sequences remain in memory.

| IEDB assay / epitope | Length | Q86X02 CDR2L | Q01850 CDR2 | A0ACI8RKQ2, unreviewed CDR2L |
|---|---:|---|---|---|
| [11610866](https://www.iedb.org/assay/11610866) / 1281771 | 20 | 445–464 | No exact or I/L-equivalent match | 436–455 |
| [18456218](https://www.iedb.org/assay/18456218) / 1933672 | 15 | 432–446 | No exact or I/L-equivalent match | 423–437 |

The first source is the benign-tissue HLA Ligand Atlas (PMID 33858848); the second
is the IFNγ-treated breast-cancer-cell study (PMID 33968037). Their original
experimental contexts and caveats remain those in the
[source map](cdr2-hla-ii-evidence-map-2026-11-06.md). Both current IEDB rows retain
**class-level** HLA-II restriction, with allele name `human` and antibody-based
class evidence. A list of alleles present in a source sample would not assign
this peptide to one allotype.

**Interpretation:** these two catalog leads are sequence-compatible with CDR2L
and distinguishable from the one checked CDR2 reference sequence. The audit does
**not** establish uniqueness across all human proteins, isoforms, variants,
modified or spliced peptides. It also does not validate the original atlas's
multi-protein annotation, spectral identification, or the actual protein source
in either experiment. No probability of the direct-ligand hypothesis is assigned.

## What ran and what failed

The successful replay retrieved only the two selected IEDB catalog records and
three named human UniProt entries. Its
[aggregate certificate](../registries/cdr2l-sequence-audit-2026-11-06.json) records
the retrieval time, UniProt REST release **2026_04**, entry and sequence versions,
peptide/protein sequence SHA-256 values, positions, and implementation hash.
The IEDB source coordinates and PMIDs are checked against the existing map;
matching uses independent local substring enumeration, including all overlapping
matches and an explicit I/L-equivalent comparison.

Candidate selection was **exploratory**, not a preregistered discovery study.
Q86X02 and Q01850 came from the existing source map. A preliminary UniProt
peptide-search response nominated A0ACI8RKQ2; its current identity and matches
were then checked directly. The three-candidate set was fixed for the recorded
replay. Broader search attempts encountered timeouts, connection errors and
HTTP 503. Therefore the certificate explicitly records database search
`not_run`; it contains no inferred exhaustive search result. This retained
result is the named-candidate comparison, not successful completion of the
initial broader search plan.

The optional remote-search path submits each public peptide separately, checks
the server's returned query parameters, rechecks every returned protein locally,
and refuses inconsistent exact-versus-I/L match sets. It fails without writing a
new report if the service is unavailable. Even a successful remote run cannot
independently establish database completeness or synchronization. Newly returned
isoform identifiers stop for separate adjudication instead of guessing their
sequences.

## Reproduce

```sh
# Offline certificate and internal-consistency checks; no network:
python3 tools/audit_cdr2l_sequences.py
python3 -m unittest tests.test_cdr2l_sequences -v

# Named-candidate live replay, saving a NEW dated result rather than replacing history:
python3 tools/audit_cdr2l_sequences.py --live --output /tmp/cdr2l-replay.json

# Optional whole-service lookup; explicitly separate from the recorded result:
python3 tools/audit_cdr2l_sequences.py --live --search --output /tmp/cdr2l-search.json
```

Offline validation detects changed certificates, implementation drift, wrong
source identities, missing comparators, invalid coordinates and impossible
I/L-versus-exact relations. It does **not** authenticate source truth or recreate
unretained sequence bytes. Live data can change; compare versions and hashes and
record a new dated finding rather than silently updating the old one.

## Source use and next decision

This was a bounded reference-sequence/catalog audit. No study matrix, spectrum
file, patient record, receptor sequence, fitted model or third-party analysis
code was acquired or executed. No author was contacted. IEDB's
[data-use account](https://discuss.iedb.org/t/iedb-coretrustseal-approved-application/205)
describes public reuse and attribution; UniProt's
[license](https://www.uniprot.org/help/license) applies CC BY 4.0 to copyrightable
database content. Credit belongs to IEDB, the source-study authors and UniProt.
The [UniProt peptide-search documentation](https://peptidesearch.uniprot.org/)
specifies exact peptide queries, taxonomy restriction and the I/L option.
Only compact derived metadata are retained here; repository licensing does not
replace third-party terms.

**Next research action:** prioritize the original identification evidence and
allotype assignment for these two leads, preserving their different source
systems. This result makes a simple canonical-CDR2 substitution an unsupported
explanation for these particular sequences; it does not rank their biological
relevance or bypass the need for natural-processing and defined-receptor evidence.
Any new study-data/spectrum analysis or functional experiment needs its own
bounded protocol and applicable execution gates. Pilot 001 is unchanged.

Prepared with GPT-6 Astra and independent internal Astra review. Internal review
is not external scientific review.

## Subsequent source adjudication

A [later executed follow-up](cdr2l-source-adjudication-2026-11-06.md) completed
the broader sequence-service searches and inspected original source evidence.
This earlier report and its named-candidate certificate remain a historical
record of the narrower run, including its unavailable broad search.
