"""Host-side owner attestation verification before networked fetch."""

from __future__ import annotations

from pilot001_first_run import failure_codes as codes


def verify_owner_attestation_on_host(attestation_id: str) -> str | None:
    """Run the same attestation gate as parse_sources, on the host before phase 1."""
    try:
        from source_data_adapter import _check_attestation

        _check_attestation(attestation_id)
        return None
    except Exception:
        return codes.P001_FAIL_SOURCE_AUTHORIZATION
