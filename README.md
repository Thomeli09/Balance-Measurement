# Balance Measurement

**Balance Measurement** (`balance_measurement`) is a Python toolkit for connecting a computer to a laboratory balance through **RS-232 or a USB-to-serial adapter**, reading its measurements and recording them in different file formats.

The code is organized so that **balance protocols**, **serial communication**, **measurement acquisition**, **data processing**, and **file storage** can be changed independently. It is intended to be easy to extend when you change manufacturer or add a new export format.

> **Project status:** v0.3.0 — development release. This is a reorganized version of the v0.2.0 rebuild, **not** a drop-in replacement for the original `BalanceLib.py` project. See the [migration guide](docs/MIGRATION.md) and [v0.2 → v0.3 import changes](docs/MIGRATION_V0.2_TO_V0.3.md).

## Disclaimer

This software is provided **as-is**, without warranty of any kind. Before using it in laboratory, industrial, regulated, or safety-critical environments, check it with your **specific scale model, firmware, cable, communication settings, and measurement procedure**.

In particular, the protocol adapters have **not been validated against physical balances** in this development environment. Verify actual readings, units, stable/unstable status, serial replies, and data persistence before relying on the results. The author is not responsible for incorrect measurements, data loss, equipment damage, or other consequences of its use.

## Features

- **Interchangeable balance protocols:** Mettler Toledo MT-SICS, A&D weighing protocols, and a legacy multiline parser. Add another manufacturer through the `ScaleProtocol` interface.
- **Separated RS-232 transport:** configure the COM/TTY port, baud rate, parity, data/stop bits, timeout, and line terminator without changing any protocol code.
- **Structured measurements:** use `Decimal` for precision, UTC timestamps, scale identifiers, stability flags, raw responses, and experiment/specimen metadata.
- **Multiple recording formats:** CSV, JSON, JSON Lines (`.jsonl` / `.ndjson`), and SQLite (`.sqlite3` / `.db`). Write one acquisition to multiple formats simultaneously.
- **Acquisition workflows:** read once or sample at intervals, optionally accept stable readings only, stop a session safely, or acquire from separate balances concurrently.
- **Data tools:** reload saved measurements, compute descriptive statistics, filter by scale/specimen, convert mass units, and calculate relative mass loss.
- **Optional visualization and reports:** time-series plots with Matplotlib; Markdown and LaTeX specimen summaries.
- **CLI and GUI:** command-line tools and a basic Tkinter application.
- **Testing and maintainability:** `src/` package structure, type annotations, simulated serial tests, pytest, Ruff, mypy, and CI configuration.

## Requirements

- **Python 3.13 or later** according to the package metadata, including **Python 3.15** as a target. Python 3.15 has **not yet been tested locally**; the test run delivered with this release uses Python 3.13.
- A supported balance and an RS-232 connection/USB-to-serial adapter for real acquisition; simulated tests require **no hardware**.
- **pySerial** is installed automatically with the package.
- **Matplotlib** is optional, for plotting only. NumPy and pandas are **not needed** for basic acquisition or recording.
- Development/testing tools are declared in the `dev` optional dependency group.

## Installation

Clone the repository (or extract the distributed ZIP):

```bash
git clone https://github.com/Thomeli09/balance_measurement.git
cd balance_measurement
```

Create a virtual environment with **Python 3.15** on Windows PowerShell:

```powershell
py -3.15 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Linux/macOS, replace those first two commands with `python3.15 -m venv .venv` and `source .venv/bin/activate`.

The requirement files deliberately reuse the dependencies declared in `pyproject.toml`, rather than maintaining duplicated dependency lists:

| File | Installs | Recommended use |
|---|---|---|
| `requirements.txt` | `-e .` | Editable application install for normal use |
| `requirements-dev.txt` | `-e .[dev,plot]` | Editable install with pytest, Ruff, mypy, build and plotting |

For development, use **either** `python -m pip install -r requirements-dev.txt` **or** `python -m pip install -e ".[dev,plot]"`. For a regular non-editable installation, use `python -m pip install .`.

## Repository layout

The main implementation is subdivided by **responsibility**, rather than placing all Python modules directly in the package root:

```text
balance_measurement/
├── pyproject.toml                 # Package metadata and dependencies (source of truth)
├── requirements.txt               # Editable runtime installation
├── requirements-dev.txt           # Editable development + plotting installation
├── src/
│   └── balance_measurement/
│       ├── __init__.py            # Convenient public Python API
│       ├── __main__.py            # Enables python -m balance_measurement
│       ├── core/                  # Measurement, Specimen, exceptions
│       ├── scale/
│       │   ├── client.py          # High-level instrument commands
│       │   ├── protocols/         # Mettler Toledo, A&D, protocol registry
│       │   └── transport/         # RS-232 and abstract transport
│       ├── acquisition/           # Measurement sessions and scheduling
│       ├── storage/               # CSV, JSON, JSONL, SQLite readers/writers
│       ├── data/                  # Statistics, filtering, mass conversions
│       ├── config/                # TOML configuration models and loader
│       ├── times/                 # Stopwatch / elapsed-time utilities
│       ├── logging/               # Application logging setup
│       ├── visualization/         # Optional plotting functions
│       ├── reporting/             # Markdown / LaTeX reports
│       ├── interfaces/            # CLI and Tkinter GUI
│       └── utils/                 # Small generic helpers (decimal parsing)
├── examples/                      # Config and runnable Python examples
├── tests/                         # Unit and opt-in hardware tests
├── docs/                          # Architecture, conventions, migration
└── resources/                     # Reference assets from the original project
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for the internal dependencies and how to extend a protocol or recorder.

## Quick start

First, list the available protocols and serial ports:

```powershell
balance-measurement protocols
balance-measurement ports
```

Read **one** value from a Mettler Toledo balance connected to `COM3`:

```powershell
balance-measurement read --port COM3 --baudrate 9600 --protocol mettler-toledo
```

For an A&D balance, use `--protocol a-and-d` and the settings required by **that specific instrument**. The two manufacturers may use different serial command/reply formats and configuration.

### Acquire measurements and save them

Record 100 attempts at a half-second interval in **both** CSV and JSONL:

```powershell
balance-measurement capture --port COM3 --protocol mettler-toledo `
  --count 100 --interval 0.5 --stable-only `
  --output measurements.csv --output measurements.jsonl `
  --metadata '{"specimen_id":"S001","experiment":"drying"}'
```

Alternatively, share the experimental settings with a TOML file:

```powershell
balance-measurement capture --config examples/settings.toml
```

Edit `examples/settings.toml` before running: its output paths are resolved **relative to that file**. Use `--forever` instead of `--count` for a session that ends with Ctrl+C.

### Python API

The following script changes **protocol** and **storage** independently:

```python
from pathlib import Path

from balance_measurement import (
    AcquisitionSession,
    AcquisitionSettings,
    ScaleClient,
    SerialSettings,
    SerialTransport,
    default_registry,
)
from balance_measurement.storage import default_recorder_registry

protocol = default_registry().create("mettler-toledo")  # or "a-and-d"
transport = SerialTransport(SerialSettings(port="COM3", baudrate=9600))
client = ScaleClient(transport, protocol, scale_id="lab-scale-1")

recorders = default_recorder_registry()
with AcquisitionSession(
    client,
    [recorders.create(Path("weights.csv")), recorders.create(Path("weights.sqlite3"))],
    AcquisitionSettings(count=20, interval_seconds=1.0),
) as session:
    for measurement in session.collect():
        if measurement is not None:
            print(measurement.timestamp, measurement.value, measurement.unit)
```

## Examples and tests

Explore `examples/custom_protocol.py`, `examples/multiscale.py`, `examples/specimen_report.py`, and `examples/settings.toml`.

Install development dependencies and run the hardware-independent test suite:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The **real-hardware** integration test is opt-in. It only requests a measurement: it does not automatically tare or zero the balance. After confirming the equipment and serial settings, on PowerShell:

```powershell
$env:BALANCE_PORT = "COM3"
$env:BALANCE_PROTOCOL = "mettler-toledo"
python -m pytest -q -m hardware
```

On Linux/macOS use `export BALANCE_PORT=/dev/ttyUSB0` and `export BALANCE_PROTOCOL=mettler-toledo`. See [hardware validation](docs/HARDWARE_VALIDATION.md) before testing on a real instrument.

## Usage

Analyze measurements that were already saved:

```powershell
balance-measurement stats measurements.csv
balance-measurement plot measurements.csv --output measurements.png
balance-measurement gui
```

The plotting command requires the optional `plot` extra. Tkinter must also be installed and supported by your desktop Python environment for the GUI to work.

For developers, the other useful commands are:

```powershell
ruff check .
ruff format --check .
mypy src/balance_measurement
python -m build
```

To add a scale or a new file format, see [Architecture](docs/ARCHITECTURE.md), [Conventions](docs/CONVENTIONS.md), and [Development](docs/DEVELOPMENT.md). To migrate from the original software or from v0.2.0, follow the respective [migration notes](docs/MIGRATION.md).

## Contributing

Contributions are welcome, especially for additional weighing protocols, USB/RS-232 compatibility, storage formats, tests with actual devices, error handling, documentation, and visualization tools. Please follow the existing Python naming and typing conventions, add tests for new behavior, and discuss large changes in an issue before implementing them.

## Citation

If you use `balance_measurement` in scientific or published work, please cite the project. The reference metadata is stored in [`CITATION.cff`](CITATION.cff).

```bibtex
@software{Thommes_BalanceMeasurement_2026,
  author  = {Thommes, Eliott},
  title   = {Balance Measurement: Modular RS232 laboratory scale acquisition},
  year    = {2026},
  version = {0.3.0},
  url     = {https://github.com/Thomeli09/balance_measurement}
}
```

Author: **Eliott Thommes** · ORCID: [0009-0005-0697-2438](https://orcid.org/0009-0005-0697-2438)

## License

This project is licensed under the **MIT License**. Copyright © 2026 Eliott Thommes. See [`LICENSE`](LICENSE) for the full text.
