# Physical scale acceptance test

The offline tests use a fake byte transport. A connected balance, USB-RS232
converter, instrument manual and appropriately authorized operator are still
required to validate these points:

- [ ] Exact manufacturer/model and firmware are identified.
- [ ] Cable wiring, port assignment, signal level and USB adapter are correct.
- [ ] RS232 configuration matches baud, 5/6/7/8 data bits, parity, stop bits,
      handshaking, framing, read timeout and the device's output terminator.
- [ ] Instrument is set to **command/response** (not unsolicited continuous
      print) mode if required by the selected protocol.
- [ ] `balance-measurement ports` lists the expected port.
- [ ] Known reference mass readback matches the instrument display, including
      negative values, leading zeros, decimal places, units and stable flags.
- [ ] Several readings are acquired; disconnect and close release the COM port.
- [ ] Overload, wrong setting, unplugged cable and timeout raise expected errors.
- [ ] A&D `T` / `ZR` completion acknowledgements are configured and inspected;
      unsupported firmware requires an appropriate custom protocol.
- [ ] Tare and zero are performed **only** in authorized controlled conditions
      and their physical effects are independently checked.
- [ ] Captures of at least one hour are tested with JSONL/SQLite, cancellation,
      reconnect on safe reads, and multiple files.
- [ ] Interoperability and data precision are verified after re-opening CSV,
      JSONL and SQLite; CSV timestamps, units and metadata are validated.
- [ ] On Windows 11 with Python 3.15, create venv, install and run pytest/
      Ruff/mypy and the GUI smoke test.

Enable the opt-in integration test from a shell, e.g. in PowerShell:

```powershell
$env:BALANCE_PORT = "COM3"
$env:BALANCE_PROTOCOL = "mettler-toledo"
python -m pytest -q -m hardware
```

Never treat no-acknowledgement as a confirmed success. The standard-library
logger can log errors to file via `configure_logging(output="logs/run.log")`.
