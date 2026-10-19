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

For a regular non-editable installation, use `python -m pip install .`.

## Repository layout

```text
src/balance_measurement/
    __init__.py                # Public API
    data_record/
        data_record.py         # Data record class and methods
    gui/                        # GUI components (if any)
    latex_report/
    logging/
        logger.py              # Logging configuration and helpers
    scale/
        scale.py               # Scale communication and measurement classes
        scale_abc.py           # Abstract base class for scales
        scale_exceptions.py    # Scale-related exceptions
    time/
        time_utils.py          # Time-related utilities
    utils/                     # Reused generic data tools
    visualization/
        plot_parameters.py     # Shared plotting configuration
        plot_basic.py          # Figures and formatting
        plot_2d.py             # General 2D plot helpers
        plot_board.py          # Voltorb-specific heatmaps
    balance_lib.py                 # Balance-specific algorithms and helpers
examples/                       # Runnable scripts
    MettlerToledo_RS232_example.py  # Example for Mettler Toledo RS-232 balance
tests/                          # Automated tests
```
## Quick start

```python
from balance_measurement import Scale
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

