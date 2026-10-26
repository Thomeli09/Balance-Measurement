"""Line-delimited JSON for append-safe, long-running measurement logs."""

from __future__ import annotations

import json
from pathlib import Path

from balance_measurement.core.models import Measurement
from balance_measurement.storage.base import FileRecorder


class JSONLRecorder(FileRecorder):
    def __init__(self, path: str | Path) -> None:
        super().__init__(path)
        self._file = self.path.open("a", encoding="utf-8")

    def write(self, measurement: Measurement) -> None:
        self._ensure_open()
        self._file.write(json.dumps(measurement.to_dict(), ensure_ascii=False) + "\n")
        self._file.flush()

    def close(self) -> None:
        if not self._closed:
            self._file.close()
        super().close()
