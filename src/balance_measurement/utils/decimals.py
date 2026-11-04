"""Numeric parsing helpers for ASCII instrument protocols."""

from __future__ import annotations

from decimal import Decimal


def decimal_from_device(raw: str) -> Decimal:
    """Strict finite decimal parsing without converting through binary float."""
    try:
        parsed = Decimal(raw)
    except Exception as exc:
        raise ValueError(f"Invalid numeric field: {raw!r}") from exc
    if not parsed.is_finite():
        raise ValueError(f"Invalid nonfinite weight: {raw!r}")
    return parsed
