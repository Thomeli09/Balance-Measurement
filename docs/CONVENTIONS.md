# Python conventions

- Package and modules use `snake_case`; classes use `PascalCase`; functions,
  methods and parameters use `snake_case`; constants use `UPPER_SNAKE_CASE`.
- Imports are absolute only at public boundaries and relative for sibling code.
  No wildcard imports. `src/` package layout avoids accidentally importing
  files from the development checkout.
- Public APIs use explicit keyword-only configuration dataclasses and
  type annotations; avoid `getX/setX` Java-style method names.
- Immutable domain objects (`@dataclass(frozen=True, slots=True)`) retain
  instrument value and units together. Numeric values use `Decimal`.
- Context managers own OS resources (`with ScaleClient`,
  `with AcquisitionSession`). No destructive operations in constructors or
  module import (no serial port opens, GUI creation or logfile setup on import).
- Manufacturer-specific grammar is isolated from RS232 transport and storage.
  Fake ports are injected in unit tests instead of monkey-patching USB drivers.
- Exceptions must be explicit. Never silently swallow serial/storage/protocol
  failures; only skip timeouts when the user's policy requests it.
- Time durations use `time.monotonic()` or `time.perf_counter()`. Measurement
  timestamps use timezone-aware UTC `datetime`.
- File text encoding is explicit UTF-8; CSV uses `newline=""`; append mode
  validates existing headers; SQLite uses parameterized SQL queries.
- Standard-library `logging` is used instead of a custom incompatible
  global logger. No handlers are added by import.
- Tests live in `tests/` and do no hardware work unless explicitly opted in.
- Tooling: pytest, Ruff formatting/lint, mypy and GitHub Actions for
  Python 3.13/3.14/3.15. The initial local check was on Python 3.13.

## Example naming changes

| Previously | Now |
|---|---|
| `SerialScale.getWeight()` | `ScaleClient.read_weight()` |
| `SerialScale.setTare()` | `ScaleClient.tare()` |
| `ScaleBench.py` | `transport/serial.py`, `protocols/*`, `client.py` |
| `BalanceLib.py` | `domain.py`, `acquisition.py`, `client.py` |
| `DataStorageLib.py` | `storage/*`, `analysis.py`, `data_processing.py` |
| `GUIMessageLib.py` | `app_logging.py`, `gui.py` |
| `TimeLib.Chrono` | `timing.Stopwatch` |
| `Data2LATEXLib` | `reporting.latex_report` |
