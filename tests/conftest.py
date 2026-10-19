import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-hardware",
        action="store_true",
        default=False,
        help="run tests that require a connected physical scale",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-hardware"):
        return

    skip_hardware = pytest.mark.skip(reason="requires --run-hardware and a connected scale")
    for item in items:
        if "hardware" in item.keywords:
            item.add_marker(skip_hardware)
