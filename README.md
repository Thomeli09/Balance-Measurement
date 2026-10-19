# Balance Measurement

balance_measurement is a Python project for communicating with and acquiring measurements from RS-232/USB bench scales.

## Disclaimer

This project is provided as-is, without warranty of any kind.

Before using it in laboratory, industrial, safety-critical, or regulated environments, verify that the software behaves correctly with your specific balance, communication interface, and measurement workflow.

The author is not responsible for incorrect measurements, data loss, equipment damage, or other consequences resulting from the use of this software.

## Features

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

```python
from balance_measurement import Scale

scale = Scale(Port="COM3", Protocol=1)
try:
    scale.Start()
    print(scale.getWeight())
finally:
    scale.Disconnect()
```
## Examples and tests

## Usage

Usage documentation and examples will be added as the project develops.

For supported balances, serial communication settings, and API examples, see the project documentation and source code.

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

