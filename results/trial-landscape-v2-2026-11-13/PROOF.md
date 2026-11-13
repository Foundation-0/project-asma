# Ovarian interventional trial landscape, 2026-11-13 UTC

**Evidence label: VERIFIED, finite metadata count. No mathematical, biological,
or clinical proof is claimed.**

The [dated report](../../docs/trial-landscape-v2-2026-11-13.md) states the
question, the exact requests, the pinned keyword map, the counts, and the
limits. `certificate.json` is the aggregate result. The `snapshot/` pages are
projected API responses that the two offline readers recount, with contact email
addresses in study-page bodies replaced by `[email redacted]` per
`redaction_rule` beside `archive_rule`. They are public registry fields, not
participant rows and not eligibility narratives.

```sh
python3 results/trial-landscape-v2-2026-11-13/verify.py
```

The checker requires the export reader and the recompute reader to agree, the
certificate and the report count block to match that agreement, the SHA-256
manifest to match the post-redaction files, no mailbox email addresses to remain
in study pages, and the pinned as-fetched archive hash to match the pre-redaction
concatenation. It does not establish efficacy, eligibility,
or which NCT identifiers entered or left the recruiting query after 2026-11-05.
That identifier diff is not reconstructable: the 2026-11-05 certificate did not
retain NCT identifiers.

**Not clinical advice and not a treatment recommendation.** Class counts are
registry text matches. They do not say that a study should be joined, that a
drug works, or that a patient resembles the registered population.

**Prior art.** ClinicalTrials.gov supplies the registry and the API. Literal
keyword counting is an ordinary descriptive method. The dated contribution is
this frozen, field-projected pull, the pinned lexicon, the dual offline recount,
and an explicit negative finding on identifier-level comparison with the
2026-11-05 aggregate. No new biological finding is claimed.

**Open obligations.** A later snapshot can name NCT-level changes only if it
keeps identifiers, as this one does. Semantic review of whether a keyword hit
is the study's actual intervention was not done. Live data will move.
