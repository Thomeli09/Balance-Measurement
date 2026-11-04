"""Roundtrip data in every built-in storage backend."""

from decimal import Decimal

import pytest

from balance_measurement.domain import Measurement
from balance_measurement.storage import (
    MultiRecorder, default_recorder_registry, load_measurements,
)


@pytest.fixture
def reading():
    return Measurement(value=Decimal("123.00001"), unit="g", stable=None,
                       protocol="test", metadata={"id": "A,1", "condition": "CO2 20%"})


@pytest.mark.parametrize("suffix", [".csv", ".json", ".jsonl", ".ndjson", ".sqlite3", ".db"])
def test_roundtrip(tmp_path, reading, suffix):
    path = tmp_path / f"a{suffix}"
    registry = default_recorder_registry()
    sink = registry.create(path)
    sink.write(reading)
    sink.close()
    second = registry.create(path)
    second.write(reading)
    second.close()
    assert list(load_measurements(path)) == [reading, reading]


def test_csv_existing_schema_validation(tmp_path, reading):
    path = tmp_path / "bad.csv"
    path.write_text("wrong,header\n", encoding="utf-8")
    with pytest.raises(ValueError, match="different header"):
        default_recorder_registry().create(path)


def test_json_existing_array_validation(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{}', encoding="utf-8")
    with pytest.raises(ValueError):
        default_recorder_registry().create(path)


def test_fanout(tmp_path, reading):
    a = tmp_path / "out.csv"
    b = tmp_path / "out.jsonl"
    registry = default_recorder_registry()
    with MultiRecorder([registry.create(a), registry.create(b)]) as combined:
        combined.write(reading)
    assert list(load_measurements(a)) == list(load_measurements(b))


def test_closed_writer(tmp_path, reading):
    sink = default_recorder_registry().create(tmp_path / "test.jsonl")
    sink.close()
    with pytest.raises(ValueError, match="closed"):
        sink.write(reading)


def test_unknown_output_suffix(tmp_path):
    with pytest.raises(ValueError, match="Unsupported"):
        default_recorder_registry().create(tmp_path / "record.xls")


@pytest.mark.parametrize("flag", [True, False])
def test_sqlite_stability_flag_roundtrip(tmp_path, reading, flag):
    from dataclasses import replace

    path = tmp_path / "stable.sqlite3"
    sink = default_recorder_registry().create(path)
    changed = replace(reading, stable=flag)
    sink.write(changed)
    sink.close()
    assert list(load_measurements(path)) == [changed]
