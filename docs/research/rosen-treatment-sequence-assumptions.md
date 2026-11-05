# What a treatment-sequence model needs to know about surgery

**Executed 2026-11-05. Original synthetic mathematics, for research review.**
Building on Gu et al. (2021, Barry Rosen coauthor), this experiment identifies a
concrete next research question: **how does residual burden depend on the burden,
composition and anatomy present immediately before surgery?** Two plausible
mathematical removal rules give the same surgery-first observations and different
predictions for the other order. A good fit to one sequence need not resolve that
uncertainty.

The contribution is a reproducible assumption audit and a discriminating study
design. It does not discover a treatment, establish biological novelty, reproduce
the full published model, or recommend a sequence. It is separate from Pilot
001's primary platinum-refractory protein endpoint.

## Published motivation and prior work

[Gu et al., PNAS 2021, DOI 10.1073/pnas.2026663118](https://doi.org/10.1073/pnas.2026663118)
models HGSC dynamics, resistance and treatment sequence. Barry Rosen is linked
in article metadata to Princess Margaret/UHN and Toronto gynecologic oncology;
this is the clinician, not the FIU arsenic biochemist.

The readable [main article](https://pmc.ncbi.nlm.nih.gov/articles/PMC8237655/),
Results sections on predicted treatment outcomes and alternative regimens
(Figures 4 and 5 and the paragraph on reducing neoadjuvant cycles), connects
chemo-associated enrichment to resistant burden when the same number of residual
cancer cells remains after surgery. Its model has much more structure than the
experiment below: stochastic extinction, growth and resistance generation,
recovery gaps, and an inaccessible/unresectable compartment. Resistant cells may
still grow during chemotherapy. Its clinical analyses and survival predictions
have **not** been reanalyzed here. Figure-color descriptions are not used as
scientific evidence.

This modeling question has clear prior art.
[Kohandel, Sivaloganathan and Oza, 2006, PMID 16580022](https://pubmed.ncbi.nlm.nih.gov/16580022/),
[DOI 10.1016/j.jtbi.2006.02.001](https://doi.org/10.1016/j.jtbi.2006.02.001),
explicitly assumes instantaneous fixed-fraction surgery and compares growth and
cell-kill models for sequencing. Its abstract was read; the equations/full text
were not recovered. We do not claim the mathematical observations below are new
to the literature. Our contribution is the independently implemented, inspectable
comparison and its measurement implications for Project Asma.

[Source record](../../registries/rosen-treatment-sequence-sources.json) preserves
access depth, notice checks, identity, rights limits and unsuccessful routes.
Gu's main article was readable once through PMC HTML; subsequent requests returned
a browser challenge. Europe PMC XML failed and the publisher returned 403.
No full texts, supplements, author software or study data are redistributed.
The accessible main article changes the earlier survey's abstract-only access
ceiling; supplementary equations, executable code and dataset rights remain
unverified. Full reconstruction remains deferred.

## The exact comparison

Let `x=(S,R)` contain nonnegative sensitive and resistant burden and `T=S+R>0`.
The invented units have no mapping to patients, cells, doses or tumor diameters.
In the main experiment, chemotherapy is `C=diag(a,b)`, with `0<a<=b<=1`:
selection of existing resistance, without mutation or conversion. Both sequences
receive the same exposure; the endpoint is after both interventions. Surgery is
instantaneous, with no recovery gap or intervening growth. This isolates the
removal rule, not a complete treatment schedule.

Compare two composition-preserving surgery operators:

- Proportional retention: `P_q(x)=q*x`, `0<q<=1`.
- Fixed residual target: `F_K(x)=min(1,K/T)*x`, `K>=0`, with `F_K(0)=0`.
  The cap prevents surgery from adding burden when less than `K` is present.

Set `K=q*T` for the paired comparison. The two models now give the **same**
intermediate state after surgery first, and the same state after subsequent
chemotherapy. This is a constructed observational equivalence, not a fit to data.

For proportional removal, `C(P_q(x))=P_q(C(x))`. Scalar retention commutes with
**any fixed linear map**, even a map containing growth or transitions between
states. Differential but fixed diagonal removal also commutes with diagonal
chemotherapy. Differential removal by itself is therefore not sufficient for an
order effect in that restricted setting. Tests include a selective-removal plus
conversion counterexample to show where that latter conclusion stops applying.

For the fixed-target rule, put `g=sum(C(x))/T>0`. Then

```text
surgery first:  C(F_K(x)) = q * C(x)
chemo first:    F_K(C(x)) = min(1, q/g) * C(x)
ratio of final resistant burden, chemo first / surgery first
    = min(1/q, 1/g), when the compared resistant burden is positive.
```

The same ratio applies to sensitive and total burden. **Final resistant fractions
are identical in the two orders.** Within the contraction grid `g<=1`, the ratio
cannot be below one. Without that assumption it can reverse. The equation also
holds for a general fixed nonnegative linear map with nonzero output; the grid
uses diagonal maps for a simple interpretation.

This means an absolute resistant-burden difference can arise from the amount
removed under an absolute-target rule while the two final mixtures are identical.
It does not imply that chemotherapy generated resistance. It also does not mean
that different sequences can attain the same target in practice. Conditioning
an observational analysis on a postsurgery residual category is conditioning on
a post-treatment variable, with selection/confounding implications; this
controlled mathematical comparison supplies no causal treatment-policy estimate.

## Executed results and retained negatives

The fixed [protocol](../../protocols/rosen-treatment-sequence-assumptions.md)
uses exact rational arithmetic and an 84-case invented grid. No random sampling,
patient rows, statistical inference or model fitting occurs.

| Model/order, main example | Sensitive burden | Resistant burden | Total | Resistant fraction |
| --- | ---: | ---: | ---: | ---: |
| Initial state | 90 | 10 | 100 | 1/10 |
| Proportional retention 1/10, surgery first | 9/10 | 1 | 19/10 | 10/19 |
| Proportional retention 1/10, chemo first | 9/10 | 1 | 19/10 | 10/19 |
| Fixed target 10, surgery first | 9/10 | 1 | 19/10 | 10/19 |
| Fixed target 10, chemo first | 90/19 | 100/19 | 10 | 10/19 |

Here `a=1/10,b=1`. Fixed-target chemo-first resistant burden is `100/19`
(approximately 5.263) times surgery-first burden, while proportional removal gives
exact equality. These are synthetic ratios, not patient effect sizes.

Across all **84** grid cases, proportional surgery gives equal endpoints;
fixed-target surgery gives **54** chemo-first-higher and **30** equal endpoints.
All 84 retain equal final resistant fractions and satisfy the capped formula.
The grid also includes `a=b=1/2`: there is no selective enrichment at all, yet
an active equal-target comparison still produces a twofold common-scale
difference. Thus, enrichment is neither sufficient under proportional removal
nor necessary under a fixed absolute target in this restricted model.
In **31** cases the second sequence's target is above its available burden,
so the cap matters. These are enumerated parameter cases, not independent trials
or evidence about the frequency of outcomes in patients.

Two retained boundary examples prevent overgeneralization:

- Reducing the chemo-first target to **1** while retaining the surgery-first
  target **10** reverses the main example's resistant-burden ratio to `10/19`.
  The crossing point is `K_after/K_before=g=19/100` while both targets are active.
  Neither target's clinical attainability is asserted.
- An explicitly declared post-grid extension permits invented growth under
  treatment: `a=1/2,b=10`, with the same initial state and target 10. Total burden
  grows (`g=29/20`) and the equal-target ratio reverses to `20/29`.
  These are **not** Gu's parameter values. Its resistant-cell growth makes the
  contraction restriction important to state, even if its total burden shrinks.

No survival or extinction result is calculated. Arbitrary fractional burden
cannot establish the probability of zero surviving cells. Equal mean burden
under a linear operation need not imply equal stochastic extinction probability.
The equal-target result is not a decomposition or refutation of the full Gu
model. In particular, a spatially inaccessible compartment, density-dependent
kinetics, gaps and changing treatment effects can invalidate the toy assumptions.

## The next discriminating research question

**Does a pre-specified surgery response map predict residual burden better than
constant absolute residual or constant proportional retention, and does that
choice change treatment-order predictions on held-out observations?**

This is a candidate measurement/design study, not an adopted clinical study.
Its first unit of analysis would be an operation within a clearly defined HGSC
population and treatment era, with a separate protocol for any later causal
sequence comparison. It should compare `K` constant with `q*T_pre` and a limited,
pre-specified map `M(T_pre, anatomical distribution, procedure, sequence)`.
The last model cannot receive unlimited flexibility to win a fit comparison.

| Measurement or design element | What it distinguishes; what remains unresolved |
| --- | --- |
| Quantitative burden immediately before and after surgery, on a consistent assay/scale | Constant `K` predicts flat residual burden across preoperative burden; constant `q` predicts proportional residual. Clinical R0 or millimeter categories are censored/coarse observations, not exact surviving-cell counts. Record limits of detection and measurement error. |
| Anatomical distribution and unresectable sites, operative extent and independent resectability assessment | Separates removal-map effects from inaccessible disease; connects to Gu's explicit inaccessible compartment. Measurement alone does not remove selection bias. |
| Paired composition observations, if a validated assay/definition exists | Tests the composition-preserving assumption. A molecular marker is not automatically a functional resistance label; distinguish pre-existing resistance, selection and newly generated states. |
| Exposure, interval and outcome observation times; treatment history | Tests growth/gap and treatment changes that were suppressed here. Match endpoints and distinguish initial refractory disease from later recurrence. |
| Patient grouping, site separation and pre-specified held-out assessment | Compare burden-prediction error and calibration without fitting to held-out outcomes; retain exclusions/missingness and avoid repeated-patient leakage. No survival superiority follows from this predictive test. |

The two calibrated models agree on all surgery-first observations in the main
example yet disagree for the other order. More observations of that exact same
input/sequence would not separate them. Variation in preoperative burden with
quantitative residual measurements offers a direct discriminating prediction;
composition alone cannot separate this pair. Cross-sequence data can add evidence
but requires explicit handling of selection and confounding.

**Negative result and stop rule:** if residual observations are only broad
categories, burden scales cannot be aligned, anatomy is unmeasured, or the two
maps are indistinguishable at measured precision, report the removal rule as
unresolved and retain both sequence predictions. Do not select a favored model
from survival fit alone. If both simple maps fail held-out checks, that rules out
this simplification and prioritizes spatial/kinetic model development. Obtaining
study data, fitting this map or advancing a clinical claim needs separate
rights, owner execution authorization and scientific review. No authors have
been contacted.

## Reproduce and review

```sh
python3 tools/analyze_treatment_sequence.py > /tmp/asma-sequence-replay.json
cmp /tmp/asma-sequence-replay.json registries/rosen-treatment-sequence-results.json
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

The [machine-readable result](../../registries/rosen-treatment-sequence-results.json)
contains all synthetic cases, parameters, implementation/protocol SHA-256 hashes
and explicit unsupported claims. Python standard library only; no installed
scientific dependency, third-party analysis code execution, network call or random seed is
needed. Recorded local runtime: Python 3.12.14 on Linux x86_64; the experiment and
its eight tests each complete in under a second on this host. Tests check
hand-calculated fractions, the linear null and its boundary, caps/zero burden,
invalid inputs, the exact grid formula, model ambiguity and byte-content replay.
They verify this mathematics/software, not a biological mechanism, source model,
clinical efficacy or permission to acquire data.
