import aioserial
import pytest

from syringe_pump import Pump


@pytest.fixture(scope="session")
def serial():
    return aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)


@pytest.fixture(scope="session")
def pump(serial):
    return Pump(serial=serial)
