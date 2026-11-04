"""Cooperative, cancelable acquisition engine; no GUI or file-format coupling."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

from balance_measurement.scale.client import ScaleClient
from balance_measurement.core.models import Measurement
from balance_measurement.core.exceptions import ReadTimeoutError
from balance_measurement.storage import MultiRecorder, Recorder

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class AcquisitionSettings:
    count: int | None = 100
    interval_seconds: float = 1.0
    stable_only: bool = False
    reconnect_attempts: int = 0
    reconnect_delay_seconds: float = 0.5
    timeout_policy: Literal["raise", "skip"] = "skip"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.count is not None and self.count < 0:
            raise ValueError("count must be nonnegative or None (continuous)")
        if self.interval_seconds < 0:
            raise ValueError("interval_seconds cannot be negative")
        if self.reconnect_attempts < 0 or self.reconnect_delay_seconds < 0:
            raise ValueError("Reconnect attempts/delay cannot be negative")
        if self.timeout_policy not in ("raise", "skip"):
            raise ValueError("timeout_policy must be 'raise' or 'skip'")


@dataclass(slots=True)
class AcquisitionStats:
    attempted: int = 0
    saved: int = 0
    unstable_skipped: int = 0
    timeouts: int = 0


class AcquisitionSession:
    """Owns its client/recorders while active. One thread per balance.

    A failure in a recorder stops the acquisition. No falsely reported success.
    """

    def __init__(
        self,
        client: ScaleClient,
        recorders: Sequence[Recorder] = (),
        settings: AcquisitionSettings | None = None,
    ) -> None:
        self.client = client
        self.writer = MultiRecorder(list(recorders))
        self.settings = settings or AcquisitionSettings()
        self.stats = AcquisitionStats()
        self._active = False

    def __enter__(self) -> AcquisitionSession:
        try:
            self.client.connect()
        except BaseException:
            self.writer.close()
            raise
        self._active = True
        return self

    def __exit__(self, *_: object) -> None:
        self._active = False
        try:
            self.client.disconnect()
        finally:
            self.writer.close()

    def take(self) -> Measurement | None:
        if not self._active:
            raise RuntimeError("Use AcquisitionSession inside a 'with' block")
        self.stats.attempted += 1
        try:
            item = self.client.read_with_reconnect(
                metadata=self.settings.metadata,
                attempts=self.settings.reconnect_attempts,
                delay_seconds=self.settings.reconnect_delay_seconds,
            )
        except ReadTimeoutError:
            self.stats.timeouts += 1
            if self.settings.timeout_policy == "raise":
                raise
            logger.warning("Timed out reading from %s", self.client.scale_id)
            return None
        if self.settings.stable_only and item.stable is not True:
            self.stats.unstable_skipped += 1
            return None
        self.writer.write(item)
        self.stats.saved += 1
        return item

    def collect(
        self, *, stop_event: threading.Event | None = None
    ) -> Iterator[Measurement | None]:
        """Start-to-start cadence; cancel immediately during idle waits."""
        if not self._active:
            raise RuntimeError("Use AcquisitionSession inside a 'with' block")
        deadline = time.monotonic()
        attempt = 0
        while self.settings.count is None or attempt < self.settings.count:
            remaining = max(0.0, deadline - time.monotonic())
            if stop_event is not None and stop_event.wait(remaining):
                break
            elif stop_event is None and remaining:
                time.sleep(remaining)
            yield self.take()
            attempt += 1
            deadline = max(deadline + self.settings.interval_seconds, time.monotonic())


class MultiScaleRunner:
    """Optional concurrent acquisition. Each scale owns distinct sinks/serial port."""

    def __init__(self, sessions: Sequence[AcquisitionSession]) -> None:
        ids = [session.client.scale_id for session in sessions]
        if len(ids) != len(set(ids)):
            raise ValueError("Each scale_id must be unique")
        self.sessions = tuple(sessions)
        self.stop_event = threading.Event()

    def stop(self) -> None:
        self.stop_event.set()

    def run(self, on_measurement: Callable[[Measurement], None] | None = None) -> None:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def worker(session: AcquisitionSession) -> None:
            with session:
                for measurement in session.collect(stop_event=self.stop_event):
                    if measurement is not None and on_measurement is not None:
                        on_measurement(measurement)

        with ThreadPoolExecutor(max_workers=max(1, len(self.sessions))) as pool:
            futures = [pool.submit(worker, session) for session in self.sessions]
            for future in as_completed(futures):
                try:
                    future.result()
                except BaseException:
                    self.stop()
                    raise
