# Evidence graph: separating recognition from injury

**2026-11-05. VERIFIED — bounded software result; biological mechanisms remain
unresolved.** The [Virtual Human proposal](virtual-human-research-fit.md) now has
an executable, offline prototype. It uses the unchanged MIT-licensed graph core
from [Rohan Arun's Virtual Human](https://github.com/rohanarun/virtual-human/tree/3d75e8e25d6f3fec08e1ccecd424532bccaa1b82)
and original Asma rules for matching evidence to a question. Shared graph work
lives in [Foundation-0/virtual-human](https://github.com/Foundation-0/virtual-human).

## Executed result

The [registry](../registries/anti-yo-evidence-graph.json) contains **24 curated
public evidence assertions and 22 request fixtures** from existing reviews.
These are not 24 independent observations or patients: some records summarize
methods, grouped catalog annotations or an explicitly labeled design inference.
The assertions retain source IDs, locators, entity identities, measurement scope,
evidence kind, polarity and unresolved attributes. No new study files were
acquired and no patient records were used.

| Result on the curated requests | Count | Meaning |
| --- | ---: | --- |
| Supported within scope | 6 | At least one encoded assertion matches the requested conjunction; its full actual context is returned. |
| Counterevidence | 1 | A negative result matches the particular tested endpoint and scope. |
| Unresolved | 15 | The selected evidence does not support that requested claim; absence of support is not evidence of absence. |

All 22 cases match their manually specified expectations. This is a regression
benchmark, **not** an independently labeled scientific accuracy estimate. Thirteen
new tests also check invalid transfers, contradictory artificial evidence,
permutation invariance, duplicate observation identities, source references and
the exact hashes of the vendored code and license. The repository's 227 Python
tests pass. These checks do not verify the truth or completeness of the curation.

The useful addition over the Markdown tables is repeatable rejection of a false
join. CDR2L, HLA-II, and a glioblastoma model each appear in the selected catalog
records, but never as that whole conjunction in one record. Combining marginal
matches would manufacture an apparent observation. The tool requires one record
to satisfy the full request and reports which fields fail. It also retains a
finite negative epitope screen without turning it into a universal absence of
autoreactivity. Manual tables remain the authoritative interpretive baseline;
this prototype has not been compared with human review in a blinded study.

## What this changes in the frontier question

**CONJECTURE — research organization, not a discovered mechanism:** recognition
and injury need separate axes. A receptor recognizing a CDR2L-derived ligand
could still cause indirect injury. Conversely, determining a ligand's origin
does not establish neural damage. The earlier three-explanation diagram remains
useful as a map, but its rows should not become mutually exclusive categories.

| Axis | Possibilities retained | Most consequential missing evidence |
| --- | --- | --- |
| Recognition/source dependence | Direct CDR2L ligand; partner/cargo ligand; altered cellular state or antigen supply | Unique source assignment, an identified receptor/ligand/HLA relationship, natural processing, and separation of delivery from global cell/presentation effects |
| Effector consequence | Direct target recognition; indirect injury; no demonstrated injury in a competent tested system | Injury measured independently of activation, with context-matched evidence separating upstream activation from target recognition and downstream effects |

The direct-ligand checklist retains the human CDR2L-associated HLA-II annotation
(E02/E03; sources S110–S112). **Unique source attribution and naturally processed
recognition by a defined anti-Yo CD4 receptor remain unresolved.** The tool does
not rank this explanation above another by counting fulfilled checklist items.
The checklist requirements themselves are proposals, not sufficient causal
identification criteria or a jointly observed experimental system.

The next high-value research direction is therefore still **adjudicating ligand
origin and receptor recognition while preserving alternatives**. Sequence/source
ambiguity, catalog restriction assumptions and actual assay context should be
resolved before assigning a CDR2L-specific receptor mechanism. A whole-protein
knockout/rescue result alone cannot separate ligand origin, protein function,
cell health and antigen delivery. Proposed selective comparisons should retain
those controls and an unrelated-antigen comparison; they need domain review and
their own execution authorization before becoming experiments.

Separately, a proposed injury comparison must hold upstream activation comparable
while testing target-recognition dependence and independently measuring injury.
The multiple-sclerosis astrocyte observation in S105 has its own activation and
target context; it does not establish anti-Yo Purkinje injury or exclude every
recognition route. No numerical rate or probability is invented to join these
missing relationships.

## Shared development with Virtual Human

Asma currently imports only the **graph container and schema**, vendored as an
unchanged, hash-pinned file with the upstream copyright and full MIT notice.
See [provenance](../tools/vendor/virtual_human/provenance.json) and [NOTICE](../NOTICE).
It needs only Python's standard library. Updating that pin requires reviewing
the diff and rerunning the evidence benchmark; it is not a floating dependency.

Two reusable contributions are prepared in the Foundation-0 fork:

1. Correct graph clearance reporting that combined hepatic blood and renal plasma
   reference bases. Exported clearances now use an explicit plasma reference;
   independent mass-balance checks also distinguish a reported parameter sum
   from effective IV dose/AUC clearance. The PBPK equations are unchanged.
2. Add an opt-in registry for named model edges, with explicit scalar quantities,
   units, reference bases, exact declared contexts, bounds and provenance. Invalid
   inputs stop before a callable runs. This is infrastructure for reviewed models,
   not an implemented anti-Yo model or automatic biological validation.

This gives a practical two-way workflow: Asma supplies concrete failure cases;
the fork receives general graph improvements; Asma adopts only reviewed parts
needed for its research. Contributor access to the original repository is being
arranged by the owner. Upstream submission remains a separate, explicitly tracked
step; a Foundation-0 PR is not an upstream acceptance.

## Reproduce and interpret

From this repository root:

```bash
python3 tools/evidence_graph.py
python3 tools/evidence_graph.py --json
python3 -m unittest discover -s tests -p test_evidence_graph.py -v
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

Queries are existential metadata lookups. Omitting an assay, population or other
context field does not generalize the evidence: the full matched context is
returned, and the caller must request every distinction needed for the claim.
The tool cannot discover an omitted confounder, authenticate a source, verify
cohort independence or make a causal inference. Contradictory matching assertions
are preserved as `conflicting`; they are not resolved by majority vote. Unknown
values remain unresolved rather than defaulting to zero or one.

**Decision:** continue this bounded prototype and shared graph work. Defer a
whole-body disease simulator: no implemented middle-scale model currently supplies
the missing ligand, receptor and injury evidence. Independent domain review and a
real curation task should determine whether the prototype earns continued use.
This software result changes neither Pilot 001 nor its data/execution gates.

Prepared with OpenAI Codex and independent internal agent review. Internal review
is not external scientific validation.
