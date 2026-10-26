"""Simultaneously record two physical instruments to separate files."""

from balance_measurement.acquisition import (
    AcquisitionSession, AcquisitionSettings, MultiScaleRunner,
)
from balance_measurement.client import ScaleClient
from balance_measurement.protocols import default_registry
from balance_measurement.storage import default_recorder_registry
from balance_measurement.transport import SerialSettings, SerialTransport

registry = default_registry()
outputs = default_recorder_registry()

sessions = [
    AcquisitionSession(
        ScaleClient(SerialTransport(SerialSettings(port="COM3")),
                    registry.create("mettler-toledo"), scale_id="mt-1"),
        [outputs.create("mt.csv")],
        AcquisitionSettings(count=20, interval_seconds=1.0),
    ),
    AcquisitionSession(
        ScaleClient(SerialTransport(SerialSettings(port="COM4")),
                    registry.create("a-and-d"), scale_id="ad-1"),
        [outputs.create("ad.jsonl")],
        AcquisitionSettings(count=20, interval_seconds=1.0),
    ),
]

if __name__ == "__main__":
    MultiScaleRunner(sessions).run(lambda m: print(m.scale_id, m.value, m.unit))
