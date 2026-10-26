# Migration from the original project

**Breaking-change rebuild.** The old import and method paths were not kept as
compatibility aliases. This is intentional: leaving 5,000+ lines of original
coupled modules in `src` would defeat the maintainability goal.

## Application-level migration

Old program: create `BalanceMettler` or `BalanceAD`, start a connection, call
`getWeight()` repeatedly, then pass data to `StorageCSV` or `DataLog`.

New program: create `ScaleClient(SerialTransport(SerialSettings(...)),
MettlerToledoProtocol())`, then use `AcquisitionSession` with one or more
independent writer instances from `default_recorder_registry()`.

### Example

```python
from balance_measurement.acquisition import AcquisitionSession, AcquisitionSettings
from balance_measurement.scale import ScaleClient
from balance_measurement.scale.protocols import MettlerToledoProtocol
from balance_measurement.storage import default_recorder_registry
from balance_measurement.scale.transport import SerialSettings, SerialTransport

client = ScaleClient(
    SerialTransport(SerialSettings(port="COM3", baudrate=9600)),
    MettlerToledoProtocol(),
)
writer = default_recorder_registry().create("measurements.csv")
with AcquisitionSession(client, [writer], AcquisitionSettings(count=100)) as session:
    readings = [m for m in session.collect() if m is not None]
```

## Old feature -> new home

| Original interface | New interface | Notes |
|---|---|---|
| `Balance`, `BalanceMettler`, `BalanceAD` | `ScaleClient` + `AcquisitionSession` | Manufacturer is injected, not a different balance class |
| `SerialScale` | `SerialTransport` + `ScaleProtocol` | No on-connect protocol guessing; choose explicitly |
| `AutoReconSerialScale` | `read_with_reconnect()` and `AcquisitionSettings.reconnect_attempts` | Read-only retry, not control commands |
| `getWeightStable`, `getWeightRepeated` | `stable_only`, `collect()` | Different scheduling and return types |
| `StorageCSV`, `StorageJSON` | `CSVRecorder`, `JSONRecorder` | Plus JSONL/SQLite; common writer interface |
| `DataLog` processing | `load_measurements`, `summarize`, `data.processing` | **Not fully equivalent** for arbitrary matrices |
| `MessageManager` | Python `logging`, `configure_logging()` | No logger attached to every data model |
| `TimeLib.Chrono` | `Stopwatch` | Monotonic timer |
| `SpecimenData` | `Specimen` | Simpler model |
| `BalanceLaTeX` | `latex_report`, `markdown_report` | General-purpose report; not old elaborate template |
| GUI placeholders | `balance-measurement gui` | Minimal running acquisition window |
| Plot helpers | `plot_measurements` | Simple time-series; specialized plot API not retained |

## Output/data compatibility

The new CSV header is `timestamp,value,unit,stable,protocol,scale_id,raw_response,metadata`.
The old CSV `StorageCSV` schema is not guaranteed to match it, and attempts
to append to an existing incompatible CSV raise an explicit error. Save to a
new output path or write a one-off migration parser for your legacy files.

New `Measurement.value` is `Decimal`, not `float`. Use `float(m.value)` only at
visualization boundaries. `Measurement.to_dict()` uses a **string** for
`value` so JSON does not lose instrument precision.

## Suggested migration steps

1. Keep the original ZIP as reference; do not overwrite original experiments.
2. Create a new virtual environment and install this project editable.
3. Use `balance-measurement ports`, verify device COM settings, choose protocol.
4. Test one reading and, separately, explicitly test tare and zero with
   appropriate lab authorization.
5. Compare the same reference mass and timestamps in old and new acquisition.
6. For analysis/plotting, port old specialized data processing one function at
   a time against known expected output; do not assume automatic parity.

For migration from the **v0.2.0 rebuilt project**, rather than the original monolithic project, see [MIGRATION_V0.2_TO_V0.3.md](MIGRATION_V0.2_TO_V0.3.md).
