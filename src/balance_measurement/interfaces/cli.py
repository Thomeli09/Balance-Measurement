"""Command-line application: ports, protocols, read, capture, stats and plotting."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import replace
from pathlib import Path
from typing import Sequence

from balance_measurement.acquisition import AcquisitionSession
from balance_measurement.data.analysis import summarize
from balance_measurement.logging.setup import configure_logging
from balance_measurement.scale.client import ScaleClient
from balance_measurement.config import AppConfig, load_config
from balance_measurement.core.exceptions import BalanceError
from balance_measurement.scale.protocols import default_registry
from balance_measurement.storage import default_recorder_registry, load_measurements
from balance_measurement.scale.transport import SerialSettings, SerialTransport, list_serial_ports


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="balance-measurement", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ports", help="List serial ports detected by the operating system")
    sub.add_parser("protocols", help="List available scale protocols")
    read = sub.add_parser("read", help="Take one measurement")
    capture = sub.add_parser("capture", help="Collect repeated measurements and save")
    for action in (read, capture):
        action.add_argument("--config", type=Path, help="TOML config file")
        action.add_argument("--port", help="COM3 or /dev/ttyUSB0")
        action.add_argument("--baudrate", type=int)
        action.add_argument("--timeout", type=float)
        action.add_argument("--protocol", choices=default_registry().names())
        action.add_argument("--scale-id")
    capture.add_argument("--output", action="append", type=Path, help="Repeat for multiple sinks")
    capture.add_argument("--count", type=int, help="Number of attempts")
    capture.add_argument("--interval", type=float, help="Seconds between attempts")
    capture.add_argument("--stable-only", action="store_true")
    capture.add_argument("--forever", action="store_true", help="Capture until Ctrl+C")
    capture.add_argument("--metadata", help="JSON object saved with each measurement")
    stats = sub.add_parser("stats", help="Summarize a recorded dataset")
    stats.add_argument("file", type=Path)
    plot = sub.add_parser("plot", help="Save a time-series plot (requires plot extra)")
    plot.add_argument("file", type=Path)
    plot.add_argument("--output", required=True, type=Path)
    sub.add_parser("gui", help="Launch optional Tkinter desktop application")
    return parser


def _config_from_args(args: argparse.Namespace) -> AppConfig:
    if args.config:
        config = load_config(args.config)
    else:
        if not args.port:
            raise ValueError("--port COM3 or --config settings.toml is required")
        config = AppConfig(serial=SerialSettings(port=args.port))
    serial = replace(
        config.serial,
        port=args.port or config.serial.port,
        baudrate=args.baudrate if args.baudrate is not None else config.serial.baudrate,
        timeout=args.timeout if args.timeout is not None else config.serial.timeout,
    )
    metadata = dict(config.acquisition.metadata)
    if getattr(args, "metadata", None):
        provided = json.loads(args.metadata)
        if not isinstance(provided, dict):
            raise ValueError("--metadata must be a JSON object")
        metadata.update(provided)
    if getattr(args, "forever", False) and args.count is not None:
        raise ValueError("--forever cannot be combined with --count")
    acq = replace(
        config.acquisition,
        count=(None if getattr(args, "forever", False)
               else args.count if getattr(args, "count", None) is not None
               else config.acquisition.count),
        interval_seconds=(args.interval if getattr(args, "interval", None) is not None
                          else config.acquisition.interval_seconds),
        stable_only=config.acquisition.stable_only or getattr(args, "stable_only", False),
        metadata=metadata,
    )
    return replace(
        config, serial=serial, acquisition=acq,
        protocol=args.protocol or config.protocol,
        scale_id=args.scale_id or config.scale_id,
        outputs=tuple(args.output) if getattr(args, "output", None) else config.outputs,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    configure_logging(level=logging.WARNING)
    try:
        if args.command == "ports":
            ports = list_serial_ports()
            for port, description in ports:
                print(f"{port}\t{description}")
            if not ports:
                print("No serial ports found")
            return 0
        if args.command == "protocols":
            for name in default_registry().names():
                print(name)
            return 0
        if args.command == "stats":
            info = summarize(load_measurements(args.file))
            for name in (
                "count", "stable_count", "scale_id", "unit", "mean", "minimum", "maximum",
                "standard_deviation",
            ):
                print(f"{name}: {getattr(info, name)}")
            return 0
        if args.command == "plot":
            from balance_measurement.visualization import plot_measurements

            print(plot_measurements(load_measurements(args.file), args.output))
            return 0
        if args.command == "gui":
            from .gui import run_gui

            run_gui()
            return 0
        config = _config_from_args(args)
        client = ScaleClient(
            SerialTransport(config.serial), default_registry().create(config.protocol),
            scale_id=config.scale_id,
        )
        if args.command == "read":
            with client:
                print(json.dumps(client.read_weight().to_dict(), ensure_ascii=False))
            return 0
        recorder_registry = default_recorder_registry()
        recorders = []
        try:
            for path in config.outputs:
                recorders.append(recorder_registry.create(path))
        except BaseException:
            for recorder in recorders:
                recorder.close()
            raise
        session = AcquisitionSession(client, recorders, config.acquisition)
        try:
            with session:
                try:
                    for measurement in session.collect():
                        if measurement is not None:
                            print(
                                f"{measurement.timestamp.isoformat()} "
                                f" {measurement.value} {measurement.unit}"
                                f" stable={measurement.stable}"
                            )
                except KeyboardInterrupt:
                    print("Acquisition interrupted; files closed", file=sys.stderr)
        finally:
            print(f"attempted={session.stats.attempted} saved={session.stats.saved} "
                  f"timeouts={session.stats.timeouts} "
                  f"unstable_skipped={session.stats.unstable_skipped}", file=sys.stderr)
        return 0
    except (BalanceError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
