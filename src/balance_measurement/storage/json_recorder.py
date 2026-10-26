"""Atomic JSON-array snapshots, designed for small and medium acquisitions."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from balance_measurement.core.models import Measurement
from balance_measurement.storage.base import FileRecorder


class JSONRecorder(FileRecorder):
    def __init__(self, path: str | Path) -> None:
        super().__init__(path)
        self._data: list[dict[str, Any]] = []
        if self.path.exists() and self.path.stat().st_size:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(loaded, list):
                raise ValueError("Existing JSON data must be an array")
            self._data = loaded

    def write(self, measurement: Measurement) -> None:
        self._ensure_open()
        updated = [*self._data, measurement.to_dict()]
        temp: Path | None = None
        try:
            with NamedTemporaryFile(
                mode="w", prefix=f".{self.path.name}.", suffix=".tmp",
                dir=self.path.parent, encoding="utf-8", delete=False,
            ) as stream:
                temp = Path(stream.name)
                json.dump(updated, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, self.path)
        finally:
            if temp is not None:
                temp.unlink(missing_ok=True)
        self._data = updated
