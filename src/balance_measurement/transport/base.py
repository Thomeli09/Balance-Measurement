"""Minimal byte-stream interface; easily replaced by simulated transports."""

from __future__ import annotations

from typing import Protocol


class LineTransport(Protocol):
    @property
    def is_open(self) -> bool: ...

    def open(self) -> None: ...

    def write(self, data: bytes) -> None: ...

    def readline(self) -> bytes: ...

    def close(self) -> None: ...
