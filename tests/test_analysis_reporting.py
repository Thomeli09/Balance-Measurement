"""Standalone stopwatch, statistics and report generation."""

from decimal import Decimal

import pytest

from balance_measurement.analysis import summarize
from balance_measurement.domain import Measurement, Specimen
from balance_measurement.reporting import escape_latex, latex_report, markdown_report, save_report
from balance_measurement.timing import Stopwatch


def m(value, unit="g", stable=True):
    return Measurement(value=Decimal(value), unit=unit, stable=stable, protocol="test")


def test_summary():
    result = summarize([m("1"), m("2", stable=False), m("3")])
    assert result.count == 3
    assert result.stable_count == 2
    assert result.mean == 2
    assert result.standard_deviation == 1


def test_summary_rejects_mixed_units():
    with pytest.raises(ValueError, match="units"):
        summarize([m("1", "g"), m("2", "kg")])


def test_summary_empty():
    with pytest.raises(ValueError):
        summarize([])


def test_report_escapes_tex(tmp_path):
    specimen = Specimen(specimen_id="A_1%", operator="M&M")
    summary = summarize([m("10")])
    assert "A\\_1\\%" in latex_report(specimen, summary)
    assert "M\\&M" in latex_report(specimen, summary)
    assert "A_1%" in markdown_report(specimen, summary)
    assert escape_latex("100%") == "100\\%"
    assert save_report(markdown_report(specimen, summary), tmp_path / "report.md").exists()


def test_stopwatch():
    watch = Stopwatch()
    watch.start()
    assert watch.elapsed >= 0
    watch.lap()
    watch.stop()
    assert len(watch.laps) == 1
    watch.reset()
    assert watch.elapsed == 0


def test_summary_rejects_multiple_scales():
    from dataclasses import replace

    first = m("1")
    with pytest.raises(ValueError, match="scales"):
        summarize([first, replace(first, scale_id="another")])
