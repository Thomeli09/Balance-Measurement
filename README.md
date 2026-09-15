# Balance Measurement

Balance-Measurement is a Python project for communicating with and acquiring measurements from RS-232/USB bench scales.

## Disclaimer

This project is provided as-is, without warranty of any kind.

Before using it in laboratory, industrial, safety-critical, or regulated environments, verify that the software behaves correctly with your specific balance, communication interface, and measurement workflow.

The author is not responsible for incorrect measurements, data loss, equipment damage, or other consequences resulting from the use of this software.

## Requirements

* Python 3.12
* Additional Python packages listed in `requirements.txt`

Development and testing dependencies are listed separately in `requirements-dev.txt`.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Thomeli09/Balance-Measurement.git
cd Balance-Measurement
```

### 2. Install the required dependencies

Install the runtime dependencies with:

```bash
pip install -r requirements.txt
```

### 3. Development installation

Additional packages used for development, testing, documentation, and related tools are listed in `requirements-dev.txt`.

Install the complete development environment with:

```bash
pip install -r requirements-dev.txt
```

The development requirements include the packages from `requirements.txt`, so developers only need to install `requirements-dev.txt`.

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

If you use Balance-Measurement in academic, scientific, technical, or published work, please cite the project.

Citation metadata is available in [`CITATION.cff`](CITATION.cff).

A BibTeX citation can also be written as:

```bibtex
@software{Thommes_BalanceMeasurement_2026,
  author       = {Thommes, Eliott},
  title        = {Balance-Measurement: Python driver for RS-232/USB bench scales},
  year         = {2026},
  version      = {0.0.1},
  url          = {https://github.com/Thomeli09/Balance-Measurement}
}
```

Author: **Eliott Thommes**
ORCID: [0009-0005-0697-2438](https://orcid.org/0009-0005-0697-2438)

## License

Balance-Measurement is licensed under the MIT License.

Copyright © 2026 Eliott Thommes.

See the [`LICENSE`](LICENSE) file for the full license text.

