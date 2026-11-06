# Anti-Yo frontier: antigen, presenting cell and effector role

**Follow-up, 2026-11-05:** [Discovery round 2](discovery-round2-2026-11-05.md)
and its [antigen evidence audit](antigen-discovery-round2-2026-11-05.md) refine
the search gaps below. Curated HLA-II presentation annotations must be kept
distinct from functional human anti-Yo CD4 recognition. This document retains
the earlier dated search and does not claim that its nonfindings remain the full
current evidence.

**2026-11-04 · exploration cycles 1–2 · proposal v0.1.** Literature and public
methods reviewed; an [original synthetic identifiability calculation](compartment-identifiability.md)
executed. No disease mechanism discovered, study data analysed, or treatment
recommended. This record preserves evidence, decision rationale, rejected
interpretations and testable next questions. Claim labels follow
[CLAIMS.md](../CLAIMS.md); source IDs refer to [sources.json](../registries/sources.json).

The starting point is Petitpré et al., *Communications Medicine*, published
**2026-09-01**, DOI [10.1038/s43856-026-01841-x](https://doi.org/10.1038/s43856-026-01841-x).
The priority is to resolve **antigen × presenting-cell context × effector role**
for human anti-Yo CD4 clones. Merely nominating CDR2L, measuring immune enrichment
or drawing another pathway network would leave the central uncertainty open.

## Source audit

**KNOWN (S37):** the accepted article reports compartment-associated CD4
cytotoxic states and myeloid programs. Six cases included ovarian or breast
cancer; only **three provided paired blood/CSF**. Five were pretreated. Cancer
controls were untreated and blood-only. PBMC enrichment differed across samples.
Methods use TCR identity to revise cell labels and remove multi-chain cells.
Only the CTL-low frequency contrast against IIH was significant in Figure 4;
blood CTLs showed greater maturation in Figure 5. Overall repertoire overlap
was small. Local switching is an interpretation. Antigen specificity and
functional injury remain untested. Raw sequencing is nonpublic, with institutional
approval and a data-use agreement required for access.

Locators: accepted PDF Methods pp. 2–3, Results pp. 3/5/8, Figures 4–5,
Discussion/Data availability p. 10. No executable repository was located.
Supplement descriptions identify cell-level/TCR material in Excel 5–6;
those files were not downloaded. The accepted version may change.

**KNOWN (S38):** transparent review p. 5 records retention of control samples
excluded in the originating study; identities could not be resolved. Review
pp. 8–9 corrected the inference from RNA expression to JAK/STAT activation.
Phosphorylation remains unmeasured. This warrants sensitivity checks; it does
not establish that the study is wrong.

Article: CC BY-NC-ND 4.0; review file: CC BY 4.0. PDFs were read outside Git,
not redistributed. The registry records URLs, versions and hashes. Exact-DOI
correction/retraction searches located no applicable notice; this is a bounded
search, not certification that none exists. Public source review supplies no
permission to acquire clinical rows or TCR sequences.

## What the first exploration changed

**VERIFIED (V19):** the synthetic calculation constructs different mechanisms
with identical snapshot summaries. A same-clone state difference does not by
itself identify conversion, trafficking direction or local expansion. For a
particular exact paired sign-flip test with three independent donors, the
smallest conventional two-sided p-value is 0.25. That is not a bound on the
paper's between-group tests. A separate sampling example quantifies why an
undetected blood clone need not be absent. See the linked calculation for all
assumptions, code and results.

**CONJECTURE (C09):** the highest-value next evidence would establish a
functional receptor–antigen–presenter relationship and distinguish activation
from injury. A larger transcriptomic signature cannot replace those observations.
Robustness checks remain useful because they determine which clones/states merit
follow-up, but their result would remain an association.

This narrows rather than abandons the protein question. **CDR2L and CDR2 are
candidate antigens; HLA-II molecules determine presentation context; cytotoxic
and signalling proteins are candidate readouts.** They occupy different roles.
An antibody target is not automatically a T-cell antigen, a necessary disease
driver, a tumor dependency or a safe therapeutic target. The broader
[molecular handoff](molecular-research-handoff-2026-11-04.md) preserves those
distinctions and other research directions.

## Prior art and the remaining gap

| Source | Already in the literature | Consequence for this proposal |
| --- | --- | --- |
| Albert et al. 2000, [PMID 10632096](https://pubmed.ncbi.nlm.nih.gov/10632096/) (S51) | Activated CDR2-reactive cytotoxic T cells in PCD CSF | Neither T-cell involvement nor CSF autoreactivity is a new idea. |
| Hillary et al. 2018, [10.1016/j.jneuroim.2017.12.012](https://doi.org/10.1016/j.jneuroim.2017.12.012) (S43) | HLA-II susceptibility associations differ by cancer context | Association does not reveal the human presented peptide or its relevant presenter. |
| Blachère et al. 2017, [10.1172/jci.insight.96173](https://doi.org/10.1172/jci.insight.96173) (S44) | Context-dependent CDR2 presentation and CTL anergy in experimental systems; murine CD4 epitopes | Generic context-dependent immunity is prior art. Human CDR2L-specific CD4 function remains a separate question. |
| Small / Vialatte de Pémille 2018 (S42/S41) | Anti-Yo ovarian antigen alterations and immune-rich tumors | Another bulk immune-enrichment analysis alone would add little. |
| O'Donovan et al. 2020, [10.1093/braincomms/fcaa059](https://doi.org/10.1093/braincomms/fcaa059) (S45) | Anti-Yo antibody fragment recognition maps | Antibody epitopes do not define the naturally presented HLA-II repertoire. |
| AEGIS, [May 2026 preprint](https://pmc.ncbi.nlm.nih.gov/articles/PMC13192975/) (S46) | Functional B/T specificity mapping in ROHHAD | Useful method transfer, not peer-reviewed anti-Yo evidence. Generic B/T convergence is not our invention. |
| Chen et al. 2026, [10.1038/s41591-026-04728-5](https://doi.org/10.1038/s41591-026-04728-5) (S47) | Shared-clone compartment comparisons and APC–T-cell complexes in ALS; differing outcome associations | Transfer comparisons, not disease conclusions. Local immune activity does not establish a harmful role. |
| Petitpré et al. 2026 (S37) | Explicitly proposes antigen-specific functional follow-up | Testing CDR2/CDR2L recognition is the authors' next step, not a newly invented proposal here. |

**Novelty status:** none of the broad mechanisms or techniques above is claimed
as new. The contribution proposed here is a discriminating, anti-Yo-specific
comparison of antigen identity, natural processing, presenter and effector role,
with an explicit ambiguity/robustness benchmark. A positive empirical result
could be new; no such result exists in this repository. Patent, conference,
non-English and unpublished-work coverage is incomplete.

## Competing explanations and observations that separate them

All rows are **CONJECTURE**, including their priority. Several may coexist.

| Model | Observation that would support it | Observation that would weaken it | What a snapshot cannot settle |
| --- | --- | --- | --- |
| H1: natural CDR2L/CDR2 presentation restimulates specific CD4 clones | The same receptor recognizes a naturally processed antigen in the relevant HLA-II context; activation depends on antigen and presentation | Only artificial peptide delivery activates it; responses persist without the candidate antigen; unrelated receptors respond similarly | Which antigen is actually recognized |
| H2: selective entry/retention explains compartment composition | Already-present states account for CSF patterns after clone/depth matching; no robust residual within-clone contrast | Repeatable state changes in tracked cells under controlled presentation | Direction of movement, local conversion, survival versus recruitment |
| H3: CD4 cells amplify injury indirectly | APC/CD8/B-cell or soluble-mediator dependence separates CD4 activation from neural injury | Direct target-specific injury persists when proposed intermediaries are absent | Cytotoxic transcripts do not identify the injured cell |
| H4: expansion is unrelated-antigen, bystander or protective activity | Alternative antigen recognition or protective function explains expanded clones | Reproducible candidate-antigen-dependent neural injury across independent relevant systems | Clonal expansion alone does not imply pathogenicity |
| H5: preparation, annotation or control choice drives a key contrast | Effect changes materially under independently defined labels, preparation strata or control exclusions | Effect direction is stable across predefined sensitivities and donors | Clean integrated clusters alone cannot certify absence of confounding |

### Priority question: can presenting context separate tumor response from neural injury?

**CONJECTURE (C10):** for a receptor with validated antigen recognition,
presenter identity and natural processing may distinguish useful tumor-directed
activity from harmful neural inflammation. It is possible that these functions
cannot be separated; that negative result would also matter. Do not assume the
same antigen amount means the same peptide–HLA display.

A future mechanistic study should compare the following **conceptual conditions**,
without treating them as a ready-to-run clinical or laboratory protocol:

| Fixed or varied factor | Required comparison | Separate readouts |
| --- | --- | --- |
| Receptor | Same paired receptor versus unrelated/nonexpanded controls | Antigen-specific activation, not expansion alone |
| Antigen | CDR2L, CDR2, unrelated controls; broader search if negative | Recognition potential versus natural processing |
| HLA and presenter | Relevant human HLA-II; myeloid/B-cell/other candidate presenters with appropriate presentation controls | Presenter-dependent activation and presenter injury |
| Effector context | Neural versus tumor targets; potential cellular intermediaries | Neural injury and tumor control measured separately |
| Antigen form, only if justified | Documented tumor alteration versus reference protein, with abundance and processing controlled | Cross-recognition rather than assumed mutant-to-self spread |

A response to supplied peptide can bypass normal antigen processing. A reporter
response is not killing. A shared receptor sequence is not proof of a shared
antigen. Human HLA restriction cannot be inferred from a mouse epitope or a
population risk haplotype. Do not limit a T-cell antigen search to known antibody
binding fragments, or equate a negative finite panel with absence of autoreactivity.

The protein sequence/structure route becomes useful after these constraints are
defined: it could prioritize hypotheses about processing or cross-recognition.
Structure prediction or peptide-binding prediction alone cannot identify the
causal antigen, receptor specificity or a safe intervention.

**2026-11-05 addition:** the [exposure and observability record](research/paraneoplastic-exposure-observability.md)
examines the same separation at the level of dynamics. If tumor and neurons share
an antigen-driven effector, neural loss depends on antigen exposure over time, and
the order of treatments can change it while the tumor endpoint cannot. Whether
injury is still antigen-driven needs an injury-rate measurement anchored to
treatment events; deficits and antibody titers cannot show it.

### Secondary question: could antigen processing uncouple abundance from immune risk?

**CONJECTURE (C11):** the relevant change may concern which peptides are
presented, not simply how much CDR2L exists. This is a candidate explanation for
why a tumor protein's abundance and the immune response need not track together.
The [CDR2L knockout study](https://doi.org/10.1186/s12885-024-12399-z) (S39)
offers a separate cell-biology lead, not evidence of such a presentation mechanism.

A useful future comparison would hold growth/stress state and antigen abundance
as comparable as possible while distinguishing protein function, processing and
T-cell recognition. If an apparent immune effect disappears after those controls,
generic stress/proliferation becomes the better explanation. If presentation
changes with recognition while total abundance remains comparable, a processing
hypothesis earns further testing. No published data reviewed here establish this
chain, and a knockout effect cannot be substituted for antibody or drug action.

## Proposed robustness protocol and feasibility gate

**Population/endpoint:** paired blood/CSF anti-Yo research samples, with cancer
type, treatment and timing retained; do not silently relabel the cohort HGSOC.
Primary descriptive endpoint: donor-level, within-shared-clone state contrasts.
Secondary endpoints: clone sharing/coverage and control-sensitive state abundance.
This proposal is not a diagnostic classifier or a treatment-response study.

**Inputs needed:** permitted expression/count data, pairing and preparation
metadata, paired TRA/TRB recovery, independent cell annotations and control-source
inclusion records. There is currently no verified unrestricted input route.
Existing Pilot 001 authorization does not transfer to these files. Any future
acquisition requires a separate protocol decision and the applicable
[Gate 0](roadmap.md), rights/consent assessment and execution-context approval.
No author request has been sent for this frontier track.

**Proposed analyses, not executed:**

1. Freeze labels and a state definition independent of TCR identity; compare with
   the published annotation procedure. Avoid testing a phenotype with the exact
   genes used to select it without a noncircular validation measure.
2. Report informative donors and shared-clone coverage before estimating effects.
   Predefine clone-averaged versus cell-weighted summaries; show both as sensitivity
   analyses, with depth/clone-size matching. Do not select the one with the best p-value.
3. Compare controls separately and retain original preprocessing provenance.
   If excluded-control identities remain unresolved, enumerate plausible exclusions
   and report the range; do not reconstruct identities by guesswork or cherry-pick.
4. Stratify preparation, cancer type, timing and treatment where supported. With
   sparse donors, label non-estimable confounding rather than fit an overparameterized
   adjustment model. Leave-one-donor-out stability is descriptive, not validation.
5. Check multi-chain and annotation sensitivity. Keep strict singlets as the main
   analysis. Candidate APC–T-cell conjugates need orthogonal evidence; neither
   accepting every mixed droplet nor discarding every mixture proves a mechanism.
6. Record effect sizes and uncertainty under stated assumptions. Use the synthetic
   ambiguity example as a check on interpretation, not as a fitted null model.

**Success/decision:** a stable association justifies a narrower mechanistic study;
an unstable one redirects work toward the source of instability. Neither outcome
establishes causality. **Stop** the intended contrast if pairing, usable clones,
rights or independent labels cannot be established. **Narrow** the question if
preparation/treatment confounding is inseparable. No study-data compute budget is
authorized here; the current offline calculation completes in under a second.
Future work needs neuroimmunology, cancer immunology and small-sample statistical
review; those reviewers/partners have not been recruited.

## Exploration log and continuation

| Cycle-1 action | Outcome and decision |
| --- | --- |
| Read accepted article and transparent review after landing-page access failed | Corrected cohort/access interpretation; retained the study as hypothesis-generating evidence |
| Search anti-Yo/CDR2L/CD4/HLA-II, antigen presentation, TCR specificity, immunopeptidomics and correction terms | Located HLA, context-dependent tolerance, antibody epitope and cross-disease prior art; broad novelty claims rejected |
| Challenge local-switch interpretation using an abstract selection/conversion model | Executed exact counterexample; shared identity plus changed state does not identify the transition process |
| Consider a two-condition “activation gate” analogy | Retained only as antigen/presentation factorial comparisons; no claim that biology is a binary gate |
| Compare cross-disease examples | Transferred controls and assay logic; rejected transfer of ALS or ROHHAD outcomes to anti-Yo |
| Reconsider protein-first prioritization | Prioritized antigen specificity and presenter/effector separation; parked drug nominations and structure-only target claims |

### Cycle 2: distinguish genuine antigen evidence from similar terminology

A second bounded search on 2026-11-04 used these exact queries:

```text
"CDR2L" "HLA-II" peptide TCR
"CDR2L" "CD4" "recognition"
"CDR2" "naturally processed" "class II"
"CDR2L" "immunopeptidome"
"cerebellar degeneration related" "class II" "epitope"
"CDR2L" "peptide" "HLA" -"CDR2L region" -"scFv" -"complementarity" -patent
"anti-Yo" "CD4" "antigen-specific" -review
"cdr2" "naturally processed" HLA-A2
```

Initial results frequently used **CDR2L to mean an antibody light-chain
complementarity-determining region**, not the cerebellar protein. Those hits
were excluded by biological identity, not counted as relevant evidence.
Primary-paper checks yielded this evidence matrix:

| Evidence layer | Located evidence | Unresolved transfer |
| --- | --- | --- |
| Antibody recognition | CDR2L/CDR2 fragment maps (S45) | Does not identify a T-cell ligand |
| Naturally processed CDR2, HLA class I | Santomasso et al. 2007, [PMID 18045792](https://pubmed.ncbi.nlm.nih.gov/18045792/) (S76): HLA-A2.1 work using transgenic mice and human tumor-cell recognition | Does not establish human CDR2L–HLA-II recognition |
| Naturally processed CDR2, MHC class II | Blachère et al. 2017 (S44), mouse H-2Ab; whole-protein/vector immunization followed by peptide recall | Not direct immunopeptidomics; does not establish human HLA restriction or CDR2L specificity |
| Human anti-Yo CD4 receptor + naturally processed CDR2L + HLA-II | No direct primary demonstration located in these returned results | Unresolved search gap, not a negative biological experiment or proof of novelty |
| Human CD4 antigen specificity in another disease | AEGIS preprint (S46) | Method transfer only; different antigen and disease |

**Decision:** retain H1 as an open, specific question. Do not claim antigen/TCR
mapping in paraneoplastic disease is new, confuse class I with class II, or
promote antibody-target evidence into T-cell-target evidence. The search did
not systematically query epitope databases, enumerate every citing paper, or
screen all languages and patents; those are meaningful next steps.

Next cycle: inspect curated epitope records and forward/backward citations for
**human naturally processed CDR2L/CDR2 HLA-II ligands and functionally validated
CD4 receptors**. Separate positive evidence, negative experiments and experiments
never done. Seek a result that would make H1 unnecessary. The literature task
can proceed without restricted data or outreach. Record a bounded negative search
without calling it a discovery.

For subsequent cycles, use abstract reasoning to generate competing models, then
translate each into observable variables, a falsifying result and an obtainable
input. Discard analogies that cannot make a discriminating prediction. Preserve
dated corrections and failed avenues rather than overwrite them. A discovery
claim requires new evidence and renewed prior-art checking, not confidence in
the narrative.

### Cycle 3, 2026-11-05: what irreversible injury records about antigen

| Action | Outcome and decision |
| --- | --- |
| Asked what the neural endpoint adds to the treatment-sequence null case | Exact result: final neural survival depends on a schedule only through antigen exposure; order changes exposure while the tumor endpoint is unchanged (V27) |
| Split antigen presentation into burden-driven and release-driven hypotheses, using cross-presentation of apoptotic tumor cells (S126) | The two recommend opposite orders when surgery retains more than one cycle; retained both as CONJECTURE (C22) |
| Asked what could show an ongoing attack | Deficit, atrophy and antibody titer are states (S125); intensity needs an injury rate divided by remaining target; proposed a treatment-anchored design (C23) |
| Checked serum NfL as the rate marker | Confounded by surgery (S131) and neurotoxic chemotherapy (S130); design requires an antibody-negative comparator; no anti-Yo NfL cohort found |
| Cross-checked on the Virtual Human engine | Identity, orders and signatures reproduced; continuous chemotherapy moves the burden-driven threshold (V28) |

Next cycle: the [continuation tasks](research/paraneoplastic-exposure-observability.md#continuation-for-the-team),
starting with the primary sources behind the conflicting timing evidence.
