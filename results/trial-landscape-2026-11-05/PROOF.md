# Frozen trial-landscape result

**Evidence label: VERIFIED, finite metadata audit. No mathematical or biological
proof is claimed.** The folder name follows the retrieval date in America/Chicago.

The [dated report](../../docs/trial-landscape-2026-11-05.md) states the question,
exact prespecified dictionary, source terms, acquisition interval, counts and
limitations. `certificate.json` is the sole aggregate result; no trial records,
participant data or eligibility narratives are archived. `SHA256SUMS` pins the
certificate, audit implementation, protocol and this offline verifier.

```sh
python3 results/trial-landscape-2026-11-05/verify.py
```

The checker validates the artifact's arithmetic/schema, source-version agreement,
code and protocol hashes, and exact agreement of the report table with the
certificate. It does not reconstruct historical classifications from source
records, establish API snapshot atomicity, validate semantic eligibility, or
verify clinical claims. Hashes provide integrity, not independent evidence.

The new audit's rules were committed before source acquisition; the code was
reviewed and tested on invented records before its live run. This is one new
result PR under issue #58, not an alteration of a previously locked checker or
Pilot 001 protocol. Later checker changes need separate review and must not be
used to silently revise this dated result.

**Prior art / originality:** ClinicalTrials.gov provides the registry and search
API. Literal keyword counting is an ordinary descriptive method. The contribution
is this dated, reproducible aggregate with declared scope; no novelty search or
claim of a new biological finding is made. The historical direction-8 count was
not used as the expected result of this run.

**Open obligations:** independent scientific/semantic evaluation was not done.
Live source changes can prevent an exact later historical replay. The report
lists missing language variants, negation/exclusion limits and search-cohort
ambiguity. A future snapshot or classification validation needs a separately
fixed question. AI assistance and source attribution are disclosed in the report
and CONTRIBUTORS.md.
