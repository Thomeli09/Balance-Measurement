"""Optional plotting with local Matplotlib imports (no GUI backend dependency at import)."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from balance_measurement.core.models import Measurement


def plot_measurements(
    measurements: Iterable[Measurement],
    output: str | Path,
    *,
    title: str = "Balance measurements",
    show_unstable: bool = True,
) -> Path:
    """Save weight versus timestamps; split series by scale and unit."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Install the plotting extra: pip install '.[plot]'") from exc

    groups: dict[tuple[str, str], list[Measurement]] = {}
    for item in measurements:
        if not show_unstable and item.stable is not True:
            continue
        groups.setdefault((item.scale_id, item.unit), []).append(item)
    if not groups:
        raise ValueError("No measurements to plot")

    figure, axes = plt.subplots(figsize=(10, 5))
    try:
        for (scale, unit), readings in groups.items():
            axes.plot(
                [item.timestamp for item in readings],
                [float(item.value) for item in readings],
                marker=".", linewidth=1.1, label=f"{scale} ({unit})",
            )
        axes.set_title(title)
        axes.set_xlabel("Time")
        axes.set_ylabel("Weight (see legend for units)")
        axes.legend()
        axes.grid(alpha=0.3)
        figure.autofmt_xdate()
        figure.tight_layout()
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(target, dpi=160)
    finally:
        plt.close(figure)
    return target
