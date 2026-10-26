# Development workflow

## Install a local editable copy

From the repository root (which contains `pyproject.toml`):

```powershell
py -3.15 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

- `pyproject.toml` is the **single source of truth** for dependencies and optional extras.
- `requirements.txt` is an editable install of the runtime package: `-e .`.
- `requirements-dev.txt` installs the same package with development and plot extras: `-e .[dev,plot]`.
- Neither requirements file is a frozen lockfile. To reproduce an exact environment across machines, generate a lock file with a dependency resolver and commit it separately.

Do not duplicate pinned runtime dependency lists across `pyproject.toml` and requirements files. Do not commit `.venv/`, caches, or generated measurement datasets.

## Run checks

```powershell
python -m pytest -q
ruff check .
ruff format --check .
mypy src/balance_measurement
python -m build
```

`ruff format --check .` is non-mutating; the default CI currently runs Ruff lint and unit tests. To apply formatting during development, run `ruff format .` explicitly, then review the changes and run `ruff format --check .` locally before committing.

The test suite uses an in-memory fake transport. Run real-hardware tests only after checking wiring, port permissions, firmware, and communication parameters as described in [HARDWARE_VALIDATION.md](HARDWARE_VALIDATION.md).

## Where should new code go?

| Change | Location |
|---|---|
| Add a balance manufacturer's protocol | `scale/protocols/` |
| Change serial connection handling | `scale/transport/` |
| Add a high-level balance operation | `scale/client.py` |
| Implement acquisition scheduling | `acquisition/session.py` |
| Add an export format | `storage/` |
| Analyze/filter measurements | `data/` |
| Draw charts | `visualization/` |
| Generate printable reports | `reporting/` |
| Add timer/stopwatch logic | `times/` |
| Configure log handlers | `logging/` |
| Add CLI or GUI features | `interfaces/` |
| Parse TOML config | `config/` |
| Add a generic numerical helper | `utils/` |
| Change `Measurement` fields | `core/models.py` |

Do not place domain-specific data processing into `utils/` merely because it is a function. Prefer adding a focused file to the responsible subpackage.

## Imports and naming

Use lowercase `snake_case` module names, `snake_case` functions, `PascalCase` class names and uppercase constants. Prefer importing from stable subpackage entry points where available:

```python
from balance_measurement import ScaleClient, SerialSettings
from balance_measurement.data import summarize
from balance_measurement.storage import default_recorder_registry
from balance_measurement.visualization import plot_measurements
```

Avoid relying on internal paths such as `balance_measurement.scale.transport.serial` in downstream programs when a suitable public import exists. If you must refactor public modules, update examples, tests, docs, and the migration table in the same change.
