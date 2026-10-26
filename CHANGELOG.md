# Changelog

## 0.2.0 — fresh implementation (2026-10-22)

- Replaced old monolithic classes by independent, typed modules.
- Added consistent PEP 8 naming, `src` package layout and installer entry point.
- Added MT-SICS, A&D and legacy line-based protocol adapters.
- Added decimal model, strict response errors and timestamped metadata.
- Added CSV, JSONL, JSON and SQLite sinks plus a typed reader.
- Added optional read-only reconnect, multiscale sessions and cancellation.
- Added TOML config, CLI, simple Tkinter GUI, statistics, report and plot tools.
- Added tests, CI definitions and comprehensive migration/hardware docs.

This is a new breaking API. Advanced original plotting/matrix tools are not
preserved; see docs/FEATURE_COVERAGE.md.
