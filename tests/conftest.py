import asyncio

import aioserial
import pytest

from syringe_pump import Pump


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def serial():
    return aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)


@pytest.fixture(scope="session")
async def pump(serial):
    pump = Pump(serial=serial)
    await pump.set_mode("iw")
    return pump
