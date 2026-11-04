# Balance Measurement

[![Python](https://img.shields.io/badge/Python-3.15%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL--3.0--or--later-blue)](LICENSE)

Balance Measurement is a Python project for communicating with laboratory balances by
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

## Requirements

- **Python 3.15 or later** (the declared supported version).
- NumPy and Matplotlib, installed automatically by pip.
- Development/testing tools are included in the optional `dev` extra.

## Installation

Clone the repository:

```bash
git clone https://github.com/Thomeli09/balance_measurement.git
cd balance_measurement
```

Create a virtual environment (example commands for Windows PowerShell):

```powershell
py -3.15 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

On Linux/macOS, use `python3.15 -m venv .venv` and `source .venv/bin/activate`.
Alternatively, `python -m pip install -r requirements.txt` installs the editable
package. To install development dependencies:

```bash
python -m pip install -e ".[dev]"
# Or: python -m pip install -r requirements-dev.txt
```

To run the tests:

```bash
python -m pytest -q
```

The default test run only exercises code that does not need a physical scale.
Hardware tests are marked and skipped unless explicitly requested. To run them,
set the serial port (and optionally the baud rate and protocol), then use:

```powershell
$env:BALANCE_SCALE_PORT = "COM3"
$env:BALANCE_SCALE_BAUDRATE = "9600"
# Optional: set to 1 or 2 to skip protocol auto-detection.
$env:BALANCE_SCALE_PROTOCOL = "1"
python -m pytest -q --run-hardware -m hardware
```

On Linux/macOS, set the same `BALANCE_SCALE_*` environment variables in the
shell before running pytest. Hardware tests only request a reading; they do not
send tare or zero commands.

For a regular non-editable installation, use `python -m pip install .`.

## Repository layout

```text
src/balance_measurement/
    __init__.py                 # Public package API
    BalanceLib.py               # Balance management and measurement workflows
    data_record/                 # CSV storage and data logging
    gui/                         # GUI components
    latex_report/                # Specimen metadata and report support
    logging/                     # Application logging
    scale/                       # Serial scale communication
    time/                        # Time utilities and stopwatch
    utils/                       # Shared utilities
    visualization/               # Matplotlib figures and plot helpers
examples/                        # Runnable example scripts
tests/                           # Automated tests
```

## Quick start

# Read one value

```powershell
balance-measurement read --port COM3 --protocol mettler-toledo
```

# Acquire and save 100 readings (two simultaneous formats)

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

# Python API

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

## Contributing

Contributions are welcome.

Examples of useful contributions include:

* support for additional balances or communication protocols;
* bug fixes;
* improvements to serial communication handling;
* additional tests;
* documentation improvements;
* usage examples;
* compatibility improvements for different operating systems.

If you plan to make a significant change, consider opening an issue first to discuss the proposed implementation.

## Citation

If you use balance_measurement in academic, scientific, technical, or published work, please cite the project.

Citation metadata is available in [`CITATION.cff`](CITATION.cff).

A BibTeX citation can also be written as:

```bibtex
@software{Thommes_BalanceMeasurement_2026,
  author       = {Thommes, Eliott},
  title        = {balance_measurement: Python driver for RS-232/USB bench scales},
  year         = {2026},
  version      = {0.0.2},
  url          = {https://github.com/Thomeli09/balance_measurement}
}
```

Author: **Eliott Thommes**
ORCID: [0009-0005-0697-2438](https://orcid.org/0009-0005-0697-2438)

## License

balance_measurement is licensed under the MIT License.

Copyright © 2026 Eliott Thommes.

See the [`LICENSE`](LICENSE) file for the full license text.
