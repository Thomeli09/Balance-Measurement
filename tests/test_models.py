"""Lossless decimals, time zone and metadata validation."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from balance_measurement.domain import Measurement, Specimen


def measurement(**changes):
    kwargs = dict(value=Decimal("1.234567890123456789"), unit="g", stable=True, protocol="test")
    kwargs.update(changes)
    return Measurement(**kwargs)


def test_decimal_roundtrip():
    original = measurement()
    parsed = Measurement.from_dict(original.to_dict())
    assert parsed == original
    assert original.to_dict()["value"] == "1.234567890123456789"
    assert original.timestamp.tzinfo is timezone.utc


def test_metadata_is_defensive_copy():
    meta = {"sample": "A"}
    item = measurement(metadata=meta)
    meta["sample"] = "B"
    assert item.metadata["sample"] == "A"


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity")])
def test_reject_nonfinite(value):
    with pytest.raises(ValueError):
        measurement(value=value)


def test_reject_naive_timestamp():
    with pytest.raises(ValueError):
        measurement(timestamp=datetime(2026, 1, 1))


def test_invalid_stability_field():
    item = measurement().to_dict()
    item["stable"] = "yes"
    with pytest.raises((KeyError, ValueError)):
        Measurement.from_dict(item)


def test_specimen_metadata():
    specimen = Specimen(specimen_id="A1", conditions={"RH": "65%"})
    assert specimen.metadata()["conditions"] == {"RH": "65%"}
