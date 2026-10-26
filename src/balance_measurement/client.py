"""Instrument client coordinating independent transport and protocol adapters."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from collections.abc import Iterator
from typing import Any

from .domain import Measurement
from .exceptions import (
    CommandRejectedError,
    CommandTimeoutError,
    ConnectionError,
    ReadTimeoutError,
    TransportError,
)
from .protocols import ScaleProtocol
from .transport import LineTransport


class ScaleClient:
    """One transport belongs to exactly one client/worker. Not thread-safe.

    No silent retries: retrying tare/zero could change physical state twice.
    """

    def __init__(
        self, transport: LineTransport, protocol: ScaleProtocol, *, scale_id: str = "scale-1"
    ) -> None:
        if not scale_id.strip():
            raise ValueError("scale_id must be non-empty")
        self.transport = transport
        self.protocol = protocol
        self.scale_id = scale_id

    @property
    def connected(self) -> bool:
        return self.transport.is_open

    def connect(self) -> ScaleClient:
        self.transport.open()
        return self

    def disconnect(self) -> None:
        self.transport.close()

    def __enter__(self) -> ScaleClient:
        return self.connect()

    def __exit__(self, *_: object) -> None:
        self.disconnect()

    def _send(self, command: bytes) -> None:
        if not self.connected:
            raise ConnectionError("Call connect() before issuing a command")
        self.transport.write(command)

    def _responses(self) -> Iterator[str]:
        for _ in range(self.protocol.max_response_lines):
            data = self.transport.readline()
            if not data:
                break
            yield data.decode("ascii", errors="replace").strip()

    def read_weight(self, *, metadata: dict[str, Any] | None = None) -> Measurement:
        self._send(self.protocol.read_command)
        for line in self._responses():
            if not line:
                continue
            reading = self.protocol.parse_reading(line)
            if reading is not None:
                return Measurement(
                    timestamp=datetime.now(timezone.utc),
                    value=reading.value,
                    unit=reading.unit,
                    stable=reading.stable,
                    scale_id=self.scale_id,
                    protocol=self.protocol.name,
                    raw_response=line,
                    metadata=metadata or {},
                )
        raise ReadTimeoutError(f"{self.scale_id}: no valid weight response")


    def read_with_reconnect(
        self, *, attempts: int = 1, delay_seconds: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> Measurement:
        """Retry an idempotent read on connection/transport errors only.

        Never retry non-idempotent commands such as tare or zero. Attempts
        counts retries after the first reading; protocol errors still propagate.
        """
        if attempts < 0 or delay_seconds < 0:
            raise ValueError("attempts and delay_seconds must be nonnegative")
        for index in range(attempts + 1):
            try:
                return self.read_weight(metadata=metadata)
            except (ConnectionError, TransportError):
                if index == attempts:
                    raise
                self.disconnect()
                time.sleep(delay_seconds * (2**index))
                self.connect()
        raise AssertionError("unreachable")

    def _execute(self, action: str) -> None:
        self._send(self.protocol.command(action))
        count = 0
        for response in self._responses():
            outcome = self.protocol.acknowledgement(action, response)
            if outcome is False:
                raise CommandRejectedError(f"{action} was rejected: {response}")
            if outcome is True:
                count += 1
                if count >= self.protocol.required_acknowledgements(action):
                    return
        raise CommandTimeoutError(f"{action} was not confirmed by {self.scale_id}")

    def tare(self) -> None:
        """Success only when instrument acknowledgements confirm completion."""
        self._execute("tare")

    def zero(self) -> None:
        self._execute("zero")
