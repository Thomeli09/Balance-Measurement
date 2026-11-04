"""A scale's command syntax, response parsing and acknowledgements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from ..exceptions import UnsupportedOperationError


@dataclass(frozen=True, slots=True)
class Reading:
    value: Decimal
    unit: str
    stable: bool | None


class ScaleProtocol(ABC):
    """Implement this abstract class to support a new instrument family.

    parse_reading returns None only for irrelevant informational responses;
    malformed weight frames must raise ProtocolError.
    """

    name: str
    read_command: bytes
    tare_command: bytes | None = None
    zero_command: bytes | None = None
    max_response_lines: int = 5

    @abstractmethod
    def parse_reading(self, line: str) -> Reading | None: ...

    def command(self, operation: str) -> bytes:
        if operation not in ("tare", "zero"):
            raise UnsupportedOperationError(f"Unknown operation {operation}")
        result: bytes | None = getattr(self, f"{operation}_command")
        if result is None:
            raise UnsupportedOperationError(f"{self.name} does not implement {operation}")
        return result

    def required_acknowledgements(self, operation: str) -> int:
        """Number of acknowledgements needed to confirm completion."""
        return 1

    def acknowledgement(self, operation: str, line: str) -> bool | None:
        """True: acknowledged, False: rejected, None: unrelated response."""
        return None
