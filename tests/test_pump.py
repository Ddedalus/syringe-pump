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


async def test_pump_not_initialized():
    """This is what the user will see if they try to use the pump without initializing it"""
    with pytest.raises(PumpError):
        await Pump(serial=aioserial.AioSerial()).version()


async def test_pump_version(pump: Pump):
    output = await pump.version()
    assert isinstance(output, PumpVersion)


async def test_direction_check(pump: Pump):
    with pytest.raises(ValueError):
        await pump.run(direction="invalid")  # type: ignore


@pytest.mark.parametrize("direction", ["infusion", "withdrawal"])
@pytest.mark.motion
async def test_start_stop(pump: Pump, direction: str):
    rate = getattr(pump, f"{direction}_rate")
    volume = getattr(pump, f"{direction}_volume")
    try:
        await pump.set_mode("iw")
        await rate.set(Quantity("5 ml/min"))
        await pump.run()
        await asyncio.sleep(0.1)

        if direction == "infusion":
            # TODO: for some reason withdrawal volume is not being updated
            value = await volume.get()
            assert value.real > 0
    finally:
        await pump.stop()
        await volume.clear()
        await asyncio.sleep(0.1)


async def test_force(pump: Pump, rng: random):  # type: ignore
    with pytest.raises(ValueError):
        await pump.set_force(-1)
    with pytest.raises(ValueError):
        await pump.set_force(150)

    force = rng.randint(15, 25)
    await pump.set_force(force)
    new_force = await pump.get_force()
    assert new_force == force


# @pytest.mark.skip
@pytest.mark.motion
async def test_set_brightness(pump: Pump):
    with pytest.raises(PumpError):
        await pump.set_brightness(-1)
    with pytest.raises(PumpError):
        await pump.set_brightness(150)

    # TODO: this is not working for some unknown reason
    # await pump.set_brightness(15)


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
    time = await pump.set_clock()
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
