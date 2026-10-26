"""Optional plotting and application logging smoke tests."""

import logging
from decimal import Decimal

from balance_measurement.app_logging import configure_logging
from balance_measurement.domain import Measurement
from balance_measurement.plotting import plot_measurements


def test_idempotent_logging_configuration(tmp_path):
    name = tmp_path / "run.log"
    logger = configure_logging(output=name)
    count = len(logger.handlers)
    same = configure_logging(output=name)
    assert count == len(same.handlers) == 2
    same.warning("RS232 test")
    assert "RS232 test" in name.read_text(encoding="utf-8")
    configure_logging(level=logging.ERROR)


def test_plot_file(tmp_path):
    name = tmp_path / "plot.png"
    assert plot_measurements(
        [Measurement(value=Decimal("1.0"), unit="g", stable=True, protocol="test")],
        name,
    ) == name
    assert name.stat().st_size > 0
