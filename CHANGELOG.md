# Changelog

## 0.3.0 — reorganized source and developer experience (2026-10-26)

- Grouped Python modules into purposeful packages: `core`, `scale`, `acquisition`,
  `storage`, `data`, `config`, `times`, `logging`, `visualization`, `reporting`,
  `interfaces`, and `utils`.
- Moved manufacturer protocols and serial transport under `scale/`;
  retained the existing recorder implementations and high-level public API.
- Rewrote internal imports, tests, examples, and application entry point.
- Expanded README to match the original repository documentation style.
- Added editable `requirements.txt` and `requirements-dev.txt` backed by
  optional dependency definitions in `pyproject.toml`.
- Documented old-to-new imports and the module ownership/contribution rules.
- Kept CI non-mutating by running Ruff lint rather than rewriting code.


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
