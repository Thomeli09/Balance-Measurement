"""A&D GX-A/GF-A standard output mode (ST/US status frames)."""

from __future__ import annotations

import re

from balance_measurement.utils.decimals import decimal_from_device
from balance_measurement.core.exceptions import ProtocolError
from balance_measurement.scale.protocols.base import Reading, ScaleProtocol

_WEIGHT = re.compile(
    r"^(?P<status>ST|US),\s*"
    r"(?P<number>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*"
    r"(?P<unit>[A-Za-z%]+)\s*$"
)


class ADWeighingProtocol(ScaleProtocol):
    name = "a-and-d"
    read_command = b"Q\r\n"
    tare_command = b"T\r\n"
    zero_command = b"ZR\r\n"
    max_response_lines = 5

    def parse_reading(self, line: str) -> Reading | None:
        frame = line.strip()
        if frame.startswith(("EC,", "OL,")):
            raise ProtocolError(f"A&D instrument error/overload: {frame}")
        match = _WEIGHT.fullmatch(frame)
        if match:
            return Reading(
                value=decimal_from_device(match["number"]),
                unit=match["unit"],
                stable=match["status"] == "ST",
            )
        if frame.startswith(("ST,", "US,")):
            raise ProtocolError(f"Invalid A&D weight frame: {frame}")
        return None

    def required_acknowledgements(self, operation: str) -> int:
        # Depends on AK settings. An unacknowledged command is never marked as successful.
        return 2

    def acknowledgement(self, operation: str, line: str) -> bool | None:
        response = line.strip()
        if response in ("AK", "\x06"):
            return True
        if response.startswith("EC,"):
            return False
        return None
