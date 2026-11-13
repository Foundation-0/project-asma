# A public evidence atlas for CDR2 and CDR2L

**Retrieved 2026-11-13.** This note assembles public records about human CDR2 and CDR2L that are relevant to anti-Yo paraneoplastic cerebellar degeneration, including its association with gynecologic tumours. It is a research record. It is not a diagnostic method, a prognostic tool, or treatment advice.

The question is narrow: which public identifiers, HLA class-II mass-spectrometry annotations, expression summaries, and primary papers can be tied to these two proteins, and what do those records actually count? Detecting a protein, eluting a peptide, and showing that an antibody or T cell recognises it are different observations. An association in a case series is not a demonstration that the protein caused the injury.

This run repeats the IEDB procedure recorded on 2026-11-05 and adds UniProt identity, Human Protein Atlas summaries, and cited study counts. It continues the [antigen audit](antigen-discovery-round2-2026-11-05.md), the [HLA-II evidence map](cdr2-hla-ii-evidence-map-2026-11-06.md), and the CDR2L source adjudication in [the 2026-11-06 source note](cdr2l-source-adjudication-2026-11-06.md). Claim labels are in [CLAIMS.md](../CLAIMS.md).

Prepared with AI assistance (Cursor cloud agent, Grok 4.7) under human direction. The checks below are internal and are not external scientific review.

## How the records were retrieved

IEDB, on 2026-11-13, using the same procedure as the 2026-11-05 audit ([S110](../registries/sources.json), [S139](../registries/sources.json)):

1. `antigen_search` with `parent_source_antigen_iri=eq.UNIPROT:Q01850` or `UNIPROT:Q86X02`, `select=elution_ids`, `limit=1`.
2. A parent-card query for the same IRI, `select=parent_source_antigen_id,parent_source_antigen_iri,elution_ids`, `limit=2`, and request header `Prefer: count=exact`.
3. `mhc_search` on those elution ids in batches of at most 50, with `mhc_class=eq.II`, `limit=50`, and the same selected fields as in 2026-11-05: `elution_id`, `reference_id`, `pubmed_id`, `reference_titles`, `mhc_class`, `mhc_allele_name`, `mhc_allele_evidence`, `assay_names`, `qualitative_measure`.

The seven CDR2 parent ids present on this date and absent from the 2026-11-05 id list were queried once more, without an MHC-class filter, selecting only class, allele name, assay name, qualitative measure, and PubMed id ([S140](../registries/sources.json)). No peptide sequences were requested.

UniProt REST entries `Q01850.json` and `Q86X02.json` were saved as retrieved ([S136](../registries/sources.json), [S137](../registries/sources.json)). Human Protein Atlas version 26.0 files were downloaded and reduced to the two genes, or saved whole when the file was only a tissue or cancer legend ([S141](../registries/sources.json)–[S148](../registries/sources.json)). Literature rows use Europe PMC core records for named PMIDs. Abstracts were read. Full texts were not re-reviewed for this note. Exact URLs, the observed `Content-Range` where the API sent one, and SHA-256 values are in [manifest.json](../results/cdr2-cdr2l-evidence-atlas-2026-11-13/manifest.json).

Two checkers re-read the pinned bytes offline. One reads export fields and assigns each class-II row to the parent named on its batch. The other parses the raw JSON with a separate reader and assigns the parent by which antigen-search id list contains the assay id. `verify.py` fails if those results differ or if a pinned file hash changes. `--live` re-fetches and does not write snapshot files.

## Protein identity

Both accessions are reviewed Swiss-Prot entries for *Homo sapiens* (taxon 9606), with protein-level existence recorded by UniProt.

| Accession | Gene | Recommended name | Length | Ensembl gene | NCBI Gene | HGNC | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q01850 | CDR2 | Cerebellar degeneration-related protein 2 | 454 | ENSG00000140743.9 | 1039 | HGNC:1799 | [S136](../registries/sources.json) |
| Q86X02 | CDR2L | Cerebellar degeneration-related protein 2-like | 465 | ENSG00000109089.8 | 30850 | HGNC:29999 | [S137](../registries/sources.json) |

UniProt states that copyrightable database content is available under CC BY 4.0 ([S138](../registries/sources.json)). These are reference records, not evidence that either protein is the receptor target in a particular person.

## HLA class-II assay annotations

The repeated procedure returned **7** class-II rows for Q01850 and **2** for Q86X02. Each row is a positive `ligand presentation|cellular MHC/mass spectrometry` annotation. The assay-id set is the same set recorded on 2026-11-05. These are curated assay rows, not patients, not unique peptides, and not receptor assays.

| Parent | Assay | PMID | Reference | Allele field | Allele evidence | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Q01850 | 11480011 | 33858848 | 1036766 | human | Allele/Locus-specific Antibody | [S111](../registries/sources.json), [S139](../registries/sources.json) |
| Q01850 | 16293090 | 34357683 | 1039356 | HLA-DP | Allele/Locus-specific Antibody | [S117](../registries/sources.json), [S139](../registries/sources.json) |
| Q01850 | 16293091 | 34357683 | 1039356 | HLA-DP | Allele/Locus-specific Antibody | [S117](../registries/sources.json), [S139](../registries/sources.json) |
| Q01850 | 16293092 | 34357683 | 1039356 | HLA-DP | Allele/Locus-specific Antibody | [S117](../registries/sources.json), [S139](../registries/sources.json) |
| Q01850 | 16543635 | 33592498 | 1039604 | HLA-DRB1*03:01 | Inferred by motif or alleles present | [S113](../registries/sources.json), [S139](../registries/sources.json) |
| Q01850 | 16553502 | 33592498 | 1039604 | HLA-DRB1*01:02 | Inferred by motif or alleles present | [S113](../registries/sources.json), [S139](../registries/sources.json) |
| Q01850 | 16559485 | 33592498 | 1039604 | HLA-DRB1*01:02 | Inferred by motif or alleles present | [S113](../registries/sources.json), [S139](../registries/sources.json) |
| Q86X02 | 11610866 | 33858848 | 1036766 | human | Allele/Locus-specific Antibody | [S111](../registries/sources.json), [S139](../registries/sources.json) |
| Q86X02 | 18456218 | 33968037 | 1040330 | human | Allele/Locus-specific Antibody | [S112](../registries/sources.json), [S139](../registries/sources.json) |

Q01850 has 3 reference ids. Q86X02 has 2. The parent-card responses each contained one record and `Content-Range: 0-0/1`.

The parent elution-id list is now **383** for Q01850 and still **45** for Q86X02. On 2026-11-05 those lists were 376 and 45. The seven added Q01850 ids (31042323, 31042324, 31042325, 31042326, 31048994, 31083521, 31100939) are MHC **class I** rows, all PMID [42653321](https://pubmed.ncbi.nlm.nih.gov/42653321/), allele field `human`. That paper is a psoriatic-arthritis MHC class-I immunopeptidome study ([S157](../registries/sources.json)). It does not add a class-II anti-Yo annotation. The CDR2L antigen-search body, parent card, and class-II response are byte-identical to the 2026-11-05 hashes. The CDR2 antigen-search body is not. The multiset of CDR2 class-II batch-response hashes still matches 2026-11-05, because the class-II rows themselves did not change. Reproducing a known set of nine annotations is not a new biological result.

## Expression summaries

Human Protein Atlas version 26.0, Ensembl 109, describes consensus nTPM as the maximum of the HPA and GTEx nTPM values for that gene and tissue, not a mean and not a between-group effect ([S142](../registries/sources.json)). The consensus file has 51 tissue rows for each gene and does not include a donor or sample count. No sample size is stated here for nTPM. CDR2L is labelled tissue enhanced, with the maximum in cerebellum. CDR2 is labelled low tissue specificity, detected in all consensus tissues, with the maximum in retina rather than cerebellum. CDR2 normal-tissue IHC reliability in the gene summary is Uncertain. CDR2L IHC reliability is Approved ([S148](../registries/sources.json)).

| Gene | Cerebellum nTPM | Ovary nTPM | Fallopian tube | Breast | Endometrium | Maximum |
| --- | --- | --- | --- | --- | --- | --- |
| CDR2 | 16.1 | 13.9 | 15.4 | 14.1 | 17.5 | retina 69.5 |
| CDR2L | 58.8 | 2.9 | 6.6 | 7.6 | 11.4 | cerebellum 58.8 |

Normal-tissue IHC in the pinned extract, which has no patient count:

| Gene | Tissue and cell type | Level | Reliability |
| --- | --- | --- | --- |
| CDR2 | Cerebellum, Purkinje cells | Medium | Uncertain |
| CDR2 | Ovary, follicle cells and ovarian stroma | Medium | Uncertain |
| CDR2L | Cerebellum, Purkinje cells | High | Approved |
| CDR2L | Ovary, ovarian stroma | Low | Approved |

Cancer IHC columns are numbers of patients in staining bins on tissue microarrays ([S143](../registries/sources.json), [S145](../registries/sources.json)). They are not anti-Yo status, and they have no comparison group in this file, so they are not an effect size.

| Gene | Cancer | Patients | High | Medium | Low | Not detected |
| --- | --- | --- | --- | --- | --- | --- |
| CDR2 | Ovarian | 12 | 8 | 4 | 0 | 0 |
| CDR2 | Breast | 12 | 7 | 5 | 0 | 0 |
| CDR2 | Endometrial | 12 | 8 | 2 | 1 | 1 |
| CDR2 | Cervical | 12 | 8 | 4 | 0 | 0 |
| CDR2L | Ovarian | 12 | 6 | 5 | 1 | 0 |
| CDR2L | Breast | 11 | 1 | 8 | 2 | 0 |
| CDR2L | Endometrial | 12 | 9 | 1 | 1 | 1 |
| CDR2L | Cervical | 12 | 5 | 6 | 1 | 0 |

The TCGA legend in the same Atlas release lists cohort sizes for the RNA resource: ovary serous cystadenocarcinoma **349**, breast invasive carcinoma **1022**, cervical squamous cell carcinoma and endocervical adenocarcinoma **283**, and uterine corpus endometrial carcinoma **176** ([S147](../registries/sources.json)). Those are denominators of the resource. This atlas did not keep per-sample RNA rows or sample identifiers, and it does not report a per-gene cancer RNA effect.

The HPA position string for CDR2L is chromosome 17, 74987632-75005800. That uses the same integers as the NCBI Gene span already recorded as [K37](../CLAIMS.md). CDR2 is given as chromosome 16, 22345936-22437165. HPA's own licence for copyrightable parts is CC BY 4.0, with separate terms for included resources such as GTEx and TCGA ([S141](../registries/sources.json)).

## Primary literature counts

These sentences are what the retrieved abstracts state. Where an abstract interprets causation or recommends care, that sentence is the authors' and is not adopted here.

| Paper | What the abstract counts | What it does not establish | Source |
| --- | --- | --- | --- |
| Peterson et al. 1992, PMID 1407575, DOI 10.1212/wnl.42.10.1931 | 55 women with anti-Yo cerebellar degeneration, ages 26–85. 52 of 55 had a malignancy, almost exclusively breast or gynecologic. In 34 of 52 the neurologic syndrome preceded the cancer diagnosis. 37 of 48 assessable patients could not walk or sit unassisted. | A case series. No effect size against an unaffected comparison group. The abstract's management sentence is not used here. | [S149](../registries/sources.json) |
| Corradi et al. 1997, PMID 9006982, PMC6793730 | In the mouse, cdr2 mRNA was widespread and the protein was reported in brain and testis. The abstract identifies cdr2 as the PCD tumour antigen among the cdr genes they compared. | A mouse distribution. Not the human HPA staining table, and not a patient denominator. | [S150](../registries/sources.json) |
| Darnell, Albert and Darnell 2000, PMID 10786675 | The abstract says cdr2 is widely expressed in breast and ovarian tumours from neurologically normal patients, revising earlier reports of absence. | The retrieved abstract gives no sample size and no effect size. "Tumour suppression" in the abstract is the authors' interpretation. | [S151](../registries/sources.json) |
| Eichler et al. 2013, PMID 23823982, PMC3688866 | 42 Yo sera: 36 had both CDR2 and CDR2L antibodies and 6 had CDR2 only. 5 of 179 ovarian-cancer sera without PNS had CDR2L antibodies. 4 of 114 breast-cancer sera without PNS had CDR2 or CDR2L antibodies. 0 of 100 blood donors had Yo antibodies. The abstract says only patients with both antibodies had PCD. | Proportions in the tested sera. The pathogenic ranking of CDR2L is the authors' interpretation. | [S152](../registries/sources.json) |
| Schubert et al. 2014, PMID 25341622, PMC4231287 | Organotypic cerebellar slice cultures internalised patient or rabbit CDR antibodies, with changes in calbindin staining, dendritic arbors, and calcium-pathway proteins. | A culture model. No patient sample size. The abstract's sentence about neuroprotective drugs is not adopted. | [S153](../registries/sources.json) |
| Raspotnig et al. 2017, PMID 28710511, PMC11028591 | Ovarian-cancer tissue from 16 patients (4 anti-Yo with PCD, 2 anti-Yo without PCD, 5 with only CDR2L antibodies, 5 without onconeural antibodies). All 16 expressed CDR2 and CDR2L. | A selected series of 16. Presence in antibody-negative tumours means expression alone did not mark antibody status here. No odds ratio is reported. | [S154](../registries/sources.json) |
| Kråkenes et al. 2019, PMID 31148214, DOI 10.1002/ana.25511 | Yo antibodies bound endogenous CDR2L and not endogenous CDR2, while they could bind recombinant CDR2 used in routine testing. The authors conclude CDR2L is the major Yo antigen. | The abstract does not give a patient denominator. | [S155](../registries/sources.json) |
| Herdlevær et al. 2020, PMID 33009713, PMC7664253 | Yo antibodies were CDR2L-specific by mass spectrometry in their experiments. CDR2L was cytoplasmic and CDR2 nuclear in the systems they stained. | Localisation in the stated preparations. Not a population rate. | [S156](../registries/sources.json) |

## Machine-checkable counts

<!-- BEGIN CDR2 ATLAS COUNTS -->
CDR2 Q01850 class-II assays: 7
CDR2L Q86X02 class-II assays: 2
CDR2 class-II references: 3
CDR2L class-II references: 2
CDR2 parent elution IDs: 383
CDR2L parent elution IDs: 45
CDR2 parent IDs added since 2026-11-05: 7
CDR2L parent IDs added since 2026-11-05: 0
class-II assay IDs unchanged since 2026-11-05: True
CDR2L antigen, parent-card and class-II bytes match 2026-11-05: True
CDR2 antigen bytes match 2026-11-05: False
CDR2 class-II response hash multiset matches 2026-11-05: True
class-I delta rows: 7
class-I delta pubmed: 42653321
CDR2 amino acids: 454
CDR2L amino acids: 465
CDR2 GeneID: 1039
CDR2 HGNC: HGNC:1799
CDR2L GeneID: 30850
CDR2L HGNC: HGNC:29999
CDR2 cerebellum nTPM: 16.1
CDR2 ovary nTPM: 13.9
CDR2L cerebellum nTPM: 58.8
CDR2L ovary nTPM: 2.9
CDR2 consensus max: retina 69.5
CDR2L consensus max: cerebellum 58.8
CDR2 ovarian cancer IHC patients: 12 high 8 medium 4 low 0 not_detected 0
CDR2L ovarian cancer IHC patients: 12 high 6 medium 5 low 1 not_detected 0
TCGA ovary serous cystadenocarcinoma samples: 349
<!-- END CDR2 ATLAS COUNTS -->

```sh
python3 results/cdr2-cdr2l-evidence-atlas-2026-11-13/verify.py
```

Optional live comparison, which will not replace committed bytes:

```sh
python3 results/cdr2-cdr2l-evidence-atlas-2026-11-13/verify.py --live
```

## Limits

The offline check shows that two readers of these pinned files produce the same table and that the files still have their recorded hashes. It does not show that IEDB, UniProt, or the Human Protein Atlas are complete, current, or correct against the underlying spectra and donors. It does not re-identify peptides, assign a presenting HLA allotype, or test a T-cell or antibody receptor.

A class-II elution row does not show anti-Yo recognition. Consensus nTPM and cancer IHC do not show that expression caused cerebellar injury. Peterson's series shows how often cancer was found in that antibody-defined group; it does not estimate risk in people with ovarian cancer. Raspotnig's 16 tumours show that both proteins can be present with and without the antibodies they tested. No odds ratio was calculated here, because the abstracts that lack a comparison group do not support one.

Nothing in this note should be read as a way to diagnose anti-Yo disease, to interpret a blot, or to choose a treatment.

## Credit

Assay metadata are from the Immune Epitope Database. Protein entries are from UniProt. Expression tables are from the Human Protein Atlas version 26.0, which incorporates other resources under their own terms. The counts in the literature table are the authors' published abstracts. The 2026-11-05 parent audit and the 2026-11-06 evidence map and CDR2L source checks are earlier work in this repository; this note re-derives the class-II count and does not replace those source-level spectrum checks.
