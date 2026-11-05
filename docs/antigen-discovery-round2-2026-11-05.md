# Antigen discovery, round 2: recover ligands before inventing targets

**2026-11-05 · public-source review and curated-metadata audit.** No new
biological mechanism demonstrated. This follow-up to the
[first frontier exploration](anti-yo-frontier-2026-11-04.md) finds a concrete
lead missed by the earlier keyword searches and develops a second, untested
explanation for antibody/T-cell antigen mismatch. Labels follow
[CLAIMS.md](../CLAIMS.md).

## Result that changes the next step

**VERIFIED, finite database check:** IEDB contains positive **HLA class II
mass-spectrometry presentation annotations associated with human CDR2L**, not
only antibody epitopes or class I ligands. Two assay records linked to the
canonical CDR2L parent accession were returned. Human CDR2 had seven such
records. These are counts of database annotations, not independent patients,
unique peptides, replicated mechanisms or functional CD4 responses.

The earlier report correctly bounded its nonfinding to returned literature
searches. The new result narrows that gap: there are existing human HLA-II
ligand leads to adjudicate before starting a peptide search entirely from
prediction. It does **not** fill the gap of a human anti-Yo CD4 receptor
recognizing a naturally processed, unambiguously assigned CDR2L ligand.

| Parent antigen | Class-II assay records | Source publication and interpretation |
| --- | --- | --- |
| CDR2L, UniProt Q86X02 | [11610866](https://www.iedb.org/assay/11610866) | Marcu et al., 2021, [HLA Ligand Atlas](https://doi.org/10.1136/jitc-2020-002071); benign-tissue reference study |
| CDR2L, UniProt Q86X02 | [18456218](https://www.iedb.org/assay/18456218) | Goncalves et al., 2021, [IFNγ and the TNBC immunopeptidome](https://doi.org/10.3389/fimmu.2021.645770); MDA-MB-231 cell-line study |
| CDR2, UniProt Q01850 | [11480011](https://www.iedb.org/assay/11480011) | Marcu et al., 2021; benign-tissue reference study |
| CDR2, UniProt Q01850 | [16293090](https://www.iedb.org/assay/16293090), [16293091](https://www.iedb.org/assay/16293091), [16293092](https://www.iedb.org/assay/16293092) | [PMID 34357683](https://pubmed.ncbi.nlm.nih.gov/34357683/), HLA-II immunopeptidomics of co-inherited allotypes; records specify HLA-DP |
| CDR2, UniProt Q01850 | [16543635](https://www.iedb.org/assay/16543635), [16553502](https://www.iedb.org/assay/16553502), [16559485](https://www.iedb.org/assay/16559485) | Forlani et al., 2021, [CIITA-transduced glioblastoma](https://doi.org/10.1074/mcp.RA120.002201); named HLA-DR allotypes are **inferred by motif or alleles present**, not experimentally restricted |

All nine records are annotated as positive cellular-MHC/mass-spectrometry
ligand presentation. Both CDR2L records give only a generic human MHC name and
antibody-based class/locus evidence. Neither supplies a validated anti-Yo
receptor or disease-specific restriction in the fields examined.

### What was actually checked

The [IEDB Query API](https://discuss.iedb.org/t/immune-epitope-database-query-api-iq-api/154)
was queried on 2026-11-05. Parent-protein metadata confirmed **UNIPROT:Q01850**
and **UNIPROT:Q86X02**. Case matters: an initial `UniProt:` query returned an
empty response and was corrected against the API's parent-protein metadata;
that empty response was not interpreted as absent evidence.

For each accession:

1. Query `antigen_search` with `parent_source_antigen_iri=eq.UNIPROT:<accession>`,
   selecting only `elution_ids`. The returned parent records listed 376 CDR2
   assay IDs and 45 CDR2L assay IDs across MHC classes.
2. Query those explicit IDs through `mhc_search`, in batches of at most 50,
   with `mhc_class=eq.II` and `limit=50`. Select only `elution_id`,
   `reference_id`, `pubmed_id`, `reference_titles`, `mhc_class`,
   `mhc_allele_name`, `mhc_allele_evidence`, `assay_names`, and
   `qualitative_measure`.
3. Complete every batch, then count returned assay records and distinct
   reference IDs: CDR2 **7 records / 3 references**; CDR2L **2 / 2**.
   These denominators describe the selected canonical-parent mappings only.

Both parent queries were subsequently repeated with `limit=2` and
`Prefer: count=exact`; each returned `Content-Range: 0-0/1`, ruling out a
hidden second parent record at the earlier limit. Requested IDs and returned
class-II IDs were unique; all returned IDs belonged to the requested set and
every batch returned at most its requested ID count.

The [metadata audit](../registries/antigen-metadata-audit-2026-11-05.json)
preserves exact query URLs, selected fields, counts, reference joins and SHA-256
digests of the API response bytes. It contains no peptide/receptor sequences
or participant/sample identifiers. To replay the recorded class-II queries:

```sh
python3 - <<'PY'
import hashlib, json, urllib.request
from pathlib import Path
audit = json.loads(Path('registries/antigen-metadata-audit-2026-11-05.json').read_text())
for antigen in audit['antigens']:
    rows = []
    hashes_match = True
    for query in antigen['queries']:
        with urllib.request.urlopen(query['url'], timeout=30) as response:
            body = response.read()
        hashes_match &= hashlib.sha256(body).hexdigest() == query['response_sha256']
        batch = json.loads(body)
        assert len(batch) <= query['requested_assay_count']
        rows.extend(batch)
    ids = [row['elution_id'] for row in rows]
    assert len(ids) == len(set(ids))
    assert set(ids) <= set(antigen['returned_assay_ids'])
    print(antigen['uniprot'], len(rows),
          len({row['reference_id'] for row in rows}), hashes_match)
PY
```

Snapshot output is `Q01850 7 3 True` and `Q86X02 2 2 True`. A later API change
can change hashes or annotations; preserve it as a new dated check rather than
editing this snapshot. These replay queries use the recorded parent membership;
a fresh coverage audit must repeat the parent queries too.

This was a bibliographic/assay-metadata inspection. The retained queries exclude
peptide sequences, receptor sequences and participant/tissue/sample identifiers.
No supplementary study tables or mass-spectrometry files were requested.
An initial API schema probe requested one antigen record without field
selection; it was not retained or used as research evidence. Subsequent queries
used explicit fields. Primary article methods were read separately. No external
analysis code ran.

The mixed-class antigen summary lists the Forlani glioblastoma paper for
CDR2L, but the joined class-II records above **do not**. Treating independently
aggregated protein, paper and MHC-class lists as a joint observation would
have produced a false CDR2L/class-II attribution. That interpretation was
rejected before recording the result.

### What the annotation still cannot establish

**KNOWN, source-method limits:** Goncalves et al. studied IFNγ-treated and
untreated MDA-MB-231 cells. HLA-II was detected under the treated condition;
the study purified HLA complexes from lysates and identified eluted peptides
by mass spectrometry. Its main text does not name CDR2L. The link between
CDR2L and the paper here comes from IEDB's curated annotation, not a newly
verified original spectrum. Locators: *Immunopeptidomics Sample Preparation*,
*HLA Peptide Identification*, Figure 1 and first Results subsection.

**KNOWN, source-method limits:** Marcu et al. used HLA-affinity purification
and LC-MS/MS on benign tissues, with a 1% local peptide-level FDR and an
estimated 3.9% global HLA-II peptide-level FDR. Their methods explicitly
annotate **all proteins containing a peptide**, without protein inference.
Therefore, an annotation under CDR2L need not uniquely identify CDR2L as its
source. The main text does not identify this particular ligand or tissue.
Locators: *HLA ligand purification*, *Data analysis* and Figure 1. This audit
does not identify a presenting cell, organ or neuronal source for that record.

Neither study establishes anti-Yo specificity. Bulk lysate HLA recovery is
not a direct measurement of a particular peptide-HLA complex at the surface
of the relevant target cell. A benign-tissue annotation does not show immune
tolerance, pathogenicity or safety; a cancer-cell annotation does not show
tumour selectivity. The two annotations have not been checked for shared
peptides, sequence uniqueness, source-version differences, replicate support,
spectral ambiguity, or underlying data reuse.

**Decision:** prioritize adjudicating these specific literature leads before
predicting new HLA-II binders. A future, separately gated source-data check
would establish sequence-to-protein uniqueness, original identification quality,
condition/replicate support and experimental versus inferred restriction.
Only then should a disease-receptor recognition question be posed around a
particular ligand. **Stop or downgrade** a candidate if its assignment is
ambiguous or the original evidence fails; retain any ambiguity in the record.
Original study-data acquisition and fitting remain outside this review.

## Candidate mechanism: the captured antigen and the CD4 ligand may differ

**CONJECTURE:** a CDR2L-specific B-cell receptor could capture a native complex
containing CDR2L, while a CD4 cell recognizes a peptide from another component.
In this model, CDR2L is an **uptake handle**, but need not supply the CD4 ligand.
This is a concrete alternative to assuming that antibody and T-cell specificity
must converge on the same protein. It does not assert that the September study's
expanded cytotoxic CD4 cells have this specificity or this role.

The underlying principle is established immunology, not a new discovery:

- **KNOWN:** [Roosnek and Lanzavecchia, 1991](https://doi.org/10.1084/jem.173.2.487)
  demonstrated efficient presentation of antigen-antibody complexes by
  rheumatoid-factor B cells to antigen-specific T cells. Capture specificity
  and presented antigen can differ within a linked complex.
- **KNOWN:** [Fahlquist-Hagert et al., 2023](https://doi.org/10.1038/s41467-023-42541-7)
  used a murine lupus-like model to show B-cell antigen-presentation-dependent
  spread of autoreactivity across MHC compartments. This does not demonstrate
  an anti-Yo mechanism or a cytotoxic-CD4 pathway.
- **KNOWN:** [Herdlevær et al., 2020](https://doi.org/10.1002/acn3.51212)
  reported CDR2L/rpS6 co-localization, proximity and co-immunoprecipitation in
  OVCAR3 cells (Figures 2 and 3A), plus localization observations in neural
  material. Co-immunoprecipitation supports membership of a recoverable complex;
  it does not by itself prove direct binding, stable extracellular association,
  BCR-mediated uptake or presentation of the partner.

The unexplored bridge is **native cargo → selective uptake → naturally
processed partner peptide → defined CD4 receptor** in anti-Yo. Even a positive
result would first explain an antigen-recognition relationship. Connecting
it to neuronal injury or useful tumour immunity requires separate evidence.
Helper CD4 cells supporting antibody formation cannot be silently substituted
for the September paper's cytotoxic CD4 clones.

### Discriminating observations, rather than an expanding protein list

| Comparison, proposed only | Direct CDR2L-ligand model | Complex-partner-ligand model | Interpretation safeguard |
| --- | --- | --- | --- |
| Purified CDR2L with competent physiological processing versus intact native cargo | Can support the same receptor if the relevant CDR2L ligand is generated | Requires the partner unless another cross-reactive ligand exists | Negative protein delivery is uninterpretable without uptake/processing controls |
| Preserve CDR2L capture but remove a verified complex partner | Response should persist if delivery and presentation remain intact | Response should depend on the true partner | Removing a partner may also change assembly, delivery or cell health |
| Preserve candidate partner delivery but remove the CDR2L capture route | Response may depend on whether CDR2L ligand still reaches the presenter | Alternative delivery can restore response despite loss of the handle | Restoration establishes delivery dependence only when receptor and HLA context are fixed |
| Map recognition to the peptide-HLA complex, then require natural processing of its parent protein | Assigns the receptor to CDR2L if all links agree | Assigns the receptor to a partner if all links agree | Artificial peptide responses alone bypass the key processing question |

**Inference:** even loss of a response after CDR2L deletion, followed by rescue
with CDR2L, would not on its own identify the T-cell ligand. Deletion could
remove the capture handle or disturb associated cargo. Protein function and
cell state are additional alternatives. The decisive question is which
peptide-HLA complex activates the **same** receptor after natural processing,
not which knockout perturbs a bulk readout.

**Falsifier/stop:** if a receptor reproducibly recognizes naturally processed
CDR2L alone under controlled uptake and HLA conditions, the partner model is
unnecessary for that receptor. If intact cargo cannot be demonstrated or the
response is not receptor/HLA-dependent, stop describing it as linked recognition.
A finite negative CDR2L/CDR2 screen neither proves the partner model nor rules
out autoreactivity; it could also reflect an irrelevant clone or failed assay.

## Negative evidence that must travel with the positive evidence

**KNOWN:** [Carpenter et al., 2008](https://doi.org/10.1016/j.jneuroim.2007.10.014)
reported no detectable CD8 responses to two previously described CDR2 epitopes
in seven PCD patients, while viral responses were measurable. This conflicts
with an obligate role for those two epitopes, not with every possible CDR2,
CDR2L or CD4 response. The abstract was inspected; the full experimental record
was not recovered here. Earlier positive CDR2 studies remain in the
[first frontier record](anti-yo-frontier-2026-11-04.md#prior-art-and-the-remaining-gap).

This result argues against treating the historical CDR2 epitope literature as a
single settled chain. It strengthens the need to keep antigen, epitope, HLA,
sample compartment, assay and function separate. It supplies no evidence that
the newly identified database annotations are disease-relevant.

## Novelty audit and limits

The deliverable is a **new-to-project evidence recovery and a discriminating
hypothesis**, not a claim that the literature's authors overlooked their own
results. The ligand annotations and all underlying experiments predate this
review. Linked recognition and epitope spreading are prior art. No direct
anti-Yo native-complex/partner-CD4 demonstration was located in the bounded
queries below; absence from these results is not proof of novelty.

```text
"CDR2L" "HLA-II" peptide TCR
"cerebellar degeneration-related protein 2" site:iedb.org
"CDR2L" "linked recognition"
"CDR2L" "intermolecular" epitope
"anti-Yo" "B cells" "presentation"
"CDR2" "T cells" "negative" response
"CDR2L" "HLA-DR" peptide
"CDR2L" "ligand" "CD4"
```

Primary article methods and curated IEDB metadata were checked, alongside
exact-DOI correction searches for the two CDR2L-linked source papers and the
2023 B-cell paper; no applicable correction was located in the returned results.
This is not an exhaustive correction, patent, conference or non-English search.
CDR2/CDR2L hits referring to immunoglobulin complementarity-determining regions
were excluded by biological identity. No antibody-region prediction result was
accepted as evidence about the cerebellar proteins.

Marcu, Goncalves, Forlani and Fahlquist-Hagert articles state CC BY terms;
Herdlevær states CC BY-NC-ND 4.0. Citation and original summaries here do not
grant reuse rights to study datasets or third-party figures. No paper, figure,
sequence dataset or source table is redistributed. IEDB API access and source
availability do not close the project's separate research-execution gates.

Prepared with OpenAI Codex under human direction. Internal agent review is not
external scientific review.
