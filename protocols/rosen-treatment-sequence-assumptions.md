# Rosen treatment-sequence assumption experiment

Version 1, 2026-11-05. Original synthetic mathematics; no study input, model
fitting, clinical validation or treatment recommendation. Locally specified before
the initial analysis run; not independently preregistered. The boundary extension
below was specified after that first run. [Research report](../docs/research/rosen-treatment-sequence-assumptions.md).

## Question and choice

Does chemotherapy enrichment of a resistant compartment by itself imply that
surgery first leaves fewer resistant cells, or does that conclusion depend on
how the surgical removal rule changes with preoperative burden?

Gu et al. (2021, PMID 34161278, Barry Rosen coauthor) motivates this question.
Kohandel et al. (2006, PMID 16580022) already studied sequencing under different
growth and cell-kill assumptions with fixed-fraction surgery. This is an original
implementation and assumption audit, not a claim to originate sequencing models
or reproduce either paper. Its output is a boundary condition for further
research on treatment failure, not Pilot 001's primary-refractory endpoint.

Compared with a recurrent-disease empirical study, this bounded evidence/methods
question has immediately permissible inputs and can identify what a later study
must measure. GSE51831 analysis, request-only survival reanalysis, and full Gu
reconstruction stay deferred under their existing data/method/rights gates.
A null result is useful: it prevents resistant enrichment alone being treated
as a sufficient explanation for a treatment-order effect.

## Fixed model and outputs

- Nonnegative sensitive/resistant burden vector x=(S,R), in invented arbitrary
  units. No units map to people, cells, tumor diameter, dose or time.
- One aggregate chemotherapy operator C=diag(a,b); 0<a<=b<=1 in the grid.
  This selects existing resistance; it does not generate resistance. The same
  operator/exposure is used in both orders, observed after both interventions.
  Surgery is instantaneous; there is no recovery gap, growth between operations,
  dose adaptation, cell interaction, toxicity or stochastic extinction.
- Compare proportional surgery P_q(x)=q*x with fixed-residual surgery
  F_K(x)=min(1,K/sum(x))*x. Both preserve composition. Define F_K(0)=0;
  K>=0, 0<=q<=1. Never add burden to meet K.
- Compare C(surgery(x)) with surgery(C(x)). For paired comparisons set
  K=q*sum(x), making surgery-first intermediate states exactly identical.
- Derive exact algebra, then verify with standard-library rational arithmetic.
  Report absolute sensitive/resistant/total burden **and** resistant fraction.
  Distinguish a common-scale effect from composition change.
- Fixed grid: initial total=100; resistant fraction in {1/100,1/10,1/2};
  a in {1/100,1/10,1/2,1}; b in {1/2,1}; retain q in
  {1/100,1/10,1/2,1}, excluding a>b. This is 84 cases, not a population.
  Report every synthetic case and aggregate equality/direction counts.
- Main example x=(90,10), a=1/10,b=1,q=1/10,K=10. Include an explicit
  reversal with a smaller second-sequence target K_after=1; do not imply that
  this difference is clinically attainable.
- Verify broader linear-map null for scalar retention, and show that diagonal
  selective retention commutes with diagonal chemotherapy. Include a conversion
  map counterexample with selective retention to mark that boundary.
- Keep a protocol identifier, implementation SHA-256, parameters and exact
  output. No randomness, fitting, statistical tests or effect estimates.

## Pre-publication boundary extension

After the contraction grid was executed, source review emphasized that Gu's
resistant cells can grow during chemotherapy. Add one explicitly out-of-grid,
invented boundary example x=(90,10), a=1/2,b=10,K=10, with its result retained
regardless of direction. This is a declared extension, not an alteration of the
84-case grid or a fitted Gu parameter set.

## Interpretation and stopping

Stop the empirical claim at this synthetic construction. No survival, cure,
patient outcome, optimal treatment, biomarker validation or benefit follows.
Do not classify a surgery category such as R0 or <1 mm as exact K. The Gu model
includes dynamics and stochastic processes absent here; a disagreement with this
submodel is not a refutation of its full model. No supplement/code/data retrieval
is required; do not acquire those materials for this experiment.

Advance only to a measurement-design question: can pre/postoperative burden and
composition, timing/exposure, anatomic resectability and selection into sequence
separate the competing removal rules? Aggregate survival or one surgical category
alone does not identify those rules. A future observational causal comparison
also requires confounding/selection analysis and independent review; measuring
these variables does not itself remove bias. Real-data work needs its own
protocol, rights review and applicable owner attestation/execution instruction.
