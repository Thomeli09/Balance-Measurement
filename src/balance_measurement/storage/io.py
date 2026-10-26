"""Factories and readers for every supported persistence format."""

from __future__ import annotations

import csv
import json
from collections.abc import Callable, Iterator
from pathlib import Path

from balance_measurement.core.models import Measurement
from balance_measurement.storage.base import Recorder
from balance_measurement.storage.csv_recorder import CSVRecorder
from balance_measurement.storage.json_recorder import JSONRecorder
from balance_measurement.storage.jsonl_recorder import JSONLRecorder
from balance_measurement.storage.sqlite_recorder import SQLiteRecorder, read_sqlite


class RecorderRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, Callable[[Path], Recorder]] = {}

    def register(self, extension: str, factory: Callable[[Path], Recorder]) -> None:
        if not extension.startswith(".") or extension in self._factories:
            raise ValueError(f"Invalid or already registered extension: {extension}")
        self._factories[extension] = factory

    def create(self, path: str | Path) -> Recorder:
        output = Path(path)
        try:
            return self._factories[output.suffix.lower()](output)
        except KeyError as exc:
            raise ValueError(f"Unsupported output suffix {output.suffix!r}") from exc


def default_recorder_registry() -> RecorderRegistry:
    registry = RecorderRegistry()
    registry.register(".csv", CSVRecorder)
    registry.register(".jsonl", JSONLRecorder)
    registry.register(".ndjson", JSONLRecorder)
    registry.register(".json", JSONRecorder)
    registry.register(".db", SQLiteRecorder)
    registry.register(".sqlite3", SQLiteRecorder)
    return registry


def load_measurements(path: str | Path) -> Iterator[Measurement]:
    """Stream previously recorded measurements from the provided path."""
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix in (".db", ".sqlite3"):
        yield from read_sqlite(source)
    elif suffix == ".csv":
        with source.open(newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                yield Measurement.from_dict(row)
    elif suffix in (".jsonl", ".ndjson"):
        with source.open(encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    yield Measurement.from_dict(json.loads(line))
    elif suffix == ".json":
        items = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            raise ValueError("JSON measurement data must be an array")
        for item in items:
            yield Measurement.from_dict(item)
    else:
        raise ValueError(f"Unsupported measurement format {suffix!r}")
