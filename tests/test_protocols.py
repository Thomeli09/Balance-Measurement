"""Protocol conformance examples and malformed device output."""

from decimal import Decimal

import pytest

from balance_measurement.exceptions import ProtocolError, UnsupportedOperationError
from balance_measurement.protocols import (
    ADWeighingProtocol, LegacyMultilineProtocol, MettlerToledoProtocol,
    Reading, default_registry,
)


@pytest.mark.parametrize("frame,value,unit,stable", [
    ("S S 12.340 g", "12.340", "g", True),
    ("S D -0.003 mg", "-0.003", "mg", False),
    ("SI S +1.0E-2 kg", "0.010", "kg", True),
])
def test_mettler_valid(frame, value, unit, stable):
    actual = MettlerToledoProtocol().parse_reading(frame)
    assert actual == Reading(Decimal(value), unit, stable)


@pytest.mark.parametrize("frame", ["S I", "S + 1 g", "S D nan g", "ES", "EL"])
def test_mettler_invalid(frame):
    with pytest.raises(ProtocolError):
        MettlerToledoProtocol().parse_reading(frame)


@pytest.mark.parametrize("frame,value,stable", [
    ("ST,+00012.34  g", "12.34", True),
    ("US,-00000.01  g", "-0.01", False),
    ("ST, 0.100 kg", "0.100", True),
])
def test_and_valid(frame, value, stable):
    assert ADWeighingProtocol().parse_reading(frame) == Reading(
        Decimal(value), "kg" if "kg" in frame else "g", stable
    )


@pytest.mark.parametrize("frame", ["OL,+9999 g", "EC,E01", "ST,abc g", "US,+nan g"])
def test_and_invalid(frame):
    with pytest.raises(ProtocolError):
        ADWeighingProtocol().parse_reading(frame)


def test_legacy_adapter():
    assert LegacyMultilineProtocol().parse_reading("GS 17.20 g") == Reading(
        Decimal("17.20"), "g", None
    )
    assert LegacyMultilineProtocol().parse_reading("random") is None
    with pytest.raises(ProtocolError):
        LegacyMultilineProtocol().parse_reading("GT impossible")


def test_registry_rejects_duplicate_and_unknown():
    registry = default_registry()
    assert registry.create("a-and-d").name == "a-and-d"
    with pytest.raises(ValueError):
        registry.register("a-and-d", ADWeighingProtocol)
    with pytest.raises(ValueError):
        registry.create("bad-name")


def test_unsupported_action():
    with pytest.raises(UnsupportedOperationError):
        LegacyMultilineProtocol().command("tare")
