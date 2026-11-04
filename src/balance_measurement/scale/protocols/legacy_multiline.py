"""Dedicated adapter for GS/NT/GT lines seen in the old project."""

from __future__ import annotations

import re

from balance_measurement.utils.decimals import decimal_from_device
from balance_measurement.core.exceptions import ProtocolError
from balance_measurement.scale.protocols.base import Reading, ScaleProtocol

_FRAME = re.compile(
    r"^(?:GS|NT|GT)\s+(?P<number>[+-]?(?:\d+(?:\.\d*)?|\.\d+))\s+(?P<unit>\S+)$"
)


class LegacyMultilineProtocol(ScaleProtocol):
    name = "legacy-multiline"
    read_command = b"SI\r\n"
    max_response_lines = 6

    def parse_reading(self, line: str) -> Reading | None:
        frame = line.strip()
        match = _FRAME.fullmatch(frame)
        if match:
            return Reading(decimal_from_device(match["number"]), match["unit"], None)
        if frame.startswith(("GS ", "NT ", "GT ")):
            raise ProtocolError(f"Invalid multiline reading: {frame}")
        return None
