import asyncio
import random

import pytest

from syringe_pump import Pump
from syringe_pump.exceptions import PumpError


async def test_pump_version(pump: Pump):
    output = await pump.version()
    assert "Firmware" in output
    assert "Pump address" in output
    assert "Serial number" in output


@pytest.mark.skip(reason="Don't annoy the pump")
async def test_start_stop(pump: Pump):
    with pytest.raises(ValueError):
        await pump.run(direction="invalid")  # type: ignore

    try:
        await pump.run()
        await asyncio.sleep(0.1)
        await pump.run(direction="withdraw")
        await asyncio.sleep(0.1)
    finally:
        await pump.stop()


async def test_set_brightness(pump: Pump):
    with pytest.raises(PumpError):
        await pump.set_brightness(-1)
    with pytest.raises(PumpError):
        await pump.set_brightness(150)

    await pump.set_brightness(15)


async def test_force(pump: Pump):
    with pytest.raises(ValueError):
        await pump.set_force(-1)
    with pytest.raises(ValueError):
        await pump.set_force(150)

    force = random.randint(15, 25)
    await pump.set_force(force)
    new_force = await pump.get_force()
    assert new_force == force


async def test_address(pump: Pump):
    with pytest.raises(ValueError):
        await pump.set_address(-1)
    with pytest.raises(ValueError):
        await pump.set_address(256)

    address = random.randint(1, 25)
    try:
        new_address = await pump.set_address(address)
        assert new_address == address
    finally:
        await pump.set_address(0)


async def test_time(pump: Pump):
    time = await pump.set_time()
    assert len(time) == len("05/06/23 11:29:01 PM")
