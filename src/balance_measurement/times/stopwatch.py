"""Monotonic stopwatch utilities without wall-clock drift."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass(slots=True)
class Stopwatch:
    _start: float | None = field(default=None, init=False, repr=False)
    _elapsed: float = field(default=0.0, init=False, repr=False)
    laps: list[float] = field(default_factory=list)

    def start(self) -> None:
        if self._start is None:
            self._start = time.perf_counter()

    def stop(self) -> float:
        if self._start is not None:
            self._elapsed += time.perf_counter() - self._start
            self._start = None
        return self.elapsed

    @property
    def elapsed(self) -> float:
        return self._elapsed + (
            time.perf_counter() - self._start if self._start is not None else 0.0
        )

    def lap(self) -> float:
        result = self.elapsed
        self.laps.append(result)
        return result

    def reset(self) -> None:
        self._start = None
        self._elapsed = 0.0
        self.laps.clear()
