# Architecture

## Dependency direction

```text
CLI / GUI / user scripts
        |
        v
AcquisitionSession -----------------------> Recorder interface
        |                                           |
        v                               +-----------+------------+
     ScaleClient                    CSV / JSONL / JSON / SQLite
       /   \
      v     v
Transport  ScaleProtocol
(RS232)   (MT-SICS / A&D / legacy / custom)
        |
        v
Measurement (decimal, timestamp, stability, metadata)
```

**Ports transmit bytes. Protocols interpret frames. Clients coordinate
commands. Sessions schedule work. Recorders persist domain objects.** No
vendor-specific parsing is located in transport, GUI or recorders.

| Subpackage | Responsibility | Examples |
|---|---|---|
| `core/` | Immutable measurement and specimen models; application errors | `Measurement`, `Specimen`, `BalanceError` |
| `scale/transport/` | RS-232 byte transport and serial settings | `LineTransport`, `SerialTransport` |
| `scale/protocols/` | Manufacturer commands and ASCII response parsing | `ScaleProtocol`, `ProtocolRegistry` |
| `scale/client.py` | Coordinate commands/response acknowledgements | `ScaleClient` |
| `acquisition/` | Acquisition loops and multi-scale sessions | `AcquisitionSession`, `MultiScaleRunner` |
| `storage/` | Writers/readers of measurement files | `Recorder`, `load_measurements` |
| `config/` | Parse TOML configuration | `AppConfig`, `load_config` |
| `data/` | Summaries, filtering, unit conversion and mass-loss | `summarize`, `convert_mass` |
| `visualization/` | Optional time-series visualization | `plot_measurements` |
| `reporting/` | Markdown and LaTeX reports | `markdown_report`, `latex_report` |
| `times/` | Monotonic stopwatch | `Stopwatch` |
| `logging/` | Standard logging setup | `configure_logging` |
| `interfaces/` | End-user entry points | CLI and Tkinter GUI |
| `utils/` | Small reusable parsing helpers | `decimal_from_device` |

Python subpackage imports are documented in [MIGRATION_V0.2_TO_V0.3.md](MIGRATION_V0.2_TO_V0.3.md).

### Add a protocol

Subclass `ScaleProtocol` in `scale/protocols/my_brand.py` and define:

- `name`, `read_command` (`bytes` including delimiter), optionally `tare_command`
  and `zero_command`, and `max_response_lines`.
- `parse_reading(line) -> Reading | None`: extract `Decimal`/unit/stability,
  reject malformed frames using `ProtocolError`. Returning `None` means a
  clearly unrelated informational frame, **not a malformed weight**.
- `acknowledgement(operation, line)` and `required_acknowledgements(operation)`
  only if the device confirms completion; never infer tare/zero success.

Register in a custom `ProtocolRegistry` (`registry.register(...)`) and create
`ScaleClient(transport, registry.create("my-brand"))`. You can also instantiate
your protocol class directly. See `examples/custom_protocol.py`.

### Add a recorder

Implement `write(self, measurement: Measurement) -> None` and
`close(self) -> None`. Register a file suffix with
`RecorderRegistry.register(".tsv", TSVRecorder)` or pass an instance directly
to `AcquisitionSession`.

All built-in sinks preserve `Decimal` as **text**, avoiding binary floating-point
rounding. Time is UTC ISO8601; metadata is embedded as a JSON object or JSON
string in CSV/SQLite. File formats can be appended across runs (JSON is a full
atomic rewrite on each write, appropriate for relatively small datasets).

### Failure semantics and reliability

- Missing measurement -> `ReadTimeoutError`; can be skipped or raised via
  `AcquisitionSettings.timeout_policy`.
- Invalid scale frame -> `ProtocolError`: always surfaced; never silently
  coerce invalid digits to `0`.
- Disconnection/write error -> `ConnectionError` / `TransportError`. For **read
  operations only**, optional exponential reconnect uses `reconnect_attempts`.
- Tare/zero -> command accepted **only after acknowledgements**. In some
  A&D modes ACK must be enabled. Unconfirmed does not mean unsuccessful;
  `CommandTimeoutError` signals it could not be verified.
- Storage failure -> propagates and halts the session. **Multiple sinks are not
  transactionally atomic**; some may contain a saved row if a later sink fails.
- In multiscale mode, each session has its **own transport and sink(s)**.
  Callback functions execute on worker threads and must be thread-safe.
- Serial buffers / stale lines must be considered when switching between
  unsolicited streaming and command/response modes; the current client assumes
  command/response with a finite maximum number of lines.

### Storage choice for long experiments

`JSONL`, `CSV` and `SQLite` append. `SQLite` has a schema/index and transactional
single-row commits; prefer it when there will be many observations. JSON arrays
are rewritten atomically on each observation (O(N²) cumulative IO).

### Scope and validation

The current application supports command/response ASCII protocols, not binary
packets, custom checksums, instrument discovery, or vendor-specific continuous
streaming modes. No hardware protocol has been certified on an actual instrument;
match all baudrate, parity, stopbits, commands and reply terminators to the
manufacturer's manual before laboratory use.
