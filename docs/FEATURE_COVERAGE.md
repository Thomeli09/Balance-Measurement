# Feature coverage — accurately stated

The Python package has been **redesigned and implemented from scratch**.
No original application `.py` modules are present under the new `src` tree.
This is a new implementation of the intended workflow, **not an assertion of
1:1 parity** with every experimental function in the old project.

| Area in original | New project | Status |
|---|---|---|
| RS232 read/write/connection | `transport`, `client` | Rebuilt; hardware verification pending |
| Mettler Toledo and A&D commands | `protocols` | Rebuilt; model-specific verification pending |
| Old GS/NT/GT serial frames | `LegacyMultilineProtocol` | Rebuilt parser; model-specific testing pending |
| Zero / tare | `ScaleClient.tare/zero` | Acknowledgement-based; actual devices not tested |
| Auto reconnect | `read_with_reconnect` | Bounded retry for safe reads |
| Measure intervals / stable filter | `acquisition` | Rebuilt |
| Multi-balance running | `MultiScaleRunner` | Rebuilt with isolated sessions |
| CSV/JSON export | `storage` | Rebuilt, new fixed schema |
| JSON Lines/SQLite | `storage` | Added |
| Logging | `app_logging` | Rebuilt on `logging` |
| Basic GUI | `gui` | Rebuilt minimal Tkinter application |
| Generic stopwatch | `timing` | Rebuilt |
| Specimen metadata | `domain.Specimen` | Rebuilt simplified |
| Markdown/LaTeX reports | `reporting` | Simple new reports, **old designed template not migrated** (original TeX/PNG assets are preserved in `resources/original_report_templates/`) |
| DataLog arbitrary column/matrix operations | `analysis`, `data_processing` | **Subset only**, not drop-in equivalent |
| General purpose 2D/3D visualization wrappers | `plotting` | **Simple mass-vs-time chart only** |
| Old generic `utils/data.py` list/ndarray utilities | `data_processing` | **Not migrated**; separate non-acquisition utilities |
| Code and import conventions | `src` package + `pyproject.toml` | Rebuilt |

The prioritized deliverable is reliable, extensible balance acquisition and
recording. The original advanced plotting and scientific worksheet utilities
would require separate specification and golden-output tests for feature-equivalent
replacement. Avoid claiming they are available from this fresh package.

## Remaining verification requirements

- Physical balance and cable (MT-SICS / A&D command variants, output mode,
  ACK settings, parity/handshake, stable vs dynamic, overload, remote commands)
- Python 3.15 installed run with all dependencies (only 3.13 is tested locally)
- Windows/Tkinter real desktop smoke test
- Running Ruff and mypy (not installed in this offline environment)
- Serial hot-unplug and disk-full/permission error simulation in production
