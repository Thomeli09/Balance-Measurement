# Balance Measurement — full rebuild

A **clean, typed Python project** for communicating with laboratory balances by
RS232/USB-to-serial, exchanging manufacturer-specific commands and recording
readings in multiple formats.

This version is a **new public API**, not a drop-in replacement for the original
`BalanceLib`, `ScaleBench`, `DataStorageLib`, or `GUIMessageLib`. See
[Migration](docs/MIGRATION.md) and [Feature coverage](docs/FEATURE_COVERAGE.md).

## Features

- Mettler Toledo **MT-SICS** (`SI`, `T`, `Z`); A&D **GX-A/GF-A style**
  (`Q`, `T`, `ZR`); old `GS/NT/GT` line parser as a separate adapter.
  **Verify commands and COM settings with the exact balance manual.**
- Port settings (baudrate, parity, stop bits, terminator) kept separate from
  balance protocol/parsing and acquisition/storage logic.
- Precision-preserving `Decimal` values, UTC ISO timestamps, stability flags,
  scale IDs, original responses and optional specimen/experiment metadata.
- CSV, newline-delimited JSON (`.jsonl`, `.ndjson`), JSON arrays, SQLite;
  save the same acquisition to several formats simultaneously.
- Serial read retry/reconnect on connection failures, explicitly disabled by
  default; **tare/zero are never automatically retried**.
- Single and multiple balance sessions; Tkinter control window; logging;
  basic plotting, filtering, unit conversion, stopwatch and laboratory reports.
- No pandas/numpy required for acquisition; plotting is optional.

## Setup on Windows 11 using Python 3.15

```powershell
# From the extracted project root
py -3.15 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,plot]"
python -m pytest -q
balance-measurement protocols
balance-measurement ports
```

Python 3.13+ is permitted by package metadata. CI defines jobs for 3.13, 3.14
and 3.15; Python 3.15 and real hardware **have not been executed in the
provided development environment**. Running this on your machine is an
important remaining validation step.

## Read one value

```powershell
balance-measurement read --port COM3 --protocol mettler-toledo
```

## Acquire and save 100 readings (two simultaneous formats)

```powershell
balance-measurement capture --port COM3 --protocol mettler-toledo `
  --count 100 --interval 0.5 --stable-only `
  --output measurements.csv --output measurements.jsonl `
  --metadata '{"specimen_id":"S001","experiment":"drying"}'
```

For A&D, use `--protocol a-and-d` and the instrument's exact COM configuration.
See `examples/settings.toml` for a shareable configuration file:

```powershell
balance-measurement capture --config examples/settings.toml
```

The CLI prints readings as they arrive and reports attempts, saves, timeouts,
and unstable readings omitted. Use `--forever` for an unbounded capture; Ctrl+C ends acquisition safely.
In the Python API, use `AcquisitionSettings(count=None)`.

## Python API

```python
from pathlib import Path
from balance_measurement.acquisition import AcquisitionSession, AcquisitionSettings
from balance_measurement.client import ScaleClient
from balance_measurement.protocols import default_registry
from balance_measurement.storage import default_recorder_registry
from balance_measurement.transport import SerialSettings, SerialTransport

transport = SerialTransport(SerialSettings(port="COM3", baudrate=9600))
protocol = default_registry().create("mettler-toledo")
client = ScaleClient(transport, protocol, scale_id="scale-a")

writers = default_recorder_registry()
with AcquisitionSession(
    client,
    [writers.create(Path("weights.csv")), writers.create(Path("weights.sqlite3"))],
    AcquisitionSettings(count=20, interval_seconds=1, stable_only=True),
) as acquisition:
    for weight in acquisition.collect():
        if weight is not None:
            print(weight.value, weight.unit, weight.stable)
```

## Analyze or plot previously recorded data

```powershell
balance-measurement stats measurements.csv
balance-measurement plot measurements.csv --output measurements.png
balance-measurement gui
```

## Quality checks

```powershell
python -m pytest -q
ruff check .
ruff format .
mypy src/balance_measurement
python -m build
```

Dependencies for these commands are included in `.[dev]`. The project also
contains a hardware integration test, gated by `BALANCE_PORT` and
`BALANCE_PROTOCOL` environment variables.

## More information

- [Architecture, boundaries and extension points](docs/ARCHITECTURE.md)
- [Naming, typing and source code conventions](docs/CONVENTIONS.md)
- [Migration guide from the old libraries](docs/MIGRATION.md)
- [What is and is not fully migrated](docs/FEATURE_COVERAGE.md)
- [Hardware acceptance checklist](docs/HARDWARE_VALIDATION.md)

The repository is intended for research measurement workflows, not validated
industrial safety or legal-for-trade measurement applications.
