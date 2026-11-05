# A virtual human with an evidence trail

**Vision record, 2026-11-05.** The long-term ambition below is **CONJECTURE**:
a research direction, not a description of an existing complete system. Current
software results are identified separately. This record supports the public
website and extends the [mission](mission.md) without changing any study endpoint
or data-execution gate.

## The dream

Imagine an executable atlas of human biology: molecules, cells, tissues and
organs connected through explicit mathematics. A researcher could follow a
prediction back through every modeled interaction, inspect the evidence and
assumptions, and ask what would have to be measured for that prediction to be
trusted. A discovery in one part of the atlas could become a carefully checked
building block for work somewhere else.

Our most ambitious destination is an end-to-end system of biological models
whose stated mathematical properties and connections carry machine-checkable
proofs. Instead of losing assumptions between disciplines, the system would make
them visible. Instead of hiding disagreement, it would show which experiments
could distinguish competing explanations. Its purpose would be to help people
ask better questions about life, disease and treatment—and answer more of them
with evidence they can inspect.

For Project Asma, that dream begins with ovarian cancer: understanding treatment
failure, separating plausible mechanisms, and making research more reproducible.
The wider hope reaches medicine as a whole. The meaningful measure of progress
would eventually be better decisions, less unnecessary experimentation, less
suffering and more lives lived well. None of those benefits has been demonstrated
by this project yet.

## What it could make possible

Every use in this table is a **conditional aspiration**, requiring suitable models,
observations and validation for its own intended use.

| Area | A capability worth working toward |
| --- | --- |
| Understanding the human body | Trace how a molecular change might affect a cell, a tissue and an organ; identify where knowledge is missing or contradictory; compare mechanisms across scales without silently changing units, assumptions or populations. |
| Research and experiments | Run controlled computational perturbations, test alternative explanations, and select measurements that best distinguish them. A model that fails against independent observations would reveal a useful gap rather than quietly becoming the next model's input. |
| Drug discovery and design | Investigate binding, exposure, metabolism, resistance and possible off-target effects together, helping prioritize candidates for experimental testing. Predicting a target interaction alone would not establish a safe or effective medicine. |
| Drug synthesis and manufacturing | Connect candidate design to separately verified chemistry models and proposed synthesis routes, constraints and experimental records. Making a compound, controlling impurities, producing a stable formulation and manufacturing it reliably would still require additional chemistry, process models and laboratory evidence. This capability is not present in the current fork. |
| Clinical testing and trials | Explore protocol assumptions, timing, candidate endpoints and sources of variation before a study; help identify informative measurements and conditions under which a design could fail. Any use of simulated participants or model-derived evidence would need validation for that precise role, appropriate oversight and regulatory acceptance. |
| Individual variation and future care | Study how explicitly modeled differences change predictions, then test whether those differences correspond to people. Personal models would require appropriately consented and permitted data, uncertainty that remains visible, and prospective evaluation before informing care. No patient-specific model is offered here. |
| A shared scientific memory | Preserve methods, unsuccessful hypotheses and evidence provenance so that a checked result can be reused, challenged or revised. Human researchers and AI systems could collaborate on the same inspectable mathematical objects. |

The ambition is to make experiments and trials more informative, and potentially
reduce avoidable burden where evidence supports that use. It is not a promise to
replace laboratory work, animal studies, clinical trials or clinical judgment.
Some questions may remain too uncertain, computationally expensive or poorly
observed for useful prediction.

## What “formally verified” would mean

A proof establishes a stated property from stated assumptions. It does not
establish that those assumptions completely describe a living person. A model
could be mathematically consistent and still omit a decisive biological process.
The distinction is central to the dream, because it tells us what to prove and
what to measure.

The proposed system would keep three questions separate:

1. **Does the mathematics and implementation do what is specified?** Examples
   include dimensional consistency, conserved quantities, valid connections
   between models, and explicitly bounded numerical approximations. A future
   proof-assistant layer could check selected theorems and their assumptions;
   the trusted computing base and any unproved obligations would remain visible.
2. **Does the model predict the observed biology in this context?** Independent
   measurements, held-out observations, uncertainty analysis and experiments
   designed to falsify the model must answer that. A proof cannot supply missing
   observations or turn an assumed mechanism into an established one.
3. **Does using it improve the intended decision or outcome?** Clinical or
   research usefulness needs its own prospective evaluation. Numerical accuracy
   alone does not establish efficacy, safety or patient benefit.

For example, proving conservation in a reaction network would establish a
property of its equations. Showing that a numerical solver preserves that
property within tolerance is a different check. Establishing that those reactions
and rates describe an actual tumor is a further empirical task. Linking models
would require checking the assumptions and approximation error at each boundary;
verified components do not automatically make a verified whole.

[Lean's own documentation](https://lean-lang.org/) describes a proof assistant for
formal mathematics and program verification; it illustrates a class of tools a
future layer might use, not a selected dependency or an implemented integration.
The FDA's [November 2023 computational-model credibility guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/assessing-credibility-computational-modeling-and-simulation-medical-device-submissions)
describes a risk-informed framework for medical-device submissions. Its scope is
not a general approval route for a virtual human, drug development or Project Asma.
Both primary pages were read on 2026-11-05; no endorsement is implied.

“End-to-end” is therefore a distant ambition for connected, explicitly scoped
models with traceable proof and evidence obligations. It is not a claim that
every human process can be completely captured or that simulating every atom is
the route to it. Models at different scales would need justified approximations,
with the missing biology and limits of applicability kept in view.

## The foundation we actually have

The project builds on [Rohan Arun's Virtual Human](https://github.com/rohanarun/virtual-human)
through the [Foundation-0 fork](https://github.com/Foundation-0/virtual-human).
Creator credit and MIT attribution are retained. The upstream project contains
molecular, quantum, physiological and graph modules; their existence is not a
claim that the full stack has been validated for ovarian cancer or adopted by Asma.

| Work in place as of 2026-11-05 | Evidence and exact boundary |
| --- | --- |
| Public evidence graph | [Asma PR #45](https://github.com/Foundation-0/project-asma/pull/45), merged. The [executed record](evidence-graph-result-2026-11-05.md) describes 24 curated assertions and 22 scoped requests. It retains unknowns, counterevidence and context; it does not prove the assertions or an anti-Yo mechanism. |
| Explicit model interfaces and clearance reporting | [Fork PR #1](https://github.com/Foundation-0/virtual-human/pull/1), merged. Required quantities, units, reference bases, context and provenance make some incompatible connections fail. Exact checks exposed a blood/plasma reference issue. These are bounded software and mathematical checks, not formal verification of the full system. |
| Reaction and intervention experiments | [Fork PR #3](https://github.com/Foundation-0/virtual-human/pull/3), merged as `3523b288661e41c6ebf10ac427b75fd88f329e31`. Its [pinned report](https://github.com/Foundation-0/virtual-human/blob/8e5eacda08027219c0e8f6dfc37ef276829fb928/auto-research/2026-11-05-E-reaction-experiments/report.md) records exact conserved-pool checks, elementary reaction dynamics, ordered interventions and local rate sensitivities. It passed 153 Python tests and JavaScript engine checks. This is one fixed compartment, with artificial fixtures and a fixed-step solver. |
| A research question that uses those tools | [Asma PR #47](https://github.com/Foundation-0/project-asma/pull/47), merged as `290af9d05566dd2ce2451a3d5f0d8201d1d84557`. The [Rosen-inspired assumption audit](research/rosen-treatment-sequence-assumptions.md) shows how two surgical-removal rules can agree on one sequence yet disagree on the other. It proposes a discriminating measurement study; no treatment preference or biological novelty is established. |
| A connection between the repositories | The [pinned integration record](https://github.com/Foundation-0/virtual-human/blob/8e5eacda08027219c0e8f6dfc37ef276829fb928/docs/project-asma-integration.md) compares twelve synthetic outcomes against Asma's exact rational operators. Maximum absolute discrepancy is about `4.8531e-14 mol/L`, below `1e-10 mol/L`. This checks the same artificial mathematics in two implementations; it is not a physiological unit conversion or clinical validation. |

These checks are **VERIFIED** within the recorded cases. There is no current
proof-assistant integration, formally verified complete biology, validated
end-to-end human model, or demonstrated clinical efficacy. The full SBML import
milestone also remains open. Asma uses a small pinned graph core and an optional
synthetic comparison; it does not depend on the entire simulation stack.

## How the dream could become research

The next useful step is a bounded question with a result that could prove a model
wrong. For the Rosen-derived direction, that means identifying observations that
distinguish competing removal rules. For the anti-Yo frontier, it means resolving
specific evidence links among antigen source, presentation, receptor recognition
and injury before assigning numerical kinetics to unknown biology.

As that work develops, a proposed verification layer could start with one modest
theorem, such as conservation for a declared class of reaction networks. It would
record its assumptions, mechanization and connection to executable code. A
separate empirical benchmark would test whether a particular network is useful
for a particular biological question. Connecting two models would add new proof
and validation obligations rather than inheriting confidence by association.

The long-term hope is cumulative: increasingly capable models, increasingly
explicit guarantees, and increasingly demanding tests against reality. Each step
should leave something useful even if the complete vision proves unattainable.
That is how a dream about understanding the body can remain accountable to the
person whose memory gave this project its purpose.
