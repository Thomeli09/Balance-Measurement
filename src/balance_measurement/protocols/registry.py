"""Explicit registry: select protocols by name, register new ones without editing client."""

from __future__ import annotations

from collections.abc import Callable

from .and_weighing import ADWeighingProtocol
from .base import ScaleProtocol
from .legacy_multiline import LegacyMultilineProtocol
from .mettler_toledo import MettlerToledoProtocol


class ProtocolRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, Callable[[], ScaleProtocol]] = {}

    def register(self, name: str, factory: Callable[[], ScaleProtocol]) -> None:
        if not name.strip() or name in self._factories:
            raise ValueError(f"Invalid or already-registered protocol: {name!r}")
        self._factories[name] = factory

    def create(self, name: str) -> ScaleProtocol:
        if name not in self._factories:
            raise ValueError(f"Unknown protocol {name!r}; choices: {', '.join(self.names())}")
        return self._factories[name]()

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))


def default_registry() -> ProtocolRegistry:
    registry = ProtocolRegistry()
    registry.register("mettler-toledo", MettlerToledoProtocol)
    registry.register("a-and-d", ADWeighingProtocol)
    registry.register("legacy-multiline", LegacyMultilineProtocol)
    return registry
