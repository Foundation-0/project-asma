# Contributing

Start with the [roadmap](docs/roadmap.md) and a
[research question](templates/research-question.md). Keep changes small and
reviewable. Cite primary evidence, verify corrections, and record access dates.
Use [experiment records](templates/experiment.md) to distinguish proposals from
executed work. Include negative findings and explain deviations from the protocol.

Before submitting:

1. Follow the [data and reproducibility rules](docs/reproducibility-and-data.md).
   Inspect `git diff --cached` for private context, data, and secrets.
2. Update registry records when adding a source or dataset. Check reuse terms;
   no project license grant has been chosen.
3. Run `python3 tools/validate.py` and
   `python3 -m unittest discover -s tests -v` from the repository root.
4. Explain the question, evidence class, methods, checks actually run, unrun
   stages, and limitations in the PR. Avoid clinical advice and performance hype.

Keep patient independence, leakage prevention, assay effects, and uncertainty
explicit in analysis reviews. Do not recruit partners, contact third parties,
import sensitive data, create a large issue backlog, or change repository
settings as part of routine scaffold work.
