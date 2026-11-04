"""Transport-independent, immutable measurement and laboratory metadata models."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True, kw_only=True)
class Measurement:
    """One observation. Decimal avoids silently rounding instrument digits.

    Units are *not* automatically converted; a file can contain different units.
    Timestamps must be timezone-aware and are serialized as UTC ISO8601.
    """

    value: Decimal
    unit: str
    stable: bool | None
    protocol: str
    scale_id: str = "scale-1"
    raw_response: str = ""
    timestamp: datetime = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.value.is_finite():
            raise ValueError("A measurement must have a finite value")
        if not self.unit.strip() or not self.protocol.strip() or not self.scale_id.strip():
            raise ValueError("Unit, protocol and scale_id must be non-empty")
        if self.timestamp.utcoffset() is None:
            raise ValueError("The measurement timestamp must include a timezone")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a JSON-serializable dictionary")
        # A fresh copy prevents inadvertent mutation by the original caller.
        object.__setattr__(self, "metadata", json.loads(json.dumps(self.metadata, allow_nan=False)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.astimezone(timezone.utc).isoformat(),
            "value": str(self.value),
            "unit": self.unit,
            "stable": self.stable,
            "protocol": self.protocol,
            "scale_id": self.scale_id,
            "raw_response": self.raw_response,
            "metadata": self.metadata.copy(),
        }

    @classmethod
    def from_dict(cls, record: dict[str, Any]) -> Measurement:
        stable = record.get("stable")
        if isinstance(stable, str):
            mapping = {"true": True, "false": False, "": None, "none": None}
            if stable.lower() not in mapping:
                raise ValueError(f"Invalid stability field: {stable!r}")
            stable = mapping[stable.lower()]
        if stable is not None and not isinstance(stable, bool):
            raise ValueError("stable must be true, false, or null")
        metadata = record.get("metadata") or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        return cls(
            timestamp=datetime.fromisoformat(record["timestamp"]),
            value=Decimal(str(record["value"])),
            unit=str(record["unit"]),
            stable=stable,
            protocol=str(record["protocol"]),
            scale_id=str(record.get("scale_id", "scale-1")),
            raw_response=str(record.get("raw_response", "")),
            metadata=metadata,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class Specimen:
    """Optional metadata associated with a laboratory specimen."""

    specimen_id: str
    project: str = ""
    material: str = ""
    description: str = ""
    operator: str = ""
    conditions: dict[str, str] = field(default_factory=dict)

    def metadata(self) -> dict[str, Any]:
        return {
            "specimen_id": self.specimen_id,
            "project": self.project,
            "material": self.material,
            "description": self.description,
            "operator": self.operator,
            "conditions": self.conditions.copy(),
        }

