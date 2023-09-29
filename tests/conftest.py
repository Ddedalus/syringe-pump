import asyncio
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Protocol
from unittest import mock

import aioserial
import pytest
from pydantic import Field
from pydantic_settings import BaseSettings

from syringe_pump import Pump
from syringe_pump.response_parser import PumpResponse
from tests.pytest_config import (  # noqa: F401; fixtures defined elsewhere for convenience
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
    port: str = Field(default="COM3", validation_alias="SYRINGE_PUMP_PORT")
    baudrate: int = Field(default=115200, validation_alias="SYRINGE_PUMP_BAUDRATE")
    timeout: float = Field(default=2, validation_alias="SYRINGE_PUMP_TIMEOUT")


class SpySerial(aioserial.AioSerial):
    """Interface that talks to the actual pump, but collects all input-output pairs for later offline use."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.io_mapping: dict[str, list[str]] = defaultdict(list)
        self._most_recent_command: str = ""

    async def write_async(self, data) -> int:
        self._most_recent_command = bytes(data).decode()
        return await super().write_async(data)

    async def read_until_async(self, expected: bytes = b"\r\n", size=None) -> bytes:
        answer = await super().read_until_async(expected, size)
        if self._most_recent_command:
            self.io_mapping[self._most_recent_command].append(answer.decode())
        self._most_recent_command = ""
        return answer

    def persist(self, json_file: Path):
        with json_file.open("w") as f:
            json.dump(self.io_mapping, f, indent=4)


class OfflineSerial(aioserial.AioSerial):
    def __init__(self, casette: Path, **kwargs) -> None:
        super().__init__(**kwargs)
        with casette.open("r") as f:
            self.io_mapping: dict[str, list[str]] = json.load(f)
        self._next_response: str = ""

    async def write_async(self, data) -> int:
        command = bytes(data).decode()
        if command not in self.io_mapping:
            raise KeyError(f"Command {command!r} not found in {self.io_mapping.keys()}")
        outputs = self.io_mapping[command]
        if not outputs:
            raise IndexError(f"Command {command!r} has no outputs left")
        self._next_response = outputs.pop(0)
        return len(data)

    async def read_until_async(self, expected: bytes = b"\r\n", size=None) -> bytes:
        if not self._next_response:
            raise ValueError("No response set")
        response = self._next_response
        self._next_response = ""
        return response.encode()


casette_file = Path(__file__).parent / "casette.json"


@pytest.fixture(scope="session")
def serial(request):
    if request.config.option.offline:
        print("Using offline serial interface")
        yield OfflineSerial(casette=casette_file)
    else:
        s = SpySerial(**ConnectionSettings().dict())
        yield s
        s.persist(casette_file)


@pytest.fixture(scope="session")
async def pump(request, serial):
    pump = Pump(serial=serial)

    mock_now = datetime.strptime("02:48:23 PM 05/08/2023", "%I:%M:%S %p %m/%d/%Y")
    with mock.patch("syringe_pump.pump.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        async with pump:
            yield pump


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
