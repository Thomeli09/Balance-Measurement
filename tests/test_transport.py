"""Serial settings validation and simulated port errors."""

import pytest

from balance_measurement.scale.transport import SerialSettings, SerialTransport


@pytest.mark.parametrize("changes", [
    {"port": ""}, {"baudrate": 0}, {"timeout": 0}, {"bytesize": 9},
    {"parity": "X"}, {"stopbits": 3}, {"max_line_bytes": 2},
])
def test_invalid_serial_options(changes):
    with pytest.raises(ValueError):
        SerialSettings(**({"port": "COM3"} | changes))


def test_serial_not_connected():
    transport = SerialTransport(SerialSettings(port="COM3"))
    assert not transport.is_open
    with pytest.raises(Exception, match="not open"):
        transport.readline()


def test_serial_transport_with_fake_pyserial(monkeypatch):
    import sys
    import types

    from balance_measurement.core.exceptions import TransportError

    class FakeSerialException(Exception):
        pass

    class FakeSerial:
        def __init__(self, **kwargs):
            self.settings = kwargs
            self.is_open = True
            self.written = []
            self.responses = [b"S S 1.25 g\r\n", b"x" * 30]

        def write(self, data):
            self.written.append(data)
            return len(data)

        def flush(self):
            pass

        def read_until(self, expected, size):
            assert expected == b"\n"
            return self.responses.pop(0)

        def close(self):
            self.is_open = False

    shim = types.SimpleNamespace(
        Serial=FakeSerial,
        SerialException=FakeSerialException,
        SerialTimeoutException=FakeSerialException,
    )
    monkeypatch.setitem(sys.modules, "serial", shim)
    transport = SerialTransport(SerialSettings(port="COM5", max_line_bytes=20))
    transport.open()
    assert transport.is_open
    transport.write(b"SI\r\n")
    assert transport.readline() == b"S S 1.25 g\r\n"
    with pytest.raises(TransportError, match="maximum"):
        transport.readline()
    transport.close()
    assert not transport.is_open
