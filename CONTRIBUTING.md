# Contributing

Start with the [roadmap](docs/roadmap.md) and a
[research question](templates/research-question.md). Keep changes small and
reviewable. Cite primary evidence, verify corrections, and record access dates.
Use [experiment records](templates/experiment.md) to distinguish proposals from
executed work. Include negative findings and explain deviations from the protocol.

Claim labels (Foundation-0 [repository standard](https://github.com/Foundation-0/.github/blob/main/REPO-STANDARD.md)):

- **PROVEN** — written proof in-repo
- **VERIFIED** — finite check with a recorded re-run command (not a proof)
- **KNOWN** — cited primary source with exact citation
- **CONJECTURE** — hypothesis or open target; "not found" is never "new"

Some notes add qualifiers taken from Foundation-0/aletheia
([`spec/LAWS_AND_GATES.md`](https://github.com/Foundation-0/aletheia/blob/a07d7db02018ab852d7653f08678ee7c692f3a33/spec/LAWS_AND_GATES.md)
at `a07d7db`: Law 4 and sections 2.2, 2.3 and 4). They qualify one of the four
labels, never replace it, and never create a ledger row.

- `N0`: known, textbook or repackaged work. It is the default; a higher novelty
  grade needs a recorded full-text prior-art search by mechanism.
- `exact`: a proof, symbolic identity, per-input certificate or exhaustive finite
  enumeration. `sampled`: a finite check on seeded, random or grid inputs. Exact
  arithmetic does not make a check `exact`: random inputs decided in exact
  rationals are still `sampled`.
- Uncompiled source (`uncompiled_source`): Lean or other formal source that the
  pinned CI toolchain has not compiled yet. It is not verified until that job passes.
- R3 and R4 (gate-integrity contracts). R3: a checker accepts one spelling of each
  checked value, and re-spelling a value (`1` for `true`, a float, a trailing
  newline, a duplicate JSON key) never turns a rejection into an acceptance. R4:
  the same exit code and standard output under `python3 -I -B`,
  `python3 -I -O -B` and `python3 -I -B -W error`, with no bare `assert` guarding
  a check and no test skipped under `-O`.
- "External claim, not re-checked here": a statement taken from another
  repository and not re-run here (aletheia's provenance tag `source_claim`).

Record new public claims in [CLAIMS.md](CLAIMS.md). Disclose AI assistance and
models in the pull request and update [CONTRIBUTORS.md](CONTRIBUTORS.md) when credit
changes.

An "independent" reader or checker is a separately written code path that does
not import the producer. Unless a ledger row says otherwise, treat producer and
checker as coming from the same contributor stream; their agreement is not
external review ([roadmap](docs/roadmap.md) Q4). This is separate from patient
independence.

When a change narrows, downgrades or removes a claim, record a second pass in the
pull request: the first-pass text; who did the second pass (a person, or an agent
and its model, not the first-pass author); the rebuild command, commit and output
SHA-256; the sources read (full text, section only or not obtained, with access
dates); the ruling, `stands`, `stands_narrowed` or `falls` (aletheia Gate 10); the
strongest surviving claim with its label; and the words "not externally
reviewed". The first such case is the trace-slack threshold (Check 4) in
[`studies/expedition-mobius-ropt/README.md`](studies/expedition-mobius-ropt/README.md).
The outside check in Foundation-0/cave-expedition found that it is not an exact
law, and its second pass ruled that finding `stands_narrowed`: the threshold is a
conservative first-order sufficient condition, not the exact crossing
([`verification/outside/rulings.json`](https://github.com/Foundation-0/cave-expedition/blob/9729839b6c021f7db6416053f3d72f43ad9c47e5/verification/outside/rulings.json)
at `9729839`, area `twoloop-stack`, finding F5). By that check's own account its
observer is a team of AI agents and no human reviewed it, so it is not external
review here.

Before submitting:

1. Follow the [data and reproducibility rules](docs/reproducibility-and-data.md).
   Inspect `git diff --cached` for private context, data, and secrets.
2. Update registry records when adding a source or dataset. Check reuse terms;
   third-party study files keep their own licences ([NOTICE](NOTICE)).
3. Run `python3 tools/validate.py` and
   `python3 -m unittest discover -s tests -v` from the repository root.
4. Explain the question, evidence class, methods, checks actually run, unrun
   stages, and limitations in the PR. Avoid clinical advice and performance hype.

Keep patient independence, leakage prevention, assay effects, and uncertainty
explicit in analysis reviews. Do not recruit partners, contact third parties,
import sensitive data, create a large issue backlog, or change repository
settings as part of routine scaffold work.
