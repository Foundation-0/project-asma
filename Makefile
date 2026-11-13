.PHONY: verify verify-fast verify-trial-landscape certificates

# Offline repository checks. Network audits and container/R execution remain
# explicit commands in their protocols and CI; this target does not run them.
verify: verify-fast

verify-fast: verify-trial-landscape
	python3 results/trial-landscape-v2-2026-11-13/verify.py
	python3 results/tcga-ov-cohort-reconciliation-20261113/verify.py
	python3 tools/validate.py
	python3 tools/check_implementation_hashes.py
	python3 tools/check_tracked_study_sources.py
	python3 -m unittest discover -s tests -v
	node tools/test_research_lab.cjs
	python3 tools/check_site_models.py

verify-trial-landscape:
	python3 results/trial-landscape-2026-11-05/verify.py

# Regenerate byte-integrity pins deliberately; never re-fetch/overwrite a result.
certificates:
	python3 results/trial-landscape-2026-11-05/verify.py --write-manifest
