""" Configuration for custom pytest flags:
  --offline: run tests using mock pump responses; no need for live serial connecton.
  --motion: run tests for motion commands (infuse, withdraw, run, stop).
"""
import pytest


def pytest_addoption(parser):
    parser.addoption("--offline", action="store_true", help="Use mock pump responses.")
    parser.addoption("--motion", action="store_true", help="Test motion commands.")


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "motion: mark test to be run only when --motion is specified."
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--motion"):
        return
    skip_motion = pytest.mark.skip(reason="Add --motion pytest option to run")
    for item in items:
        if "motion" in item.keywords:
            item.add_marker(skip_motion)
