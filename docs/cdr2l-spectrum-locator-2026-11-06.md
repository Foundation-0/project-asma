# CDR2L source identification reaches its experimental peak list

**Executed 2026-11-06.** The original submitted CDR2L identification now has a verified experimental-spectrum locator: **MGF index 22949, scan 23848**, with the same precursor m/z and charge as its mzIdentML item. This closes the catalog → submitted identification → deposited experimental peak-list link. It does not independently establish the peptide sequence, calibrate its identification confidence, or assign an HLA allotype.

The [compact spectrum certificate](../registries/cdr2l-spectrum-locator-2026-11-06.json) retains only the selected spectrum's metadata and 173 original decimal-string peak pairs, together with complete-file hashes and provenance. The full 72.8 MB MGF was streamed in memory and discarded. No RAW file was acquired, no search engine was run, and no spectra were rescored.

## Selection was determined before precursor comparison

The corrected [identification parser](../tools/audit_cdr2l_source_psm.py) preserves the actual source `SpectrumIDFormat` and `FileFormat` CV parameters. Its complete three-file replay verified the same checksum/size pins and unchanged single target record. Source `SPECTRADATA_1111` declares **MS:1000774**, multiple peak list nativeID format, and **MS:1001062**, Mascot MGF file.

The official [PSI-MS term served by EBI OLS](https://www.ebi.ac.uk/ols4/api/ontologies/ms/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMS_1000774) defines the index as the spectrum number starting from zero. Therefore `index=22949` selects the **22,950th** `BEGIN IONS` block. This rule was established before retrieval; no neighboring spectrum was chosen because its precursor looked suitable. [Matrix Science's MGF specification](https://www.matrixscience.com/help/data_file_help.html) defines those block delimiters and the precursor, charge, scan and peak-list fields.

| Field | Exact selected source value |
|---|---|
| TITLE | `index=22949` |
| SCANS | `23848` |
| PEPMASS | `614.999` |
| CHARGE | `3+` |
| RTINSECONDS | `4337.466` |
| Experimental peaks | 173 |
| Source text lines, one-based | 2,817,977–2,818,156 |
| Complete MGF spectrum blocks | 37,350 |

The submitted identification `SII_4292668_2890010` records experimental m/z `614.9990` and charge `3`. Decimal comparison gives exactly zero difference and matching charge. Its calculated m/z remains `614.99646`; we do not reinterpret that difference as a confidence score. The MGF `SCANS` field, rather than the zero-based index, supplies scan 23848. The peak list is deposited experimental data; it is not raw instrument data or independent replication of the experiment.

## Complete-file identity and bounded retention

The exact [PRIDE peak-list URL](https://ftp.pride.ebi.ac.uk/pride/data/archive/2021/05/PXD023044/F1202000304_PF_MDAMB231_IFN-positive_replicate_5_pool_6_Immunopeptidomics-classII.mgf) belongs to public cell-line project [PXD023044](https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD023044), whose metadata declares CC0. Its [file inventory](https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD023044/files?pageSize=100&page=0) supplies the size and checksum pins. This followup was explicitly scoped to this one PEAK file, not participant data or RAW files.

- Served and API size: **72,832,889 bytes**, below the 90,000,000-byte cap.
- Complete served SHA1 matches the API pin: `56fd6906ed468329c56962eb24a5429373265a60`.
- Complete served SHA256: `19221e28bf764c2a1030ccafb1531150982e863f71ad6525b71215bd94c2f974`.
- HTTP Content-Length also matches; the certificate records ETag and Last-Modified.

Unlike the earlier gzip/XML mixed-domain observation, this uncompressed MGF size and checksum both describe the same served bytes. The tool requires complete block closure, EOF, pinned byte count and SHA1 before writing a certificate. It caps individual lines and selected peaks, preserves decimal source strings, and refuses missing or ambiguous locator-format information. It is a bounded locator inspector, not a general MGF validator. Nonselected peak bodies are discarded as they arrive. The identification certificate and implementation are SHA256-linked in the result. Before selecting a spectrum, the tool requires the certificate's exact project, assay, target, three source-file identities, original checksum/size pins and byte domains, complete XML, unique unmodified peptide declaration and identification reference. This checks consistency against pinned provenance; the source certificate is a replayable local result, not a signed external attestation.

## What remains discriminating

The next spectral question is whether the observed fragments discriminate `SQPEYKALFKEIFSR` from credible alternative assignments under documented acquisition and search settings. That requires a separately specified spectral adjudication with explicit ion/mass rules, tolerances and alternatives; a calibrated synthetic-peptide reference would add an independent comparison. We have deliberately produced no fragment match fraction, new score, q-value or sequence-validation claim from this locator check. The source's PEAKS score 33.56 and `passThreshold=true` retain the limitations described in the [identification report](cdr2l-source-identification-2026-11-06.md).

Even successful sequence confirmation would not resolve which DR/DP/DQ molecule presented the peptide, defined receptor recognition, or anti-Yo neural injury. The source is an IFNγ-treated multiallelic breast cell line with combined class-II capture. Those biological distinctions remain separate experimental questions.

## Reproduce

```sh
python3 -m unittest discover -s tests -p 'test_cdr2l_*.py'
# First create a fresh identification certificate with the corrected source parser:
python3 tools/audit_cdr2l_source_psm.py --live --output /tmp/cdr2l-source-new.json
# Explicit second retrieval; outputs must be new paths:
python3 tools/audit_cdr2l_spectrum_locator.py --live \
  --identification-certificate /tmp/cdr2l-source-new.json \
  --output /tmp/cdr2l-spectrum-new.json
python3 -m unittest discover -s tests
python3 tools/validate.py
```

All **384 local tests** passed on the isolated source branch, including 16 identification-parser tests and six spectrum-locator tests. The repository validator passed. Synthetic cases cover zero-based selection, exact decimal preservation, bad pins, late truncation, malformed blocks, limits, absent indices, duplicate metadata and refusal when source index-format evidence is missing. Ten certificate mutation probes additionally reject wrong project/assay/target, missing files, changed source pins, wrong spectrum identifier or peptide reference, and a modified target. These establish software behavior; they do not validate biological or spectral correctness. Independent Astra review is recorded separately at the exact commit.

Prepared by gpt-forge with GPT-6 Astra.
