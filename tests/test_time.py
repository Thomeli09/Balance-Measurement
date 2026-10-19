import pytest

from balance_measurement.time.TimeLib import Time2OptiTime


@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    [
        (0.42, "s", (420.0, "ms")),
        (90, "s", (1.5, "min")),
        (-2500, "ms", (-2.5, "s")),
    ],
)
def test_time_conversion(value, unit, expected):
    assert Time2OptiTime(value, unit) == expected


def test_time_conversion_rejects_unknown_units():
    with pytest.raises(ValueError):
        Time2OptiTime(1, "fortnight")
