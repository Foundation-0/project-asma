# What a compartment snapshot can identify

**Executed 2026-11-04; synthetic arithmetic only (VERIFIED, V19).** This is an
original implementation of elementary calculations, not a new statistical
method or an empirical discovery. It supports the
[anti-Yo frontier proposal](anti-yo-frontier-2026-11-04.md). No patient values,
TCR sequences, fitted parameters, random seeds, dependencies or network access
are used. The invented direction below is not the direction reported in the
paper. The [source audit](anti-yo-frontier-2026-11-04.md#source-audit) records why
the effective donor count and compartment interpretation need care.

## Counterexample: the same observation supports different mechanisms

Let `p` be the fraction of high-state cells in a blood clonotype. In this toy
model, entry/retention weights high-state cells by `r` relative to low-state
cells; afterward, a fraction `c` of the low-state cells converts to high state.
Assume a closed two-state summary, no reverse conversion and no other processes.
The resulting CSF fraction is:

```text
q = [r p + c (1 - p)] / [r p + (1 - p)]
r = (q - c)(1 - p) / [p(1 - q)]
```

For invented `p = 1/5` and `q = 4/5`, these settings produce exactly the same
observations, even if every cell has the same paired TCR:

| Relative high-state selection `r` | Low-to-high conversion `c` | Observed CSF high fraction |
| --- | --- | --- |
| 16 | 0 | 4/5 |
| 11 | 1/4 | 4/5 |
| 6 | 1/2 | 4/5 |
| 1 | 3/4 | 4/5 |

An independent count construction checks the endpoints: weighting an 80-low /
20-high mixture by 1 and 16 gives 80/320, equivalent to 20/80. Converting 60 of
the original 80 low cells also gives 20/80. These are expected weights, not
observed cell counts or literal estimates of migration rates. Other choices of
`p`, `q`, reverse conversion, sampling, survival or proliferation create further
ambiguities. The example concerns this summary; it does not prove that all
possible longitudinal, functional or transcriptomic measurements are uninformative.
Nor does it cover models with independently justified common parameters across
donors or clones. The table illustrates the `r >= 1` family; allowing depletion
(`r < 1`) extends the compatible conversion range.

**Design consequence (CONJECTURE):** a shared-clone state contrast can reject
a narrowly specified *state-independent sampling with no state change* model.
It cannot, by itself, distinguish local conversion from state-dependent entry,
retention or survival. Pseudotime does not supply the missing observation of
movement. Time-resolved tracking and antigen/presenting-cell perturbations would
provide different information, subject to their own assumptions.

**What additional information could help:** in this model
`c = q - r p(1 - q)/(1 - p)`. An independently justified bound `1 <= r <= 4`
would constrain the invented example to `0.60 <= c <= 0.75`, whereas allowing
`r = 16` permits zero conversion. The script verifies this bound. No such
recruitment/retention bound is established for the study. This illustrates the
value of an additional measurement rather than selecting a favored explanation.

## Resolution of an exact paired sign-flip check

Under independent donors and a null permitting exchangeable signs of the paired
effects, enumerate all `2^n` sign patterns for the sum statistic. The smallest
conventional two-sided tail includes the observed extreme and its sign reverse:

| Independent informative pairs | Sign patterns | Smallest one-sided tail | Smallest two-sided tail |
| --- | --- | --- | --- |
| 3 | 8 | 1/8 = 0.125 | 2/8 = 0.25 |
| 6 | 64 | 1/64 = 0.015625 | 2/64 = 0.03125 |

These bounds apply to this **specific unrandomized exact test**, with nonzero
effects and the stated null. They are not universal bounds on p-values, effect
sizes or what a three-donor study can reveal. They do not invalidate another
study's different tests, including three-case versus six-control comparisons.
Sign exchangeability is an assumption, not randomization supplied by observing
blood and CSF. More cells improve measurement of sampled donors;
they do not create additional independent donors. A valid, explicitly modelled
hierarchical analysis can use cell measurements, but its assumptions and
population uncertainty must remain visible. Small cell-level p-values
cannot be substituted for this donor-level question.

**Design consequence (CONJECTURE):** report donor effects, coverage and
leave-one-donor-out sensitivity. Do not set a conventional two-sided `p < .05`
success criterion for this three-pair exact check. Pooling donors across
incompatible compartments to reach six changes the question.

## Missing a blood clone is plausible even without compartment restriction

In an illustrative independent-sampling model, a clone with true frequency
`f = 1/1000` has probability `(1 - f)^1000 = 0.367695425` of being missed in
1,000 draws. Real cell capture may violate those assumptions. This calculation
shows why an unobserved blood counterpart alone is inadequate evidence of a
CSF-exclusive clone, local expansion or a migration direction.

## Reproduction and limits

Run from the repository root:

```sh
python3 tools/analyze_compartment_identifiability.py
```

The command uses standard-library rational arithmetic, enumerates every sign
pattern, and fails if endpoint counts or theoretical tail bounds disagree.
It prints the four counterexamples, both exact-test bounds, the hypothetical
selection-bound calculation, and the sampling
example. It writes no files. These are the executed results above; no study-data
analysis has run. The purpose is to avoid an unidentifiable research claim and
choose measurements that could distinguish the competing explanations.

**See also (2026-11-05):** the [exposure and observability record](research/paraneoplastic-exposure-observability.md)
gives a related identifiability result for neural injury: equal deficits allow
different recent injury rates, and equal injury rates allow different attack
intensities.
