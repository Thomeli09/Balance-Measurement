"""Reusable measurement processing without pandas / numpy requirements."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import replace
from decimal import Decimal

from balance_measurement.core.models import Measurement

_MASS_TO_GRAMS = {
    "µg": Decimal("0.000001"),
    "mg": Decimal("0.001"),
    "g": Decimal("1"),
    "kg": Decimal("1000"),
}


def convert_mass(measurement: Measurement, unit: str) -> Measurement:
    """Convert *recognized mass units only*, leaving device response untouched."""
    if unit not in _MASS_TO_GRAMS or measurement.unit not in _MASS_TO_GRAMS:
        raise ValueError("Only µg, mg, g and kg mass units are currently supported")
    factor = _MASS_TO_GRAMS[measurement.unit] / _MASS_TO_GRAMS[unit]
    return replace(measurement, value=measurement.value * factor, unit=unit)


def filter_measurements(
    source: Iterable[Measurement], *, stable_only: bool = False,
    scale_id: str | None = None, specimen_id: str | None = None,
) -> Iterator[Measurement]:
    """Lazily filter recorded data with explicit criteria."""
    for item in source:
        if stable_only and item.stable is not True:
            continue
        if scale_id is not None and item.scale_id != scale_id:
            continue
        if specimen_id is not None and item.metadata.get("specimen_id") != specimen_id:
            continue
        yield item


def split_by_scale(source: Iterable[Measurement]) -> dict[str, list[Measurement]]:
    """Group readings by scale ID for comparative analyses."""
    groups: defaultdict[str, list[Measurement]] = defaultdict(list)
    for item in source:
        groups[item.scale_id].append(item)
    return dict(groups)


def relative_mass_loss(
    source: Iterable[Measurement], *, unit: str = "g",
) -> list[tuple[float, Decimal]]:
    """Elapsed seconds and weight loss from the first reading.

    Useful for material mass-loss experiments. Negative values denote gain.
    Readings must be chronological, non-empty and of mass units.
    """
    items = list(source)
    if not items:
        return []
    first = convert_mass(items[0], unit)
    series: list[tuple[float, Decimal]] = []
    for item in items:
        if item.scale_id != first.scale_id:
            raise ValueError("Cannot combine different scales in a mass-loss series")
        converted = convert_mass(item, unit)
        elapsed = (converted.timestamp - first.timestamp).total_seconds()
        if elapsed < 0:
            raise ValueError("Measurements are not ordered chronologically")
        series.append((elapsed, first.value - converted.value))
    return series
