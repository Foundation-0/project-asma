# Discovery round 2: distinguish antigen identity, protein function and injury

**2026-11-05, America/Chicago.** Public-source research and proposed comparisons,
starting from merged commit `dae425c`. No new biological discovery, clinical
result or study-data reanalysis is claimed. The purpose is to expose assumptions
that can hide useful findings, then specify observations that distinguish the
alternatives. Patient-specific material is outside this public record.

## What changed in this round

The central question is now more precise: **does an immune response depend on
CDR2L because it recognizes CDR2L, because CDR2L changes the supply/presentation
of another antigen, or because both occur?** A separate question asks whether
that response causes neural injury. These propositions require different
evidence. The previous [antigen/presenter/effector proposal](anti-yo-frontier-2026-11-04.md)
already separated broad roles; this round seeks discriminators within them.

| Priority | New-to-project evidence or deduction | What would change the decision |
| --- | --- | --- |
| 1. Resolve the exact antigen-evidence gap | The [antigen review](antigen-discovery-round2-2026-11-05.md) distinguishes curated HLA-II presentation evidence for CDR2L from anti-Yo-specific receptor recognition and injury. | A validated human anti-Yo receptor recognizing an identified, naturally processed CDR2L–HLA-II ligand would materially advance the direct-recognition model. A database hit alone does not. |
| 2. Separate CDR2L's cellular function from its antigenic role | The [tumor review](tumor-discovery-round2-2026-11-05.md) adds ER/dynein adaptor biology and audits the ovarian knockout's growth and secretome readouts. | A recognition effect that follows a defined ligand independently of trafficking, viability and general presentation supports direct antigen causality; an effect shared across unrelated ligands supports a broader cellular explanation. |
| 3. Test antigen identity independently from effector harm | The [causal review](causal-discovery-round2-2026-11-05.md) examines CMV-associated cytotoxic CD4 states, alternative injury routes and source confounding. | Receptor-level specificity and separately measured target injury can discriminate autoreactivity, historical antiviral activation, cross-reactivity and bystander effects. Seropositivity or a cytotoxic expression state cannot. |

The ranking is a **CONJECTURE** about research value, not an estimate of which
mechanism is true. The three questions can yield different answers in different
clones, tissues or phases of disease. A single dominant narrative is not required.

## A trap worth designing around

**CONJECTURE — conceptual causal alternatives, not observed experiments:**
suppose removal of CDR2L reduces T-cell activation and reintroduction restores
it. At least three explanations can fit that result:

1. The receptor recognizes a CDR2L-derived ligand that disappears and returns.
2. CDR2L influences source-cell physiology, antigen release or processing, so
   another recognized ligand disappears and returns.
3. Both processes contribute.

Ordinary restoration of the whole protein restores both its sequence and its
cellular roles. It does not, by itself, separate these explanations. The general
logic is established perturbation reasoning; its application here is a design
proposal, not a new mathematical result. The new cell-biology evidence makes the
alternative worth testing, but **does not demonstrate CDR2L-dependent HLA-II
processing in ovarian tumors or neurons**.

A discriminating future study would keep source-cell and presenting-cell roles
explicit, identify the recognized ligand/restriction, and compare antigen supply
with unrelated presentation controls and source-cell viability. A functional
separation between sequence recognition and cellular activity would be valuable
only if it can actually be validated. No ready-to-use separation-of-function
construct or experiment is asserted here. Supplied peptide can bypass processing;
its rescue of activation is informative but cannot establish physiological
presentation or neural injury on its own.

The linked-recognition alternative adds another distinction: a B cell could
capture a protein-containing complex while its helper T cell recognizes a
different component. General linked recognition is old immunology. Its proposed
anti-Yo implementation, the existence of the relevant extracellular complex, and
its connection to the cytotoxic CSF clones are all unproved. See the antigen
review for prior art and the required separate links.

## An additional avenue examined and held below the shortlist

**KNOWN — reported exploratory study:** Nicola et al., published **17 June
2026**, studied vascular/stromal features of Yo- and Ri-associated **breast**
cancers ([primary article](https://doi.org/10.1186/s13058-026-02321-9)).
Its main Results report only three Yo-group genes and no Ri-group genes surviving
multiple-testing correction; many pathway interpretations use nominal values.
Methods describe retrospective groups, targeted expression profiling and small,
partially overlapping histology subsets. The authors already propose lymphatic
antigen transport and local priming; that idea is not new here. Their Discussion
states that tertiary lymphoid structures were not directly assessed.

**Decision:** retain antigen delivery and regional lymph-node context as a
possible modifier, but do not promote this to an established ovarian mechanism
or an intervention target. It ranks below identifying ligand/receptor evidence
because the proposed route lacks direct mechanistic demonstration and independent
ovarian validation. No individual data or supplemental tables were acquired.
Locators: Methods, “Study design and tumour selection” / “Statistical analysis”;
Results, “Shared tumour-related and microenvironment features involving
angiogenesis”; Discussion. Exact-DOI notice search found no applicable correction
or retraction in returned results; this is not certification of absence.

## How to pursue novelty without assuming it

| Potential reasoning failure | Countermeasure used here | Remaining limitation |
| --- | --- | --- |
| A familiar antibody name fixes the T-cell antigen | Separate protein identity, antibody binding, HLA presentation, receptor activation and injury; query stable protein identifiers. | A finite literature/database search can miss evidence. |
| A changed phenotype after deletion establishes the direct mechanism | Enumerate direct antigen loss and indirect physiological effects; require a comparison that separates them. | Conceptual controls need validation in relevant systems. |
| A cytotoxic state establishes a pathogenic target | Check unrelated-antigen and bystander alternatives; keep specificity and injury as separate outcomes. | Cross-disease evidence does not establish an anti-Yo mechanism. |
| Integrated data remove source confounding | Identify comparisons in which disease and source cannot be separated; require bridging observations. | Statistical correction alone cannot supply missing design overlap. |
| A plausible story counts as a novel finding | Record prior art, contrary experiments, discriminators and explicit rejection conditions. | No exhaustive patent, conference, non-English or unpublished search. |

## Continuation contract

The immediate handoff is a **source-grounded research shortlist**, with the
individual reviews preserving search routes, counterevidence and stopped ideas.
Existing Pilot 001 and its endpoint remain unchanged. Before acquiring study
files, reconstructing receptors, fitting models or laboratory execution, a
bounded protocol must define the population/model, allowed inputs, comparison,
independent replication unit and stop rule under the existing
[roadmap gates](roadmap.md). This review does not claim those activities occurred
or that their permissions are established.

The strongest next desk-research deliverable is an evidence map for each
candidate CDR2L/CDR2 HLA-II source: protein identity, presenter/model, isolation
method, class/allele resolution, processing context, receptor evidence and injury
evidence. Keep unknown cells unknown. A map that shows exactly where evidence
ends is more useful than assigning a causal protein from a name or signature.
**Executed follow-up:** [CDR2/CDR2L HLA-II evidence map, 2026-11-06](cdr2-hla-ii-evidence-map-2026-11-06.md).

Independent internal agent review challenged the source transfers and novelty
claims. It is not external scientific or clinical review. Repository validation
checks structure and links; it cannot establish the proposed biology.
