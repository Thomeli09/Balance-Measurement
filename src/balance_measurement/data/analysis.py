"""Numerically correct statistics independent of acquisition and plotting."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from statistics import mean, stdev
from typing import Iterable

from balance_measurement.core.models import Measurement


@dataclass(frozen=True, slots=True)
class Summary:
    count: int
    stable_count: int
    unit: str
    scale_id: str
    minimum: Decimal
    maximum: Decimal
    mean: Decimal
    standard_deviation: Decimal | None


def summarize(measurements: Iterable[Measurement]) -> Summary:
    """Summarize one unit at a time, never silently mixing g / kg / mg."""
    values: list[Decimal] = []
    stable = 0
    unit: str | None = None
    scale_id: str | None = None
    for measurement in measurements:
        if unit is None:
            unit = measurement.unit
        elif measurement.unit != unit:
            raise ValueError("Different measurement units cannot be combined")
        if scale_id is None:
            scale_id = measurement.scale_id
        elif measurement.scale_id != scale_id:
            raise ValueError("Different scales must be summarized separately")
        values.append(measurement.value)
        stable += measurement.stable is True
    if not values or unit is None or scale_id is None:
        raise ValueError("No measurements to summarize")
    return Summary(
        count=len(values), stable_count=stable, unit=unit, scale_id=scale_id,
        minimum=min(values), maximum=max(values), mean=mean(values),
        standard_deviation=stdev(values) if len(values) >= 2 else None,
    )
