"""Opt-in physical test: BALANCE_PORT must name a connected, configured balance."""

import os

import pytest

from balance_measurement.client import ScaleClient
from balance_measurement.protocols import default_registry
from balance_measurement.transport import SerialSettings, SerialTransport


@pytest.mark.hardware
def test_one_real_read():
    port = os.environ.get("BALANCE_PORT")
    if not port:
        pytest.skip("Set BALANCE_PORT to execute the physical integration test")
    name = os.environ.get("BALANCE_PROTOCOL", "mettler-toledo")
    with ScaleClient(SerialTransport(SerialSettings(port=port)),
                     default_registry().create(name)) as scale:
        measurement = scale.read_weight()
    assert measurement.unit
