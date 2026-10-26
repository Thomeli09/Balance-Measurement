"""RS232 transport, with no manufacturer-specific assumptions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..exceptions import ConnectionError, TransportError


@dataclass(frozen=True, slots=True, kw_only=True)
class SerialSettings:
    port: str
    baudrate: int = 9600
    timeout: float = 1.0
    bytesize: int = 8
    parity: str = "N"
    stopbits: float = 1.0
    xonxoff: bool = False
    rtscts: bool = False
    response_terminator: bytes = b"\n"
    max_line_bytes: int = 256

    def __post_init__(self) -> None:
        if not self.port.strip():
            raise ValueError("Serial port is required")
        if self.baudrate <= 0 or self.timeout <= 0 or self.bytesize not in (5, 6, 7, 8):
            raise ValueError("Invalid serial speed, timeout or bytesize")
        if self.parity not in ("N", "E", "O", "M", "S") or self.stopbits not in (1, 1.5, 2):
            raise ValueError("Invalid parity or stopbits")
        if not self.response_terminator or self.max_line_bytes < 16:
            raise ValueError("Invalid line terminator or max_line_bytes")


class SerialTransport:
    """Open on demand and close deterministically. Not shared across threads."""

    def __init__(self, settings: SerialSettings) -> None:
        self.settings = settings
        self._connection: Any = None

    @property
    def is_open(self) -> bool:
        return self._connection is not None and bool(self._connection.is_open)

    def open(self) -> None:
        if self.is_open:
            return
        import serial

        try:
            self._connection = serial.Serial(
                port=self.settings.port,
                baudrate=self.settings.baudrate,
                timeout=self.settings.timeout,
                write_timeout=self.settings.timeout,
                bytesize=self.settings.bytesize,
                parity=self.settings.parity,
                stopbits=self.settings.stopbits,
                xonxoff=self.settings.xonxoff,
                rtscts=self.settings.rtscts,
            )
        except (serial.SerialException, OSError) as exc:
            raise ConnectionError(f"Cannot open {self.settings.port}: {exc}") from exc

    def write(self, data: bytes) -> None:
        if not self.is_open:
            raise ConnectionError("Serial port is not open")
        import serial

        try:
            sent: int = self._connection.write(data)
            if sent != len(data):
                raise TransportError(f"Partial write: {sent}/{len(data)} bytes")
            self._connection.flush()
        except (serial.SerialException, serial.SerialTimeoutException, OSError) as exc:
            raise TransportError("Serial write failed") from exc

    def readline(self) -> bytes:
        if not self.is_open:
            raise ConnectionError("Serial port is not open")
        import serial

        try:
            data: bytes = self._connection.read_until(
                expected=self.settings.response_terminator,
                size=self.settings.max_line_bytes + 1,
            )
        except (serial.SerialException, OSError) as exc:
            raise TransportError("Serial read failed") from exc
        if len(data) > self.settings.max_line_bytes:
            raise TransportError("Serial response exceeds maximum line length")
        return data

    def close(self) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            finally:
                self._connection = None

    def __enter__(self) -> SerialTransport:
        self.open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def list_serial_ports() -> list[tuple[str, str]]:
    """Return USB/serial device identifiers and human-readable descriptions."""
    from serial.tools import list_ports

    return [(port.device, port.description) for port in list_ports.comports()]
