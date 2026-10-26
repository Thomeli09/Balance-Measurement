"""Conventional application logging, no global handlers configured on import."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(
    *, level: int = logging.INFO, output: str | Path | None = None
) -> logging.Logger:
    """Idempotently configure only the application's named logger."""
    logger = logging.getLogger("balance_measurement")
    logger.setLevel(level)
    logger.propagate = False
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if output is not None:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        rotating = RotatingFileHandler(path, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
        rotating.setFormatter(formatter)
        logger.addHandler(rotating)
    return logger
