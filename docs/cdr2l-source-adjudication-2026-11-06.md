# CDR2L: original identification and source-context adjudication

Executed public-source research, 2026-11-06. This advances two existing ligand
leads; it does not establish an anti-Yo receptor, neural injury or patient relevance.

## What changed

The [earlier sequence audit](cdr2l-sequence-adjudication-2026-11-06.md) established
matches to named reference entries. A subsequent successful UniProt service
search, an official Atlas peptide-page inspection and an original deposited
cell-line identification inspection now narrow three specific uncertainties.

| Lead | New evidence | Still unresolved |
| --- | --- | --- |
| IEDB 11610866, Q86X02 residues 445–464 | Official Atlas page reports one cerebellum source-association row and displayed q-value 0.00189334; a processed spectrum representation is accessible in PCI-DB | Original acquisition lineage and independent identification validation; presenting allotype; source cell type |
| IEDB 18456218, Q86X02 residues 432–446 | Exact 15mer found once in the three original class-II mzIdentML result files from PXD023044, non-decoy Q86X02 at the expected coordinates; linked experimental peak list located and verified | Raw-spectrum validation, peptide-specific error probability and presenting allotype |
| Both sequences | UniProt human exact and I/L-equivalent searches return Q86X02 and A0ACI8RKQ2 only; every returned sequence is locally rechecked | Search completeness/synchronization and unrepresented sequences; biological specificity |

These are different peptides from different source systems. Their canonical
coordinate intervals intersect only at residues 445–446 (two residues). They
must not be combined into a replicated observation of one ligand, one receptor
specificity or a tumor-to-neuron pathway.

## Broader sequence search: completed, with bounded coverage

The [new certificate](../registries/cdr2l-database-search-2026-11-06.json) records
four successful human queries: each peptide with and without I/L equivalence,
including unreviewed entries. All four return only Q86X02 and A0ACI8RKQ2, both
annotated CDR2L. Direct sequence verification retains the coordinates from the
earlier audit; canonical CDR2 Q01850 has no match. UniProt REST reports 2026_04;
the peptide-search service does not expose a release. This is a verified
service-returned result, not a proof of exhaustive proteome uniqueness, sequence
coverage or synchronization. The historical failed-search certificate is unchanged.

## Atlas source: cerebellum association, not cell or allotype assignment

The official [exact-peptide page](https://hla-ligand-atlas.org/peptide/SRIQKTKADINATKVKTHSS)
links Q86X02 and IEDB 1281771. Its HLA-II table contains one source-association
row, tissue Cerebellum, displayed q-value 0.00189334. The page explicitly reports
no prediction-based binding evidence. That is neither a negative binding assay
nor evidence that the identification is false. The executable inspection retains
only aggregate tissue/count/quality metadata and source hashes, never donor IDs,
genotypes, linkage keys or full HTML. See the [certificate](../registries/cdr2l-atlas-source-2026-11-06.json).

The [original study](https://pmc.ncbi.nlm.nih.gov/articles/PMC8054196/) used a
combined Tü39/L243 HLA-II column. Source HLA genotypes are not peptide-specific
restriction measurements. The paper's local peptide-level 1% FDR and estimated
aggregate HLA-II 3.9% FDR are study-method quantities; neither independently
validates this peptide. The portal's displayed q-value aggregation remains
unresolved. Tissue association does not identify the presenting cell type.
Original deposition [PXD019643](https://www.ebi.ac.uk/pride/archive/projects/PXD019643)
also includes runs that failed study QC; no full study files were acquired here.

A targeted lookup located a [PCI-DB 2024 processed spectrum page](https://pci-db.org/psm_spectrum_info/3426396/?database=DB_release_240822_default)
for the same complete 20mer: scan 1888, charge 4, XCorr 2.195, displayed
q-value 0.000246609 and 14/114 matched/total ions. Its annotated spectrum image
was inspected transiently. The [2026 processed page](https://pci-db.org/psm_spectrum_info/2853502/?database=DB_release_260407_default)
reports the same sequence/scan/charge with XCorr 2.194 and q-value 0.00023.
These processed scores differ from the Atlas display and must remain separate.
Neither page supplies sufficient raw-file/PRIDE/USI linkage to establish the
original Atlas acquisition. This locates a spectrum representation, without
independent score computation, identification validation or biological
replication. PCI-DB's predicted best allele is not an experimental restriction.
The [PCI-DB paper](https://jitc.bmj.com/content/13/4/e011366) describes the resource;
its existence does not validate this individual record.

## Breast cell-line original identification

The [Goncalves study](https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2021.645770/full)
used combined DR/DP/DQ antibodies (LB3.1, B721 and SPV-L3). The correct
immunopeptidomics deposit is [PXD023044](https://www.ebi.ac.uk/pride/archive/projects/PXD023044),
not the separate tryptic-proteome deposit PXD023038. IEDB labels its sequence
source “Author Provided”; the numeric catalog name 84980 is not assumed to
crosswalk to a deposited peptide identifier.

A bounded streaming inspection of exactly three class-II result files found the
exact 15mer only in result file r3: peptide PEPTIDE_2890010, identification
SII_4292668_2890010, native spectrum locator `index=22949`, rank 1, charge 3,
`passThreshold=true`, non-decoy Q86X02 residues 432–446, no modifications.
The reported PEAKS score is 33.56. PSI-MS defines MS:1001950 as the PEAKS
−10lgP score; it is not a q-value. The deposited protocol says MS:1001494
“no threshold”; the flag cannot independently confirm the paper's 1% FDR.
The linked MGF basename places the acquisition in an IFN-positive MDA-MB-231
class-II sample. Result-file r3 and acquisition replicate 5 are distinct labels.
The identification pass read no RAW/MGF file and executed no third-party analysis
code. A subsequent bounded MGF inspection is described below; no RAW file or
search engine was used.

The [detailed source report](cdr2l-source-identification-2026-11-06.md) and
[identification certificate](../registries/cdr2l-source-identification-2026-11-06.json)
retain the exact original locators and score semantics.

All three served gzip streams matched their API SHA1 checksums; all three
expanded XML sizes matched API sizes and parsed to completion. These are
empirically different byte domains in this deposit. The replay records both
compressed and expanded sizes/digests and fails without a new artifact if any
file fails integrity. A match in an original identification output strengthens
source traceability; it does not independently reidentify the spectrum.

## Linked experimental peak list: locator resolved

The [executed spectrum-locator report](cdr2l-spectrum-locator-2026-11-06.md) and
[compact peak-list certificate](../registries/cdr2l-spectrum-locator-2026-11-06.json)
record a subsequent bounded inspection of the complete referenced MGF:
72,832,889 bytes, pinned SHA1 `56fd6906ed468329c56962eb24a5429373265a60`,
37,350 spectra. The source mzIdentML declares MS:1000774, whose official
[PSI-MS definition](https://www.ebi.ac.uk/ols4/api/ontologies/ms/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMS_1000774)
specifies zero-based spectrum indexing. Consequently `index=22949` selects the
22,950th spectrum without choosing an ordinal based on precursor agreement.

That spectrum's title is `index=22949`, its scan is 23848, charge is 3+, retention
time is 4337.466 seconds and precursor m/z is 614.999, exactly equal as a decimal
to the submitted identification's 614.9990. Only its 173 original experimental
peak entries and provenance are retained. This establishes the record-to-peak-list
link, not independent sequence identification. MGF is a deposited peak-list
representation; the original instrument RAW acquisition was not inspected.
No fragment score, peptide-specific FDR or synthetic-standard match was invented.

## The next discriminating result

The useful next question is **whether either exact peptide is securely identified
and naturally presented by a defined HLA allotype**. More catalog matches or an
unfitted simulation cannot answer that question.

1. For the breast lead, independently adjudicate the now-located experimental
   spectrum against the stated sequence and competing explanations. Preserve the
   original search settings and distinguish identification confidence from protein
   inference. For the Atlas lead, first establish original-file lineage for the
   processed representation; do not treat the two PCI-DB releases as replication.
2. Resolve the presenting allotype with evidence that distinguishes alleles in the
   mixed source preparations. Prediction can prioritize a test, but cannot supply
   the missing measurement. A defined-allotype binding result alone would still
   need natural-processing evidence to justify a presentation claim.
3. Only after these steps would a defined receptor's recognition and dependence
   on antigen/allotype justify connecting presentation to an immune mechanism.
   Injury requires separate evidence. No receptor or kinetic parameter has been
   measured here, so the Virtual Human evidence interface receives no invented
   scalar values.

This is a research decision sequence, not an executed experiment or a treatment
recommendation. No wet-lab access, new patient-study execution context or defined
receptor has been supplied. Pilot 001 and its dated owner-attestation gates are
unchanged. Public cell-line identification inspection does not attest a patient
analysis host or authorize use of private correspondence as data.

## Reproduce and assess

```sh
python3 tools/audit_cdr2l_sequences.py --output registries/cdr2l-database-search-2026-11-06.json
python3 tools/audit_cdr2l_atlas.py
python3 -m unittest tests.test_cdr2l_source_psm -v
python3 -m unittest tests.test_cdr2l_sequences tests.test_cdr2l_atlas -v
# New live output; preserve the historical receipts:
python3 tools/audit_cdr2l_sequences.py --live --search --output /tmp/cdr2l-new-search.json
python3 tools/audit_cdr2l_atlas.py --live --output /tmp/cdr2l-new-atlas.json
```

Offline checks establish artifact integrity and internal consistency, not the
truth of unretained source bytes. Live services and their annotations can change.
Credit belongs to the source-study authors, IEDB, UniProt, HLA Ligand Atlas,
PCI-DB and PRIDE; repository licensing does not replace their terms.
Prepared with GPT-6 Astra and independent internal Astra review; this is not
external scientific peer review.
