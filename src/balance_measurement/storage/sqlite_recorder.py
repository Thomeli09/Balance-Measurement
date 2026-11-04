"""SQLite for long acquisition sessions and structured query access."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from pathlib import Path

from balance_measurement.core.models import Measurement
from balance_measurement.storage.base import FileRecorder


class SQLiteRecorder(FileRecorder):
    def __init__(self, path: str | Path) -> None:
        super().__init__(path)
        self._connection = sqlite3.connect(self.path, timeout=5.0)
        self._connection.execute("PRAGMA busy_timeout = 5000")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                value TEXT NOT NULL,
                unit TEXT NOT NULL,
                stable INTEGER,
                protocol TEXT NOT NULL,
                scale_id TEXT NOT NULL,
                raw_response TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        """)
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_measurement_timestamp ON measurements(timestamp)"
        )
        self._connection.commit()

    def write(self, measurement: Measurement) -> None:
        self._ensure_open()
        data = measurement.to_dict()
        with self._connection:
            self._connection.execute(
                """INSERT INTO measurements (
                    timestamp, value, unit, stable, protocol, scale_id, raw_response, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data["timestamp"], data["value"], data["unit"],
                    None if measurement.stable is None else int(measurement.stable),
                    data["protocol"], data["scale_id"], data["raw_response"],
                    json.dumps(data["metadata"], ensure_ascii=False),
                ),
            )

    def close(self) -> None:
        if not self._closed:
            self._connection.close()
        super().close()


def read_sqlite(path: str | Path) -> Iterator[Measurement]:
    """Stream rows with no need to load a complete SQLite database into memory."""
    conn = sqlite3.connect(f"file:{Path(path).resolve().as_posix()}?mode=ro", uri=True)
    try:
        cursor = conn.execute(
            "SELECT timestamp, value, unit, stable, protocol, scale_id, raw_response, metadata "
            "FROM measurements ORDER BY id"
        )
        columns = [description[0] for description in cursor.description]
        for row in cursor:
            record = dict(zip(columns, row, strict=True))
            if record["stable"] is not None:
                record["stable"] = bool(record["stable"])
            yield Measurement.from_dict(record)
    finally:
        conn.close()
