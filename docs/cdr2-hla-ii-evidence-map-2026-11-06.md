# CDR2 / CDR2L HLA-II source evidence map

**2026-11-06 (UTC) · public literature and database review.** This report continues
[Discovery round 2](discovery-round2-2026-11-05.md) and the
[antigen IEDB audit](antigen-discovery-round2-2026-11-05.md). It maps **candidate
presentation sources** (where a CDR2- or CDR2L-linked HLA-II ligand has been
reported or inferred) separately from **receptor recognition** and **injury**.
No new mechanism, patient result, or anti-Yo CD4 specificity is demonstrated.
Claim labels follow [CLAIMS.md](../CLAIMS.md).

**VERIFIED (this session):** repeating the nine canonical-parent IEDB class-II
assay joins on **2026-11-06** returns the same seven CDR2 and two CDR2L positive
cellular MHC/mass-spectrometry records as the **2026-11-05** audit
([V20](../CLAIMS.md#verified), [S110](../registries/sources.json)).

**CONJECTURE:** ranking which source is most relevant to anti-Yo ovarian/neural
biology is a research judgment only; this map does not perform that ranking.

Prepared with AI assistance (Cursor Cloud Agent) under human direction. Internal
repository checks are not external scientific review.

---

## How to read the map

| Column | Meaning |
| --- | --- |
| **Protein identity** | Stable IDs as cited in the source or IEDB parent mapping. |
| **Presenter / model** | Cells or tissues in which presentation was measured. |
| **Isolation** | How MHC–peptide material was obtained (when stated). |
| **MHC class & allele** | Reported or curated restriction; **unknown** when not resolved. |
| **Processing context** | **Natural processing** = eluted from MHC after cellular expression; **synthetic peptide** = exogenous peptide used in a functional assay; **unclear** = mixed or insufficient detail. |
| **Receptor-recognition evidence** | Whether a defined TCR/BCR recognizes a ligand from this source—not an IEDB row alone. |
| **Injury evidence** | Neural or other tissue injury tied to that recognition—kept separate. |

A positive IEDB **ligand presentation | cellular MHC/mass spectrometry** record
is **HLA presentation metadata**, not human anti-Yo CD4 receptor recognition of a
naturally processed ligand in CSF or tumor.

---

## Table A — Human HLA-II immunopeptidome sources (IEDB curated MS)

Each row is one **source system × parent protein** (one primary publication and
model). IEDB assay IDs link curated metadata only; peptide sequences were not
retrieved here.

| Map ID | Protein identity | Presenter / model | Isolation method | MHC class & allele resolution | Processing context | Receptor-recognition evidence | Injury evidence | Primary source (locator) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **A1** | **CDR2** — UniProt [Q01850](https://www.uniprot.org/uniprotkb/Q01850); RefSeq **NP_001793.1** (UniProt REST, 2026-11-06). IEDB parent **UNIPROT:Q01850**; assay [11480011](https://www.iedb.org/assay/11480011). | **KNOWN:** human **benign reference tissues** from autopsy/living donors (16 autopsy subjects, thymus, ovary, and other tissues aggregated in atlas). Locator: Marcu et al., *J Immunother Cancer* 2021, Methods “Human tissue samples” / “HLA ligands were isolated via immunoaffinity purification” ([DOI 10.1136/jitc-2020-002071](https://doi.org/10.1136/jitc-2020-002071), [S111](../registries/sources.json)). | **KNOWN:** immunoaffinity purification of HLA complexes from tissue, LC-MS/MS (>1200 runs atlas-wide). Same Methods. | **KNOWN (IEDB):** class **II**; allele field **human**; evidence **Allele/Locus-specific Antibody** ([11480011](https://www.iedb.org/assay/11480011)). **Unknown** which specific HLA-II allotype presents this curated CDR2 parent assignment. | **KNOWN:** **Natural processing** (MHC-eluted peptidomics). **KNOWN caveat:** authors state **no protein inference**—“all proteins that contain a given peptide were annotated as peptide source proteins” (Methods, *Data analysis*). Unique CDR2 as source is **unknown**. | **Unknown** for this MS record: no anti-Yo or PCD TCR tied to the eluted peptide in Marcu et al. | **Unknown** (reference atlas; not an injury experiment). | Marcu et al. 2021; IEDB 11480011; PMC8054196 Methods. |
| **A2** | **CDR2L** — UniProt [Q86X02](https://www.uniprot.org/uniprotkb/Q86X02); RefSeq **NP_055418.2** (UniProt REST, 2026-11-06). IEDB assay [11610866](https://www.iedb.org/assay/11610866). | Same **benign tissue atlas** as A1 ([S111](../registries/sources.json)). | Same immunoaffinity/LC-MS/MS pipeline as A1. | **KNOWN (IEDB):** class **II**; **human**; antibody-based class evidence ([11610866](https://www.iedb.org/assay/11610866)). Specific allotype **unknown**. | **Natural processing** with same **multi-protein source annotation** caveat as A1. | **Unknown** (no Yo-specific TCR in source). | **Unknown**. | Marcu et al. 2021; IEDB 11610866. |
| **A3** | **CDR2L** — Q86X02 / NP_055418.2. IEDB assay [18456218](https://www.iedb.org/assay/18456218). | **KNOWN:** human **MDA-MB-231** triple-negative breast cancer cell line; **IFNγ-treated** cells (HLA-II detected under treatment; untreated comparators in study). Locator: Goncalves et al., *Front Immunol* 2021, “Cell Culture” / “Immunopeptidomics Sample Preparation” ([DOI 10.3389/fimmu.2021.645770](https://doi.org/10.3389/fimmu.2021.645770), [S112](../registries/sources.json)). | **KNOWN:** lysate (0.5% IGEPAL), ultracentrifugation; **pan HLA-I (w6/32)** and **HLA-II** with **LB3.1 (DR), B721 (DP), SPV-L3 (DQ)**; acid elution, RP-HPLC, Orbitrap Fusion MS (“HLA Peptide Identification”). | **KNOWN (cell line):** VTIS typing reports class I **A*02:01/02:17, B*40:02/41:01, C*02:02/17:01**; class II **DR*07:01, DR*13:05** (partial table in “HLA Typing of MDA-MB-231 Cells”). **KNOWN (IEDB):** **human** generic class II on [18456218](https://www.iedb.org/assay/18456218)—which allotype carries the CDR2L-linked peptide **unknown**. | **Natural processing** (eluted ligands). **KNOWN:** main text does **not** name CDR2L; link is **IEDB curation** only ([S112](../registries/sources.json)). | **Unknown** (no patient TCR). | **Unknown**. | Goncalves et al. 2021; IEDB 18456218. |
| **A4a** | **CDR2** — Q01850. IEDB [16543635](https://www.iedb.org/assay/16543635). | **KNOWN:** **CIITA-transduced glioblastoma** lines **HROG02, HROG17, RA** (engineered HLA-II presentation). Locator: Forlani et al., *Mol Cell Proteomics* 2021, Abstract / “HROG02, HROG17, and RA GBM cell lines” ([DOI 10.1074/mcp.RA120.002201](https://doi.org/10.1074/mcp.RA120.002201), [S113](../registries/sources.json)). | **KNOWN:** immunoaffinity purification of HLA-I/II complexes and peptide extraction (Methods “Immunoaffinity Purification…”). | **KNOWN (IEDB):** **HLA-DRB1*03:01** with evidence **Inferred by motif or alleles present** ([16543635](https://www.iedb.org/assay/16543635)). **KNOWN (paper):** sample HROG02 includes **DRB1*03:01** in HLA table. | **Natural processing** (MS ligandomics). Allele assignment **partially inferred** (MoDec motif deconvolution; Methods). | **Unknown** (no anti-Yo CD4). | **Unknown**. | Forlani et al. 2021; IEDB 16543635; Figure 4 / peptide identification Methods. |
| **A4b** | **CDR2** — Q01850. IEDB [16553502](https://www.iedb.org/assay/16553502), [16559485](https://www.iedb.org/assay/16559485). | Same CIITA GBM panel as A4a. | Same as A4a. | **KNOWN (IEDB):** **HLA-DRB1*01:02**, **Inferred by motif or alleles present** (both assay IDs). | **Natural processing**; inference caveat as A4a. | **Unknown**. | **Unknown**. | Forlani et al. 2021; IEDB IDs above. |
| **A5** | **CDR2** — Q01850. IEDB [16293090](https://www.iedb.org/assay/16293090)–[16293092](https://www.iedb.org/assay/16293092) (three records). | **KNOWN (abstract):** human **C1R B-lymphoblastoid** cells expressing haplotype **HLA-DR12 / DQ7 / DP4** ([PMID 34357683](https://pubmed.ncbi.nlm.nih.gov/34357683/), [S117](../registries/sources.json)). Full methods **not retrieved** in this session. | **Unknown** in retrieved text (immunopeptidomics stated in abstract; protocol detail not verified here). | **KNOWN (IEDB):** **HLA-DP** locus, **Allele/Locus-specific Antibody** evidence on all three assays. Specific **DP4** peptide assignment to CDR2 **unknown** here. | **Natural processing** (abstract: “naturally processed peptides”). Original spectrum for CDR2 parent **unknown**. | **Unknown**. | **Unknown**. | Ramms et al. 2021, PMID 34357683; IEDB 16293090–16293092. |

**IEDB mixed-list trap (retained):** aggregated antigen summaries may list CDR2L
on the Forlani reference, but the **class-II join used here does not return CDR2L**
([antigen audit](antigen-discovery-round2-2026-11-05.md#what-was-actually-checked)).
Do not treat that aggregation as joint evidence.

---

## Table B — Non–immunopeptidome HLA-II presentation / recall (often cited with CDR2)

These are **not** IEDB MS ligand rows but appear in anti-Yo/T-cell searches and
must stay separate from Table A.

| Map ID | Protein identity | Presenter / model | Isolation / assay | MHC class & allele | Processing context | Receptor-recognition evidence | Injury evidence | Primary source (locator) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **B1** | **CDR2** (murine **Cdr2**), not UniProt human row. | **KNOWN:** **H-2b** mice; **Cdr2-knockout** vs wild-type; adenovirus **AdV-CDR2** immunization ([JCI Insight](https://doi.org/10.1172/jci.insight.96173), [S44](../registries/sources.json)). | **KNOWN:** CD4+ T cells from immunized **Cdr2-KO** hosts stimulated with **predicted H-2-Ab binding peptides** (not MS elution in Figure 2B narrative). | **KNOWN:** **MHCII H-2-Ab**; epitopes called **CDR2-170** and **CDR2-172** (Figure 2B text on publisher page). | **CONJECTURE in source wording** (“naturally processed epitopes”) rests on **prediction + CD4 proliferation**, not HLA-II peptidomics in that figure path. Treat as **unclear** for strict “MS natural processing.” | **KNOWN (mouse):** CD4 proliferation / IFNγ ELISPOT to **CDR2-120** and peptide pools ([S44](../registries/sources.json)); **not** human anti-Yo CSF clones. | **KNOWN (mouse model):** cerebellar / PCD-like autoimmunity context in paper framing; **not** established human neural injury mechanism. | Blachère et al. 2017; Figure 2B–C, Figure 3 (insight.jci.org article view 96173). |

---

## Table C — Human T-cell recognition literature (not HLA-II ligand sources)

Included because searches conflate these with Table A. **Not** candidate HLA-II
**presentation** sources for mapping peptidome leads.

| Map ID | Protein identity | Compartment / model | Assay | MHC | Processing | Receptor evidence | Injury | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **C1** | Human **CDR2** | PCD patient **CSF** | **KNOWN:** activated **CD8+ CTL** reactive to **CDR2** ([PMID 10632096](https://pubmed.ncbi.nlm.nih.gov/10632096/), [S51](../registries/sources.json)). | **Unknown** in abstract for class II. | **Unknown** (not eluted ligand). | **KNOWN:** CD8 effector reactivity; **not** HLA-II presentation map. | **CONJECTURE** in abstract (autoimmune Purkinje destruction); not measured in same assay as ligand. | Albert et al. 2000. |
| **C2** | Human **CDR2** | **HLA-A2.1** transgenic mice; human tumor recognition | **KNOWN:** cloned **CD8+ TCR**; tumor cell recognition ([PMID 18045792](https://pubmed.ncbi.nlm.nih.gov/18045792/), [S76](../registries/sources.json)). | **Class I HLA-A2.1** — not HLA-II. | Epitope discovery included binding screen; **not** Table A peptidomics. | **KNOWN:** CD8 TCR; species/model mixed. | **Unknown** in cited abstract path. | Santomasso et al. 2007. |
| **C3** | Human **cdr2** | **7 PCD patients** — blood | **KNOWN:** **no** CD8 responses to **cdr2-1** or **cdr2-2** peptides; viral CD8 controls positive ([DOI 10.1016/j.jneuroim.2007.10.014](https://doi.org/10.1016/j.jneuroim.2007.10.014), [S116](../registries/sources.json)). | **Unknown** (class I epitope assay in abstract). | **Synthetic peptide** challenge. | **KNOWN negative** for those two epitopes; does not rule out other CDR2/CDR2L/CD4 specificities. | **Unknown**. | Carpenter et al. 2008; abstract only retrieved here. |

**KNOWN gap (unchanged):** no primary source located in bounded project searches
for a **human anti-Yo CD4 receptor** recognizing a **naturally processed CDR2L
(or CDR2) HLA-II ligand** with explicit peptide–HLA assignment
([anti-Yo frontier](anti-yo-frontier-2026-11-04.md#prior-art-and-the-remaining-gap)).
Absence in these queries is **not** proof that no such receptor exists.

---

## Synthesis (what the map does and does not show)

| Question | Map answer | Label |
| --- | --- | --- |
| Are there curated **human HLA-II MS** links to CDR2/CDR2L? | Yes: **7 + 2** IEDB assay records across **five** publication systems (Table A). | **VERIFIED** (IEDB replay); **KNOWN** (methods limits in sources) |
| Is **CDR2L** linked to Forlani CIITA GBM MS in the class-II join? | **No** in joined query (see audit). | **VERIFIED** |
| Does any row establish **anti-Yo CD4** specificity? | **No** row in A–C. | **KNOWN** (negative claim = no supporting source found here) |
| Does presentation imply **neural injury**? | **No** Table A source measures Purkinje/neural injury from that ligand. | **KNOWN** |
| Best next desk step (research judgment) | Adjudicate **sequence uniqueness, allele, and original spectrum** for A2/A3 before receptor questions. | **CONJECTURE** ([C17](../CLAIMS.md)) |

---

## Machine-checkable reproduction

**Run date:** **2026-11-06 (UTC)**. Query manifest:
[registries/cdr2-hla-ii-evidence-map-2026-11-06.json](../registries/cdr2-hla-ii-evidence-map-2026-11-06.json).
Prior parent-enumeration audit:
[registries/antigen-metadata-audit-2026-11-05.json](../registries/antigen-metadata-audit-2026-11-05.json).

### UniProt (REST)

```text
https://rest.uniprot.org/uniprotkb/Q01850.json
https://rest.uniprot.org/uniprotkb/Q86X02.json
```

### IEDB Query API (class II on nine assay IDs)

```sh
python3 - <<'PY'
import hashlib, json, urllib.request
from pathlib import Path
manifest = json.loads(Path("registries/cdr2-hla-ii-evidence-map-2026-11-06.json").read_text())
for q in manifest["iedb_queries"]:
    with urllib.request.urlopen(q["url"], timeout=60) as r:
        body = r.read()
    h = hashlib.sha256(body).hexdigest()
    rows = json.loads(body)
    ok = h == q["response_sha256"] and len(rows) == q["expected_row_count"]
    print(q["label"], len(rows), h, ok)
PY
```

Expected on **2026-11-06:** `CDR2 class-II batch 7 … True` and
`CDR2L class-II batch 2 … True`. API or curation changes should be preserved as a
**new dated** manifest, not silent edits.

Full parent enumeration (376 / 45 total assay IDs per parent) remains the
**2026-11-05** audit replay in
[antigen-discovery-round2-2026-11-05.md](antigen-discovery-round2-2026-11-05.md#what-was-actually-checked).

### PubMed (E-utilities)

Exact queries and expected counts are in the JSON manifest (`pubmed_queries`).
**2026-11-06:** CDR2L + HLA-II terms → **0** hits; CDR2 (excluding CDR2L token)
+ HLA-II terms → **23** hits (mostly non–cerebellar-protein noise; not auto-imported
as evidence).

### IEDB web (manual cross-check)

```text
site:iedb.org UNIPROT:Q86X02
site:iedb.org UNIPROT:Q01850
```

Case-sensitive **`UNIPROT:`** prefix matches API parent IRI convention
([S110](../registries/sources.json)).

### Primary full text retrieved this session

| DOI / ID | Use |
| --- | --- |
| [10.1136/jitc-2020-002071](https://doi.org/10.1136/jitc-2020-002071) | PMC8054196 text — Methods, protein-source annotation |
| [10.1074/mcp.RA120.002201](https://doi.org/10.1074/mcp.RA120.002201) | PMC8724627 text — CIITA GBM immunopeptidomics |
| [10.3389/fimmu.2021.645770](https://doi.org/10.3389/fimmu.2021.645770) | Publisher HTML — MDA-MB-231 methods |
| [10.1172/jci.insight.96173](https://doi.org/10.1172/jci.insight.96173) | Publisher HTML — murine CDR2 CD4 peptides |
| [PMID 34357683](https://pubmed.ncbi.nlm.nih.gov/34357683/) | Abstract only (full text not retrieved) |

Exact-DOI correction searches were not repeated exhaustively on **2026-11-06**;
see dated notices in linked round-2 reviews.

---

## Continuation

Pilot 001 and its endpoint are unchanged. No study matrices, pipelines, author
contact, or private data were used. Next gated work remains **ligand adjudication**
then **receptor–ligand–presenter** tests under [roadmap](roadmap.md) gates—not
collapsing Table A into anti-Yo causality.
