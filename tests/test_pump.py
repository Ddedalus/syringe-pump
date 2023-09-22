import asyncio
import random

import aioserial
import pytest
import serial
from quantiphy import Quantity

from syringe_pump import Pump, PumpVersion
from syringe_pump.exceptions import PumpError
from syringe_pump.pump import QS_MODE_CODE


async def test_com_missconfiguration():
    """This is what the user will see if they choose the wrong COM port"""
    with pytest.raises(serial.SerialException):
        aioserial.AioSerial(port="COM42", baudrate=19200, timeout=0.1)


async def test_pump_version(pump: Pump):
    output = await pump.version()
    assert isinstance(output, PumpVersion)


@pytest.mark.motion
async def test_start_stop(pump: Pump):
    with pytest.raises(ValueError):
        await pump.run(direction="invalid")  # type: ignore

    try:
        await pump.infusion_rate.set(Quantity("1 ml/min"))
        await pump.run()
        await asyncio.sleep(0.1)
        await pump.stop()

        await pump.withdrawal_rate.set(Quantity("1 ml/min"))
        await pump.run(direction="withdraw")
        await asyncio.sleep(0.1)
    finally:
        await pump.stop()


@pytest.mark.skip(reason="This suddenly stopped working. TODO: investigate")
async def test_set_brightness(pump: Pump):
    with pytest.raises(PumpError):
        await pump.set_brightness(-1)
    with pytest.raises(PumpError):
        await pump.set_brightness(150)

    await pump.set_brightness(15)


async def test_force(pump: Pump, rng: random):  # type: ignore
    with pytest.raises(ValueError):
        await pump.set_force(-1)
    with pytest.raises(ValueError):
        await pump.set_force(150)

    force = rng.randint(15, 25)
    await pump.set_force(force)
    new_force = await pump.get_force()
    assert new_force == force


async def test_address(pump: Pump, rng: random):  # type: ignore
    with pytest.raises(ValueError):
        await pump.set_address(-1)
    with pytest.raises(ValueError):
        await pump.set_address(256)

    address = rng.randint(1, 25)
    try:
        new_address = await pump.set_address(address)
        assert new_address == address
    finally:
        await pump.set_address(0)


async def test_time(pump: Pump):
    time = await pump.set_time()
    assert ":" in time
    assert "PM" in time or "AM" in time
    assert "/" in time


@pytest.mark.parametrize(
    "mode,output",
    [
        ("i", "Infuse Only"),
        ("w", "Withdraw Only"),
        ("iw", "Infuse/Withdraw"),
    ],
)
async def test_qs_mode(pump: Pump, mode: QS_MODE_CODE, output: str):
    await pump.set_mode(mode)
    outcome = await pump.get_mode()
    assert output in outcome
