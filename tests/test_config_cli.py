"""Configuration loading and command-line behavior with no actual COM port."""

import json

import pytest

from balance_measurement.interfaces.cli import main
from balance_measurement.config import load_config
from balance_measurement.core.models import Measurement
from balance_measurement.storage import default_recorder_registry, load_measurements


def test_config_relative_output_paths(tmp_path):
    path = tmp_path / "settings.toml"
    path.write_text(
        'protocol = "a-and-d"\noutputs = ["measurements.csv"]\n'
        '[serial]\nport = "COM4"\nresponse_terminator = "\\\\r"\n'
        '[acquisition]\ncount = 5\ninterval_seconds = 0.5\n',
        encoding="utf-8",
    )
    config = load_config(path)
    assert config.serial.port == "COM4"
    assert config.serial.response_terminator == b"\r"
    assert config.outputs == (tmp_path / "measurements.csv",)
    assert config.acquisition.count == 5


def test_cli_protocols(capsys):
    assert main(["protocols"]) == 0
    assert "a-and-d" in capsys.readouterr().out


def test_cli_missing_port(capsys):
    assert main(["read"]) == 2
    assert "--port" in capsys.readouterr().err


def test_cli_stats(capsys, tmp_path):
    from decimal import Decimal

    path = tmp_path / "measurement.csv"
    writer = default_recorder_registry().create(path)
    writer.write(Measurement(value=Decimal("8.25"), unit="g", stable=True, protocol="test"))
    writer.close()
    assert main(["stats", str(path)]) == 0
    assert "mean: 8.25" in capsys.readouterr().out


def test_cli_forever_and_count_conflict(capsys):
    assert main(["capture", "--port", "COM3", "--forever", "--count", "5"]) == 2
    assert "cannot be combined" in capsys.readouterr().err


def test_cli_read_with_simulated_client(monkeypatch, capsys):
    from decimal import Decimal

    from balance_measurement.interfaces import cli

    class SimulatedClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

        def read_weight(self):
            return Measurement(value=Decimal("7.125"), unit="g", stable=True,
                               protocol="mettler-toledo")

    monkeypatch.setattr(cli, "ScaleClient", SimulatedClient)
    assert main(["read", "--port", "COM3"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["value"] == "7.125"


def test_cli_capture_with_fake_serial(monkeypatch, tmp_path, capsys):
    from balance_measurement.interfaces import cli
    from conftest import FakeTransport

    adapter = FakeTransport([b"S S 10.1 g\n", b"S D 10.2 g\n"])
    monkeypatch.setattr(cli, "SerialTransport", lambda _settings: adapter)
    target = tmp_path / "output.csv"
    assert main(["capture", "--port", "COM3", "--count", "2", "--interval", "0",
                 "--output", str(target)]) == 0
    assert [str(m.value) for m in load_measurements(target)] == ["10.1", "10.2"]
    assert "attempted=2 saved=2" in capsys.readouterr().err


def test_config_bad_terminator(tmp_path):
    path = tmp_path / "bad.toml"
    path.write_text('[serial]\nport = "COM3"\nresponse_terminator = "ETX"\n')
    with pytest.raises(ValueError, match="response_terminator"):
        load_config(path)
