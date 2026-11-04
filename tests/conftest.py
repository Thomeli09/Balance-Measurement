"""In-memory fake RS232 port. No real hardware required."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable

import pytest


class FakeTransport:
    def __init__(self, lines: Iterable[bytes] = ()) -> None:
        self.lines = deque(lines)
        self.writes: list[bytes] = []
        self.is_open = False

    def open(self) -> None:
        self.is_open = True

    def write(self, data: bytes) -> None:
        if not self.is_open:
            raise RuntimeError("Port closed")
        self.writes.append(data)

    def readline(self) -> bytes:
        return self.lines.popleft() if self.lines else b""

    def close(self) -> None:
        self.is_open = False


@pytest.fixture
def fake_transport():
    return FakeTransport
