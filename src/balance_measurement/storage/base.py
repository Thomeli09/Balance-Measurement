"""Recorder abstractions for schema-stable, independently configurable sinks."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from balance_measurement.core.models import Measurement


class Recorder(Protocol):
    def write(self, measurement: Measurement) -> None: ...

    def close(self) -> None: ...


class FileRecorder:
    """Small common lifecycle; subclasses own actual file resources."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise ValueError("Cannot write to a closed recorder")

    def close(self) -> None:
        self._closed = True


class MultiRecorder:
    """Broadcast the same observation to each sink; not a distributed transaction."""

    def __init__(self, recorders: list[Recorder]) -> None:
        self.recorders = tuple(recorders)
        self._closed = False

    def write(self, measurement: Measurement) -> None:
        if self._closed:
            raise ValueError("Recorder is closed")
        for recorder in self.recorders:
            recorder.write(measurement)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            errors: list[Exception] = []
            for recorder in reversed(self.recorders):
                try:
                    recorder.close()
                except Exception as exc:
                    errors.append(exc)
            if errors:
                raise ExceptionGroup("Failed to close recorders", errors)

    def __enter__(self) -> MultiRecorder:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
