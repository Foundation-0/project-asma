# CDR2L breast-cell lead: an original identification record recovered

**Executed 2026-11-06.** The exact 15-residue peptide in IEDB assay 18456218 has a matching submitted identification in the original breast-cell immunopeptidomics deposit. This establishes a traceable identification-record link beyond catalog curation. It does not independently validate the spectrum, identify the presenting HLA allotype, or demonstrate receptor recognition or injury.

## Result and exact locator

The [aggregate certificate](../registries/cdr2l-source-identification-2026-11-06.json) records complete, hash-checked inspection of the three class-II mzIdentML result files in **PXD023044**. Exact target sequence `SQPEYKALFKEIFSR` was found in r3 only. No exact target declaration or identification was found in r1/r2. That bounded negative is not proof of biological absence or a detection-limit estimate.

| Field | Submitted value |
|---|---|
| Result file | `peptides_1_1_0_CII_r3.mzid.gz` |
| Peptide | `PEPTIDE_2890010`; no listed modifications |
| Identification item | `SII_4292668_2890010` |
| Identification result | `SPECGROUP_4292668` |
| Native spectrum identifier | `index=22949` |
| Source | `Q86X02`, residues 432–446, `isDecoy=false` |
| Rank / charge / passThreshold | `1` / `3` / `true` |
| Calculated / experimental m/z | `614.99646` / `614.9990` |
| Score | `MS:1001950`, `PEAKS:peptideScore`, `33.56` |
| SpectraData reference | `SPECTRADATA_1111` |

The exact referenced peak-list filename is:

```text
F1202000304_PF_MDAMB231_IFN-positive_replicate_5_pool_6_Immunopeptidomics-classII.mgf
```

`index=22949` is preserved as a native index, not renamed a scan number. The result-file label r3 and peak-list filename replicate_5 are not silently equated as experimental replicate numbering. Their document reference is verified; the naming convention remains unresolved. Source-directory prefixes are omitted, while their exact full-location string is hashed for replay.

The three files contain 74,510 / 46,724 / 77,131 identification items respectively. The retained exact target has one matching item in one result, not independent replication across all three files.

## What supports the catalog-to-source correspondence

[IEDB detailed assay 18456218](https://www.iedb.org/details_v3.php?id=18456218&type=assay) names epitope 1933672 as **Eluted Peptide 84980** and marks both epitope and assay data locations **Author Provided**. The detailed curator comment specifies combined LB3.1/DR, B721/DP and SPV-L3/DQ elution. The [query record](https://query-api.iedb.org/mhc_search?elution_id=eq.18456218&limit=1) has class-level restriction and parent Q86X02.2 at 432–446.

The submitted mzIdentML independently supplies the same exact sequence, protein accession and coordinates. That supports correspondence by those fields. It does **not** prove that IEDB's author identifier 84980 directly cross-references the mzIdentML item identifier; no such numeric crosswalk was established.

## Score and filtering limits

The [PSI-MS term MS:1001950](https://www.ebi.ac.uk/ols4/api/ontologies/ms/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMS_1001950) defines the score type as PEAKS -10lgP. It is not a q-value or posterior probability of a correct identification. [PEAKS' scoring documentation](https://www.bioinfor.com/dbscoring-tutorial/) separately discusses selection of a score cutoff using dataset FDR.

All three exported protocols carry [MS:1001494](https://www.ebi.ac.uk/ols4/api/ontologies/ms/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMS_1001494), `no threshold`. Therefore the target's `passThreshold=true` cannot recover a numeric FDR cutoff. The article's stated 1% FDR procedure and the export's missing threshold specification are retained separately. This does not establish that filtering was absent, and no FDR was recomputed.

## Original experimental context

Goncalves et al., PMID 33968037, DOI 10.3389/fimmu.2021.645770 used IFNγ-treated MDA-MB-231 cells (50 IU, 48 h), combined DR/DP/DQ immunoaffinity isolation, and PEAKS X identification. The typing table provides DR 07:01/13:05, DP 02:01/17:01 and DQ 02:02/03:01. Sample typing does not assign this peptide; the table does not resolve alpha-chain pairings. The NetMHCpan 4 figures concern class-I peptides. Methods mention both Orbitrap Fusion and QExactive Plus in different sections; this inspection does not settle peptide-specific acquisition instrument identity.

Locators: [original article](https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2021.645770/full), Cell Culture; HLA Typing; Immunopeptidomics Sample Preparation; HLA Peptide Identification; Figure 1D; Supplementary Figure 4. The [EuropePMC XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8100505/fullTextXML) maps supplementary figures to Presentation_1.pptx and a cancer-antigen table to Table_1.xlsx. Binary supplements were not inspected in this pass, and are not claimed to supply or lack a peptide-specific spectrum row.

## Input identity, byte domains and completeness

[PRIDE project metadata](https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD023044) identifies the immunopeptidomics deposit as COMPLETE and gives CC0 license metadata. PXD023038 instead describes tryptic whole-proteome DDA/DIA and is PARTIAL; it is not the identification source used here. Credit belongs to Goncalves and colleagues and PRIDE. Public availability is not scientific validation.

File inventory pages 0/1/2 of the [files API](https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD023044/files?pageSize=100&page=0) returned 100/79/0 rows, 179 unique accessions (85 RAW, 84 PEAK, 9 RESULT, 1 design). The three selected class-II result files are pinned by API checksum and size in the original inspection tool. No RAW/MGF body was retrieved during that initial identification-record inspection. The subsequent bounded MGF locator check is documented in [the spectrum followup](cdr2l-spectrum-locator-2026-11-06.md).

A source-identity assumption initially failed: API `fileSizeBytes` describes expanded XML, while its 40-hex checksum matches the served gzip's SHA1. For r1 the HTTP gzip length is 6,103,692, while expanded XML has 85,957,996 bytes. The workflow first rejected this mismatch, then adopted an explicit tested mixed-domain contract after measuring both representations. This is observed behavior on these files, not a claim about documented API semantics. **Each of the three files independently matches both original pins**, plus HTTP Content-Length for the served body. The certificate records both representations' sizes, SHA1, SHA256, HTTP metadata and the initially rejected assumption.

The final run read 15,907,955 gzip bytes and 226,809,010 expanded bytes under caps of 90 MB per compressed file, 230 MB total compressed and 2 GB total expanded. Gzip trailers and the complete XML document must verify before output. A failure in any file prevents a partial scientific artifact. Nonmatching content is discarded in memory; only compact target records, aggregate counts and provenance are retained.

## Accessibility and discriminating next step

The referenced MGF is present in the project file inventory as PEAK, size 72,832,889 bytes, API checksum `56fd6906ed468329c56962eb24a5429373265a60`. A **initial HEAD-only** request on 2026-11-06 returned HTTP 200, Content-Length 72,832,889 and Accept-Ranges bytes at the [exact peak-list locator](https://ftp.pride.ebi.ac.uk/pride/data/archive/2021/05/PXD023044/F1202000304_PF_MDAMB231_IFN-positive_replicate_5_pool_6_Immunopeptidomics-classII.mgf). Its body and checksum were not acquired during the initial identification-record inspection; the subsequent [spectrum followup](cdr2l-spectrum-locator-2026-11-06.md) records the separately authorized retrieval. A subsequent attempt to resolve the same-basename RAW inventory record timed out; RAW accessibility remains unverified. Endpoint accessibility is not evidence of spectral quality.

The next discriminating action is a separately bounded inspection of that native-index identification's experimental spectrum and its match to the unmodified 15mer: first establish index-to-spectrum mapping, then assess supporting fragment ions, competing sequences and calibration. A synthetic-peptide reference could later provide an independent spectral comparison. No such analysis or experiment ran here. Even convincing sequence identification would leave allotype assignment and defined-receptor recognition as separate questions; neither follows from the source's multiallelic antibody mixture. Receptor/presenter work requires its own protocol, rather than promoting this cell-line record into anti-Yo or neural-injury evidence.

## Reproduce and limits of checks

```sh
python3 -m unittest discover -s tests -p test_cdr2l_source_psm.py -v
# Explicit bounded live inspection; output must be a NEW file:
python3 tools/audit_cdr2l_source_psm.py --live --output /tmp/cdr2l-source-new.json
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

On the isolated source branch based on main `9931c1f`, all **376 local tests** passed, including 14 new source-inspection cases; the repository validator passed. The original standard-library parser does not execute downloaded code. Synthetic tests cover wrong hashes/sizes, both byte domains, truncation, caps, DTD rejection, reference mismatches, retained false/decoy states, late failure and omission of source-directory prefixes. Tests check software, not spectrum accuracy. No search engine, training or model fitting ran. The certificate's timestamps, runtime and implementation hash identify the executed inspection; source bytes are not retained.

Notice checks on 2026-11-06: EuropePMC core metadata for PMID 33968037 had no commentCorrectionList, and exact-DOI correction/retraction/corrigendum searches restricted to publisher/PubMed located no notice. This is bounded checking, not proof of absence. [ProteomeXchange history](https://proteomecentral.proteomexchange.org/cgi/GetDataset?ID=PXD023044) records a 2023-11-14 metadata update, distinct from a paper correction.

Prepared by gpt-forge with GPT-6 Astra. Internal software/source review is distinct from external scientific review. Pilot 001 remains unchanged.

The parser correction retains `SubstitutionModification` as well as `Modification`, and preserves source `SpectrumIDFormat`/`FileFormat` terms. A complete three-file replay verified the same source pins, target count and empty modification list with the corrected parser. Its certificate contains the updated implementation hash.
