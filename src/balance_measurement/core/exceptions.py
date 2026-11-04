"""Explicit domain exceptions; callers can distinguish failure scenarios."""


class BalanceError(Exception):
    """Base error for the acquisition library."""


class ConnectionError(BalanceError):
    """Serial port could not be opened or was disconnected."""


class TransportError(BalanceError):
    """An open serial connection could not transmit or receive data."""


class ReadTimeoutError(BalanceError):
    """The instrument did not return a measurement within the time limit."""


class ProtocolError(BalanceError, ValueError):
    """Instrument output was invalid, corrupt or an instrument-reported error."""


class CommandRejectedError(BalanceError):
    """The instrument explicitly rejected an action."""


class CommandTimeoutError(BalanceError):
    """The instrument did not confirm completion of an action."""


class UnsupportedOperationError(BalanceError, NotImplementedError):
    """An instrument does not support the requested command."""


class StorageError(BalanceError):
    """A measurement could not be persisted."""
