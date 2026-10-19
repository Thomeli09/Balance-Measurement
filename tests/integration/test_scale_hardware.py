import os

import os

import pytest

from balance_measurement.scale.ScaleBench import SerialScale


@pytest.mark.hardware
def test_scale_connects_and_returns_a_numeric_weight():
    port = os.getenv("BALANCE_SCALE_PORT")
    if not port:
        pytest.skip("set BALANCE_SCALE_PORT to the connected scale's serial port")

    baudrate = int(os.getenv("BALANCE_SCALE_BAUDRATE", "9600"))
    protocol_value = os.getenv("BALANCE_SCALE_PROTOCOL")
    protocol = int(protocol_value) if protocol_value else None

    scale = SerialScale(Port=port, Baudrate=baudrate, Protocol=protocol)
    try:
        if scale.getProtocol is None:
            scale.getAutoProtocol()
        weight = scale.getWeight()
        assert isinstance(weight, float)
    finally:
        scale.Close()
