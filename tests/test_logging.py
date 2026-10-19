import logging

from balance_measurement.logging.GUIMessageLib import LogManager


def test_logger_configuration_without_file_or_console_output():
    manager = LogManager(
        Name="test_balance_measurement",
        BConsole=False,
        BRecord=False,
    )
    try:
        manager.LoggerConfiguration()
        manager.Info("test message")

        assert manager.getBLoggerStart
        assert manager.getLogger.level == logging.DEBUG
    finally:
        for handler in manager.getLogger.handlers[:]:
            manager.getLogger.removeHandler(handler)
            handler.close()
