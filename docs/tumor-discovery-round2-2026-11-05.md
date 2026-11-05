# Tumor-side discovery review: function, antigen routing and cell number

**2026-11-05 (America/Chicago). Status: public-source evidence review and
proposed discriminating work.** No study-data analysis, experiment, clinical
recommendation or biological discovery is reported. **KNOWN** means a cited
published observation; **CONJECTURE** identifies a proposed explanation or
experiment. This extends the [molecular handoff](molecular-research-handoff-2026-11-04.md)
and [anti-Yo frontier](anti-yo-frontier-2026-11-04.md), with two bounded candidates.

The useful new connection is that the suspected antigen is also part of cell
machinery. Removing it can change both what an immune cell recognizes and how
other material reaches that immune cell. A knockout/rescue result could
therefore establish **dependence on CDR2L without identifying the recognized
antigen**. This is an experimental interpretation problem, not evidence that
either mechanism actually explains the September study.

## Evidence that changes the question

**KNOWN — antigen presence is insufficient.** Raspotnig et al. found CDR2 and
CDR2L in ovarian tumors with and without Yo antibodies. This limits a simple
presence/absence explanation; it does not exclude differences in abundance,
processing or immune context. [2017 primary article](https://doi.org/10.1007/s00262-017-2041-8),
Results, “Expression of CDR2 and CDR2L in ovarian cancer,” and Discussion.

**KNOWN — the 2024 functional lead has specific measurement limits.** Solheim
et al. studied CDR knockouts in OVCAR-3. CDR2L loss altered ribosome/translation
and cell-cycle programs. Their growth readout was well confluence. The
“secretome” was concentrated conditioned medium, explicitly including secreted,
vesicle-associated and dying-cell proteins; database overlap suggested an EV
contribution but did not isolate a route. Re-expression validation remained
proposed work. [Primary article](https://doi.org/10.1186/s12885-024-12399-z),
PDF pp. 2, 10–13; Fig. 7; Methods “Cell proliferation assay” and “Mass
spectrometry-based proteomics.” These limitations do not refute the reported
phenotype.

**KNOWN — a newly recovered mechanistic bridge has strong transfer limits.**
Teixeira et al. demonstrated CDR2L-dependent dynein motility in vitro and
mapped a CDR2–KTN1–eEF1Bβ mechanism regulating ER sheets. The cellular work
principally uses HeLa and CDR2; ER rescue uses CDR2 in a CDR2/CDR2L double
knockout. Endogenous CDR2L immunofluorescence was not detectable; tagged CDR2L
localization used overexpression. The study does not establish ovarian CDR2L
control of HLA-II presentation. [2025 primary article](https://doi.org/10.1083/jcb.202411034),
Figs. 1–5 and S2; Results “CDR2 and CDR2L interact and co-localize…”;
Conclusions. The authors already propose a possible connection between ER
disorganization and anti-Yo toxicity: that broad idea is **prior art**.

## Candidate 1: distinguish an antigen from a regulator of antigen delivery

**CONJECTURE — priority candidate.** In a future assay where deleting CDR2L
reduces activation of a candidate anti-Yo CD4 receptor, at least three
explanations would remain:

1. CDR2L supplies the peptide recognized by the receptor.
2. CDR2L function changes release, uptake or processing of another recognized
   antigen.
3. The perturbation changes viable source-cell number, stress or global antigen
   availability, without a selective antigen mechanism.

Wild-type rescue can restore all three routes. It is valuable evidence against
an unrelated editing artifact, but by itself does not distinguish these
explanations. The added 2025 cell biology makes the second explanation concrete
enough to test. It does not establish that explanation in ovarian cancer.

**Proposed smallest discriminating study, not an executable protocol:** first
validate the relevant localization/functional effect in an ovarian model with
independent perturbations and rescue. Then distinguish **antigen source cells**
from **presenting cells**. Manipulate the source while holding the presenter,
receptor and HLA context fixed; measure naturally processed ligand display and
receptor activation separately from source viability and amount of antigen
delivered. A direct tumor-cell presentation assay answers a different question
and should remain a separate condition.

| Discriminating observation | Interpretation it would support | What it would not establish |
| --- | --- | --- |
| Recognition follows a mapped CDR2L peptide–HLA complex, with sequence-specific receptor evidence and natural processing confirmed | CDR2L is a recognized antigen in that assay | Pathogenicity in humans, exclusivity of that antigen, or safe intervention |
| Source-cell perturbation changes recognition despite comparable antigen amount/sequence; an independently validated routing rescue reverses it | A contribution from source-cell processing or delivery | That the recognized peptide is from CDR2L, or that a specific EV route caused it |
| Effects disappear when viable source-cell exposure and extracellular antigen dose are matched | Cell number, release quantity or nonspecific stress can explain the original contrast | That all CDR2L-related biology is irrelevant |
| Recognition changes across unrelated control antigens in the same direction | A global presentation/activation effect deserves priority | A selective CDR2L antigen mechanism |

The cleanest theoretical contrast would preserve a mapped epitope while
changing a validated cellular function, or preserve function while changing
receptor recognition. **No such separation-of-function reagent has been
established here.** A mutation can alter folding, turnover and processing far
from its own sequence; an unchanged epitope sequence alone does not control
presentation. The HeLa CDR2 rescue constructs cannot simply be relabelled
ovarian CDR2L reagents. KTN1 or EEF1D perturbation is also broad, so it needs
orthogonal specificity controls rather than being treated as a clean switch.

**Falsifier and stop:** if the proposed functional/localization effect cannot
be reproduced in the chosen ovarian context, stop the ER-routing branch. If a
functional rescue cannot be separated from antigen abundance, processing and
general cell health, narrow the result to dependence and do not claim antigen
identity. A negative CDR2L ligand result can redirect an antigen search; a
negative finite panel cannot prove absence of autoreactivity.

**Novelty disposition:** the broad ideas that intracellular localization affects
presentation and that knockout phenotypes need rescue are established. The
candidate contribution is a specific, source-grounded way to challenge a
CDR2L-dependent recognition result using the newly recovered adaptor biology.
No direct demonstration of this ovarian-CDR2L-to-CD4 causal chain was located
in the bounded search below. That is a search limit, not a novelty certificate.

## Candidate 2: separate a growth dependency from geometry and antigen flux

**CONJECTURE — prerequisite measurement question.** Before interpreting the
OVCAR-3 phenotype as a selective tumor dependency or linking it to immune
activation, test whether changes in cell number, spreading, death and secreted
material have been separated. Confluence measures occupied area; changes in
cell area or attachment can change it without a proportional change in cell
number. The newer transport/ER evidence increases the reason to measure these
variables independently. It does **not** demonstrate that cell shape caused
the original confluence difference.

For secreted material, an endpoint concentration also conflates cumulative
source-cell exposure, active release, lysis, uptake and degradation. Equal
starting cell numbers, equal collected volume or equal total loaded protein
cannot each resolve those processes on their own. Comparing only normalized
protein proportions can obscure a change in total material released.

**Proposed smallest discriminating study:** pair direct cell-number/division
and death measurements with confluence and cell area; quantify extracellular
antigen against cumulative viable-cell exposure. Evaluate soluble material,
vesicle-associated material and cell-death leakage as competing explanations
before choosing a transport mechanism. Follow any apparent selective effect
with the source/presenter separation in Candidate 1. Independent perturbations,
physiologic rescue and an additional ovarian model are needed before a general
dependency claim.

**Falsifier and stop:** if confluence changes while division and viable-cell
counts do not, abandon the corresponding growth-rate inference. If release
differences disappear after viable-cell and death accounting, stop the selective
export interpretation. If a reproducible growth effect persists, that supports
a cellular dependency only; it still supplies no platinum-response result,
therapeutic window or neuronal-safety evidence.

**Novelty disposition:** this is an assay-design deduction and a protection
against overinterpreting a target, not a newly discovered molecular mechanism.
It is a small prerequisite that can prevent a larger program following an
incorrect explanation.

## Adjacent lead retained without adding a third priority

**KNOWN:** a separate 2024 study profiled serum exosomal miRNAs in anti-Yo PCD
with ovarian cancer. PCD samples came from Lyon, while ovarian-cancer and
healthy controls came from Bergen. The authors themselves propose CDR2L/RPS6
targeting and serum/CSF comparisons; they call for validation and clarification
of vesicle origin. [Solheim et al.](https://doi.org/10.1002/acn3.52232), Methods
“Sample material,” Table 1, Discussion, Data Availability Statement.

**CONJECTURE / deferred:** this is a useful alternative route into the biology,
but disease and source are inseparable in that group comparison without
additional assumptions or bridge samples. It cannot independently validate
tumor-derived vesicles or neuronal delivery. Computational target assignments
do not demonstrate an effect in either recipient cell. Treat it as prior art
and a design lesson, not corroboration of Candidate 1. Its underlying data are
request-only for privacy/ethical reasons; no request or acquisition occurred.

## Search, sources and limits

Access date for all checks: **2026-11-05**. Discovery used public web search,
followed by primary publisher/PMC article reads. Solheim 2024's main PDF was
read locally outside Git; Teixeira's published PMC article was read through
the web tool after Europe PMC XML returned HTTP 500. The older Teixeira
preprint surfaced separately and was not counted as independent evidence.
No supplements, participant-level tables, external analysis code, private
records or epitope datasets were acquired for this lane.

Selected exact discovery/novelty queries:

```text
CDR2L ovarian cancer knockout ribosome secretome 2024 Solheim
anti Yo ovarian cancer tumors HLA II mutations CDR2L 2018 Vialatte
CDR2L extracellular vesicles antigen presentation cancer
CDR2L platinum resistance ovarian cancer
"CDR2L" "secretome" "upregulated"
"CDR2L" "ribosomal" "localization"
"CDR2L" "antigen presentation" "2025"
"kinectin" "antigen presentation"
"CDR2L" "autophagy"
"CDR2L" "extracellular vesicles"
"CDR2L" "growth" "rescue" antigen
```

Exact DOI searches with `correction OR retraction` for the 2024 knockout,
2025 adaptor and 2024 miRNA articles returned no identified notice. This is a
bounded search, not a publisher certification of absence. CDR2L meaning an
antibody light-chain complementarity region, CDHR2, docking-only target
nominations and unrelated-gene associations were excluded from supporting
evidence. No exhaustive citation-network, patent or all-language review was
completed. No claim of a direct platinum-resistance mechanism survived this
search.

The 2020 localization paper was also checked at primary abstract/returned
full-text-section level: [Herdlevær et al., 10.1002/acn3.51212](https://doi.org/10.1002/acn3.51212),
Results and Fig. 2. Its ribosome/nuclear-speckle observations provide historical
context, not a universal localization rule overriding the newer cell-specific
results. The 2018 tumor-profile papers remain in the preceding handoff; this
review does not treat those tumors as an independent replication of later
cohorts or infer an unverified overlap.

Only original synthesis and citations are retained here. The knockout article
states CC BY 4.0; Teixeira's article points to Rockefeller University Press
terms. Other third-party source rights remain their own. No full text, figure,
dataset or third-party code is redistributed, and no training or clinical-use
right is inferred. The existing [data rules](reproducibility-and-data.md) and
[owner gates](roadmap.md) still govern any future empirical work.
