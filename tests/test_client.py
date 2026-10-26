"""Command lifecycle, failures and response handling."""

import pytest

from balance_measurement.client import ScaleClient
from balance_measurement.exceptions import (
    CommandRejectedError, CommandTimeoutError, ConnectionError, ProtocolError,
    ReadTimeoutError,
)
from balance_measurement.protocols import ADWeighingProtocol, MettlerToledoProtocol


def test_client_read(fake_transport):
    transport = fake_transport([b"ignored\r\n", b"S S 1.230 g\r\n"])
    client = ScaleClient(transport, MettlerToledoProtocol(), scale_id="lab-a")
    with client:
        item = client.read_weight(metadata={"sample": "A1"})
        assert item.to_dict()["value"] == "1.230"
        assert item.scale_id == "lab-a"
        assert item.metadata == {"sample": "A1"}
        assert transport.writes == [b"SI\r\n"]
    assert transport.is_open is False


def test_client_requires_connection(fake_transport):
    with pytest.raises(ConnectionError):
        ScaleClient(fake_transport(), MettlerToledoProtocol()).read_weight()


def test_timeout(fake_transport):
    with ScaleClient(fake_transport(), MettlerToledoProtocol()) as client:
        with pytest.raises(ReadTimeoutError):
            client.read_weight()


def test_malformed_response(fake_transport):
    with ScaleClient(fake_transport([b"S D invalid g\r\n"]), MettlerToledoProtocol()) as client:
        with pytest.raises(ProtocolError):
            client.read_weight()


def test_mettler_tare_and_zero(fake_transport):
    transport = fake_transport([b"T S\r\n", b"Z A\r\n"])
    with ScaleClient(transport, MettlerToledoProtocol()) as client:
        client.tare()
        client.zero()
    assert transport.writes == [b"T\r\n", b"Z\r\n"]


def test_explicit_rejection(fake_transport):
    with ScaleClient(fake_transport([b"T I\r\n"]), MettlerToledoProtocol()) as client:
        with pytest.raises(CommandRejectedError):
            client.tare()


def test_ad_two_acknowledgements(fake_transport):
    transport = fake_transport([b"AK\r\n", b"AK\r\n"])
    with ScaleClient(transport, ADWeighingProtocol()) as client:
        client.tare()
    assert transport.writes == [b"T\r\n"]


def test_unconfirmed_tare_not_silent_success(fake_transport):
    with ScaleClient(fake_transport([b"AK\r\n"]), ADWeighingProtocol()) as client:
        with pytest.raises(CommandTimeoutError):
            client.tare()


def test_read_can_reconnect_without_repeating_tare(fake_transport):
    from balance_measurement.exceptions import TransportError
    from decimal import Decimal

    class FlakyPort:
        def __init__(self):
            self.is_open = False
            self.opens = 0
            self.writes = []

        def open(self):
            self.is_open = True
            self.opens += 1

        def close(self):
            self.is_open = False

        def write(self, data):
            self.writes.append(data)
            if self.opens == 1:
                raise TransportError("Port vanished")

        def readline(self):
            return b"S S 12.34 g\r\n"

    port = FlakyPort()
    with ScaleClient(port, MettlerToledoProtocol()) as client:
        item = client.read_with_reconnect(attempts=1, delay_seconds=0)
    assert item.value == Decimal("12.34")
    assert port.opens == 2
    assert port.writes == [b"SI\r\n", b"SI\r\n"]
