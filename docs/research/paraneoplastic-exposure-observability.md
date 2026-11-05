# What the brain records: antigen exposure, treatment order and the missing injury-rate measurement

**Executed 2026-11-05. Original synthetic mathematics plus public literature, for
research review.** This record connects three existing lines of Project Asma
work: the [anti-Yo frontier](../anti-yo-frontier-2026-11-04.md) (recognition and
injury are separate questions), the
[treatment-sequence assumption audit](rosen-treatment-sequence-assumptions.md)
(proportional surgery and chemotherapy commute for tumor burden) and the
[compartment identifiability record](../compartment-identifiability.md) (some
observations cannot choose between mechanisms). It adds the endpoint those lines
leave out: **neural injury that does not reverse**.

It does not model any person, estimate a clinical effect, recommend a treatment
order or claim a new biological mechanism. All model quantities are invented.
Sources are public; no patient-level or private material is used.

## The thread in five statements

1. **The brain integrates.** If an antigen-driven immune response injures
   neurons that are not replaced, final neural loss depends on the *time course*
   of antigen, not on the final tumor burden. In the linear model below it
   depends on the antigen area under the curve, exactly. (VERIFIED algebra;
   biological applicability is CONJECTURE.)
2. **Order can matter for the brain where it provably cannot matter for the
   tumor.** Two schedules with an identical final tumor burden can deliver
   different antigen exposure. Which order minimizes exposure depends on how
   antigen reaches the immune system. Two plausible hypotheses give opposite
   answers in a definable region.
3. **Deficit is a state; "is the attack still active?" asks about a rate.** No
   number of deficit, atrophy or antibody-titer observations answers a rate
   question at the time of measurement. Attack intensity is identifiable only from
   an injury *rate* divided by the remaining target, so it needs both kinds of
   measurement.
4. **A circulating tumor marker is a weighted sum over lesions.** It cannot
   certify that the antigen driving neural injury is falling unless the two
   weightings are proportional.
5. **One measurement series could separate the regimes.** Serial injury-rate
   measurements, anchored to surgery and chemotherapy and compared with
   antibody-negative patients on the same treatment, give different predicted
   signatures for burden-driven, release-driven and autonomous injury. The
   simplest marker candidate, serum neurofilament light, is confounded by both
   treatments; the design must remove that.

## Published premises

| Premise | Source and locator | Limit |
| --- | --- | --- |
| In anti-Yo cerebellar degeneration, "massive loss of PCs" occurs and "the loss of PCs is often very rapid"; CD8 infiltration of the Purkinje layer is an early change. | Venkatraman & Opal 2016, Pathogenesis > Pathology (S125) | Narrative review; mechanism still debated between antibodies and cytotoxic T cells. |
| Antibody titers "may not correlate with symptoms", persist after treatment, and "damage can happen even with titers of antibodies reduced". | Same review, Treatment > Monitoring progress with antibody titers (S125) | Antibody titer is therefore not an injury-rate measurement. |
| Immunotherapies have been "largely ineffective"; one report found only tumor therapy stabilized or improved neurological outcome; treatment within a month was associated with better outcome in one series while "other large series have not found convincing evidence for earlier treatment initiation". | Same review, Treatment and Prognosis (S125) | Conflicting observational evidence; no randomized data. |
| cdr2-specific cytotoxic T cells were expanded in the blood of 3/3 HLA-A2.1+ patients; dendritic cells that engulfed **apoptotic** tumor cells drove a potent killer-cell response; peripheral activation is proposed to contribute to neuronal degeneration. | Albert et al. 1998, abstract (S126) | Three patients; cdr2 rather than CDR2L; proposed, not demonstrated, injury pathway. |
| Ataxia progressed over weeks to months and stabilized within 6 months in all 50 patients; 4/19 anti-Yo patients remained ambulatory; all 7 patients who improved had antitumour treatment with complete remission. | Shams'ili et al. 2003, abstract (S127) | Retrospective; functional states only. |
| Pre-existing paraneoplastic syndromes worsened in 8 of 16 patients after PD-1/PD-L1 blockade. | Manson et al. 2019, abstract (S129) | Mixed tumours and syndromes; supports coupling between immune activation and harm, not its form. |
| Serum neurofilament light (NfL) tracked disease activity "albeit with delay" in anti-NMDA-receptor encephalitis and correlated with CSF NfL. | Brenner et al. 2023, abstract (S128) | Different disease; no anti-Yo NfL cohort was found in our searches (not a claim that none exists). |
| Serum NfL rises with platinum and especially taxane chemotherapy, and was 1.6 times baseline 48 hours after surgery. | Smyth et al. 2026 (S130); Atkins et al. 2026 (S131) | Both standard HGSOC treatment anchors are confounded for serum NfL. |

## The model and its assumptions

Arbitrary units throughout. `A(t)` is tumor burden, `E(t)` an antigen-driven
effector, `N(t)` surviving target neurons and `F(t)` an injury-rate marker.

```text
dE/dt = alpha * u(t) - delta * E          antigen drive u(t) raises the effector
dN/dt = -kappa * E * N                   first-order attack; no replacement
dF/dt = beta * kappa * E * N - lambda * F  marker released by injury, then cleared
```

Two antigen-presentation hypotheses define `u`:

- **Burden-driven:** `u = d * A`. Presented antigen is proportional to living
  tumor burden.
- **Release-driven:** `u = d * A + (burden killed in the body)`. Tumor cells
  killed in place add antigen, as in cross-presentation of apoptotic cells
  (S126). Surgery removes cells from the body without releasing them there.

An **autonomous** variant adds a CNS-resident effector seeded by `E` that
persists without antigen. A **target-exhausted** state has few remaining neurons.
Tumor dynamics are deliberately reduced to instantaneous operations separated by
holding intervals with no growth: the commuting null case of the
treatment-sequence audit. These are research hypotheses, not established anti-Yo
biology.

## Executed results

The [machine-readable result](../../registries/paraneoplastic-exposure-results.json)
records every case. The tool uses exact rational arithmetic, a discrete-time
effector with retention `r` per interval, and no random numbers.

### 1. The exposure identity

Integrating the effector equation gives, for any drive history,

```text
integral of E over [0, T] = (E(0) - E(T) + alpha * integral of u) / delta
N(T) / N(0)               = exp(-kappa * integral of E over [0, T])
```

For two schedules that end in the same tumor state and continue identically,
the effector boundary terms cancel and the cumulative-hazard difference is exactly
`kappa * alpha / delta` times the difference in antigen exposure. Final survival
depends on the schedule **only through exposure**. The discrete analogue,
`(1 - r) * sum(E) = E(0) - E(n) + alpha * sum(u)`, is checked exactly for both
hypotheses. This is the paraneoplastic counterpart of the dose/AUC relation in
pharmacokinetics; its algebra is elementary and not claimed as new.

### 2. Order changes neural exposure while the tumor endpoint cannot change

Worked example: initial burden 100; surgery retains `q`; each of six chemotherapy
cycles retains `1/2`; each operation is followed by one holding interval.

| Schedule | Final burden | Burden exposure | In-body release |
| --- | ---: | ---: | ---: |
| Surgery, then six cycles, `q = 1/10` | 5/32 | 635/32 ≈ 19.8 | 315/32 ≈ 9.8 |
| Three cycles, surgery, three cycles, `q = 1/10` | 5/32 | 2875/32 ≈ 89.8 | 2835/32 ≈ 88.6 |
| Surgery, then six cycles, `q = 3/4` | 75/64 | 9525/64 ≈ 148.8 | 4725/64 ≈ 73.8 |
| Three cycles, surgery, three cycles, `q = 3/4` | 75/64 | 6725/64 ≈ 105.1 | 6125/64 ≈ 95.7 |

The table uses the two pure forms: burden exposure (`u = A`) and in-body release
(`u` = burden killed in place). Moving surgery from position `p` to `p + 1` among
identical cycles changes exposure by exact closed forms:

```text
burden exposure:  A0 * a^p * (a - q)
in-body release:  A0 * a^p * (1 - a) * (1 - q)
mixture d*burden + release:  A0 * a^p * [d * (a - q) + (1 - a) * (1 - q)]
```

- **Burden-driven:** the more effective operation should come first. An adjacent
  exchange argument generalizes this to any operations with any fixed interval
  lengths: ascending order of retained fraction minimizes exposure. Brute-force
  enumeration confirms it on three permutation sets.
- **Release-driven:** release equals initial burden minus final burden minus the
  amount surgery removed. Surgery removes the most when it comes first, so
  surgery-first minimizes release whenever burden does not grow between
  operations. The mass balance holds in all 30 grid cases.
- **Mixture:** the bracket's sign does not depend on `p`, so the optimum is always
  the first or last position, never in between. The criterion predicted the
  optimum in all **150** mixture cases.
- **Disagreement:** the two pure hypotheses recommend opposite positions exactly
  when surgery removes something but retains more than one cycle (`a < q < 1`):
  6 of 30 grid cases. In the worked `q = 3/4` example, delaying surgery lowers
  burden exposure but raises release.

These are statements about an omitted endpoint inside a toy model. They are not
a comparison of primary and interval debulking strategies. Real choices involve
resectability, the surgery response map that the
[treatment-sequence audit](rosen-treatment-sequence-assumptions.md) identifies as
unknown, tumor growth, toxicity and the patient's condition. Kinetic constants are
invented; the hazard differences in the result file show direction and exposure
bookkeeping, not effect sizes.

### 3. State versus rate

Deficit at a visit is the sum of all losses before it, so it is invariant to any
rearrangement of loss timing between visits. An injury-rate marker is weighted
toward recent loss. Example: two visits; in one history 3/10 of the target is lost
just after the first visit and the attack ends; in the other, the same 3/10 is lost
evenly through four steps and continues. Deficits are identical at both visits.
With marker retention 1/2 per step, the marker at the second visit is **3/80**
versus **9/64**, a ratio of exactly **15/4**.

A low injury rate is still ambiguous. A remaining fraction of 9/10 under per-step
hazard 1/90 and a remaining fraction of 1/20 under hazard 1/5 both lose 1/100 per
step: equal markers, **18-fold** different attack intensity. Intensity is
`injury rate / remaining target`, so it needs a rate measurement **and** a state
measurement. This also explains why a clinical plateau (S127) is uninformative
about the attack by itself: the attack may have ended, or the target may be nearly
exhausted.

### 4. A circulating marker cannot certify the antigen that matters

With marker weights `(1, 1)` and drive weights `(1, 3)` over two lesions, burdens
moving from `(10, 2)` to `(4, 5)` lower the marker from 12 to 9 while raising
drive from 16 to 19. In general, opposite-sign changes are possible **if and only
if** the drive weights are not a nonnegative multiple of the marker weights. The
proof's witness `(v·w + w·w) v - (v·w + v·v) w` is checked exactly for every
non-parallel pair on a small grid, and the shared sign is checked for every
parallel pair. Lesion-level antigen measurement, not an aggregate marker, would be
needed to follow drive.

### 5. Regimes after complete antigen removal

In the antigen-driven model, once antigen falls to zero at time `t*`, further
cumulative hazard is bounded exactly by `kappa * E(t*) / delta`: injury is
*committed* by the effector present at removal, and no more. The discrete example
reproduces this bound exactly (7/50). In the autonomous variant, hazard persists
without antigen. Over eight steps after removal, the late-to-early loss-rate ratio
is about **0.0073** in the antigen-driven regime and **0.41** in the autonomous
regime.

### 6. A no-rise theorem and the release signature

Start the effector at its pre-treatment steady state. Under burden-driven
presentation with non-increasing burden, the effector stays at or above the
steady state of the current burden, so hazard **never rises** (72 of 72 schedules).
Under release-driven presentation, the first chemotherapy cycle from steady state
raises hazard if and only if `(1 - a)(1 - d) > 0` (54 of 54 chemotherapy-first
schedules). Surgery never raises hazard (0 of 72). After surgery-first, the effector
is already decaying and the release pulse was masked in **3 of 18** schedules; it
then appears only as a slower decline, which needs denser sampling to detect.

## Why published timing evidence could conflict

**CONJECTURE.** Retrospective series disagree about whether earlier treatment
helps (S125). Under this model, the following would blur such associations:

- Patients may differ in regime. Tumor control protects the brain only in
  antigen-driven disease; pooled with autonomous disease, the effect dilutes.
- Outcomes recorded as functional states saturate. Deficit is `1 - exp(-H)`, so a
  fixed exposure reduction matters less once much of the target is lost; earlier
  treatment can only help while neurons remain.
- Treatment start time is not antigen exposure. Exposure depends on the
  effectiveness and order of operations, and under release-driven presentation a
  first chemotherapy cycle can transiently raise the drive.

Each point is testable only with rate measurements and regime-level
stratification; none is established here.

## A discriminating study design

**CONJECTURE: a proposed design, not an adopted protocol.** Population: patients
with a high-risk onconeural antibody such as anti-Yo and a newly treated associated
cancer, enrolled during the subacute progressive phase, before the plateau.

| Measurement | Purpose |
| --- | --- |
| Serial CSF NfL where clinically obtained, and serial serum NfL | Injury-rate candidate. CSF is expected to be more CNS-specific; serum is more practical. |
| Quantitative cerebellar scale at the same visits | Remaining-target state; with the rate it estimates attack intensity. |
| Exact dates of surgery and every chemotherapy dose, plus tumor-burden measures | Defines antigen-exposure and release events. |
| Antibody-negative comparison patients on the same surgery and regimen | Removes the non-specific NfL response to surgery (S131) and neurotoxic chemotherapy (S130). The anti-Yo-specific signal is the between-group difference. |

| Regime | After maximal debulking | After first chemotherapy cycle | After complete remission |
| --- | --- | --- | --- |
| Burden-driven | Excess falls, with marker lag | Excess falls | Returns to comparator, committed injury bounded |
| Release-driven | Excess falls | Transient excess rise | Returns to comparator |
| Autonomous CNS | No tumor-linked change | No tumor-linked change | Excess persists while target remains |
| Target exhausted | Low throughout | Low throughout | Uninformative |

**Stop rules.** Report the regime as unresolved if: the deficit has already
plateaued; sampling cannot resolve changes on the marker's clearance timescale
(unknown for this setting; one secondary estimate of serum NfL half-life was not
traced to its primary source); the comparator does not match treatment exposure;
or the between-group difference is within measurement variation. A
Purkinje-cell-specific injury marker would remove the confound; none was
identified in our searches. Any study needs its own protocol, ethics approval,
consent and clinical leadership. Nothing here suggests changing anyone's care.

**Why the answer would matter.** If injury proves antigen-driven, the speed and
completeness of antigen removal is the neuroprotective variable, and the
presentation hypothesis decides which order minimizes exposure. If it proves
autonomous, tumor control cannot protect the brain, and only CNS-directed immune
intervention could. Rate measurements anchored to treatment events are the
cheapest observations found here that separate these possibilities.

## Novelty and prior art

The linear-ODE identity, the scheduling exchange argument and the mass balance
are elementary. No novelty is claimed for the mathematics. The contribution is
their connection to the anti-Yo frontier and the treatment-sequence audit, the
explicit disagreement region, the no-rise signature and the confound-aware
measurement design. Searches of Europe PMC and general web search found no anti-Yo
NfL cohort and no published analysis of treatment order against paraneoplastic
neural exposure. That is a bounded search result, not evidence of absence.

## Reproduce and review

```sh
python3 tools/analyze_paraneoplastic_exposure.py > /tmp/asma-exposure-replay.json
cmp /tmp/asma-exposure-replay.json registries/paraneoplastic-exposure-results.json
python3 -m unittest tests.test_paraneoplastic_exposure -v
```

Python standard library only. The tests recompute the worked example by hand,
recheck the adjacent-position and mass-balance formulas on separate inputs,
enumerate the exchange argument independently, replay the discrete identity
against an explicit loop, and compare the artifact byte-for-byte. The Foundation-0
[Virtual Human fork](https://github.com/Foundation-0/virtual-human) integrates the
continuous version of the same model with its reaction engine and compares it
against these exact results and closed forms.

These checks verify mathematics and software. They do not establish that anti-Yo
injury follows this model, that either presentation hypothesis holds, that NfL
measures cerebellar injury in this disease, or that any schedule benefits a
patient. External scientific review has not occurred; label any use of this
record **not externally reviewed**.
