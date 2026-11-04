"""Read portable TOML configurations using the Python standard library."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from balance_measurement.acquisition import AcquisitionSettings
from balance_measurement.scale.transport import SerialSettings


@dataclass(frozen=True, slots=True)
class AppConfig:
    serial: SerialSettings
    protocol: str = "mettler-toledo"
    scale_id: str = "scale-1"
    acquisition: AcquisitionSettings = field(default_factory=AcquisitionSettings)
    outputs: tuple[Path, ...] = (Path("measurements.csv"),)

    def __post_init__(self) -> None:
        if not self.protocol.strip() or not self.scale_id.strip() or not self.outputs:
            raise ValueError("protocol, scale_id and at least one output are required")
        if len(self.outputs) != len(set(self.outputs)):
            raise ValueError("Duplicate output paths are not allowed")


def load_config(path: str | Path) -> AppConfig:
    """Load TOML. Output paths are resolved relative to the TOML file."""
    source = Path(path).resolve()
    with source.open("rb") as stream:
        data: dict[str, Any] = tomllib.load(stream)
    serial_config = dict(data.get("serial", {}))
    if "response_terminator" in serial_config:
        option = serial_config["response_terminator"]
        terminators = {r"\n": b"\n", r"\r": b"\r", r"\r\n": b"\r\n"}
        if option not in terminators:
            raise ValueError("response_terminator must be \\n, \\r or \\r\\n")
        serial_config["response_terminator"] = terminators[option]
    outputs = tuple(
        (source.parent / Path(value)).resolve()
        for value in data.get("outputs", ["measurements.csv"])
    )
    acquisition = AcquisitionSettings(**data.get("acquisition", {}))
    return AppConfig(
        serial=SerialSettings(**serial_config),
        protocol=str(data.get("protocol", "mettler-toledo")),
        scale_id=str(data.get("scale_id", "scale-1")),
        acquisition=acquisition,
        outputs=outputs,
    )
