"""Integration-like acquisition tests using a simulated serial device."""

from decimal import Decimal
from threading import Event

import pytest

from balance_measurement.acquisition import (
    AcquisitionSession, AcquisitionSettings, MultiScaleRunner,
)
from balance_measurement.client import ScaleClient
from balance_measurement.exceptions import ReadTimeoutError
from balance_measurement.protocols import MettlerToledoProtocol
from balance_measurement.storage import default_recorder_registry, load_measurements


def test_session_saves_and_filters(fake_transport, tmp_path):
    device = fake_transport([b"S D 4.20 g\n", b"S S 4.30 g\n", b"S S 4.40 g\n"])
    client = ScaleClient(device, MettlerToledoProtocol())
    path = tmp_path / "out.jsonl"
    session = AcquisitionSession(client, [default_recorder_registry().create(path)],
                                 AcquisitionSettings(count=3, interval_seconds=0,
                                                     stable_only=True))
    with session:
        observed = list(session.collect())
    assert observed[0] is None
    assert session.stats.saved == 2
    assert session.stats.unstable_skipped == 1
    assert [m.value for m in load_measurements(path)] == [Decimal("4.30"), Decimal("4.40")]


def test_timeout_skip(fake_transport):
    session = AcquisitionSession(ScaleClient(fake_transport(), MettlerToledoProtocol()),
                                 settings=AcquisitionSettings(count=3, interval_seconds=0))
    with session:
        assert list(session.collect()) == [None, None, None]
    assert session.stats.timeouts == 3


def test_timeout_raise(fake_transport):
    session = AcquisitionSession(ScaleClient(fake_transport(), MettlerToledoProtocol()),
                                 settings=AcquisitionSettings(count=1, timeout_policy="raise"))
    with session:
        with pytest.raises(ReadTimeoutError):
            list(session.collect())


def test_stop_event(fake_transport):
    stop = Event()
    stop.set()
    session = AcquisitionSession(ScaleClient(fake_transport(), MettlerToledoProtocol()),
                                 settings=AcquisitionSettings(count=None))
    with session:
        assert list(session.collect(stop_event=stop)) == []
    assert session.stats.attempted == 0


def test_invalid_settings():
    with pytest.raises(ValueError):
        AcquisitionSettings(count=-1)
    with pytest.raises(ValueError):
        AcquisitionSettings(interval_seconds=-0.5)
    with pytest.raises(ValueError):
        AcquisitionSettings(timeout_policy="wrong")


def test_two_clients(fake_transport):
    one = ScaleClient(fake_transport([b"S S 1 g\n"]), MettlerToledoProtocol(), scale_id="one")
    two = ScaleClient(fake_transport([b"S S 2 g\n"]), MettlerToledoProtocol(), scale_id="two")
    sessions = [
        AcquisitionSession(client, settings=AcquisitionSettings(count=1, interval_seconds=0))
        for client in (one, two)
    ]
    observed = []
    MultiScaleRunner(sessions).run(observed.append)
    assert sorted((m.scale_id, m.value) for m in observed) == [
        ("one", Decimal(1)), ("two", Decimal(2)),
    ]


def test_duplicate_client_id(fake_transport):
    client = ScaleClient(fake_transport(), MettlerToledoProtocol())
    with pytest.raises(ValueError):
        MultiScaleRunner([AcquisitionSession(client), AcquisitionSession(client)])
