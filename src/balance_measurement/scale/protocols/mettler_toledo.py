"""MT-SICS protocol (confirm commands supported by your specific balance)."""

from __future__ import annotations

import re

from balance_measurement.utils.decimals import decimal_from_device
from balance_measurement.core.exceptions import ProtocolError
from balance_measurement.scale.protocols.base import Reading, ScaleProtocol

_WEIGHT = re.compile(
    r"^(?:S|SI)\s+(?P<status>[SD])\s+"
    r"(?P<number>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s+"
    r"(?P<unit>\S+)$"
)


class MettlerToledoProtocol(ScaleProtocol):
    name = "mettler-toledo"
    read_command = b"SI\r\n"
    tare_command = b"T\r\n"
    zero_command = b"Z\r\n"
    max_response_lines = 5

    def parse_reading(self, line: str) -> Reading | None:
        frame = line.strip()
        match = _WEIGHT.fullmatch(frame)
        if match:
            return Reading(
                value=decimal_from_device(match["number"]),
                unit=match["unit"],
                stable=match["status"] == "S",
            )
        if frame.startswith(("S ", "SI ", "ES", "ET", "EL", "EI")):
            raise ProtocolError(f"MT-SICS scale returned an invalid/error reading: {frame}")
        return None

    def acknowledgement(self, operation: str, line: str) -> bool | None:
        frame = line.strip().split()
        expected = "T" if operation == "tare" else "Z"
        if len(frame) < 2 or frame[0] != expected:
            return None
        if frame[1] in ("S", "A"):
            return True
        return False
