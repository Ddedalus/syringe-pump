import asyncio

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
    await pump.start()
    await asyncio.sleep(0.1)
    await pump.stop()


async def test_set_brightness(pump: Pump):
    with pytest.raises(PumpError):
        await pump.set_brightness(-1)
    with pytest.raises(PumpError):
        await pump.set_brightness(150)
    await pump.set_brightness(15)


async def test_infusion_rate(pump: Pump):
    irate = pump.infusion_rate

    with pytest.raises(PumpError):
        await irate.set(0)

    with pytest.raises(PumpError):
        await irate.set(1.0, "nonsense")

    await irate.set(1.0, "mL/min")
    rate = await irate.get()
    assert rate == 1.0
