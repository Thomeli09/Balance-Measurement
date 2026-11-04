"""Smoke tests that ensure the public paths in the README are usable."""

from decimal import Decimal

import pytest

import balance_measurement as bm
from balance_measurement.acquisition import AcquisitionSession, AcquisitionSettings
from balance_measurement.config import AppConfig, load_config
from balance_measurement.core import Measurement, Specimen
from balance_measurement.data import convert_mass, summarize
from balance_measurement.interfaces.cli import main
from balance_measurement.logging import configure_logging
from balance_measurement.reporting import markdown_report
from balance_measurement.scale import SerialSettings, default_registry
from balance_measurement.storage import default_recorder_registry, load_measurements
from balance_measurement.times import Stopwatch
from balance_measurement.utils import decimal_from_device
from balance_measurement.visualization import plot_measurements


def test_root_api_uses_subpackages():
    assert bm.Measurement is Measurement
    assert bm.AcquisitionSession is AcquisitionSession
    assert bm.AcquisitionSettings is AcquisitionSettings
    assert set(default_registry().names()) >= {"mettler-toledo", "a-and-d"}
    assert callable(main) and callable(load_config)
    assert callable(configure_logging) and callable(markdown_report)
    assert callable(plot_measurements) and callable(summarize)
    assert callable(convert_mass) and callable(default_recorder_registry)
    assert callable(load_measurements)
    assert SerialSettings(port="COM3").baudrate == 9600
    assert issubclass(Stopwatch, object) and issubclass(Specimen, object)
    assert AppConfig(serial=SerialSettings(port="COM3")).protocol == "mettler-toledo"


@pytest.mark.parametrize("invalid", ["NaN", "Infinity", "invalid", "-Inf"])
def test_low_level_decimal_rejects_non_numeric_readings(invalid):
    with pytest.raises(ValueError):
        decimal_from_device(invalid)


def test_low_level_decimal_preserves_precision():
    assert decimal_from_device("+0.000012340") == Decimal("0.000012340")


def test_data_helpers_reexported():
    measured = Measurement(value=Decimal("1.25"), unit="g", stable=True, protocol="test")
    assert convert_mass(measured, "mg").value == Decimal("1250.00")


def test_plot_command_from_cli(tmp_path):
    """The CLI's lazy visualization import must work after package moves."""
    pytest.importorskip("matplotlib")
    from balance_measurement.storage import default_recorder_registry

    target = tmp_path / "measurements.csv"
    output = tmp_path / "figure.png"
    writer = default_recorder_registry().create(target)
    try:
        writer.write(Measurement(value=Decimal("1.25"), unit="g", stable=True, protocol="test"))
    finally:
        writer.close()
    assert main(["plot", str(target), "--output", str(output)]) == 0
    assert output.exists()
