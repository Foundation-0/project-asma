# Identifiability and C20 certificate, v1 archive (2026-11-13)

This folder keeps the certificate whose SHA-256
`366a230dbcf8f8a253bc4d0bd14a6ae91ce54e66d019cbd0c7454abde9e73923` is cited in issue #82 and PR #83.
It came from the 2026-11-13 vault drop together with its generator.

- `identifiability_and_c20_certificates.json` is the certificate, byte for byte.
- `generator_v1.py` is the generator, byte for byte.
- `verify.py` runs the generator in a temporary directory and checks that the output matches the committed file.

Run `python3 results/identifiability-and-c20-2026-11-13/verify.py`.

## Status of its contents

This is an archive of what the v1 generator produced. The maintained checks are
`formal/AsmaIdentifiabilityProofs.lean` and `tools/verify_identifiability_and_c20.py`.
Two parts of the v1 output are superseded:

- Its C20 section weights within-fold pairs by 863, an alignment with fold sizes 28 and 26.
  The balanced split used now gives 862.
- Its `constructive_exact_3491_witness` is the first simulated draw with U = 3491 after rho was
  fitted from 3491 and 0.83. That is a fitted consistency check and makes no prediction.
  C20 stays a CONJECTURE in `CLAIMS.md`.

For the (1/10, 2/5) and (1/20, 3/8) designs, the v1 C25 and C50 ceilings and the (1/20, 3/8) C75 ceiling
match the Lean module and the maintained script.
