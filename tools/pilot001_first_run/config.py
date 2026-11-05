"""Typed run configuration for Pilot 001 first-run orchestration."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "registries/pilot-001-first-run-input-manifest.json"

HOSTS = frozenset({"linux-ci", "macos"})


@dataclass(frozen=True)
class InputPin:
    role: str
    sha256: str
    bytes: int

    def to_dict(self) -> dict[str, Any]:
        return {"role": self.role, "sha256": self.sha256, "bytes": self.bytes}


@dataclass(frozen=True)
class RunConfig:
    host: str
    output_dir: Path
    dry_run: bool = True
    gate0_signed: bool = False
    gate0_attestation_ref: str | None = None
    dropbox_cleared: bool = False
    input_manifest: tuple[InputPin, ...] = field(default_factory=tuple)
    git_sha: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["output_dir"] = str(self.output_dir)
        payload["input_manifest"] = [pin.to_dict() for pin in self.input_manifest]
        return payload


def default_input_manifest() -> tuple[InputPin, ...]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pins = []
    for item in data["inputs"]:
        pins.append(InputPin(item["role"], item["sha256"], int(item["bytes"])))
    return tuple(pins)


ATTESTATION_REF = re.compile(
    r"^(?P<id>[A-Za-z0-9._-]+):(?P<date>\d{4}-\d{2}-\d{2})$"
)


def parse_attestation_ref(ref: str | None) -> tuple[str, str] | None:
    if not ref:
        return None
    match = ATTESTATION_REF.fullmatch(ref.strip())
    if not match:
        return None
    return match.group("id"), match.group("date")


def load_config_json(path: Path) -> RunConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("host") not in HOSTS:
        raise ValueError("invalid run config")
    pins = []
    for item in data.get("input_manifest", data.get("inputs", [])):
        pins.append(InputPin(item["role"], item["sha256"], int(item["bytes"])))
    return RunConfig(
        host=data["host"],
        output_dir=Path(data["output_dir"]),
        dry_run=bool(data.get("dry_run", True)),
        gate0_signed=bool(data.get("gate0_signed", False)),
        gate0_attestation_ref=data.get("gate0_attestation_ref"),
        dropbox_cleared=bool(data.get("dropbox_cleared", False)),
        input_manifest=tuple(pins) if pins else default_input_manifest(),
        git_sha=data.get("git_sha"),
    )
