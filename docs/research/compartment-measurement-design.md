# Which extra observation would distinguish the mechanisms?

**Original synthetic mathematics, 2026-11-13 UTC.** The
[earlier compartment example](../compartment-identifiability.md) showed that
preferential selection of an existing cell state and conversion into that state
can produce exactly the same snapshot. This continuation asks a more useful
question: **which additional observations would separate those explanations,
and how accurate would they need to be?**

In the declared model, pairing two different starting mixtures separates zero
conversion from a specified substantial-conversion alternative at a precision
where either reading alone, or repeating the baseline with one changed mixture,
does not. That advantage disappears if the measurement offsets differ freely
between readings, or if selection changes freely between mixtures. These are
conditional mathematical results, not findings about patients or the biology
of the source study. No assay precision, biological rate or clinical benefit
has been estimated.

## The question in ordinary language

Imagine a mixture of cells in two states, called low and high. A larger fraction
of high-state cells at the end could mean that high cells were preferentially
selected, that low cells changed state, or some combination. Counting more cells
in that same mixture does not necessarily distinguish these explanations.

Now imagine changing the starting mixture. Different explanations predict
different responses. A measurement device may also shift every reading up or
down by an unknown common amount. Subtracting two readings cancels that shared
shift. The useful signal is then the difference in responses, which must exceed
the remaining error. This familiar idea only works if the two experiments share
both the relevant biology and the measurement offset.

An actual experiment would need a validated state definition, feasible mixture
preparation and evidence for those shared properties. An input fraction here is
an exact invented number. It is not a patient blood fraction, a dosing choice,
or evidence that a particular cell-state intervention is attainable.

## Declared model and fair comparisons

The frozen [protocol](../../protocols/compartment-measurement-design.md) was
committed before the first implementation run. It was developed analytically,
not independently preregistered. All parameters are invented. In particular,
the illustrative error `1/60` was deliberately chosen between two derived
boundaries; it is not an observed assay error or an unbiased benchmark sample.

After selecting high-state cells with relative weight `r`, convert fraction
`c` of the selected low-state cells. The final high-state fraction is

```text
q(p;r,c) = [r*p + c*(1-p)] / [r*p + (1-p)].
```

The earlier exact baseline `p=1/5, q=4/5` admits all four worlds below. The
baseline is a latent constraint, not a noisy observation secretly used for
calibration. The new readings have continuous additive uncertainty
`y_a=q_a+b+e_a`: one common offset `|b|<=1/20`, and separately bounded
residuals `|e_a|<=epsilon`. They are bounds, not probability distributions.

| World | Selection r | Conversion c | L: input 1/10 | R: repeat input 1/5 | H: input 2/5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 16 | 0 | 16/25 | 4/5 | 32/35 |
| C25 | 11 | 1/4 | 53/80 | 4/5 | 91/100 |
| C50 | 6 | 1/2 | 7/10 | 4/5 | 9/10 |
| C75 | 1 | 3/4 | 31/40 | 4/5 | 17/20 |

At most two distinct observations may be selected. Exhaustively compare all
six designs from this menu: L, R, H, LR, LH and RH. R is a useful calibration
control, since every world predicts its true value to be 4/5. The primary
question is separation of S from **both** C50 and C75. C25 remains a live
intermediate explanation; it is never silently assigned to either target.
This does not supply a binary diagnosis or a detector of any positive conversion.

## The precision boundary

For the primary target, the exact separation boundaries are:

| Design | Guaranteed primary target separation requires | All-four separation requires | Primary target at epsilon=1/60 |
| --- | --- | --- | --- |
| L | No separation, even at zero residual error | No separation | Unresolved |
| R | No separation, even at zero residual error | No separation | Unresolved |
| H | No separation, even at zero residual error | No separation | Unresolved |
| LR: repeat plus lower input | epsilon < 3/200 = 0.015 | epsilon < 9/1600 | Unresolved |
| RH: repeat plus higher input | epsilon < 1/280 ≈ 0.003571 | epsilon < 3/2800 | Unresolved |
| LH: lower plus higher input | epsilon < 13/700 ≈ 0.018571 | epsilon < 3/448 | Separated |

Each failure means that at least one cross-target pair can produce the **same
observation vector** using permitted offsets and errors. It does not mean every
possible observation is uninformative. Equality at a boundary remains
ambiguous because the uncertainty intervals are closed. The claims apply only
to the declared menu and model.

For LH, the offset-free contrast `q_H-q_L` is `48/175` in S and `1/5` in
C50. Their gap is `13/175`. Each observed contrast can differ from its true
value by `2*epsilon`, so guaranteed separation requires a gap greater than
`4*epsilon`. C75 is farther away. At `epsilon=13/700`, S and C50 both
permit the observations `y_L=67/100, y_H=127/140`: use offsets `2/175`
and `-2/175` respectively and opposite endpoint residuals of magnitude
`13/700`. This exact collision makes the boundary sharp.

The LH error boundary is `26/21` times that of the best repeat-and-shift design
LR: about **24% more tolerated residual error**, under these invented equal-cost
conditions. This modest comparison is the useful increment over the existing
snapshot algebra. It is not a comparison of real laboratory efficiency.

If the target instead requires distinguishing **all four** representative
worlds, the boundary is much smaller: LH requires `epsilon<3/448`, versus
`epsilon<9/1600` for LR. At `1/60`, LH cannot distinguish all four. Their
spacing was chosen for illustration; a finer grid would reduce this secondary
threshold. The calculation never claims exact recovery of continuous parameters
at positive error.

## Does the primary result depend on choosing four points?

There is a narrow continuous extension, supported by algebra rather than
extrapolation from the finite enumeration. On the same exact baseline curve,
take `1<=r<=16` and `c=(16-r)/20`. Then

```text
q_L(r) = (11*r + 144) / [20*(r + 9)]
q_R(r) = 4/5
q_H(r) = (37*r + 48) / [20*(2*r + 3)]

dq_L/dr = -9 / [4*(r+9)^2] < 0
dq_H/dr =  3 / [4*(2*r+3)^2] > 0.
```

Therefore the LH contrast increases strictly with r. Among the entire
material-conversion family `c>=1/2`, equivalent here to `1<=r<=6`, the
closest contrast to S at r=16 occurs at r=6, namely C50. The contrast-gap
argument separates S from this whole family below `13/700`; the C50 collision
at that boundary proves it cannot be improved under this readout model.
This is a written mathematical argument with an independently checked finite
endpoint calculation, not a proof-assistant result or a claim that the finite
checker explored a continuum.

The lower bound on conversion matters. As c approaches zero along this curve,
predictions approach those of S continuously. No fixed positive error permits
uniform discrimination from **arbitrarily small** positive conversion.
Uncertain baseline fractions, extra states, reverse conversion, proliferation,
survival or other processes would require a different analysis.

## Two ways the apparent information disappears

**Different measurement offsets.** Allow a separate offset of at most 1/20
for each action. Even with **zero residual error**, S and C50 can produce
the same complete three-action vector
`(67/100, 4/5, 127/140)`. S uses offsets `(3/100,0,-1/140)` and C50
uses their negatives. Taking more readings in this menu does not repair an
unjustified shared-offset assumption.

**Different selection in each mixture.** Keep conversion zero, but allow
selection weights `(21,16,27/2)` for L, R and H. This model exactly matches
the invariant C50 model's `(7/10,4/5,9/10)` with no offset or error.
These are constructed parameters, not asserted biological rates. More generally,
for any `0<p<1` and `0<q<1`, a zero-conversion model can match that observation
by choosing `r=q*(1-p)/[p*(1-q)]`. Thus arbitrarily many such composition-only
readings cannot identify conversion if selection is allowed to vary freely
for each condition. A model with independently constrained selection is a
different question.

These failures sharpen the research requirement: a later experiment must
establish the relevant shared measurement calibration **and** constrain how
selection changes with input composition. A state-tracking or perturbation
experiment may supply different information, but has its own assumptions; this
calculation neither validates one nor specifies a clinical procedure.

## What the computation adds, and what it does not

The [certificate](../../results/compartment-design-2026-11-13/certificate.json)
retains every design and world pair, exact overlap radii, the eight-point error
table, and constructive collisions. Noise and offset sets are continuous; the
eight displayed error points are not a grid approximation of them. Pair-specific
algebraic radii beyond 1/40 are explicitly marked outside the declared physical
readout range. For all main calculations up to 1/40, readouts remain in [0,1]
without clipping. Clipping would invalidate the simple cancellation equation.

The producer derives radii from prediction differences. The separately written
checker reconstructs the fractions by counting selected/converted weights and
asks whether a shared offset difference can lie in every required interval.
It imports no producer code. For each pair, that interval check is equivalent
to finding any shared observation; it catches overlap between grid points.
It also checks the complete menu, witnesses, fixed contract, artifact hashes
and selected design. Forging a hash cannot make a wrong result pass semantic
reconstruction. A malformed or incomplete artifact supplies no exclusion.

This is small enough for exhaustive exact arithmetic. No Soko dependency,
heuristic solver, learning system or general search framework is justified by
the example. Soko's checked-exclusion approach and the separately represented
certificate pattern from finite-state-proofs informed the checking discipline;
see the [ecosystem assessment](https://github.com/Foundation-0/project-asma/pull/77).
No upstream implementation was copied or executed. The earlier compartment
script already catches snapshot non-identifiability; the new computation adds
measurement-menu comparison, precision boundaries, nuisance controls and a
separately implemented artifact check. It does not establish software speedup,
biological novelty, receptor specificity, natural presentation or injury.

Commands, recorded verification, trust boundaries and execution details are
preserved with the result in [PROOF.md](../../results/compartment-design-2026-11-13/PROOF.md).
The filename follows the repository's result convention; it does not label
this as a formally verified biological system. Internal AI review is not
external scientific peer review. A future empirical question needs a separate
protocol, validated measurement model and the project's existing data and
execution gates.
