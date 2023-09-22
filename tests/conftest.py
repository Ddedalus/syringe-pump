import asyncio
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Protocol
from unittest import mock

import aioserial
import pytest
from pydantic import BaseSettings, Field

from syringe_pump import Pump
from syringe_pump.response_parser import PumpResponse
from tests.pytest_config import (
    pytest_addoption,
    pytest_collection_modifyitems,
    pytest_configure,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


class ConnectionSettings(BaseSettings):
    port: str = Field(default="COM3", env="SYRINGE_PUMP_PORT")
    baudrate: int = Field(default=115200, env="SYRINGE_PUMP_BAUDRATE")
    timeout: float = Field(default=2, env="SYRINGE_PUMP_TIMEOUT")


@pytest.fixture(scope="session")
def serial(request):
    if request.config.option.offline:
        print("No serial connection created in offline mode.")
        return aioserial.AioSerial()
    else:
        return aioserial.AioSerial(**ConnectionSettings().dict())


class SpyPump(Pump):
    """Interface that talks to the actual pump, but collects all input-output pairs for later offline use."""

    io_mapping: Dict[str, List[Dict]] = defaultdict(list)

    async def _write(self, command: str):
        output = await super()._write(command)
        self.io_mapping[command].append(output.dict())
        return output

    def dump(self, json_file: Path):
        with json_file.open("w") as f:
            json.dump(self.io_mapping, f, indent=4)


class OfflinePump(Pump):
    io_mapping: Dict[str, List[Dict]]

    async def load(self, json_file: Path):
        with json_file.open("r") as f:
            self.io_mapping = json.load(f)

    async def _write(self, command: str):
        if command not in self.io_mapping:
            raise ValueError(
                f"Command {command!r} not found in {self.io_mapping.keys()}"
            )
        outputs = self.io_mapping[command]
        if not outputs:
            raise ValueError(f"Command {command!r} has no outputs left")
        output = PumpResponse(**outputs.pop(0))  # type: ignore
        return output


@pytest.fixture(scope="session")
async def pump(request, serial):
    mapping_file = Path(__file__).parent / "io_mapping.json"
    if request.config.option.offline:
        print("Using offline pump")
        pump = OfflinePump(serial=serial)
        await pump.load(mapping_file)
    else:
        pump = SpyPump(serial=serial)

    mock_now = datetime.strptime("02:48:23 PM 05/08/2023", "%I:%M:%S %p %m/%d/%Y")
    with mock.patch("syringe_pump.pump.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        async with pump:
            yield pump

    if not request.config.option.offline:
        assert isinstance(pump, SpyPump)
        pump.dump(mapping_file)


@pytest.fixture(scope="session", params=["infusion_rate", "withdrawal_rate"])
def rate(request, pump: Pump):
    return getattr(pump, request.param)


class Random(Protocol):
    """Protocol for random module, to allow mocking"""

    def uniform(self, a: float, b: float) -> float:
        ...

    def seed(self, seed: int) -> None:
        ...

    def choice(self, seq: list) -> float:
        ...

    def randint(self, a: int, b: int) -> int:
        ...

    def shuffle(self, seq: list) -> None:
        ...

    def sample(self, seq: list, k: int) -> list:
        ...

    def choices(self, seq: list, weights: list, k: int) -> list:
        ...

    def triangular(self, low: float, high: float, mode: float) -> float:
        ...


@pytest.fixture()
def rng() -> Random:
    """Ensure the same random numbers are generated inside each individual test."""
    import random

    random.seed(123)
    return random  # type: ignore
