"""New, pure scientific data-processing utilities."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from balance_measurement.data.processing import (
    convert_mass, filter_measurements, relative_mass_loss, split_by_scale,
)
from balance_measurement.core.models import Measurement


def item(value, **changes):
    values = dict(value=Decimal(value), unit="g", stable=True, protocol="test")
    values.update(changes)
    return Measurement(**values)


def test_convert_mass():
    assert convert_mass(item("1.25"), "mg").value == Decimal("1250.00")
    assert convert_mass(item("250", unit="mg"), "g").value == Decimal("0.250")
    with pytest.raises(ValueError):
        convert_mass(item("1", unit="oz"), "g")


def test_filters_and_groups():
    readings = [item("1", scale_id="a", metadata={"specimen_id": "S1"}),
                item("2", scale_id="b", stable=False)]
    assert len(list(filter_measurements(readings, stable_only=True, specimen_id="S1"))) == 1
    assert sorted(split_by_scale(readings)) == ["a", "b"]


def test_relative_mass_loss():
    now = datetime(2026, 10, 22, tzinfo=timezone.utc)
    first = item("8.25", timestamp=now)
    second = replace(first, value=Decimal("8.00"), timestamp=now + timedelta(seconds=10))
    assert relative_mass_loss([first, second]) == [(0.0, Decimal(0)), (10.0, Decimal("0.25"))]
    with pytest.raises(ValueError):
        relative_mass_loss([second, first])


def test_mass_loss_rejects_multiple_scales():
    first = item("1")
    with pytest.raises(ValueError, match="scales"):
        relative_mass_loss([first, replace(first, scale_id="other")])
