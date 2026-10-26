"""CSV recorder preserving measured decimals exactly as strings."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from balance_measurement.core.models import Measurement
from balance_measurement.storage.base import FileRecorder


class CSVRecorder(FileRecorder):
    fields = (
        "timestamp", "value", "unit", "stable", "protocol", "scale_id",
        "raw_response", "metadata",
    )

    def __init__(self, path: str | Path) -> None:
        super().__init__(path)
        self._file = self.path.open("a+", newline="", encoding="utf-8")
        try:
            self._file.seek(0)
            first = next(csv.reader(self._file), None)
            if first is not None and first != list(self.fields):
                raise ValueError(f"Existing CSV has a different header: {self.path}")
            self._file.seek(0, 2)
            if first is None:
                csv.writer(self._file).writerow(self.fields)
                self._file.flush()
        except Exception:
            self._file.close()
            raise
        self._writer = csv.DictWriter(self._file, fieldnames=self.fields)

    def write(self, measurement: Measurement) -> None:
        self._ensure_open()
        data = measurement.to_dict()
        data["metadata"] = json.dumps(data["metadata"], ensure_ascii=False)
        data["stable"] = "" if measurement.stable is None else str(measurement.stable).lower()
        self._writer.writerow(data)
        self._file.flush()

    def close(self) -> None:
        if not self._closed:
            self._file.close()
        super().close()
