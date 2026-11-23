# Compartment measurement design under shared measurement bias

Version 1, 2026-11-13 UTC. Original synthetic mathematics, specified locally
before the first implementation run; not independently preregistered. The
illustrative operating error was deliberately chosen after analytical design
to fall between two design boundaries. It is not a measured assay error.

## Question and decision

Can two altered input mixtures distinguish selection without conversion from
substantial conversion when a shared measurement offset makes either individual
reading ambiguous? How does the answer change with measurement precision and
with the assumption that the offset and mechanism remain shared?

This extends the existing [compartment counterexample](../docs/compartment-identifiability.md).
That example already shows snapshot ambiguity and the value of an independently
bounded selection ratio. Merely reproducing it or wrapping it in a solver would
add no result. This experiment must supply exact separation boundaries,
constructive overlap witnesses, and a comparison with repeating the original
mixture to calibrate the offset. The work serves experimental-design reasoning
for the frontier track; it does not replace Pilot 001 or establish a biological
mechanism. It needs no study files, patient inputs or third-party analysis code.

## Fixed model and complete finite menu

Retain the original idealized closed two-state model: select high-state cells
with relative weight `r`, then convert fraction `c` of selected low-state cells:

```text
q(p;r,c) = [r*p + c*(1-p)] / [r*p + (1-p)].
```

No reverse conversion, proliferation, death, input measurement error or other
processes are modeled. Parameters and mixtures are invented, not estimated.
The baseline `p=1/5, q=4/5` is an exact latent constraint, not a new noisy
observation or patient measurement. It defines four representative worlds:

| ID | r | c | Target group |
| --- | ---: | ---: | --- |
| S | 16 | 0 | zero conversion |
| C25 | 11 | 1/4 | intermediate; retain, do not assign to either target |
| C50 | 6 | 1/2 | material conversion |
| C75 | 1 | 3/4 | material conversion |

The three candidate observation actions are `L: p=1/10`, `R: p=1/5`
(repeat baseline), and `H: p=2/5`. Both `r` and `c` must stay fixed across
actions in a given world. Budget is at most two distinct actions: enumerate
exactly `L`, `R`, `H`, `LR`, `LH`, `RH`. There is no claim of optimality over
other input fractions, assays, biological models or laboratory costs. Each
action costs one invented observation unit; an action is shared across every
pair it distinguishes, so pairwise costs must not be added.

For each action `a`, the readout is `y_a=q_a+b+e_a`. One common additive offset
`b` lies anywhere in the continuous closed interval `[-1/20,1/20]`.
Each residual error `e_a` independently lies anywhere in `[-epsilon,epsilon]`.
These are adversarial bounds, not random errors, confidence intervals or error
probabilities. The same observed vector can have different nuisance values
under competing explanations. No clipping or rounding is applied. Check that
all readouts remain in `[0,1]` throughout `0<=epsilon<=1/40`; beyond that domain
no guarantee is reported. The main illustrative error is `epsilon=1/60`.
Offsets/errors are continuous, never replaced with a finite grid.

Primary target: all observation sets of S must be disjoint from those of both
C50 and C75. An overlap for either pair makes the target unresolved. C25 remains
a live intermediate explanation and prevents a binary clinical interpretation.
Secondary target: pairwise discrimination of all four representative worlds.
Report both targets for all six designs and their exact maximum-error
boundaries. Strict separation requires error below the boundary; equality
counts as overlap. The all-four boundary depends on the chosen world spacing;
it cannot show exact parameter recovery from continuous biological parameters.

Also tabulate the deliberately chosen error points `0`, `1/280`, `9/1600`,
`3/448`, `3/200`, `1/60`, `13/700`, `1/40`. The eight-point table is a
presentation aid, not a discretization of the continuous uncertainty sets.
Individual-pair algebraic overlap radii may exceed `1/40`; label those as
outside the declared physical readout range. Their algebraic witnesses may be
checked at their stated radius, but do not extend the bounded measurement
guarantee. The two overall targets and the main boundary witness remain within
the declared range.

As a written analytic sensitivity check, consider the continuum
`1<=r<=16, c=(16-r)/20` on the same exact baseline curve. Determine whether
the primary separation from `c>=1/2` (`1<=r<=6`) follows from endpoint bounds.
Do not infer separation from arbitrarily small positive conversion or interpret
the finite enumeration as exhaustive over that continuum. Monotonicity, if
used, must be established algebraically in the report.

## Calculation and independent checking

The original standard-library producer enumerates every admitted design and
world pair using rational arithmetic. Derive the critical error from the
range of pairwise prediction differences and the offset bound. A separately
written checker must reconstruct predictions from selected/converted low/high
weights and check continuous common-offset feasibility by interval
intersection, without importing the producer or its helpers. The checker
enumerates the full menu, validates every retained scalar and boolean, and
checks a constructive observation collision at a boundary. Both implementations
trust the stated model and Python rational arithmetic; this is neither a proof
assistant nor an independent biological validation.

Certificate schema version 1 has contract ID `asma-compartment-design-v1`,
status `complete`, exact protocol/producer paths and SHA-256 hashes, complete
contract inputs, all predictions, all six design results, selected minimum-cost
target-separating designs, and the controls below. Fractions are canonical
strings; booleans are actual JSON booleans. The checker fixes the model and
input universe independently: a self-consistent rehash of changed data must
not silently redefine the question. Missing, extra, duplicated, malformed or
revision-mismatched inputs invalidate the certificate. A hash is an integrity
check, not evidence that a result is mathematically correct.

Only a complete check can support separation. Incomplete enumeration, exception,
resource limit, or timeout supplies no exclusion or impossibility result. The
CLI must fail closed; tests must exercise a truncated/forged complete artifact.
Exhaustive comparison is cheap here (four worlds, six designs, six unordered
pairs); no search dependency, heuristic pruning or solver speedup is needed.

## Required retained controls

1. Recover all four baseline values and the earlier no-extra-measurement
   ambiguity. Compare each singleton with every two-action design, including
   `LR` and `RH`: repeating the baseline is a valid offset-calibration action.
2. Validate an exact same-observation witness for S and C50 at the `LH`
   critical error, with both biases and every residual error within bounds.
   Test strict separation just below it and overlap at and above it.
3. Replace the shared offset with independent per-action offsets, each still
   in `[-1/20,1/20]`. At zero residual error, preserve an explicit S/C50
   collision across all three actions. This is a changed model, not the main
   certificate's conclusion.
4. Relax the shared-mechanism assumption. The zero-conversion rule with
   `r_L=21, r_R=16, r_H=27/2` matches the shared C50 world at every action.
   Record this exact countermodel with zero offset/error; no plausibility
   or measured selection rates are asserted.
5. Corrupt a prediction, threshold, target flag, selected design, witness,
   contract/model revision, and enumerated menu. Rehash a forged payload where
   applicable: independent semantic checking must still reject it. Keep a known
   valid certificate accepted. Test boundary-touching and continuous overlap,
   not just point equality or sampled error grids.

## Value, limits and stop rules

Proceed only if the result adds a quantified precision/invariance boundary to
the existing algebra. Report the improvement over repeat-plus-one-shift, not
only over single observations. If simple exact interval checks solve it, use
them: no generic search framework is justified by this example. Keep the whole
calculation and tests below five minutes on the current host; stop expansion
if the semantics cannot be stated or checked within this bounded task.

The result cannot establish that controlled mixtures are attainable, that
selection/conversion stay invariant when composition changes, that an assay
has shared additive bias, or that the stated error bounds apply. It cannot
establish receptor specificity, natural antigen presentation, injury mechanism,
patient outcomes or a treatment choice. The direction of the invented contrast
is not assigned to the cited biological study. A future experiment needs its
own validated state definition, measurement/error model, biological controls,
protocol, rights and applicable execution/scientific review gates.

No claim of new-to-literature methodology is planned. Common-offset
cancellation and set-based identifiability are elementary ideas. Method
attribution: the [Soko checked-search assessment](https://github.com/Foundation-0/project-asma/pull/77)
motivates rejecting unchecked exclusions; the
[finite-state certificate pattern](https://github.com/Foundation-0/finite-state-proofs/tree/9eeb3da2cdd6ba6b100ac24d23b32c369c0db8ec)
motivates a separately represented checker. All implementation here is original;
neither project's code is copied, installed or executed.
