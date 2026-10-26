"""Example: add one manufacturer without modifying the acquisition engine."""

from decimal import Decimal

from balance_measurement.protocols import Reading, ScaleProtocol


class MyScaleProtocol(ScaleProtocol):
    name = "my-scale"
    read_command = b"READ\r\n"

    def parse_reading(self, line: str) -> Reading | None:
        # Example response is "W:1.25:g"; replace with the actual manufacturer grammar.
        if not line.startswith("W:"):
            return None
        _, value, unit = line.split(":")
        return Reading(value=Decimal(value), unit=unit, stable=None)


if __name__ == "__main__":
    print("Pass MyScaleProtocol() to ScaleClient with a SerialTransport instance.")
